# CIM Wizard Integrated Service - Comprehensive Documentation

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Database Schema Design](#database-schema-design)
4. [Application Structure](#application-structure)
5. [User Management App](#user-management-app)
6. [Vector Data App](#vector-data-app)
7. [Raster Data App](#raster-data-app)
8. [Census Data App](#census-data-app)
9. [FastAPI Migration Guide](#fastapi-migration-guide)
10. [API Endpoints Summary](#api-endpoints-summary)

---

## Project Overview

**CIM Wizard Integrated Service** is a comprehensive Django-based platform for urban analysis and spatial data management. It combines four specialized data services into a unified system that supports geospatial data processing, demographic analysis, and building energy modeling.

### Key Features
- **Multi-tenant architecture** with PostgreSQL schema separation
- **Spatial data processing** for vector and raster operations
- **Demographic analysis** with Italian ISTAT census integration
- **Building energy modeling** with 3DCityDB compatibility
- **User management** with role-based access control
- **API-first design** with REST endpoints

### Technology Stack
- **Backend**: Django 4.x with Django REST Framework
- **Database**: PostgreSQL with PostGIS extension
- **Spatial**: GDAL/OGR for geospatial operations
- **Multi-tenancy**: django-tenants for schema separation
- **Authentication**: Token-based authentication

---

## Architecture

### Multi-Schema Database Design

The application implements a four-schema PostgreSQL architecture using `django-tenants`:

```
┌─────────────────┐
│   public        │  ← User management, authentication
├─────────────────┤
│   vector        │  ← Spatial vector data, buildings, scenarios
├─────────────────┤
│   raster        │  ← DTM/DSM data, height calculations
├─────────────────┤
│   census        │  ← Demographic data, census statistics
└─────────────────┘
```

### Service Integration
```
┌─────────────────────────────────────────────────────────────┐
│                CIM Wizard Integrated Service                │
├─────────────────┬─────────────────┬─────────────────┬───────┤
│ User Management │   Vector Data   │   Raster Data   │Census │
│                 │                 │                 │Data   │
│ • Authentication│ • Project Mgmt  │ • DTM/DSM       │• ISTAT│
│ • Authorization │ • Building Geo  │ • Height Calc   │• Demo │
│ • API Keys      │ • Calculations  │ • Clipping      │• GIS  │
│ • Activity Log  │ • 3DCityDB      │ • Processing    │• Query│
└─────────────────┴─────────────────┴─────────────────┴───────┘
```

---

## Database Schema Design

### Schema Separation Strategy

1. **Public Schema** (`user_management`)
   - Shared across all tenants
   - User accounts, authentication, sessions
   - API key management
   - Activity logging

2. **Vector Schema** (`vector_data`)
   - Project scenarios and boundaries
   - Building geometries (LoD 0-2)
   - Building properties and calculations
   - Spatial analysis results

3. **Raster Schema** (`raster_data`)
   - DTM/DSM raster datasets
   - Processing jobs and status
   - Building height calculations
   - Spatial raster operations

4. **Census Schema** (`census_data`)
   - Census geographical sections
   - Demographic statistics (ISTAT P1-P138)
   - Housing characteristics
   - Administrative hierarchies

---

## Application Structure

### Django Project Layout
```
cim_wizard_integrated/
├── cim_wizard_integrated/          # Main Django project
│   ├── settings.py                # Multi-tenant configuration
│   ├── urls.py                    # Main URL routing
│   └── routers.py                 # Database routing logic
├── user_management/               # Public schema app
├── vector_data/                   # Vector schema app
├── raster_data/                   # Raster schema app
├── census_data/                   # Census schema app
└── main.py                        # FastAPI implementation (WIP)
```

### Key Configuration Files

**settings.py** - Multi-tenant setup:
```python
# django-tenants configuration
TENANT_MODEL = "user_management.Client"
TENANT_DOMAIN_MODEL = "user_management.Domain"
PUBLIC_SCHEMA_NAME = 'public'

SHARED_APPS = [
    'django_tenants',
    'django.contrib.admin',
    # ... core Django apps
    'user_management',  # Public schema only
]

TENANT_APPS = [
    'vector_data',      # Vector schema
    'raster_data',      # Raster schema  
    'census_data',      # Census schema
]
```

---

## User Management App

**Schema**: `public`  
**Purpose**: Authentication, authorization, user profiles, and API key management

### Database Models

#### 1. User Model (Extended AbstractUser)
```python
class User(AbstractUser, SchemaInspectionMixin):
    user_id = UUIDField()                    # Unique identifier
    full_name = CharField(max_length=255)    # Complete name
    organization = CharField(max_length=255) # Institution
    role = CharField(choices=USER_ROLES)     # admin/researcher/analyst/viewer/guest
    api_access_enabled = BooleanField()      # API privileges
    preferred_coordinate_system = IntegerField() # Default EPSG
```

#### 2. UserProfile Model
```python
class UserProfile(models.Model):
    user = OneToOneField(User)
    research_interests = TextField()         # Research focus areas
    expertise_areas = JSONField()            # List of expertise
    default_map_zoom = IntegerField()        # Map preferences
    default_map_center = JSONField()         # Center coordinates
```

#### 3. APIKey Model
```python
class APIKey(models.Model):
    user = ForeignKey(User)
    key_id = UUIDField()                     # Key identifier
    name = CharField()                       # Human-readable name
    key_hash = CharField()                   # Hashed key value
    # Permissions
    can_read_vector = BooleanField()
    can_write_vector = BooleanField()
    can_read_raster = BooleanField()
    # Usage tracking
    usage_count = BigIntegerField()
    last_used = DateTimeField()
```

#### 4. UserSession Model
```python
class UserSession(models.Model):
    user = ForeignKey(User)
    session_id = UUIDField()
    ip_address = GenericIPAddressField()
    login_time = DateTimeField()
    logout_time = DateTimeField()
    project_accessed = JSONField()           # Projects in session
```

#### 5. UserActivity Model
```python
class UserActivity(models.Model):
    user = ForeignKey(User)
    session = ForeignKey(UserSession)
    activity_type = CharField()              # login/logout/api_call/etc
    description = TextField()
    endpoint = CharField()                   # API endpoint accessed
    execution_time = FloatField()            # Performance metrics
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users/auth/login/` | User authentication |
| POST | `/api/users/auth/logout/` | User logout |
| GET | `/api/users/users/` | List users (admin only) |
| GET/PUT | `/api/users/profile/` | User profile management |
| GET/POST | `/api/users/api-keys/` | API key management |
| GET | `/api/users/dashboard/` | User dashboard with statistics |
| GET | `/api/users/permissions/` | User permissions summary |

### Key Views and Functions

#### Authentication Views
```python
def user_login(request):
    # Authenticate user
    # Create auth token
    # Start user session
    # Log activity
    
def user_logout(request):
    # End session
    # Delete token
    # Log activity
```

#### Management Views
```python
class UserListView(ListCreateAPIView):
    # List/create users (admin only)
    
class UserProfileView(RetrieveUpdateAPIView):
    # Manage user profiles
    
class APIKeyListView(ListCreateAPIView):
    # Manage API keys
```

#### Analytics Views
```python
def user_dashboard(request):
    # Recent activity (7 days)
    # Active sessions count
    # API usage statistics
    # Activity breakdown (30 days)
```

---

## Vector Data App

**Schema**: `vector`  
**Purpose**: Spatial vector data operations, building management, and geometric calculations

### Database Models

#### 1. ProjectScenario Model
```python
class ProjectScenario(gis_models.Model):
    project_id = CharField(max_length=100)        # Unique project ID
    scenario_id = CharField(max_length=100)       # Scenario ID
    project_name = CharField(max_length=255)      # Human-readable name
    
    # Spatial fields
    project_boundary = GeometryField(srid=4326)   # Project area
    project_center = PointField(srid=4326)        # Map center
    project_zoom = IntegerField(default=15)       # Default zoom
    project_crs = IntegerField(default=4326)      # Coordinate system
    
    # Census integration
    census_boundry = MultiPolygonField()          # Census boundaries
```

#### 2. Building Model
```python
class Building(gis_models.Model):
    building_id = CharField(max_length=100)       # Unique building ID
    lod = IntegerField(default=0)                 # Level of Detail (0-4)
    building_geometry = GeometryField(srid=4326)  # Building footprint
    building_geometry_source = CharField()        # Data source (osm/cadastral)
    census_id = BigIntegerField()                 # Associated census section
    
    # 3DCityDB compatibility
    building_surfaces_lod12 = JSONField()         # Semantic surfaces
```

#### 3. BuildingProperties Model
```python
class BuildingProperties(models.Model):
    building_id = CharField(max_length=100)
    project_id = CharField(max_length=100)
    scenario_id = CharField(max_length=100)
    lod = IntegerField(default=0)
    
    # Geometric properties
    height = FloatField()                         # Building height (m)
    area = FloatField()                           # Footprint area (m²)
    volume = FloatField()                         # Building volume (m³)
    number_of_floors = FloatField()               # Floor count
    
    # Building characteristics
    type = CharField()                            # residential/commercial/etc
    const_period_census = CharField()             # Census construction period
    const_year = IntegerField()                   # Construction year
    const_TABULA = CharField()                    # TABULA energy classification
    
    # Demographics
    n_people = IntegerField()                     # Estimated population
    n_family = IntegerField()                     # Number of families
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/vector/scenarios/` | Project scenario management |
| GET/PUT/DELETE | `/api/vector/scenarios/{project_id}/` | Scenario details |
| GET/POST | `/api/vector/buildings/` | Building data operations |
| GET/PUT/DELETE | `/api/vector/buildings/{building_id}/` | Building details |
| GET/POST | `/api/vector/buildings/{id}/properties/` | Building properties |
| POST | `/api/vector/calculate/` | Feature calculations |
| POST | `/api/vector/calculate/{feature_name}/` | Named calculations |

### Calculation Endpoints (Legacy CIM Wizard)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/vector/milestones/1/scenario/` | Scenario initialization |
| POST | `/api/vector/milestones/1/building/` | Building initialization |
| POST | `/api/vector/milestones/2/` | Height calculation |
| POST | `/api/vector/milestones/3/` | Volume calculation |
| POST | `/api/vector/milestones/4/demographic/` | Demographic calculation |

### Export Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/vector/export/buildings/` | Buildings as GeoJSON |
| GET | `/api/vector/export/scenarios/` | Scenarios as GeoJSON |
| GET | `/api/vector/export/properties/` | Properties as JSON |

### Key Views and Functions

#### Calculator Functions
```python
def single_feature_calculator(request, feature_name=None):
    # Route to specific calculators:
    # - scenario_geo: Project boundary calculations
    # - building_geo: Building geometry operations
    # - building_height: Height estimation
    # - building_area: Area calculations
    # - building_volume: Volume calculations
    
def _calculate_building_geometry(input_data):
    # Query buildings by IDs and LoD
    # Return GeoJSON FeatureCollection
    
def _calculate_building_area(input_data):
    # Calculate area from geometry
    # Return area in square meters
```

#### Spatial Operations
```python
@api_view(['POST'])
def spatial_intersect(request):
    # Spatial intersection analysis
    
@api_view(['POST'])  
def spatial_buffer(request):
    # Buffer analysis operations
```

---

## Raster Data App

**Schema**: `raster`  
**Purpose**: DTM/DSM raster processing, height calculations, and spatial raster operations

### Database Models

#### 1. RasterDataset Model
```python
class RasterDataset(gis_models.Model):
    filename = CharField(max_length=255)
    raster_type = CharField(choices=['DTM', 'DSM', 'DEM', 'HEIGHT'])
    rast = RasterField()                          # PostGIS raster data
    
    # Spatial metadata
    srid = IntegerField(default=4326)
    extent = PolygonField()                       # Spatial extent
    pixel_size_x = FloatField()
    pixel_size_y = FloatField()
    width = IntegerField()                        # Raster dimensions
    height = IntegerField()
    
    # Value statistics
    min_value = FloatField()
    max_value = FloatField()
    nodata_value = FloatField()
    
    # Processing metadata
    processing_parameters = JSONField()
    source_data = TextField()
```

#### 2. RasterProcessingJob Model
```python
class RasterProcessingJob(models.Model):
    job_id = CharField(max_length=100)
    job_type = CharField(choices=['CLIP', 'HEIGHT_CALC', 'INTERSECT'])
    status = CharField(choices=['PENDING', 'RUNNING', 'COMPLETED', 'FAILED'])
    
    # Input/output references
    input_raster = ForeignKey(RasterDataset)
    output_raster = ForeignKey(RasterDataset)
    input_geometry = GeometryField()              # Input polygon for operations
    
    # Processing data
    processing_parameters = JSONField()
    result_data = JSONField()                     # Operation results
    error_message = TextField()
    
    # Timing
    created_at = DateTimeField()
    started_at = DateTimeField()
    completed_at = DateTimeField()
    progress_percent = IntegerField(0-100)
```

#### 3. BuildingHeightResult Model
```python
class BuildingHeightResult(models.Model):
    building_id = CharField(max_length=100)
    project_id = CharField(max_length=100)
    scenario_id = CharField(max_length=100)
    
    # Processing references
    processing_job = ForeignKey(RasterProcessingJob)
    dtm_raster = ForeignKey(RasterDataset)        # Ground elevation
    dsm_raster = ForeignKey(RasterDataset)        # Surface elevation
    building_geometry = GeometryField()
    
    # Height results
    ground_height = FloatField()                  # DTM average
    surface_height = FloatField()                 # DSM average  
    calculated_height = FloatField()              # DSM - DTM
    
    # Statistics
    min_ground_height = FloatField()
    max_ground_height = FloatField()
    min_surface_height = FloatField()
    max_surface_height = FloatField()
    
    # Quality metrics
    pixel_count = IntegerField()
    coverage_ratio = FloatField(0.0-1.0)          # Coverage quality
    calculation_method = CharField(default='mean')
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/raster/datasets/` | Raster dataset management |
| GET/PUT/DELETE | `/api/raster/datasets/{id}/` | Dataset details |
| GET/POST | `/api/raster/jobs/` | Processing job management |
| GET | `/api/raster/jobs/{job_id}/` | Job status and results |
| GET | `/api/raster/heights/` | Height calculation results |

### Raster Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/raster/clip/dtm/` | Clip DTM by polygon |
| POST | `/api/raster/clip/dsm/` | Clip DSM by polygon |
| POST | `/api/raster/clip/{type}/` | Generic raster clipping |
| POST | `/api/raster/heights/calculate/` | Calculate building heights |
| POST | `/api/raster/heights/calculate/fast/` | Optimized height calculation |

### Key Views and Functions

#### Raster Clipping
```python
def clip_raster(request, raster_type):
    # Parse polygon geometry
    # Create processing job
    # SQL query for ST_Clip operation:
    query = """
    SELECT ST_AsGDALRaster(
               ST_Clip(rast, ST_GeomFromText(%s, 4326)),
               %s
           ) AS clipped_raster
    FROM {table_name}
    WHERE ST_Intersects(rast, ST_GeomFromText(%s, 4326))
    """
    # Return base64 encoded raster
```

#### Height Calculation
```python
def calculate_building_heights(request):
    # Parse GeoJSON features with building geometries
    # Process in batches with ThreadPoolExecutor
    # For each building:
    #   - Query DTM for ground height
    #   - Query DSM for surface height  
    #   - Calculate height = DSM - DTM
    #   - Store results in BuildingHeightResult
    
def process_building_height_batch(features, job_id):
    # Parallel processing function
    # DTM query: AVG/MIN/MAX statistics
    # DSM query: AVG/MIN/MAX statistics
    # Return height calculations
```

#### SQL Queries for Height Calculation
```sql
-- DTM Ground Height Query
SELECT AVG((ST_SummaryStats(ST_Resample(ST_Clip(rast, geometry), 10))).mean),
       MIN((ST_SummaryStats(ST_Resample(ST_Clip(rast, geometry), 10))).min),
       MAX((ST_SummaryStats(ST_Resample(ST_Clip(rast, geometry), 10))).max)
FROM dtm_raster
WHERE ST_Intersects(rast, geometry);

-- DSM Surface Height Query  
SELECT AVG((ST_SummaryStats(ST_Resample(ST_Clip(rast, geometry), 10))).mean),
       MIN((ST_SummaryStats(ST_Resample(ST_Clip(rast, geometry), 10))).min),
       MAX((ST_SummaryStats(ST_Resample(ST_Clip(rast, geometry), 10))).max)
FROM dsm_raster
WHERE ST_Intersects(rast, geometry);
```

---

## Census Data App

**Schema**: `census`  
**Purpose**: Demographic analysis, Italian ISTAT census data, and administrative boundaries

### Database Models

#### 1. CensusSection Model
```python
class CensusSection(gis_models.Model):
    # Primary identifier
    SEZ2011 = BigIntegerField(unique=True)        # Census section ID
    
    # Spatial fields
    geometry = MultiPolygonField()                # Section boundaries
    crs = CharField(default="urn:ogc:def:crs:OGC:1.3:CRS84")
    Shape_Area = FloatField()                     # Area in square meters
    
    # Administrative hierarchy (Italian system)
    CODREG = CharField(max_length=10)             # Region code
    REGIONE = CharField(max_length=50)            # Region name
    CODPRO = CharField(max_length=10)             # Province code  
    PROVINCIA = CharField(max_length=50)          # Province name
    CODCOM = CharField(max_length=10)             # Municipality code
    COMUNE = CharField(max_length=50)             # Municipality name
    PROCOM = CharField(max_length=10)             # Province-Municipality
    NSEZ = CharField(max_length=10)               # Section number
```

#### 2. DemographicData Model
```python
class DemographicData(models.Model):
    census_section = OneToOneField(CensusSection)
    
    # Core population data (ISTAT variables P1-P10)
    P1 = IntegerField()                           # Total resident population
    P2 = IntegerField()                           # Male population
    P3 = IntegerField()                           # Female population
    P4 = IntegerField()                           # Population aged 0-5
    P5 = IntegerField()                           # Population aged 6-14
    P6 = IntegerField()                           # Population aged 15-64
    P7 = IntegerField()                           # Population aged 65+
    P8 = IntegerField()                           # Italian citizens
    P9 = IntegerField()                           # Foreign citizens
    P10 = IntegerField()                          # Population in collective households
    
    # Extended demographic variables (P11-P66, P128-P138)
    P11 = IntegerField()  # ... through P66
    P128 = IntegerField() # ... through P138
    
    # Building age variables (E8-E17)  
    E8 = IntegerField()   # Buildings before 1919
    # ... through E17 (post-2005)
    
    # Metadata
    data_year = IntegerField(default=2011)
    data_source = CharField(default="ISTAT")
```

#### 3. HousingData Model  
```python
class HousingData(models.Model):
    census_section = OneToOneField(CensusSection)
    
    # Housing units
    total_housing_units = IntegerField()
    occupied_housing_units = IntegerField()
    vacant_housing_units = IntegerField()
    
    # Building types
    buildings_residential = IntegerField()
    buildings_non_residential = IntegerField()
    
    # Construction periods (ISTAT classification)
    buildings_before_1919 = IntegerField()
    buildings_1919_1945 = IntegerField()
    buildings_1946_1970 = IntegerField()
    buildings_1971_1980 = IntegerField()
    buildings_1981_1990 = IntegerField()
    buildings_1991_2000 = IntegerField()
    buildings_2001_2005 = IntegerField()
    buildings_after_2005 = IntegerField()
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/census/sections/` | Census section management |
| GET/PUT/DELETE | `/api/census/sections/{SEZ2011}/` | Section details |
| GET/POST | `/api/census/demographics/` | Demographic data |
| GET/POST | `/api/census/housing/` | Housing data |

### Spatial Query Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/census/spatial/?polygonArray=[coords]` | Spatial query by polygon |
| POST | `/api/census/spatial/` | Advanced spatial query |
| POST | `/api/census/save/` | Save census data |
| GET | `/api/census/data/` | Get census data by filters |
| POST | `/api/census/query/` | Query by demographic properties |

### Key Views and Functions

#### Spatial Queries
```python
def census_spatial(request):
    # Parse polygon coordinates from query parameters
    # Create Polygon geometry
    # Query intersecting census sections:
    census_sections = CensusSection.objects.filter(
        geometry__intersects=polygon
    ).select_related('demographic_data', 'housing_data')
    
    # Return GeoJSON FeatureCollection with:
    # - Section geometries
    # - Demographic summaries  
    # - Housing statistics
    # - Population density calculations

def census_spatial_post(request):
    # Advanced POST version with filters:
    # - Administrative filters (region/province/municipality)
    # - Include/exclude demographics and housing
    # - Summary statistics (total population, housing units)
```

#### Data Management
```python
def save_census_data(request):
    # Save/update census data for a section
    # Handle demographic_data and housing_data
    # Get or create CensusSection
    # Update related DemographicData and HousingData

def query_census_properties(request):
    # Query by demographic properties:
    # - Population ranges (min/max)
    # - Housing unit filters
    # - Administrative area filters
    # Return matching sections with full data
```

#### Calculated Properties
```python
def get_population_density(self):
    # Calculate people per square kilometer
    if self.P1 and self.census_section.Shape_Area:
        area_km2 = self.census_section.Shape_Area / 1000000
        return self.P1 / area_km2

def get_occupancy_rate(self):
    # Calculate housing occupancy rate
    if self.total_housing_units > 0:
        return self.occupied_housing_units / self.total_housing_units
```

---

## FastAPI Migration Guide

Based on the Django implementation analysis, here's a comprehensive guide for migrating to FastAPI:

### 1. Project Structure
```
fastapi_cim_wizard/
├── app/
│   ├── core/
│   │   ├── config.py              # Settings and configuration
│   │   ├── database.py            # Database connection and session
│   │   ├── security.py            # Authentication and authorization
│   │   └── middleware.py          # Custom middleware
│   ├── models/
│   │   ├── user.py               # User management models
│   │   ├── vector.py             # Vector data models
│   │   ├── raster.py             # Raster data models
│   │   └── census.py             # Census data models
│   ├── schemas/
│   │   ├── user.py               # Pydantic schemas for users
│   │   ├── vector.py             # Pydantic schemas for vector
│   │   ├── raster.py             # Pydantic schemas for raster
│   │   └── census.py             # Pydantic schemas for census
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── auth.py           # Authentication endpoints
│   │   │   ├── users.py          # User management
│   │   │   ├── vector.py         # Vector operations
│   │   │   ├── raster.py         # Raster operations
│   │   │   └── census.py         # Census operations
│   │   └── routes.py             # API router setup
│   ├── services/
│   │   ├── user_service.py       # User business logic
│   │   ├── vector_service.py     # Vector processing
│   │   ├── raster_service.py     # Raster processing
│   │   └── census_service.py     # Census operations
│   └── utils/
│       ├── spatial.py            # Spatial utilities
│       ├── raster_ops.py         # Raster operations
│       └── validation.py         # Custom validators
├── alembic/                      # Database migrations
├── tests/
└── main.py                       # FastAPI app entry point
```

### 2. Database Configuration

#### SQLAlchemy Setup with Multi-Schema Support
```python
# app/core/database.py
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema
from geoalchemy2 import Geometry
import asyncpg

# Multi-schema configuration
SCHEMAS = {
    'public': 'user_management',
    'vector': 'vector_data', 
    'raster': 'raster_data',
    'census': 'census_data'
}

# Create bases for each schema
UserBase = declarative_base(metadata=MetaData(schema='public'))
VectorBase = declarative_base(metadata=MetaData(schema='vector'))
RasterBase = declarative_base(metadata=MetaData(schema='raster'))
CensusBase = declarative_base(metadata=MetaData(schema='census'))

async def create_schemas():
    """Create schemas if they don't exist"""
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        for schema in SCHEMAS.keys():
            if schema != 'public':
                await conn.execute(CreateSchema(schema, if_not_exists=True))
```

#### Model Examples
```python
# app/models/user.py
from sqlalchemy import Column, String, Integer, Boolean, DateTime, UUID
from app.core.database import UserBase

class User(UserBase):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(UUID, unique=True, nullable=False)
    username = Column(String(150), unique=True, nullable=False)
    email = Column(String(254), unique=True, nullable=False)
    role = Column(String(20), nullable=False, default='viewer')
    api_access_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False)

# app/models/vector.py  
from geoalchemy2 import Geometry
from app.core.database import VectorBase

class Building(VectorBase):
    __tablename__ = 'buildings'
    __table_args__ = {'schema': 'vector'}
    
    id = Column(Integer, primary_key=True)
    building_id = Column(String(100), nullable=False)
    lod = Column(Integer, default=0)
    building_geometry = Column(Geometry('GEOMETRY', srid=4326))
    building_geometry_source = Column(String(50), default='osm')
```

### 3. Pydantic Schemas
```python
# app/schemas/user.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    full_name: Optional[str] = None
    organization: Optional[str] = None
    role: str = Field(default='viewer')

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: int
    user_id: UUID
    api_access_enabled: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

# app/schemas/vector.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from geojson_pydantic import Feature, FeatureCollection

class BuildingBase(BaseModel):
    building_id: str
    lod: int = 0
    building_geometry_source: str = 'osm'
    census_id: Optional[int] = None

class BuildingCreate(BuildingBase):
    building_geometry: Dict[str, Any]  # GeoJSON geometry

class BuildingResponse(BuildingBase):
    id: int
    building_geometry: Dict[str, Any]
    area: Optional[float] = None
    
    class Config:
        orm_mode = True
```

### 4. API Endpoints

#### Authentication
```python
# app/api/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.security import create_access_token, verify_password
from app.schemas.user import Token

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
```

#### Vector Data Operations
```python
# app/api/endpoints/vector.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.vector import BuildingResponse, BuildingCreate
from app.services.vector_service import VectorService

router = APIRouter()

@router.get("/buildings/", response_model=List[BuildingResponse])
async def list_buildings(
    skip: int = 0,
    limit: int = 100,
    building_id: Optional[str] = None,
    lod: Optional[int] = None,
    vector_service: VectorService = Depends()
):
    return await vector_service.get_buildings(
        skip=skip, 
        limit=limit, 
        filters={"building_id": building_id, "lod": lod}
    )

@router.post("/calculate/{feature_name}")
async def calculate_feature(
    feature_name: str,
    input_data: Dict[str, Any],
    vector_service: VectorService = Depends()
):
    result = await vector_service.calculate_feature(feature_name, input_data)
    return {"feature_name": feature_name, "result": result}
```

#### Raster Operations
```python
# app/api/endpoints/raster.py
from fastapi import APIRouter, UploadFile, File
from app.schemas.raster import HeightCalculationRequest, HeightCalculationResponse

router = APIRouter()

@router.post("/heights/calculate/", response_model=HeightCalculationResponse)
async def calculate_building_heights(
    request: HeightCalculationRequest,
    raster_service: RasterService = Depends()
):
    job_id = await raster_service.calculate_heights(request.features)
    return HeightCalculationResponse(job_id=job_id, status="running")

@router.post("/clip/{raster_type}/")
async def clip_raster(
    raster_type: str,
    polygon: Dict[str, Any],
    raster_service: RasterService = Depends()
):
    result = await raster_service.clip_raster(raster_type, polygon)
    return result
```

### 5. Service Layer
```python
# app/services/vector_service.py
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.vector import Building, BuildingProperties
from app.core.database import get_db

class VectorService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
    
    async def get_buildings(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Building]:
        query = self.db.query(Building)
        
        if filters:
            if filters.get('building_id'):
                query = query.filter(Building.building_id == filters['building_id'])
            if filters.get('lod') is not None:
                query = query.filter(Building.lod == filters['lod'])
        
        return query.offset(skip).limit(limit).all()
    
    async def calculate_feature(self, feature_name: str, input_data: Dict[str, Any]):
        calculators = {
            'building_area': self._calculate_building_area,
            'building_height': self._calculate_building_height,
            'building_volume': self._calculate_building_volume,
        }
        
        if feature_name not in calculators:
            raise ValueError(f"Unknown feature: {feature_name}")
        
        return await calculators[feature_name](input_data)
```

### 6. Background Tasks for Processing
```python
# app/services/raster_service.py
from fastapi import BackgroundTasks
from celery import Celery
import asyncio

class RasterService:
    def __init__(self):
        self.celery_app = Celery('raster_tasks', broker='redis://localhost:6379')
    
    async def calculate_heights(
        self, 
        features: List[Dict[str, Any]],
        background_tasks: BackgroundTasks
    ) -> str:
        job_id = str(uuid.uuid4())
        
        # Add background task
        background_tasks.add_task(
            self._process_height_calculation,
            job_id,
            features
        )
        
        return job_id
    
    async def _process_height_calculation(
        self, 
        job_id: str, 
        features: List[Dict[str, Any]]
    ):
        # Parallel processing with asyncio
        tasks = [
            self._calculate_single_building_height(feature)
            for feature in features
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Store results in database
        await self._store_height_results(job_id, results)
```

### 7. Key Differences from Django

#### Database Access
- **Django**: ORM with automatic migrations
- **FastAPI**: SQLAlchemy with Alembic migrations

#### Request Handling  
- **Django**: Class-based views with built-in serialization
- **FastAPI**: Function-based endpoints with Pydantic validation

#### Authentication
- **Django**: Built-in session and token auth
- **FastAPI**: JWT tokens with OAuth2 flows

#### Background Processing
- **Django**: Celery or Django-RQ
- **FastAPI**: Background tasks or Celery

#### Spatial Data
- **Django**: GeoDjango with automatic spatial queries
- **FastAPI**: GeoAlchemy2 with manual spatial operations

### 8. Migration Strategy

1. **Phase 1**: Setup FastAPI structure with core models
2. **Phase 2**: Implement user management and authentication  
3. **Phase 3**: Migrate vector data operations
4. **Phase 4**: Implement raster processing
5. **Phase 5**: Add census data functionality
6. **Phase 6**: Performance optimization and testing

### 9. Performance Considerations

#### Async Operations
```python
# Async database operations
@router.get("/buildings/")
async def get_buildings():
    async with AsyncSession() as session:
        result = await session.execute(select(Building))
        return result.scalars().all()

# Parallel processing for raster operations
async def process_multiple_buildings(buildings):
    tasks = [process_single_building(building) for building in buildings]
    return await asyncio.gather(*tasks)
```

#### Caching
```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@cache(expire=3600)  # 1 hour cache
async def get_census_data(section_id: int):
    return await census_service.get_section(section_id)
```

---

## API Endpoints Summary

### Complete API Reference

| Service | Method | Endpoint | Description |
|---------|--------|----------|-------------|
| **Authentication** | POST | `/api/auth/login/` | User login |
| | POST | `/api/auth/logout/` | User logout |
| | POST | `/api/auth/token/` | Token refresh |
| **User Management** | GET | `/api/users/users/` | List users |
| | POST | `/api/users/users/` | Create user |
| | GET | `/api/users/profile/` | Get user profile |
| | PUT | `/api/users/profile/` | Update profile |
| | GET | `/api/users/api-keys/` | List API keys |
| | POST | `/api/users/api-keys/` | Create API key |
| | GET | `/api/users/dashboard/` | User dashboard |
| **Vector Data** | GET | `/api/vector/scenarios/` | List scenarios |
| | POST | `/api/vector/scenarios/` | Create scenario |
| | GET | `/api/vector/buildings/` | List buildings |
| | POST | `/api/vector/buildings/` | Create building |
| | POST | `/api/vector/calculate/{feature}/` | Calculate features |
| | GET | `/api/vector/export/buildings/` | Export buildings |
| **Raster Data** | GET | `/api/raster/datasets/` | List datasets |
| | POST | `/api/raster/datasets/` | Upload dataset |
| | POST | `/api/raster/clip/{type}/` | Clip raster |
| | POST | `/api/raster/heights/calculate/` | Calculate heights |
| | GET | `/api/raster/jobs/{id}/` | Job status |
| **Census Data** | GET | `/api/census/sections/` | List sections |
| | GET | `/api/census/spatial/` | Spatial query |
| | POST | `/api/census/spatial/` | Advanced spatial query |
| | POST | `/api/census/query/` | Property-based query |
| | GET | `/api/census/data/` | Get census data |

This comprehensive documentation provides the foundation needed to understand and recreate the CIM Wizard Integrated Service using FastAPI, maintaining the same multi-schema architecture and functionality while leveraging FastAPI's modern async capabilities.