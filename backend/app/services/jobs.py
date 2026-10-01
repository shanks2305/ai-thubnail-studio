import logging
import threading
from uuid import uuid4

from fastapi import BackgroundTasks

from app.core.database import session_scope
from app.db.library import StudioJob
from app.db.models import AgentRun, Project, utcnow

logger = logging.getLogger(__name__)
BUSY = {"analyzing", "generating"}


def enqueue(background: BackgroundTasks, kind: str, project_id: str, payload: dict | None = None) -> str:
    job_id = str(uuid4())
    with session_scope() as session:
        session.add(
            StudioJob(id=job_id, project_id=project_id, kind=kind, payload=payload or {}, status="queued")
        )
    background.add_task(execute_job, job_id)
    return job_id


def execute_job(job_id: str) -> None:
    kind, project_id, payload = _claim(job_id)
    if kind is None or project_id is None:
        return
    try:
        _dispatch(kind, project_id, payload)
    except Exception:
        logger.exception("Job %s failed", job_id)
        _finish(job_id, "failed", "The thumbnail workflow stopped before it finished.")
        return
    with session_scope() as session:
        project = session.get(Project, project_id)
        failed = project is not None and project.status == "failed"
        error = project.error if project is not None else None
    _finish(job_id, "failed" if failed else "done", error if failed else None)


def recover_jobs() -> None:
    with session_scope() as session:
        for run in session.query(AgentRun).filter_by(status="running"):
            run.status = "failed"
            run.error = "Stopped when the server restarted."
            run.finished_at = utcnow()
        jobs = session.query(StudioJob).filter(StudioJob.status.in_(["queued", "running"])).all()
        job_ids = [job.id for job in jobs]
        projects_with_jobs = {job.project_id for job in jobs}
        for job in jobs:
            job.status = "queued"
        for project in session.query(Project).filter(Project.status.in_(BUSY)):
            if project.id not in projects_with_jobs:
                project.status = "failed"
                project.error = "The run stopped when the server restarted. Start it again."
                project.updated_at = utcnow()
    for job_id in job_ids:
        threading.Thread(target=execute_job, args=(job_id,), daemon=True).start()


def _claim(job_id: str) -> tuple[str | None, str | None, dict]:
    with session_scope() as session:
        job = session.get(StudioJob, job_id)
        if job is None or job.status == "done":
            return None, None, {}
        job.status = "running"
        job.started_at = utcnow()
        return job.kind, job.project_id, dict(job.payload or {})


def _finish(job_id: str, status: str, error: str | None) -> None:
    with session_scope() as session:
        job = session.get(StudioJob, job_id)
        if job is None:
            return
        job.status = status
        job.error = error
        job.finished_at = utcnow()


def _dispatch(kind: str, project_id: str, payload: dict) -> None:
    if kind == "concepts":
        from app.agents.concept_pipeline import run_concept_pipeline

        run_concept_pipeline(project_id, archive=bool(payload.get("archive")))
        return
    if kind == "thumbnail":
        from app.agents.thumbnail_pipeline import run_thumbnail_pipeline

        run_thumbnail_pipeline(project_id, str(payload["concept_id"]))
        return
    if kind == "batch":
        _batch(project_id)
        return
    if kind == "variation":
        from app.agents.variations import run_visual_variation

        run_visual_variation(project_id, str(payload["generation_id"]), str(payload["axis"]))
        return
    if kind == "rerender":
        from app.agents.variations import run_rerender

        run_rerender(project_id, str(payload["generation_id"]), str(payload.get("instruction") or ""))


def _batch(project_id: str) -> None:
    from app.agents.thumbnail_pipeline import run_thumbnail_pipeline

    with session_scope() as session:
        project = session.get(Project, project_id)
        if project is None:
            return
        concept_ids = [concept.id for concept in project.concepts if not concept.archived]
    for index, concept_id in enumerate(concept_ids):
        run_thumbnail_pipeline(project_id, concept_id, finalize=index == len(concept_ids) - 1)
        with session_scope() as session:
            project = session.get(Project, project_id)
            if project is None or project.status == "failed":
                return
