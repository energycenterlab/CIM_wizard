# CIM Wizard Integrated Database Setup Summary

## Overview
This document summarizes the database setup for the CIM Wizard Integrated project, which now includes automatic loading of census and raster data into properly organized PostGIS schemas.

## Database Setup

### Docker Configuration
- **File**: `docker-compose.db.yml`
- **Container**: `integrateddb` (PostgreSQL 15 + PostGIS 3.4)
- **Port**: 5433 (host) -> 5432 (container)
- **Database**: `cim_wizard_integrated`
- **User**: `cim_wizard_user`
- **Password**: `cim_wizard_password`

### Volume Mounts
- `./pgdata:/var/lib/postgresql/data` - Database persistence
- `./init-scripts:/docker-entrypoint-initdb.d` - Initialization scripts
- `./rawdata:/rawdata:ro` - Raw data files (read-only)

### Schema Organization
The database is organized into three main schemas:

1. **cim_vector** - Vector/building data
2. **cim_census** - Census demographic data
3. **cim_raster** - Raster elevation data (DTM/DSM)

## Initialization Scripts

The database initialization happens automatically through numbered scripts in `init-scripts/`:

### 01-init-database.sql
- Creates PostGIS extensions (postgis, postgis_raster, postgis_topology, pgrouting, ogr_fdw)
- Creates the three main schemas
- Sets up user permissions
- Configures default search path

### 02-create-sample-data.sql
- Creates sample test data for verification
- Inserts sample records in all three schemas
- Provides basic functionality testing

### 03-load-census-data.sql
- Loads census data from `rawdata/sansalva_census.gpkg`
- Uses OGR Foreign Data Wrapper (ogr_fdw) for GPKG access
- Handles geometry transformation to MULTIPOLYGON
- Creates spatial indexes for performance
- Maps all census attributes (P1-P140, ST1-ST15, A2-A48, PF1-PF9, E1-E31)

### 04-load-raster-data.sh
- Loads DSM and DTM raster data from TIF files
- Uses `raster2pgsql` tool for raster loading
- Creates proper PostGIS raster tables
- Calculates elevation statistics (min/max)
- Creates spatial indexes on raster data

### 05-verify-setup.sql
- Comprehensive verification of database setup
- Shows all schemas, tables, and data counts
- Displays sample data from each schema
- Confirms spatial indexes are created
- Provides final status confirmation

## Raw Data Files

Located in `rawdata/` directory:
- `sansalva_census.gpkg` - Census demographic data (GPKG format)
- `sansalva_dsm.tif` - Digital Surface Model raster
- `sansalva_dtm.tif` - Digital Terrain Model raster

## Key Features

### PostGIS Extensions
- Full spatial data support with PostGIS
- Raster data support with postgis_raster
- Network analysis with pgrouting
- External data access with ogr_fdw

### Automatic Data Loading
- Census data automatically loaded from GPKG
- Raster data automatically loaded from TIF files
- Proper coordinate system handling (EPSG:4326)
- Spatial indexing for performance

### Data Verification
- Built-in verification scripts
- Data count reports
- Sample data display
- Setup completion confirmation

## Usage Instructions

1. **Build and Start Database**:
   ```bash
   docker-compose -f docker-compose.db.yml up --build
   ```

2. **Connect via pgAdmin**:
   - Host: localhost
   - Port: 5433
   - Database: cim_wizard_integrated
   - Username: cim_wizard_user
   - Password: cim_wizard_password

3. **Verify Setup**:
   Check container logs for initialization messages and "DATABASE SETUP COMPLETE" confirmation.

## Schema Details

### cim_census.census_geo
- Contains Italian census data with full demographic attributes
- Geometry stored as MULTIPOLYGON in WGS84 (EPSG:4326)
- Indexed on SEZ2011 (census ID), COMUNE (municipality), and geometry

### cim_raster.dsm_raster / cim_raster.dtm_raster
- Contains elevation raster data as PostGIS raster type
- Automatic elevation statistics calculation
- Spatial indexing for efficient querying
- Metadata tracking (filename, upload date, SRID)

### cim_vector.* tables
- Building geometries and properties
- Project scenarios and boundaries
- Grid infrastructure (buses and lines)
- Ready for CIM Wizard application data

## Notes
- All scripts handle conflicts gracefully (ON CONFLICT DO NOTHING)
- Foreign data wrappers are cleaned up after use
- Raster data is tiled for optimal performance (100x100 tiles)
- Database is ready for immediate use by the CIM Wizard application
