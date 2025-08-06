# CIM Wizard Integrated

CIM Wizard Integrated is a comprehensive FastAPI service that combines vector data management, census data, raster processing, and pipeline execution with direct database access. This is version 2.0 that integrates all services with direct database connections instead of API calls.

## Quick Start

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up PostgreSQL with PostGIS:
   ```bash
   createdb cim_wizard_integrated
   psql -d cim_wizard_integrated -c "CREATE EXTENSION postgis;"
   psql -d cim_wizard_integrated -c "CREATE EXTENSION postgis_raster;"
   ```

4. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your database settings
   ```

5. Run the application:
   ```bash
   python run.py
   ```

### Simple Example

```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

# Example 1: Calculate building height using integrated raster service
building_geometry = {
    "type": "Polygon",
    "coordinates": [[
        [11.5734, 48.1371],
        [11.5736, 48.1371],
        [11.5736, 48.1373],
        [11.5734, 48.1373],
        [11.5734, 48.1371]
    ]]
}

response = requests.post(
    f"{BASE_URL}/api/raster/height",
    json={
        "building_geometry": building_geometry,
        "building_id": "building_001",
        "use_cache": True
    }
)

height_data = response.json()
print(f"Building height: {height_data['building_height']}m")

# Example 2: Get census data for an area
polygon = [[11.57, 48.13], [11.58, 48.13], [11.58, 48.14], [11.57, 48.14], [11.57, 48.13]]

response = requests.post(
    f"{BASE_URL}/api/census/census_spatial",
    json={"polygon_array": polygon}
)

census_data = response.json()
print(f"Found {len(census_data['features'])} census zones")

# Example 3: Execute a pipeline for building features
response = requests.post(
    f"{BASE_URL}/api/pipeline/execute",
    json={
        "project_id": "project_001",
        "scenario_id": "scenario_001",
        "features": ["building_height", "building_area", "building_volume"],
        "parallel": True,
        "input_data": {
            "building_geo": building_geometry
        }
    }
)

pipeline_result = response.json()
print(f"Calculated features: {pipeline_result['executed_features']}")
```

## API Documentation

Access the interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Schemas

The system uses three PostgreSQL schemas:
- `cim_vector`: Vector data (buildings, projects, scenarios)
- `cim_census`: Census geographical data
- `cim_raster`: Raster data (DTM, DSM)

## Services

### Vector Service (`/api/vector`)
- Project and scenario management
- Building geometry operations
- Grid network data

### Census Service (`/api/census`)
- Census zone queries
- Population statistics
- Building age distribution

### Raster Service (`/api/raster`)
- Building height calculation
- Raster clipping
- Elevation queries

### Pipeline Service (`/api/pipeline`)
- Feature calculation pipelines
- Predefined workflows
- Method chaining

## Documentation

See the `/docs` folder for detailed documentation:
- Architecture overview
- API endpoints reference
- OOP design patterns
- Calculator methods logic

## Testing

Run the test suite:
```bash
python test_api.py
```

## Development

For development guidelines, see `docs/development.md`