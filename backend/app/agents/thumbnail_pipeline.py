import logging
from io import BytesIO
from uuid import uuid4

from PIL import Image
from sqlalchemy.orm import Session

from app.agents.judge import judge_thumbnail
from app.agents.runner import mark_failed, public_error, record_step, run_structured
from app.core.config import get_settings
from app.core.database import session_scope
from app.db.models import Asset, Concept, CritiqueRow, Generation, Project, utcnow
from app.domain.state import DesignSpec
from app.services.events import publish
from app.tools.compositor import compose, image_bytes, make_studio_background
from app.tools.critic import revise_spec
from app.tools.image_generation import render_background
from app.tools.storage import read_bytes, save_bytes

logger = logging.getLogger(__name__)


def run_thumbnail_pipeline(project_id: str, concept_id: str) -> None:
    try:
        with session_scope() as session:
            project = session.get(Project, project_id)
            concept = session.get(Concept, concept_id)
            if project is None or concept is None or concept.project_id != project_id:
                return
            spec = run_structured(session, project, "visual_director", _payload(project, concept), DesignSpec)
            publish(project.id, {"type": "agent_started", "agent": "image_generator"})
            background, provider = render_background(spec)
            background_asset = _store_image(session, project.id, "background", background)
            record_step(session, project.id, "image_generator", provider, provider, {"asset_id": background_asset.id})
            _review_loop(session, project, concept, spec, background, background_asset.id)
            project.status = "ready"
            project.error = None
            project.updated_at = utcnow()
            session.commit()
            publish(project.id, {"type": "job_completed", "stage": "thumbnail"})
    except Exception as exc:
        logger.exception("Thumbnail pipeline failed")
        mark_failed(project_id, public_error(exc))


def load_background(session: Session, generation: Generation, spec: DesignSpec) -> Image.Image:
    if generation.background_asset_id:
        asset = session.get(Asset, generation.background_asset_id)
        if asset is not None:
            return Image.open(BytesIO(read_bytes(asset.path))).convert("RGB")
    return make_studio_background(spec)


def _review_loop(session, project: Project, concept: Concept, spec: DesignSpec, background, background_id: str) -> None:
    settings = get_settings()
    publish(project.id, {"type": "agent_started", "agent": "critic"})
    for attempt in range(1, settings.max_revisions + 2):
        composite = compose(background, spec)
        critique = judge_thumbnail(session, project, composite, spec)
        image_asset = _store_image(session, project.id, "composite", composite)
        generation = Generation(
            id=str(uuid4()),
            project_id=project.id,
            concept_id=concept.id,
            attempt=attempt,
            design_spec=spec.model_dump(),
            background_asset_id=background_id,
            image_asset_id=image_asset.id,
        )
        session.add(generation)
        session.flush()
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
        session.commit()
        publish(project.id, {"type": "generation_completed", "generation_id": generation.id, "attempt": attempt})
        if critique.passed or attempt > settings.max_revisions:
            return
        revised = revise_spec(spec, critique)
        # Only text issues can be fixed automatically; re-judging an unchanged spec would repeat the verdict.
        if revised == spec:
            return
        spec = revised


def _store_image(session, project_id: str, kind: str, image: Image.Image) -> Asset:
    path = save_bytes(project_id, kind, image_bytes(image), ".png")
    asset = Asset(id=str(uuid4()), project_id=project_id, kind=kind, content_type="image/png", path=path)
    session.add(asset)
    session.commit()
    return asset


def _payload(project: Project, concept: Concept) -> dict:
    return {
        "description": project.description,
        "video_brief": project.video_brief,
        "reference_profile": project.reference_profile,
        "concept": {
            "name": concept.name,
            "hook": concept.hook,
            "visual_story": concept.visual_story,
            "subject": concept.subject,
            "background": concept.background,
            "composition": concept.composition,
            "text": concept.text,
            "emotional_direction": concept.emotional_direction,
            "why_it_works": concept.why_it_works,
        },
    }
