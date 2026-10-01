from fastapi import APIRouter, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.access import current_owner
from app.api.library import visible_to_owner
from app.api.projects import require_project
from app.core.database import session_scope
from app.db.library import BrandKit, Channel, CreatorProfile, Experiment
from app.db.models import Asset, Concept, Generation, Project, utcnow
from app.tools.storage import delete_file

router = APIRouter()
_BUSY = {"analyzing", "generating"}
_LOOSE_IMAGES = {"reference", "face", "person", "video_person", "popular"}


@router.delete("/brand-kits/{kit_id}", status_code=204)
def delete_brand_kit(kit_id: str) -> None:
    with session_scope() as session:
        kit = _owned(session, BrandKit, kit_id, "Brand kit")
        if kit.logo_path:
            delete_file(kit.logo_path)
        _clear(session, Project.brand_kit_id, kit.id)
        session.delete(kit)


@router.delete("/profiles/{profile_id}", status_code=204)
def delete_profile(profile_id: str) -> None:
    with session_scope() as session:
        profile = _owned(session, CreatorProfile, profile_id, "Saved style")
        _clear(session, Project.creator_profile_id, profile.id)
        session.delete(profile)


@router.delete("/channels/{channel_id}", status_code=204)
def delete_channel(channel_id: str) -> None:
    with session_scope() as session:
        channel = _owned(session, Channel, channel_id, "Channel")
        _clear(session, Project.channel_id, channel.id)
        session.delete(channel)


@router.delete("/experiments/{experiment_id}", status_code=204)
def delete_experiment(experiment_id: str) -> None:
    with session_scope() as session:
        experiment = session.get(Experiment, experiment_id)
        if experiment is None:
            raise HTTPException(status_code=404, detail="Experiment not found.")
        _idle_owner(session, experiment.project_id)
        session.delete(experiment)


@router.delete("/assets/{asset_id}", status_code=204)
def delete_asset(asset_id: str) -> None:
    with session_scope() as session:
        asset = session.get(Asset, asset_id)
        if asset is None:
            raise HTTPException(status_code=404, detail="Asset not found.")
        _idle_owner(session, asset.project_id)
        if asset.kind not in _LOOSE_IMAGES:
            raise HTTPException(status_code=400, detail="Delete the thumbnail this image belongs to.")
        _drop_asset(session, asset)


@router.delete("/concepts/{concept_id}", status_code=204)
def delete_concept(concept_id: str) -> None:
    with session_scope() as session:
        concept = session.get(Concept, concept_id)
        if concept is None:
            raise HTTPException(status_code=404, detail="Concept not found.")
        project = _idle_owner(session, concept.project_id)
        for generation in session.query(Generation).filter_by(concept_id=concept.id):
            _remove_generation(session, project, generation)
        if project.selected_concept_id == concept.id:
            project.selected_concept_id = None
        session.delete(concept)
        _settle(session, project)


@router.delete("/generations/{generation_id}", status_code=204)
def delete_generation(generation_id: str) -> None:
    with session_scope() as session:
        generation = session.get(Generation, generation_id)
        if generation is None:
            raise HTTPException(status_code=404, detail="Thumbnail not found.")
        project = _idle_owner(session, generation.project_id)
        _remove_generation(session, project, generation)
        _settle(session, project)


def _owned(session: Session, model, row_id: str, label: str):
    row = session.get(model, row_id)
    if row is None or not visible_to_owner(row):
        raise HTTPException(status_code=404, detail=f"{label} not found.")
    if row.owner_id != current_owner():
        raise HTTPException(status_code=403, detail=f"Only the owner can delete this {label.lower()}.")
    return row


def _idle_owner(session: Session, project_id: str) -> Project:
    project = require_project(session, project_id)
    if project.owner_id != current_owner():
        raise HTTPException(status_code=403, detail="Only the owner can delete this.")
    if project.status in _BUSY:
        raise HTTPException(status_code=409, detail="Wait until the current run finishes.")
    return project


def _clear(session: Session, column, value: str) -> None:
    session.query(Project).filter(column == value).update({column: None}, synchronize_session=False)


def _remove_generation(session: Session, project: Project, generation: Generation) -> None:
    _drop_asset(session, generation.image_asset_id)
    _drop_asset(session, generation.background_asset_id)
    session.query(Experiment).filter(
        or_(Experiment.generation_a_id == generation.id, Experiment.generation_b_id == generation.id)
    ).delete(synchronize_session=False)
    if project.selected_generation_id == generation.id:
        project.selected_generation_id = None
    session.delete(generation)


def _drop_asset(session: Session, asset_or_id: Asset | str | None) -> None:
    asset = asset_or_id if isinstance(asset_or_id, Asset) else session.get(Asset, asset_or_id) if asset_or_id else None
    if asset is None:
        return
    delete_file(asset.path)
    session.delete(asset)


def _settle(session: Session, project: Project) -> None:
    session.flush()
    if project.status not in {"ready", "concepts_ready"}:
        return
    renders = session.query(Generation).filter_by(project_id=project.id).count()
    concepts = session.query(Concept).filter_by(project_id=project.id, archived=False).count()
    project.status = "ready" if renders else "concepts_ready" if concepts else "draft"
    project.updated_at = utcnow()
