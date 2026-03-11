-- outputs schema: simulation output hypertables linked to building_properties
-- Runs after init_backup.sql (alphabetical: init < outputs)
-- Requires: TimescaleDB extension, cim_vector schema with cim_wizard_building_properties
--
-- NOTE: scenario_id and building_id are UUID in the actual database
--       (the SQLAlchemy models use String(100) for compatibility but the DB uses UUID)

CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE SCHEMA IF NOT EXISTS outputs;

-- ---------------------------------------------------------------------------
-- Simulation run metadata (step size, optional wall-clock start)
-- ---------------------------------------------------------------------------
CREATE TABLE outputs.simulation_run (
    project_id       VARCHAR(100) NOT NULL,
    scenario_id      UUID NOT NULL,
    step_size_ms     INTEGER NOT NULL,          -- e.g. 200, 600
    simulation_start TIMESTAMPTZ,               -- optional wall-clock start
    created_at       TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (project_id, scenario_id)
);

COMMENT ON TABLE  outputs.simulation_run IS 'Metadata per simulation run: step size and optional start time';
COMMENT ON COLUMN outputs.simulation_run.step_size_ms IS 'Duration of one time step in milliseconds';

-- ---------------------------------------------------------------------------
-- Building thermal output (building_frassinetto3)
-- ---------------------------------------------------------------------------
CREATE TABLE outputs.building_frassinetto3 (
    project_id          VARCHAR(100) NOT NULL,
    scenario_id         UUID NOT NULL,
    building_id         UUID NOT NULL,
    lod                 INTEGER NOT NULL DEFAULT 0,
    time_step           BIGINT NOT NULL,
    t_building          FLOAT,
    heating_load_target FLOAT,
    FOREIGN KEY (scenario_id, building_id, lod)
        REFERENCES cim_vector.cim_wizard_building_properties(scenario_id, building_id, lod)
);

SELECT create_hypertable('outputs.building_frassinetto3', 'time_step',
       chunk_time_interval => 10000);

COMMENT ON COLUMN outputs.building_frassinetto3.time_step           IS 'Simulation step index (0, 1, 2, …)';
COMMENT ON COLUMN outputs.building_frassinetto3.t_building          IS 'Building temperature (°C)';
COMMENT ON COLUMN outputs.building_frassinetto3.heating_load_target IS 'Heating load target (W)';

-- ---------------------------------------------------------------------------
-- Battery output
-- ---------------------------------------------------------------------------
CREATE TABLE outputs.battery (
    project_id   VARCHAR(100) NOT NULL,
    scenario_id  UUID NOT NULL,
    building_id  UUID NOT NULL,
    lod          INTEGER NOT NULL DEFAULT 0,
    time_step    BIGINT NOT NULL,
    i            FLOAT DEFAULT 0,
    v            FLOAT DEFAULT 0,
    soc          FLOAT DEFAULT 0,
    p_net_batt   FLOAT DEFAULT 0,
    FOREIGN KEY (scenario_id, building_id, lod)
        REFERENCES cim_vector.cim_wizard_building_properties(scenario_id, building_id, lod)
);

SELECT create_hypertable('outputs.battery', 'time_step',
       chunk_time_interval => 10000);

COMMENT ON COLUMN outputs.battery.time_step   IS 'Simulation step index (0, 1, 2, …)';
COMMENT ON COLUMN outputs.battery.i           IS 'Current of the battery (A)';
COMMENT ON COLUMN outputs.battery.v           IS 'Voltage (V)';
COMMENT ON COLUMN outputs.battery.soc         IS 'State of Charge (-)';
COMMENT ON COLUMN outputs.battery.p_net_batt  IS 'Actual power from/to battery (W)';

-- ---------------------------------------------------------------------------
-- Heating / heat-pump output (heating_frassinetto_hp2)
-- ---------------------------------------------------------------------------
CREATE TABLE outputs.heating_frassinetto_hp2 (
    project_id   VARCHAR(100) NOT NULL,
    scenario_id  UUID NOT NULL,
    building_id  UUID NOT NULL,
    lod          INTEGER NOT NULL DEFAULT 0,
    time_step    BIGINT NOT NULL,
    en_el        FLOAT DEFAULT 0,
    en_auxel     FLOAT DEFAULT 0,
    qt_return    FLOAT DEFAULT 0,
    cop          FLOAT DEFAULT 0,
    cr           FLOAT DEFAULT 0,
    FOREIGN KEY (scenario_id, building_id, lod)
        REFERENCES cim_vector.cim_wizard_building_properties(scenario_id, building_id, lod)
);

SELECT create_hypertable('outputs.heating_frassinetto_hp2', 'time_step',
       chunk_time_interval => 10000);

COMMENT ON COLUMN outputs.heating_frassinetto_hp2.time_step IS 'Simulation step index (0, 1, 2, …)';
COMMENT ON COLUMN outputs.heating_frassinetto_hp2.en_el     IS 'Sensible thermal power (W)';
COMMENT ON COLUMN outputs.heating_frassinetto_hp2.en_auxel  IS 'Electrical power (W)';
COMMENT ON COLUMN outputs.heating_frassinetto_hp2.qt_return IS 'Demand heat power (W)';
COMMENT ON COLUMN outputs.heating_frassinetto_hp2.cop       IS 'Coefficient of performance (-)';
COMMENT ON COLUMN outputs.heating_frassinetto_hp2.cr        IS 'Manipulated variable (-)';
