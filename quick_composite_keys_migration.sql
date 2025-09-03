-- Quick Migration to Composite Keys
-- BACKUP FIRST: pg_dump -h localhost -p 5433 -U cim_wizard_user cim_wizard_integrated > backup.sql

BEGIN;

-- 1. Clean data and remove NULLs
UPDATE cim_vector.building SET lod = 0 WHERE lod IS NULL;
UPDATE cim_vector.building_properties SET lod = 0 WHERE lod IS NULL;
UPDATE cim_vector.building_properties SET project_id = 'unknown_project' WHERE project_id IS NULL;
UPDATE cim_vector.building_properties SET scenario_id = 'unknown_scenario' WHERE scenario_id IS NULL;

-- 2. Remove duplicates (keep first occurrence)
DELETE FROM cim_vector.building b1 
USING cim_vector.building b2 
WHERE b1.ctid > b2.ctid 
  AND b1.building_id = b2.building_id 
  AND b1.lod = b2.lod;

DELETE FROM cim_vector.building_properties bp1
USING cim_vector.building_properties bp2
WHERE bp1.ctid > bp2.ctid
  AND bp1.building_id = bp2.building_id
  AND bp1.lod = bp2.lod  
  AND bp1.project_id = bp2.project_id
  AND bp1.scenario_id = bp2.scenario_id;

-- 3. Drop existing primary keys
ALTER TABLE cim_vector.building DROP CONSTRAINT IF EXISTS building_pkey;
ALTER TABLE cim_vector.project_scenario DROP CONSTRAINT IF EXISTS project_scenario_pkey;
ALTER TABLE cim_vector.building_properties DROP CONSTRAINT IF EXISTS building_properties_pkey;

-- 4. Create new composite primary keys
ALTER TABLE cim_vector.building ADD PRIMARY KEY (building_id, lod);
ALTER TABLE cim_vector.project_scenario ADD PRIMARY KEY (project_id, scenario_id);
ALTER TABLE cim_vector.building_properties ADD PRIMARY KEY (building_id, lod, project_id, scenario_id);

-- 5. Add foreign key constraints
ALTER TABLE cim_vector.building_properties 
ADD CONSTRAINT fk_bp_building 
FOREIGN KEY (building_id, lod) REFERENCES cim_vector.building(building_id, lod);

ALTER TABLE cim_vector.building_properties 
ADD CONSTRAINT fk_bp_scenario 
FOREIGN KEY (project_id, scenario_id) REFERENCES cim_vector.project_scenario(project_id, scenario_id);

COMMIT;

-- Test the new structure
SELECT 'Migration completed!' as status;
SELECT COUNT(*) as buildings FROM cim_vector.building;
SELECT COUNT(*) as properties FROM cim_vector.building_properties;
SELECT COUNT(*) as joined_records 
FROM cim_vector.building b
INNER JOIN cim_vector.building_properties bp 
    ON b.building_id = bp.building_id AND b.lod = bp.lod;
