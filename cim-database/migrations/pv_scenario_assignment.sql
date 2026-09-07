-- ---------------------------------------------------------------------------
-- Migration: make PV assignment scenario-scoped
-- ---------------------------------------------------------------------------
--
-- Before: cim_vector.pv.building_id held a single owning building, so a PV
-- polygon could only ever belong to one building and there was no way to tell
-- which scenario had claimed it.
--
-- After:
--   1. cim_vector.pv.scenario_id            uuid[]  -- scenarios using this PV
--   2. cim_wizard_project_scenario.pv_assigned boolean -- has PV been assigned?
--   3. cim_wizard_building_properties.pv    uuid[]  -- PVs on this footprint
--
-- The building link moves from cim_vector.pv to
-- cim_wizard_building_properties.pv, which is already keyed by
-- (scenario_id, building_id, lod) and is therefore scenario-aware.
--
-- Apply with pgAdmin, or:
--   psql -h 130.192.238.11 -p 15432 -U cim_wizard_user \
--        -d cim_wizard_integrated -f pv_scenario_assignment.sql
--
-- NOTE: this drops cim_vector.pv.building_id, discarding the 6056 existing
-- single-building assignments.  Re-run POST /api/v1/building/assign_pv for
-- each scenario afterwards to repopulate.
-- ---------------------------------------------------------------------------

BEGIN;

-- =========================================================================
-- 1) cim_vector.pv : building_id -> scenario_id uuid[]
-- =========================================================================

ALTER TABLE cim_vector.pv
    ADD COLUMN IF NOT EXISTS scenario_id UUID[];

COMMENT ON COLUMN cim_vector.pv.scenario_id
    IS 'Scenarios (cim_wizard_project_scenario.scenario_id) that have claimed '
       'this PV polygon. NULL when the polygon is not used by any scenario.';

-- building_id had an index but no FK on the live DB; drop both defensively.
DROP INDEX IF EXISTS cim_vector.pv_building_id_idx;

ALTER TABLE cim_vector.pv
    DROP CONSTRAINT IF EXISTS pv_building_fk;

ALTER TABLE cim_vector.pv
    DROP COLUMN IF EXISTS building_id;

CREATE INDEX IF NOT EXISTS pv_scenario_id_gin_idx
    ON cim_vector.pv USING GIN (scenario_id);

-- =========================================================================
-- 2) cim_wizard_project_scenario.pv_assigned
-- =========================================================================

ALTER TABLE cim_vector.cim_wizard_project_scenario
    ADD COLUMN IF NOT EXISTS pv_assigned BOOLEAN NOT NULL DEFAULT FALSE;

COMMENT ON COLUMN cim_vector.cim_wizard_project_scenario.pv_assigned
    IS 'TRUE once assign_pv has run for this project-scenario.';

-- =========================================================================
-- 3) cim_wizard_building_properties.pv
-- =========================================================================

ALTER TABLE cim_vector.cim_wizard_building_properties
    ADD COLUMN IF NOT EXISTS pv UUID[];

COMMENT ON COLUMN cim_vector.cim_wizard_building_properties.pv
    IS 'pv_id list from cim_vector.pv matched to this building footprint by '
       'offset spatial join. NULL when no PV polygon was matched.';

CREATE INDEX IF NOT EXISTS cim_wizard_building_properties_pv_gin_idx
    ON cim_vector.cim_wizard_building_properties USING GIN (pv);

-- =========================================================================
-- 4) Geography indexes for the offset spatial join
--    PV polygons are digitised from roofprints, so they overhang the
--    footprints and the join needs a metric tolerance.  ST_DWithin on the
--    geography cast can only use an index if that cast is indexed.
-- =========================================================================

CREATE INDEX IF NOT EXISTS pv_geom_geog_gix
    ON cim_vector.pv USING GIST ((pv_geometry::geography));

CREATE INDEX IF NOT EXISTS cim_wizard_building_geom_geog_gix
    ON cim_vector.cim_wizard_building USING GIST ((building_geometry::geography));

COMMIT;


-- ---------------------------------------------------------------------------
-- OPTIONAL cleanup -- run separately, only when you are happy with the above.
--
-- cim_wizard_building.pv_ids is now superseded by
-- cim_wizard_building_properties.pv: it is building-level, so it cannot
-- represent per-scenario assignments.  The application no longer writes it,
-- so its current contents will go stale.
--
-- Either clear it and keep the column:
--
--   UPDATE cim_vector.cim_wizard_building SET pv_ids = NULL;
--
-- or drop it outright:
--
--   DROP INDEX IF EXISTS cim_vector.cim_wizard_building_pv_ids_gin_idx;
--   ALTER TABLE cim_vector.cim_wizard_building DROP COLUMN IF EXISTS pv_ids;
--
-- If you drop it, also remove the `pv_ids` column from
-- app/models/vector.py::Building.
-- ---------------------------------------------------------------------------
