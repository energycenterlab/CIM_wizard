-- Add envelope_efficiency column to cim_wizard_building_properties
-- Run manually on existing databases: psql -U cim_wizard_user -d cim_wizard_integrated -f add_envelope_efficiency.sql

ALTER TABLE cim_vector.cim_wizard_building_properties
ADD COLUMN IF NOT EXISTS envelope_efficiency VARCHAR(20);

COMMENT ON COLUMN cim_vector.cim_wizard_building_properties.envelope_efficiency IS 'Envelope efficiency: low, medium, or high';
