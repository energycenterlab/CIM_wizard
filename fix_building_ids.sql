-- SQL Script to fix building_id mismatches in the database

-- First, let's see the current state
SELECT 'Current Database State:' as info;

SELECT 
    'building table' as table_name,
    COUNT(*) as total_records,
    COUNT(DISTINCT building_id) as unique_building_ids
FROM cim_vector.building
UNION ALL
SELECT 
    'building_properties table' as table_name,
    COUNT(*) as total_records,
    COUNT(DISTINCT building_id) as unique_building_ids
FROM cim_vector.building_properties;

-- Check for orphaned building_properties (properties without matching buildings)
SELECT 
    'Orphaned building_properties' as issue,
    COUNT(DISTINCT bp.building_id) as count
FROM cim_vector.building_properties bp
LEFT JOIN cim_vector.building b ON b.building_id = bp.building_id
WHERE b.building_id IS NULL;

-- IMPORTANT: Before running the fixes below, backup your data!
-- pg_dump -h localhost -p 5433 -U cim_wizard_user -t cim_vector.building -t cim_vector.building_properties cim_wizard_integrated > backup_buildings.sql

-- Option 1: If you want to keep all building_properties and create missing building records
-- This assumes the building geometries can be reconstructed from other sources
/*
INSERT INTO cim_vector.building (building_id, lod, building_geometry_source, created_at)
SELECT DISTINCT 
    bp.building_id,
    bp.lod,
    'reconstructed',
    NOW()
FROM cim_vector.building_properties bp
LEFT JOIN cim_vector.building b ON b.building_id = bp.building_id
WHERE b.building_id IS NULL;
*/

-- Option 2: If you want to delete orphaned building_properties
-- WARNING: This will delete data!
/*
DELETE FROM cim_vector.building_properties bp
WHERE NOT EXISTS (
    SELECT 1 FROM cim_vector.building b 
    WHERE b.building_id = bp.building_id
);
*/

-- Option 3: If building IDs have inconsistent formats, standardize them
-- First, check the patterns
SELECT 
    CASE 
        WHEN building_id LIKE 'bld_%' THEN 'bld_ prefix'
        WHEN building_id LIKE 'osm_%' THEN 'osm_ prefix'
        WHEN building_id LIKE 'way/%' THEN 'way/ prefix'
        WHEN building_id LIKE 'node/%' THEN 'node/ prefix'
        WHEN building_id ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' THEN 'UUID format'
        ELSE 'other'
    END as id_pattern,
    COUNT(*) as count
FROM cim_vector.building
GROUP BY id_pattern
ORDER BY count DESC;

-- After fixing, verify the join works
SELECT 
    'Fixed join test' as test,
    COUNT(*) as joined_records
FROM cim_vector.building_properties bp
INNER JOIN cim_vector.building b ON b.building_id = bp.building_id
WHERE bp.filter_res = TRUE;

-- Clean up duplicate building records if any
-- Find duplicates
SELECT building_id, COUNT(*) as duplicate_count
FROM cim_vector.building
GROUP BY building_id
HAVING COUNT(*) > 1;

-- Remove duplicates keeping the one with geometry
/*
DELETE FROM cim_vector.building b1
USING cim_vector.building b2
WHERE b1.id > b2.id 
  AND b1.building_id = b2.building_id
  AND b1.building_geometry IS NULL;
*/
