"""Create and update cim_vector.cim_wizard_job rows."""

from datetime import datetime, timezone
from typing import Any, Callable, Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.models.jobs import Job

TERMINAL = ("success", "failed")


def json_safe(obj: Any):
    """Make Celery/Postgres JSONB payloads serializable."""
    import json
    from datetime import date, datetime
    from uuid import UUID as _UUID

    def _default(o):
        if isinstance(o, _UUID):
            return str(o)
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if hasattr(o, "item"):
            try:
                return o.item()
            except Exception:
                pass
        return str(o)

    return json.loads(json.dumps(obj, default=_default))


def create_job(
    db: Session,
    job_type: str,
    project_id: Optional[str] = None,
    scenario_id: Optional[str] = None,
) -> Job:
    job = Job(
        id=uuid4(),
        job_type=job_type,
        status="queued",
        project_id=project_id,
        scenario_id=scenario_id,
        progress=0.0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, job_id: UUID) -> Optional[Job]:
    return db.get(Job, job_id)


def mark_running(db: Session, job_id: UUID, step: str = None, progress: float = None):
    job = db.get(Job, job_id)
    if not job or job.status in TERMINAL:
        return
    if job.status == "queued":
        job.status = "running"
        job.started_at = datetime.now(timezone.utc)
    if step is not None:
        job.current_step = step
    if progress is not None:
        job.progress = progress
    db.commit()


def mark_success(db: Session, job_id: UUID, result: Any = None):
    job = db.get(Job, job_id)
    if not job:
        return
    job.status = "success"
    job.progress = 1.0
    job.result = json_safe(result) if result is not None else None
    job.finished_at = datetime.now(timezone.utc)
    db.commit()


def mark_failed(db: Session, job_id: UUID, error: str):
    job = db.get(Job, job_id)
    if not job:
        return
    job.status = "failed"
    job.error = error[:8000] if error else "unknown error"
    job.finished_at = datetime.now(timezone.utc)
    db.commit()


def progress_cb(db: Session, job_id: UUID) -> Callable[[int, int, str], None]:
    def _cb(step_num: int, total: int, feature: str):
        mark_running(
            db,
            job_id,
            step=f"{step_num}/{total} {feature}",
            progress=step_num / max(total, 1),
        )
    return _cb


def job_to_dict(job: Job) -> dict:
    return {
        "job_id": str(job.id),
        "job_type": job.job_type,
        "status": job.status,
        "project_id": job.project_id,
        "scenario_id": job.scenario_id,
        "progress": job.progress,
        "current_step": job.current_step,
        "error": job.error,
        "result": job.result,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "finished_at": job.finished_at.isoformat() if job.finished_at else None,
    }
