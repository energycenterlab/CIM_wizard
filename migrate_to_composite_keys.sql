-- SQL Migration Script: Convert to Composite Primary Keys
-- Building: (building_id, lod) as PK
-- ProjectScenario: (project_id, scenario_id) as PK  
-- BuildingProperties: (building_id, lod, project_id, scenario_id) as PK with FK constraints

-- CRITICAL: Backup your data first!
-- pg_dump -h localhost -p 5433 -U cim_wizard_user cim_wizard_integrated > backup_before_composite_keys.sql

BEGIN;

-- =============================================================================
-- STEP 1: Prepare data and handle NULLs
-- =============================================================================

-- Ensure no NULL values in future primary key columns
UPDATE cim_vector.building 
SET lod = 0 WHERE lod IS NULL;

UPDATE cim_vector.project_scenario 
SET project_id = 'default_project_' || (random() * 1000000)::int::text,
    scenario_id = 'default_scenario_' || (random() * 1000000)::int::text
WHERE project_id IS NULL OR scenario_id IS NULL;

UPDATE cim_vector.building_properties 
SET building_id = 'building_' || (random() * 1000000)::int::text
WHERE building_id IS NULL;

UPDATE cim_vector.building_properties 
SET lod = 0 WHERE lod IS NULL;

UPDATE cim_vector.building_properties 
SET project_id = 'unknown_project'
WHERE project_id IS NULL;

UPDATE cim_vector.building_properties 
SET scenario_id = 'unknown_scenario'
WHERE scenario_id IS NULL;

-- =============================================================================
-- STEP 2: Remove duplicates on composite keys
-- =============================================================================

-- Remove duplicate buildings (keep one with lowest id if exists, otherwise first one)
WITH building_duplicates AS (
    SELECT building_id, lod, 
           ROW_NUMBER() OVER (PARTITION BY building_id, lod ORDER BY created_at ASC) as rn
    FROM cim_vector.building
)
DELETE FROM cim_vector.building 
WHERE (building_id, lod) IN (
    SELECT building_id, lod FROM building_duplicates WHERE rn > 1
);

-- Remove duplicate project_scenarios
WITH scenario_duplicates AS (
    SELECT project_id, scenario_id,
           ROW_NUMBER() OVER (PARTITION BY project_id, scenario_id ORDER BY created_at ASC) as rn
    FROM cim_vector.project_scenario
)
DELETE FROM cim_vector.project_scenario 
WHERE (project_id, scenario_id) IN (
    SELECT project_id, scenario_id FROM scenario_duplicates WHERE rn > 1
);

-- Remove duplicate building_properties
WITH props_duplicates AS (
    SELECT building_id, lod, project_id, scenario_id,
           ROW_NUMBER() OVER (PARTITION BY building_id, lod, project_id, scenario_id ORDER BY created_at ASC) as rn
    FROM cim_vector.building_properties
)
DELETE FROM cim_vector.building_properties 
WHERE (building_id, lod, project_id, scenario_id) IN (
    SELECT building_id, lod, project_id, scenario_id FROM props_duplicates WHERE rn > 1
);

-- =============================================================================
-- STEP 3: Drop existing constraints and indexes
-- =============================================================================

-- Drop existing primary keys
ALTER TABLE cim_vector.building DROP CONSTRAINT IF EXISTS building_pkey;
ALTER TABLE cim_vector.project_scenario DROP CONSTRAINT IF EXISTS project_scenario_pkey;
ALTER TABLE cim_vector.building_properties DROP CONSTRAINT IF EXISTS building_properties_pkey;

-- Drop any existing foreign key constraints
ALTER TABLE cim_vector.building_properties DROP CONSTRAINT IF EXISTS building_properties_building_id_fkey;
ALTER TABLE cim_vector.building_properties DROP CONSTRAINT IF EXISTS building_properties_project_fkey;

-- =============================================================================
-- STEP 4: Create new composite primary keys
-- =============================================================================

-- Building: (building_id, lod) as composite PK
ALTER TABLE cim_vector.building ALTER COLUMN building_id SET NOT NULL;
ALTER TABLE cim_vector.building ALTER COLUMN lod SET NOT NULL;
ALTER TABLE cim_vector.building ADD PRIMARY KEY (building_id, lod);

-- ProjectScenario: (project_id, scenario_id) as composite PK  
ALTER TABLE cim_vector.project_scenario ALTER COLUMN project_id SET NOT NULL;
ALTER TABLE cim_vector.project_scenario ALTER COLUMN scenario_id SET NOT NULL;
ALTER TABLE cim_vector.project_scenario ADD PRIMARY KEY (project_id, scenario_id);

-- BuildingProperties: (building_id, lod, project_id, scenario_id) as composite PK
ALTER TABLE cim_vector.building_properties ALTER COLUMN building_id SET NOT NULL;
ALTER TABLE cim_vector.building_properties ALTER COLUMN lod SET NOT NULL;
ALTER TABLE cim_vector.building_properties ALTER COLUMN project_id SET NOT NULL;
ALTER TABLE cim_vector.building_properties ALTER COLUMN scenario_id SET NOT NULL;
ALTER TABLE cim_vector.building_properties ADD PRIMARY KEY (building_id, lod, project_id, scenario_id);

-- =============================================================================
-- STEP 5: Add foreign key constraints
-- =============================================================================

-- BuildingProperties references Building
ALTER TABLE cim_vector.building_properties 
ADD CONSTRAINT fk_building_properties_building 
FOREIGN KEY (building_id, lod) 
REFERENCES cim_vector.building(building_id, lod)
ON DELETE CASCADE ON UPDATE CASCADE;

-- BuildingProperties references ProjectScenario
ALTER TABLE cim_vector.building_properties 
ADD CONSTRAINT fk_building_properties_project_scenario 
FOREIGN KEY (project_id, scenario_id) 
REFERENCES cim_vector.project_scenario(project_id, scenario_id)
ON DELETE CASCADE ON UPDATE CASCADE;

-- =============================================================================
-- STEP 6: Verification and cleanup
-- =============================================================================

-- Check table structures
SELECT 'Building table structure:' as info;
\d cim_vector.building;

SELECT 'ProjectScenario table structure:' as info;
\d cim_vector.project_scenario;

SELECT 'BuildingProperties table structure:' as info;
\d cim_vector.building_properties;

-- Test data integrity
SELECT 'Testing data integrity:' as test;

SELECT 
    COUNT(*) as total_buildings
FROM cim_vector.building;

SELECT 
    COUNT(*) as total_scenarios
FROM cim_vector.project_scenario;

SELECT 
    COUNT(*) as total_properties
FROM cim_vector.building_properties;

-- Test joins
SELECT 
    COUNT(*) as valid_building_references
FROM cim_vector.building_properties bp
INNER JOIN cim_vector.building b 
    ON bp.building_id = b.building_id AND bp.lod = b.lod;

SELECT 
    COUNT(*) as valid_scenario_references  
FROM cim_vector.building_properties bp
INNER JOIN cim_vector.project_scenario ps
    ON bp.project_id = ps.project_id AND bp.scenario_id = ps.scenario_id;

-- Test residential buildings query
SELECT 
    COUNT(*) as residential_buildings_with_geometry
FROM cim_vector.building b
INNER JOIN cim_vector.building_properties bp 
    ON b.building_id = bp.building_id AND b.lod = bp.lod
WHERE bp.filter_res = TRUE;

COMMIT;

SELECT 'Migration to composite keys completed successfully!' as result;
