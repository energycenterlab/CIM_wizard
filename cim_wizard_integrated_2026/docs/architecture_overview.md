# CIM Wizard Integrated - Architecture Overview

## System Architecture

CIM Wizard Integrated is a comprehensive geospatial data processing system that combines multiple services into a unified FastAPI application with direct database integration.

```
┌─────────────────────────────────────────────────────────┐
│                    Client Applications                   │
│         (Web UI, Mobile Apps, Third-party Systems)       │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                     FastAPI Gateway                      │
│                    (main.py - Port 8000)                 │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │  Vector  │  │  Census  │  │  Raster  │  │Pipeline │ │
│  │  Routes  │  │  Routes  │  │  Routes  │  │ Routes  │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    Service Layer                         │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │    Census    │  │    Raster    │  │   Pipeline    │  │
│  │   Service    │  │   Service    │  │   Executor    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         │                  │                  │          │
│         └──────────────────┴──────────────────┘          │
│                            │                             │
│                    ┌───────────────┐                     │
│                    │ Data Manager  │                     │
│                    └───────────────┘                     │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  Data Access Layer                       │
│                    (SQLAlchemy ORM)                      │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  cim_vector  │  │  cim_census  │  │  cim_raster  │  │
│  │    Models    │  │    Models    │  │    Models    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              PostgreSQL Database + PostGIS               │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  cim_vector  │  │  cim_census  │  │  cim_raster  │  │
│  │    Schema    │  │    Schema    │  │    Schema    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Component Description

### 1. API Gateway Layer

**FastAPI Application** (`main.py`)
- Entry point for all HTTP requests
- CORS middleware for cross-origin requests
- Automatic OpenAPI documentation
- Request validation with Pydantic
- Dependency injection for database sessions

### 2. Route Handlers

**Vector Routes** (`api/vector_routes.py`)
- Project and scenario management
- Building geometry operations
- Grid network data access
- GeoJSON exports

**Census Routes** (`api/census_routes.py`)
- Census zone queries
- Population statistics
- Building age distribution
- Demographic analysis

**Raster Routes** (`api/raster_routes.py`)
- Height calculation from DTM/DSM
- Raster clipping operations
- Elevation queries
- Statistics calculation

**Pipeline Routes** (`api/pipeline_routes.py`)
- Feature calculation orchestration
- Method chaining support
- Predefined workflows
- Configuration management

### 3. Service Layer

**Census Service** (`services/census_service.py`)
- Direct database queries to census data
- Spatial intersection operations
- Statistical aggregations
- No external API dependencies

**Raster Service** (`services/raster_service.py`)
- PostGIS raster operations
- Height calculation (DSM - DTM)
- Result caching mechanism
- Batch processing support

**Pipeline Executor** (`core/pipeline_executor.py`)
- Calculator instance management
- Dependency resolution
- Method selection strategy
- Parallel execution support

**Data Manager** (`core/data_manager.py`)
- Context management
- Service instantiation
- Feature storage
- Configuration loading

### 4. Calculator Layer

**Calculator Classes** (`calculators/*.py`)
- Feature-specific logic
- Multiple calculation methods
- Fallback strategies
- Validation and logging

Each calculator:
- Receives executor and data_manager
- Implements multiple methods
- Handles errors gracefully
- Returns calculated values

### 5. Data Models

**Vector Models** (`models/vector.py`)
- ProjectScenario
- Building
- BuildingProperties
- GridBus
- GridLine

**Census Models** (`models/census.py`)
- CensusGeo (with 100+ attributes)

**Raster Models** (`models/raster.py`)
- DTMRaster
- DSMRaster
- BuildingHeightCache

### 6. Database Layer

**PostgreSQL with PostGIS**
- Three schemas for separation
- Spatial indexing
- Raster data support
- Transaction management

## Data Flow

### Example: Building Height Calculation

1. **Client Request**
   ```
   POST /api/pipeline/calculate_feature
   {
     "feature_name": "building_height",
     "building_geometry": {...}
   }
   ```

2. **Route Handler**
   - Validates request with Pydantic
   - Creates database session
   - Initializes data manager

3. **Pipeline Executor**
   - Loads BuildingHeightCalculator
   - Checks dependencies
   - Selects calculation method

4. **Calculator Execution**
   - Method 1: Try raster service
   - Gets RasterService from data manager
   - Queries DTM/DSM from database

5. **Raster Service**
   - Executes PostGIS queries
   - Calculates average heights
   - Returns height difference

6. **Result Storage**
   - Store in data manager
   - Cache in database
   - Return to client

## Key Design Patterns

### 1. Dependency Injection
```python
@router.post("/endpoint")
async def handler(db: Session = Depends(get_db)):
    # Database session injected
```

### 2. Service Pattern
```python
class CensusService:
    def __init__(self, db_session):
        self.db = db_session
```

### 3. Strategy Pattern
```python
class Calculator:
    def method1(self): pass
    def method2(self): pass  # Fallback
```

### 4. Factory Pattern
```python
def get_calculator_instance(feature_name):
    # Dynamic instantiation
```

## Integration Points

### Previous Architecture (v1.0)
- **Vector Gateway**: API calls → Direct DB
- **Census Gateway**: API calls → Direct DB
- **Raster Gateway**: API calls → Direct DB

### Current Architecture (v2.0)
- All services integrated
- Shared database connections
- Transaction support
- No network latency

## Performance Optimizations

### 1. Connection Pooling
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20
)
```

### 2. Result Caching
- Database-level caching
- Application-level caching
- Calculator instance caching

### 3. Parallel Execution
- Independent features in parallel
- ThreadPoolExecutor for I/O
- Async route handlers

### 4. Spatial Indexing
```sql
CREATE INDEX idx_geometry ON table USING GIST(geometry);
```

## Scalability Considerations

### Horizontal Scaling
- Stateless application
- Multiple FastAPI instances
- Load balancer distribution
- Shared database

### Vertical Scaling
- Database optimization
- Connection pool tuning
- Memory management
- CPU utilization

### Caching Strategy
- Redis for session data
- Database result caching
- Application-level caching
- CDN for static assets

## Security Considerations

### Current Implementation
- CORS configured
- Input validation
- SQL injection prevention (ORM)
- Error message sanitization

### Production Recommendations
- Authentication (JWT/OAuth2)
- Rate limiting
- API key management
- HTTPS enforcement
- Database encryption
- Audit logging

## Monitoring and Logging

### Application Metrics
- Request/response times
- Error rates
- Feature calculation times
- Cache hit rates

### Database Metrics
- Query performance
- Connection pool status
- Index usage
- Storage utilization

### Logging Strategy
- Structured logging
- Log aggregation
- Error tracking
- Performance monitoring

## Deployment Architecture

### Development
```
Local PostgreSQL → FastAPI (uvicorn) → Browser
```

### Production
```
PostgreSQL Cluster
    ↓
Load Balancer
    ↓
FastAPI Instances (Gunicorn + Uvicorn)
    ↓
Nginx Reverse Proxy
    ↓
CDN/Cache Layer
    ↓
Clients
```

## Technology Stack

### Core Technologies
- **Language**: Python 3.10+
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL + PostGIS
- **Validation**: Pydantic

### Geospatial Libraries
- **Shapely**: Geometry operations
- **GeoAlchemy2**: Spatial ORM
- **PostGIS**: Spatial database
- **GDAL**: Raster operations

### Development Tools
- **Uvicorn**: ASGI server
- **Docker**: Containerization
- **pytest**: Testing
- **Black**: Code formatting

## Future Enhancements

### Planned Features
1. GraphQL API support
2. WebSocket for real-time updates
3. Machine learning integration
4. 3D visualization support
5. Mobile SDK

### Architecture Evolution
1. Microservices decomposition
2. Event-driven architecture
3. Serverless functions
4. Kubernetes orchestration
5. Multi-region deployment

This architecture provides a robust, scalable, and maintainable system for geospatial data processing with integrated services and efficient database access.