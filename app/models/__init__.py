"""
Database models for CIM Wizard Integrated
"""

# Import all models to make them available
from app.models.vector import (
    ProjectScenario,
    Building,
    BuildingProperties,
    GridBus,
    GridLine
)

from app.models.census import CensusGeo

from app.models.raster import (
    RasterModel,
    DTMRaster,
    DSMRaster,
    BuildingHeightCache
)

# Make all models available at package level
__all__ = [
    # Vector models
    'ProjectScenario',
    'Building',
    'BuildingProperties',
    'GridBus',
    'GridLine',
    
    # Census models
    'CensusGeo',
    
    # Raster models
    'RasterModel',
    'DTMRaster',
    'DSMRaster',
    'BuildingHeightCache'
]