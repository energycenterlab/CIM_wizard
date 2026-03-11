-- Add outputs schema with TimescaleDB hypertables
-- For existing databases (where init scripts have already run)
-- Run: psql -U cim_wizard_user -d cim_wizard_integrated -h localhost -p 15432 -f add_outputs_schema.sql
--
-- NOTE: scenario_id and building_id are UUID to match cim_wizard_building_properties

CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE SCHEMA IF NOT EXISTS outputs;

-- Simulation run metadata
CREATE TABLE IF NOT EXISTS outputs.simulation_run (
    project_id       VARCHAR(100) NOT NULL,
    scenario_id      UUID NOT NULL,
    step_size_ms     INTEGER NOT NULL,
    simulation_start TIMESTAMPTZ,
    created_at       TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (project_id, scenario_id)
);

-- Building thermal output
CREATE TABLE IF NOT EXISTS outputs.building_frassinetto3 (
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
       chunk_time_interval => 10000, if_not_exists => TRUE);

-- Battery output
CREATE TABLE IF NOT EXISTS outputs.battery (
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
       chunk_time_interval => 10000, if_not_exists => TRUE);

-- Heating / heat-pump output
CREATE TABLE IF NOT EXISTS outputs.heating_frassinetto_hp2 (
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
       chunk_time_interval => 10000, if_not_exists => TRUE);

-- Column comments
COMMENT ON COLUMN outputs.building_frassinetto3.time_step           IS 'Simulation step index (0, 1, 2, …)';
COMMENT ON COLUMN outputs.building_frassinetto3.t_building          IS 'Building temperature (°C)';
COMMENT ON COLUMN outputs.building_frassinetto3.heating_load_target IS 'Heating load target (W)';

COMMENT ON COLUMN outputs.battery.time_step   IS 'Simulation step index (0, 1, 2, …)';
COMMENT ON COLUMN outputs.battery.i           IS 'Current of the battery (A)';
COMMENT ON COLUMN outputs.battery.v           IS 'Voltage (V)';
COMMENT ON COLUMN outputs.battery.soc         IS 'State of Charge (-)';
COMMENT ON COLUMN outputs.battery.p_net_batt  IS 'Actual power from/to battery (W)';

COMMENT ON COLUMN outputs.heating_frassinetto_hp2.time_step IS 'Simulation step index (0, 1, 2, …)';
COMMENT ON COLUMN outputs.heating_frassinetto_hp2.en_el     IS 'Sensible thermal power (W)';
COMMENT ON COLUMN outputs.heating_frassinetto_hp2.en_auxel  IS 'Electrical power (W)';
COMMENT ON COLUMN outputs.heating_frassinetto_hp2.qt_return IS 'Demand heat power (W)';
COMMENT ON COLUMN outputs.heating_frassinetto_hp2.cop       IS 'Coefficient of performance (-)';
COMMENT ON COLUMN outputs.heating_frassinetto_hp2.cr        IS 'Manipulated variable (-)';

COMMENT ON TABLE  outputs.simulation_run IS 'Metadata per simulation run: step size and optional start time';
COMMENT ON COLUMN outputs.simulation_run.step_size_ms IS 'Duration of one time step in milliseconds';
