"""
Pydantic schemas for Raster data
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class BuildingHeightRequest(BaseModel):
    building_geometry: Dict[str, Any] = Field(..., description="Building geometry in GeoJSON format")
    building_id: Optional[str] = None
    use_cache: bool = True


class BuildingHeightResponse(BaseModel):
    building_id: Optional[str] = None
    dtm_avg_height: Optional[float] = None
    dsm_avg_height: Optional[float] = None
    building_height: Optional[float] = None
    status: str
    error: Optional[str] = None
    calculation_date: Optional[str] = None


class RasterClipRequest(BaseModel):
    polygon: Dict[str, Any] = Field(..., description="Polygon geometry in GeoJSON format")
    raster_type: str = Field("DTM", description="Raster type: DTM or DSM")


class RasterStatisticsResponse(BaseModel):
    raster_type: str
    min: Optional[float] = None
    max: Optional[float] = None
    mean: Optional[float] = None
    stddev: Optional[float] = None
    status: Optional[str] = None
    error: Optional[str] = None


class ElevationResponse(BaseModel):
    lat: float
    lon: float
    elevation: Optional[float] = None
    raster_type: str
    status: str