-- Quick SQL commands to restructure cim_vector.building_properties table
-- Make (building_id, project_id, scenario_id) composite primary key and drop id column

-- BACKUP FIRST!
-- pg_dump -h localhost -p 5433 -U cim_wizard_user -t cim_vector.building_properties cim_wizard_integrated > backup_building_properties.sql

BEGIN;

-- 1. Ensure no NULLs in future primary key columns
UPDATE cim_vector.building_properties 
SET project_id = 'unknown_project' 
WHERE project_id IS NULL;

UPDATE cim_vector.building_properties 
SET scenario_id = 'unknown_scenario' 
WHERE scenario_id IS NULL;

UPDATE cim_vector.building_properties 
SET building_id = 'building_' || id::text 
WHERE building_id IS NULL;

-- 2. Remove duplicates if any (keep the one with the lowest id)
DELETE FROM cim_vector.building_properties bp1
USING cim_vector.building_properties bp2
WHERE bp1.id > bp2.id 
  AND bp1.building_id = bp2.building_id
  AND bp1.project_id = bp2.project_id
  AND bp1.scenario_id = bp2.scenario_id;

-- 3. Drop current primary key
ALTER TABLE cim_vector.building_properties DROP CONSTRAINT building_properties_pkey;

-- 4. Set columns as NOT NULL and add composite primary key
ALTER TABLE cim_vector.building_properties ALTER COLUMN building_id SET NOT NULL;
ALTER TABLE cim_vector.building_properties ALTER COLUMN project_id SET NOT NULL;
ALTER TABLE cim_vector.building_properties ALTER COLUMN scenario_id SET NOT NULL;

ALTER TABLE cim_vector.building_properties 
ADD PRIMARY KEY (building_id, project_id, scenario_id);

-- 5. Drop the old id column
ALTER TABLE cim_vector.building_properties DROP COLUMN id;

COMMIT;

-- Test the result
SELECT 'Building Properties restructure completed!' as status;
SELECT COUNT(*) as properties_count FROM cim_vector.building_properties;
SELECT COUNT(*) as residential_with_geometry 
FROM cim_vector.building b
INNER JOIN cim_vector.building_properties bp ON b.building_id = bp.building_id
WHERE bp.filter_res = TRUE;
