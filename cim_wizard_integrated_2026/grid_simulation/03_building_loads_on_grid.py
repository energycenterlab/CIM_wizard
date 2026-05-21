"""
03 — Assign building energy simulation results as time-series loads on the grid.

This script connects the two sub-projects:
  • building_simulation/ → annual / hourly energy demand per building
  • grid_simulation/     → pandapower LV network

Pipeline
--------
  cim_simulation.building_energy_results  (written by 03_run_district_simulation.py)
      ↓  load_building_energy_results()
  Hourly building load profiles  →  normalised to peak
      ↓  assign_loads_to_network()
  pandapower time-series power flow (24 h)
      ↓  run_timeseries_powerflow()
  Results: voltage profiles, line loading, grid import/export per hour
      ↓  write_grid_results_to_db() / save CSV

Usage
-----
    export DATABASE_URL="postgresql://user:pass@localhost:5433/cim_wizard_integrated"

    python 03_building_loads_on_grid.py \
        --project_id  my_project \
        --scenario_id scenario_001 \
        --network     ./output/cim_network.json
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd
import pandapower as pp
from sqlalchemy import create_engine, text


# ---------------------------------------------------------------------------
# Load building energy results from DB
# ---------------------------------------------------------------------------

def load_building_energy_results(
    engine,
    project_id: str,
    scenario_id: str,
) -> pd.DataFrame:
    """
    Read annual energy demand from cim_simulation schema.
    Returns DataFrame indexed by building_egid.
    """
    sql = text("""
        SELECT
            building_egid,
            heating_demand_kwh,
            cooling_demand_kwh,
            electricity_demand_kwh,
            total_final_energy_kwh
        FROM cim_simulation.building_energy_results
        WHERE project_id   = :pid
          AND scenario_id  = :sid
        ORDER BY building_egid
    """)
    df = pd.read_sql(sql, engine, params={"pid": project_id, "sid": scenario_id})
    df = df.set_index("building_egid")
    return df


# ---------------------------------------------------------------------------
# Typical normalised load profiles (fraction of annual peak, 8760 hours)
# For a full simulation use measured SCADA profiles or BDEW standard profiles.
# ---------------------------------------------------------------------------

def _build_daily_profile_residential() -> np.ndarray:
    """Typical residential load profile (24 values, fraction of peak)."""
    return np.array([
        0.25, 0.20, 0.18, 0.18, 0.20, 0.30,
        0.50, 0.70, 0.75, 0.65, 0.60, 0.65,
        0.70, 0.65, 0.60, 0.60, 0.65, 0.80,
        0.95, 1.00, 0.90, 0.75, 0.60, 0.40,
    ])


def _build_daily_profile_office() -> np.ndarray:
    """Typical office load profile (24 values, fraction of peak)."""
    return np.array([
        0.10, 0.10, 0.10, 0.10, 0.10, 0.15,
        0.20, 0.50, 0.80, 0.95, 0.95, 0.90,
        0.85, 0.90, 0.90, 0.85, 0.60, 0.30,
        0.20, 0.15, 0.12, 0.10, 0.10, 0.10,
    ])


def _build_daily_pv_profile() -> np.ndarray:
    """Typical summer midday PV generation profile (fraction of peak kWp)."""
    return np.array([
        0.00, 0.00, 0.00, 0.00, 0.00, 0.02,
        0.10, 0.30, 0.55, 0.75, 0.90, 0.98,
        1.00, 0.98, 0.90, 0.75, 0.50, 0.20,
        0.05, 0.00, 0.00, 0.00, 0.00, 0.00,
    ])


# ---------------------------------------------------------------------------
# Assign building loads to network buses
# ---------------------------------------------------------------------------

def assign_loads_to_network(
    net: pp.pandapowerNet,
    energy_results: pd.DataFrame,
) -> dict[int, int]:
    """
    For each building in energy_results, find the matching pandapower load
    (by name convention "load_sp{egid}") and return a mapping of
    egid → pandapower load index.

    Buildings without a matching load are skipped with a warning.
    """
    egid_to_load_idx: dict[int, int] = {}
    for egid in energy_results.index:
        match = net.load[net.load["name"] == f"load_sp{egid}"]
        if match.empty:
            # Fallback: match by building egid in name
            match = net.load[net.load["name"].str.contains(str(egid), na=False)]
        if match.empty:
            print(f"  WARNING: no load found for building EGID {egid} — skipped.")
            continue
        egid_to_load_idx[egid] = match.index[0]
    return egid_to_load_idx


# ---------------------------------------------------------------------------
# 24-hour time-series power flow
# ---------------------------------------------------------------------------

def run_timeseries_powerflow(
    net: pp.pandapowerNet,
    energy_results: pd.DataFrame,
    egid_to_load_idx: dict[int, int],
    n_hours: int = 24,
) -> pd.DataFrame:
    """
    Run n_hours of power flow, scaling each building's load by its annual
    energy × hourly profile / 8760.

    Returns
    -------
    pd.DataFrame with per-hour grid metrics.
    """
    residential_profile = _build_daily_profile_residential()
    office_profile      = _build_daily_profile_office()

    records = []
    for hour in range(n_hours):
        # Scale each building load
        for egid, load_idx in egid_to_load_idx.items():
            row = energy_results.loc[egid]
            annual_elec_kwh = float(row.get("electricity_demand_kwh") or 0)
            # Peak hourly consumption = annual / 8760 * profile_peak_factor
            peak_kw = annual_elec_kwh / 8760 * 3.5  # ~3.5× average peak factor
            fraction = residential_profile[hour % 24]
            net.load.at[load_idx, "p_mw"] = peak_kw * fraction / 1000

        pp.runpp(net, verbose=False)

        r = {
            "hour": hour,
            "grid_import_kW":   net.res_ext_grid["p_mw"].iloc[0] * 1000,
            "grid_reactive_kVAR": net.res_ext_grid["q_mvar"].iloc[0] * 1000,
            "min_voltage_pu":   net.res_bus["vm_pu"].min(),
            "max_voltage_pu":   net.res_bus["vm_pu"].max(),
            "max_line_loading_pct": net.res_line["loading_percent"].max(),
            "total_load_kW":    net.res_load["p_mw"].sum() * 1000,
            "line_losses_kW":   net.res_line["pl_mw"].sum() * 1000,
        }
        records.append(r)

    ts_df = pd.DataFrame(records).set_index("hour")
    return ts_df


# ---------------------------------------------------------------------------
# Write grid results to cim_simulation schema
# ---------------------------------------------------------------------------

CREATE_GRID_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS cim_simulation.grid_powerflow_results (
    id                      SERIAL PRIMARY KEY,
    project_id              TEXT    NOT NULL,
    scenario_id             TEXT    NOT NULL,
    simulation_tool         TEXT    DEFAULT 'pandapower',
    hour                    INTEGER NOT NULL,
    grid_import_kw          DOUBLE PRECISION,
    min_voltage_pu          DOUBLE PRECISION,
    max_voltage_pu          DOUBLE PRECISION,
    max_line_loading_pct    DOUBLE PRECISION,
    total_load_kw           DOUBLE PRECISION,
    line_losses_kw          DOUBLE PRECISION,
    simulated_at            TIMESTAMPTZ DEFAULT now()
);
"""


def write_grid_results_to_db(
    ts_df: pd.DataFrame,
    project_id: str,
    scenario_id: str,
    engine,
) -> None:
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS cim_simulation;"))
        conn.execute(text(CREATE_GRID_TABLE_SQL))

    out = ts_df.reset_index().rename(columns={
        "grid_import_kW": "grid_import_kw",
        "min_voltage_pu": "min_voltage_pu",
        "max_voltage_pu": "max_voltage_pu",
        "max_line_loading_pct": "max_line_loading_pct",
        "total_load_kW": "total_load_kw",
        "line_losses_kW": "line_losses_kw",
    })
    out["project_id"]  = project_id
    out["scenario_id"] = scenario_id

    out.to_sql(
        "grid_powerflow_results",
        engine,
        schema="cim_simulation",
        if_exists="append",
        index=False,
        method="multi",
    )
    print(f"  Wrote {len(out)} hourly records to cim_simulation.grid_powerflow_results")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(
    project_id: str,
    scenario_id: str,
    network_json: Path,
    database_url: str | None = None,
) -> None:
    import os
    db_url = database_url or os.environ["DATABASE_URL"]
    engine = create_engine(db_url)

    print("Loading network …")
    net = pp.from_json(str(network_json))
    print(f"  {len(net.bus)} buses, {len(net.line)} lines, {len(net.load)} loads")

    print("Loading building energy results …")
    energy_results = load_building_energy_results(engine, project_id, scenario_id)
    print(f"  {len(energy_results)} buildings with energy results")

    print("Matching buildings to grid loads …")
    egid_map = assign_loads_to_network(net, energy_results)
    print(f"  {len(egid_map)} buildings matched to grid loads")

    print("Running 24-hour time-series power flow …")
    ts_df = run_timeseries_powerflow(net, energy_results, egid_map)

    print("\n=== 24-hour grid summary ===")
    print(ts_df.round(3).to_string())

    print("\nKey grid metrics:")
    print(f"  Peak grid import      : {ts_df['grid_import_kW'].max():.1f} kW (hour {ts_df['grid_import_kW'].idxmax()})")
    print(f"  Min voltage           : {ts_df['min_voltage_pu'].min():.4f} pu")
    print(f"  Max line loading      : {ts_df['max_line_loading_pct'].max():.1f} %")
    print(f"  Daily line losses     : {ts_df['line_losses_kW'].sum():.1f} kWh")

    if ts_df["min_voltage_pu"].min() < 0.95:
        print("\n⚠  Voltage drops below 0.95 pu — consider cable upgrade or reactive support.")
    if ts_df["max_line_loading_pct"].max() > 80:
        print("⚠  Line loading exceeds 80 % — consider load balancing or reinforcement.")

    print("\nWriting results to DB …")
    write_grid_results_to_db(ts_df, project_id, scenario_id, engine)

    csv_path = Path("output") / "grid_timeseries_results.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    ts_df.to_csv(csv_path)
    print(f"CSV saved to {csv_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_id",   required=True)
    parser.add_argument("--scenario_id",  required=True)
    parser.add_argument("--network",      required=True, help="Path to pandapower JSON network file")
    parser.add_argument("--database_url", default=None)
    args = parser.parse_args()

    main(
        project_id=args.project_id,
        scenario_id=args.scenario_id,
        network_json=Path(args.network),
        database_url=args.database_url,
    )
