-- Migration: grid_id on project_scenario, rename network_scenarios.scenario_id -> grid_id,
--            add z_value + building_name to cim_wizard_building,
--            create cim_vector.pv table
--
-- Run on existing DB:
--   psql -U cim_wizard_user -d cim_wizard_integrated -h localhost -p 15432 \
--        -f migrations/add_grid_id_building_cols_pv_table.sql

BEGIN;

-- =========================================================================
-- 1) Rename network_scenarios.scenario_id -> grid_id
--    Must drop dependent FKs first, rename, then re-create FKs
-- =========================================================================

-- Drop FKs that reference network_scenarios.scenario_id
ALTER TABLE cim_network.scenario_buses
    DROP CONSTRAINT IF EXISTS scenario_buses_scenario_id_fkey;
ALTER TABLE cim_network.scenario_lines
    DROP CONSTRAINT IF EXISTS scenario_lines_scenario_id_fkey;

-- Rename PK column in network_scenarios
ALTER TABLE cim_network.network_scenarios
    RENAME COLUMN scenario_id TO grid_id;

-- Rename FK columns in junction tables
ALTER TABLE cim_network.scenario_buses
    RENAME COLUMN scenario_id TO grid_id;
ALTER TABLE cim_network.scenario_lines
    RENAME COLUMN scenario_id TO grid_id;

-- Re-create FKs pointing to the renamed column
ALTER TABLE cim_network.scenario_buses
    ADD CONSTRAINT scenario_buses_grid_id_fkey
    FOREIGN KEY (grid_id) REFERENCES cim_network.network_scenarios(grid_id);
ALTER TABLE cim_network.scenario_lines
    ADD CONSTRAINT scenario_lines_grid_id_fkey
    FOREIGN KEY (grid_id) REFERENCES cim_network.network_scenarios(grid_id);

-- =========================================================================
-- 2) Add grid_id to cim_vector.cim_wizard_project_scenario
--    Nullable UUID, FK to cim_network.network_scenarios(grid_id)
-- =========================================================================

ALTER TABLE cim_vector.cim_wizard_project_scenario
    ADD COLUMN IF NOT EXISTS grid_id UUID;

ALTER TABLE cim_vector.cim_wizard_project_scenario
    ADD CONSTRAINT project_scenario_grid_id_fkey
    FOREIGN KEY (grid_id)
    REFERENCES cim_network.network_scenarios(grid_id)
    ON UPDATE CASCADE ON DELETE SET NULL;

COMMENT ON COLUMN cim_vector.cim_wizard_project_scenario.grid_id
    IS 'Optional reference to a network/grid scenario in cim_network';

-- =========================================================================
-- 3) Add z_value and building_name to cim_vector.cim_wizard_building
-- =========================================================================

ALTER TABLE cim_vector.cim_wizard_building
    ADD COLUMN IF NOT EXISTS z_value DOUBLE PRECISION;

ALTER TABLE cim_vector.cim_wizard_building
    ADD COLUMN IF NOT EXISTS building_name VARCHAR(100);

COMMENT ON COLUMN cim_vector.cim_wizard_building.z_value
    IS 'DTM height at building footprint — floor level (m)';
COMMENT ON COLUMN cim_vector.cim_wizard_building.building_name
    IS 'User-friendly building label (e.g. BUI-0001)';

ALTER TABLE cim_vector.cim_wizard_building
    ADD COLUMN IF NOT EXISTS pv_ids UUID[] DEFAULT '{}';

COMMENT ON COLUMN cim_vector.cim_wizard_building.pv_ids
    IS 'List of pv_id UUIDs from cim_vector.pv assigned to this building (denormalized reverse lookup)';

CREATE INDEX IF NOT EXISTS cim_wizard_building_pv_ids_gin_idx
    ON cim_vector.cim_wizard_building USING GIN (pv_ids);

-- =========================================================================
-- 4) Create cim_vector.pv table
--    One building can have many PV polygons (roof segments)
-- =========================================================================

CREATE TABLE IF NOT EXISTS cim_vector.pv (
    pv_id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    building_id    UUID NOT NULL,
--    fid            BIGINT,
    slope          DOUBLE PRECISION,
    num            DOUBLE PRECISION,
    area_reale     DOUBLE PRECISION,
    number         INTEGER,
    s              DOUBLE PRECISION,
    index_righ     BIGINT,
    id_pod         DOUBLE PRECISION,
    pv_geometry    geometry(MultiPolygon, 4326) NOT NULL,
    created_at     TIMESTAMPTZ DEFAULT now(),
    updated_at     TIMESTAMPTZ DEFAULT now(),

    CONSTRAINT pv_building_fk
        FOREIGN KEY (building_id)
        REFERENCES cim_vector.cim_wizard_building(building_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS pv_geom_gix
    ON cim_vector.pv USING GIST (pv_geometry);

CREATE INDEX IF NOT EXISTS pv_building_id_idx
    ON cim_vector.pv (building_id);

COMMENT ON TABLE  cim_vector.pv IS 'PV-suitable roof polygon segments, each linked to a building';
COMMENT ON COLUMN cim_vector.pv.slope      IS 'Roof slope (degrees)';
COMMENT ON COLUMN cim_vector.pv.area_reale IS 'Real surface area of PV polygon (m²)';
COMMENT ON COLUMN cim_vector.pv.s          IS 'Module area capacity (m²)';
COMMENT ON COLUMN cim_vector.pv.id_pod     IS 'Point of Delivery identifier';

COMMIT;
