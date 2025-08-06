"""
Pydantic schemas for Census data
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class CensusSpatialQuery(BaseModel):
    polygon_array: List[List[float]] = Field(..., description="Polygon coordinates [[lon, lat], ...]")


class CensusResponse(BaseModel):
    SEZ2011: int
    COMUNE: Optional[str] = None
    PROVINCIA: Optional[str] = None
    REGIONE: Optional[str] = None
    P1: Optional[int] = None  # Total population
    PF1: Optional[int] = None  # Total families
    E3: Optional[int] = None  # Total buildings
    E4: Optional[int] = None  # Residential buildings


class CensusStatistics(BaseModel):
    total_population: int
    total_families: int
    total_buildings: int
    residential_buildings: int
    census_zones_count: int
    avg_population_per_zone: float


class BuildingAgeDistribution(BaseModel):
    before_1918: int
    year_1919_1945: int = Field(alias="1919_1945")
    year_1946_1960: int = Field(alias="1946_1960")
    year_1961_1970: int = Field(alias="1961_1970")
    year_1971_1980: int = Field(alias="1971_1980")
    year_1981_1990: int = Field(alias="1981_1990")
    year_1991_2000: int = Field(alias="1991_2000")
    year_2001_2005: int = Field(alias="2001_2005")
    after_2005: int
    total_buildings: int
    residential_buildings: int