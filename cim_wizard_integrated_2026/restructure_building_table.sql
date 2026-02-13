-- SQL Script to restructure cim_vector.building table
-- Drop the 'id' column and make 'building_id' the primary key

-- IMPORTANT: Backup your data first!
-- pg_dump -h localhost -p 5433 -U cim_wizard_user -t cim_vector.building cim_wizard_integrated > backup_building_table.sql

BEGIN;

-- Step 1: Check current table structure
SELECT 'Current building table structure:' as info;
\d cim_vector.building;

-- Step 2: Check for any foreign key constraints that reference building.id
SELECT 
    tc.constraint_name,
    tc.table_schema,
    tc.table_name,
    kcu.column_name,
    ccu.table_schema AS foreign_table_schema,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND ccu.table_schema = 'cim_vector'
    AND ccu.table_name = 'building'
    AND ccu.column_name = 'id';

-- Step 3: Drop any foreign key constraints that reference building.id
-- (Should be none based on our code cleanup, but this is a safety check)
-- Example: ALTER TABLE cim_vector.building_properties DROP CONSTRAINT IF EXISTS building_properties_building_fk_fkey;

-- Step 4: Check if building_id is unique (required for primary key)
SELECT 'Checking building_id uniqueness:' as info;
SELECT 
    building_id,
    COUNT(*) as count
FROM cim_vector.building
GROUP BY building_id
HAVING COUNT(*) > 1;

-- If there are duplicates, you need to fix them first!
-- Example fix for duplicates (keep the one with geometry):
/*
DELETE FROM cim_vector.building b1
USING cim_vector.building b2
WHERE b1.id > b2.id 
  AND b1.building_id = b2.building_id
  AND (b1.building_geometry IS NULL OR b2.building_geometry IS NOT NULL);
*/

-- Step 5: Ensure building_id is NOT NULL (required for primary key)
UPDATE cim_vector.building 
SET building_id = 'building_' || id::text 
WHERE building_id IS NULL;

-- Step 6: Drop the current primary key constraint
ALTER TABLE cim_vector.building DROP CONSTRAINT IF EXISTS building_pkey;

-- Step 7: Add NOT NULL constraint to building_id if not already present
ALTER TABLE cim_vector.building ALTER COLUMN building_id SET NOT NULL;

-- Step 8: Add primary key constraint to building_id
ALTER TABLE cim_vector.building ADD PRIMARY KEY (building_id);

-- Step 9: Drop the id column
ALTER TABLE cim_vector.building DROP COLUMN id;

-- Step 10: Verify the new structure
SELECT 'New building table structure:' as info;
\d cim_vector.building;

-- Step 11: Test the join to make sure it works
SELECT 'Testing join after restructure:' as test;
SELECT COUNT(*) as total_joined_records
FROM cim_vector.building b
INNER JOIN cim_vector.building_properties bp ON b.building_id = bp.building_id;

SELECT COUNT(*) as residential_buildings_with_geometry
FROM cim_vector.building b
INNER JOIN cim_vector.building_properties bp ON b.building_id = bp.building_id
WHERE bp.filter_res = TRUE;

COMMIT;

-- If everything looks good, you can run:
SELECT 'Restructure completed successfully!' as result;
