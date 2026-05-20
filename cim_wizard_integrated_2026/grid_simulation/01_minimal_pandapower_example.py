"""
01 — Minimal pandapower example (no CIM Wizard DB required).

Builds a simple LV residential feeder from scratch and demonstrates:
  A) Power flow (runpp)       — where does the current flow? are voltages ok?
  B) Short-circuit (sc)       — fault currents for protection coordination
  C) Optimal power flow (OPF) — minimise cost while respecting constraints
  D) Time-series simulation   — 24-hour load profile

                   HV external grid (20 kV)
                         │
                    [Transformer]
                    20 kV / 0.4 kV  ← MV/LV substation
                         │
                    [bus_lv_main]   ← LV busbar (400 V)
                    /     │     \
              line_1   line_2   line_3
                /         │         \
         [bus_1]      [bus_2]      [bus_3]
            │             │             │
         Load_A        Load_B        Load_C
      (house A)     (house B)     (house C)
                                        │
                                    PV_sgen
                                  (rooftop PV)

Run:
    pip install -r requirements.txt
    python 01_minimal_pandapower_example.py
"""

from __future__ import annotations

import pandas as pd
import pandapower as pp
import pandapower.shortcircuit as sc


# ═══════════════════════════════════════════════════════════════════════════
# PANDAPOWER  MODEL  OVERVIEW  (printed at startup)
# ═══════════════════════════════════════════════════════════════════════════
MODEL_OVERVIEW = """
┌─────────────────────────────────────────────────────────────────────────┐
│                   pandapower  MODEL  OVERVIEW                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  NETWORK ELEMENT   │  KEY INPUTS                │  KEY OUTPUTS          │
│  ─────────────────   ───────────────────────────   ──────────────────── │
│  bus               │  vn_kv (nominal voltage)   │  vm_pu (voltage mag.) │
│                    │  type: "b"/"n"/"m"         │  va_degree (angle)    │
│                    │                            │  p_mw, q_mvar         │
│                    │                            │  (at bus from flows)  │
│                                                                         │
│  ext_grid (slack)  │  vm_pu (voltage setpoint)  │  p_mw, q_mvar drawn  │
│  (HV connection)   │  va_degree (angle ref)     │  from upstream grid   │
│                                                                         │
│  transformer       │  hv_bus, lv_bus            │  loading_percent      │
│                    │  std_type (standard type)  │  p_hv_mw, p_lv_mw    │
│                    │  e.g. "0.4 MVA 20/0.4 kV"  │  pl_mw (losses)       │
│                                                                         │
│  line              │  from_bus, to_bus          │  loading_percent      │
│                    │  length_km                 │  p_from_mw            │
│                    │  std_type (cable/OHL)      │  i_from_ka (current)  │
│                    │  e.g. "NAYY 4x50 SE"       │  pl_mw (losses)       │
│                                                                         │
│  load              │  bus                       │  (consumed as given)  │
│                    │  p_mw  (active power)      │                       │
│                    │  q_mvar (reactive power)   │                       │
│                    │  controllable=True → OPF   │                       │
│                                                                         │
│  sgen (static gen) │  bus                       │  (injected as given)  │
│  (PV, wind, CHP)   │  p_mw (generation)         │                       │
│                    │  q_mvar                    │                       │
│                    │  controllable=True → OPF   │                       │
│                                                                         │
│  gen (sync. gen)   │  bus                       │  q_mvar (regulated)   │
│  (voltage control) │  p_mw, vm_pu setpoint      │                       │
│                                                                         │
│  storage           │  bus, p_mw, max_e_mwh      │  soc_percent          │
│  (battery/EV)      │  controllable=True → OPF   │                       │
│                                                                         │
│  ANALYSES AVAILABLE                                                     │
│  ─────────────────                                                      │
│  pp.runpp(net)          Power flow (Newton-Raphson)                     │
│  pp.runopp(net)         Optimal power flow (minimise cost)              │
│  sc.calc_sc(net)        Short-circuit (IEC 60909)                       │
│  pp.timeseries.*        24h / annual time-series (controller API)       │
│  pp.topology.*          Graph analysis (radial/meshed detection,        │
│                         unsupplied buses, shortest path)                │
│  pp.estimation.*        State estimation (with PMU/SCADA measurements)  │
│                                                                         │
│  RESULT DataFrames (after runpp)                                        │
│  ─────────────────                                                      │
│  net.res_bus       vm_pu, va_degree, p_mw, q_mvar                      │
│  net.res_line      p_from_mw, q_from_mvar, i_from_ka, loading_percent  │
│  net.res_trafo     p_hv_mw, p_lv_mw, pl_mw, loading_percent            │
│  net.res_load      p_mw, q_mvar                                         │
│  net.res_sgen      p_mw, q_mvar                                         │
│  net.res_ext_grid  p_mw, q_mvar                                         │
└─────────────────────────────────────────────────────────────────────────┘
"""


# ═══════════════════════════════════════════════════════════════════════════
# A) Build the example network
# ═══════════════════════════════════════════════════════════════════════════

def build_example_network() -> pp.pandapowerNet:
    """
    Build a simple LV residential feeder.

    Topology: HV ext_grid → 20/0.4 kV transformer → LV busbar
              → 3 radial branches with residential loads and one rooftop PV.
    """
    net = pp.create_empty_network(name="Residential LV Feeder Example")

    # ── Buses ──────────────────────────────────────────────────────────────
    # MV side (20 kV)
    bus_mv = pp.create_bus(net, vn_kv=20.0, name="MV_Bus_20kV", type="b")

    # LV busbar (0.4 kV = 400 V)
    bus_lv_main = pp.create_bus(net, vn_kv=0.4, name="LV_Main_400V", type="b")

    # Three feeder buses (LV)
    bus_1 = pp.create_bus(net, vn_kv=0.4, name="Bus_HouseA")
    bus_2 = pp.create_bus(net, vn_kv=0.4, name="Bus_HouseB")
    bus_3 = pp.create_bus(net, vn_kv=0.4, name="Bus_HouseC_PV")

    # ── External grid (upstream HV supply — the "slack" bus) ───────────────
    # vm_pu=1.0 → the HV side is held at nominal voltage
    pp.create_ext_grid(net, bus=bus_mv, vm_pu=1.0, name="HV_Grid_Connection")

    # ── MV/LV Transformer ──────────────────────────────────────────────────
    # Standard type "0.4 MVA 20/0.4 kV" is built-in to pandapower
    pp.create_transformer(
        net,
        hv_bus=bus_mv,
        lv_bus=bus_lv_main,
        std_type="0.4 MVA 20/0.4 kV",
        name="MV_LV_Trafo_400kVA",
    )

    # ── LV Cable Lines ─────────────────────────────────────────────────────
    # std_type "NAYY 4x50 SE" = standard 4-core aluminium 50mm² cable
    # Typical for suburban/residential LV networks
    pp.create_line(net, from_bus=bus_lv_main, to_bus=bus_1,
                   length_km=0.05, std_type="NAYY 4x50 SE", name="Line_1_HouseA")
    pp.create_line(net, from_bus=bus_lv_main, to_bus=bus_2,
                   length_km=0.08, std_type="NAYY 4x50 SE", name="Line_2_HouseB")
    pp.create_line(net, from_bus=bus_lv_main, to_bus=bus_3,
                   length_km=0.12, std_type="NAYY 4x50 SE", name="Line_3_HouseC")

    # ── Loads (residential houses) ─────────────────────────────────────────
    # p_mw = active power consumed (MW).  Typical house: 3–5 kW peak
    # q_mvar = reactive power (inductive, motors/heating)
    pp.create_load(net, bus=bus_1, p_mw=0.004, q_mvar=0.001,  name="House_A")
    pp.create_load(net, bus=bus_2, p_mw=0.005, q_mvar=0.0015, name="House_B")
    pp.create_load(net, bus=bus_3, p_mw=0.003, q_mvar=0.001,  name="House_C")

    # ── Rooftop PV (static generator) ──────────────────────────────────────
    # Injects power into the grid (p_mw is positive = generation)
    # At noon on a sunny day a 5 kWp system delivers ~4.5 kW
    pp.create_sgen(
        net,
        bus=bus_3,
        p_mw=0.0045,   # 4.5 kW
        q_mvar=0.0,
        name="Rooftop_PV_5kWp",
        type="PV",
    )

    return net


# ═══════════════════════════════════════════════════════════════════════════
# B) Power flow
# ═══════════════════════════════════════════════════════════════════════════

def run_power_flow(net: pp.pandapowerNet) -> None:
    print("\n" + "="*60)
    print("A)  POWER FLOW  (Newton-Raphson, balanced 3-phase)")
    print("="*60)

    pp.runpp(net, algorithm="nr", calculate_voltage_angles=True)

    print("\n--- Bus voltages ---")
    print(net.res_bus[["vm_pu", "va_degree", "p_mw", "q_mvar"]].round(4).to_string())

    print("\n--- Line loading ---")
    print(net.res_line[["p_from_mw", "i_from_ka", "loading_percent"]].round(4).to_string())

    print("\n--- Transformer loading ---")
    print(net.res_trafo[["p_hv_mw", "p_lv_mw", "pl_mw", "loading_percent"]].round(5).to_string())

    print("\n--- External grid (power drawn from HV network) ---")
    print(net.res_ext_grid[["p_mw", "q_mvar"]].round(5).to_string())

    # Flag voltage violations (EN 50160: ±10 % of nominal)
    v_low  = net.res_bus["vm_pu"] < 0.90
    v_high = net.res_bus["vm_pu"] > 1.10
    if v_low.any() or v_high.any():
        print("\n⚠  VOLTAGE VIOLATION detected on buses:")
        print(net.res_bus[v_low | v_high][["vm_pu"]])
    else:
        print("\n✓  All bus voltages within ±10 % of nominal (EN 50160).")

    # Flag overloaded lines
    overloaded = net.res_line[net.res_line["loading_percent"] > 100]
    if not overloaded.empty:
        print("\n⚠  OVERLOADED lines:")
        print(overloaded[["loading_percent"]])
    else:
        print("✓  No lines overloaded.")


# ═══════════════════════════════════════════════════════════════════════════
# C) Short-circuit analysis (IEC 60909)
# ═══════════════════════════════════════════════════════════════════════════

def run_short_circuit(net: pp.pandapowerNet) -> None:
    print("\n" + "="*60)
    print("B)  SHORT-CIRCUIT  (IEC 60909, max fault)")
    print("="*60)
    print("Purpose: size protective devices (fuses, circuit breakers).")
    print("         Ikss = steady-state short-circuit current.")

    sc.calc_sc(net, fault="3ph", case="max")
    print("\n--- Short-circuit currents at LV buses (kA) ---")
    print(net.res_bus_sc[["ikss_ka", "ip_ka"]].round(4).to_string())


# ═══════════════════════════════════════════════════════════════════════════
# D) Optimal power flow
# ═══════════════════════════════════════════════════════════════════════════

def run_optimal_power_flow(net: pp.pandapowerNet) -> None:
    print("\n" + "="*60)
    print("C)  OPTIMAL POWER FLOW  (minimise generation cost)")
    print("="*60)
    print("Purpose: find the cheapest dispatch that keeps voltages & lines within limits.")

    # Assign cost to the external grid (€/MWh)
    pp.create_poly_cost(net, element=0, et="ext_grid", cp1_eur_per_mw=80.0)
    # Assign (negative) cost to PV — incentivise local consumption
    pp.create_poly_cost(net, element=0, et="sgen", cp1_eur_per_mw=-20.0)

    # Add voltage and loading constraints
    net.bus["max_vm_pu"] = 1.05
    net.bus["min_vm_pu"] = 0.95
    net.line["max_loading_percent"] = 100.0
    net.trafo["max_loading_percent"] = 100.0

    try:
        pp.runopp(net)
        print("\n--- OPF bus voltages ---")
        print(net.res_bus[["vm_pu", "p_mw", "q_mvar"]].round(4).to_string())
        print(f"\nTotal cost: {net.res_cost:.2f} €")
    except pp.optimal_powerflow.OPFNotConverged:
        print("OPF did not converge — check constraints / network feasibility.")


# ═══════════════════════════════════════════════════════════════════════════
# E) 24-hour time-series (simplified loop — for full controller API see docs)
# ═══════════════════════════════════════════════════════════════════════════

def run_timeseries_simple(net: pp.pandapowerNet) -> pd.DataFrame:
    """
    Run power flow for each of 24 hours using a simple load profile.
    Returns a DataFrame with vm_pu at each bus per hour.
    """
    print("\n" + "="*60)
    print("D)  24-HOUR  TIME-SERIES  (simplified loop)")
    print("="*60)

    # Normalised load profile (fraction of peak) — typical residential
    load_profile = [
        0.25, 0.20, 0.18, 0.18, 0.20, 0.30,   # 00–05 h
        0.50, 0.70, 0.75, 0.65, 0.60, 0.65,   # 06–11 h
        0.70, 0.65, 0.60, 0.60, 0.65, 0.80,   # 12–17 h
        0.95, 1.00, 0.90, 0.75, 0.60, 0.40,   # 18–23 h
    ]
    # PV generation profile (fraction of peak, noon peak)
    pv_profile = [
        0.00, 0.00, 0.00, 0.00, 0.00, 0.02,
        0.10, 0.30, 0.55, 0.75, 0.90, 0.98,
        1.00, 0.98, 0.90, 0.75, 0.50, 0.20,
        0.05, 0.00, 0.00, 0.00, 0.00, 0.00,
    ]

    base_loads_mw  = net.load["p_mw"].values.copy()
    base_sgen_mw   = net.sgen["p_mw"].values.copy()

    results = []
    for hour, (lf, pf) in enumerate(zip(load_profile, pv_profile)):
        net.load["p_mw"]  = base_loads_mw  * lf
        net.sgen["p_mw"]  = base_sgen_mw   * pf
        pp.runpp(net, verbose=False)

        row = {"hour": hour}
        for idx, bus_name in net.bus["name"].items():
            row[f"vm_pu_{bus_name}"] = net.res_bus.loc[idx, "vm_pu"]
        row["grid_import_kW"] = net.res_ext_grid["p_mw"].iloc[0] * 1000
        results.append(row)

    ts_df = pd.DataFrame(results).set_index("hour")

    print("\nHourly voltage at LV_Main bus and grid import:")
    print(ts_df[["vm_pu_LV_Main_400V", "grid_import_kW"]].round(4).to_string())

    # Restore original values
    net.load["p_mw"] = base_loads_mw
    net.sgen["p_mw"] = base_sgen_mw

    return ts_df


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(MODEL_OVERVIEW)

    net = build_example_network()
    print(f"\nNetwork created: {net}")
    print(f"  Buses       : {len(net.bus)}")
    print(f"  Lines       : {len(net.line)}")
    print(f"  Transformers: {len(net.trafo)}")
    print(f"  Loads       : {len(net.load)}  (total {net.load.p_mw.sum()*1000:.1f} kW)")
    print(f"  Sgens (PV)  : {len(net.sgen)}  (total {net.sgen.p_mw.sum()*1000:.1f} kW)")

    run_power_flow(net)
    run_short_circuit(net)
    run_optimal_power_flow(net)
    ts = run_timeseries_simple(net)

    # Save network to file (JSON format)
    pp.to_json(net, "example_lv_feeder.json")
    print("\nNetwork saved to example_lv_feeder.json")
    print("Load it again with:  net = pp.from_json('example_lv_feeder.json')")
