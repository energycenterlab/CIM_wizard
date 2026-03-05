# CIM Wizard Integrated

CIM Wizard Integrated is a comprehensive FastAPI service that combines vector data management, census data, raster processing, and pipeline execution with direct database access. This is version 2.0 that integrates all services with direct database connections instead of API calls.

## Key Features

- **Simplified API**: No Pydantic validation - uses simple dictionaries for maximum clarity
- **Direct Database Access**: Services communicate directly via database instead of API calls
- **Multi-Schema Design**: Organized data using `cim_vector`, `cim_census`, and `cim_raster` schemas
- **Object-Oriented Architecture**: Preserved from datalake8 (pipeline executor, data manager, calculators)
- **Integrated Services**: Vector, census, and raster data in one unified API

## Database Setup

### Prerequisites
- PostgreSQL 12+ with PostGIS 3.0+
- Python 3.8+
- All dependencies from `requirements.txt`

### Database Installation

1. **Create Database and Extensions**:
   ```bash
   # Connect as postgres superuser
   psql -U postgres
   
   # Create database
   CREATE DATABASE cim_wizard_integrated;
   \c cim_wizard_integrated;
   
   # Run initialization script
   \i init_db.sql
   ```

2. **Verify Setup**:
   ```sql
   -- Check schemas
   SELECT schema_name FROM information_schema.schemata 
   WHERE schema_name IN ('cim_vector', 'cim_census', 'cim_raster');
   
   -- Check extensions
   SELECT name, installed_version FROM pg_available_extensions 
   WHERE name LIKE 'postgis%' AND installed_version IS NOT NULL;
   ```

For detailed database setup instructions, see [DATABASE_SETUP.md](DATABASE_SETUP.md).

## Installation

### Using Conda (Recommended)
```bash
# Create environment
conda env create -f environment.yml
conda activate cim_wizard

# Set up database (see Database Setup above)

# Configure environment
cp env.example .env
# Edit .env with your database settings

# Run application
python run.py
```

### Using pip
```bash
# Install dependencies
pip install -r requirements.txt

# Set up database and environment as above

# Run application
python run.py
```

## API Usage (Simplified)

The API uses simple dictionaries instead of complex validation schemas for maximum clarity:

### Example 1: Pipeline Execution
```python
import requests
import json

# Simple pipeline request - just a dictionary
request_data = {
    "project_id": "test_project_001",
    "scenario_id": "scenario_001", 
    "features": ["building_height", "building_area"],
    "parallel": False
}

response = requests.post(
    "http://localhost:8000/api/pipeline/execute",
    json=request_data
)

print(response.json())
```

### Example 2: Building Height Calculation
```python
# Calculate building height from raster data
building_geometry = {
    "type": "Polygon",
    "coordinates": [[
        [11.25, 43.75], [11.26, 43.75], 
        [11.26, 43.76], [11.25, 43.76], 
        [11.25, 43.75]
    ]]
}

response = requests.post(
    "http://localhost:8000/api/raster/height",
    json=building_geometry
)

print(f"Building height: {response.json()['height']}m")
```

### Example 3: Census Data Query
```python
# Get census data for a polygon area
polygon_coords = [
    [11.2, 43.7], [11.3, 43.7],
    [11.3, 43.8], [11.2, 43.8], 
    [11.2, 43.7]
]

response = requests.post(
    "http://localhost:8000/api/census/census_spatial",
    json=polygon_coords
)

census_zones = response.json()
print(f"Found {len(census_zones['features'])} census zones")
```

## API Endpoints

### Vector Data (`/api/vector`)
- `GET /projects` - List all projects
- `GET /dashboard` - Project dashboard
- `GET /pscenarios/{project_id}` - Get project scenarios
- `GET /bgeo/{building_id}` - Get building geometry
- `GET /get_buildings_geojson/{project_id}/{scenario_id}` - Buildings as GeoJSON

### Pipeline Execution (`/api/pipeline`)
- `POST /execute` - Execute feature pipeline
- `POST /execute_explicit` - Execute with explicit method calls
- `POST /execute_predefined` - Execute predefined pipeline
- `POST /calculate_feature` - Calculate single feature
- `GET /available_features` - List available features
- `GET /configuration` - Get pipeline configuration

### Census Data (`/api/census`)
- `POST /census_spatial` - Spatial census query
- `GET /census/{census_id}` - Get census by ID
- `GET /building_age_distribution` - Building age statistics
- `GET /population_statistics` - Population statistics

### Raster Data (`/api/raster`)
- `POST /height` - Calculate building height
- `POST /height_batch` - Batch height calculation  
- `POST /clip` - Clip raster by geometry
- `GET /statistics` - Raster statistics

### CIM Wizard Views (`/api/cim-wizard`)
- `POST /calculate` - Calculate a single feature (body includes feature_name)
- `GET /calculate?feature_name=<n>` - Calculate a single feature (query param)
- `POST /chainable` - Execute chain of calculators separated by `|`
- `POST /priority-override` - Set runtime priority override for a feature
- `GET /list` - List all available features, pipelines, and endpoints

## Architecture Overview

### Database Schemas
- **`cim_vector`**: Buildings, projects, grid infrastructure
- **`cim_census`**: Census zones and demographic data
- **`cim_raster`**: DTM/DSM data and height calculations

### Core OOP Design

The system is built around three core classes and a `BaseCalculator` hierarchy:

```
BaseCalculator                  (app/calculators/base_calculator.py)
  |-- ScenarioGeoCalculator
  |-- ScenarioCensusBoundaryCalculator
  |-- BuildingGeoCalculator
  |-- BuildingPropsCalculator
  |-- BuildingHeightCalculator
  |-- BuildingAreaCalculator
  |-- BuildingVolumeCalculator
  |-- BuildingNFloorsCalculator
  |-- BuildingResidentialFilterCalculator
  |-- CensusPopulationCalculator
  |-- BuildingPopulationCalculator
  |-- BuildingTypeCalculator
  |-- BuildingConstructionYearCalculator
  |-- BuildingNFamiliesCalculator
  |-- BuildingDemographicCalculator
  |-- BuildingGeoLod12Calculator
  |-- EnvelopeEfficiencyCalculator
  |-- FmuAssignCalculator

CimWizardDataManager            (app/core/data_manager.py)
CimWizardPipelineExecutor       (app/core/pipeline_executor.py)
```

**BaseCalculator** -- Every calculator inherits from `BaseCalculator`, which
provides pipeline/data-manager references, convenience wrappers for logging,
validation, feature access, and properties for `db_session`, `project_id`,
and `scenario_id`.  Subclasses only call `super().__init__(pipeline_executor)`
and implement domain-specific methods.

**CimWizardDataManager** -- Central context object for a pipeline run.
Stores calculated features, project/scenario identifiers, DB session,
`configuration.json`, and `FeatureProxy` objects that enable fluent chaining
(`dm.building_height.calculate_from_raster_tiles`).

**CimWizardPipelineExecutor** -- Orchestrates calculator execution.
Dynamically loads calculator classes from `configuration.json`, resolves
dependency order via topological sort, and selects methods through a
priority-based fallback mechanism (lowest priority number runs first; runtime
overrides are supported).

### How Calculators Work

1. The pipeline executor instantiates a calculator via its `class_path` and
   `class_name` from `configuration.json`.
2. Each calculator receives the executor in its constructor and gains access
   to the data manager and all convenience methods through `BaseCalculator`.
3. A calculation method reads its inputs via `self.get_feature(...)`,
   performs computation, and stores results with `self.set_feature(...)`.
4. The executor tries methods in priority order; the first one whose
   dependencies are satisfied and returns a non-None value wins.

### Configuration-Driven Development

`configuration.json` is the single coordinator between calculators, database
columns, the field normalizer, and the data manager.  There are no separate
codegen or migration scripts to run.  The developer workflow is:

1. **Stop** the backend.
2. **Add** a calculator file under `app/calculators/` (inherit from
   `BaseCalculator`).
3. **Edit** `app/core/configuration.json` -- register the feature, its
   methods, and optionally its `output` column mapping.
4. Optionally add or update a route under `app/api/`.
5. **Start** the backend.  On startup the application automatically:
   - Creates any missing DB columns declared in `output` sections.
   - Extends `normalization_config.json` with fields for new columns.
   - Builds dynamic feature proxies and `_data` attributes in the data
     manager -- no hardcoded list to maintain.

#### Adding a New Calculator (step by step)

**a) Create the calculator file** `app/calculators/solar_potential_calculator.py`:

```python
from app.calculators.base_calculator import BaseCalculator

class SolarPotentialCalculator(BaseCalculator):
    def __init__(self, pipeline_executor):
        super().__init__(pipeline_executor)

    def estimate_from_area(self):
        area = self.get_feature("building_area")
        if area is None:
            self.log_error("building_area not available")
            return None
        result = area * 0.15  # simplified
        self.set_feature("solar_potential", result)
        self.log_success("estimate_from_area", result, "kWp")
        return result
```

**b) Register in `configuration.json`:**

```json
"solar_potential": {
  "constraints": {"datatype": "float", "value_range": [0, 100000]},
  "class_path": "app.calculators.solar_potential_calculator",
  "class_name": "SolarPotentialCalculator",
  "output": [
    {
      "table": "cim_wizard_building_properties",
      "schema": "cim_vector",
      "column": "solar_potential_kwp",
      "type": "Float"
    }
  ],
  "methods": [
    {
      "priority": 1,
      "input_dependencies": ["building_area"],
      "method_name": "estimate_from_area"
    }
  ]
}
```

**c) Restart the backend.**  The startup sync will:
- Run `ALTER TABLE cim_vector.cim_wizard_building_properties ADD COLUMN "solar_potential_kwp" DOUBLE PRECISION` if the column does not yet exist.
- Add a `solar_potential_kwp` entry in `normalization_config.json`.
- Create `data_manager.solar_potential` (FeatureProxy) and
  `data_manager.solar_potential_data` automatically.

No manual migration or model editing required.

#### Alembic (for tracked migrations)

Alembic is configured for cases where you need a reviewable migration
history (column renames, type changes, data backfills):

```bash
# Generate a migration from model changes
alembic revision --autogenerate -m "describe change"

# Apply pending migrations
alembic upgrade head
```

For simple column additions driven by `configuration.json`, the startup
sync handles it and Alembic is not required.

### CIM Wizard Views Endpoint

The unified views module (`app/api/cim_wizard_views.py`) exposes four
endpoints under `/api/v1/cim-wizard`:

| Endpoint | Method | Purpose |
|---|---|---|
| `/calculate` | POST, GET | Single feature calculation |
| `/chainable` | POST | Chain of calculators separated by `\|` |
| `/priority-override` | POST | Runtime method priority override |
| `/list` | GET | List features, pipelines, and endpoints |

Chain format example:
`scenario_geo.calculate_from_scenario_geo|building_height.calculate_from_raster_tiles`

### Core Components (Summary)
- **Pipeline Executor**: Orchestrates feature calculations with fallback
- **Data Manager**: Manages context, configuration, and dynamic feature proxies
- **BaseCalculator**: Parent class for all calculators
- **Calculators**: Individual feature calculation implementations
- **Config Sync** (`app/core/config_sync.py`): Startup hook that syncs DB columns and normalizer from `configuration.json`
- **Normalizer** (`app/core/normalizer.py`): Field-name aliasing and validation, auto-extended at startup
- **Services**: Direct database access layers (census, raster, vector)

### FastAPI vs Django MVT
This FastAPI implementation provides:
- **Async Support**: Better performance for I/O operations
- **Direct Database Access**: No API overhead between services
- **Simplified Requests**: Dict-based API for clarity
- **Auto Documentation**: Interactive API docs at `/docs`

See [docs/fastapi_vs_mvt.md](docs/fastapi_vs_mvt.md) for detailed comparison.

## Development

### Testing
```bash
# Run API tests
python examples/simple_api_usage.py

# Check health
curl http://localhost:8000/health
```

### Docker Deployment

**Full stack** (DB + backend; requires `../cim-database/init-db/init_backup.sql`):
```bash
docker compose up -d --build

# Check status
docker compose ps

# Logs
docker compose logs -f backend
```

**Backend only** (when DB is already running on localhost:15432):
```bash
docker compose -f docker-compose.backend-only.yml up -d --build
```

API docs: http://localhost:8000/docs

## Documentation

- [Architecture Overview](docs/architecture_overview.md)
- [FastAPI vs MVT Comparison](docs/fastapi_vs_mvt.md)
- [OOP Approach](docs/oop_approach.md)
- [Calculator Methods](docs/calculator_methods.md)
- [Service Endpoints](docs/service_endpoints.md)
- [Database Setup Guide](DATABASE_SETUP.md)

## Error Handling

The simplified API includes error comments in the code instead of complex validation:

```python
# Possible errors to handle later:
# - Missing project_id, scenario_id, features
# - Invalid feature names  
# - Database connection issues
# - Calculator execution failures

if not project_id:
    return {"error": "Missing project_id"}
```

This approach prioritizes **clarity and simplicity** over robustness, making the code easy to understand and extend.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes (following the clarity-first principle)
4. Add error comments for potential issues
5. Submit a pull request

## License

MIT





install environment:
pip install -r requirements.txt
conda activate webgis

sudo docker-compose -f docker-compose.db.yml up -d

docker compose -f docker-compose.db.yml down


export DATABASE_URL="postgresql://cim_wizard_user:cim_wizard_password@localhost:5433/cim_wizard_integrated"

export POSTGRES_HOST="localhost"
export POSTGRES_PORT="5433"
export POSTGRES_DB="cim_wizard_integrated"
export POSTGRES_USER="cim_wizard_user"
export POSTGRES_PASSWORD="cim_wizard_password"

# Then run uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000





DATABASE_URL=postgresql://cim_wizard_user:cim_wizard_password@localhost:5433/cim_wizard_integrated uvicorn main:app --host 0.0.0.0 --port 8000




method1:
# Copy the development environment
cp env.development .env

# Start the application
./start_app.sh dev

method2:
# Set environment variables
export DATABASE_URL="postgresql://user:pass@host:port/db"
export DEBUG=True
export PORT=9000



Method3:
# Override settings for a single run
DATABASE_URL="postgresql://user:pass@host:port/db" PORT=9000 ./start_app.sh dev

for closing the dockerized database session
sudo docker compose -f docker-compose.db.yml down


# Basic shutdown (stops and removes containers)
docker compose -f docker-compose.db.yml down

# Remove volumes as well (⚠️ This will delete your database data!)
docker compose -f docker-compose.db.yml down -v

# Remove images as well
docker compose -f docker-compose.db.yml down --rmi all

# Force remove (doesn't wait for graceful shutdown)
docker compose -f docker-compose.db.yml down --timeout 0

# Remove orphaned containers
docker compose -f docker-compose.db.yml down --remove-orphans