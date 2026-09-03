-- ---------------------------------------------------------------------------
-- Register the Energy ADE 2.0 feature classes in citydb.objectclass
-- ---------------------------------------------------------------------------
--
-- init-db/energy_ade_2.sql creates all ng2_* tables but does NOT register the
-- ADE (that is normally done by the 3DCityDB Importer/Exporter ADE Manager).
-- As a result citydb.ade is empty and there is no ThermalZone objectclass, so
-- ng2_building_partition.objectclass_id -- which has an enforced FK to
-- objectclass -- has to stay NULL.
--
-- This migration is OPTIONAL.  The mapper works without it: it resolves the
-- objectclass id at runtime and leaves the ADE column NULL when unregistered.
-- Applying it makes the thermal zones properly typed and lets the 3DCityDB
-- Importer/Exporter round-trip them as CityGML Energy ADE features.
--
-- The ids below start at 26100, well clear of the highest id currently used
-- by the installed schema (1600).
--
-- Apply with:
--   psql -h <host> -p 15432 -U cim_wizard_user -d cim_wizard_integrated \
--        -f register_energy_ade_objectclasses.sql
-- ---------------------------------------------------------------------------

BEGIN;

-- 1) ADE registry entry
INSERT INTO citydb.ade (id, name, description, version)
VALUES (1, 'CityGML Energy ADE', 'CityGML Energy ADE 2.0 (beta 7)', '2.0')
ON CONFLICT (id) DO NOTHING;

-- 2) XML namespace for the ADE
INSERT INTO citydb.namespace (id, alias, namespace, ade_id)
VALUES (26100, 'energy', 'http://www.sig3d.org/citygml/2.0/energy/2.0', 1)
ON CONFLICT (id) DO NOTHING;

-- 3) Feature classes used by the LoD 1.2 mapper
INSERT INTO citydb.objectclass
    (id, superclass_id, classname, is_abstract, is_toplevel, ade_id, namespace_id)
VALUES
    (26100, NULL, 'energy:ThermalZone',      0, 0, 1, 26100),
    (26101, NULL, 'energy:ThermalBoundary',  0, 0, 1, 26100),
    (26102, NULL, 'energy:ThermalOpening',   0, 0, 1, 26100),
    (26103, NULL, 'energy:UsageZone',        0, 0, 1, 26100)
ON CONFLICT (id) DO NOTHING;

COMMIT;

-- Backfill objectclass_id on any zones written before registration.
UPDATE citydb.ng2_building_partition p
SET    objectclass_id = 26100
FROM   citydb.cityobject co
WHERE  co.id = p.id
  AND  p.objectclass_id IS NULL
  AND  co.objectclass_id = 26100;
