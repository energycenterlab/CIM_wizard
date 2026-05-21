"""
03 — Run a full district energy simulation and store results back to CIM Wizard DB.

Pipeline
--------
  CIM Wizard DB
      ↓  02_cim_wizard_exporter.py
  SiteVertices.csv + BuildingInformation.csv
      ↓  CESAR-P + EnergyPlus
  Hourly/annual energy demand per building
      ↓  write_results_to_db()
  cim_simulation.building_energy_results (new schema)

Usage
-----
    export DATABASE_URL="postgresql://user:pass@localhost:5433/cim_wizard_integrated"

    python 03_run_district_simulation.py \
        --project_id  my_project \
        --scenario_id scenario_001 \
        --weather      ./data/weather/Florence.epw \
        --output_dir   ./output/my_project_scenario_001
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text


# ---------------------------------------------------------------------------
# Step 1 – Export from CIM Wizard
# ---------------------------------------------------------------------------
def _export(project_id: str, scenario_id: str, work_dir: Path) -> tuple[Path, Path]:
    from building_simulation.cim_wizard_exporter import export_to_cesarp  # noqa: F401
    # Re-use the exporter from step 02
    from importlib.util import spec_from_file_location, module_from_spec
    spec = spec_from_file_location("exporter", Path(__file__).parent / "02_cim_wizard_exporter.py")
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.export_to_cesarp(project_id, scenario_id, work_dir)


# ---------------------------------------------------------------------------
# Step 2 – Build CESAR-P config pointing to exported data & weather
# ---------------------------------------------------------------------------
def _build_config(work_dir: Path, weather_epw: Path) -> Path:
    import yaml  # pip install pyyaml

    config = {
        "MANAGER": {
            "BUILDING_OPERATION_FACTORY_CLASS": "cesarp.SIA2024.SIA2024Facade.SIA2024Facade",
            "SITE_VERTICES_FILE": {
                "PATH": str(work_dir / "SiteVertices.csv"),
                "LABELS": {"gis_fid": "TARGET_FID", "x": "SHAPE_X", "y": "SHAPE_Y"},
            },
            "BLDG_INFORMATION_FILE": {
                "PATH": str(work_dir / "BuildingInformation.csv"),
                "LABELS": {
                    "gis_fid": "EGID",
                    "height": "HEIGHT",
                    "floors_above_ground": "FLOORS_ABOVE_GROUND",
                    "year_of_construction": "YEAR_OF_CONSTRUCTION",
                    "neighbours": "NEIGHBOURS",
                },
            },
        },
        "SINGLE_SITE": {
            "WEATHER_FILE": str(weather_epw),
        },
        "SIA2024": {
            "BLDG_TYPE_PER_BLDG_FILE": {
                "PATH": str(work_dir / "BuildingInformation.csv"),
                "LABELS": {"gis_fid": "EGID", "sia_bldg_type": "SIA_BLDG_TYPE"},
            }
        },
    }

    config_path = work_dir / "run_config.yml"
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    return config_path


# ---------------------------------------------------------------------------
# Step 3 – Run CESAR-P simulation
# ---------------------------------------------------------------------------
def _run_cesarp(config_path: Path, output_dir: Path) -> pd.DataFrame:
    import cesarp.common
    from cesarp.manager.SimulationManager import SimulationManager

    output_dir.mkdir(parents=True, exist_ok=True)
    ureg = cesarp.common.init_unit_registry()
    mgr = SimulationManager(
        base_output_path=str(output_dir),
        main_config_path=str(config_path),
        unit_registry=ureg,
        fids_to_use=None,
        load_from_disk=False,
    )
    mgr.run_all_sims(include_neighborhood=True)
    return mgr.collect_all_results()


# ---------------------------------------------------------------------------
# Step 4 – Write results back to cim_simulation schema
# ---------------------------------------------------------------------------
CREATE_SCHEMA_SQL = "CREATE SCHEMA IF NOT EXISTS cim_simulation;"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS cim_simulation.building_energy_results (
    id                      SERIAL PRIMARY KEY,
    project_id              TEXT        NOT NULL,
    scenario_id             TEXT        NOT NULL,
    building_egid           INTEGER     NOT NULL,
    simulation_tool         TEXT        DEFAULT 'CESAR-P + EnergyPlus',
    heating_demand_kwh      DOUBLE PRECISION,
    cooling_demand_kwh      DOUBLE PRECISION,
    dhw_demand_kwh          DOUBLE PRECISION,
    electricity_demand_kwh  DOUBLE PRECISION,
    total_final_energy_kwh  DOUBLE PRECISION,
    co2_kg                  DOUBLE PRECISION,
    heating_intensity_kwh_m2 DOUBLE PRECISION,
    simulated_at            TIMESTAMPTZ DEFAULT now(),
    UNIQUE (project_id, scenario_id, building_egid)
);
"""


def write_results_to_db(
    results: pd.DataFrame,
    project_id: str,
    scenario_id: str,
    engine,
) -> None:
    with engine.begin() as conn:
        conn.execute(text(CREATE_SCHEMA_SQL))
        conn.execute(text(CREATE_TABLE_SQL))

    col_map = {
        "heating_demand_kWh":       "heating_demand_kwh",
        "cooling_demand_kWh":       "cooling_demand_kwh",
        "dhw_demand_kWh":           "dhw_demand_kwh",
        "electricity_demand_kWh":   "electricity_demand_kwh",
        "total_final_energy_kWh":   "total_final_energy_kwh",
        "CO2_kg":                   "co2_kg",
        "heating_demand_kWh_m2":    "heating_intensity_kwh_m2",
    }

    rows = []
    for egid, row in results.iterrows():
        record = {
            "project_id": project_id,
            "scenario_id": scenario_id,
            "building_egid": int(egid),
        }
        for src_col, dst_col in col_map.items():
            if src_col in row:
                record[dst_col] = float(row[src_col]) if row[src_col] is not None else None
        rows.append(record)

    insert_df = pd.DataFrame(rows)
    insert_df.to_sql(
        "building_energy_results",
        engine,
        schema="cim_simulation",
        if_exists="append",
        index=False,
        method="multi",
    )
    print(f"  Wrote {len(insert_df)} records to cim_simulation.building_energy_results")


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------
def run_full_pipeline(
    project_id: str,
    scenario_id: str,
    weather_epw: Path,
    output_dir: Path,
    database_url: str | None = None,
) -> pd.DataFrame:
    import os
    db_url = database_url or os.environ["DATABASE_URL"]
    engine = create_engine(db_url)

    work_dir = output_dir / "cesarp_inputs"

    print("=== Step 1: Export from CIM Wizard DB ===")
    _export(project_id, scenario_id, work_dir)

    print("\n=== Step 2: Build CESAR-P config ===")
    config_path = _build_config(work_dir, weather_epw)
    print(f"  Config → {config_path}")

    print("\n=== Step 3: Run CESAR-P (EnergyPlus) ===")
    sim_output = output_dir / "cesarp_output"
    results = _run_cesarp(config_path, sim_output)

    print("\n=== Step 4: Write results to DB ===")
    write_results_to_db(results, project_id, scenario_id, engine)

    # Also save CSV locally
    csv_path = output_dir / "annual_energy_results.csv"
    results.to_csv(csv_path)
    print(f"\nLocal CSV saved to: {csv_path}")

    # District summary
    if "total_final_energy_kWh" in results.columns:
        total = results["total_final_energy_kWh"].sum()
        avg_intensity = results.get("heating_demand_kWh_m2", pd.Series()).mean()
        print(f"\n{'='*50}")
        print(f"District total final energy : {total:,.0f} kWh/year")
        if not pd.isna(avg_intensity):
            print(f"Average heating intensity   : {avg_intensity:.1f} kWh/m²·a")
        print(f"{'='*50}")

    return results


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CIM Wizard → CESAR-P full district simulation.")
    parser.add_argument("--project_id",   required=True)
    parser.add_argument("--scenario_id",  required=True)
    parser.add_argument("--weather",      required=True, help="Path to .epw weather file")
    parser.add_argument("--output_dir",   default="./output/district_simulation")
    parser.add_argument("--database_url", default=None)
    args = parser.parse_args()

    run_full_pipeline(
        project_id=args.project_id,
        scenario_id=args.scenario_id,
        weather_epw=Path(args.weather),
        output_dir=Path(args.output_dir),
        database_url=args.database_url,
    )
