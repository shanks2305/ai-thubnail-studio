from app.db.models import AgentRun, Asset, Concept, Generation, Project


def present_project_summary(project: Project) -> dict:
    cover_id = next((item.image_asset_id for item in reversed(project.generations) if item.image_asset_id), None)
    return {
        "id": project.id,
        "title": project.title,
        "description": project.description,
        "status": project.status,
        "favorite": project.favorite,
        "youtube_url": project.youtube_url,
        "updated_at": project.updated_at.isoformat(),
        "cover_url": f"/api/assets/{cover_id}" if cover_id else None,
    }


def present_project(project: Project) -> dict:
    return {
        **present_project_summary(project),
        "youtube_title": project.youtube_title,
        "error": project.error,
        "selected_concept_id": project.selected_concept_id,
        "video_brief": project.video_brief,
        "reference_profile": project.reference_profile,
        "hooks": project.hooks or [],
        "concepts": [_concept(concept) for concept in project.concepts],
        "generations": [present_generation(generation) for generation in project.generations],
        "agent_runs": [_run(run) for run in project.agent_runs],
        "references": [_reference(asset) for asset in project.assets if asset.kind == "reference"],
        "created_at": project.created_at.isoformat(),
    }


def present_generation(generation: Generation) -> dict:
    critique = generation.critique
    return {
        "id": generation.id,
        "concept_id": generation.concept_id,
        "attempt": generation.attempt,
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
    }


def _run(run: AgentRun) -> dict:
    return {
        "id": run.id,
        "agent": run.agent,
        "status": run.status,
        "provider": run.provider,
        "model": run.model,
        "error": run.error,
    }


def _reference(asset: Asset) -> dict:
    return {"id": asset.id, "url": f"/api/assets/{asset.id}"}
