# Co-simulation practice (mosaik)

Small sandbox for learning co-simulation. It is **not** wired into the CIM Wizard API or CESAR-P pipeline. Production building simulation stays in `cim_wizard_integrated_2026/building_simulation/`.

You asked about **Helix**. In energy-system co-simulation that almost always means **[HELICS](https://helics.org/)** (Hierarchical Engine for Large-scale Infrastructure Co-Simulation), which is already cited in the thesis bibliography as `helics`. mosaik is the other common academic stack (OFFIS / energy systems, Python-first).

## mosaik vs HELICS

Both do the same job: **keep independent simulators, exchange values at agreed times, and advance a shared clock**. Neither *is* the physics. Each simulator owns its own model (here: a one-line equation).

| | **mosaik** | **HELICS** |
|---|---|---|
| Origin | OFFIS (Germany), energy / smart-grid labs | PNNL / NREL / LLNL, US DOE, power + multi-infrastructure |
| Feel | Python scenario file + Python (or socket) simulators | C++ core, bindings in Python / C++ / Java / MATLAB / FMI |
| Typical size | District / campus, tens to low hundreds of simulators | Large federations, HPC, many processes / machines |
| Time | Discrete mosaik time (int steps). Easy hourly / 15 min | Flexible: time-based, event-based, real-time, mixed |
| Coupling | `world.connect(src, dest, attr)` in one scenario | Federates + publications / subscriptions (or endpoints) |
| FMI / FMU | Possible (adapters) | First-class use case |
| Learning curve | Low if you already write Python | Higher: brokers, cores, federate lifecycle |

**mosaik — pros**

- Fastest path for a Python toy like this one.
- Scenario is readable: entities and arrows live in one file.
- Good teaching tool and good match for later wrapping EnergyPlus / pandapower / custom occupant models.
- Used in several Polito / OFFIS-style papers (district heating, CPES testing).

**mosaik — cons**

- Weaker story for huge distributed runs and HPC.
- Less native real-time / hardware-in-the-loop than HELICS.
- Ecosystem is smaller; some adapters are research-grade.

**HELICS — pros**

- Built for scale and mixed languages (power-flow C++ + Python controls + FMUs).
- Strong time / event / real-time modes and multiple machines.
- Common in US lab stacks (GridLAB-D, etc.).

**HELICS — cons**

- More moving parts (broker, core type, federation config) for a 4-simulator room.
- Python is a binding, not the native centre of gravity.
- Overkill for “learn input–output this afternoon”.

**Rule of thumb for this repo:** practise in **mosaik**. Reach for **HELICS** when you federate heavy tools (EnergyPlus FMU, grid, district heating) across processes or languages.

## YAML instantiation (no FMU required)

Simulators are **classes**. mosaik `create(...)` makes **instances**. The YAML file is just data that `scenario.py` passes into `create()`:

- `OccupantSim` class → entities `alice`, `bob` with different `present_hours`
- `DaylightSim` class → one `outdoor` entity with sunrise/sunset/cloudiness
- each room also gets its own curtain and light

That is the normal mosaik pattern. **FMU/FMI is not required** because these models already live in Python. An FMU is a *packaging* standard (compiled Modelica / EnergyPlus / Dymola wrapped as a black box with inputs, outputs, and a `doStep`). You reach for it when the model is written in another tool and you do not want to reimplement it. For a schedule and a triangle of lux, wrapping an FMU would only add friction.

Later, if you couple EnergyPlus or a Modelica HVAC, you add an FMU adapter *next to* these Python simulators. mosaik still orchestrates; the YAML would then list an FMU path instead of (or as well as) `present_hours`.

Edit `configs/room_week.yaml` to add rooms or change schedules. Do not hard-code occupants in the simulator.

```
Occupant          Daylight
 present            is_day, is_cloudy, illuminance_lux
    \               /          \
     \             /            \
      v           v              v
      Curtain                  Light
      curtain_open             light_on
              \                /
               v              v
                 Collector
```

| Simulator | Equation |
|---|---|
| Occupant | present if hour in YAML `present_hours` windows `[start, end)` |
| Daylight | triangle illuminance between YAML `sunrise`/`sunset`; `cloudy` flag |
| Curtain | `curtain_open = present AND is_day` (open fully to use daylight) |
| Light | `light_on = present AND (cloudy OR night)` |

Default YAML: Alice keeps 08–13 / 14–20; Bob is 10–16. On this cloudy week each light is on while that occupant is present. Curtains open only while that occupant is present and it is day.

## Run

```bash
cd cosimulation
python -m pip install -r requirements.txt
python scenario.py
# or: python scenario.py configs/room_week.yaml
```

Outputs: `output/room_week.csv` and `output/room_week.png`. CSV columns are `entity.attribute` (e.g. `alice.present`).
