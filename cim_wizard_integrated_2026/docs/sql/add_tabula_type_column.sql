-- Run in pgAdmin against your CIM Wizard database
-- Adds tabula_type to building properties (Italian TABULA typology code)

ALTER TABLE cim_vector.cim_wizard_building_properties
    ADD COLUMN IF NOT EXISTS tabula_type VARCHAR(50);

COMMENT ON COLUMN cim_vector.cim_wizard_building_properties.tabula_type IS
    'TABULA typology code derived from construction period + usage, e.g. IT.RES.TABULA_5';

-- Optional: index for filtering by typology in analytics queries
CREATE INDEX IF NOT EXISTS idx_cim_wizard_bp_tabula_type
    ON cim_vector.cim_wizard_building_properties (tabula_type)
    WHERE tabula_type IS NOT NULL;
