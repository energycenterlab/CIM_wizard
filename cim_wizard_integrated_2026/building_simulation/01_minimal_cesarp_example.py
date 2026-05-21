"""
01 — Minimal CESAR-P example (no CIM Wizard DB required).

What this script does
---------------------
  1. Reads building footprints from SiteVertices_example.csv
  2. Reads building attributes from BuildingInformation_example.csv
  3. Loads the config from config/cesar_p_config.yml
  4. Runs EnergyPlus for each building in parallel via CESAR-P
  5. Collects and prints annual energy demand per building

Prerequisites
-------------
  pip install -r requirements.txt
  EnergyPlus installed (https://energyplus.net/downloads) — CESAR-P calls it
  internally.  Set the ENERGYPLUS_DIR env var if not in the standard location.

  A weather .epw file placed at data/weather/your_city.epw
  → run  python 00_weather_downloader.py  first.

CESAR-P model summary
---------------------
  Thermal zones  : one zone per floor (simplified box model)
  Heat transfer  : RC-equivalent + EnergyPlus zone heat balance
  Constructions  : year-of-construction → U-values from Swiss BFE/SIA database
  Schedules      : SIA 2024 standard (occupancy, lighting, equipment, DHW)
  HVAC           : ideal air loads (no detailed HVAC equipment modelled by default)
  Shading        : neighbouring buildings cast shadows via EnergyPlus shading surfaces

Outputs
-------
  Per building, per year:
    - heating_demand_kWh     (space heating)
    - cooling_demand_kWh     (space cooling)
    - dhw_demand_kWh         (domestic hot water)
    - electricity_demand_kWh (lighting + appliances, from SIA 2024 schedules)
    - total_final_energy_kWh
    - CO2_kg                 (based on Swiss KBOB emission factors)
    - heating_demand_kWh_m2  (specific energy intensity)
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output" / "minimal_example"
CONFIG_PATH = BASE_DIR / "config" / "cesar_p_config.yml"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Helper: check prerequisites
# ---------------------------------------------------------------------------
def _check_prerequisites() -> None:
    weather_files = list((BASE_DIR / "data" / "weather").glob("*.epw"))
    if not weather_files:
        raise FileNotFoundError(
            "No EPW weather file found in data/weather/.\n"
            "Run:  python 00_weather_downloader.py"
        )

    try:
        import cesarp  # noqa: F401
    except ImportError:
        raise ImportError(
            "CESAR-P not installed.  Run:\n"
            "  pip install -r requirements.txt"
        )

    ep_dir = os.environ.get("ENERGYPLUS_DIR", "")
    default_ep_paths = [
        Path("/usr/local/EnergyPlus-9-5-0"),
        Path("/usr/local/EnergyPlus-9-4-0"),
        Path(r"C:\EnergyPlusV9-5-0"),
    ]
    ep_found = ep_dir or any(p.exists() for p in default_ep_paths)
    if not ep_found:
        print(
            "WARNING: EnergyPlus not detected.  "
            "Download from https://energyplus.net/downloads and set:\n"
            "  export ENERGYPLUS_DIR=/path/to/EnergyPlus"
        )


# ---------------------------------------------------------------------------
# Run CESAR-P
# ---------------------------------------------------------------------------
def run_simulation() -> pd.DataFrame:
    """
    Execute CESAR-P for all buildings defined in the example CSV files.

    Returns
    -------
    pd.DataFrame
        Annual energy results indexed by building EGID.
    """
    import cesarp.common
    from cesarp.manager.SimulationManager import SimulationManager

    _check_prerequisites()

    print(f"Starting CESAR-P simulation...")
    print(f"  Config  : {CONFIG_PATH}")
    print(f"  Output  : {OUTPUT_DIR}")

    ureg = cesarp.common.init_unit_registry()
    mgr = SimulationManager(
        base_output_path=str(OUTPUT_DIR),
        main_config_path=str(CONFIG_PATH),
        unit_registry=ureg,
        fids_to_use=None,   # None = simulate all buildings in the CSV
        load_from_disk=False,
    )

    # Runs EnergyPlus in parallel (one process per building)
    mgr.run_all_sims(include_neighborhood=True)

    # Collect results as a flat DataFrame
    results: pd.DataFrame = mgr.collect_all_results()
    return results


# ---------------------------------------------------------------------------
# Post-process and display
# ---------------------------------------------------------------------------
def summarise(results: pd.DataFrame) -> None:
    cols_of_interest = [
        "heating_demand_kWh",
        "cooling_demand_kWh",
        "dhw_demand_kWh",
        "electricity_demand_kWh",
        "total_final_energy_kWh",
        "CO2_kg",
        "heating_demand_kWh_m2",
    ]
    available = [c for c in cols_of_interest if c in results.columns]
    summary = results[available]

    print("\n=== Annual Energy Demand per Building ===")
    print(summary.to_string())

    csv_out = OUTPUT_DIR / "annual_results.csv"
    summary.to_csv(csv_out)
    print(f"\nResults saved to {csv_out}")

    district_total = summary["total_final_energy_kWh"].sum()
    print(f"\nDistrict total final energy: {district_total:,.0f} kWh/year")


# ---------------------------------------------------------------------------
# CESAR-P model explanation (printed to stdout as a reference)
# ---------------------------------------------------------------------------
CESARP_MODEL_EXPLANATION = """
┌─────────────────────────────────────────────────────────────────────┐
│                    CESAR-P  MODEL  OVERVIEW                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  INPUTS                                                             │
│  ──────                                                             │
│  Geometry                                                           │
│    • Building footprint polygon (vertices in projected CRS)         │
│    • Building height  →  floor height = height / n_floors           │
│    • Number of floors above ground                                  │
│    • Neighbour footprints (for mutual shading calculation)          │
│                                                                     │
│  Building meta                                                      │
│    • Year of construction  →  selects envelope U-values             │
│    • Building type (SFH/MFH/OFFICE/…) → SIA 2024 schedules         │
│                                                                     │
│  Climate                                                            │
│    • .epw weather file  (8 760 hourly rows)                         │
│      - dry-bulb temp, dew point, relative humidity                  │
│      - global/direct/diffuse irradiance (W/m²)                      │
│      - wind speed & direction                                       │
│      - atmospheric pressure                                         │
│                                                                     │
│  WHAT IS SIMULATED (EnergyPlus physics)                             │
│  ──────────────────────────────────────                             │
│  Thermal balance per zone                                           │
│    • Solar heat gain through glazing                                │
│    • Conduction through walls, roof, floor, windows                 │
│    • Infiltration / ventilation heat loss                           │
│    • Internal gains: occupants, lighting, equipment                 │
│    • Ideal-load HVAC (heating/cooling power to maintain setpoints)  │
│                                                                     │
│  Schedules (SIA 2024 standard)                                      │
│    • Occupancy profile (presence / absence per hour)                │
│    • Lighting W/m²  (linked to presence)                            │
│    • Equipment W/m² (linked to presence)                            │
│    • DHW litres/day (linked to presence)                            │
│    • Heating setpoint 20 °C occupied / 16 °C setback               │
│    • Cooling setpoint 26 °C occupied / 28 °C setback               │
│                                                                     │
│  OUTPUTS                                                            │
│  ───────                                                            │
│  Annual totals (kWh/year) or hourly time series:                    │
│    • heating_demand          space heating energy                   │
│    • cooling_demand          space cooling energy                   │
│    • dhw_demand              domestic hot water                     │
│    • electricity_demand      lights + plug loads                    │
│    • total_final_energy       sum of above                          │
│    • heating_demand_kWh_m2   energy intensity (kWh/m²·a)           │
│    • CO2_kg                  operational carbon                     │
│    • retrofit details        cost / savings if retrofit run         │
└─────────────────────────────────────────────────────────────────────┘
"""


if __name__ == "__main__":
    print(CESARP_MODEL_EXPLANATION)
    results = run_simulation()
    summarise(results)
