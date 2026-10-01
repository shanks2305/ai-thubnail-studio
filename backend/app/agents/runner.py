import logging
from typing import TypeVar
from uuid import uuid4

from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.db.models import AgentRun, Project, utcnow
from app.providers.base import ProviderError
from app.providers.json_text import extract_json
from app.providers.router import ModelRouter
from app.services.events import publish

logger = logging.getLogger(__name__)
router = ModelRouter()
T = TypeVar("T", bound=BaseModel)


def public_error(exc: Exception) -> str:
    if isinstance(exc, ProviderError):
        return str(exc)[:300]
    if isinstance(exc, ValidationError):
        return "The model returned a result the studio could not read."
    return "The thumbnail workflow stopped before it finished."


def run_structured(session: Session, project: Project, task: str, payload: dict, model: type[T]) -> T:
    run = _start(session, project.id, task)
    try:
        response = router.generate(task=task, payload=payload, privacy_mode=project.privacy_mode)
        parsed = model.model_validate_json(extract_json(response.content))
    except Exception as exc:
        _finish(session, run, "failed", error=public_error(exc))
        publish(project.id, {"type": "agent_failed", "agent": task, "message": run.error})
        raise
    _finish(session, run, "completed", provider=response.provider, model_name=response.model, output=parsed.model_dump())
    publish(project.id, {"type": "agent_completed", "agent": task, "provider": response.provider})
    return parsed


def record_step(session: Session, project_id: str, agent: str, provider: str, model_name: str, output: dict) -> None:
    now = utcnow()
    session.add(
        AgentRun(
            id=str(uuid4()),
            project_id=project_id,
            agent=agent,
            status="completed",
            provider=provider,
            model=model_name,
            output=output,
            started_at=now,
            finished_at=now,
        )
    )
    session.commit()
    publish(project_id, {"type": "agent_completed", "agent": agent, "provider": provider})


def mark_failed(project_id: str, message: str) -> None:
    from app.core.database import session_scope

    with session_scope() as session:
        project = session.get(Project, project_id)
        if project is None:
            return
        project.status = "failed"
        project.error = message
        project.updated_at = utcnow()
    publish(project_id, {"type": "job_failed", "message": message})


def _start(session: Session, project_id: str, task: str) -> AgentRun:
    run = AgentRun(id=str(uuid4()), project_id=project_id, agent=task, status="running")
    session.add(run)
    session.commit()
    publish(project_id, {"type": "agent_started", "agent": task})
    return run


def _finish(
    session: Session,
    run: AgentRun,
    status: str,
    provider: str | None = None,
    model_name: str | None = None,
    output: dict | None = None,
    error: str | None = None,
) -> None:
    run.status = status
    run.provider = provider
    run.model = model_name
    run.output = output
    run.error = error
    run.finished_at = utcnow()
    session.commit()
