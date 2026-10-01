import asyncio
import json
from pathlib import Path
from queue import Empty
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.agents.thumbnail_pipeline import load_background
from app.api.projects import require_project
from app.api.schemas import ConceptPrompt, GenerateThumbnailBody, TextUpdate
from app.api.serialize import present_generation
from app.core.database import session_scope
from app.db.models import Asset, Concept, CritiqueRow, Generation, utcnow
from app.domain.state import DesignSpec
from app.providers.router import readiness_error
from app.services.events import bus
from app.services.jobs import enqueue
from app.tools.compositor import compose, image_bytes
from app.tools.critic import critique_image
from app.tools.edits import apply_editor
from app.tools.portraits import load_portrait
from app.tools.storage import save_bytes

router = APIRouter()
BUSY = {"analyzing", "generating"}


@router.post("/projects/{project_id}/generate", status_code=202)
def generate_concepts(project_id: str, background: BackgroundTasks) -> dict[str, str]:
    with session_scope() as session:
        project = require_project(session, project_id)
        _ensure_idle(project.status)
        if project.generations:
            raise HTTPException(status_code=409, detail="Use new directions to keep the thumbnails you already have.")
        _ensure_ready()
        project.status = "analyzing"
        project.error = None
        project.updated_at = utcnow()
    enqueue(background, "concepts", project_id, {"archive": False})
    return {"status": "analyzing"}


@router.post("/projects/{project_id}/directions", status_code=202)
def new_directions(project_id: str, background: BackgroundTasks) -> dict[str, str]:
    with session_scope() as session:
        project = require_project(session, project_id)
        _ensure_idle(project.status)
        _ensure_ready()
        project.status = "analyzing"
        project.error = None
        project.updated_at = utcnow()
    enqueue(background, "concepts", project_id, {"archive": True})
    return {"status": "analyzing"}


@router.post("/projects/{project_id}/render-all", status_code=202)
def render_all(project_id: str, background: BackgroundTasks) -> dict[str, str]:
    with session_scope() as session:
        project = require_project(session, project_id)
        _ensure_idle(project.status)
        if not any(not concept.archived for concept in project.concepts):
            raise HTTPException(status_code=400, detail="Generate concepts before rendering.")
        _ensure_ready()
        project.status = "generating"
        project.error = None
        project.updated_at = utcnow()
    enqueue(background, "batch", project_id)
    return {"status": "generating"}


@router.post("/projects/{project_id}/concepts/{concept_id}/generate", status_code=202)
def generate_thumbnail(
    project_id: str,
    concept_id: str,
    background: BackgroundTasks,
    body: GenerateThumbnailBody | None = None,
) -> dict[str, str]:
    with session_scope() as session:
        project = require_project(session, project_id)
        concept = session.get(Concept, concept_id)
        if concept is None or concept.project_id != project.id or concept.archived:
            raise HTTPException(status_code=404, detail="Concept not found.")
        _ensure_idle(project.status)
        _ensure_ready()
        if body is not None and body.image_prompt is not None:
            concept.image_prompt = body.image_prompt.strip()[:3900] or None
        project.status = "generating"
        project.selected_concept_id = concept.id
        project.error = None
        project.updated_at = utcnow()
    enqueue(background, "thumbnail", project_id, {"concept_id": concept_id})
    return {"status": "generating"}


@router.patch("/concepts/{concept_id}")
def update_concept(concept_id: str, body: ConceptPrompt) -> dict[str, str | None]:
    with session_scope() as session:
        concept = session.get(Concept, concept_id)
        if concept is None or concept.archived:
            raise HTTPException(status_code=404, detail="Concept not found.")
        require_project(session, concept.project_id)
        concept.image_prompt = body.image_prompt.strip()[:3900] or None
        return {"id": concept.id, "image_prompt": concept.image_prompt}


@router.patch("/generations/{generation_id}")
def edit_generation(generation_id: str, body: TextUpdate) -> dict:
    with session_scope() as session:
        generation = session.get(Generation, generation_id)
        if generation is None:
            raise HTTPException(status_code=404, detail="Thumbnail not found.")
        spec = apply_editor(DesignSpec.model_validate(generation.design_spec), body)
        project = require_project(session, generation.project_id)
        image = compose(load_background(session, generation, spec), spec, load_portrait(session, project))
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
