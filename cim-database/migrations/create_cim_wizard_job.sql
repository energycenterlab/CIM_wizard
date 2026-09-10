-- Job rows for Celery-backed heavy tasks (create project, PV, CityDB map).
-- Applied automatically by FastAPI/Celery on startup via SQLAlchemy create_all.
-- This file is for manual apply if you prefer:
--   psql -h 130.192.238.11 -p 15432 -U cim_wizard_user \
--        -d cim_wizard_integrated -f create_cim_wizard_job.sql

BEGIN;

CREATE TABLE IF NOT EXISTS cim_vector.cim_wizard_job (
    id            UUID PRIMARY KEY,
    job_type      VARCHAR(64) NOT NULL,
    status        VARCHAR(20) NOT NULL DEFAULT 'queued',
    project_id    VARCHAR(100),
    scenario_id   VARCHAR(100),
    progress      DOUBLE PRECISION NOT NULL DEFAULT 0,
    current_step  VARCHAR(128),
    error         TEXT,
    result        JSONB,
    created_at    TIMESTAMPTZ DEFAULT now(),
    started_at    TIMESTAMPTZ,
    finished_at   TIMESTAMPTZ,
    updated_at    TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_cim_wizard_job_job_type
    ON cim_vector.cim_wizard_job (job_type);
CREATE INDEX IF NOT EXISTS ix_cim_wizard_job_status
    ON cim_vector.cim_wizard_job (status);
CREATE INDEX IF NOT EXISTS ix_cim_wizard_job_project_id
    ON cim_vector.cim_wizard_job (project_id);
CREATE INDEX IF NOT EXISTS ix_cim_wizard_job_scenario_id
    ON cim_vector.cim_wizard_job (scenario_id);

COMMIT;
