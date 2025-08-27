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

## Architecture Overview

### Database Schemas
- **`cim_vector`**: Buildings, projects, grid infrastructure
- **`cim_census`**: Census zones and demographic data
- **`cim_raster`**: DTM/DSM data and height calculations

### Core Components
- **Pipeline Executor**: Orchestrates feature calculations
- **Data Manager**: Manages context and configuration  
- **Calculators**: Individual feature calculation methods
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
```bash
# Build and run
docker-compose up --build

# Check status
docker-compose ps
```

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

docker-compose -f docker-compose.db.yml up -d



export DATABASE_URL="postgresql://cim_wizard_user:cim_wizard_password@localhost:5433/cim_wizard_integrated"
export POSTGRES_HOST="localhost"
export POSTGRES_PORT="5433"
export POSTGRES_DB="cim_wizard_integrated"
export POSTGRES_USER="cim_wizard_user"
export POSTGRES_PASSWORD="cim_wizard_password"

# Then run uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
run fast api
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

# Start the application
./start_app.sh dev

Method3:
# Override settings for a single run
DATABASE_URL="postgresql://user:pass@host:port/db" PORT=9000 ./start_app.sh dev

