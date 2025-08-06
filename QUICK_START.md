# Quick Start Guide - Docker PostGIS Setup

## 🚀 One-Command Setup

### Windows:
```bash
setup_docker_postgis.bat
```

### Linux/macOS:
```bash
chmod +x setup_docker_postgis.sh
./setup_docker_postgis.sh
```

## 📋 Manual Step-by-Step

### 1. Setup Docker PostGIS
```bash
# Build and start PostGIS
docker-compose build postgres
docker-compose up postgres -d

# Check status
docker-compose ps
```

### 2. Test Connection
```bash
# Test database connection
python scripts/test_docker_connection.py
```

### 3. Populate Sample Data
```bash
# Add sample census and raster data
python scripts/populate_sample_data.py
```

### 4. Start Application
```bash
# Create environment file
cp env.example .env

# Start the FastAPI application
python run.py
```

### 5. Test Everything
```bash
# Test the simplified API
python examples/simple_api_usage.py

# Access API documentation
# http://localhost:8000/docs
```

## 🔧 Database Configuration

The application automatically connects to:
- **Host**: localhost:5432
- **Database**: cim_wizard_integrated
- **User**: cim_wizard_user
- **Password**: cim_wizard_password

## 📊 What Gets Created

### Docker Services:
- **PostgreSQL/PostGIS**: Database with spatial extensions
- **pgAdmin**: Database management interface
- **Application**: CIM Wizard Integrated API

### Database Schemas:
- **cim_vector**: Buildings, projects, grid data
- **cim_census**: Census zones and demographics  
- **cim_raster**: DTM/DSM elevation data

### Sample Data:
- 6 census zones (Florence area)
- 3 buildings with properties
- DTM and DSM raster samples
- 1 project scenario

## 🌐 Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| API | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| pgAdmin | http://localhost:5050 | admin@cimwizard.com / admin |
| Database | localhost:5432 | cim_wizard_user / cim_wizard_password |

## 🧪 Quick Tests

```bash
# Test census API
curl -X POST "http://localhost:8000/api/census/census_spatial" \
  -H "Content-Type: application/json" \
  -d '[[11.2, 43.7], [11.3, 43.7], [11.3, 43.8], [11.2, 43.8], [11.2, 43.7]]'

# Test raster API
curl -X POST "http://localhost:8000/api/raster/height" \
  -H "Content-Type: application/json" \
  -d '{"type": "Polygon", "coordinates": [[[11.25, 43.75], [11.26, 43.75], [11.26, 43.76], [11.25, 43.76], [11.25, 43.75]]]}'

# Test pipeline API
curl -X POST "http://localhost:8000/api/pipeline/execute" \
  -H "Content-Type: application/json" \
  -d '{"project_id": "sample_florence_project", "scenario_id": "scenario_001", "features": ["building_height"]}'
```

## 🔄 Common Commands

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs postgres

# Restart containers
docker-compose restart

# Stop everything
docker-compose down

# Rebuild containers
docker-compose down
docker-compose build
docker-compose up -d
```

## 🐛 Troubleshooting

### Container won't start:
```bash
docker-compose logs postgres
```

### Connection refused:
```bash
# Check if port is available
netstat -an | findstr 5432  # Windows
netstat -an | grep 5432     # Linux/macOS

# Restart Docker service
```

### Database empty:
```bash
# Re-populate sample data
python scripts/populate_sample_data.py
```

### Application errors:
```bash
# Check Python environment
python -c "import psycopg2; print('✅ psycopg2 available')"
python -c "from app.db.database import engine; print('✅ Database imports work')"
```

## 📚 Next Steps

1. **Load Real Data**: See [DOCKER_SETUP_GUIDE.md](DOCKER_SETUP_GUIDE.md) for census/raster data loading
2. **Customize**: Modify `docker/postgis/init-scripts/` for your data
3. **Deploy**: Use the same Docker setup for production
4. **Monitor**: Access pgAdmin for database management

🎉 **You're ready to use CIM Wizard Integrated with Docker PostGIS!**