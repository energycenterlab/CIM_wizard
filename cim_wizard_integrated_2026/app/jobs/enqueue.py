"""Enqueue a Celery task or fail fast if Redis is down."""

from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.jobs.service import job_to_dict, mark_failed


def accepted_payload(job) -> dict:
    body = job_to_dict(job)
    body["poll_url"] = f"{settings.API_V1_STR}/jobs/{job.id}"
    return body


def enqueue_or_503(db: Session, job, task, *args: Any):
    try:
        task.delay(*args)
    except Exception as exc:
        mark_failed(db, job.id, f"Could not enqueue job: {exc}")
        raise HTTPException(
            status_code=503,
            detail=f"Job queue unavailable (Redis/Celery): {exc}",
        ) from exc
    return accepted_payload(job)
