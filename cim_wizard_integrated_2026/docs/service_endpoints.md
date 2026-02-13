# Service Endpoints Documentation

## Base URL
```
http://localhost:8000
```

## Vector Service Endpoints

### Get All Projects
```http
GET /api/vector/projects
```
Query Parameters:
- `limit` (int, default: 100): Maximum number of results
- `offset` (int, default: 0): Pagination offset

Response:
```json
[
  {
    "project_id": "project_001",
    "scenario_id": "scenario_001",
    "project_name": "City Center Development",
    "scenario_name": "Baseline",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### Get Project Dashboard
```http
GET /api/vector/dashboard
```
Response:
```json
{
  "total_projects": 42,
  "projects": [...]
}
```

### Get Project Scenarios
```http
GET /api/vector/pscenarios/{project_id}
```
Path Parameters:
- `project_id`: Project identifier

### Get Building Geometry
```http
GET /api/vector/bgeo/{building_id}
```
Path Parameters:
- `building_id`: Building identifier

Query Parameters:
- `lod` (int, default: 0): Level of detail

### Get Buildings GeoJSON
```http
GET /api/vector/get_buildings_geojson/{project_id}/{scenario_id}
```
Path Parameters:
- `project_id`: Project identifier
- `scenario_id`: Scenario identifier

Query Parameters:
- `lod` (int, default: 0): Level of detail

### Query Building Properties
```http
GET /api/vector/buildingproperties/{project_id}/{scenario_id}
```
Path Parameters:
- `project_id`: Project identifier
- `scenario_id`: Scenario identifier

Query Parameters:
- `building_id` (string, optional): Filter by building
- `lod` (int, default: 0): Level of detail
- `limit` (int): Maximum results
- `offset` (int): Pagination offset

### Find Buildings at Point
```http
GET /api/vector/building_id_fetcher
```
Query Parameters:
- `lat` (float, required): Latitude
- `lng` (float, required): Longitude

### Find Buildings in Buffer
```http
GET /api/vector/building_id_fetcher_buffer
```
Query Parameters:
- `lat` (float, required): Latitude
- `lng` (float, required): Longitude
- `buffer_m` (float, default: 10): Buffer radius in meters

### Get Grid Lines
```http
GET /api/vector/{project_id}/{scenario_id}/gridline
```
Path Parameters:
- `project_id`: Project identifier
- `scenario_id`: Scenario identifier

Query Parameters:
- `network_id` (string, optional): Filter by network
- `limit` (int): Maximum results
- `offset` (int): Pagination offset

## Census Service Endpoints

### Census Spatial Query
```http
POST /api/census/census_spatial
```
Request Body:
```json
{
  "polygon_array": [[lon1, lat1], [lon2, lat2], ...]
}
```
Response: GeoJSON FeatureCollection with census zones

### Get Census by ID
```http
GET /api/census/census/{census_id}
```
Path Parameters:
- `census_id`: SEZ2011 census identifier

Response:
```json
{
  "SEZ2011": 123456,
  "COMUNE": "Milano",
  "P1": 1500,
  "PF1": 650,
  "E3": 45,
  "E4": 42
}
```

### Get Census Population
```http
POST /api/census/census_population
```
Request Body:
```json
{
  "census_ids": [123456, 123457, 123458]
}
```
Response:
```json
{
  "census_population": {
    "123456": 1500,
    "123457": 2100
  },
  "total_population": 3600
}
```

### Get Building Age Distribution
```http
GET /api/census/building_age_distribution/{census_id}
```
Path Parameters:
- `census_id`: SEZ2011 census identifier

Response:
```json
{
  "before_1918": 5,
  "1919_1945": 8,
  "1946_1960": 12,
  "1961_1970": 15,
  "1971_1980": 20,
  "1981_1990": 18,
  "1991_2000": 10,
  "2001_2005": 5,
  "after_2005": 7,
  "total_buildings": 100,
  "residential_buildings": 85
}
```

### Get Census Statistics
```http
POST /api/census/census_statistics
```
Request Body:
```json
{
  "polygon_array": [[lon1, lat1], [lon2, lat2], ...]
}
```
Response:
```json
{
  "total_population": 15000,
  "total_families": 6500,
  "total_buildings": 450,
  "residential_buildings": 380,
  "census_zones_count": 12,
  "avg_population_per_zone": 1250.0
}
```

### Get Census by Building Location
```http
POST /api/census/census_by_building
```
Request Body:
```json
{
  "building_geometry": {
    "type": "Polygon",
    "coordinates": [...]
  }
}
```

### Query Census Properties
```http
GET /api/census/query_census
```
Query Parameters:
- `comune` (string, optional): Filter by comune name
- `provincia` (string, optional): Filter by provincia
- `min_population` (int, optional): Minimum population
- `max_population` (int, optional): Maximum population
- `limit` (int): Maximum results
- `offset` (int): Pagination offset

## Raster Service Endpoints

### Calculate Building Height
```http
POST /api/raster/height
```
Request Body:
```json
{
  "building_geometry": {
    "type": "Polygon",
    "coordinates": [...]
  },
  "building_id": "building_001",
  "use_cache": true
}
```
Response:
```json
{
  "building_id": "building_001",
  "dtm_avg_height": 245.5,
  "dsm_avg_height": 258.3,
  "building_height": 12.8,
  "status": "calculated"
}
```

### Batch Height Calculation
```http
POST /api/raster/height_batch
```
Request Body:
```json
{
  "features": [
    {
      "properties": {"building_id": "001"},
      "geometry": {...}
    }
  ]
}
```

### Get Cached Height
```http
GET /api/raster/cached_height/{building_id}
```
Path Parameters:
- `building_id`: Building identifier

Query Parameters:
- `project_id` (string, optional)
- `scenario_id` (string, optional)

### Clip DTM Raster
```http
POST /api/raster/clip_dtm
```
Request Body:
```json
{
  "polygon": {
    "type": "Polygon",
    "coordinates": [...]
  }
}
```
Response: Base64 encoded raster data

### Clip DSM Raster
```http
POST /api/raster/clip_dsm
```
Request Body: Same as clip_dtm

### Get Elevation at Point
```http
GET /api/raster/elevation
```
Query Parameters:
- `lat` (float, required): Latitude
- `lon` (float, required): Longitude
- `raster_type` (string, default: "DTM"): DTM or DSM

### Get Raster Statistics
```http
POST /api/raster/statistics
```
Request Body:
```json
{
  "polygon": {...},
  "raster_type": "DTM"
}
```
Response:
```json
{
  "raster_type": "DTM",
  "min": 240.5,
  "max": 265.8,
  "mean": 252.3,
  "stddev": 5.2
}
```

### Fast Height Calculation
```http
POST /api/raster/height_fast
```
Request Body: Same as height_batch
Additional features: Prioritizes cache, optimized for performance

## Pipeline Service Endpoints

### Execute Pipeline
```http
POST /api/pipeline/execute
```
Request Body:
```json
{
  "project_id": "project_001",
  "scenario_id": "scenario_001",
  "building_id": "building_001",
  "features": ["building_height", "building_area", "building_volume"],
  "parallel": true,
  "input_data": {
    "building_geo": {...}
  }
}
```
Response:
```json
{
  "success": true,
  "requested_features": ["building_height", "building_area", "building_volume"],
  "executed_features": ["building_height", "building_area", "building_volume"],
  "failed_features": [],
  "execution_order": ["building_height", "building_area", "building_volume"],
  "results": {
    "building_height": 12.5,
    "building_area": 150.0,
    "building_volume": 1875.0
  }
}
```

### Execute Explicit Pipeline
```http
POST /api/pipeline/execute_explicit
```
Request Body:
```json
{
  "project_id": "project_001",
  "scenario_id": "scenario_001",
  "execution_plan": [
    {
      "feature_name": "building_height",
      "method_name": "calculate_from_raster_service"
    }
  ],
  "input_data": {...}
}
```

### Execute Predefined Pipeline
```http
POST /api/pipeline/execute_predefined
```
Request Body:
```json
{
  "project_id": "project_001",
  "scenario_id": "scenario_001",
  "pipeline_name": "milestone1_scenario",
  "input_data": {...}
}
```

### Calculate Single Feature
```http
POST /api/pipeline/calculate_feature
```
Request Body:
```json
{
  "project_id": "project_001",
  "scenario_id": "scenario_001",
  "feature_name": "building_height",
  "method_name": "calculate_from_raster_service",
  "input_data": {...}
}
```

### Get Configuration
```http
GET /api/pipeline/configuration
```
Response: Complete configuration JSON

### Get Available Features
```http
GET /api/pipeline/available_features
```
Response:
```json
{
  "features": [
    "building_height",
    "building_area",
    "building_volume",
    ...
  ],
  "services": {
    "census": "integrated",
    "raster": "integrated"
  }
}
```

### Get Predefined Pipelines
```http
GET /api/pipeline/predefined_pipelines
```
Response:
```json
{
  "pipelines": [
    {
      "name": "milestone1_scenario",
      "description": "Initialize scenario data",
      "features": ["scenario_geo", "building_geo"],
      "required_inputs": ["scenario_id"]
    }
  ]
}
```

### Get Feature Methods
```http
GET /api/pipeline/feature_methods/{feature_name}
```
Path Parameters:
- `feature_name`: Feature name

Response:
```json
{
  "feature": "building_height",
  "methods": [
    {
      "name": "calculate_from_raster_service",
      "priority": 1,
      "dependencies": ["building_geo", "raster_service"]
    }
  ]
}
```

## Health Check Endpoints

### Main Health Check
```http
GET /health
```
Response:
```json
{
  "status": "healthy",
  "services": {
    "vector": "operational",
    "pipeline": "operational",
    "census": "operational",
    "raster": "operational"
  }
}
```

### Service-Specific Health Checks
- Vector: `GET /api/vector/health`
- Census: `GET /api/census/health`
- Raster: `GET /api/raster/health`
- Pipeline: `GET /api/pipeline/health`

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

Common status codes:
- `200`: Success
- `400`: Bad Request
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

## Authentication

Currently, all endpoints are public. In production, add authentication:
- Bearer token authentication
- API key authentication
- OAuth2 support

## Rate Limiting

No rate limiting in development. Production recommendations:
- 100 requests/minute for general endpoints
- 10 requests/minute for heavy calculations
- Implement caching for frequently accessed data