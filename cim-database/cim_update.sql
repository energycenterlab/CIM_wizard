CREATE TABLE cim_vector.nvlp_props (
    id                      SERIAL PRIMARY KEY,

    -- identity / links (ER: BUILDING + ENVELOPE_COMPONENT)
    building_id             UUID NOT NULL,
    lod                     INTEGER NOT NULL DEFAULT 0,
    -- scenario_id             UUID NOT NULL,
    -- project_id              VARCHAR(100),
    nvlp_cmpnt_id           UUID NOT NULL
        REFERENCES cim_vector.envelope_component (id) ON DELETE CASCADE,

    -- typed attributes from cim_tz_v1_t.sql NVLP_PROPS
    total_thickness       DOUBLE PRECISION,
    moc_total_thickness    VARCHAR(100),

    nvlp_area                 DOUBLE PRECISION,
    moc_nvlp_area              VARCHAR(100),

    u_value                 DOUBLE PRECISION,
    moc_u_value              VARCHAR(100),

    layers_list             TEXT,                 -- JSON text of layers
    moc_layers_list          VARCHAR(100),

    component_type          VARCHAR(50),
    moc_component_type       VARCHAR(100),

    storey_label            VARCHAR(20),
    moc_storey_label         VARCHAR(100),

    tabula_archetype_code   VARCHAR(20),
    moc_tabula_archetype_code VARCHAR(100),

    tabula_construction_code VARCHAR(50),
    moc_tabula_construction_code VARCHAR(100),

    n_layers                INTEGER,
    moc_n_layers             VARCHAR(100),

    u_value_best            DOUBLE PRECISION,
    moc_u_value_best         VARCHAR(100),

    y_internal              DOUBLE PRECISION,
    moc_y_internal           VARCHAR(100),

    y_external              DOUBLE PRECISION,
    moc_y_external           VARCHAR(100),

    u_periodic              DOUBLE PRECISION,
    moc_u_periodic           VARCHAR(100),

    azimuth                 DOUBLE PRECISION,
    moc_azimuth              VARCHAR(100),

    inclination_tilt        DOUBLE PRECISION,     -- ER name; = tilt
    moc_inclination_tilt     VARCHAR(100),

    boundary_condition      VARCHAR(40),
    moc_boundary_condition   VARCHAR(100),

    w2w_ratio               DOUBLE PRECISION,     -- glazing / wall ratio
    moc_w2w_ratio            VARCHAR(100),

    g_value                 DOUBLE PRECISION,
    moc_g_value              VARCHAR(100),

    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_nvlp_props_scenario_nvlp
        UNIQUE (scenario_id, nvlp_cmpnt_id),

    CONSTRAINT fk_nvlp_props_building_props
        FOREIGN KEY (scenario_id, building_id, lod)
        REFERENCES cim_vector.cim_wizard_building_properties (scenario_id, building_id, lod)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_nvlp_props_building
    ON cim_vector.nvlp_props (building_id);
CREATE INDEX IF NOT EXISTS idx_nvlp_props_nvlp_id
    ON cim_vector.nvlp_props (nvlp_id);
CREATE INDEX IF NOT EXISTS idx_nvlp_props_type
    ON cim_vector.nvlp_props (component_type);

COMMENT ON TABLE cim_vector.nvlp_props IS
  'Typed envelope properties (TABULA + geometry attrs); cm_* = method_recorder per value';
COMMENT ON COLUMN cim_vector.nvlp_props.cm_u_value_best IS
  'Method that produced u_value_best, e.g. tabula_dati | tabula_glaser | catalog_text';