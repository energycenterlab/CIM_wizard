"""
Vector Gateway Routes - All endpoints from vector_gateway_service
FastAPI implementation for CIM Wizard Integrated
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping
import json

from app.db.database import get_db
from app.models.vector import (
    ProjectScenario, Building, BuildingProperties, 
    GridBus, GridLine
)
# Removed Pydantic schemas for simplicity - using dict responses


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


@router.get("/get_buildings_geojson/{project_id}/{scenario_id}")
async def get_buildings_geojson(
    project_id: str,
    scenario_id: str,
    lod: Optional[int] = Query(0),
    db: Session = Depends(get_db)
):
    """Get all buildings for a project scenario as GeoJSON"""
    try:
        # Get building properties with buildings using the cim_wizard tables
        # Join on building_id only (lod filter applied separately)
        query = db.query(BuildingProperties, Building).join(
            Building,
            Building.building_id == BuildingProperties.building_id
        ).filter(
            and_(
                BuildingProperties.project_id == project_id,
                BuildingProperties.scenario_id == scenario_id,
                BuildingProperties.lod == lod
            )
        )
        
        features = []
        for props, building in query:
            # Convert geometry to GeoJSON
            try:
                geom_shape = to_shape(building.building_geometry)
                geometry = mapping(geom_shape)
            except Exception as geo_err:
                print(f"Warning: Failed to convert geometry for building {building.building_id}: {geo_err}")
                continue
            
            # Create feature
            feature = {
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    "building_id": str(building.building_id),
                    "lod": building.lod,
                    "height": props.height,
                    "area": props.area,
                    "volume": props.volume,
                    "type": props.type,
                    "n_people": props.n_people,
                    "n_family": props.n_family,
                    "number_of_floors": props.number_of_floors,
                    "const_year": props.const_year,
                    "const_period_census": props.const_period_census
                }
            }
            features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features
        }
    except Exception as e:
        # Possible errors: Geometry conversion issues, database issues
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
    """Query building properties for a project scenario"""
    try:
        query = db.query(BuildingProperties).filter(
            and_(
                BuildingProperties.project_id == project_id,
                BuildingProperties.scenario_id == scenario_id,
                BuildingProperties.lod == lod
            )
        )
        
        if building_id:
            query = query.filter(BuildingProperties.building_id == building_id)
        
        properties = query.offset(offset).limit(limit).all()
        
        # Serialize properties to dict
        serialized = []
        for p in properties:
            item = {
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
            serialized.append(item)
        return serialized
    except Exception as e:
        # Possible errors: Database connection issues
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


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


# Grid-related endpoints
@router.get("/{project_id}/{scenario_id}/gridline")
async def get_grid_lines(
    project_id: str,
    scenario_id: str,
    network_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get grid lines for a project scenario"""
    try:
        query = db.query(GridLine).filter(
            and_(
                GridLine.project_id == project_id,
                GridLine.scenario_id == scenario_id
            )
        )
        
        if network_id:
            query = query.filter(GridLine.network_id == network_id)
        
        lines = query.offset(offset).limit(limit).all()
        return lines
    except Exception as e:
        # Possible errors: Database connection issues
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/gridline/network/{network_id}")
async def get_grid_lines_by_network(
    network_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get grid lines by network ID"""
    try:
        lines = db.query(GridLine).filter(
            GridLine.network_id == network_id
        ).offset(offset).limit(limit).all()
        
        return lines
    except Exception as e:
        # Possible errors: Database connection issues
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/health")
async def vector_health():
    """Health check for vector gateway routes"""
    return {"status": "healthy", "service": "vector_gateway"}