import logging
from uuid import uuid4

from app.agents.runner import mark_failed, public_error, run_structured
from app.core.database import session_scope
from app.db.models import Asset, Concept, Project, utcnow
from app.domain.state import ConceptList, HookList, ReferenceProfile, VideoBrief
from app.providers.base import ProviderError
from app.services.events import publish
from app.tools.image_analysis import analyze_image
from app.tools.storage import save_bytes
from app.tools.youtube import download_bytes, fetch_youtube

logger = logging.getLogger(__name__)


def run_concept_pipeline(project_id: str) -> None:
    try:
        with session_scope() as session:
            project = session.get(Project, project_id)
            if project is None:
                return
            _enrich_youtube(session, project)
            base = {
                "description": project.description,
                "youtube": _youtube_payload(project),
            }
            brief = run_structured(session, project, "video_analyst", base, VideoBrief)
            project.video_brief = brief.model_dump()
            project.updated_at = utcnow()
            session.commit()

            references = _reference_payload(project)
            profile = run_structured(
                session,
                project,
                "reference_analyst",
                {**base, "video_brief": brief.model_dump(), "references": references},
                ReferenceProfile,
            )
            project.reference_profile = profile.model_dump()
            session.commit()

            hooks = run_structured(
                session,
                project,
                "hook_strategist",
                {**base, "video_brief": brief.model_dump(), "reference_profile": profile.model_dump()},
                HookList,
            )
            for hook in hooks.hooks:
                hook.id = hook.id or str(uuid4())
            project.hooks = [hook.model_dump() for hook in hooks.hooks]
            session.commit()

            concepts = run_structured(
                session,
                project,
                "creative_director",
                {
                    **base,
                    "video_brief": brief.model_dump(),
                    "reference_profile": profile.model_dump(),
                    "hooks": project.hooks,
                },
                ConceptList,
            )
            _replace_concepts(session, project, concepts)
            project.status = "concepts_ready"
            project.error = None
            project.updated_at = utcnow()
            session.commit()
            publish(project.id, {"type": "concepts_ready"})
            publish(project.id, {"type": "job_completed", "stage": "concepts"})
    except Exception as exc:
        logger.exception("Concept pipeline failed")
        mark_failed(project_id, public_error(exc))


def _enrich_youtube(session, project: Project) -> None:
    if not project.youtube_url:
        return
    metadata = fetch_youtube(project.youtube_url)
    if metadata is None:
        return
    project.youtube_title = metadata.title
    project.title = metadata.title[:200]
    already_has_reference = any(asset.kind == "reference" for asset in project.assets)
    thumbnail = download_bytes(metadata.thumbnail_url) if metadata.thumbnail_url and not already_has_reference else None
    if thumbnail:
        path = save_bytes(project.id, "reference", thumbnail, ".jpg")
        session.add(
            Asset(
                id=str(uuid4()),
                project_id=project.id,
                kind="reference",
                content_type="image/jpeg",
                path=path,
            )
        )
    session.commit()


def _youtube_payload(project: Project) -> dict | None:
    if not project.youtube_url:
        return None
    return {"url": project.youtube_url, "title": project.youtube_title}


def _reference_payload(project: Project) -> list[dict[str, object]]:
    analyses: list[dict[str, object]] = []
    for asset in project.assets:
        if asset.kind != "reference":
            continue
        try:
            analyses.append(analyze_image(asset.path))
        except OSError:
            logger.warning("Could not read reference %s", asset.id)
    return analyses


def _replace_concepts(session, project: Project, concepts: ConceptList) -> None:
    if not concepts.concepts:
        raise ProviderError("The creative director did not return any concepts.")
    for concept in list(project.concepts):
        session.delete(concept)
    session.flush()
    for index, concept in enumerate(concepts.concepts[:4]):
        session.add(
            Concept(
                id=str(uuid4()),
                project_id=project.id,
                position=index,
                name=concept.name[:160],
                hook=concept.hook[:200],
                visual_story=concept.visual_story,
                subject=concept.subject,
                background=concept.background,
                composition=concept.composition,
                text=(concept.text or concept.hook)[:200],
                emotional_direction=concept.emotional_direction[:200],
                why_it_works=concept.why_it_works,
            )
        )
