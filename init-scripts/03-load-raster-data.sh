#!/bin/bash
# Load raster data from TIF files into cim_raster schema
# This script loads DSM and DTM raster files

set -e

echo "Loading raster data into cim_raster schema..."

# Database connection parameters
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=${POSTGRES_DB}
export PGUSER=${POSTGRES_USER}
export PGPASSWORD=${POSTGRES_PASSWORD}

# Create raster tables
psql -c "
CREATE TABLE IF NOT EXISTS cim_raster.dsm_raster (
    id SERIAL PRIMARY KEY,
    rast raster,
    filename VARCHAR(255),
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    srid INTEGER DEFAULT 4326,
    min_elevation FLOAT,
    max_elevation FLOAT
);

CREATE TABLE IF NOT EXISTS cim_raster.dtm_raster (
    id SERIAL PRIMARY KEY,
    rast raster,
    filename VARCHAR(255),
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    srid INTEGER DEFAULT 4326,
    min_elevation FLOAT,
    max_elevation FLOAT
);

-- Create table for individual DTM tiles (for detailed analysis)
CREATE TABLE IF NOT EXISTS cim_raster.dtm_raster_tiles (
    id SERIAL PRIMARY KEY,
    rast raster,
    filename VARCHAR(255),
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    srid INTEGER DEFAULT 4326,
    tile_x INTEGER,
    tile_y INTEGER
);

-- Create table for individual DSM tiles (for detailed analysis)
CREATE TABLE IF NOT EXISTS cim_raster.dsm_raster_tiles (
    id SERIAL PRIMARY KEY,
    rast raster,
    filename VARCHAR(255),
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    srid INTEGER DEFAULT 4326,
    tile_x INTEGER,
    tile_y INTEGER
);

CREATE TABLE IF NOT EXISTS cim_raster.building_height_cache (
    id SERIAL PRIMARY KEY,
    building_id VARCHAR(100) NOT NULL,
    project_id VARCHAR(100) NOT NULL,
    scenario_id VARCHAR(100) NOT NULL,
    dtm_avg_height FLOAT,
    dsm_avg_height FLOAT,
    building_height FLOAT,
    calculation_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    calculation_method VARCHAR(50) DEFAULT 'raster_intersection',
    coverage_percentage FLOAT,
    confidence_score FLOAT
);
"

# Load DSM raster data with optimized tiling and mosaicking
echo "Loading DSM raster data with mosaicking..."
if [ -f "/rawdata/sansalva_dsm.tif" ]; then
    # Load raster data using optimized parameters for spatial queries
    echo "Loading DSM tiles into temporary table..."
    raster2pgsql -I -C -M -F -t 256x256 -s 4326 -r /rawdata/sansalva_dsm.tif cim_raster.dsm_raster_tiles_temp | psql
    
    # Create mosaicked version for faster spatial queries
    echo "Creating mosaicked DSM raster..."
    psql -c "
    -- Create a single mosaicked raster for optimal spatial performance
    INSERT INTO cim_raster.dsm_raster (rast, filename, srid, min_elevation, max_elevation)
    SELECT 
        ST_Union(rast) as rast,
        'sansalva_dsm.tif' as filename,
        4326 as srid,
        MIN(ST_BandMetadata(rast, 1).min) as min_elevation,
        MAX(ST_BandMetadata(rast, 1).max) as max_elevation
    FROM cim_raster.dsm_raster_tiles_temp;
    
    -- Also keep individual tiles for detailed analysis if needed
    INSERT INTO cim_raster.dsm_raster_tiles (rast, filename, srid, tile_x, tile_y)
    SELECT 
        rast,
        'sansalva_dsm.tif',
        4326,
        ROW_NUMBER() OVER (ORDER BY ST_UpperLeftX(rast)) as tile_x,
        ROW_NUMBER() OVER (ORDER BY ST_UpperLeftY(rast) DESC) as tile_y
    FROM cim_raster.dsm_raster_tiles_temp;
    
    -- Clean up temp table
    DROP TABLE IF EXISTS cim_raster.dsm_raster_tiles_temp;
    "
    
    echo "DSM raster data loaded and mosaicked successfully"
else
    echo "Warning: DSM file not found at /rawdata/sansalva_dsm.tif"
fi

# Load DTM raster data with optimized tiling and mosaicking
echo "Loading DTM raster data with mosaicking..."
if [ -f "/rawdata/sansalva_dtm.tif" ]; then
    # Load raster data using optimized parameters for spatial queries
    # -t 256x256: Larger tiles for better performance
    # -r: Add raster constraints and spatial index
    # -I: Create spatial index (GIST)
    # -C: Apply raster constraints 
    # -M: Vacuum analyze after load
    # -F: Add filename column
    echo "Loading DTM tiles into temporary table..."
    raster2pgsql -I -C -M -F -t 256x256 -s 4326 -r /rawdata/sansalva_dtm.tif cim_raster.dtm_raster_tiles_temp | psql
    
    # Create mosaicked version for faster spatial queries
    echo "Creating mosaicked DTM raster..."
    psql -c "
    -- Create a single mosaicked raster for optimal spatial performance
    INSERT INTO cim_raster.dtm_raster (rast, filename, srid, min_elevation, max_elevation)
    SELECT 
        ST_Union(rast) as rast,
        'sansalva_dtm.tif' as filename,
        4326 as srid,
        MIN(ST_BandMetadata(rast, 1).min) as min_elevation,
        MAX(ST_BandMetadata(rast, 1).max) as max_elevation
    FROM cim_raster.dtm_raster_tiles_temp;
    
    -- Also keep individual tiles for detailed analysis if needed
    INSERT INTO cim_raster.dtm_raster_tiles (rast, filename, srid, tile_x, tile_y)
    SELECT 
        rast,
        'sansalva_dtm.tif',
        4326,
        ROW_NUMBER() OVER (ORDER BY ST_UpperLeftX(rast)) as tile_x,
        ROW_NUMBER() OVER (ORDER BY ST_UpperLeftY(rast) DESC) as tile_y
    FROM cim_raster.dtm_raster_tiles_temp;
    
    -- Clean up temp table
    DROP TABLE IF EXISTS cim_raster.dtm_raster_tiles_temp;
    "
    
    echo "DTM raster data loaded and mosaicked successfully"
else
    echo "Warning: DTM file not found at /rawdata/sansalva_dtm.tif"
fi

# Create spatial indexes for optimal query performance
echo "Creating spatial indexes for raster tables..."
psql -c "
-- Indexes for mosaicked rasters (main tables)
CREATE INDEX IF NOT EXISTS dsm_raster_st_convexhull_idx ON cim_raster.dsm_raster USING GIST(ST_ConvexHull(rast));
CREATE INDEX IF NOT EXISTS dtm_raster_st_convexhull_idx ON cim_raster.dtm_raster USING GIST(ST_ConvexHull(rast));

-- Indexes for tiled rasters (for detailed analysis)
CREATE INDEX IF NOT EXISTS dsm_tiles_raster_gist_idx ON cim_raster.dsm_raster_tiles USING GIST(ST_ConvexHull(rast));
CREATE INDEX IF NOT EXISTS dtm_tiles_raster_gist_idx ON cim_raster.dtm_raster_tiles USING GIST(ST_ConvexHull(rast));
CREATE INDEX IF NOT EXISTS dsm_tiles_tile_idx ON cim_raster.dsm_raster_tiles(tile_x, tile_y);
CREATE INDEX IF NOT EXISTS dtm_tiles_tile_idx ON cim_raster.dtm_raster_tiles(tile_x, tile_y);

-- Index for building height cache
CREATE INDEX IF NOT EXISTS building_height_cache_idx ON cim_raster.building_height_cache(building_id, project_id, scenario_id);
CREATE INDEX IF NOT EXISTS building_height_cache_building_idx ON cim_raster.building_height_cache(building_id);
"

# Verify data loading
echo "Verifying raster data loading..."
psql -c "
SELECT 'Raster data loaded successfully' as status;

-- Mosaicked rasters (main tables for spatial queries)
SELECT 'DSM mosaicked rasters: ' || COUNT(*) as dsm_mosaic_count FROM cim_raster.dsm_raster;
SELECT 'DTM mosaicked rasters: ' || COUNT(*) as dtm_mosaic_count FROM cim_raster.dtm_raster;

-- Individual tiles (for detailed analysis)
SELECT 'DSM tiles: ' || COUNT(*) as dsm_tiles_count FROM cim_raster.dsm_raster_tiles;
SELECT 'DTM tiles: ' || COUNT(*) as dtm_tiles_count FROM cim_raster.dtm_raster_tiles;

-- Show sample metadata
SELECT 'DSM elevation range: ' || min_elevation || ' to ' || max_elevation || 'm' as dsm_range 
FROM cim_raster.dsm_raster LIMIT 1;

SELECT 'DTM elevation range: ' || min_elevation || ' to ' || max_elevation || 'm' as dtm_range 
FROM cim_raster.dtm_raster LIMIT 1;

-- Show raster coverage area
SELECT 'DSM coverage area: ' || ROUND(ST_Area(ST_ConvexHull(rast))::numeric, 2) || ' sq units' as dsm_area
FROM cim_raster.dsm_raster LIMIT 1;

SELECT 'DTM coverage area: ' || ROUND(ST_Area(ST_ConvexHull(rast))::numeric, 2) || ' sq units' as dtm_area
FROM cim_raster.dtm_raster LIMIT 1;
"

echo "Raster data loading completed!"
