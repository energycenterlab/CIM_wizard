-- Final verification script for CIM Wizard Integrated database setup
-- This script verifies that all schemas, tables, and data are properly loaded

-- Show all schemas
SELECT 'Database schemas:' as info;
SELECT schema_name FROM information_schema.schemata 
WHERE schema_name IN ('cim_vector', 'cim_census', 'cim_raster')
ORDER BY schema_name;

-- Show PostGIS extensions
SELECT 'PostGIS extensions:' as info;
SELECT name, default_version, installed_version 
FROM pg_available_extensions 
WHERE name IN ('postgis', 'postgis_raster', 'postgis_topology', 'pgrouting')
AND installed_version IS NOT NULL
ORDER BY name;

-- Check tables in each schema
SELECT 'Tables in cim_vector schema:' as info;
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'cim_vector'
ORDER BY table_name;

SELECT 'Tables in cim_census schema:' as info;
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'cim_census'
ORDER BY table_name;

SELECT 'Tables in cim_raster schema:' as info;
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'cim_raster'
ORDER BY table_name;

-- Data counts
SELECT 'Data verification:' as info;

-- Census data count
SELECT 'Census records: ' || COALESCE(COUNT(*), 0) as count 
FROM cim_census.census_geo;

-- Sample census data
SELECT 'Sample census data (first 3 records):' as info;
SELECT SEZ2011, COMUNE, P1 as total_population, REGIONE
FROM cim_census.census_geo 
LIMIT 3;

-- Raster data count
SELECT 'DSM raster tiles: ' || COALESCE(COUNT(*), 0) as count 
FROM cim_raster.dsm_raster;

SELECT 'DTM raster tiles: ' || COALESCE(COUNT(*), 0) as count 
FROM cim_raster.dtm_raster;

-- Sample raster metadata
SELECT 'Sample DSM raster info:' as info;
SELECT filename, srid, min_elevation, max_elevation, upload_date
FROM cim_raster.dsm_raster 
LIMIT 1;

SELECT 'Sample DTM raster info:' as info;
SELECT filename, srid, min_elevation, max_elevation, upload_date
FROM cim_raster.dtm_raster 
LIMIT 1;

-- Spatial indexes verification
SELECT 'Spatial indexes:' as info;
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE schemaname IN ('cim_vector', 'cim_census', 'cim_raster')
AND (indexname LIKE '%geom%' OR indexname LIKE '%geog%' OR indexname LIKE '%rast%' OR indexname LIKE '%gist%')
ORDER BY schemaname, tablename;

-- Database ready confirmation
SELECT 'DATABASE SETUP COMPLETE - Ready for CIM Wizard Integrated!' as status;
