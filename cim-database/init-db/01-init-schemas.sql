-- CIM Wizard Database: Create schemas and extensions
-- Runs first (alphabetically) before restore script
-- Ensures cim_vector, cim_census, cim_raster exist even if restore fails

-- Enable PostGIS extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS postgis_raster;

-- Create schemas for backend compatibility
CREATE SCHEMA IF NOT EXISTS cim_vector;
CREATE SCHEMA IF NOT EXISTS cim_census;
CREATE SCHEMA IF NOT EXISTS cim_raster;

-- Set search path
ALTER DATABASE cim_wizard_integrated SET search_path TO cim_vector, cim_census, cim_raster, public;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA cim_vector TO cim_wizard_user;
GRANT ALL PRIVILEGES ON SCHEMA cim_census TO cim_wizard_user;
GRANT ALL PRIVILEGES ON SCHEMA cim_raster TO cim_wizard_user;

SELECT 'Schemas and extensions initialized' as status;
