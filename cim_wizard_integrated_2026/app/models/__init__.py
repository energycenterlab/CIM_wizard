"""
Database models for CIM Wizard Integrated
"""

# Import all models to make them available
from app.models.vector import (
    ProjectScenario,
    Building,
    BuildingProperties,
    GridBus,
    GridLine,
    PV
)

from app.models.census import CensusGeo

from app.models.raster import (
    RasterModel,
    DTMRaster,
    DSMRaster,
    BuildingHeightCache
)

from app.models.outputs import (
    SimulationRun,
    BuildingFrassinetto3,
    Battery,
    HeatingFrassinettoHp2
)

# Make all models available at package level
__all__ = [
    # Vector models
    'ProjectScenario',
    'Building',
    'BuildingProperties',
    'GridBus',
    'GridLine',
    'PV',
    
    # Census models
    'CensusGeo',
    
    # Raster models
    'RasterModel',
    'DTMRaster',
    'DSMRaster',
    'BuildingHeightCache',

    # Output models (TimescaleDB hypertables)
    'SimulationRun',
    'BuildingFrassinetto3',
    'Battery',
    'HeatingFrassinettoHp2',
]