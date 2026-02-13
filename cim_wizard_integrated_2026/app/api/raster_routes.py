"""
Raster Routes - Direct database access to raster data
FastAPI implementation for CIM Wizard Integrated
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json

from app.db.database import get_db
from app.services.raster_service import RasterService
# Removed Pydantic schemas for simplicity - using dict responses


router = APIRouter()


@router.post("/height")
async def calculate_building_height(
    building_geometry: Dict[str, Any] = Body(..., description="Building geometry in GeoJSON format"),
    building_id: Optional[str] = Body(None, description="Building ID for caching"),
    use_cache: bool = Body(True, description="Use cached values if available"),
    db: Session = Depends(get_db)
):
    """Calculate building height from DTM and DSM rasters"""
    try:
        raster_service = RasterService(db_session=db)
        
        result = raster_service.calculate_building_height(
            building_geometry=building_geometry,
            building_id=building_id,
            use_cache=use_cache
        )
        
        return result
        
    except Exception as e:
        # Possible errors: Invalid geometry, raster data not available
        raise HTTPException(status_code=500, detail=f"Height calculation error: {str(e)}")


@router.post("/height_batch")
async def calculate_building_heights_batch(
    features: List[Dict[str, Any]] = Body(..., description="GeoJSON features with building geometries"),
    db: Session = Depends(get_db)
):
    """Calculate heights for multiple buildings"""
    try:
        raster_service = RasterService(db_session=db)
        
        results = raster_service.calculate_building_heights_batch(features)
        
        return {
            "results": results,
            "total": len(results),
            "successful": len([r for r in results if r.get("status") == "calculated"])
        }
        
    except Exception as e:
        # Possible errors: Invalid features, database issues
        raise HTTPException(status_code=500, detail=f"Batch height calculation error: {str(e)}")


@router.get("/cached_height/{building_id}")
async def get_cached_height(
    building_id: str,
    project_id: Optional[str] = Query(None),
    scenario_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get cached building height"""
    try:
        raster_service = RasterService(db_session=db)
        
        cached = raster_service.get_cached_height(
            building_id=building_id,
            project_id=project_id,
            scenario_id=scenario_id
        )
        
        if not cached:
            raise HTTPException(status_code=404, detail="No cached height found")
        
        return cached
        
    except HTTPException:
        raise
    except Exception as e:
        # Possible errors: Database connection issues
        raise HTTPException(status_code=500, detail=f"Cache query error: {str(e)}")


@router.post("/clip_dtm")
async def clip_dtm_raster(
    polygon: Dict[str, Any] = Body(..., description="Polygon geometry in GeoJSON format"),
    db: Session = Depends(get_db)
):
    """Clip DTM raster to a polygon"""
    try:
        raster_service = RasterService(db_session=db)
        
        clipped_raster = raster_service.clip_raster(
            polygon_geometry=polygon,
            raster_type="DTM"
        )
        
        if not clipped_raster:
            raise HTTPException(status_code=404, detail="No raster data found for the given polygon")
        
        return {"raster": clipped_raster}
        
    except HTTPException:
        raise
    except Exception as e:
        # Possible errors: Invalid polygon, raster data not available
        raise HTTPException(status_code=500, detail=f"Raster clip error: {str(e)}")


@router.post("/clip_dsm")
async def clip_dsm_raster(
    polygon: Dict[str, Any] = Body(..., description="Polygon geometry in GeoJSON format"),
    db: Session = Depends(get_db)
):
    """Clip DSM raster to a polygon"""
    try:
        raster_service = RasterService(db_session=db)
        
        clipped_raster = raster_service.clip_raster(
            polygon_geometry=polygon,
            raster_type="DSM"
        )
        
        if not clipped_raster:
            raise HTTPException(status_code=404, detail="No raster data found for the given polygon")
        
        return {"raster": clipped_raster}
        
    except HTTPException:
        raise
    except Exception as e:
        # Possible errors: Invalid polygon, raster data not available
        raise HTTPException(status_code=500, detail=f"Raster clip error: {str(e)}")


@router.get("/elevation")
async def get_elevation_at_point(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    raster_type: str = Query("DTM", description="Raster type: DTM or DSM"),
    db: Session = Depends(get_db)
):
    """Get elevation value at a specific point"""
    try:
        raster_service = RasterService(db_session=db)
        
        elevation = raster_service.get_elevation_at_point(
            lon=lon,
            lat=lat,
            raster_type=raster_type
        )
        
        if elevation is None:
            return {
                "lat": lat,
                "lon": lon,
                "elevation": None,
                "raster_type": raster_type,
                "status": "no_data"
            }
        
        return {
            "lat": lat,
            "lon": lon,
            "elevation": elevation,
            "raster_type": raster_type,
            "status": "success"
        }
        
    except Exception as e:
        # Possible errors: Point outside raster bounds
        raise HTTPException(status_code=500, detail=f"Elevation query error: {str(e)}")


@router.post("/statistics")
async def get_raster_statistics(
    polygon: Dict[str, Any] = Body(..., description="Polygon geometry in GeoJSON format"),
    raster_type: str = Body("DTM", description="Raster type: DTM or DSM"),
    db: Session = Depends(get_db)
):
    """Get raster statistics within a polygon"""
    try:
        raster_service = RasterService(db_session=db)
        
        statistics = raster_service.get_raster_statistics(
            polygon_geometry=polygon,
            raster_type=raster_type
        )
        
        return statistics
        
    except Exception as e:
        # Possible errors: Invalid polygon, database issues
        raise HTTPException(status_code=500, detail=f"Statistics calculation error: {str(e)}")


@router.post("/height_fast")
async def calculate_building_heights_fast(
    features: List[Dict[str, Any]] = Body(..., description="GeoJSON features with building geometries"),
    use_cache: bool = Body(True, description="Use cached values where available"),
    db: Session = Depends(get_db)
):
    """Fast batch height calculation with caching"""
    try:
        raster_service = RasterService(db_session=db)
        
        results = []
        cached_count = 0
        calculated_count = 0
        
        for feature in features:
            building_id = feature.get("properties", {}).get("building_id")
            geometry = feature.get("geometry")
            
            if not geometry:
                results.append({
                    "building_id": building_id,
                    "status": "error",
                    "error": "Missing geometry"
                })
                continue
            
            # Try cache first if building_id available
            if use_cache and building_id:
                cached = raster_service.get_cached_height(building_id)
                if cached:
                    results.append(cached)
                    cached_count += 1
                    continue
            
            # Calculate if not cached
            height_data = raster_service.calculate_building_height(
                building_geometry=geometry,
                building_id=building_id,
                use_cache=False  # Already checked cache
            )
            results.append(height_data)
            if height_data.get("status") == "calculated":
                calculated_count += 1
        
        return {
            "results": results,
            "total": len(results),
            "cached": cached_count,
            "calculated": calculated_count,
            "errors": len(results) - cached_count - calculated_count
        }
        
    except Exception as e:
        # Possible errors: Database issues
        raise HTTPException(status_code=500, detail=f"Fast height calculation error: {str(e)}")


@router.get("/health")
async def raster_health():
    """Health check for raster service"""
    return {"status": "healthy", "service": "raster_service"}