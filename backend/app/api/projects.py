from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.api.access import current_owner
from app.api.schemas import CreateProjectBody, UpdateProjectBody, title_from_description
from app.api.serialize import present_project, present_project_summary
from app.core.database import session_scope
from app.db.library import BrandKit, Channel, CreatorProfile
from app.db.models import Project, utcnow
from app.providers.router import system_status
from app.services.events import bus
from app.tools.storage import delete_project_files

router = APIRouter()


def can_view(project: Project) -> bool:
    return project.owner_id == current_owner() or bool(project.shared)


def require_project(session, project_id: str) -> Project:
    project = session.get(Project, project_id)
    if project is None or not can_view(project):
        raise HTTPException(status_code=404, detail="Project not found.")
    return project


@router.get("/system")
def read_system() -> dict[str, object]:
    return system_status()


@router.get("/projects")
def list_projects() -> list[dict]:
    owner = current_owner()
    with session_scope() as session:
        projects = (
            session.query(Project)
            .filter((Project.owner_id == owner) | (Project.shared.is_(True)))
            .order_by(Project.updated_at.desc())
            .all()
        )
        return [present_project_summary(project) for project in projects]


@router.post("/projects", status_code=201)
def create_project(body: CreateProjectBody) -> dict:
    project = Project(
        id=str(uuid4()),
        title=title_from_description(body.description),
        description=body.description.strip(),
        youtube_url=body.youtube_url,
        owner_id=current_owner(),
        shared=body.shared,
    )
    with session_scope() as session:
        _assign_library(session, project, body)
        session.add(project)
        session.flush()
        return present_project(project)


@router.get("/projects/{project_id}")
def get_project(project_id: str) -> dict:
    with session_scope() as session:
        return present_project(require_project(session, project_id))


@router.patch("/projects/{project_id}")
def update_project(project_id: str, body: UpdateProjectBody) -> dict:
    with session_scope() as session:
        project = require_project(session, project_id)
        if body.favorite is not None:
            project.favorite = body.favorite
        if body.shared is not None:
            if project.owner_id != current_owner():
                raise HTTPException(status_code=403, detail="Only the owner can share this project.")
            project.shared = body.shared
        project.updated_at = utcnow()
        session.flush()
        return present_project(project)


@router.delete("/projects/{project_id}", status_code=204)
def delete_project(project_id: str) -> None:
    with session_scope() as session:
        project = require_project(session, project_id)
        if project.owner_id != current_owner():
            raise HTTPException(status_code=403, detail="Only the owner can delete this project.")
        if project.status in {"analyzing", "generating"}:
            raise HTTPException(status_code=409, detail="Wait until the current run finishes.")
        session.delete(project)
    bus.clear_project(project_id)
    delete_project_files(project_id)


def _assign_library(session, project: Project, body: CreateProjectBody) -> None:
    if body.brand_kit_id:
        kit = session.get(BrandKit, body.brand_kit_id)
        if kit is None or not (kit.owner_id == current_owner() or kit.shared):
            raise HTTPException(status_code=400, detail="Choose a brand kit you can use.")
        project.brand_kit_id = kit.id
    if body.creator_profile_id:
        profile = session.get(CreatorProfile, body.creator_profile_id)
        if profile is None or not (profile.owner_id == current_owner() or profile.shared):
            raise HTTPException(status_code=400, detail="Choose a creator profile you can use.")
        project.creator_profile_id = profile.id
    if body.channel_id:
        channel = session.get(Channel, body.channel_id)
        if channel is None or channel.owner_id != current_owner():
            raise HTTPException(status_code=400, detail="Choose a channel you own.")
        project.channel_id = channel.id

