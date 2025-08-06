-- CIM Wizard Integrated Database Initialization Script
-- Run this script BEFORE starting the FastAPI application

-- Enable required PostGIS extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS postgis_raster;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schemas for different service domains
CREATE SCHEMA IF NOT EXISTS cim_vector;   -- Vector/building data from vector_gateway_service
CREATE SCHEMA IF NOT EXISTS cim_census;   -- Census data from census_gateway_service  
CREATE SCHEMA IF NOT EXISTS cim_raster;   -- Raster data from raster_gateway_service

-- Set default search path to include all schemas
SET search_path TO cim_vector, cim_census, cim_raster, public;

-- Grant permissions (adjust username as needed)
GRANT ALL ON SCHEMA cim_vector TO postgres;
GRANT ALL ON SCHEMA cim_census TO postgres;
GRANT ALL ON SCHEMA cim_raster TO postgres;

-- Grant usage on all schemas to application user
-- Replace 'app_user' with your actual application database user
-- GRANT USAGE ON SCHEMA cim_vector TO app_user;
-- GRANT USAGE ON SCHEMA cim_census TO app_user;
-- GRANT USAGE ON SCHEMA cim_raster TO app_user;

-- Verify schema creation
SELECT schema_name FROM information_schema.schemata 
WHERE schema_name IN ('cim_vector', 'cim_census', 'cim_raster');

-- Create indexes after tables are created by SQLAlchemy
-- These should be run after the application creates the tables

-- Vector schema indexes
-- CREATE INDEX IF NOT EXISTS idx_building_geometry ON cim_vector.building USING GIST(building_geometry);
-- CREATE INDEX IF NOT EXISTS idx_building_id ON cim_vector.building(building_id);
-- CREATE INDEX IF NOT EXISTS idx_building_census_id ON cim_vector.building(census_id);
-- CREATE INDEX IF NOT EXISTS idx_project_scenario ON cim_vector.building_properties(project_id, scenario_id);
-- CREATE INDEX IF NOT EXISTS idx_grid_line_geometry ON cim_vector.grid_line USING GIST(geometry);
-- CREATE INDEX IF NOT EXISTS idx_grid_bus_geometry ON cim_vector.grid_bus USING GIST(geometry);

-- Census schema indexes
-- CREATE INDEX IF NOT EXISTS idx_census_geometry ON cim_census.census_geo USING GIST(geometry);
-- CREATE INDEX IF NOT EXISTS idx_census_sez2011 ON cim_census.census_geo(SEZ2011);
-- CREATE INDEX IF NOT EXISTS idx_census_comune ON cim_census.census_geo(COMUNE);

-- Raster schema indexes
-- CREATE INDEX IF NOT EXISTS idx_height_cache_building ON cim_raster.building_height_cache(building_id, project_id, scenario_id);