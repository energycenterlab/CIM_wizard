"""
Vector Gateway Routes - All endpoints from vector_gateway_service
FastAPI implementation for CIM Wizard Integrated
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping
import json
import uuid

from app.db.database import get_db
from app.models.vector import (
    ProjectScenario, Building, BuildingProperties, 
    
)
from app.core.normalizer import (
    normalize_input, normalize_output, validate,
    normalize_geojson_properties, get_client_schema,
    get_schema as get_entity_schema, get_entity_names,
)


router = APIRouter()


@router.get("/projects")
async def get_all_projects(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all projects with pagination"""
    try:
        projects = db.query(ProjectScenario).offset(offset).limit(limit).all()
        serialized = []
        for p in projects:
            item = {
                "project_id": p.project_id,
                "scenario_id": p.scenario_id,
                "project_name": p.project_name,
                "scenario_name": p.scenario_name,
                "project_zoom": p.project_zoom,
                "project_crs": p.project_crs,
                "created_at": p.created_at,
                "updated_at": p.updated_at,
            }
            # Serialize geometries safely
            try:
                if p.project_boundary is not None:
                    geom_shape = to_shape(p.project_boundary)
                    item["project_boundary"] = mapping(geom_shape)
            except Exception:
                item["project_boundary"] = None
            try:
                if p.project_center is not None:
                    center_shape = to_shape(p.project_center)
                    item["project_center"] = mapping(center_shape)
            except Exception:
                item["project_center"] = None
            serialized.append(item)
        return serialized
    except Exception as e:
        # Possible errors: Database connection issues
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/dashboard")
async def project_dashboard(db: Session = Depends(get_db)):
    """Get project dashboard with summary statistics"""
    try:
        total_projects = db.query(ProjectScenario).count()
        projects = db.query(ProjectScenario).limit(10).all()
        serialized = []
        for p in projects:
            item = {
                "project_id": p.project_id,
                "scenario_id": p.scenario_id,
                "project_name": p.project_name,
                "scenario_name": p.scenario_name,
                "project_zoom": p.project_zoom,
                "project_crs": p.project_crs,
                "created_at": p.created_at,
                "updated_at": p.updated_at,
            }
            try:
                if p.project_boundary is not None:
                    item["project_boundary"] = mapping(to_shape(p.project_boundary))
            except Exception:
                item["project_boundary"] = None
            try:
                if p.project_center is not None:
                    item["project_center"] = mapping(to_shape(p.project_center))
            except Exception:
                item["project_center"] = None
            serialized.append(item)
        
        return {
            "total_projects": total_projects,
            "projects": serialized
        }
    except Exception as e:
        # Possible errors: Database connection issues
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/pscenarios/{project_id}")
async def get_project_scenarios(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Get all scenarios for a specific project"""
    try:
        scenarios = db.query(ProjectScenario).filter(
            ProjectScenario.project_id == project_id
        ).all()
        
        if not scenarios:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Serialize scenarios properly (same as /projects endpoint)
        serialized = []
        for s in scenarios:
            item = {
                "project_id": s.project_id,
                "scenario_id": s.scenario_id,
                "project_name": s.project_name,
                "scenario_name": s.scenario_name,
                "project_zoom": s.project_zoom,
                "project_crs": s.project_crs,
                "created_at": s.created_at,
                "updated_at": s.updated_at,
            }
            # Serialize geometries safely
            try:
                if s.project_boundary is not None:
                    geom_shape = to_shape(s.project_boundary)
                    item["project_boundary"] = mapping(geom_shape)
            except Exception:
                item["project_boundary"] = None
            try:
                if s.project_center is not None:
                    center_shape = to_shape(s.project_center)
                    item["project_center"] = mapping(center_shape)
            except Exception:
                item["project_center"] = None
            serialized.append(item)
        return serialized
    except HTTPException:
        raise
    except Exception as e:
        # Possible errors: Database connection issues
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/projects/{project_id}/scenarios")
async def create_scenario(
    project_id: str,
    request_body: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Create a new scenario for a project based on the baseline scenario.
    Baseline scenario has scenario_id == project_id. The new scenario gets a new UUID.
    Copies project metadata (boundary, center, etc.) from baseline.
    """
    scenario_name = request_body.get("scenario_name")
    if not scenario_name or not str(scenario_name).strip():
        raise HTTPException(status_code=400, detail="scenario_name is required and cannot be empty")

    try:
        # Get baseline scenario: prefer scenario_id == project_id, else scenario_name='baseline'
        baseline = db.query(ProjectScenario).filter(
            and_(
                ProjectScenario.project_id == project_id,
                ProjectScenario.scenario_id == project_id
            )
        ).first()

        if not baseline:
            baseline = db.query(ProjectScenario).filter(
                and_(
                    ProjectScenario.project_id == project_id,
                    ProjectScenario.scenario_name.ilike("baseline")
                )
            ).first()

        if not baseline:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Project not found or baseline scenario missing for project_id '{project_id}'. "
                    "Verify the project exists via GET /api/v1/vector/projects and "
                    "GET /api/v1/vector/pscenarios/{project_id}"
                )
            )

        # Generate new scenario UUID
        scenario_id = str(uuid.uuid4())

        # Create new ProjectScenario copying metadata from baseline
        new_scenario = ProjectScenario(
            project_id=project_id,
            scenario_id=scenario_id,
            project_name=baseline.project_name,
            scenario_name=str(scenario_name).strip(),
            project_boundary=baseline.project_boundary,
            project_center=baseline.project_center,
            project_zoom=baseline.project_zoom,
            project_crs=baseline.project_crs,
            census_boundary=baseline.census_boundary,
        )
        db.add(new_scenario)
        db.commit()
        db.refresh(new_scenario)

        # Serialize response
        item = {
            "project_id": new_scenario.project_id,
            "scenario_id": new_scenario.scenario_id,
            "project_name": new_scenario.project_name,
            "scenario_name": new_scenario.scenario_name,
            "project_zoom": new_scenario.project_zoom,
            "project_crs": new_scenario.project_crs,
            "created_at": new_scenario.created_at,
            "updated_at": new_scenario.updated_at,
        }
        try:
            if new_scenario.project_boundary is not None:
                item["project_boundary"] = mapping(to_shape(new_scenario.project_boundary))
        except Exception:
            item["project_boundary"] = None
        try:
            if new_scenario.project_center is not None:
                item["project_center"] = mapping(to_shape(new_scenario.project_center))
        except Exception:
            item["project_center"] = None

        return item
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create scenario: {str(e)}")


@router.get("/project_scenario_details/{project_id}/{scenario_id}")
async def get_project_scenario_details(
    project_id: str,
    scenario_id: str,
    db: Session = Depends(get_db)
):
    """Get details for a specific project scenario"""
    try:
        scenario = db.query(ProjectScenario).filter(
            and_(
                ProjectScenario.project_id == project_id,
                ProjectScenario.scenario_id == scenario_id
            )
        ).first()
        
        if not scenario:
            raise HTTPException(status_code=404, detail="Project scenario not found")
        
        # Serialize scenario properly
        item = {
            "project_id": scenario.project_id,
            "scenario_id": scenario.scenario_id,
            "project_name": scenario.project_name,
            "scenario_name": scenario.scenario_name,
            "project_zoom": scenario.project_zoom,
            "project_crs": scenario.project_crs,
            "created_at": scenario.created_at,
            "updated_at": scenario.updated_at,
        }
        # Serialize geometries safely
        try:
            if scenario.project_boundary is not None:
                geom_shape = to_shape(scenario.project_boundary)
                item["project_boundary"] = mapping(geom_shape)
        except Exception:
            item["project_boundary"] = None
        try:
            if scenario.project_center is not None:
                center_shape = to_shape(scenario.project_center)
                item["project_center"] = mapping(center_shape)
        except Exception:
            item["project_center"] = None
        return item
    except HTTPException:
        raise
    except Exception as e:
        # Possible errors: Database connection issues
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/bgeo/{building_id}")
async def get_building_geometry(
    building_id: str,
    lod: Optional[int] = Query(0),
    db: Session = Depends(get_db)
):
    """Get building geometry by building ID"""
    try:
        building = db.query(Building).filter(
            and_(
                Building.building_id == building_id,
                Building.lod == lod
            )
        ).first()
        
        if not building:
            raise HTTPException(status_code=404, detail="Building not found")
        
        # Convert geometry to GeoJSON
        geom_shape = to_shape(building.building_geometry)
        geometry = mapping(geom_shape)
        
        return {
            "building_id": building.building_id,
            "lod": building.lod,
            "geometry": geometry,
            "geometry_source": building.building_geometry_source,
            "census_id": building.census_id
        }
    except HTTPException:
        raise
    except Exception as e:
        # Possible errors: Geometry conversion issues, database issues
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


def _props_to_dict(props: BuildingProperties) -> Dict[str, Any]:
    """Serialize BuildingProperties to dict for merge/response."""
    return {
        "height": props.height,
        "area": props.area,
        "volume": props.volume,
        "type": props.type,
        "n_people": props.n_people,
        "n_family": props.n_family,
        "number_of_floors": props.number_of_floors,
        "const_year": props.const_year,
        "const_period_census": props.const_period_census,
        "const_tabula": props.const_tabula,
        "envelope_efficiency": props.envelope_efficiency,
        "fmu_file": props.fmu_file,
    }


def _merge_baseline_delta(baseline: Dict[str, Any], delta: Optional[BuildingProperties]) -> Dict[str, Any]:
    """Overwrite baseline values with non-NULL delta values."""
    out = dict(baseline)
    if delta:
        d = _props_to_dict(delta)
        for k, v in d.items():
            if v is not None:
                out[k] = v
    return out


def _resolve_baseline_scenario_id(db: Session, project_id: str) -> Optional[str]:
    """
    Resolve the baseline scenario_id for a project.
    Prefer scenario_id == project_id, else scenario_name='baseline'.
    """
    row = db.query(ProjectScenario).filter(
        and_(
            ProjectScenario.project_id == project_id,
            ProjectScenario.scenario_id == project_id
        )
    ).first()
    if row:
        return row.scenario_id
    row = db.query(ProjectScenario).filter(
        and_(
            ProjectScenario.project_id == project_id,
            ProjectScenario.scenario_name.ilike("baseline")
        )
    ).first()
    return row.scenario_id if row else None


@router.get("/get_buildings_geojson/{project_id}/{scenario_id}")
async def get_buildings_geojson(
    project_id: str,
    scenario_id: str,
    lod: Optional[int] = Query(0),
    db: Session = Depends(get_db)
):
    """
    Get all buildings for a project scenario as GeoJSON.
    Baseline (scenario_id == project_id or scenario_name='baseline'): single query.
    Non-baseline: two queries (baseline + delta), merge in memory, then return.
    """
    try:
        baseline_scenario_id = _resolve_baseline_scenario_id(db, project_id)
        is_baseline = scenario_id == project_id or scenario_id == baseline_scenario_id
        query_scenario_id = baseline_scenario_id if baseline_scenario_id else scenario_id

        if is_baseline:
            # Single query: baseline has full rows for all buildings
            query = db.query(BuildingProperties, Building).join(
                Building,
                Building.building_id == BuildingProperties.building_id
            ).filter(
                and_(
                    BuildingProperties.project_id == project_id,
                    BuildingProperties.scenario_id == query_scenario_id,
                    BuildingProperties.lod == lod
                )
            )
            features = []
            for props, building in query:
                try:
                    geom_shape = to_shape(building.building_geometry)
                    geometry = mapping(geom_shape)
                except Exception as geo_err:
                    print(f"Warning: Failed to convert geometry for building {building.building_id}: {geo_err}")
                    continue
                feature = {
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": {
                        "building_id": str(building.building_id),
                        "lod": building.lod,
                        **_props_to_dict(props),
                    }
                }
                features.append(feature)
        else:
            # Two queries: baseline + delta, merge in memory
            if not baseline_scenario_id:
                raise HTTPException(
                    status_code=404,
                    detail=f"No baseline scenario found for project_id '{project_id}'"
                )
            baseline_query = db.query(BuildingProperties, Building).join(
                Building,
                Building.building_id == BuildingProperties.building_id
            ).filter(
                and_(
                    BuildingProperties.project_id == project_id,
                    BuildingProperties.scenario_id == baseline_scenario_id,
                    BuildingProperties.lod == lod
                )
            )
            delta_rows = db.query(BuildingProperties).filter(
                and_(
                    BuildingProperties.project_id == project_id,
                    BuildingProperties.scenario_id == scenario_id,
                    BuildingProperties.lod == lod
                )
            ).all()
            delta_by_building = {(r.building_id, r.lod): r for r in delta_rows}

            features = []
            for props, building in baseline_query:
                try:
                    geom_shape = to_shape(building.building_geometry)
                    geometry = mapping(geom_shape)
                except Exception as geo_err:
                    print(f"Warning: Failed to convert geometry for building {building.building_id}: {geo_err}")
                    continue
                delta = delta_by_building.get((building.building_id, lod))
                merged = _merge_baseline_delta(_props_to_dict(props), delta)
                feature = {
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": {
                        "building_id": str(building.building_id),
                        "lod": building.lod,
                        **merged,
                    }
                }
                features.append(feature)
        return {
            "type": "FeatureCollection",
            "features": features
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/buildingproperties/{project_id}/{scenario_id}")
async def query_building_properties(
    project_id: str,
    scenario_id: str,
    building_id: Optional[str] = Query(None),
    lod: Optional[int] = Query(0),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Query building properties for a project scenario.
    Baseline (scenario_id == project_id or scenario_name='baseline'): single query.
    Non-baseline: two queries (baseline + delta), merge in memory.
    """
    try:
        baseline_scenario_id = _resolve_baseline_scenario_id(db, project_id)
        is_baseline = scenario_id == project_id or scenario_id == baseline_scenario_id
        query_scenario_id = baseline_scenario_id if baseline_scenario_id else scenario_id

        if is_baseline:
            query = db.query(BuildingProperties).filter(
                and_(
                    BuildingProperties.project_id == project_id,
                    BuildingProperties.scenario_id == query_scenario_id,
                    BuildingProperties.lod == lod
                )
            )
            if building_id:
                query = query.filter(BuildingProperties.building_id == building_id)
            properties = query.offset(offset).limit(limit).all()
            serialized = [
                {
                    "building_id": str(p.building_id),
                    "scenario_id": str(p.scenario_id),
                    "project_id": p.project_id,
                    "lod": p.lod,
                    "height": p.height,
                    "area": p.area,
                    "volume": p.volume,
                    "number_of_floors": p.number_of_floors,
                    "type": p.type,
                    "const_period_census": p.const_period_census,
                    "const_year": p.const_year,
                    "const_tabula": p.const_tabula,
                    "n_people": p.n_people,
                    "n_family": p.n_family,
                    "created_at": p.created_at,
                    "updated_at": p.updated_at,
                }
                for p in properties
            ]
            return serialized
        else:
            # Two queries: baseline + delta, merge
            if not baseline_scenario_id:
                raise HTTPException(
                    status_code=404,
                    detail=f"No baseline scenario found for project_id '{project_id}'"
                )
            baseline_query = db.query(BuildingProperties).filter(
                and_(
                    BuildingProperties.project_id == project_id,
                    BuildingProperties.scenario_id == baseline_scenario_id,
                    BuildingProperties.lod == lod
                )
            )
            if building_id:
                baseline_query = baseline_query.filter(BuildingProperties.building_id == building_id)
            baseline_rows = baseline_query.offset(offset).limit(limit).all()

            delta_rows = db.query(BuildingProperties).filter(
                and_(
                    BuildingProperties.project_id == project_id,
                    BuildingProperties.scenario_id == scenario_id,
                    BuildingProperties.lod == lod
                )
            ).all()
            delta_by_building = {(r.building_id, r.lod): r for r in delta_rows}

            serialized = []
            for p in baseline_rows:
                delta = delta_by_building.get((p.building_id, p.lod))
                merged = _merge_baseline_delta(
                    {
                        "height": p.height, "area": p.area, "volume": p.volume,
                        "number_of_floors": p.number_of_floors, "type": p.type,
                        "const_period_census": p.const_period_census,
                        "const_year": p.const_year, "const_tabula": p.const_tabula,
                        "n_people": p.n_people, "n_family": p.n_family,
                        "envelope_efficiency": p.envelope_efficiency,
                        "fmu_file": p.fmu_file,
                    },
                    delta
                )
                item = {
                    "building_id": str(p.building_id),
                    "scenario_id": scenario_id,
                    "project_id": p.project_id,
                    "lod": p.lod,
                    **merged,
                    "created_at": p.created_at,
                    "updated_at": delta.updated_at if delta else p.updated_at,
                }
                serialized.append(item)
            return serialized
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# Editable BuildingProperties fields (delta storage - only these can be modified)
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
    db: Session = Depends(get_db)
):
    """
    Store or update modified building properties for a non-baseline scenario (delta storage).
    Only modified fields need to be sent; NULL in delta means inherit from baseline.
    Rejects if scenario_id == project_id (baseline cannot be modified via this endpoint).
    Accepts single modification or batch: {"modifications": [{...}, ...]}.
    """
    if scenario_id == project_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot modify baseline scenario via this endpoint. Use pipeline/calculators for baseline."
        )

    # Resolve scenario exists and is non-baseline
    scenario = db.query(ProjectScenario).filter(
        and_(
            ProjectScenario.project_id == project_id,
            ProjectScenario.scenario_id == scenario_id
        )
    ).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Parse modifications: batch or single
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

            # Filter to editable fields only
            updates = {k: v for k, v in mod.items() if k in _BP_EDITABLE_FIELDS and k != "building_id"}
            if not updates:
                raise HTTPException(status_code=400, detail=f"No editable fields provided for building_id '{building_id}'")

            existing = db.query(BuildingProperties).filter(
                and_(
                    BuildingProperties.project_id == project_id,
                    BuildingProperties.scenario_id == scenario_id,
                    BuildingProperties.building_id == building_id,
                    BuildingProperties.lod == lod,
                )
            ).first()

            if existing:
                for k, v in updates.items():
                    setattr(existing, k, v)
            else:
                new_row = BuildingProperties(
                    project_id=project_id,
                    scenario_id=scenario_id,
                    building_id=building_id,
                    lod=lod,
                    **updates
                )
                db.add(new_row)
            upserted += 1

        db.commit()
        return {"upserted": upserted, "scenario_id": scenario_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to upsert building properties: {str(e)}")


@router.get("/building_id_fetcher")
async def building_id_fetcher(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    db: Session = Depends(get_db)
):
    """Fetch building IDs at a specific point"""
    try:
        # Create point from coordinates
        from geoalchemy2 import func
        point = func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326)
        
        # Query buildings that contain the point
        buildings = db.query(Building).filter(
            func.ST_Contains(Building.building_geometry, point)
        ).all()
        
        return {
            "buildings": [
                {
                    "building_id": b.building_id,
                    "lod": b.lod,
                    "census_id": b.census_id
                }
                for b in buildings
            ]
        }
    except Exception as e:
        # Possible errors: Invalid coordinates, database issues
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/building_id_fetcher_buffer")
async def building_id_fetcher_buffer(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    buffer_m: float = Query(10, description="Buffer in meters"),
    db: Session = Depends(get_db)
):
    """Fetch building IDs within a buffer of a point"""
    try:
        from geoalchemy2 import func
        # Create point from coordinates
        point = func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326)
        
        # Convert buffer from meters to degrees (approximate)
        buffer_deg = buffer_m / 111320.0  # 1 degree ≈ 111.32 km at equator
        
        # Query buildings within buffer distance
        buildings = db.query(Building).filter(
            func.ST_DWithin(Building.building_geometry, point, buffer_deg)
        ).all()
        
        return {
            "buildings": [
                {
                    "building_id": b.building_id,
                    "lod": b.lod,
                    "census_id": b.census_id
                }
                for b in buildings
            ],
            "buffer_m": buffer_m
        }
    except Exception as e:
        # Possible errors: Invalid coordinates, database issues
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# # Grid-related endpoints
# @router.get("/{project_id}/{scenario_id}/gridline")
# async def get_grid_lines(
#     project_id: str,
#     scenario_id: str,
#     network_id: Optional[str] = Query(None),
#     limit: int = Query(100, ge=1, le=1000),
#     offset: int = Query(0, ge=0),
#     db: Session = Depends(get_db)
# ):
#     """Get grid lines for a project scenario"""
#     try:
#         query = db.query(GridLine).filter(
#             and_(
#                 GridLine.project_id == project_id,
#                 GridLine.scenario_id == scenario_id
#             )
#         )
        
#         if network_id:
#             query = query.filter(GridLine.network_id == network_id)
        
#         lines = query.offset(offset).limit(limit).all()
#         return lines
#     except Exception as e:
#         # Possible errors: Database connection issues
#         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# @router.get("/gridline/network/{network_id}")
# async def get_grid_lines_by_network(
#     network_id: str,
#     limit: int = Query(100, ge=1, le=1000),
#     offset: int = Query(0, ge=0),
#     db: Session = Depends(get_db)
# ):
#     """Get grid lines by network ID"""
#     try:
#         lines = db.query(GridLine).filter(
#             GridLine.network_id == network_id
#         ).offset(offset).limit(limit).all()
        
#         return lines
#     except Exception as e:
#         # Possible errors: Database connection issues
#         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ── Delete endpoints ───────────────────────────────────────────────────

@router.delete("/delete")
async def delete_project_data(
    project_id: str = Query(..., description="Project ID (required)"),
    scenario_id: Optional[str] = Query(None, description="Scenario ID (optional)"),
    building_id: Optional[str] = Query(None, description="Building ID (optional)"),
    db: Session = Depends(get_db)
):
    """
    Flexible delete endpoint. Behavior depends on which parameters are provided:
    
    1. project_id + scenario_id + building_id
       Delete one building from building_properties and building tables.
    
    2. project_id + scenario_id (no building_id)
       Delete the project scenario and ALL its buildings from
       building_properties, building, and project_scenario tables.
    
    3. project_id only (no scenario_id, no building_id)
       Delete ALL scenarios for that project and ALL their buildings
       from building_properties, building, and project_scenario tables.
    """
    try:
        deleted = {
            "building_properties_deleted": 0,
            "buildings_deleted": 0,
            "project_scenarios_deleted": 0,
        }

        # ── Case 1: Delete a specific building ──────────────────────
        if project_id and scenario_id and building_id:
            # Delete from building_properties
            bp_count = db.query(BuildingProperties).filter(
                and_(
                    BuildingProperties.project_id == project_id,
                    BuildingProperties.scenario_id == scenario_id,
                    BuildingProperties.building_id == building_id,
                )
            ).delete(synchronize_session=False)
            deleted["building_properties_deleted"] = bp_count

            # Check if this building_id is used by any other scenario
            other_refs = db.query(BuildingProperties).filter(
                BuildingProperties.building_id == building_id
            ).count()

            if other_refs == 0:
                # No other scenario references this building, safe to delete geometry
                b_count = db.query(Building).filter(
                    Building.building_id == building_id
                ).delete(synchronize_session=False)
                deleted["buildings_deleted"] = b_count

            db.commit()
            return {
                "action": "delete_building",
                "project_id": project_id,
                "scenario_id": scenario_id,
                "building_id": building_id,
                **deleted,
            }

        # ── Case 2: Delete a project scenario and all its buildings ─
        elif project_id and scenario_id:
            # Get all building_ids for this scenario
            bp_building_ids = [
                row.building_id for row in
                db.query(BuildingProperties.building_id).filter(
                    and_(
                        BuildingProperties.project_id == project_id,
                        BuildingProperties.scenario_id == scenario_id,
                    )
                ).all()
            ]

            # Delete building_properties
            bp_count = db.query(BuildingProperties).filter(
                and_(
                    BuildingProperties.project_id == project_id,
                    BuildingProperties.scenario_id == scenario_id,
                )
            ).delete(synchronize_session=False)
            deleted["building_properties_deleted"] = bp_count

            # Delete buildings that are no longer referenced by any scenario
            b_count = 0
            for bid in bp_building_ids:
                still_referenced = db.query(BuildingProperties).filter(
                    BuildingProperties.building_id == bid
                ).count()
                if still_referenced == 0:
                    b_count += db.query(Building).filter(
                        Building.building_id == bid
                    ).delete(synchronize_session=False)
            deleted["buildings_deleted"] = b_count

            # Delete the project_scenario record
            ps_count = db.query(ProjectScenario).filter(
                and_(
                    ProjectScenario.project_id == project_id,
                    ProjectScenario.scenario_id == scenario_id,
                )
            ).delete(synchronize_session=False)
            deleted["project_scenarios_deleted"] = ps_count

            db.commit()
            return {
                "action": "delete_scenario",
                "project_id": project_id,
                "scenario_id": scenario_id,
                **deleted,
            }

        # ── Case 3: Delete entire project (all scenarios + buildings) ─
        else:
            # Get all scenario_ids for this project
            scenario_ids = [
                row.scenario_id for row in
                db.query(ProjectScenario.scenario_id).filter(
                    ProjectScenario.project_id == project_id
                ).all()
            ]

            if not scenario_ids:
                raise HTTPException(
                    status_code=404,
                    detail=f"No project found with project_id '{project_id}'"
                )

            # Get all building_ids across all scenarios of this project
            bp_building_ids = [
                row.building_id for row in
                db.query(BuildingProperties.building_id).filter(
                    BuildingProperties.project_id == project_id
                ).distinct().all()
            ]

            # Delete all building_properties for this project
            bp_count = db.query(BuildingProperties).filter(
                BuildingProperties.project_id == project_id
            ).delete(synchronize_session=False)
            deleted["building_properties_deleted"] = bp_count

            # Delete buildings no longer referenced by any scenario
            b_count = 0
            for bid in bp_building_ids:
                still_referenced = db.query(BuildingProperties).filter(
                    BuildingProperties.building_id == bid
                ).count()
                if still_referenced == 0:
                    b_count += db.query(Building).filter(
                        Building.building_id == bid
                    ).delete(synchronize_session=False)
            deleted["buildings_deleted"] = b_count

            # Delete all project_scenario records for this project
            ps_count = db.query(ProjectScenario).filter(
                ProjectScenario.project_id == project_id
            ).delete(synchronize_session=False)
            deleted["project_scenarios_deleted"] = ps_count

            db.commit()
            return {
                "action": "delete_project",
                "project_id": project_id,
                "scenarios_affected": scenario_ids,
                **deleted,
            }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


# ── Schema discovery endpoints ─────────────────────────────────────────
# These let any client fetch the normalization config so they know
# which canonical field names the API uses and which aliases are accepted.

@router.get("/schema")
async def get_normalization_schema():
    """
    Return the full normalization schema for all entities.
    
    Clients (frontend, Postman, scripts) can call this endpoint to discover:
    - Available entities and their canonical field names
    - Accepted aliases for each field
    - Field types, required status, value ranges, and descriptions
    
    Use this to auto-generate client-side normalizers or validate payloads.
    """
    return get_client_schema()


@router.get("/schema/{entity_name}")
async def get_entity_normalization_schema(entity_name: str):
    """
    Return the normalization schema for a single entity.
    
    Entity names: project_scenario, building, building_properties
    """
    schema = get_entity_schema(entity_name)
    if schema is None:
        available = get_entity_names()
        raise HTTPException(
            status_code=404,
            detail=f"Entity '{entity_name}' not found. Available: {available}"
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