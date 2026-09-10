"""Job status API for Celery-backed heavy tasks."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.jobs.service import get_job, job_to_dict
from app.models.jobs import Job

router = APIRouter()


@router.get("/")
def list_jobs(
    project_id: str = Query(None),
    status: str = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Job).order_by(Job.created_at.desc())
    if project_id:
        q = q.filter(Job.project_id == project_id)
    if status:
        q = q.filter(Job.status == status)
    jobs = q.limit(limit).all()
    return {"jobs": [job_to_dict(j) for j in jobs]}


@router.get("/{job_id}")
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    try:
        jid = UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="job_id must be a UUID")
    job = get_job(db, jid)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_to_dict(job)
