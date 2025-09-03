-- Direct SQL Commands to Update Existing Tables
-- Run these commands one by one in your PostgreSQL database

-- =============================================================================
-- STEP 1: Connect to your database
-- =============================================================================
-- psql -h localhost -p 5433 -U cim_wizard_user -d cim_wizard_integrated

-- =============================================================================
-- STEP 2: Prepare data (fix NULLs and ensure data consistency)
-- =============================================================================

-- Fix NULL values in lod columns
UPDATE cim_vector.building SET lod = 0 WHERE lod IS NULL;
UPDATE cim_vector.building_properties SET lod = 0 WHERE lod IS NULL;

-- Fix NULL values in project/scenario columns
UPDATE cim_vector.building_properties SET project_id = 'unknown_project' WHERE project_id IS NULL;
UPDATE cim_vector.building_properties SET scenario_id = 'unknown_scenario' WHERE scenario_id IS NULL;

-- =============================================================================
-- STEP 3: Remove duplicates (keep first occurrence)
-- =============================================================================

-- Remove duplicate buildings on (building_id, lod)
DELETE FROM cim_vector.building b1 
USING cim_vector.building b2 
WHERE b1.ctid > b2.ctid 
  AND b1.building_id = b2.building_id 
  AND b1.lod = b2.lod;

-- Remove duplicate building_properties on (building_id, lod, project_id, scenario_id)
DELETE FROM cim_vector.building_properties bp1
USING cim_vector.building_properties bp2
WHERE bp1.ctid > bp2.ctid
  AND bp1.building_id = bp2.building_id
  AND bp1.lod = bp2.lod  
  AND bp1.project_id = bp2.project_id
  AND bp1.scenario_id = bp2.scenario_id;

-- =============================================================================
-- STEP 4: Drop existing primary key constraints
-- =============================================================================

ALTER TABLE cim_vector.building DROP CONSTRAINT IF EXISTS building_pkey;
ALTER TABLE cim_vector.project_scenario DROP CONSTRAINT IF EXISTS project_scenario_pkey;
ALTER TABLE cim_vector.building_properties DROP CONSTRAINT IF EXISTS building_properties_pkey;

-- =============================================================================
-- STEP 5: Drop old id columns (if they exist)
-- =============================================================================

ALTER TABLE cim_vector.building DROP COLUMN IF EXISTS id;
ALTER TABLE cim_vector.building_properties DROP COLUMN IF EXISTS id;

-- =============================================================================
-- STEP 6: Set columns as NOT NULL (required for primary keys)
-- =============================================================================

-- Building table
ALTER TABLE cim_vector.building ALTER COLUMN building_id SET NOT NULL;
ALTER TABLE cim_vector.building ALTER COLUMN lod SET NOT NULL;

-- Project_scenario table
ALTER TABLE cim_vector.project_scenario ALTER COLUMN project_id SET NOT NULL;
ALTER TABLE cim_vector.project_scenario ALTER COLUMN scenario_id SET NOT NULL;

-- Building_properties table
ALTER TABLE cim_vector.building_properties ALTER COLUMN building_id SET NOT NULL;
ALTER TABLE cim_vector.building_properties ALTER COLUMN lod SET NOT NULL;
ALTER TABLE cim_vector.building_properties ALTER COLUMN project_id SET NOT NULL;
ALTER TABLE cim_vector.building_properties ALTER COLUMN scenario_id SET NOT NULL;

-- =============================================================================
-- STEP 7: Create new composite primary keys
-- =============================================================================

-- Building: (building_id, lod)
ALTER TABLE cim_vector.building ADD PRIMARY KEY (building_id, lod);

-- Project_scenario: (project_id, scenario_id)
ALTER TABLE cim_vector.project_scenario ADD PRIMARY KEY (project_id, scenario_id);

-- Building_properties: (building_id, lod, project_id, scenario_id)
ALTER TABLE cim_vector.building_properties ADD PRIMARY KEY (building_id, lod, project_id, scenario_id);

-- =============================================================================
-- STEP 8: Add foreign key constraints
-- =============================================================================

-- BuildingProperties references Building (building_id, lod)
ALTER TABLE cim_vector.building_properties 
ADD CONSTRAINT fk_building_properties_building 
FOREIGN KEY (building_id, lod) 
REFERENCES cim_vector.building(building_id, lod)
ON DELETE CASCADE ON UPDATE CASCADE;

-- BuildingProperties references ProjectScenario (project_id, scenario_id)
ALTER TABLE cim_vector.building_properties 
ADD CONSTRAINT fk_building_properties_project_scenario 
FOREIGN KEY (project_id, scenario_id) 
REFERENCES cim_vector.project_scenario(project_id, scenario_id)
ON DELETE CASCADE ON UPDATE CASCADE;

-- =============================================================================
-- STEP 9: Verification queries
-- =============================================================================

-- Check table structures
\d cim_vector.building
\d cim_vector.project_scenario  
\d cim_vector.building_properties

-- Test data integrity
SELECT COUNT(*) as total_buildings FROM cim_vector.building;
SELECT COUNT(*) as total_scenarios FROM cim_vector.project_scenario;
SELECT COUNT(*) as total_properties FROM cim_vector.building_properties;

-- Test the join that was failing before
SELECT COUNT(*) as residential_buildings_with_geometry
FROM cim_vector.building AS b
INNER JOIN cim_vector.building_properties AS bp 
    ON b.building_id = bp.building_id AND b.lod = bp.lod
WHERE bp.filter_res = TRUE;

SELECT 'Schema update completed successfully!' as status;
