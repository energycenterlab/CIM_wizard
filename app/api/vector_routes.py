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
from app.schemas.vector_schemas import (
    ProjectScenarioResponse, BuildingGeometryResponse,
    BuildingsGeoJSONResponse, BuildingPropertiesResponse,
    GridBusResponse, GridLineResponse
)


router = APIRouter()


@router.get("/projects", response_model=List[ProjectScenarioResponse])
async def get_all_projects(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all projects with pagination"""
    try:
        projects = db.query(ProjectScenario).offset(offset).limit(limit).all()
        return projects
    except Exception as e:
        # Possible errors: Database connection issues
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/dashboard")
async def project_dashboard(db: Session = Depends(get_db)):
    """Get project dashboard with summary statistics"""
    try:
        total_projects = db.query(ProjectScenario).count()
        projects = db.query(ProjectScenario).limit(10).all()
        
        return {
            "total_projects": total_projects,
            "projects": projects
        }
    except Exception as e:
        # Possible errors: Database connection issues
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/pscenarios/{project_id}", response_model=List[ProjectScenarioResponse])
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
        
        return scenarios
    except HTTPException:
        raise
    except Exception as e:
        # Possible errors: Database connection issues
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/project_scenario_details/{project_id}/{scenario_id}", 
           response_model=ProjectScenarioResponse)
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
        
        return scenario
    except HTTPException:
        raise
    except Exception as e:
        # Possible errors: Database connection issues
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/bgeo/{building_id}", response_model=BuildingGeometryResponse)
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
        # Get building properties with buildings
        query = db.query(BuildingProperties, Building).join(
            Building,
            and_(
                Building.building_id == BuildingProperties.building_id,
                Building.lod == BuildingProperties.lod
            )
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
            geom_shape = to_shape(building.building_geometry)
            geometry = mapping(geom_shape)
            
            # Create feature
            feature = {
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    "building_id": building.building_id,
                    "lod": building.lod,
                    "height": props.height,
                    "area": props.area,
                    "volume": props.volume,
                    "type": props.type,
                    "n_people": props.n_people,
                    "n_family": props.n_family
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


@router.get("/buildingproperties/{project_id}/{scenario_id}", 
           response_model=List[BuildingPropertiesResponse])
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
        return properties
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
@router.get("/{project_id}/{scenario_id}/gridline", 
           response_model=List[GridLineResponse])
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


@router.get("/gridline/network/{network_id}", 
           response_model=List[GridLineResponse])
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