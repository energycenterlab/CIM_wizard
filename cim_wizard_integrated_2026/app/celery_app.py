"""Celery application for CIM Wizard heavy tasks."""

import os
from celery import Celery
from celery.signals import worker_process_init

BROKER = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

celery = Celery(
    "cim_wizard",
    broker=BROKER,
    backend=BACKEND,
    include=["app.tasks.heavy"],
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_queue="heavy",
    task_routes={
        "app.tasks.heavy.*": {"queue": "heavy"},
    },
)


@worker_process_init.connect
def _init_worker(**_kwargs):
    """Avoid forked SQLAlchemy connections; ensure the job table exists."""
    from app.db.database import engine, Base
    from app.models.jobs import Job  # noqa: F401
    engine.dispose()
    Base.metadata.create_all(bind=engine, tables=[Job.__table__])
