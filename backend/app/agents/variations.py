from sqlalchemy.orm import Session

from app.agents.thumbnail_pipeline import _save_generation, load_background
from app.core.database import session_scope
from app.db.models import Concept, Generation, Project, utcnow
from app.domain.state import DesignSpec
from app.services.events import publish
from app.tools.compositor import compose
from app.tools.critic import critique_image
from app.tools.image_generation import render_background
from app.tools.portraits import load_people

VISUAL_AXES = {"crop", "expression"}


def apply_immediate(session: Session, generation: Generation, axis: str) -> Generation:
    project = session.get(Project, generation.project_id)
    concept = session.get(Concept, generation.concept_id)
    if project is None or concept is None:
        raise ValueError("Thumbnail not found.")
    spec = _adjust(DesignSpec.model_validate(generation.design_spec), axis, project.hooks or [])
    background = load_background(session, generation, spec)
    composite = compose(background, spec, people=load_people(session, project))
    critique = critique_image(composite, spec)
    created = _save_generation(
        session,
        project,
        concept,
        spec,
        composite,
        critique,
        generation.background_asset_id or "",
        _next_attempt(session, concept.id),
        axis,
        generation.id,
    )
    project.selected_generation_id = created.id
    project.updated_at = utcnow()
    session.commit()
    return created


def run_visual_variation(project_id: str, generation_id: str, axis: str) -> None:
    _rerender(project_id, generation_id, axis, "")


def run_rerender(project_id: str, generation_id: str, instruction: str) -> None:
    _rerender(project_id, generation_id, "rerender", instruction)


def _rerender(project_id: str, generation_id: str, axis: str, instruction: str) -> None:
    with session_scope() as session:
        generation = session.get(Generation, generation_id)
        project = session.get(Project, project_id) if generation else None
        concept = session.get(Concept, generation.concept_id) if generation else None
        if project is None or generation is None or concept is None or generation.project_id != project_id:
            return
        spec = DesignSpec.model_validate(generation.design_spec)
        if axis == "crop":
            _flip_crop(spec)
        elif instruction:
            spec.image_prompt = f"{spec.image_prompt} {instruction}".strip()[:3900]
        else:
            spec.image_prompt = f"{spec.image_prompt} A different expression, more intense at thumbnail size.".strip()
        publish(project.id, {"type": "agent_started", "agent": "image_generator"})
        background, provider = render_background(spec)
        from app.agents.thumbnail_pipeline import _store_image

        background_asset = _store_image(session, project.id, "background", background)
        composite = compose(background, spec, people=load_people(session, project))
        critique = critique_image(composite, spec)
        created = _save_generation(
            session,
            project,
            concept,
            spec,
            composite,
            critique,
            background_asset.id,
            _next_attempt(session, concept.id),
            axis,
            generation.id,
        )
        project.status = "ready"
        project.selected_generation_id = created.id
        project.selected_concept_id = concept.id
        project.error = None
        project.updated_at = utcnow()
        session.commit()
        publish(project.id, {"type": "job_completed", "stage": "thumbnail", "provider": provider})


def _adjust(spec: DesignSpec, axis: str, hooks: list) -> DesignSpec:
    updated = spec.model_copy(deep=True)
    if axis == "hook":
        updated.text.content = _next_hook(updated.text.content, hooks)
        return updated
    colors = list(updated.palette) or ["#16130f", "#ff4d2e", "#f2c14e"]
    updated.palette = colors[1:] + colors[:1]
    updated.recolor = True
    return updated


def _flip_crop(spec: DesignSpec) -> None:
    side = "left" if spec.subject.get("position") != "left" else "right"
    spec.subject["position"] = side
    spec.text.position = "right" if side == "left" else "left"


def _next_hook(current: str, hooks: list) -> str:
    texts = [str(item.get("text")) for item in hooks if isinstance(item, dict) and item.get("text")]
    for text in texts:
        if text.strip().upper() != current.strip().upper():
            return text[:80]
    return "THE REAL RESULT" if current.strip().upper() != "THE REAL RESULT" else "WATCH THIS"


def _next_attempt(session: Session, concept_id: str) -> int:
    rows = session.query(Generation.attempt).filter_by(concept_id=concept_id).all()
    return max((row[0] for row in rows), default=0) + 1
