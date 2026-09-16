-- =============================================================================
-- Italian TABULA construction catalog (Politecnico di Torino DENER)
-- Source: cim-database/materiale-tabula/materiale tabula/
--
-- Maps:
--   TABULA_Codici_costruzioni.xlsx  → building_class, period, archetype,
--                                     envelope_slot, archetype_component
--   {Wall,Roof,Floor,Ceiling}_*.xlsx
--       Caratteristiche componente  → construction, construction_layer,
--                                     construction_thermal
--       Materiali                   → material_category, material
--       Dati                        → construction_thermal (U, Y, U_periodic)
--
-- 32 archetypes (SFH/TH/MFH/AB × 8 periods) × up to 7 envelope slots
-- 46 unique construction codes (20 wall, 10 floor, 9 ceiling, 7 roof)
--
-- Apply:
--   psql -U cim_wizard_user -d cim_wizard_integrated \
--        -f migrations/create_tabula_schema.sql
-- =============================================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS cim_tabula;

COMMENT ON SCHEMA cim_tabula IS
    'Italian TABULA reference catalog: archetypes, constructions, layers, materials (UNI EN ISO 13786 / 13788)';

-- ---------------------------------------------------------------------------
-- 1) Lookups
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS cim_tabula.building_class (
    class_code      VARCHAR(8) PRIMARY KEY,     -- SFH | TH | MFH | AB
    name_en         VARCHAR(80) NOT NULL,
    name_it         VARCHAR(80) NOT NULL,
    sort_order      SMALLINT NOT NULL
);

COMMENT ON TABLE cim_tabula.building_class IS
    'TABULA residential building classes used as the prefix of Codice ed.';

INSERT INTO cim_tabula.building_class (class_code, name_en, name_it, sort_order) VALUES
    ('SFH', 'Single-family house',  'Casa unifamiliare',           1),
    ('TH',  'Terraced house',       'Casa a schiera',              2),
    ('MFH', 'Multi-family house',   'Casa plurifamiliare',         3),
    ('AB',  'Apartment block',      'Edificio in linea / blocco',  4)
ON CONFLICT (class_code) DO NOTHING;


CREATE TABLE IF NOT EXISTS cim_tabula.construction_period (
    period_suffix       CHAR(2) PRIMARY KEY,        -- '01' … '08'
    epoca               VARCHAR(40) NOT NULL,       -- catalog "Epoca" label
    year_from           INTEGER,                    -- inclusive; NULL = open
    year_to             INTEGER,                    -- inclusive; NULL = open
    const_tabula        VARCHAR(16) NOT NULL,       -- TABULA_1 … TABULA_8
    sort_order          SMALLINT NOT NULL
);

COMMENT ON TABLE cim_tabula.construction_period IS
    'Eight TABULA construction epochs; suffix of Codice ed. (SFH_05 → 05).';
COMMENT ON COLUMN cim_tabula.construction_period.const_tabula IS
    'Matches cim_wizard_building_properties.const_tabula; _08 is TABULA_8 (post-2005).';

INSERT INTO cim_tabula.construction_period
    (period_suffix, epoca, year_from, year_to, const_tabula, sort_order) VALUES
    ('01', 'Fino al 1900',  NULL, 1900, 'TABULA_1', 1),
    ('02', '1901-1920',     1901, 1920, 'TABULA_2', 2),
    ('03', '1921-1945',     1921, 1945, 'TABULA_3', 3),
    ('04', '1946-1960',     1946, 1960, 'TABULA_4', 4),
    ('05', '1961-1975',     1961, 1975, 'TABULA_5', 5),
    ('06', '1976-1990',     1976, 1990, 'TABULA_6', 6),
    ('07', '1991-2005',     1991, 2005, 'TABULA_7', 7),
    ('08', 'Dopo il 2005',  2006, NULL, 'TABULA_8', 8)
ON CONFLICT (period_suffix) DO NOTHING;


CREATE TABLE IF NOT EXISTS cim_tabula.envelope_slot (
    slot_code           VARCHAR(16) PRIMARY KEY,    -- roof, ceiling, wall_1…
    catalog_header_it   VARCHAR(80) NOT NULL,       -- row 0 of Codici costruzioni
    sort_order          SMALLINT NOT NULL,
    typical_prefix      VARCHAR(16) NOT NULL        -- Roof_ | Ceiling_ | Wall_ | Floor_
);

COMMENT ON TABLE cim_tabula.envelope_slot IS
    'Envelope roles on a TABULA archetype row (Copertura, Parete1, Solaio1, …).';

INSERT INTO cim_tabula.envelope_slot (slot_code, catalog_header_it, sort_order, typical_prefix) VALUES
    ('roof',     'Copertura',                                          1, 'Roof_'),
    ('ceiling',  'Ultimo solaio (se sottotetto non risc.)',            2, 'Ceiling_'),
    ('wall_1',   'Parete1',                                            3, 'Wall_'),
    ('wall_2',   'Parete2',                                            4, 'Wall_'),
    ('wall_3',   'Parete3',                                            5, 'Wall_'),
    ('floor_1',  'Solaio1',                                            6, 'Floor_'),
    ('floor_2',  'Solaio2',                                            7, 'Floor_')
ON CONFLICT (slot_code) DO NOTHING;


CREATE TABLE IF NOT EXISTS cim_tabula.component_type (
    type_code           VARCHAR(40) PRIMARY KEY,
    name_it             VARCHAR(80) NOT NULL,       -- "Tipo di componente" in XLS
    element_kind        VARCHAR(16) NOT NULL,       -- wall | roof | floor | ceiling
    CONSTRAINT chk_component_element_kind
        CHECK (element_kind IN ('wall', 'roof', 'floor', 'ceiling'))
);

COMMENT ON TABLE cim_tabula.component_type IS
    'UNI component class from Caratteristiche componente!D2.';

INSERT INTO cim_tabula.component_type (type_code, name_it, element_kind) VALUES
    ('vertical_envelope',        'Chiusura verticale',                      'wall'),
    ('upper_envelope',           'Chiusura superiore',                      'roof'),
    ('lower_envelope',           'Chiusura orizzontale inferiore',          'floor'),
    ('external_floor_envelope',  'Chiusura orizzontale su spazi esterni',   'floor'),
    ('horizontal_partition',     'Partizione orizzontale',                  'ceiling')
ON CONFLICT (type_code) DO NOTHING;

-- ---------------------------------------------------------------------------
-- 2) Archetypes  (32 rows from TABULA_Codici_costruzioni.xlsx)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS cim_tabula.archetype (
    archetype_code      VARCHAR(16) PRIMARY KEY,    -- SFH_05, AB_08, …
    class_code          VARCHAR(8)  NOT NULL
                            REFERENCES cim_tabula.building_class (class_code),
    period_suffix       CHAR(2)     NOT NULL
                            REFERENCES cim_tabula.construction_period (period_suffix),
    CONSTRAINT uq_archetype_class_period UNIQUE (class_code, period_suffix)
);

COMMENT ON TABLE cim_tabula.archetype IS
    '32 Italian TABULA archetypes: 4 classes × 8 periods. PK = catalog "Codice ed."';

CREATE INDEX IF NOT EXISTS idx_archetype_period
    ON cim_tabula.archetype (period_suffix);
CREATE INDEX IF NOT EXISTS idx_archetype_class
    ON cim_tabula.archetype (class_code);

-- ---------------------------------------------------------------------------
-- 3) Constructions  (46 unique Wall_*/Roof_*/Floor_*/Ceiling_* codes)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS cim_tabula.construction (
    construction_code   VARCHAR(32) PRIMARY KEY,    -- Wall_01.03, Roof_06.02, …
    element_kind        VARCHAR(16) NOT NULL,       -- wall | roof | floor | ceiling
    type_code           VARCHAR(40)
                            REFERENCES cim_tabula.component_type (type_code),
    source_file         VARCHAR(80),                -- preferred workbook filename
    notes               TEXT,
    CONSTRAINT chk_construction_element_kind
        CHECK (element_kind IN ('wall', 'roof', 'floor', 'ceiling'))
);

COMMENT ON TABLE cim_tabula.construction IS
    'One row per Politecnico DENER component workbook referenced by the catalog.';
COMMENT ON COLUMN cim_tabula.construction.source_file IS
    'Canonical XLS/XLSX in materiale-tabula (duplicates like Wall_01.07(1).xls ignored).';

CREATE INDEX IF NOT EXISTS idx_construction_kind
    ON cim_tabula.construction (element_kind);
CREATE INDEX IF NOT EXISTS idx_construction_type
    ON cim_tabula.construction (type_code);

-- ---------------------------------------------------------------------------
-- 4) Archetype → construction assignment (catalog cells)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS cim_tabula.archetype_component (
    archetype_code      VARCHAR(16) NOT NULL
                            REFERENCES cim_tabula.archetype (archetype_code)
                            ON DELETE CASCADE,
    slot_code           VARCHAR(16) NOT NULL
                            REFERENCES cim_tabula.envelope_slot (slot_code),
    construction_code   VARCHAR(32) NOT NULL
                            REFERENCES cim_tabula.construction (construction_code),
    catalog_description TEXT,                       -- "Descrizione" cell next to Codice
    PRIMARY KEY (archetype_code, slot_code)
);

COMMENT ON TABLE cim_tabula.archetype_component IS
    'Sparse assignment of constructions to archetype envelope slots (empty catalog cells omitted).';

CREATE INDEX IF NOT EXISTS idx_archetype_component_construction
    ON cim_tabula.archetype_component (construction_code);

-- ---------------------------------------------------------------------------
-- 5) Steady-state + dynamic thermal results
--     Caratteristiche componente (right-hand Parametro block) and sheet Dati
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS cim_tabula.construction_thermal (
    construction_code           VARCHAR(32) PRIMARY KEY
                                    REFERENCES cim_tabula.construction (construction_code)
                                    ON DELETE CASCADE,

    -- Surface film resistances (Strato liminare interno / esterno), m²K/W
    rsi                         DOUBLE PRECISION,   -- typically 0.13 (wall) / 0.10 (roof)
    rse                         DOUBLE PRECISION,   -- typically 0.04 (external) / 0.13 (internal)

    -- UNI EN ISO 13786 / 6946 scalars
    u_value                     DOUBLE PRECISION,   -- Trasmittanza U [W/m²K]  (Dati / Caratteristiche)
    u_value_from_r              DOUBLE PRECISION,   -- 1 / (R + Rsi + Rse) when R is layer-sum only
    thermal_resistance          DOUBLE PRECISION,   -- R [m²K/W]  Resistenza termica
    y_internal                  DOUBLE PRECISION,   -- Ammettenza termica interna Yii [W/m²K]
    y_external                  DOUBLE PRECISION,   -- Ammettenza termica esterna Yee [W/m²K]
    u_periodic                  DOUBLE PRECISION,   -- Trasmittanza periodica Yie [W/m²K]
    y_internal_phase_h          DOUBLE PRECISION,   -- Sfasamento Yii [h]
    y_external_phase_h          DOUBLE PRECISION,   -- Sfasamento Yee [h]
    u_periodic_phase_h          DOUBLE PRECISION,   -- Sfasamento Yie [h]
    areal_heat_capacity_int     DOUBLE PRECISION,   -- ki [kJ/m²K]
    areal_heat_capacity_ext     DOUBLE PRECISION,   -- ke [kJ/m²K]
    decrement_factor            DOUBLE PRECISION,   -- Fattore di attenuazione f [-]
    time_shift_h                DOUBLE PRECISION,   -- Sfasamento j [h]

    -- Geometry / mass of the opaque stack (excluding films)
    n_layers                    SMALLINT,
    total_thickness_m           DOUBLE PRECISION,   -- Spessore s [m]
    surface_mass_kg_m2          DOUBLE PRECISION,   -- Massa superficiale m [kg/m²]

    -- Hygrothermal summary from Glaser totals (optional)
    total_sd_m                  DOUBLE PRECISION,   -- Σ sd [m]
    frsi                        DOUBLE PRECISION,   -- fRsi temperature factor [-]
    condensation_risk           VARCHAR(16)         -- low | medium | high | unknown
);

COMMENT ON TABLE cim_tabula.construction_thermal IS
    'Per-construction U-value and ISO 13786 dynamic parameters from sheets Dati / Caratteristiche.';
COMMENT ON COLUMN cim_tabula.construction_thermal.u_value IS
    'Declared U from the DENER workbook (Dati!F4 / Caratteristiche N12).';
COMMENT ON COLUMN cim_tabula.construction_thermal.y_internal IS
    'Internal thermal admittance Yii [W/m²K].';
COMMENT ON COLUMN cim_tabula.construction_thermal.u_periodic IS
    'Periodic thermal transmittance Yie [W/m²K].';

-- ---------------------------------------------------------------------------
-- 6) Layer stack  (Caratteristiche componente stratigraphy, interior → exterior)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS cim_tabula.construction_layer (
    construction_code   VARCHAR(32) NOT NULL
                            REFERENCES cim_tabula.construction (construction_code)
                            ON DELETE CASCADE,
    layer_index         SMALLINT    NOT NULL,       -- 1 = innermost solid layer (Roman I)
    layer_roman         VARCHAR(8)  NOT NULL,       -- I … X
    name                VARCHAR(120) NOT NULL,      -- e.g. intonaco int.
    thickness_m         DOUBLE PRECISION,           -- s [cm] / 100
    density_kg_m3       DOUBLE PRECISION,           -- r  massa volumica
    mu                  DOUBLE PRECISION,           -- m  fattore di resistenza al vapore [-]
    specific_heat_j_kgk DOUBLE PRECISION,           -- c  [J/kgK]
    conductivity_w_mk   DOUBLE PRECISION,           -- l  λ [W/mK]
    thermal_resistance  DOUBLE PRECISION,           -- R  [m²K/W] if entered instead of λ
    r_from_lambda       BOOLEAN,                    -- catalog "opz. l→R"
    sd_m                DOUBLE PRECISION,           -- μ × s  (Glaser sd)
    PRIMARY KEY (construction_code, layer_index)
);

COMMENT ON TABLE cim_tabula.construction_layer IS
    'Opaque layers I–X from Caratteristiche componente (int→est). Surface films live on construction_thermal.';
COMMENT ON COLUMN cim_tabula.construction_layer.thickness_m IS
    'Converted from XLS column s [cm].';
COMMENT ON COLUMN cim_tabula.construction_layer.mu IS
    'Water-vapour resistance factor μ (ISO 13788).';

CREATE INDEX IF NOT EXISTS idx_construction_layer_name
    ON cim_tabula.construction_layer (name);

-- ---------------------------------------------------------------------------
-- 7) Shared material library  (sheet Materiali — identical across workbooks)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS cim_tabula.material_category (
    category_it         VARCHAR(80) PRIMARY KEY
);

INSERT INTO cim_tabula.material_category (category_it) VALUES
    ('Aria'),
    ('Calcestruzzo'),
    ('Carta, cartone e derivati'),
    ('Fibre minerali'),
    ('Intonaci e malte'),
    ('Laterizi'),
    ('Legnami'),
    ('Mastici per tenute'),
    ('Materiali per impermeabilizzazioni'),
    ('Materiali sfusi e di riempimento'),
    ('Materie plastiche cellulari'),
    ('Materie plastiche compatte'),
    ('Metalli'),
    ('Pannelli e lastre varie'),
    ('Porcellana'),
    ('Rocce naturali'),
    ('Silicato di calcio'),
    ('Vetro')
ON CONFLICT (category_it) DO NOTHING;


CREATE TABLE IF NOT EXISTS cim_tabula.material (
    material_id                 SERIAL PRIMARY KEY,
    category_it                 VARCHAR(80) NOT NULL
                                    REFERENCES cim_tabula.material_category (category_it),
    name_it                     VARCHAR(200) NOT NULL,
    density_kg_m3               DOUBLE PRECISION,   -- Massa volumica
    specific_heat_j_kgk         DOUBLE PRECISION,   -- Calore specifico
    conductivity_w_mk           DOUBLE PRECISION,   -- Conducibilità termica
    vapour_permeability         DOUBLE PRECISION,   -- Permeabilità al vapore
    mu                          DOUBLE PRECISION,   -- Fattore di resistenza al vapore
    CONSTRAINT uq_material_identity UNIQUE
        (category_it, name_it, density_kg_m3, conductivity_w_mk)
);

COMMENT ON TABLE cim_tabula.material IS
    'UNI material library from the Materiali sheet (~214 rows, shared by all component files).';

CREATE INDEX IF NOT EXISTS idx_material_name
    ON cim_tabula.material (name_it);
CREATE INDEX IF NOT EXISTS idx_material_category
    ON cim_tabula.material (category_it);

-- Optional fuzzy link from a layer name to a library material
ALTER TABLE cim_tabula.construction_layer
    ADD COLUMN IF NOT EXISTS material_id INTEGER
        REFERENCES cim_tabula.material (material_id);

-- ---------------------------------------------------------------------------
-- 8) Convenience view — one row per archetype × filled slot
--     (same grain as cim-database/tabula.csv)
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW cim_tabula.v_archetype_envelope AS
SELECT
    a.archetype_code,
    a.class_code,
    p.epoca,
    p.const_tabula,
    p.year_from,
    p.year_to,
    ac.slot_code,
    s.catalog_header_it     AS slot_label_it,
    ac.construction_code,
    c.element_kind,
    ct.name_it              AS component_type_it,
    ac.catalog_description,
    t.u_value,
    t.u_value_from_r,
    t.y_internal,
    t.y_external,
    t.u_periodic,
    t.n_layers,
    t.total_thickness_m,
    t.surface_mass_kg_m2,
    t.decrement_factor,
    t.time_shift_h,
    c.source_file
FROM cim_tabula.archetype a
JOIN cim_tabula.construction_period p
      ON p.period_suffix = a.period_suffix
JOIN cim_tabula.archetype_component ac
      ON ac.archetype_code = a.archetype_code
JOIN cim_tabula.envelope_slot s
      ON s.slot_code = ac.slot_code
JOIN cim_tabula.construction c
      ON c.construction_code = ac.construction_code
LEFT JOIN cim_tabula.component_type ct
      ON ct.type_code = c.type_code
LEFT JOIN cim_tabula.construction_thermal t
      ON t.construction_code = c.construction_code;

COMMENT ON VIEW cim_tabula.v_archetype_envelope IS
    'Denormalized archetype envelope: join of catalog slots with construction U / dynamic properties.';

COMMIT;
