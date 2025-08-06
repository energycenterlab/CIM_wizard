# Database Setup Guide for CIM Wizard Integrated

This guide explains how to set up the PostgreSQL database with PostGIS for CIM Wizard Integrated.

## Prerequisites

1. **PostgreSQL 12+** with **PostGIS 3.0+** installed
2. Database user with sufficient privileges to create extensions and schemas
3. Access to PostgreSQL command line tools (`psql`) or a database management tool

## Database Schema Structure

CIM Wizard Integrated uses three separate schemas to organize data:

- **`cim_vector`**: Vector data, buildings, grid infrastructure (from vector_gateway_service)
- **`cim_census`**: Census and demographic data (from census_gateway_service)  
- **`cim_raster`**: Raster data, DTM/DSM models (from raster_gateway_service)

## Setup Steps

### Step 1: Create Database

```sql
-- Connect as superuser (postgres)
psql -U postgres

-- Create database
CREATE DATABASE cim_wizard_integrated;

-- Connect to the new database
\c cim_wizard_integrated;
```

### Step 2: Run Initialization Script

Execute the provided SQL initialization script:

```bash
# From project root directory
psql -U postgres -d cim_wizard_integrated -f init_db.sql
```

Or copy/paste the SQL commands from `init_db.sql` into your database tool.

### Step 3: Verify Schema Creation

```sql
-- Check if schemas were created
SELECT schema_name FROM information_schema.schemata 
WHERE schema_name IN ('cim_vector', 'cim_census', 'cim_raster');

-- Check if PostGIS extensions are installed
SELECT name, default_version, installed_version 
FROM pg_available_extensions 
WHERE name LIKE 'postgis%';
```

### Step 4: Start Application

The FastAPI application will automatically create tables when started:

```bash
# Activate your environment first
conda activate cim_wizard

# Run the application
python run.py
```

### Step 5: Verify Table Creation

After starting the application, verify that tables were created:

```sql
-- Check tables in each schema
SELECT schemaname, tablename 
FROM pg_tables 
WHERE schemaname IN ('cim_vector', 'cim_census', 'cim_raster')
ORDER BY schemaname, tablename;
```

## Expected Tables

### cim_vector schema:
- `project_scenario` - Project and scenario information
- `building` - Building geometries and basic data
- `building_properties` - Detailed building properties
- `grid_bus` - Electrical grid bus locations
- `grid_line` - Electrical grid line networks

### cim_census schema:
- `census_geo` - Census zones with demographic data

### cim_raster schema:
- `raster_model` - General raster data storage
- `dtm_raster` - Digital Terrain Model data
- `dsm_raster` - Digital Surface Model data
- `building_height_cache` - Cached building height calculations

## Connection Configuration

Update your environment variables (see `env.example`):

```bash
DATABASE_URL=postgresql://username:password@localhost:5432/cim_wizard_integrated
```

Replace `username` and `password` with your PostgreSQL credentials.

## Troubleshooting

### Error: "extension does not exist"
- Ensure PostGIS is properly installed: `apt-get install postgresql-postgis` (Ubuntu/Debian)
- Connect as superuser to install extensions

### Error: "permission denied for schema"
- Grant proper permissions to your application user:
```sql
GRANT USAGE ON SCHEMA cim_vector TO your_app_user;
GRANT USAGE ON SCHEMA cim_census TO your_app_user;  
GRANT USAGE ON SCHEMA cim_raster TO your_app_user;
```

### Error: "relation does not exist"
- Ensure the application was started successfully and created tables
- Check the application logs for SQLAlchemy errors
- Verify database connection string is correct

### Performance Optimization

After loading data, you may want to create additional indexes:

```sql
-- Run these after your data is loaded
CREATE INDEX IF NOT EXISTS idx_building_geometry 
ON cim_vector.building USING GIST(building_geometry);

CREATE INDEX IF NOT EXISTS idx_census_geometry 
ON cim_census.census_geo USING GIST(geometry);

CREATE INDEX IF NOT EXISTS idx_building_id 
ON cim_vector.building(building_id);

CREATE INDEX IF NOT EXISTS idx_building_properties_project 
ON cim_vector.building_properties(project_id, scenario_id);
```

## Manual Table Creation (if needed)

If automatic table creation fails, you can manually create tables using SQLAlchemy:

```python
# Python script to create tables manually
from app.db.database import engine, Base, create_all_schemas
from app.models.vector import *
from app.models.census import *
from app.models.raster import *

# Create schemas
create_all_schemas()

# Create all tables
Base.metadata.create_all(bind=engine)
print("All tables created successfully")
```

## Data Loading

Once tables are created, you can load data:

1. **Vector data**: Use the `/api/vector` endpoints to load project scenarios and buildings
2. **Census data**: Import census shapefiles to `cim_census.census_geo` table
3. **Raster data**: Upload DTM/DSM files through `/api/raster` endpoints

## Backup and Restore

```bash
# Backup
pg_dump -U postgres -d cim_wizard_integrated > backup.sql

# Restore
psql -U postgres -d cim_wizard_integrated < backup.sql
```