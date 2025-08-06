# Docker PostGIS Setup Guide for CIM Wizard Integrated

This guide walks you through setting up PostgreSQL with PostGIS in Docker and populating the `cim_census` and `cim_raster` schemas.

## 🐳 Step 1: Docker PostGIS Setup

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB of available RAM
- 10GB of free disk space

### Start the Services

1. **Navigate to project directory**:
   ```bash
   cd cim_wizard_integrated
   ```

2. **Build and start PostGIS container**:
   ```bash
   # Build the custom PostGIS image
   docker-compose build postgres
   
   # Start PostGIS service
   docker-compose up postgres -d
   
   # Check container status
   docker-compose ps
   ```

3. **Verify PostGIS is ready**:
   ```bash
   # Check container logs
   docker-compose logs postgres
   
   # Test connection
   docker exec -it cim_integrated_db psql -U cim_wizard_user -d cim_wizard_integrated -c "SELECT version();"
   ```

### Expected Output
You should see:
- Container status: `Up (healthy)`
- PostGIS extensions installed
- Schemas created: `cim_vector`, `cim_census`, `cim_raster`

## 🗄️ Step 2: Verify Database Setup

### Connect to Database
```bash
# Using docker exec
docker exec -it cim_integrated_db psql -U cim_wizard_user -d cim_wizard_integrated

# Or using local psql (if installed)
psql -h localhost -p 5432 -U cim_wizard_user -d cim_wizard_integrated
```

### Verify Schemas and Extensions
```sql
-- Check schemas
SELECT schema_name FROM information_schema.schemata 
WHERE schema_name IN ('cim_vector', 'cim_census', 'cim_raster');

-- Check PostGIS extensions
SELECT name, installed_version FROM pg_available_extensions 
WHERE name IN ('postgis', 'postgis_raster', 'postgis_topology') 
AND installed_version IS NOT NULL;

-- Check sample data
SELECT 'Vector: ' || COUNT(*) || ' projects' FROM cim_vector.project_scenario;
SELECT 'Census: ' || COUNT(*) || ' zones' FROM cim_census.census_geo;
SELECT 'Raster: ' || COUNT(*) || ' rasters' FROM cim_raster.dtm_raster;
```

## 📊 Step 3: Populate Census Data (cim_census)

### Prepare Census Data Files

You'll need Italian census data. Common sources:
- ISTAT (Italian National Statistics Institute)
- OpenStreetMap census boundaries
- Regional government data portals

### Census Data Format
Expected format for `cim_census.census_geo` table:
```sql
-- Required columns:
SEZ2011 BIGINT         -- Census section ID
geometry MULTIPOLYGON  -- Census zone boundaries
REGIONE VARCHAR        -- Region name
PROVINCIA VARCHAR      -- Province name  
COMUNE VARCHAR         -- Municipality name
P1 INTEGER            -- Total population
-- ... additional demographic columns (P2-P140, ST1-ST15, A2-A48, etc.)
```

### Option 1: Load from Shapefile
```bash
# Install GDAL tools (if not installed)
# Ubuntu/Debian: apt-get install gdal-bin
# macOS: brew install gdal
# Windows: Download from OSGeo4W

# Convert shapefile to SQL
shp2pgsql -I -s 4326 -W UTF-8 /path/to/census_data.shp cim_census.census_geo > census_import.sql

# Import to Docker PostGIS
docker exec -i cim_integrated_db psql -U cim_wizard_user -d cim_wizard_integrated < census_import.sql
```

### Option 2: Load from CSV with geometries
```sql
-- Create temporary table
CREATE TEMP TABLE census_temp (
    sez2011 TEXT,
    geom_wkt TEXT,
    regione TEXT,
    provincia TEXT,
    comune TEXT,
    popolazione INTEGER
);

-- Load CSV data
COPY census_temp FROM '/path/to/census_data.csv' WITH CSV HEADER;

-- Insert into main table with geometry conversion
INSERT INTO cim_census.census_geo (SEZ2011, geometry, REGIONE, PROVINCIA, COMUNE, P1)
SELECT 
    sez2011::BIGINT,
    ST_GeomFromText(geom_wkt, 4326)::geometry(MULTIPOLYGON, 4326),
    regione,
    provincia,
    comune,
    popolazione
FROM census_temp;
```

### Option 3: Load Sample Florence Data
```sql
-- Insert sample data for Florence area (for testing)
INSERT INTO cim_census.census_geo (
    SEZ2011, geometry, REGIONE, PROVINCIA, COMUNE, P1, P2, P3
) VALUES 
    (480001001001, ST_GeomFromText('MULTIPOLYGON(((11.2 43.7, 11.25 43.7, 11.25 43.75, 11.2 43.75, 11.2 43.7)))', 4326), 'Toscana', 'Firenze', 'Firenze', 1500, 750, 750),
    (480001001002, ST_GeomFromText('MULTIPOLYGON(((11.25 43.7, 11.3 43.7, 11.3 43.75, 11.25 43.75, 11.25 43.7)))', 4326), 'Toscana', 'Firenze', 'Firenze', 1200, 600, 600),
    (480001001003, ST_GeomFromText('MULTIPOLYGON(((11.2 43.75, 11.25 43.75, 11.25 43.8, 11.2 43.8, 11.2 43.75)))', 4326), 'Toscana', 'Firenze', 'Firenze', 800, 400, 400);

-- Verify insertion
SELECT COUNT(*), AVG(P1) as avg_population FROM cim_census.census_geo;
```

## 🗺️ Step 4: Populate Raster Data (cim_raster)

### Prepare Raster Data Files

You'll need:
- **DTM (Digital Terrain Model)**: Ground elevation
- **DSM (Digital Surface Model)**: Surface elevation (including buildings)

Common formats: GeoTIFF (.tif), ASCII Grid (.asc)

### Raster Data Sources
- EU-DEM (European Digital Elevation Model)
- Copernicus Land Monitoring Service
- Regional/national mapping agencies
- LiDAR datasets

### Option 1: Load using raster2pgsql (Recommended)
```bash
# Install PostGIS raster tools (if not in Docker)
# They're included in our Docker image

# Import DTM raster
raster2pgsql -I -C -e -Y -f rast -s 4326 -t 100x100 /path/to/dtm_data.tif cim_raster.dtm_raster | \
    docker exec -i cim_integrated_db psql -U cim_wizard_user -d cim_wizard_integrated

# Import DSM raster  
raster2pgsql -I -C -e -Y -f rast -s 4326 -t 100x100 /path/to/dsm_data.tif cim_raster.dsm_raster | \
    docker exec -i cim_integrated_db psql -U cim_wizard_user -d cim_wizard_integrated

# Verify import
docker exec -it cim_integrated_db psql -U cim_wizard_user -d cim_wizard_integrated \
    -c "SELECT filename, ST_Width(rast), ST_Height(rast) FROM cim_raster.dtm_raster LIMIT 5;"
```

### Option 2: Load Binary Raster Data
```python
# Python script to load raster data
import psycopg2
import rasterio
import numpy as np

# Connect to Docker PostGIS
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="cim_wizard_integrated", 
    user="cim_wizard_user",
    password="cim_wizard_password"
)
cur = conn.cursor()

# Load raster file
with rasterio.open('/path/to/dtm_data.tif') as src:
    raster_data = src.read(1)  # Read first band
    transform = src.transform
    
    # Convert to binary
    raster_bytes = raster_data.tobytes()
    
    # Insert to database
    cur.execute("""
        INSERT INTO cim_raster.dtm_raster 
        (filename, rast, srid, min_elevation, max_elevation)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        'dtm_data.tif',
        raster_bytes,
        src.crs.to_epsg() or 4326,
        float(np.min(raster_data)),
        float(np.max(raster_data))
    ))

conn.commit()
conn.close()
```

### Option 3: Create Sample Raster Data (for testing)
```sql
-- Create sample DTM data for Florence area
INSERT INTO cim_raster.dtm_raster (
    filename, srid, min_elevation, max_elevation, rast
) VALUES (
    'florence_sample_dtm.tif', 
    4326, 
    45.0, 
    150.0,
    decode('89504E470D0A1A0A0000000D494844520000001000000010080600000028A0DB6F0000001974455874536F6674776172650041646F626520496D616765526561647971C9653C0000000D49444154789C63F8CFCCC0C060008007000E0C027C86FB1E0000000049454E44AE426082', 'hex')
);

-- Create sample DSM data
INSERT INTO cim_raster.dsm_raster (
    filename, srid, min_elevation, max_elevation, rast
) VALUES (
    'florence_sample_dsm.tif',
    4326,
    45.0,
    180.0,
    decode('89504E470D0A1A0A0000000D494844520000001000000010080600000028A0DB6F0000001974455874536F6674776172650041646F626520496D616765526561647971C9653C0000000D49444154789C63F8CFCCC0C060008007000E0C027C86FB1E0000000049454E44AE426082', 'hex')
);

-- Verify raster data
SELECT filename, min_elevation, max_elevation FROM cim_raster.dtm_raster;
SELECT filename, min_elevation, max_elevation FROM cim_raster.dsm_raster;
```

## 🔌 Step 5: Connect Application to Docker Database

### Update Environment Configuration
```bash
# Copy environment template
cp env.example .env

# Edit .env file (it's already configured for Docker PostGIS)
# DATABASE_URL=postgresql://cim_wizard_user:cim_wizard_password@localhost:5432/cim_wizard_integrated
```

### Test Application Connection
```bash
# Start the application
python run.py

# Test database connection
python -c "
from app.db.database import engine
with engine.connect() as conn:
    result = conn.execute('SELECT COUNT(*) FROM cim_census.census_geo')
    print(f'Census zones: {result.scalar()}')
    result = conn.execute('SELECT COUNT(*) FROM cim_raster.dtm_raster') 
    print(f'DTM rasters: {result.scalar()}')
"
```

## 🧪 Step 6: Test the Complete Setup

### Test Census API
```bash
# Test census spatial query
curl -X POST "http://localhost:8000/api/census/census_spatial" \
    -H "Content-Type: application/json" \
    -d '[[11.2, 43.7], [11.3, 43.7], [11.3, 43.8], [11.2, 43.8], [11.2, 43.7]]'
```

### Test Raster API
```bash
# Test building height calculation
curl -X POST "http://localhost:8000/api/raster/height" \
    -H "Content-Type: application/json" \
    -d '{
        "type": "Polygon",
        "coordinates": [[[11.25, 43.75], [11.26, 43.75], [11.26, 43.76], [11.25, 43.76], [11.25, 43.75]]]
    }'
```

### Run Complete Test Suite
```bash
# Run the example test script
python examples/simple_api_usage.py
```

## 🐛 Troubleshooting

### Docker Issues
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs postgres

# Restart container
docker-compose restart postgres

# Rebuild if needed
docker-compose down
docker-compose build postgres
docker-compose up postgres -d
```

### Database Connection Issues
```bash
# Test direct connection
docker exec -it cim_integrated_db psql -U cim_wizard_user -d cim_wizard_integrated -c "SELECT 1;"

# Check port availability
netstat -an | grep 5432

# Reset database (WARNING: destroys all data)
docker-compose down -v
docker-compose up postgres -d
```

### Performance Optimization
```sql
-- Create indexes after data loading
CREATE INDEX IF NOT EXISTS idx_census_geometry ON cim_census.census_geo USING GIST(geometry);
CREATE INDEX IF NOT EXISTS idx_census_sez2011 ON cim_census.census_geo(SEZ2011);
CREATE INDEX IF NOT EXISTS idx_dtm_rast ON cim_raster.dtm_raster USING GIST(ST_ConvexHull(rast));
CREATE INDEX IF NOT EXISTS idx_dsm_rast ON cim_raster.dsm_raster USING GIST(ST_ConvexHull(rast));

-- Update table statistics
ANALYZE cim_census.census_geo;
ANALYZE cim_raster.dtm_raster;
ANALYZE cim_raster.dsm_raster;
```

## 📊 Data Sources and Formats

### Census Data Sources (Italy)
- **ISTAT**: https://www.istat.it/
- **OpenStreetMap**: Census boundaries
- **Regional portals**: Tuscany, Lombardy, etc.

### Raster Data Sources  
- **EU-DEM**: https://land.copernicus.eu/imagery-in-situ/eu-dem
- **Copernicus**: https://land.copernicus.eu/
- **NASA SRTM**: https://earthdata.nasa.gov/

### File Format Guidelines
- **Census**: Shapefile (.shp) or GeoJSON with demographic attributes
- **Raster**: GeoTIFF (.tif) with proper CRS (preferably EPSG:4326)
- **Coordinate System**: WGS84 (EPSG:4326) for consistency

## ✅ Success Criteria

Your setup is complete when:
- ✅ Docker PostGIS container is running and healthy
- ✅ All three schemas exist with proper extensions
- ✅ Census data is loaded and queryable
- ✅ Raster data is loaded and accessible
- ✅ Application connects successfully to Docker database
- ✅ API endpoints return data from populated tables
- ✅ Building height calculations work with raster data

Congratulations! Your CIM Wizard Integrated system is ready with Docker PostGIS! 🎉