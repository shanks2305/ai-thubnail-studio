from datetime import datetime, timezone

from app.db.models import AgentRun, Asset, Concept, Generation, Project


def _utc_iso(value: datetime) -> str:
    # SQLite drops tzinfo on read; stored values are always UTC.
    return value.replace(tzinfo=value.tzinfo or timezone.utc).isoformat()


def present_project_summary(project: Project) -> dict:
    cover_id = _cover_id(project)
    return {
        "id": project.id,
        "title": project.title,
        "description": project.description,
        "status": project.status,
        "favorite": project.favorite,
        "shared": project.shared,
        "youtube_url": project.youtube_url,
        "updated_at": _utc_iso(project.updated_at),
        "cover_url": f"/api/assets/{cover_id}" if cover_id else None,
    }


def present_project(project: Project) -> dict:
    return {
        **present_project_summary(project),
        "youtube_title": project.youtube_title,
        "error": project.error,
        "selected_concept_id": project.selected_concept_id,
        "selected_generation_id": project.selected_generation_id,
        "brand_kit_id": project.brand_kit_id,
        "creator_profile_id": project.creator_profile_id,
        "channel_id": project.channel_id,
        "audience_brief": project.audience_brief,
        "video_brief": project.video_brief,
        "reference_profile": project.reference_profile,
        "hooks": project.hooks or [],
        "concepts": [_concept(concept) for concept in project.concepts],
        "generations": [present_generation(generation) for generation in project.generations],
        "agent_runs": [_run(run) for run in project.agent_runs],
        "references": [_reference(asset) for asset in project.assets if asset.kind == "reference"],
        "face": _face(project),
        "experiments": _experiments(project),
        "created_at": _utc_iso(project.created_at),
    }


def present_generation(generation: Generation) -> dict:
    critique = generation.critique
    return {
        "id": generation.id,
        "concept_id": generation.concept_id,
        "attempt": generation.attempt,
        "variation_axis": generation.variation_axis,
        "source_generation_id": generation.source_generation_id,
        "impressions": generation.impressions,
        "clicks": generation.clicks,
        "image_url": f"/api/assets/{generation.image_asset_id}" if generation.image_asset_id else None,
        "design_spec": generation.design_spec,
        "critique": None
        if critique is None
        else {
            "overall": critique.overall,
            "passed": critique.passed,
            "issues": critique.issues,
            "recommended_changes": critique.recommended_changes,
        },
    }


def _concept(concept: Concept) -> dict:
    return {
        "id": concept.id,
        "name": concept.name,
        "hook": concept.hook,
        "visual_story": concept.visual_story,
        "subject": concept.subject,
        "background": concept.background,
        "composition": concept.composition,
        "text": concept.text,
        "emotional_direction": concept.emotional_direction,
        "why_it_works": concept.why_it_works,
        "image_prompt": concept.image_prompt,
        "archived": concept.archived,
    }


def _run(run: AgentRun) -> dict:
    return {
        "id": run.id,
        "agent": run.agent,
        "status": run.status,
        "provider": run.provider,
        "model": run.model,
        "error": run.error,
        "input_tokens": run.input_tokens,
        "output_tokens": run.output_tokens,
        "duration_ms": _duration_ms(run),
    }


def _reference(asset: Asset) -> dict:
    return {"id": asset.id, "url": f"/api/assets/{asset.id}"}


def _cover_id(project: Project) -> str | None:
    if project.selected_generation_id:
        selected = next((item for item in project.generations if item.id == project.selected_generation_id), None)
        if selected is not None and selected.image_asset_id:
            return selected.image_asset_id
    return next((item.image_asset_id for item in reversed(project.generations) if item.image_asset_id), None)


def _face(project: Project) -> dict | None:
    asset = next((item for item in project.assets if item.kind == "face"), None)
    if asset is None:
        return None
    return {"id": asset.id, "url": f"/api/assets/{asset.id}"}


def _experiments(project: Project) -> list[dict]:
    from sqlalchemy.orm import object_session

    from app.db.library import Experiment

    session = object_session(project)
    if session is None:
        return []
    rows = session.query(Experiment).filter_by(project_id=project.id).all()
    return [
        {
            "id": row.id,
            "generation_a_id": row.generation_a_id,
            "generation_b_id": row.generation_b_id,
            "winner_id": row.winner_id,
            "notes": row.notes,
        }
        for row in rows
    ]


def _duration_ms(run: AgentRun) -> int | None:
    if run.finished_at is None:
        return None
    return max(0, int((run.finished_at - run.started_at).total_seconds() * 1000))
