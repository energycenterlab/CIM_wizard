"""Celery tasks for long-running CIM Wizard pipelines."""

from uuid import UUID
import traceback

from app.celery_app import celery
from app.db.database import SessionLocal
from app.jobs.service import mark_failed, mark_running, mark_success, progress_cb
from app.services.building_analysis import (
    job_summary,
    run_assign_pv,
    run_building_analysis,
    run_map_to_citydb,
)


def _session():
    return SessionLocal()


@celery.task(name="app.tasks.heavy.run_building_analysis")
def run_building_analysis_task(job_id: str, request_data: dict, project_id: str, scenario_id: str):
    db = _session()
    jid = UUID(job_id)
    try:
        mark_running(db, jid, step="starting", progress=0.0)
        result = run_building_analysis(
            db, request_data, project_id, scenario_id,
            on_progress=progress_cb(db, jid),
        )
        mark_success(db, jid, job_summary(result))
        return {"status": "success", "project_id": project_id, "scenario_id": scenario_id}
    except Exception:
        mark_failed(db, jid, traceback.format_exc())
        raise
    finally:
        db.close()


@celery.task(name="app.tasks.heavy.run_assign_pv")
def run_assign_pv_task(job_id: str, project_id: str, scenario_id: str, lod: int, offset_m: float):
    db = _session()
    jid = UUID(job_id)
    try:
        mark_running(db, jid, step="assign_pv", progress=0.05)
        result = run_assign_pv(db, project_id, scenario_id, lod, offset_m)
        mark_success(db, jid, result)
        return result
    except Exception:
        mark_failed(db, jid, traceback.format_exc())
        raise
    finally:
        db.close()


@celery.task(name="app.tasks.heavy.run_map_to_citydb")
def run_map_to_citydb_task(
    job_id: str,
    project_id: str,
    scenario_id: str,
    lod12_method: str,
    force_lod12: bool,
    force_remap: bool,
):
    db = _session()
    jid = UUID(job_id)
    try:
        mark_running(db, jid, step="map_to_citydb", progress=0.05)
        result = run_map_to_citydb(
            db, project_id, scenario_id, lod12_method,
            force_lod12=force_lod12, force_remap=force_remap,
        )
        mark_success(db, jid, result)
        return result
    except Exception:
        mark_failed(db, jid, traceback.format_exc())
        raise
    finally:
        db.close()
