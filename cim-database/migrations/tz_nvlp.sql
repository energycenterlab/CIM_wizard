CREATE TABLE IF NOT EXISTS cim_vector.thermal_zone (
    id              SERIAL PRIMARY KEY,
    thr_zone_id     VARCHAR(150) NOT NULL,          -- e.g. {building_id}__tz-F1-A1
    building_id     UUID NOT NULL,
    scenario_id     UUID NOT NULL,
    project_id      VARCHAR(100),
    lod             INTEGER NOT NULL DEFAULT 0,
    name            VARCHAR(150),                   -- optional display name
    type            VARCHAR(50),                    -- residential | commercial | non_residential_storage
    storey_index    INTEGER,                        -- -1 basement, 0 ground, 1..n
    apartment_index INTEGER,                        -- nullable
    geometry        geometry(GeometryZ, 4326),      -- MultiPolygonZ / PolyhedralSurfaceZ solid shell
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_thermal_zone_scenario_thr
        UNIQUE (scenario_id, thr_zone_id),
    CONSTRAINT fk_thermal_zone_building_props
        FOREIGN KEY (scenario_id, building_id, lod)
        REFERENCES cim_vector.cim_wizard_building_properties (scenario_id, building_id, lod)
        ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_thermal_zone_building
    ON cim_vector.thermal_zone (building_id);
CREATE INDEX IF NOT EXISTS idx_thermal_zone_scenario
    ON cim_vector.thermal_zone (scenario_id);
CREATE INDEX IF NOT EXISTS idx_thermal_zone_geom
    ON cim_vector.thermal_zone USING GIST (geometry);
COMMENT ON TABLE  cim_vector.thermal_zone IS 'LoD1.2 thermal zone solids (mixed-use / apartment zones)';
COMMENT ON COLUMN cim_vector.thermal_zone.thr_zone_id IS 'Stable business key from LoD1.2 generator';
COMMENT ON COLUMN cim_vector.thermal_zone.type IS 'usage: residential | commercial | non_residential_storage';
COMMENT ON COLUMN cim_vector.thermal_zone.geometry IS '3D zone shell (MultiPolygonZ of faces) in EPSG:4326';
-- ---------------------------------------------------------------------------
-- 2) TZ_PROPS  — EAV properties for thermal zones
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cim_vector.tz_props (
    id          SERIAL PRIMARY KEY,
    tz_id       INTEGER NOT NULL
                    REFERENCES cim_vector.thermal_zone (id) ON DELETE CASCADE,
    key         VARCHAR(100) NOT NULL,              -- e.g. volume_m3, u_roof, is_heated
    value       TEXT,                               -- store as text; cast in app
    unit        VARCHAR(40),                        -- e.g. m3, W/m2K, J/K
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_tz_props_tz_key UNIQUE (tz_id, key)
);
CREATE INDEX IF NOT EXISTS idx_tz_props_tz_id ON cim_vector.tz_props (tz_id);
CREATE INDEX IF NOT EXISTS idx_tz_props_key   ON cim_vector.tz_props (key);
COMMENT ON TABLE cim_vector.tz_props IS 'Flexible key/value properties for thermal zones (TABULA + simulation)';
-- ---------------------------------------------------------------------------
-- 3) ENVELOPE_COMPONENT  — wall / floor / roof / ground / window surfaces
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cim_vector.envelope_component (
    id               SERIAL PRIMARY KEY,
    thr_nvlp_com_id  VARCHAR(150) NOT NULL,         -- e.g. {building_id}__wall_F1_3
    tz_id            INTEGER
                         REFERENCES cim_vector.thermal_zone (id) ON DELETE CASCADE,
    -- nullable: roof (and some shared faces) may be building-level
    building_id      UUID NOT NULL,
    scenario_id      UUID NOT NULL,
    project_id       VARCHAR(100),
    lod              INTEGER NOT NULL DEFAULT 0,
    type             VARCHAR(50) NOT NULL,          -- WallSurface | RoofSurface | FloorSurface | GroundSurface | Window
    storey_label     VARCHAR(20),                   -- B | G | F1 | F2 ...
    azimuth          DOUBLE PRECISION,              -- degrees from North; NULL for non-walls
    tilt             DOUBLE PRECISION,              -- 90 wall, 0 roof/floor; NULL if unknown
    area             DOUBLE PRECISION,              -- m²
    geometry         geometry(PolygonZ, 4326),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_envelope_component_scenario_thr
        UNIQUE (scenario_id, thr_nvlp_com_id),
    CONSTRAINT fk_envelope_building_props
        FOREIGN KEY (scenario_id, building_id, lod)
        REFERENCES cim_vector.cim_wizard_building_properties (scenario_id, building_id, lod)
        ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_envelope_tz_id
    ON cim_vector.envelope_component (tz_id);
CREATE INDEX IF NOT EXISTS idx_envelope_building
    ON cim_vector.envelope_component (building_id);
CREATE INDEX IF NOT EXISTS idx_envelope_scenario
    ON cim_vector.envelope_component (scenario_id);
CREATE INDEX IF NOT EXISTS idx_envelope_type
    ON cim_vector.envelope_component (type);
CREATE INDEX IF NOT EXISTS idx_envelope_geom
    ON cim_vector.envelope_component USING GIST (geometry);
COMMENT ON TABLE  cim_vector.envelope_component IS 'LoD1.2 envelope faces (walls, floors, roofs, openings)';
COMMENT ON COLUMN cim_vector.envelope_component.tz_id IS 'Owning thermal zone; NULL for building-level roof etc.';
COMMENT ON COLUMN cim_vector.envelope_component.azimuth IS 'Wall azimuth [0,360); NULL for floor/roof/ground';
COMMENT ON COLUMN cim_vector.envelope_component.tilt IS 'Surface tilt degrees from horizontal';
-- ---------------------------------------------------------------------------
-- 4) NVLP_PROPS  — EAV properties for envelope components
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cim_vector.nvlp_props (
    id          SERIAL PRIMARY KEY,
    nvlp_id     INTEGER NOT NULL
                    REFERENCES cim_vector.envelope_component (id) ON DELETE CASCADE,
    key         VARCHAR(100) NOT NULL,              -- e.g. u_value_best, tabula_slot
    value       TEXT,
    unit        VARCHAR(40),                        -- e.g. W/m2K, m, m2K/W
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_nvlp_props_nvlp_key UNIQUE (nvlp_id, key)
);
CREATE INDEX IF NOT EXISTS idx_nvlp_props_nvlp_id ON cim_vector.nvlp_props (nvlp_id);
CREATE INDEX IF NOT EXISTS idx_nvlp_props_key     ON cim_vector.nvlp_props (key);
COMMENT ON TABLE cim_vector.nvlp_props IS 'Flexible key/value properties for envelope (TABULA U, layers, etc.)';
-- Optional: helpful views for debugging in pgAdmin
CREATE OR REPLACE VIEW cim_vector.v_thermal_zone_props AS
SELECT
    z.scenario_id,
    z.building_id,
    z.thr_zone_id,
    z.type,
    z.storey_index,
    p.key,
    p.value,
    p.unit
FROM cim_vector.thermal_zone z
LEFT JOIN cim_vector.tz_props p ON p.tz_id = z.id;
CREATE OR REPLACE VIEW cim_vector.v_envelope_props AS
SELECT
    e.scenario_id,
    e.building_id,
    e.thr_nvlp_com_id,
    e.type,
    e.azimuth,
    e.tilt,
    e.area,
    p.key,
    p.value,
    p.unit
FROM cim_vector.envelope_component e
LEFT JOIN cim_vector.nvlp_props p ON p.nvlp_id = e.id;