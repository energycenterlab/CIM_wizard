-- Test queries for the new composite key schema

-- Test 1: Your original query should now work perfectly!
SELECT 'Test 1: Residential buildings with geometry' as test;
SELECT COUNT(*) as residential_buildings_with_geometry
FROM cim_vector.building AS b
INNER JOIN cim_vector.building_properties AS bp 
    ON b.building_id = bp.building_id AND b.lod = bp.lod
WHERE bp.filter_res = TRUE;

-- Test 2: Get actual geometries of residential buildings  
SELECT 'Test 2: Sample residential building geometries' as test;
SELECT 
    b.building_id,
    b.lod,
    bp.project_id,
    bp.scenario_id,
    bp.filter_res,
    ST_AsText(ST_Centroid(b.building_geometry)) as centroid
FROM cim_vector.building AS b
INNER JOIN cim_vector.building_properties AS bp 
    ON b.building_id = bp.building_id AND b.lod = bp.lod
WHERE bp.filter_res = TRUE
LIMIT 5;

-- Test 3: Check data integrity
SELECT 'Test 3: Data integrity checks' as test;

SELECT 
    'Buildings' as table_name,
    COUNT(*) as total_records,
    COUNT(DISTINCT building_id) as unique_building_ids,
    COUNT(DISTINCT (building_id, lod)) as unique_composite_keys
FROM cim_vector.building

UNION ALL

SELECT 
    'Properties' as table_name,
    COUNT(*) as total_records,
    COUNT(DISTINCT building_id) as unique_building_ids,
    COUNT(DISTINCT (building_id, lod, project_id, scenario_id)) as unique_composite_keys
FROM cim_vector.building_properties;

-- Test 4: Foreign key integrity
SELECT 'Test 4: Foreign key integrity' as test;

-- Orphaned properties (should be 0)
SELECT 
    'Orphaned properties (should be 0)' as check_type,
    COUNT(*) as count
FROM cim_vector.building_properties bp
LEFT JOIN cim_vector.building b 
    ON bp.building_id = b.building_id AND bp.lod = b.lod
WHERE b.building_id IS NULL

UNION ALL

-- Properties with scenarios that don't exist (should be 0 after proper setup)
SELECT 
    'Properties without valid scenarios' as check_type,
    COUNT(*) as count
FROM cim_vector.building_properties bp
LEFT JOIN cim_vector.project_scenario ps
    ON bp.project_id = ps.project_id AND bp.scenario_id = ps.scenario_id
WHERE ps.project_id IS NULL;

-- Test 5: Complex query with all relationships
SELECT 'Test 5: Complex query with all relationships' as test;
SELECT 
    ps.project_name,
    ps.scenario_name,
    COUNT(DISTINCT b.building_id) as total_buildings,
    COUNT(DISTINCT CASE WHEN bp.filter_res = TRUE THEN b.building_id END) as residential_buildings,
    AVG(bp.height) as avg_height,
    AVG(bp.area) as avg_area
FROM cim_vector.project_scenario ps
LEFT JOIN cim_vector.building_properties bp 
    ON ps.project_id = bp.project_id AND ps.scenario_id = bp.scenario_id
LEFT JOIN cim_vector.building b 
    ON bp.building_id = b.building_id AND bp.lod = b.lod
GROUP BY ps.project_id, ps.scenario_id, ps.project_name, ps.scenario_name
ORDER BY total_buildings DESC
LIMIT 5;
