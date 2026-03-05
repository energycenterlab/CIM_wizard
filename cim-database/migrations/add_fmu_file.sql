-- Add fmu_file column to cim_wizard_building_properties
-- Run manually: psql -U cim_wizard_user -d cim_wizard_integrated -h localhost -p 15432 -f add_fmu_file.sql

ALTER TABLE cim_vector.cim_wizard_building_properties
ADD COLUMN IF NOT EXISTS fmu_file VARCHAR(255);

COMMENT ON COLUMN cim_vector.cim_wizard_building_properties.fmu_file IS 'FMU file path or identifier';
