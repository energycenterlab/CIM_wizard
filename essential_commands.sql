-- ESSENTIAL COMMANDS - Run these one by one

-- 1. Fix NULL values
UPDATE cim_vector.building SET lod = 0 WHERE lod IS NULL;
UPDATE cim_vector.building_properties SET lod = 0 WHERE lod IS NULL;
UPDATE cim_vector.building_properties SET project_id = 'unknown_project' WHERE project_id IS NULL;
UPDATE cim_vector.building_properties SET scenario_id = 'unknown_scenario' WHERE scenario_id IS NULL;

-- 2. Remove duplicates
DELETE FROM cim_vector.building b1 USING cim_vector.building b2 WHERE b1.ctid > b2.ctid AND b1.building_id = b2.building_id AND b1.lod = b2.lod;
DELETE FROM cim_vector.building_properties bp1 USING cim_vector.building_properties bp2 WHERE bp1.ctid > bp2.ctid AND bp1.building_id = bp2.building_id AND bp1.lod = bp2.lod AND bp1.project_id = bp2.project_id AND bp1.scenario_id = bp2.scenario_id;

-- 3. Drop old primary keys
ALTER TABLE cim_vector.building DROP CONSTRAINT IF EXISTS building_pkey;
ALTER TABLE cim_vector.project_scenario DROP CONSTRAINT IF EXISTS project_scenario_pkey;
ALTER TABLE cim_vector.building_properties DROP CONSTRAINT IF EXISTS building_properties_pkey;

-- 4. Drop old id columns
ALTER TABLE cim_vector.building DROP COLUMN IF EXISTS id;
ALTER TABLE cim_vector.building_properties DROP COLUMN IF EXISTS id;

-- 5. Set NOT NULL constraints
ALTER TABLE cim_vector.building ALTER COLUMN building_id SET NOT NULL;
ALTER TABLE cim_vector.building ALTER COLUMN lod SET NOT NULL;
ALTER TABLE cim_vector.project_scenario ALTER COLUMN project_id SET NOT NULL;
ALTER TABLE cim_vector.project_scenario ALTER COLUMN scenario_id SET NOT NULL;
ALTER TABLE cim_vector.building_properties ALTER COLUMN building_id SET NOT NULL;
ALTER TABLE cim_vector.building_properties ALTER COLUMN lod SET NOT NULL;
ALTER TABLE cim_vector.building_properties ALTER COLUMN project_id SET NOT NULL;
ALTER TABLE cim_vector.building_properties ALTER COLUMN scenario_id SET NOT NULL;

-- 6. Create new primary keys
ALTER TABLE cim_vector.building ADD PRIMARY KEY (building_id, lod);
ALTER TABLE cim_vector.project_scenario ADD PRIMARY KEY (project_id, scenario_id);
ALTER TABLE cim_vector.building_properties ADD PRIMARY KEY (building_id, lod, project_id, scenario_id);

-- 7. Add foreign key constraints
ALTER TABLE cim_vector.building_properties ADD CONSTRAINT fk_building_properties_building FOREIGN KEY (building_id, lod) REFERENCES cim_vector.building(building_id, lod) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE cim_vector.building_properties ADD CONSTRAINT fk_building_properties_project_scenario FOREIGN KEY (project_id, scenario_id) REFERENCES cim_vector.project_scenario(project_id, scenario_id) ON DELETE CASCADE ON UPDATE CASCADE;

-- 8. Test the result
SELECT COUNT(*) as residential_buildings_with_geometry FROM cim_vector.building AS b INNER JOIN cim_vector.building_properties AS bp ON b.building_id = bp.building_id AND b.lod = bp.lod WHERE bp.filter_res = TRUE;
