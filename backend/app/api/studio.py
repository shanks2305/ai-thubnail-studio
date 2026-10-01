from fastapi import APIRouter, BackgroundTasks, HTTPException, Response

from app.agents.variations import VISUAL_AXES, apply_immediate
from app.api.projects import require_project
from app.api.schemas import PerformanceBody, RerenderBody, VariationBody
from app.api.serialize import present_generation
from app.api.workflow import _ensure_idle, _ensure_ready
from app.core.database import session_scope
from app.db.models import Generation, utcnow
from app.services.jobs import enqueue

router = APIRouter()


@router.post("/generations/{generation_id}/variations")
def create_variation(
    generation_id: str,
    body: VariationBody,
    background: BackgroundTasks,
    response: Response,
) -> dict:
    with session_scope() as session:
        generation = _generation(session, generation_id)
        project = require_project(session, generation.project_id)
        if body.axis not in VISUAL_AXES:
            created = apply_immediate(session, generation, body.axis)
            session.refresh(created)
            return present_generation(created)
        _ensure_idle(project.status)
        _ensure_ready()
        project.status = "generating"
        project.updated_at = utcnow()
        project_id = project.id
    enqueue(background, "variation", project_id, {"generation_id": generation_id, "axis": body.axis})
    response.status_code = 202
    return {"status": "generating"}


@router.post("/generations/{generation_id}/rerender", status_code=202)
def rerender(generation_id: str, body: RerenderBody, background: BackgroundTasks) -> dict[str, str]:
    with session_scope() as session:
        generation = _generation(session, generation_id)
        project = require_project(session, generation.project_id)
        _ensure_idle(project.status)
        _ensure_ready()
        project.status = "generating"
        project.updated_at = utcnow()
        project_id = project.id
    enqueue(background, "rerender", project_id, {"generation_id": generation_id, "instruction": body.instruction.strip()})
    return {"status": "generating"}


@router.post("/generations/{generation_id}/restore")
def restore_generation(generation_id: str) -> dict:
    with session_scope() as session:
        generation = _generation(session, generation_id)
        project = require_project(session, generation.project_id)
        project.selected_generation_id = generation.id
        project.updated_at = utcnow()
        session.flush()
        return present_generation(generation)


@router.patch("/generations/{generation_id}/performance")
def record_performance(generation_id: str, body: PerformanceBody) -> dict:
    with session_scope() as session:
        generation = _generation(session, generation_id)
        project = require_project(session, generation.project_id)
        generation.impressions = body.impressions
        generation.clicks = body.clicks
        project.updated_at = utcnow()
        session.flush()
        return present_generation(generation)


def _generation(session, generation_id: str) -> Generation:
    generation = session.get(Generation, generation_id)
    if generation is None:
        raise HTTPException(status_code=404, detail="Thumbnail not found.")
    return generation
