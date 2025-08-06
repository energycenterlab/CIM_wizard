"""
Pydantic schemas for Vector data
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime


class ProjectScenarioBase(BaseModel):
    project_id: str
    scenario_id: str
    project_name: str
    scenario_name: str
    project_zoom: Optional[int] = 15
    project_crs: Optional[int] = 4326


class ProjectScenarioResponse(ProjectScenarioBase):
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class BuildingGeometryResponse(BaseModel):
    building_id: str
    lod: int
    geometry: Dict[str, Any]
    geometry_source: str
    census_id: Optional[int] = None


class BuildingPropertiesResponse(BaseModel):
    id: int
    building_id: str
    project_id: str
    scenario_id: str
    lod: int
    height: Optional[float] = None
    area: Optional[float] = None
    volume: Optional[float] = None
    number_of_floors: Optional[float] = None
    type: Optional[str] = None
    n_people: Optional[int] = None
    n_family: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class BuildingsGeoJSONResponse(BaseModel):
    type: str = "FeatureCollection"
    features: List[Dict[str, Any]]


class GridBusResponse(BaseModel):
    id: int
    network_id: str
    bus_id: int
    name: Optional[str] = None
    voltage_kv: Optional[float] = None
    in_service: bool = True
    
    model_config = ConfigDict(from_attributes=True)


class GridLineResponse(BaseModel):
    id: int
    network_id: str
    line_id: int
    name: Optional[str] = None
    from_bus: int
    to_bus: int
    length_km: Optional[float] = None
    max_loading_percent: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)