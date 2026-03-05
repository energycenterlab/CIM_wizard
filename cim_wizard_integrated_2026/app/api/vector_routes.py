"""
Vector Gateway Routes - All endpoints from vector_gateway_service
FastAPI implementation for CIM Wizard Integrated

All database access goes through CimWizardDataManager so that this
module contains only request/response logic.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app.db.database import get_db
from app.core.data_manager import CimWizardDataManager
from app.core.normalizer import (
    normalize_input, normalize_output, validate,
    normalize_geojson_properties, get_client_schema,
    get_schema as get_entity_schema, get_entity_names,
)


router = APIRouter()


def _dm(db: Session) -> CimWizardDataManager:
    """Shortcut: build a DataManager bound to the current request session."""
    return CimWizardDataManager(db_session=db)


# ── Project / Scenario endpoints ──────────────────────────────────────

@router.get("/projects")
async def get_all_projects(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get all projects with pagination"""
    try:
        return _dm(db).list_projects(offset=offset, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/dashboard")
async def project_dashboard(db: Session = Depends(get_db)):
    """Get project dashboard with summary statistics"""
    try:
        return _dm(db).get_dashboard()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/pscenarios/{project_id}")
async def get_project_scenarios(
    project_id: str,
    db: Session = Depends(get_db),
):
    """Get all scenarios for a specific project"""
    try:
        dm = _dm(db)
        scenarios = dm.get_scenarios_for_project(project_id)
        if not scenarios:
            raise HTTPException(status_code=404, detail="Project not found")
        return scenarios
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/projects/{project_id}/scenarios")
async def create_scenario(
    project_id: str,
    request_body: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
):
    """
    Create a new scenario for a project based on the baseline scenario.
    """
    scenario_name = request_body.get("scenario_name")
    if not scenario_name or not str(scenario_name).strip():
        raise HTTPException(status_code=400, detail="scenario_name is required and cannot be empty")

    try:
        dm = _dm(db)
        result = dm.create_scenario_from_baseline(project_id, str(scenario_name))
        if result is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Project not found or baseline scenario missing for project_id '{project_id}'. "
                    "Verify the project exists via GET /api/v1/vector/projects and "
                    "GET /api/v1/vector/pscenarios/{project_id}"
                ),
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create scenario: {str(e)}")


@router.get("/project_scenario_details/{project_id}/{scenario_id}")
async def get_project_scenario_details(
    project_id: str,
    scenario_id: str,
    db: Session = Depends(get_db),
):
    """Get details for a specific project scenario"""
    try:
        dm = _dm(db)
        scenario = dm.get_scenario(project_id, scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Project scenario not found")
        return scenario
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ── Building geometry endpoints ───────────────────────────────────────

@router.get("/bgeo/{building_id}")
async def get_building_geometry(
    building_id: str,
    lod: Optional[int] = Query(0),
    db: Session = Depends(get_db),
):
    """Get building geometry by building ID"""
    try:
        dm = _dm(db)
        building = dm.get_building(building_id, lod=lod)
        if not building:
            raise HTTPException(status_code=404, detail="Building not found")
        return building
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/get_buildings_geojson/{project_id}/{scenario_id}")
async def get_buildings_geojson(
    project_id: str,
    scenario_id: str,
    lod: Optional[int] = Query(0),
    db: Session = Depends(get_db),
):
    """
    Get all buildings for a project scenario as GeoJSON.
    Handles baseline and delta merging automatically.
    """
    try:
        return _dm(db).get_buildings_geojson(project_id, scenario_id, lod=lod)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ── Building properties endpoints ─────────────────────────────────────

@router.get("/buildingproperties/{project_id}/{scenario_id}")
async def query_building_properties(
    project_id: str,
    scenario_id: str,
    building_id: Optional[str] = Query(None),
    lod: Optional[int] = Query(0),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Query building properties for a project scenario.
    Handles baseline / delta merging.
    """
    try:
        return _dm(db).get_building_properties(
            project_id, scenario_id,
            building_id=building_id, lod=lod,
            offset=offset, limit=limit,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


_BP_EDITABLE_FIELDS = {
    "height", "area", "volume", "number_of_floors",
    "type", "const_period_census", "const_year", "const_tabula",
    "n_people", "n_family", "envelope_efficiency", "fmu_file",
}


@router.put("/projects/{project_id}/scenarios/{scenario_id}/buildingproperties")
async def upsert_building_properties(
    project_id: str,
    scenario_id: str,
    request_body: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
):
    """
    Store or update modified building properties for a non-baseline scenario.
    Rejects if scenario_id == project_id.
    """
    if scenario_id == project_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot modify baseline scenario via this endpoint. Use pipeline/calculators for baseline.",
        )

    dm = _dm(db)
    scenario = dm.get_scenario(project_id, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    if "modifications" in request_body:
        modifications = request_body["modifications"]
        if not isinstance(modifications, list):
            raise HTTPException(status_code=400, detail="modifications must be a list")
    else:
        modifications = [request_body]

    if not modifications:
        raise HTTPException(status_code=400, detail="At least one modification required")

    try:
        upserted = 0
        for mod in modifications:
            building_id = mod.get("building_id")
            if not building_id:
                raise HTTPException(status_code=400, detail="building_id is required in each modification")
            lod = mod.get("lod", 0)

            updates = {k: v for k, v in mod.items() if k in _BP_EDITABLE_FIELDS}
            if not updates:
                raise HTTPException(
                    status_code=400,
                    detail=f"No editable fields provided for building_id '{building_id}'",
                )

            dm.upsert_building_property_fields(
                project_id, scenario_id, building_id, lod, **updates,
            )
            upserted += 1

        return {"upserted": upserted, "scenario_id": scenario_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to upsert building properties: {str(e)}")


# ── Spatial query endpoints ───────────────────────────────────────────

@router.get("/building_id_fetcher")
async def building_id_fetcher(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    db: Session = Depends(get_db),
):
    """Fetch building IDs at a specific point"""
    try:
        return {"buildings": _dm(db).get_buildings_at_point(lng, lat)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/building_id_fetcher_buffer")
async def building_id_fetcher_buffer(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    buffer_m: float = Query(10, description="Buffer in meters"),
    db: Session = Depends(get_db),
):
    """Fetch building IDs within a buffer of a point"""
    try:
        return {
            "buildings": _dm(db).get_buildings_in_buffer(lng, lat, buffer_m),
            "buffer_m": buffer_m,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ── Delete endpoints ──────────────────────────────────────────────────

@router.delete("/delete")
async def delete_project_data(
    project_id: str = Query(..., description="Project ID (required)"),
    scenario_id: Optional[str] = Query(None, description="Scenario ID (optional)"),
    building_id: Optional[str] = Query(None, description="Building ID (optional)"),
    db: Session = Depends(get_db),
):
    """
    Flexible delete endpoint.

    1. project_id + scenario_id + building_id -- delete one building
    2. project_id + scenario_id              -- delete one scenario + its buildings
    3. project_id only                       -- delete entire project
    """
    try:
        dm = _dm(db)
        deleted = dm.delete_project_data(project_id, scenario_id, building_id)

        if project_id and scenario_id and building_id:
            action = "delete_building"
        elif project_id and scenario_id:
            action = "delete_scenario"
        else:
            action = "delete_project"

        return {
            "action": action,
            "project_id": project_id,
            **({"scenario_id": scenario_id} if scenario_id else {}),
            **({"building_id": building_id} if building_id else {}),
            **deleted,
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


# ── Schema discovery endpoints ────────────────────────────────────────

@router.get("/schema")
async def get_normalization_schema():
    """Return the full normalization schema for all entities."""
    return get_client_schema()


@router.get("/schema/{entity_name}")
async def get_entity_normalization_schema(entity_name: str):
    """Return the normalization schema for a single entity."""
    schema = get_entity_schema(entity_name)
    if schema is None:
        available = get_entity_names()
        raise HTTPException(
            status_code=404,
            detail=f"Entity '{entity_name}' not found. Available: {available}",
        )
    return {
        "entity": entity_name,
        "description": schema.get("description", ""),
        "table": schema.get("table", ""),
        "fields": schema.get("fields", {}),
    }


@router.get("/health")
async def vector_health():
    """Health check for vector gateway routes"""
    return {"status": "healthy", "service": "vector_gateway"}
