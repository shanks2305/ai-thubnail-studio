from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.api.schemas import CreateProjectBody, UpdateProjectBody, title_from_description
from app.api.serialize import present_project, present_project_summary
from app.core.database import session_scope
from app.db.models import Project, utcnow
from app.providers.router import system_status
from app.services.events import bus
from app.tools.storage import delete_project_files

router = APIRouter()


def require_project(session, project_id: str) -> Project:
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    return project


@router.get("/system")
def read_system() -> dict[str, object]:
    return system_status()


@router.get("/projects")
def list_projects() -> list[dict]:
    with session_scope() as session:
        projects = session.query(Project).order_by(Project.updated_at.desc()).all()
        return [present_project_summary(project) for project in projects]


@router.post("/projects", status_code=201)
def create_project(body: CreateProjectBody) -> dict:
    project = Project(
        id=str(uuid4()),
        title=title_from_description(body.description),
        description=body.description.strip(),
        youtube_url=body.youtube_url,
        privacy_mode=body.privacy_mode,
    )
    with session_scope() as session:
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
        project.updated_at = utcnow()
        session.flush()
        return present_project(project)


@router.delete("/projects/{project_id}", status_code=204)
def delete_project(project_id: str) -> None:
    with session_scope() as session:
        project = require_project(session, project_id)
        if project.status in {"analyzing", "generating"}:
            raise HTTPException(status_code=409, detail="Wait until the current run finishes.")
        session.delete(project)
    bus.clear_project(project_id)
    delete_project_files(project_id)
