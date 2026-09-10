"""
Building Analysis Pipeline Route - Executes building-specific calculators
Focuses on physical building properties without demographic calculations
"""

from fastapi import APIRouter, Depends, HTTPException, Body, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, List
import json as _json

from app.db.database import get_db
from app.core.data_manager import CimWizardDataManager
from app.core.pipeline_executor import CimWizardPipelineExecutor
from app.core.normalizer import normalize_input, validate
from app.calculators.pv_generator_calculator import DEFAULT_OFFSET_M
from app.jobs.service import create_job, mark_failed, mark_success, progress_cb, json_safe
from app.jobs.enqueue import enqueue_or_503
from app.services.building_analysis import (
    allocate_project_ids,
    job_summary,
    run_assign_pv,
    run_building_analysis,
    run_map_to_citydb,
    scenario_geo_from_boundary,
)

router = APIRouter()


def get_pipeline_executor(db: Session):
    """Create pipeline executor with database session"""
    data_manager = CimWizardDataManager(db_session=db)
    executor = CimWizardPipelineExecutor(data_manager)
    return executor, data_manager


@router.post("/execute_building_analysis")
async def execute_building_analysis(
    request_data: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    Start the building analysis calculator chain.

    Default: enqueue a Celery job and return **202** with ``job_id``.
    Poll ``GET /api/v1/jobs/{job_id}`` until ``status`` is ``success`` or ``failed``.
    Do **not** retry this POST on timeout — each call creates a new project.

    Pass ``"sync": true`` to run in-process (blocks this worker; for curl/debug).
    """
    try:
        request_data = normalize_input("project_scenario", request_data)
        validation_errors = validate("project_scenario", request_data, partial=True)
        if validation_errors:
            print(f"Input validation warnings: {validation_errors}")
        scenario_geo_from_boundary(request_data.get("project_boundary"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    ids = allocate_project_ids(request_data)
    project_id = ids["project_id"]
    scenario_id = ids["scenario_id"]
    job = create_job(db, "building_analysis", project_id, scenario_id)

    if request_data.get("sync"):
        try:
            result = run_building_analysis(
                db, request_data, project_id, scenario_id,
                on_progress=progress_cb(db, job.id),
            )
            mark_success(db, job.id, job_summary(result))
            return result
        except Exception as e:
            mark_failed(db, job.id, str(e))
            raise HTTPException(status_code=500, detail=str(e)) from e

    from app.tasks.heavy import run_building_analysis_task
    payload = enqueue_or_503(
        db, job, run_building_analysis_task,
        str(job.id), json_safe(request_data), project_id, scenario_id,
    )
    return JSONResponse(status_code=202, content=payload)


@router.get("/lod12_geojson")
async def get_lod12_geojson(
    project_id: str,
    scenario_id: str,
    db: Session = Depends(get_db),
):
    """
    Return LoD 1.2 building surfaces as a GeoJSON FeatureCollection.

    Each semantic surface (wall, roof, ground) is emitted as a separate
    Feature with full 3D (Z) coordinates.  The result is directly usable
    by CesiumJS with ``clampToGround: false`` and ``perPositionHeight: true``.

    Query params:
        project_id  – UUID of the project
        scenario_id – UUID of the scenario
    """
    from sqlalchemy import and_
    from app.models.vector import Building, BuildingProperties

    rows = (
        db.query(Building)
        .join(
            BuildingProperties,
            Building.building_id == BuildingProperties.building_id,
        )
        .filter(
            and_(
                BuildingProperties.project_id == project_id,
                BuildingProperties.scenario_id == scenario_id,
            )
        )
        .filter(Building.building_surfaces_lod12.isnot(None))
        .all()
    )

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="No LoD 1.2 data found for this project/scenario",
        )

    features: List[Dict[str, Any]] = []

    for bldg in rows:
        lod12 = bldg.building_surfaces_lod12
        surfaces = lod12.get("surfaces", {})
        metadata = lod12.get("metadata", {})
        building_height = metadata.get("building_height")

        shared_props = {
            "building_id": bldg.building_id,
            "lod": 1.2,
            "building_height": building_height,
        }

        for wall in surfaces.get("wall_surfaces", []):
            features.append({
                "type": "Feature",
                "geometry": wall.get("geometry"),
                "properties": {
                    **shared_props,
                    "surface_type": "WallSurface",
                    "surface_id": wall.get("surface_id"),
                    "area_m2": wall.get("properties", {}).get("area_m2"),
                    "orientation": wall.get("properties", {}).get("orientation"),
                    "azimuth_degrees": wall.get("properties", {}).get("azimuth_degrees"),
                },
            })

        roof = surfaces.get("roof_surface")
        if roof:
            features.append({
                "type": "Feature",
                "geometry": roof.get("geometry"),
                "properties": {
                    **shared_props,
                    "surface_type": "RoofSurface",
                    "surface_id": roof.get("surface_id"),
                    "area_m2": roof.get("properties", {}).get("area_m2"),
                    "roof_type": roof.get("properties", {}).get("roof_type"),
                },
            })

        ground = surfaces.get("ground_surface")
        if ground:
            features.append({
                "type": "Feature",
                "geometry": ground.get("geometry"),
                "properties": {
                    **shared_props,
                    "surface_type": "GroundSurface",
                    "surface_id": ground.get("surface_id"),
                    "area_m2": ground.get("properties", {}).get("area_m2"),
                },
            })

        for floor_s in surfaces.get("floor_surfaces", []):
            features.append({
                "type": "Feature",
                "geometry": floor_s.get("geometry"),
                "properties": {
                    **shared_props,
                    "surface_type": "FloorSurface",
                    "surface_id": floor_s.get("surface_id"),
                    "area_m2": floor_s.get("properties", {}).get("area_m2"),
                    "z_height": floor_s.get("properties", {}).get("height_m"),
                },
            })

    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "project_id": project_id,
            "scenario_id": scenario_id,
            "total_buildings": len(rows),
            "total_surfaces": len(features),
            "lod": 1.2,
            "coordinate_system": "EPSG:4326",
            "height_reference": "relative_to_ground",
        },
    }


# ── Grid generator endpoint ──────────────────────────────────────────

@router.post("/assign_grid")
async def assign_grid(
    request_data: dict = Body(...),
    db: Session = Depends(get_db),
):
    """
    Assign a grid_id to a project scenario.

    Body: { "project_id": "...", "scenario_id": "...", "grid_id": "..." }
    """
    project_id = request_data.get("project_id")
    scenario_id = request_data.get("scenario_id")
    grid_id = request_data.get("grid_id")

    if not all([project_id, scenario_id, grid_id]):
        raise HTTPException(status_code=400, detail="project_id, scenario_id, and grid_id are required")

    executor, data_manager = get_pipeline_executor(db)
    from app.calculators.grid_generator_calculator import GridGeneratorCalculator
    calc = GridGeneratorCalculator(executor)
    result = calc.assign_grid(project_id, scenario_id, grid_id)
    if not result:
        raise HTTPException(status_code=404, detail="grid_id not found or scenario not found")
    return result


@router.get("/grid/{project_id}/{scenario_id}")
async def get_grid_for_scenario(
    project_id: str,
    scenario_id: str,
    db: Session = Depends(get_db),
):
    """
    Get grid data (lines + buses) for a project scenario via its grid_id.
    """
    from sqlalchemy import text

    row = db.execute(
        text("""
            SELECT grid_id FROM cim_vector.cim_wizard_project_scenario
            WHERE project_id = :pid AND scenario_id = :sid
        """),
        {"pid": project_id, "sid": scenario_id},
    ).fetchone()

    if not row or not row[0]:
        raise HTTPException(status_code=404, detail="No grid_id assigned to this scenario")

    grid_id = str(row[0])

    lines = db.execute(text("""
        SELECT nl.*, ST_AsGeoJSON(nl.geometry)::text AS geojson
        FROM cim_network.network_lines nl
        JOIN cim_network.scenario_lines sl ON sl.line_id = nl.line_id
        WHERE sl.grid_id = :gid
    """), {"gid": grid_id}).mappings().all()

    buses = db.execute(text("""
        SELECT nb.*, ST_AsGeoJSON(nb.geometry)::text AS geojson
        FROM cim_network.network_buses nb
        JOIN cim_network.scenario_buses sb ON sb.bus_id = nb.bus_id
        WHERE sb.grid_id = :gid
    """), {"gid": grid_id}).mappings().all()

    import json
    from datetime import date, datetime

    def _row_to_dict(r):
        d = dict(r)
        geojson_str = d.pop("geojson", None)
        geom = d.pop("geometry", None)
        if geojson_str:
            try:
                d["geometry"] = json.loads(geojson_str)
            except json.JSONDecodeError:
                d["geometry"] = None
        for k, v in list(d.items()):
            if isinstance(v, (datetime, date)):
                d[k] = v.isoformat()
        return d

    return {
        "project_id": project_id,
        "scenario_id": scenario_id,
        "grid_id": grid_id,
        "lines": [_row_to_dict(r) for r in lines],
        "buses": [_row_to_dict(r) for r in buses],
    }


# ── PV generator endpoint ────────────────────────────────────────────

@router.post("/assign_pv")
async def assign_pv(
    request_data: dict = Body(...),
    db: Session = Depends(get_db),
):
    """
    Offset spatial join of PV polygons to the buildings of a scenario.

    Body::

        {
            "project_id": "...",
            "scenario_id": "...",
            "lod": 0,
            "offset_m": 2.0
        }

    ``offset_m`` (optional, default 2.0) is the metric tolerance applied to
    each building footprint before matching.  The PV polygons are digitised
    from roofprints, which overhang the footprints, so a tolerance of zero
    would miss them.

    Writes ``cim_wizard_building_properties.pv``, appends the scenario to
    ``pv.scenario_id`` and sets ``cim_wizard_project_scenario.pv_assigned``.
    Re-running withdraws the scenario's previous assignments first.
    """
    project_id = request_data.get("project_id")
    scenario_id = request_data.get("scenario_id")
    lod = request_data.get("lod", 0)
    offset_m = request_data.get("offset_m", DEFAULT_OFFSET_M)

    if not all([project_id, scenario_id]):
        raise HTTPException(status_code=400, detail="project_id and scenario_id are required")

    try:
        offset_m = float(offset_m)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="offset_m must be a number")
    if offset_m < 0:
        raise HTTPException(status_code=400, detail="offset_m must be >= 0")

    job = create_job(db, "assign_pv", project_id, scenario_id)

    if request_data.get("sync"):
        try:
            result = run_assign_pv(db, project_id, scenario_id, int(lod), offset_m)
            mark_success(db, job.id, result)
            return result
        except Exception as e:
            mark_failed(db, job.id, str(e))
            raise HTTPException(status_code=500, detail=str(e)) from e

    from app.tasks.heavy import run_assign_pv_task
    payload = enqueue_or_503(
        db, job, run_assign_pv_task,
        str(job.id), project_id, scenario_id, int(lod), offset_m,
    )
    return JSONResponse(status_code=202, content=payload)


@router.get("/pv_buildings/{project_id}/{scenario_id}")
async def get_pv_with_building_info(
    project_id: str,
    scenario_id: str,
    lod: int = Query(0),
    db: Session = Depends(get_db),
):
    """
    Return all PV polygons assigned to buildings in the given project/scenario,
    enriched with building height (from building_properties) and z_value.

    Joins via ``cim_wizard_building_properties.pv``, so the result is scoped to
    this scenario.  Returns an empty FeatureCollection until
    ``POST /assign_pv`` has run -- check ``pv_assigned`` in the response.
    """
    result = db.execute(text("""
        SELECT
            pv.pv_id,
            b.building_id,
            pv.slope,
            pv.num,
            pv.area_reale,
            pv.number,
            pv.s,
            pv.index_righ,
            pv.id_pod,
            ST_AsGeoJSON(pv.pv_geometry)::text AS pv_geojson,
            b.z_value,
            bp.height                          AS building_height
        FROM cim_vector.cim_wizard_building_properties bp
        JOIN cim_vector.cim_wizard_building b
          ON b.building_id = bp.building_id
         AND b.lod         = bp.lod
        JOIN cim_vector.pv pv
          ON pv.pv_id = ANY(bp.pv)
        WHERE bp.project_id  = :pid
          AND bp.scenario_id = CAST(:sid AS uuid)
          AND bp.lod         = :lod
        ORDER BY bp.building_id, pv.pv_id
    """), {"pid": project_id, "sid": scenario_id, "lod": lod}).mappings().all()

    pv_assigned = db.execute(text("""
        SELECT COALESCE(bool_or(pv_assigned), FALSE)
        FROM cim_vector.cim_wizard_project_scenario
        WHERE project_id = :pid AND scenario_id = CAST(:sid AS uuid)
    """), {"pid": project_id, "sid": scenario_id}).scalar()

    features = []
    for r in result:
        try:
            geom = _json.loads(r["pv_geojson"])
        except Exception:
            geom = None
        features.append({
            "type": "Feature",
            "geometry": geom,
            "properties": {
                "pv_id":            str(r["pv_id"]),
                "building_id":      str(r["building_id"]),
                "slope":            r["slope"],
                "num":              r["num"],
                "area_reale":       r["area_reale"],
                "number":           r["number"],
                "s":                r["s"],
                "index_righ":       r["index_righ"],
                "id_pod":           r["id_pod"],
                "building_height":  r["building_height"],
                "z_value":          r["z_value"],
            },
        })

    return {
        "type": "FeatureCollection",
        "project_id":  project_id,
        "scenario_id": scenario_id,
        "pv_assigned": bool(pv_assigned),
        "total_pv":    len(features),
        "features":    features,
    }


# ── CityDB / CityJSON endpoints ─────────────────────────────────────

@router.post("/map_to_citydb")
async def map_to_citydb(
    request_data: dict = Body(...),
    db: Session = Depends(get_db),
):
    """
    Generate LOD 1.2 geometry and map all buildings in a project-scenario
    to the 3DCityDB ``citydb`` schema.

    Body::

        {
            "project_id": "...",
            "scenario_id": "...",
            "lod12_method": "by_footprint_height"
        }

    ``lod12_method`` (optional, default ``"by_footprint_height"``):

    * ``"by_footprint_height"`` – basic single-zone LOD 1.2
    * ``"by_footprint_height_floors"`` – per-storey walls/floors, one thermal zone per floor
    * ``"by_mixed_use"`` – basement + commercial ground floor + residential
      apartments with per-apartment thermal zones

    ``force_lod12`` (optional, default ``false``): when ``true``,
    regenerate LOD 1.2 even for buildings that already have it.

    ``force_remap`` (optional, default ``false``): when ``true``, delete the
    existing citydb rows for each building and write them again.  Needed to
    refresh buildings that are already mapped, since they are otherwise
    skipped.
    """
    project_id = request_data.get("project_id")
    scenario_id = request_data.get("scenario_id")
    lod12_method = request_data.get("lod12_method", "by_footprint_height")
    force_lod12 = request_data.get("force_lod12", False)
    force_remap = request_data.get("force_remap", False)

    if not all([project_id, scenario_id]):
        raise HTTPException(
            status_code=400,
            detail="project_id and scenario_id are required",
        )

    valid_methods = ("by_footprint_height", "by_footprint_height_floors", "by_mixed_use")
    if lod12_method not in valid_methods:
        raise HTTPException(
            status_code=400,
            detail=f"lod12_method must be one of {valid_methods}",
        )

    job = create_job(db, "map_to_citydb", project_id, scenario_id)

    if request_data.get("sync"):
        try:
            result = run_map_to_citydb(
                db, project_id, scenario_id, lod12_method,
                force_lod12=force_lod12, force_remap=force_remap,
            )
            mark_success(db, job.id, result)
            return result
        except Exception as e:
            mark_failed(db, job.id, str(e))
            raise HTTPException(status_code=500, detail=f"CityDB mapping failed: {e}") from e

    from app.tasks.heavy import run_map_to_citydb_task
    payload = enqueue_or_503(
        db, job, run_map_to_citydb_task,
        str(job.id), project_id, scenario_id, lod12_method,
        bool(force_lod12), bool(force_remap),
    )
    return JSONResponse(status_code=202, content=payload)


@router.get("/cityjson/{citymodel_id}")
async def get_cityjson(
    citymodel_id: str,
    db: Session = Depends(get_db),
):
    """
    Return a CityJSON v1.1 document for a city model.

    ``citymodel_id`` equals the ``scenario_id`` used during
    ``POST /map_to_citydb``.  Reads directly from the 3DCityDB
    ``citydb`` schema including multi-zone thermal zones.

    Requires ``/map_to_citydb`` to have been called first.
    """
    executor, _ = get_pipeline_executor(db)
    from app.calculators.citydb_mapper_calculator import CitydbMapperCalculator

    calc = CitydbMapperCalculator(executor)
    cityjson = calc.generate_cityjson_from_citydb(citymodel_id)

    if cityjson is None:
        raise HTTPException(
            status_code=404,
            detail=f"CityModel '{citymodel_id}' not found",
        )
    if not cityjson.get("CityObjects"):
        raise HTTPException(
            status_code=404,
            detail="CityModel exists but has no mapped buildings",
        )

    return cityjson
