-- CIM Wizard Integrated PostgreSQL/PostGIS Docker Initialization
-- This script runs automatically when the container starts for the first time

-- Enable required PostGIS extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS postgis_raster;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgrouting;

-- Create schemas for different service domains
CREATE SCHEMA IF NOT EXISTS cim_vector;   -- Vector/building data
CREATE SCHEMA IF NOT EXISTS cim_census;   -- Census data  
CREATE SCHEMA IF NOT EXISTS cim_raster;   -- Raster data

-- Set default search path
ALTER DATABASE cim_wizard_integrated SET search_path TO cim_vector, cim_census, cim_raster, public;

-- Create application user with appropriate permissions
CREATE USER IF NOT EXISTS cim_app_user WITH PASSWORD 'cim_app_password';

-- Grant permissions to schemas
GRANT ALL PRIVILEGES ON SCHEMA cim_vector TO cim_wizard_user;
GRANT ALL PRIVILEGES ON SCHEMA cim_census TO cim_wizard_user;
GRANT ALL PRIVILEGES ON SCHEMA cim_raster TO cim_wizard_user;

GRANT USAGE ON SCHEMA cim_vector TO cim_app_user;
GRANT USAGE ON SCHEMA cim_census TO cim_app_user;
GRANT USAGE ON SCHEMA cim_raster TO cim_app_user;

-- Grant permissions on future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA cim_vector GRANT ALL ON TABLES TO cim_wizard_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA cim_census GRANT ALL ON TABLES TO cim_wizard_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA cim_raster GRANT ALL ON TABLES TO cim_wizard_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA cim_vector GRANT ALL ON TABLES TO cim_app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA cim_census GRANT ALL ON TABLES TO cim_app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA cim_raster GRANT ALL ON TABLES TO cim_app_user;

-- Verify setup
SELECT 'Database initialization completed' as status;
SELECT schema_name FROM information_schema.schemata 
WHERE schema_name IN ('cim_vector', 'cim_census', 'cim_raster');

-- Show installed extensions
SELECT name, default_version, installed_version 
FROM pg_available_extensions 
WHERE name IN ('postgis', 'postgis_raster', 'postgis_topology', 'pgrouting')
AND installed_version IS NOT NULL;