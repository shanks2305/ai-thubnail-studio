import asyncio
import json
from pathlib import Path
from queue import Empty
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.agents.concept_pipeline import run_concept_pipeline
from app.agents.thumbnail_pipeline import load_background, run_thumbnail_pipeline
from app.api.projects import require_project
from app.api.schemas import TextUpdate
from app.api.serialize import present_generation
from app.core.database import session_scope
from app.db.models import Asset, Concept, CritiqueRow, Generation, utcnow
from app.domain.state import DesignSpec
from app.providers.router import readiness_error
from app.services.events import bus
from app.tools.compositor import compose, image_bytes
from app.tools.critic import critique_image
from app.tools.storage import save_bytes

router = APIRouter()
BUSY = {"analyzing", "generating"}


@router.post("/projects/{project_id}/generate", status_code=202)
def generate_concepts(project_id: str, background: BackgroundTasks) -> dict[str, str]:
    with session_scope() as session:
        project = require_project(session, project_id)
        _ensure_idle(project.status)
        if project.generations:
            raise HTTPException(status_code=409, detail="This project already has thumbnails.")
        _ensure_ready()
        for concept in list(project.concepts):
            session.delete(concept)
        project.status = "analyzing"
        project.error = None
        project.updated_at = utcnow()
    background.add_task(run_concept_pipeline, project_id)
    return {"status": "analyzing"}


@router.post("/projects/{project_id}/concepts/{concept_id}/generate", status_code=202)
def generate_thumbnail(project_id: str, concept_id: str, background: BackgroundTasks) -> dict[str, str]:
    with session_scope() as session:
        project = require_project(session, project_id)
        concept = session.get(Concept, concept_id)
        if concept is None or concept.project_id != project.id:
            raise HTTPException(status_code=404, detail="Concept not found.")
        _ensure_idle(project.status)
        _ensure_ready()
        project.status = "generating"
        project.selected_concept_id = concept.id
        project.error = None
        project.updated_at = utcnow()
    background.add_task(run_thumbnail_pipeline, project_id, concept_id)
    return {"status": "generating"}


@router.patch("/generations/{generation_id}")
def edit_generation(generation_id: str, body: TextUpdate) -> dict:
    with session_scope() as session:
        generation = session.get(Generation, generation_id)
        if generation is None:
            raise HTTPException(status_code=404, detail="Thumbnail not found.")
        spec = DesignSpec.model_validate(generation.design_spec)
        spec.text.content = body.content
        spec.text.position = body.position
        spec.text.size = body.size
        spec.text.color = body.color
        image = compose(load_background(session, generation, spec), spec)
        critique = critique_image(image, spec)
        _replace_composite(session, generation, image, spec)
        if generation.critique is None:
            session.add(
                CritiqueRow(
                    id=str(uuid4()),
                    generation_id=generation.id,
                    overall=critique.overall,
                    passed=critique.passed,
                    issues=[issue.model_dump() for issue in critique.issues],
                    recommended_changes=critique.recommended_changes,
                )
            )
        else:
            generation.critique.overall = critique.overall
            generation.critique.passed = critique.passed
            generation.critique.issues = [issue.model_dump() for issue in critique.issues]
            generation.critique.recommended_changes = critique.recommended_changes
        project = require_project(session, generation.project_id)
        project.updated_at = utcnow()
        session.flush()
        return present_generation(generation)


@router.get("/projects/{project_id}/events")
async def project_events(project_id: str, request: Request) -> StreamingResponse:
    await asyncio.to_thread(_assert_project, project_id)

    async def stream():
        subscriber = bus.subscribe(project_id)
        try:
            while not await request.is_disconnected():
                try:
                    event = await asyncio.to_thread(subscriber.get, True, 15)
                except Empty:
                    yield ": ping\n\n"
                    continue
                yield f"data: {json.dumps(event)}\n\n"
        finally:
            bus.unsubscribe(project_id, subscriber)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _assert_project(project_id: str) -> None:
    with session_scope() as session:
        require_project(session, project_id)


def _ensure_idle(status: str) -> None:
    if status in BUSY:
        raise HTTPException(status_code=409, detail="This project is already running.")


def _ensure_ready() -> None:
    message = readiness_error()
    if message:
        raise HTTPException(status_code=400, detail=message)


def _replace_composite(session, generation: Generation, image, spec: DesignSpec) -> None:
    if generation.image_asset_id:
        previous = session.get(Asset, generation.image_asset_id)
        if previous is not None and previous.kind == "composite":
            Path(previous.path).unlink(missing_ok=True)
            session.delete(previous)
            session.flush()
    path = save_bytes(generation.project_id, "composite", image_bytes(image), ".png")
    asset = Asset(
        id=str(uuid4()),
        project_id=generation.project_id,
        kind="composite",
        content_type="image/png",
        path=path,
    )
    session.add(asset)
    session.flush()
    generation.image_asset_id = asset.id
    generation.design_spec = spec.model_dump()
