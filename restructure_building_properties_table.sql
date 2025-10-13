-- SQL Script to restructure cim_vector.building_properties table
-- Drop the 'id' column and make (building_id, project_id, scenario_id) the composite primary key

-- IMPORTANT: Backup your data first!
-- pg_dump -h localhost -p 5433 -U cim_wizard_user -t cim_vector.building_properties cim_wizard_integrated > backup_building_properties.sql

BEGIN;

-- Step 1: Check current table structure
SELECT 'Current building_properties table structure:' as info;
\d cim_vector.building_properties;

-- Step 2: Ensure no NULL values in the future primary key columns
UPDATE cim_vector.building_properties 
SET project_id = 'unknown_project' 
WHERE project_id IS NULL;

UPDATE cim_vector.building_properties 
SET scenario_id = 'unknown_scenario' 
WHERE scenario_id IS NULL;

UPDATE cim_vector.building_properties 
SET building_id = 'building_' || id::text 
WHERE building_id IS NULL;

-- Step 3: Check for duplicates on the composite key
SELECT 'Checking for duplicates on composite key:' as info;
SELECT 
    building_id,
    project_id,
    scenario_id,
    COUNT(*) as count
FROM cim_vector.building_properties
GROUP BY building_id, project_id, scenario_id
HAVING COUNT(*) > 1;

-- If there are duplicates, fix them (keep the one with the lowest id)
DELETE FROM cim_vector.building_properties bp1
USING cim_vector.building_properties bp2
WHERE bp1.id > bp2.id 
  AND bp1.building_id = bp2.building_id
  AND bp1.project_id = bp2.project_id
  AND bp1.scenario_id = bp2.scenario_id;

-- Step 4: Drop the current primary key constraint
ALTER TABLE cim_vector.building_properties DROP CONSTRAINT IF EXISTS building_properties_pkey;

-- Step 5: Set NOT NULL constraints on future primary key columns
ALTER TABLE cim_vector.building_properties ALTER COLUMN building_id SET NOT NULL;
ALTER TABLE cim_vector.building_properties ALTER COLUMN project_id SET NOT NULL;
ALTER TABLE cim_vector.building_properties ALTER COLUMN scenario_id SET NOT NULL;

-- Step 6: Add composite primary key constraint
ALTER TABLE cim_vector.building_properties 
ADD PRIMARY KEY (building_id, project_id, scenario_id);

-- Step 7: Drop the id column
ALTER TABLE cim_vector.building_properties DROP COLUMN id;

-- Step 8: Verify the new structure
SELECT 'New building_properties table structure:' as info;
\d cim_vector.building_properties;

-- Step 9: Test queries
SELECT 'Testing queries after restructure:' as test;

-- Count total building properties
SELECT COUNT(*) as total_building_properties 
FROM cim_vector.building_properties;

-- Test join with building table
SELECT COUNT(*) as joined_records
FROM cim_vector.building b
INNER JOIN cim_vector.building_properties bp ON b.building_id = bp.building_id;

-- Test residential buildings query
SELECT COUNT(*) as residential_buildings_with_geometry
FROM cim_vector.building b
INNER JOIN cim_vector.building_properties bp ON b.building_id = bp.building_id
WHERE bp.filter_res = TRUE;

-- Test unique combinations
SELECT 
    COUNT(DISTINCT building_id) as unique_buildings,
    COUNT(DISTINCT project_id) as unique_projects,
    COUNT(DISTINCT scenario_id) as unique_scenarios,
    COUNT(*) as total_records
FROM cim_vector.building_properties;

COMMIT;

SELECT 'Building Properties table restructure completed successfully!' as result;
