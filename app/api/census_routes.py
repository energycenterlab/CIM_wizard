"""
Census Routes - Direct database access to census data
FastAPI implementation for CIM Wizard Integrated
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json

from app.db.database import get_db
from app.services.census_service import CensusService
# Removed Pydantic schemas for simplicity - using dict responses


router = APIRouter()


@router.post("/census_spatial")
async def census_spatial(
    polygon_array: List[List[float]] = Body(..., description="Polygon coordinates as [[lon, lat], ...]"),
    db: Session = Depends(get_db)
):
    """Get census zones that intersect with a polygon"""
    try:
        # Validate polygon
        if len(polygon_array) < 4:
            raise HTTPException(status_code=400, detail="Polygon requires at least 4 points")
        
        # Initialize census service
        census_service = CensusService(db_session=db)
        
        # Get census data
        result = census_service.get_census_by_polygon(polygon_array)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        # Possible errors: Invalid polygon, database issues
        raise HTTPException(status_code=500, detail=f"Census query error: {str(e)}")


@router.get("/census/{census_id}")
async def get_census_by_id(
    census_id: int,
    db: Session = Depends(get_db)
):
    """Get census zone by SEZ2011 ID"""
    try:
        census_service = CensusService(db_session=db)
        census_zone = census_service.get_census_by_id(census_id)
        
        if not census_zone:
            raise HTTPException(status_code=404, detail="Census zone not found")
        
        return {
            "SEZ2011": census_zone.SEZ2011,
            "COMUNE": census_zone.COMUNE,
            "PROVINCIA": census_zone.PROVINCIA,
            "REGIONE": census_zone.REGIONE,
            "P1": census_zone.P1,  # Total population
            "PF1": census_zone.PF1,  # Total families
            "E3": census_zone.E3,  # Total buildings
            "E4": census_zone.E4,  # Residential buildings
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Possible errors: Database connection issues
        raise HTTPException(status_code=500, detail=f"Census query error: {str(e)}")


@router.post("/census_population")
async def get_census_population(
    census_ids: List[int] = Body(..., description="List of SEZ2011 census IDs"),
    db: Session = Depends(get_db)
):
    """Get population for multiple census zones"""
    try:
        census_service = CensusService(db_session=db)
        population_data = census_service.get_census_population(census_ids)
        
        return {
            "census_population": population_data,
            "total_population": sum(population_data.values())
        }
        
    except Exception as e:
        # Possible errors: Database connection issues
        raise HTTPException(status_code=500, detail=f"Census query error: {str(e)}")


@router.get("/building_age_distribution/{census_id}")
async def get_building_age_distribution(
    census_id: int,
    db: Session = Depends(get_db)
):
    """Get building age distribution for a census zone"""
    try:
        census_service = CensusService(db_session=db)
        distribution = census_service.get_building_age_distribution(census_id)
        
        if not distribution:
            raise HTTPException(status_code=404, detail="Census zone not found")
        
        return distribution
        
    except HTTPException:
        raise
    except Exception as e:
        # Possible errors: Database connection issues
        raise HTTPException(status_code=500, detail=f"Census query error: {str(e)}")


@router.post("/census_statistics")
async def get_census_statistics(
    polygon_array: List[List[float]] = Body(..., description="Polygon coordinates as [[lon, lat], ...]"),
    db: Session = Depends(get_db)
):
    """Get aggregated statistics for census zones within a polygon"""
    try:
        # Validate polygon
        if len(polygon_array) < 4:
            raise HTTPException(status_code=400, detail="Polygon requires at least 4 points")
        
        census_service = CensusService(db_session=db)
        statistics = census_service.get_census_statistics(polygon_array)
        
        return statistics
        
    except HTTPException:
        raise
    except Exception as e:
        # Possible errors: Invalid polygon, database issues
        raise HTTPException(status_code=500, detail=f"Census statistics error: {str(e)}")


@router.post("/census_by_building")
async def get_census_by_building_location(
    building_geometry: Dict[str, Any] = Body(..., description="Building geometry in GeoJSON format"),
    db: Session = Depends(get_db)
):
    """Get census zone that contains a building"""
    try:
        from shapely.geometry import shape
        
        # Convert GeoJSON to WKT
        geom_shape = shape(building_geometry)
        building_wkt = geom_shape.wkt
        
        census_service = CensusService(db_session=db)
        census_zone = census_service.get_census_by_building_location(building_wkt)
        
        if not census_zone:
            return {"message": "No census zone found for this building"}
        
        return {
            "SEZ2011": census_zone.SEZ2011,
            "COMUNE": census_zone.COMUNE,
            "P1": census_zone.P1,
            "PF1": census_zone.PF1,
            "E3": census_zone.E3,
            "E4": census_zone.E4
        }
        
    except Exception as e:
        # Possible errors: Invalid geometry, database issues
        raise HTTPException(status_code=500, detail=f"Census query error: {str(e)}")


@router.get("/query_census")
async def query_census_properties(
    comune: Optional[str] = Query(None, description="Filter by comune"),
    provincia: Optional[str] = Query(None, description="Filter by provincia"),
    min_population: Optional[int] = Query(None, description="Minimum population"),
    max_population: Optional[int] = Query(None, description="Maximum population"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Query census data with filters"""
    try:
        from app.models.census import CensusGeo
        
        query = db.query(CensusGeo)
        
        # Apply filters
        if comune:
            query = query.filter(CensusGeo.COMUNE.ilike(f"%{comune}%"))
        if provincia:
            query = query.filter(CensusGeo.PROVINCIA.ilike(f"%{provincia}%"))
        if min_population is not None:
            query = query.filter(CensusGeo.P1 >= min_population)
        if max_population is not None:
            query = query.filter(CensusGeo.P1 <= max_population)
        
        # Get total count
        total_count = query.count()
        
        # Get paginated results
        results = query.offset(offset).limit(limit).all()
        
        return {
            "total_count": total_count,
            "results": [
                {
                    "SEZ2011": r.SEZ2011,
                    "COMUNE": r.COMUNE,
                    "PROVINCIA": r.PROVINCIA,
                    "REGIONE": r.REGIONE,
                    "P1": r.P1,
                    "PF1": r.PF1,
                    "E3": r.E3,
                    "E4": r.E4
                }
                for r in results
            ]
        }
        
    except Exception as e:
        # Possible errors: Database connection issues
        raise HTTPException(status_code=500, detail=f"Census query error: {str(e)}")


@router.get("/health")
async def census_health():
    """Health check for census service"""
    return {"status": "healthy", "service": "census_service"}