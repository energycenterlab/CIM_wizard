# CIM Wizard Database Docker Image

This Docker image contains a pre-loaded PostGIS database with all CIM (City Information Modeling) data for the CIM Wizard Integrated application.

## Image Information

- **Image Name**: `taherdoust/cim:dsm-sansalva-dtm-torino-buildingvector-sansalva-census-torino-loaded`
- **Base Image**: `postgis/postgis:15-3.4`
- **Database**: PostgreSQL 15 with PostGIS 3.4

## Pre-loaded Data

When someone pulls this image, they will have access to all the following data:

### 1. DSM (Digital Surface Model) Data
- **Region**: Sansalva
- **Format**: Raster data stored in PostGIS raster format
- **Schema**: `cim_raster.dsm`

### 2. DTM (Digital Terrain Model) Data  
- **Region**: Torino
- **Format**: Raster data stored in PostGIS raster format
- **Schema**: `cim_raster.dtm`

### 3. Building Vector Data
- **Region**: Sansalva
- **Format**: Vector geometries with building properties
- **Schema**: `cim_vector.vec_bld`

### 4. Census Data
- **Region**: Torino
- **Format**: Vector geometries with demographic data
- **Schema**: `cim_census.census`

### 5. Network Data
- **Format**: Power network data with PandaPower integration
- **Configurations**: 
  - With PV (Photovoltaic) systems
  - Without PV systems
- **Schema**: `cim_vector.network`

### 6. Additional Data
- **Scenario Data**: Various urban scenarios
- **Properties Data**: Building and land properties
- **Schema**: `cim_vector.vec_scen`, `cim_vector.vec_props`

## Database Configuration

- **Database Name**: `cim_wizard_integrated`
- **Username**: `cim_wizard_user`
- **Password**: `cim_wizard_password`
- **Port**: `5432`

## Usage

### Pull and Run the Image

```bash
# Pull the image
docker pull taherdoust/cim:dsm-sansalva-dtm-torino-buildingvector-sansalva-census-torino-loaded

# Run the database container
docker run -d \
  --name cim-database \
  -p 5432:5432 \
  -e POSTGRES_DB=cim_wizard_integrated \
  -e POSTGRES_USER=cim_wizard_user \
  -e POSTGRES_PASSWORD=cim_wizard_password \
  taherdoust/cim:dsm-sansalva-dtm-torino-buildingvector-sansalva-census-torino-loaded
```

### Connect to the Database

```bash
# Using psql
psql -h localhost -p 5432 -U cim_wizard_user -d cim_wizard_integrated

# Using Docker exec
docker exec -it cim-database psql -U cim_wizard_user -d cim_wizard_integrated
```

### Verify Data

```sql
-- Check available schemas
SELECT schema_name FROM information_schema.schemata 
WHERE schema_name LIKE 'cim_%';

-- Check DSM data
SELECT COUNT(*) FROM cim_raster.dsm;

-- Check DTM data  
SELECT COUNT(*) FROM cim_raster.dtm;

-- Check building data
SELECT COUNT(*) FROM cim_vector.vec_bld;

-- Check census data
SELECT COUNT(*) FROM cim_census.census;

-- Check network data
SELECT COUNT(*) FROM cim_vector.network;
```

## Building the Image

**Important**: The `Dockerfile.cimdb` creates a base image with only the schema setup, not the actual data. The data is already pre-loaded in the committed image.

### Option 1: Use the Pre-loaded Image (Recommended)
```bash
# Simply pull and use the image with all data already loaded
docker pull taherdoust/cim:dsm-sansalva-dtm-torino-buildingvector-sansalva-census-torino-loaded
```

### Option 2: Build Base Image from Dockerfile
If you need to rebuild the base environment (without data):

```bash
# Build the base image (schema only, no data)
docker build -f Dockerfile.cimdb -t cim-wizard-base .

# This creates a clean database with schemas but no data
# You would need to load data separately
```

### Option 3: Recreate the Full Image
To recreate the full image with data, you would need to:
1. Build the base image
2. Run it with data mounting
3. Load all the data
4. Commit the container as a new image

This is more complex and the pre-loaded image is much more convenient.

## Data Schemas

The database is organized into three main schemas:

- **`cim_vector`**: Vector data (buildings, scenarios, properties, networks)
- **`cim_census`**: Census and demographic data
- **`cim_raster`**: Raster data (DSM, DTM)

## Performance Configuration

The image includes optimized PostgreSQL settings for handling large geospatial datasets:

- Shared buffers: 256MB
- Max connections: 200
- Work memory: 4MB
- Maintenance work memory: 64MB
- Effective cache size: 1GB

## Health Check

The container includes a health check that verifies the database is ready to accept connections.

## Notes

- All data is pre-loaded during the first container startup
- The initialization process may take several minutes due to the large amount of data
- The container will automatically create all necessary schemas and load all data
- No additional setup or data loading is required after pulling the image
