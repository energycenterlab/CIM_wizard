"""Background job rows for Celery heavy tasks."""

from sqlalchemy import Column, String, Float, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.database import Base
import uuid


class Job(Base):
    __tablename__ = "cim_wizard_job"
    __table_args__ = {"schema": "cim_vector"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_type = Column(String(64), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="queued", index=True)

    project_id = Column(String(100), nullable=True, index=True)
    scenario_id = Column(String(100), nullable=True, index=True)

    progress = Column(Float, nullable=False, default=0.0)
    current_step = Column(String(128), nullable=True)
    error = Column(Text, nullable=True)
    result = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
