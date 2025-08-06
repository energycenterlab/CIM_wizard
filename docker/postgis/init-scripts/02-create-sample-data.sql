-- Sample data creation for testing CIM Wizard Integrated
-- This creates basic test data to verify the setup works

-- Insert sample project scenario
INSERT INTO cim_vector.project_scenario (
    project_id, scenario_id, project_name, scenario_name,
    project_boundary, project_center, project_zoom, project_crs
) VALUES (
    'docker_test_project', 'scenario_001', 
    'Docker Test Project', 'Default Scenario',
    ST_GeomFromText('POLYGON((11.2 43.7, 11.3 43.7, 11.3 43.8, 11.2 43.8, 11.2 43.7))', 4326),
    ST_GeomFromText('POINT(11.25 43.75)', 4326),
    15, 4326
) ON CONFLICT DO NOTHING;

-- Insert sample building
INSERT INTO cim_vector.building (
    building_id, lod, building_geometry, building_geometry_source
) VALUES (
    'docker_test_building_001', 0,
    ST_GeomFromText('POLYGON((11.24 43.74, 11.26 43.74, 11.26 43.76, 11.24 43.76, 11.24 43.74))', 4326),
    'test_data'
) ON CONFLICT DO NOTHING;

-- Insert sample building properties
INSERT INTO cim_vector.building_properties (
    building_id, project_id, scenario_id, lod,
    height, area, volume, type, n_people
) VALUES (
    'docker_test_building_001', 'docker_test_project', 'scenario_001', 0,
    15.5, 120.0, 1860.0, 'residential', 4
) ON CONFLICT DO NOTHING;

-- Insert sample census data (Florence area example)
INSERT INTO cim_census.census_geo (
    SEZ2011, geometry, REGIONE, PROVINCIA, COMUNE, P1
) VALUES (
    480001001001, 
    ST_GeomFromText('MULTIPOLYGON(((11.2 43.7, 11.3 43.7, 11.3 43.8, 11.2 43.8, 11.2 43.7)))', 4326),
    'Toscana', 'Firenze', 'Firenze', 1000
) ON CONFLICT DO NOTHING;

-- Insert sample raster metadata (DTM example)
INSERT INTO cim_raster.dtm_raster (
    filename, srid, min_elevation, max_elevation, rast
) VALUES (
    'florence_dtm_sample.tif', 4326, 45.0, 150.0, 
    decode('89504E470D0A1A0A0000000D494844520000001000000010080600000028A0DB6F0000001974455874536F6674776172650041646F626520496D616765526561647971C9653C0000000D49444154789C63F8CFCCC0C060008007000E0C027C86FB1E0000000049454E44AE426082', 'hex')
) ON CONFLICT DO NOTHING;

-- Insert sample height cache
INSERT INTO cim_raster.building_height_cache (
    building_id, project_id, scenario_id, 
    dtm_avg_height, dsm_avg_height, building_height
) VALUES (
    'docker_test_building_001', 'docker_test_project', 'scenario_001',
    65.5, 81.0, 15.5
) ON CONFLICT DO NOTHING;

-- Verify sample data
SELECT 'Sample data inserted successfully' as status;
SELECT 'Vector data: ' || COUNT(*) || ' projects' FROM cim_vector.project_scenario;
SELECT 'Census data: ' || COUNT(*) || ' zones' FROM cim_census.census_geo;
SELECT 'Raster data: ' || COUNT(*) || ' rasters' FROM cim_raster.dtm_raster;