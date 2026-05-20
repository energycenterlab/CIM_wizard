"""
02 — Build a pandapower network from CIM Wizard grid data (cim_vector schema).

CIM Wizard stores grid infrastructure (substations, lines, transformers,
service points) in the `cim_vector` schema.  This script reads those tables
and builds a pandapower network ready for power-flow or OPF analysis.

Expected CIM Wizard grid tables (adapt SQL if your schema differs):
    cim_vector.substations          → buses (MV + LV)
    cim_vector.mv_lines / lv_lines  → lines
    cim_vector.transformers         → MV/LV transformers
    cim_vector.service_points       → load connection points

Usage
-----
    export DATABASE_URL="postgresql://user:pass@localhost:5433/cim_wizard_integrated"

    python 02_cim_wizard_network_builder.py \
        --project_id  my_project \
        --output      ./output/network.json
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd
import pandapower as pp
from sqlalchemy import create_engine, text


# ---------------------------------------------------------------------------
# Database loader helpers
# ---------------------------------------------------------------------------

def _engine(database_url: str | None = None):
    return create_engine(database_url or os.environ["DATABASE_URL"])


def load_substations(engine, project_id: str) -> pd.DataFrame:
    """Load MV and LV busbars / substations."""
    sql = text("""
        SELECT
            id,
            name,
            voltage_kv,
            substation_type,    -- 'MV', 'LV', 'HV'
            ST_X(ST_Centroid(geometry)) AS lon,
            ST_Y(ST_Centroid(geometry)) AS lat
        FROM cim_vector.substations
        WHERE project_id = :pid
        ORDER BY id
    """)
    return pd.read_sql(sql, engine, params={"pid": project_id})


def load_lines(engine, project_id: str) -> pd.DataFrame:
    """Load MV and LV cable/overhead lines."""
    sql = text("""
        SELECT
            id,
            name,
            from_bus_id,
            to_bus_id,
            voltage_kv,
            length_m,
            cable_type,         -- matches pandapower std_type, e.g. 'NAYY 4x50 SE'
            r_ohm_per_km,
            x_ohm_per_km,
            c_nf_per_km,
            max_i_ka
        FROM cim_vector.network_lines
        WHERE project_id = :pid
        ORDER BY id
    """)
    return pd.read_sql(sql, engine, params={"pid": project_id})


def load_transformers(engine, project_id: str) -> pd.DataFrame:
    """Load MV/LV transformers."""
    sql = text("""
        SELECT
            id,
            name,
            hv_bus_id,
            lv_bus_id,
            rated_kva,
            uk_percent,
            pk_kw,
            trafo_type          -- matches pandapower std_type if available
        FROM cim_vector.transformers
        WHERE project_id = :pid
    """)
    return pd.read_sql(sql, engine, params={"pid": project_id})


def load_service_points(engine, project_id: str) -> pd.DataFrame:
    """Load building service connections (load buses)."""
    sql = text("""
        SELECT
            sp.id,
            sp.bus_id,
            sp.peak_demand_kw,
            sp.power_factor,
            b.building_type
        FROM cim_vector.service_points sp
        LEFT JOIN cim_vector.buildings b ON b.id = sp.building_id
        WHERE sp.project_id = :pid
    """)
    return pd.read_sql(sql, engine, params={"pid": project_id})


# ---------------------------------------------------------------------------
# Network builder
# ---------------------------------------------------------------------------

# Pandapower standard LV cable types (built-in)
LV_CABLE_FALLBACK = "NAYY 4x50 SE"     # 50 mm² aluminium — typical suburban
MV_CABLE_FALLBACK = "NA2XS2Y 1x95 RM/25 12/20 kV"  # typical 20 kV cable

HV_GRID_VOLTAGE_KV = 110.0  # assumed upstream HV network


def build_network_from_cim(
    project_id: str,
    database_url: str | None = None,
) -> pp.pandapowerNet:
    """
    Build a pandapower network from CIM Wizard grid tables.

    Parameters
    ----------
    project_id : str
        CIM Wizard project identifier.
    database_url : str, optional
        Falls back to DATABASE_URL env var.

    Returns
    -------
    pandapower.pandapowerNet
    """
    engine = _engine(database_url)
    net = pp.create_empty_network(name=f"CIMWizard_{project_id}")

    # ── 1. Buses (substations) ─────────────────────────────────────────────
    substations = load_substations(engine, project_id)
    bus_id_map: dict[int, int] = {}   # CIM id → pandapower bus index

    print(f"Creating {len(substations)} buses …")
    for _, row in substations.iterrows():
        vn = float(row["voltage_kv"]) if row["voltage_kv"] else 0.4
        pp_idx = pp.create_bus(
            net,
            vn_kv=vn,
            name=row.get("name", f"bus_{row['id']}"),
            geodata=(row.get("lon"), row.get("lat")) if row.get("lon") else None,
        )
        bus_id_map[int(row["id"])] = pp_idx

    # ── 2. External HV grid connection (slack bus) ─────────────────────────
    # Attach to the highest-voltage bus found
    hv_buses = substations[substations["voltage_kv"] >= 10]
    if not hv_buses.empty:
        hv_bus_cim_id = int(hv_buses.sort_values("voltage_kv", ascending=False).iloc[0]["id"])
        hv_pp_idx = bus_id_map[hv_bus_cim_id]
        pp.create_ext_grid(net, bus=hv_pp_idx, vm_pu=1.0, name="HV_External_Grid")
        print(f"External grid attached to bus index {hv_pp_idx} (CIM id {hv_bus_cim_id}).")
    else:
        print("WARNING: No HV/MV bus found — add ext_grid manually.")

    # ── 3. Lines ───────────────────────────────────────────────────────────
    lines = load_lines(engine, project_id)
    print(f"Creating {len(lines)} lines …")
    for _, row in lines.iterrows():
        from_pp = bus_id_map.get(int(row["from_bus_id"]))
        to_pp   = bus_id_map.get(int(row["to_bus_id"]))
        if from_pp is None or to_pp is None:
            print(f"  SKIP line {row['id']}: bus not found.")
            continue

        length_km = float(row["length_m"]) / 1000.0
        std_type  = row.get("cable_type") or (LV_CABLE_FALLBACK if float(row["voltage_kv"] or 0.4) < 1 else MV_CABLE_FALLBACK)

        if std_type in pp.available_std_types(net)["line"]:
            pp.create_line(net, from_bus=from_pp, to_bus=to_pp,
                           length_km=length_km, std_type=std_type,
                           name=row.get("name", f"line_{row['id']}"))
        else:
            # Use custom parameters if std_type not found
            pp.create_line_from_parameters(
                net,
                from_bus=from_pp, to_bus=to_pp,
                length_km=length_km,
                r_ohm_per_km=float(row.get("r_ohm_per_km") or 0.642),
                x_ohm_per_km=float(row.get("x_ohm_per_km") or 0.083),
                c_nf_per_km=float(row.get("c_nf_per_km") or 210),
                max_i_ka=float(row.get("max_i_ka") or 0.142),
                name=row.get("name", f"line_{row['id']}"),
            )

    # ── 4. Transformers ────────────────────────────────────────────────────
    trafos = load_transformers(engine, project_id)
    print(f"Creating {len(trafos)} transformers …")
    for _, row in trafos.iterrows():
        hv_pp = bus_id_map.get(int(row["hv_bus_id"]))
        lv_pp = bus_id_map.get(int(row["lv_bus_id"]))
        if hv_pp is None or lv_pp is None:
            continue

        std_type = row.get("trafo_type")
        if std_type and std_type in pp.available_std_types(net)["trafo"]:
            pp.create_transformer(net, hv_bus=hv_pp, lv_bus=lv_pp,
                                  std_type=std_type,
                                  name=row.get("name", f"trafo_{row['id']}"))
        else:
            # Build from rated_kva
            kva = float(row.get("rated_kva") or 400)
            # Guess HV/LV voltage from connected buses
            hv_kv = net.bus.at[hv_pp, "vn_kv"]
            lv_kv = net.bus.at[lv_pp, "vn_kv"]
            pp.create_transformer_from_parameters(
                net,
                hv_bus=hv_pp, lv_bus=lv_pp,
                sn_mva=kva / 1000,
                vn_hv_kv=hv_kv, vn_lv_kv=lv_kv,
                vkr_percent=float(row.get("uk_percent") or 4.0),
                vk_percent=float(row.get("uk_percent") or 4.0),
                pfe_kw=float(row.get("pk_kw") or 1.35),
                i0_percent=0.3,
                name=row.get("name", f"trafo_{row['id']}"),
            )

    # ── 5. Loads (building service points) ────────────────────────────────
    service_pts = load_service_points(engine, project_id)
    print(f"Creating {len(service_pts)} loads …")
    for _, row in service_pts.iterrows():
        bus_pp = bus_id_map.get(int(row["bus_id"]))
        if bus_pp is None:
            continue
        peak_kw = float(row.get("peak_demand_kw") or 4.0)
        pf = float(row.get("power_factor") or 0.95)
        import math
        q_kvar = peak_kw * math.tan(math.acos(pf))
        pp.create_load(
            net,
            bus=bus_pp,
            p_mw=peak_kw / 1000,
            q_mvar=q_kvar / 1000,
            name=f"load_sp{row['id']}",
        )

    print(f"\nNetwork built: {len(net.bus)} buses, {len(net.line)} lines, "
          f"{len(net.trafo)} trafos, {len(net.load)} loads.")
    return net


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build pandapower network from CIM Wizard grid data.")
    parser.add_argument("--project_id",   required=True)
    parser.add_argument("--output",        default="./output/cim_network.json")
    parser.add_argument("--database_url",  default=None)
    args = parser.parse_args()

    net = build_network_from_cim(args.project_id, args.database_url)

    pp.runpp(net)
    print("\n--- Power flow result: bus voltages ---")
    print(net.res_bus[["vm_pu", "p_mw"]].round(4))

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    pp.to_json(net, str(out))
    print(f"\nNetwork saved to {out}")
