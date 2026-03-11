# CIM Database - PostgreSQL 15 + PostGIS + TimescaleDB

The database initializes from scripts in `init-db/` on **first startup** (alphabetical order).

## Quick Start

```bash
cd cim-database
docker compose -f docker-compose.cimdb.yml up --build -d
```

On first run the init scripts execute automatically:

1. `init_backup.sql` — restores the base schema (`cim_vector`, `cim_census`, etc.)
2. `outputs_schema.sql` — creates the `outputs` schema with TimescaleDB hypertables

## Requirements

- `init-db/init_backup.sql` – plain SQL backup from `pg_dump -F p`
- Create with: `pg_dump -U cim_wizard_user -d cim_wizard_integrated -F p -f init_backup.sql --no-owner --no-acl`

## Fresh Start (re-run init)

```bash
docker compose -f docker-compose.cimdb.yml down -v
docker compose -f docker-compose.cimdb.yml up --build -d
```

## Adding outputs schema to an existing database

If the database volume already exists, init scripts won't re-run.
Apply the migration manually:

```bash
psql -U cim_wizard_user -d cim_wizard_integrated -h localhost -p 15432 \
     -f migrations/add_outputs_schema.sql
```

## Outputs schema

The `outputs` schema stores simulation time-series data as TimescaleDB hypertables,
partitioned on `time_step` (BIGINT step index). Each row is linked to a building
scenario via FK to `cim_vector.cim_wizard_building_properties(scenario_id, building_id, lod)`.

| Table | Description |
|-------|-------------|
| `outputs.simulation_run` | Step size and optional start time per (project, scenario) |
| `outputs.building_frassinetto3` | Building thermal output (temperature, heating load) |
| `outputs.battery` | Battery output (current, voltage, SOC, power) |
| `outputs.heating_frassinetto_hp2` | Heat-pump output (thermal/electrical power, COP) |

## Connection

| Host      | Port  | Database              | User             | Password            |
|-----------|-------|-----------------------|------------------|---------------------|
| localhost | 15432 | cim_wizard_integrated | cim_wizard_user  | cim_wizard_password |
