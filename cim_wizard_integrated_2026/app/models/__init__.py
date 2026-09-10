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

from app.models.jobs import Job

from app.models.citydb import (
    CityModel,
    CityObject,
    CityObjectMember,
    CityBuilding,
    ThematicSurface,
    SurfaceGeometry,
    CityObjectGenericAttrib,
    ObjectClass,
    Ng2Building,
    Ng2BuildingPartition,
    Ng2ThematicSurface,
    Ng2ThemSurfToThermalZone,
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

    # Jobs (Celery)
    'Job',

    # 3DCityDB models (citydb schema, managed by 3DCityDB init scripts)
    'CityModel',
    'CityObject',
    'CityObjectMember',
    'CityBuilding',
    'ThematicSurface',
    'SurfaceGeometry',
    'CityObjectGenericAttrib',
    'ObjectClass',

    # Energy ADE 2.0 (citydb schema, ng2_* tables)
    'Ng2Building',
    'Ng2BuildingPartition',
    'Ng2ThematicSurface',
    'Ng2ThemSurfToThermalZone',
]