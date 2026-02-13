-- Quick SQL commands to restructure cim_vector.building table
-- Make building_id the primary key and drop the id column

-- BACKUP FIRST!
-- pg_dump -h localhost -p 5433 -U cim_wizard_user -t cim_vector.building cim_wizard_integrated > backup_building.sql

BEGIN;

-- 1. Ensure building_id has no NULLs
UPDATE cim_vector.building 
SET building_id = 'building_' || id::text 
WHERE building_id IS NULL;

-- 2. Remove duplicates if any (keep the one with the lowest id)
DELETE FROM cim_vector.building b1
USING cim_vector.building b2
WHERE b1.id > b2.id 
  AND b1.building_id = b2.building_id;

-- 3. Drop current primary key
ALTER TABLE cim_vector.building DROP CONSTRAINT building_pkey;

-- 4. Set building_id as NOT NULL and add primary key
ALTER TABLE cim_vector.building ALTER COLUMN building_id SET NOT NULL;
ALTER TABLE cim_vector.building ADD PRIMARY KEY (building_id);

-- 5. Drop the old id column
ALTER TABLE cim_vector.building DROP COLUMN id;

COMMIT;

-- Test the result
SELECT 'Restructure completed!' as status;
SELECT COUNT(*) as buildings_count FROM cim_vector.building;
SELECT COUNT(*) as joined_records 
FROM cim_vector.building b
INNER JOIN cim_vector.building_properties bp ON b.building_id = bp.building_id;
