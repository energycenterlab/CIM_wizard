# CIM Wizard Integrated

CIM Wizard Integrated is a comprehensive FastAPI service that combines vector data management, census data, raster processing, and pipeline execution with direct database access. This is version 2.0 that integrates all services with direct database connections instead of API calls.

## 🚀 Key Features

- **Simplified API**: No Pydantic validation - uses simple dictionaries for maximum clarity
- **Direct Database Access**: Services communicate directly via database instead of API calls
- **Multi-Schema Design**: Organized data using `cim_vector`, `cim_census`, and `cim_raster` schemas
- **Object-Oriented Architecture**: Preserved from datalake8 (pipeline executor, data manager, calculators)
- **Integrated Services**: Vector, census, and raster data in one unified API
- **Docker Support**: Portable PostGIS database with pgAdmin interface
- **Raw Data Integration**: Support for GPKG, GeoTIFF, and other spatial data formats

## 🐳 Docker Setup (Recommended)

### Quick Start with Docker

1. **Clone and Start Database**:
   ```bash
   git clone <repository-url>
   cd cim_wizard_integrated
   
   # Start PostGIS database with pgAdmin
   docker-compose -f docker-compose.db.yml up -d
   ```

2. **Access Services**:
   - **Database**: `localhost:5433`
     - Database: `cim_wizard_integrated`
     - User: `cim_wizard_user`
     - Password: `cim_wizard_password`
   - **pgAdmin**: `http://localhost:5050`
     - Email: `admin@cimwizard.com`
     - Password: `admin`

3. **Set Environment Variables**:
   ```bash
   export DATABASE_URL="postgresql://cim_wizard_user:cim_wizard_password@localhost:5433/cim_wizard_integrated"
   export POSTGRES_HOST="localhost"
   export POSTGRES_PORT="5433"
   export POSTGRES_DB="cim_wizard_integrated"
   export POSTGRES_USER="cim_wizard_user"
   export POSTGRES_PASSWORD="cim_wizard_password"
   ```

4. **Install Python Dependencies**:
   ```bash
   # Using conda (recommended)
   conda env create -f environment.yml
   conda activate cim_wizard
   
   # Or using pip
   pip install -r requirements.txt
   ```

5. **Run Application**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker Configuration

The `docker-compose.db.yml` provides:
- **PostGIS 15-3.4**: Latest stable PostGIS with all extensions
- **Portable Data**: Persistent data in `./cim_db` folder
- **pgAdmin**: Web-based database management
- **Raw Data Mount**: Access to `./rawdata` folder for spatial files
- **Init Scripts**: Automatic database initialization from `./initdb` folder

### Database Initialization

The database automatically initializes with:
- PostGIS extensions (postgis, postgis_raster, postgis_topology, pgrouting)
- Custom schemas (cim_vector, cim_census, cim_raster)
- User permissions and search paths
- Sample data (if provided in initdb folder)

## 📊 Database Schema

### Schemas
- **`cim_vector`**: Buildings, projects, scenarios, and vector data
- **`cim_census`**: Census zones and demographic data
- **`cim_raster`**: DTM/DSM data and height calculations

### Key Tables
- **`cim_wizard_building`**: Building geometries and metadata
- **`cim_wizard_building_properties`**: Calculated building properties
- **`data_gateway_censusgeo`**: Census zone geometries and statistics
- **`dtm_raster`** / **`dsm_raster`**: Digital terrain/surface models

## 🔧 Manual Database Setup (Alternative)

If you prefer to set up PostgreSQL manually:

1. **Install PostgreSQL with PostGIS**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql-15 postgresql-15-postgis-3
   
   # macOS with Homebrew
   brew install postgresql postgis
   ```

2. **Create Database**:
   ```sql
   CREATE DATABASE cim_wizard_integrated;
   \c cim_wizard_integrated;
   
   -- Enable extensions
   CREATE EXTENSION postgis;
   CREATE EXTENSION postgis_raster;
   CREATE EXTENSION postgis_topology;
   CREATE EXTENSION pgrouting;
   CREATE EXTENSION "uuid-ossp";
   ```

3. **Run Schema Scripts**:
   ```bash
   # Create tables from schema files
   psql -U postgres -d cim_wizard_integrated -f vec_bld_schema.sql
   psql -U postgres -d cim_wizard_integrated -f vec_props_schema.sql
   psql -U postgres -d cim_wizard_integrated -f census_schema.sql
   psql -U postgres -d cim_wizard_integrated -f dtm_schema.sql
   psql -U postgres -d cim_wizard_integrated -f dsm_schema.sql
   ```

## 🚀 API Usage

### Example 1: Pipeline Execution
```python
import requests

# Execute building analysis pipeline
request_data = {
    "project_id": "test_project_001",
    "scenario_id": "scenario_001", 
    "features": ["building_height", "building_area", "building_volume"],
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

## 📡 API Endpoints

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

### Building Analysis (`/api/building`)
- `POST /analyze` - Complete building analysis
- `GET /features` - Available analysis features

## 🏗️ Architecture

### Core Components
- **Pipeline Executor**: Orchestrates feature calculations
- **Data Manager**: Manages context and configuration  
- **Calculators**: Individual feature calculation methods
- **Services**: Direct database access layers (census, raster, vector)

### Database Design
- **Multi-Schema**: Organized by data type (vector, census, raster)
- **Direct Access**: Services bypass API overhead
- **Spatial Indexing**: Optimized for geometric queries
- **Extensible**: Easy to add new features and data types

## 🔄 Development Workflow

### Environment Setup
```bash
# 1. Start database
docker-compose -f docker-compose.db.yml up -d

# 2. Set environment variables
export DATABASE_URL="postgresql://cim_wizard_user:cim_wizard_password@localhost:5433/cim_wizard_integrated"

# 3. Install dependencies
conda env create -f environment.yml
conda activate cim_wizard

# 4. Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Check API health
curl http://localhost:8000/health

# Test database connection
curl http://localhost:8000/api/vector/projects

# Run example scripts
python examples/simple_api_usage.py
```

### Database Management
```bash
# Access database via psql
docker exec -it integrateddb psql -U cim_wizard_user -d cim_wizard_integrated

# Access via pgAdmin
# Open http://localhost:5050
# Login: admin@cimwizard.com / admin
# Add server: integrateddb:5432
```

## 📁 Project Structure

```
cim_wizard_integrated/
├── app/                          # FastAPI application
│   ├── api/                      # API routes
│   ├── calculators/              # Feature calculation methods
│   ├── core/                     # Core components (pipeline, data manager)
│   ├── db/                       # Database connection
│   ├── models/                   # Data models
│   └── services/                 # Service layers
├── initdb/                       # Database initialization scripts
├── rawdata/                      # Raw spatial data files
├── cim_db/                       # Persistent database data (Docker)
├── docker-compose.db.yml         # Database Docker configuration
├── main.py                       # FastAPI application entry point
├── requirements.txt              # Python dependencies
└── environment.yml               # Conda environment
```

## 🚀 Deployment

### Production Deployment
```bash
# 1. Set production environment variables
export DATABASE_URL="postgresql://user:pass@prod-host:5432/cim_wizard_integrated"
export DEBUG=False

# 2. Run with production server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Production
```bash
# Build production image
docker build -t cim-wizard-integrated .

# Run with production database
docker-compose -f docker-compose.prod.yml up -d
```

## 📚 Documentation

- [Architecture Overview](docs/architecture_overview.md)
- [FastAPI vs MVT Comparison](docs/fastapi_vs_mvt.md)
- [OOP Approach](docs/oop_approach.md)
- [Calculator Methods](docs/calculator_methods.md)
- [Service Endpoints](docs/service_endpoints.md)
- [Adding New Calculators](docs/adding_new_calculator.md)

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Failed**:
   ```bash
   # Check if database is running
   docker-compose -f docker-compose.db.yml ps
   
   # Check database logs
   docker logs integrateddb
   ```

2. **Port Already in Use**:
   ```bash
   # Change ports in docker-compose.db.yml
   ports:
     - "5434:5432"  # Change from 5433 to 5434
   ```

3. **Permission Issues**:
   ```bash
   # Fix cim_db folder permissions
   sudo chown -R $USER:$USER cim_db/
   ```

### Database Reset
```bash
# Stop and remove containers
docker-compose -f docker-compose.db.yml down

# Remove data (⚠️ This deletes all data!)
rm -rf cim_db/

# Start fresh
docker-compose -f docker-compose.db.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following the clarity-first principle
4. Add error comments for potential issues
5. Test with Docker setup
6. Submit a pull request

## 📄 License

MIT

---

## 🎯 Quick Commands Reference

```bash
# Start everything
docker-compose -f docker-compose.db.yml up -d
uvicorn main:app --reload

# Stop database
docker-compose -f docker-compose.db.yml down

# Reset database (⚠️ deletes data)
docker-compose -f docker-compose.db.yml down -v

# Access database
docker exec -it integrateddb psql -U cim_wizard_user -d cim_wizard_integrated

# Access pgAdmin
# http://localhost:5050 (admin@cimwizard.com / admin)
```