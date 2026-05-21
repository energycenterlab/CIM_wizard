# CIM Wizard Integrated

CIM Wizard Integrated is a comprehensive FastAPI service that combines vector data management, census data, raster processing, and pipeline execution with direct database access. This is version 2.0 that integrates all services with direct database connections instead of API calls.

## Key Features

- **Simplified API**: No Pydantic validation - uses simple dictionaries for maximum clarity
- **Direct Database Access**: Services communicate directly via database instead of API calls
- **Multi-Schema Design**: Organized data using `cim_vector`, `cim_census`, and `cim_raster` schemas
- **Object-Oriented Architecture**: Preserved from datalake8 (pipeline executor, data manager, calculators)
- **Integrated Services**: Vector, census, and raster data in one unified API

## Database Setup

### Prerequisites
- PostgreSQL 12+ with PostGIS 3.0+
- Python 3.8+
- All dependencies from `requirements.txt`

### Database Installation

1. **Create Database and Extensions**:
   ```bash
   # Connect as postgres superuser
   psql -U postgres
   
   # Create database
   CREATE DATABASE cim_wizard_integrated;
   \c cim_wizard_integrated;
   
   # Run initialization script
   \i init_db.sql
   ```

2. **Verify Setup**:
   ```sql
   -- Check schemas
   SELECT schema_name FROM information_schema.schemata 
   WHERE schema_name IN ('cim_vector', 'cim_census', 'cim_raster');
   
   -- Check extensions
   SELECT name, installed_version FROM pg_available_extensions 
   WHERE name LIKE 'postgis%' AND installed_version IS NOT NULL;
   ```

For detailed database setup instructions, see [DATABASE_SETUP.md](DATABASE_SETUP.md).

## Installation

### Using Conda (Recommended)
```bash
# Create environment
conda env create -f environment.yml
conda activate cim_wizard

# Set up database (see Database Setup above)

# Configure environment
cp env.example .env
# Edit .env with your database settings

# Run application
python run.py
```

### Using pip
```bash
# Install dependencies
pip install -r requirements.txt

# Set up database and environment as above

# Run application
python run.py
```

## API Usage (Simplified)

The API uses simple dictionaries instead of complex validation schemas for maximum clarity:

### Example 1: Pipeline Execution
```python
import requests
import json

# Simple pipeline request - just a dictionary
request_data = {
    "project_id": "test_project_001",
    "scenario_id": "scenario_001", 
    "features": ["building_height", "building_area"],
    "parallel": False
}

response = requests.post(
    "http://localhost:8000/api/pipeline/execute",
    json=request_data
)

print(response.json())
```

### Example 2: Building Height Calculation
```python
# Calculate building height from raster data
building_geometry = {
    "type": "Polygon",
    "coordinates": [[
        [11.25, 43.75], [11.26, 43.75], 
        [11.26, 43.76], [11.25, 43.76], 
        [11.25, 43.75]
    ]]
}

response = requests.post(
    "http://localhost:8000/api/raster/height",
    json=building_geometry
)

print(f"Building height: {response.json()['height']}m")
```

### Example 3: Census Data Query
```python
# Get census data for a polygon area
polygon_coords = [
    [11.2, 43.7], [11.3, 43.7],
    [11.3, 43.8], [11.2, 43.8], 
    [11.2, 43.7]
]

response = requests.post(
    "http://localhost:8000/api/census/census_spatial",
    json=polygon_coords
)

census_zones = response.json()
print(f"Found {len(census_zones['features'])} census zones")
```

## API Endpoints

### Vector Data (`/api/vector`)
- `GET /projects` - List all projects
- `GET /dashboard` - Project dashboard
- `GET /pscenarios/{project_id}` - Get project scenarios
- `GET /bgeo/{building_id}` - Get building geometry
- `GET /get_buildings_geojson/{project_id}/{scenario_id}` - Buildings as GeoJSON

### Pipeline Execution (`/api/pipeline`)
- `POST /execute` - Execute feature pipeline
- `POST /execute_explicit` - Execute with explicit method calls
- `POST /execute_predefined` - Execute predefined pipeline
- `POST /calculate_feature` - Calculate single feature
- `GET /available_features` - List available features
- `GET /configuration` - Get pipeline configuration

### Census Data (`/api/census`)
- `POST /census_spatial` - Spatial census query
- `GET /census/{census_id}` - Get census by ID
- `GET /building_age_distribution` - Building age statistics
- `GET /population_statistics` - Population statistics

### Raster Data (`/api/raster`)
- `POST /height` - Calculate building height
- `POST /height_batch` - Batch height calculation  
- `POST /clip` - Clip raster by geometry
- `GET /statistics` - Raster statistics

### CIM Wizard Views (`/api/cim-wizard`)
- `POST /calculate` - Calculate a single feature (body includes feature_name)
- `GET /calculate?feature_name=<n>` - Calculate a single feature (query param)
- `POST /chainable` - Execute chain of calculators separated by `|`
- `POST /priority-override` - Set runtime priority override for a feature
- `GET /list` - List all available features, pipelines, and endpoints

## Architecture Overview

### Database Schemas
- **`cim_vector`**: Buildings, projects, grid infrastructure
- **`cim_census`**: Census zones and demographic data
- **`cim_raster`**: DTM/DSM data and height calculations

### Core OOP Design

The system is built around three core classes and a `BaseCalculator` hierarchy:

```
BaseCalculator                  (app/calculators/base_calculator.py)
  |-- ScenarioGeoCalculator
  |-- ScenarioCensusBoundaryCalculator
  |-- BuildingGeoCalculator
  |-- BuildingPropsCalculator
  |-- BuildingHeightCalculator
  |-- BuildingAreaCalculator
  |-- BuildingVolumeCalculator
  |-- BuildingNFloorsCalculator
  |-- BuildingResidentialFilterCalculator
  |-- CensusPopulationCalculator
  |-- BuildingPopulationCalculator
  |-- BuildingTypeCalculator
  |-- BuildingConstructionYearCalculator
  |-- BuildingNFamiliesCalculator
  |-- BuildingDemographicCalculator
  |-- BuildingGeoLod12Calculator
  |-- EnvelopeEfficiencyCalculator
  |-- FmuAssignCalculator

CimWizardDataManager            (app/core/data_manager.py)
CimWizardPipelineExecutor       (app/core/pipeline_executor.py)
```

**BaseCalculator** -- Every calculator inherits from `BaseCalculator`, which
provides pipeline/data-manager references, convenience wrappers for logging,
validation, feature access, and properties for `db_session`, `project_id`,
and `scenario_id`.  Subclasses only call `super().__init__(pipeline_executor)`
and implement domain-specific methods.

**CimWizardDataManager** -- Central context object for a pipeline run.
Stores calculated features, project/scenario identifiers, DB session,
`configuration.json`, and `FeatureProxy` objects that enable fluent chaining
(`dm.building_height.calculate_from_raster_tiles`).

**CimWizardPipelineExecutor** -- Orchestrates calculator execution.
Dynamically loads calculator classes from `configuration.json`, resolves
dependency order via topological sort, and selects methods through a
priority-based fallback mechanism (lowest priority number runs first; runtime
overrides are supported).

### How Calculators Work

1. The pipeline executor instantiates a calculator via its `class_path` and
   `class_name` from `configuration.json`.
2. Each calculator receives the executor in its constructor and gains access
   to the data manager and all convenience methods through `BaseCalculator`.
3. A calculation method reads its inputs via `self.get_feature(...)`,
   performs computation, and stores results with `self.set_feature(...)`.
4. The executor tries methods in priority order; the first one whose
   dependencies are satisfied and returns a non-None value wins.

### Configuration-Driven Development

`configuration.json` is the single coordinator between calculators, database
columns, the field normalizer, and the data manager.  There are no separate
codegen or migration scripts to run.  The developer workflow is:

1. **Stop** the backend.
2. **Add** a calculator file under `app/calculators/` (inherit from
   `BaseCalculator`).
3. **Edit** `app/core/configuration.json` -- register the feature, its
   methods, and optionally its `output` column mapping.
4. Optionally add or update a route under `app/api/`.
5. **Start** the backend.  On startup the application automatically:
   - Creates any missing DB columns declared in `output` sections.
   - Extends `normalization_config.json` with fields for new columns.
   - Builds dynamic feature proxies and `_data` attributes in the data
     manager -- no hardcoded list to maintain.

#### Adding a New Calculator (step by step)

**a) Create the calculator file** `app/calculators/solar_potential_calculator.py`:

```python
from app.calculators.base_calculator import BaseCalculator

class SolarPotentialCalculator(BaseCalculator):
    def __init__(self, pipeline_executor):
        super().__init__(pipeline_executor)

    def estimate_from_area(self):
        area = self.get_feature("building_area")
        if area is None:
            self.log_error("building_area not available")
            return None
        result = area * 0.15  # simplified
        self.set_feature("solar_potential", result)
        self.log_success("estimate_from_area", result, "kWp")
        return result
```

**b) Register in `configuration.json`:**

```json
"solar_potential": {
  "constraints": {"datatype": "float", "value_range": [0, 100000]},
  "class_path": "app.calculators.solar_potential_calculator",
  "class_name": "SolarPotentialCalculator",
  "output": [
    {
      "table": "cim_wizard_building_properties",
      "schema": "cim_vector",
      "column": "solar_potential_kwp",
      "type": "Float"
    }
  ],
  "methods": [
    {
      "priority": 1,
      "input_dependencies": ["building_area"],
      "method_name": "estimate_from_area"
    }
  ]
}
```

**c) Restart the backend.**  The startup sync will:
- Run `ALTER TABLE cim_vector.cim_wizard_building_properties ADD COLUMN "solar_potential_kwp" DOUBLE PRECISION` if the column does not yet exist.
- Add a `solar_potential_kwp` entry in `normalization_config.json`.
- Create `data_manager.solar_potential` (FeatureProxy) and
  `data_manager.solar_potential_data` automatically.

No manual migration or model editing required.

#### Alembic (for tracked migrations)

Alembic is configured for cases where you need a reviewable migration
history (column renames, type changes, data backfills):

```bash
# Generate a migration from model changes
alembic revision --autogenerate -m "describe change"

# Apply pending migrations
alembic upgrade head
```

For simple column additions driven by `configuration.json`, the startup
sync handles it and Alembic is not required.

### CIM Wizard Views Endpoint

The unified views module (`app/api/cim_wizard_views.py`) exposes four
endpoints under `/api/v1/cim-wizard`:

| Endpoint | Method | Purpose |
|---|---|---|
| `/calculate` | POST, GET | Single feature calculation |
| `/chainable` | POST | Chain of calculators separated by `\|` |
| `/priority-override` | POST | Runtime method priority override |
| `/list` | GET | List features, pipelines, and endpoints |

Chain format example:
`scenario_geo.calculate_from_scenario_geo|building_height.calculate_from_raster_tiles`

### Core Components (Summary)
- **Pipeline Executor**: Orchestrates feature calculations with fallback
- **Data Manager**: Manages context, configuration, and dynamic feature proxies
- **BaseCalculator**: Parent class for all calculators
- **Calculators**: Individual feature calculation implementations
- **Config Sync** (`app/core/config_sync.py`): Startup hook that syncs DB columns and normalizer from `configuration.json`
- **Normalizer** (`app/core/normalizer.py`): Field-name aliasing and validation, auto-extended at startup
- **Services**: Direct database access layers (census, raster, vector)

### FastAPI vs Django MVT
This FastAPI implementation provides:
- **Async Support**: Better performance for I/O operations
- **Direct Database Access**: No API overhead between services
- **Simplified Requests**: Dict-based API for clarity
- **Auto Documentation**: Interactive API docs at `/docs`

See [docs/fastapi_vs_mvt.md](docs/fastapi_vs_mvt.md) for detailed comparison.

## Development

### Testing
```bash
# Run API tests
python examples/simple_api_usage.py

# Check health
curl http://localhost:8000/health
```

### Docker Deployment

**Full stack** (DB + backend; requires `../cim-database/init-db/init_backup.sql`):
```bash
docker compose up -d --build

# Check status
docker compose ps

# Logs
docker compose logs -f backend
```

**Backend only** (when DB is already running on localhost:15432):
```bash
docker compose -f docker-compose.backend-only.yml up -d --build
```

API docs: http://localhost:8000/docs

## Documentation

- [Architecture Overview](docs/architecture_overview.md)
- [FastAPI vs MVT Comparison](docs/fastapi_vs_mvt.md)
- [OOP Approach](docs/oop_approach.md)
- [Calculator Methods](docs/calculator_methods.md)
- [Service Endpoints](docs/service_endpoints.md)
- [Database Setup Guide](DATABASE_SETUP.md)

## Error Handling

The simplified API includes error comments in the code instead of complex validation:

```python
# Possible errors to handle later:
# - Missing project_id, scenario_id, features
# - Invalid feature names  
# - Database connection issues
# - Calculator execution failures

if not project_id:
    return {"error": "Missing project_id"}
```

This approach prioritizes **clarity and simplicity** over robustness, making the code easy to understand and extend.

---

## Simulator Integration Study

CIM Wizard enriches every building in a scenario with a rich set of physics-relevant features (geometry, height, volume, floors, type, construction year, demographics, envelope efficiency, …).  The natural next step is to pass those features into a **building energy simulator** and optionally couple the resulting load profiles with a **grid simulator** to analyse district-level energy flows.  This section surveys the most prominent tools in both domains and recommends a concrete integration path.

---

### 1  Building Energy Simulators

| Tool | Developer | Scale | Language / API | License | Strengths | Weaknesses |
|---|---|---|---|---|---|---|
| **EnergyPlus** | US DOE | Single building → district | C++, **Python API** (`eppy`, `pyenergyplus`) | Open source (BSD) | Industry gold standard; most validated worldwide; rich HVAC/zone modelling | Steep IDF input format learning curve; single-building per run |
| **OpenStudio / URBANopt** | NREL | District / campus | Ruby SDK, Python bindings, REST API | Open source (BSD) | Wraps EnergyPlus for district scale; grid-interactive DER support; GeoJSON city input | Heavy installation; slower iteration |
| **CESAR-P** | Empa (CH) | District / urban | **Pure Python** library | AGPL-3.0 | Designed for UBEM bottom-up workflows; inputs match CIM Wizard outputs directly; batch EnergyPlus runs | Covers EP 8.5 – 9.5 only; less HVAC detail |
| **CityBES** | LBL | Urban | Web + Python | Open source | CityGML input; energy benchmarking at city scale | Limited HVAC modelling; US-centric data |
| **CitySim Pro** | LESO-PB EPFL | Urban | GUI + XML | Commercial (academic free) | Solar / urban microclimate + thermal; good for dense cities | No Python API; less HVAC detail |
| **TRNSYS** | Univ. Wisconsin | System / district | Fortran + Python co-sim | Commercial | Best-in-class transient HVAC; solar thermal | Expensive; complex; not open source |
| **IDA ICE** | EQUA | Single building | GUI + IESVE-Macro | Commercial | Very detailed; popular in EU research | Closed, expensive, no Python API |
| **Honeybee / Ladybug** | Ladybug Tools | Single building | **Python** (`honeybee-energy`) | Open source (MIT) | Fully Python; wraps EnergyPlus & Radiance; parametric workflows | Designed for individual buildings, not urban batch |

---

### 2  Grid (Electrical Distribution) Simulators

| Tool | Developer | Scale | Language / API | License | Strengths | Weaknesses |
|---|---|---|---|---|---|---|
| **OpenDSS** | EPRI | Distribution network | COM / `py-dss-interface` | Open source | Quasi-static + dynamic LV/MV; widely used by DSOs | COM origin; Windows-first (Linux needs build) |
| **pandapower** | Fraunhofer IEE | Distribution + subtransmission | **Pure Python** | BSD | Pythonic; PostgreSQL-friendly; power flow, OPF, short-circuit | No time-series dynamic simulation |
| **PyPSA** | TU Berlin | Transmission + sector coupling | **Pure Python** | MIT | Multi-energy (heat, gas, H₂); optimisation focus; active dev | Less suited for LV radial feeders |
| **GridLAB-D** | US DOE PNNL | Distribution (smart grid) | C++ + Python | Open source | Time-series quasi-static, EV/DR, feeder automation | Complex input format; US-centric |
| **MATPOWER** | Cornell | Transmission | MATLAB / Python | BSD | Classic OPF benchmark | MATLAB heritage; not suited for Python stacks |

---

### 3  Recommendation & Deep Dive

#### 3.1  Building Energy: CESAR-P + EnergyPlus

**CESAR-P** (Combined Energy Simulation And Retrofitting — Python) is the strongest fit for CIM Wizard integration.

**Installation**
```bash
pip install cesar-p==2.4.0
# EnergyPlus engine (required separately)
# Download from https://energyplus.net/downloads  (v9.4 or v9.5)
# Then:
export ENERGYPLUS_DIR=/usr/local/EnergyPlus-9-5-0
```

**CIM Wizard → CESAR-P input mapping**

| CESAR-P input | CIM Wizard feature | Calculator |
|---|---|---|
| Building footprint polygon | `building_geo` / `building_geo_lod12` | `BuildingGeoCalculator` / `BuildingGeoLod12Calculator` |
| Building height (m) | `building_height` | `BuildingHeightCalculator` |
| Gross floor area (m²) | `building_area` | `BuildingAreaCalculator` |
| Number of floors | `building_n_floors` | `BuildingNFloorsCalculator` |
| Year of construction | `building_construction_year` | `BuildingConstructionYearCalculator` |
| Building type (SFH / MFH / OFFICE …) | `building_type` | `BuildingTypeCalculator` |
| Residential flag | `building_residential_filter` | `BuildingResidentialFilterCalculator` |
| Neighbour footprints (shading) | scenario geometry | `ScenarioGeoCalculator` |

**What EnergyPlus physically simulates**

```
For each thermal zone (one per floor):
  Solar gains     ← irradiance × window area × g-value
  Conduction      ← U-value × ΔT × surface area  (walls, roof, floor, windows)
  Infiltration    ← n50 blower-door value × ΔT
  Ventilation     ← schedule-driven fresh air × heat recovery efficiency
  Internal gains  ← occupancy (80 W/person) + lighting (W/m²) + equipment (W/m²)
  HVAC            ← ideal-load system: exactly the energy to maintain setpoints
  DHW             ← schedule-driven hot water demand (litres/day)
```

**CESAR-P outputs** (annual totals or hourly time series)

| Output | Unit | Description |
|---|---|---|
| `heating_demand_kWh` | kWh/year | Space heating energy (net thermal) |
| `cooling_demand_kWh` | kWh/year | Space cooling energy |
| `dhw_demand_kWh` | kWh/year | Domestic hot water |
| `electricity_demand_kWh` | kWh/year | Lighting + plug loads (SIA 2024 schedules) |
| `total_final_energy_kWh` | kWh/year | Sum of all above |
| `heating_demand_kWh_m2` | kWh/m²·a | Specific heating intensity (for benchmarking) |
| `CO2_kg` | kg CO₂eq/year | Operational carbon (KBOB emission factors) |
| Retrofit results | €, kWh | Cost and savings per retrofit measure |

**Occupancy schedules — SIA 2024 (built-in)**

CESAR-P ships pre-generated schedules for every SIA 2024 building type.  No external download needed.  The schedules encode:

| Schedule | SFH example | MFH example |
|---|---|---|
| Occupancy (fraction present) | 0.5 day / 1.0 night | 0.3 day / 0.8 night |
| Heating setpoint | 20 °C occupied / 16 °C setback | 20 °C / 16 °C |
| Cooling setpoint | 26 °C occupied / 28 °C setback | 26 °C / 28 °C |
| Lighting W/m² | 8 W/m² | 10 W/m² |
| Equipment W/m² | 7 W/m² | 5 W/m² |
| DHW litres/day | 100 L | 60 L/person |

Supported SIA 2024 building types: `SFH`, `MFH`, `OFFICE`, `SCHOOL`, `SHOP`, `RESTAURANT`, `HOSPITAL`, `INDUSTRY`, `SPORTS`, `INDOOR_SWIMMING`.

**Weather files (EPW)**

EPW files contain 8 760 hourly rows with: dry-bulb temp, dew point, humidity, direct/diffuse solar radiation, wind speed, atmospheric pressure.

| Source | Coverage | How to get |
|---|---|---|
| [climate.onebuilding.org](https://climate.onebuilding.org) | 17 000+ stations worldwide (TMYx 2009–2023) | Browse & download ZIP |
| [energyplus.net/weather](https://energyplus.net/weather) | ~3 000 curated stations | Direct EPW download |
| PVGIS (EU JRC) via `pvlib` | Any lat/lon in Europe/Africa/Asia | `pvlib.iotools.get_pvgis_tmy()` |

See `building_simulation/00_weather_downloader.py` for automated download helpers.

**Why not others?**
- *URBANopt* requires a heavy OpenStudio/Ruby stack and a different GeoJSON city format.
- *Honeybee* is designed for single buildings; batch urban runs need extra orchestration.
- *CitySim / TRNSYS / IDA ICE* are commercial or lack a Python API.

---

#### 3.2  Grid Simulation: pandapower (+ OpenDSS for dynamic studies)

**pandapower** (Fraunhofer IEE) is a pure-Python power systems analysis library that reads/writes pandas DataFrames — a natural fit for a PostGIS/SQLAlchemy stack.

**Installation**
```bash
pip install pandapower[all]>=2.14.0
# Optional: for time-series controller API
pip install pandapower[timeseries]
```

**Network elements and their inputs / outputs**

| Element | Key inputs | Key result columns (after `runpp`) |
|---|---|---|
| `bus` | `vn_kv` (nominal voltage), `type` | `vm_pu` (voltage magnitude), `va_degree` (angle), `p_mw`, `q_mvar` |
| `ext_grid` | `vm_pu` setpoint, `va_degree` reference | `p_mw`, `q_mvar` drawn from upstream |
| `line` | `from_bus`, `to_bus`, `length_km`, `std_type` (cable) | `p_from_mw`, `i_from_ka` (current), `loading_percent`, `pl_mw` (losses) |
| `trafo` | `hv_bus`, `lv_bus`, `std_type` (rating) | `p_hv_mw`, `p_lv_mw`, `pl_mw`, `loading_percent` |
| `load` | `bus`, `p_mw`, `q_mvar` | `p_mw`, `q_mvar` (consumed) |
| `sgen` | `bus`, `p_mw` (PV/wind/CHP) | `p_mw`, `q_mvar` (injected) |
| `storage` | `bus`, `p_mw`, `max_e_mwh`, `soc_percent` | `p_mw`, `soc_percent` |
| `gen` | `bus`, `p_mw`, `vm_pu` (voltage-controlled) | `q_mvar`, `va_degree` |

**Standard cable types (built-in to pandapower)**

| `std_type` | Voltage | Application |
|---|---|---|
| `"NAYY 4x50 SE"` | LV (0.4 kV) | Typical suburban residential cable |
| `"NAYY 4x120 SE"` | LV | High-density residential / commercial |
| `"NA2XS2Y 1x95 RM/25 12/20 kV"` | MV (20 kV) | Urban MV distribution |
| `"0.4 MVA 20/0.4 kV"` | — | Standard distribution transformer |
| `"0.63 MVA 20/0.4 kV"` | — | Larger distribution transformer |

**Analyses available**

| Function | Purpose | Typical use |
|---|---|---|
| `pp.runpp(net)` | Newton-Raphson AC power flow | Voltage check, line loading |
| `pp.runopp(net)` | Optimal power flow (minimise cost) | PV curtailment, dispatch optimisation |
| `sc.calc_sc(net)` | Short-circuit IEC 60909 | Fuse / breaker sizing |
| `pp.timeseries.*` | Controller-based time series | 24 h / annual load profiles |
| `pp.topology.*` | Graph analysis | Radial/meshed detection, unsupplied buses |
| `pp.estimation.*` | State estimation | SCADA / smart-meter measurement fusion |

**Key result DataFrames** (after `pp.runpp(net)`)

```python
net.res_bus        # vm_pu, va_degree, p_mw, q_mvar  (per bus)
net.res_line       # p_from_mw, i_from_ka, loading_percent, pl_mw  (per line)
net.res_trafo      # p_hv_mw, p_lv_mw, pl_mw, loading_percent
net.res_load       # p_mw, q_mvar  (what each load consumed)
net.res_sgen       # p_mw, q_mvar  (what each generator injected)
net.res_ext_grid   # p_mw, q_mvar  (import/export from HV grid)
```

**Voltage quality standard (EN 50160)**
- Normal operation: `0.90 ≤ vm_pu ≤ 1.10`
- Line loading alarm threshold: `loading_percent > 80 %`

---

### 4  Sub-project Structure

The simulation sub-projects live in two dedicated folders:

```
cim_wizard_integrated_2026/
├── building_simulation/                 ← CESAR-P + EnergyPlus
│   ├── requirements.txt
│   ├── config/
│   │   └── cesar_p_config.yml           ← main CESAR-P config
│   ├── data/
│   │   ├── SiteVertices_example.csv     ← example building footprints
│   │   ├── BuildingInformation_example.csv
│   │   └── weather/                     ← put your .epw here
│   ├── 00_weather_downloader.py         ← download EPW from onebuilding.org / PVGIS
│   ├── 01_minimal_cesarp_example.py     ← standalone CESAR-P run (no DB)
│   ├── 02_cim_wizard_exporter.py        ← export scenario → CESAR-P CSV inputs
│   └── 03_run_district_simulation.py    ← full pipeline: DB export → simulate → write results
│
└── grid_simulation/                     ← pandapower
    ├── requirements.txt
    ├── 01_minimal_pandapower_example.py ← build LV feeder, power flow, OPF, short-circuit
    ├── 02_cim_wizard_network_builder.py ← build network from cim_vector grid tables
    └── 03_building_loads_on_grid.py     ← assign CESAR-P results as loads → time-series PF
```

**End-to-end pipeline**

```
CIM Wizard DB (PostGIS)
    │
    ▼  building_simulation/02_cim_wizard_exporter.py
SiteVertices.csv + BuildingInformation.csv  ──►  weather .epw
    │
    ▼  building_simulation/03_run_district_simulation.py  (CESAR-P + EnergyPlus)
Hourly load profiles → cim_simulation.building_energy_results
    │
    ▼  grid_simulation/02_cim_wizard_network_builder.py
pandapower network from cim_vector grid tables
    │
    ▼  grid_simulation/03_building_loads_on_grid.py  (pandapower)
Power flow / OPF results → cim_simulation.grid_powerflow_results
```

**Phase 1 — Start here (building energy only)**

```bash
# 1. Download weather
cd building_simulation
python 00_weather_downloader.py

# 2. Test with example data (no DB required)
python 01_minimal_cesarp_example.py

# 3. Export from CIM Wizard and run for real
python 02_cim_wizard_exporter.py --project_id my_project --scenario_id s001
python 03_run_district_simulation.py --project_id my_project --scenario_id s001 \
    --weather ./data/weather/my_city.epw
```

**Phase 2 — Grid coupling (once building results exist)**

```bash
cd grid_simulation

# Test with standalone example
python 01_minimal_pandapower_example.py

# Build grid from CIM Wizard and run power flow
python 02_cim_wizard_network_builder.py --project_id my_project --output ./output/net.json
python 03_building_loads_on_grid.py --project_id my_project --scenario_id s001 \
    --network ./output/net.json
```

---

### 5  Validation Strategy — Grid as a Validator of Building Simulation

#### 5.1  The core question: do you have access to substation consumption data in Turin?

**Short answer: yes — but the path depends on the access tier.**

Turin's electricity distribution network is managed by **IREN Reti Elettriche S.p.A.** (not e-distribuzione, which covers the rest of Italy).  IREN is the successor of the historical city utility ACEA Torino.

| Data tier | Granularity | Access |
|---|---|---|
| **IREN open portal** | Aggregated neighbourhood / census zone level, annual | Public — <https://www.irenenergia.it> (ask the open data desk) |
| **aperTO (Turin municipality)** | Some energy datasets at census zone level | Public — <https://aperto.comune.torino.it> — search `energia` |
| **e-distribuzione e-API** | Smart meter load curves, 15-min resolution | Registered access — <https://e-api.e-distribuzione.it> (covers areas outside Turin city centre) |
| **IREN secondary substation (cabina secondaria) data** | Hourly feeder load at MV/LV substation | **Formal research agreement with IREN** required — contact `opendata@irengruppe.it` |
| **ARERA national statistics** | Municipal-level annual totals by sector | Public — <https://www.arera.it/dati-e-statistiche> |
| **IEEE DataPort — Italian distribution profiles** | 33-node feeder active power profiles (MW), seasonal | Public — <https://ieee-dataport.org/documents/pv-wind-and-load-profiles-italian-distribution-networks> |

**Practical recommendation for Turin:**  Start with the aperTO census-zone energy data or ARERA municipal totals for a coarse validation.  For fine-grained substation-level validation, file a research data agreement with IREN Reti Elettriche.  Italian DSOs are increasingly granting access under the EU Smart Grid Directive and ARERA Resolution 646/2021.

---

#### 5.2  Is the bottom-up → substation comparison a valid validation path?

**Yes — this is a standard, well-established UBEM validation methodology.**  It is used in dozens of peer-reviewed studies and is the recommended approach when individual building meters are unavailable.

The method is called **spatial aggregation validation** (or territory-level calibration):

```
MEASURED  (top-down)
─────────────────────────────────────────────────────────────────────
  IREN/e-distribuzione secondary substation
      │   hourly or 15-min active power (kW) for each feeder
      ▼
  Aggregate to supply area  →  E_measured_substation(t)  [kWh/h]


SIMULATED  (bottom-up)
─────────────────────────────────────────────────────────────────────
  CIM Wizard features (per building)
      │
      ▼  CESAR-P + EnergyPlus
  E_simulated_building_i(t)  [kWh/h per building]
      │
      ▼  sum over all buildings i served by the substation
  E_simulated_substation(t)  [kWh/h]


COMPARISON  (error metrics)
─────────────────────────────────────────────────────────────────────
  E_measured_substation(t)  vs  E_simulated_substation(t)
      │
      ▼
  MBE, CV(RMSE), MAPE, Pearson r  →  is the simulation calibrated?
```

**Why aggregation helps accuracy:**  individual building errors tend to cancel out (some over-, some under-estimated), so substation-level comparisons achieve much lower error than single-building comparisons.  This is why district-scale UBEM validation is more reliable than building-by-building validation.

---

#### 5.3  The disaggregation path (top-down proxy for per-building ground truth)

You described a second, complementary approach:  use the **historic substation total to disaggregate down to individual building loads**, then compare those disaggregated values to the CESAR-P outputs.  This is a valid calibration technique.

```
                    ┌──────────────────────────────────────────────┐
                    │    MEASURED  (substation total)              │
                    │    E_measured_substation(t)                  │
                    └──────────────────┬───────────────────────────┘
                                       │
                        ┌──────────────▼──────────────┐
                        │  DISAGGREGATION ENGINE       │
                        │                              │
                        │  Weight per building i:      │
                        │    w_i = f(floor_area_i,     │
                        │           building_type_i,   │
                        │           n_residents_i,     │
                        │           construction_year) │
                        │                              │
                        │  E_proxy_i(t) =              │
                        │    E_measured(t) × w_i/Σw   │
                        └──────────────┬───────────────┘
                                       │
                        ┌──────────────▼──────────────────────────┐
                        │  COMPARISON per building i               │
                        │  E_proxy_i(t)  vs  E_simulated_i(t)     │
                        │                                          │
                        │  → identify which building types or      │
                        │    construction cohorts are systematically│
                        │    over/under-simulated                  │
                        └──────────────────────────────────────────┘
```

CIM Wizard already calculates all the weights needed:

| Disaggregation weight | CIM Wizard feature |
|---|---|
| Floor area (m²) | `building_area` |
| Building type | `building_type` |
| Number of residents | `building_population` |
| Residential flag | `building_residential_filter` |
| Construction year → efficiency class | `building_construction_year` + `envelope_efficiency` |
| Number of families | `building_n_families` |

The "another service that generates grid by buildings" you mention — if that is the CIM Wizard `FmuAssignCalculator` or a spatial join service — produces exactly the **building → substation assignment** needed to define the supply area boundary.

---

#### 5.4  Critical considerations for a valid comparison

| Issue | Why it matters | How to handle |
|---|---|---|
| **Energy type mismatch** | Substation measures only **electricity**.  CESAR-P outputs heating, cooling, DHW separately.  Heating in Italy is mostly gas, not electric. | Compare only `electricity_demand_kWh` from CESAR-P (lights + plugs + heat pumps) — NOT heating demand unless buildings have heat pumps. |
| **Weather year alignment** | TMY weather ≠ actual weather in the measured year. | Use an actual measured-year EPW (e.g. from Meteonorm or PVGIS for the same calendar year as the measured data). |
| **Supply area boundary** | Simulation must include exactly the buildings served by the substation — no more, no less. | Use the spatial join from `cim_vector.service_points → substations` as the supply area boundary. |
| **Unmetered buildings** | Some buildings (construction sites, vacant, etc.) have no real consumption but appear in geometry. | Filter with `building_residential_filter` and occupancy proxies. |
| **Temporal resolution** | Annual totals hide seasonal and diurnal errors. | Validate at monthly, weekly, and daily level.  ASHRAE 14 requires hourly CV(RMSE). |
| **PV self-consumption** | Buildings with rooftop PV consume less from the grid; substation measures net import, not gross consumption. | Subtract `sgen` PV injection from simulated loads at the substation bus. |
| **EV charging** | Growing electric vehicle load is not modelled in CESAR-P. | Add an EV load layer on top if the measured year is 2022+. |

---

#### 5.5  Accepted error metrics (ASHRAE Guideline 14)

| Metric | Formula | Acceptable threshold |
|---|---|---|
| MBE (Mean Bias Error) | `Σ(E_sim - E_meas) / Σ E_meas` | Annual: **< ±5 %** |
| CV(RMSE) (Coeff. of Variation of RMSE) | `RMSE / mean(E_meas)` | Hourly: **< 30 %**; Monthly: **< 15 %** |
| MAPE | `mean(|E_sim - E_meas| / E_meas)` | Informational (no hard threshold) |
| Pearson r | Correlation of time series | > 0.9 indicates good temporal pattern |

A CV(RMSE) < 15 % monthly with MBE < ±5 % annually is considered a **well-calibrated** district energy model in the literature.

---

#### 5.6  Proposed implementation plan

```python
# grid_simulation/04_substation_validator.py  (to be created)
#
# 1. Load measured substation hourly data from IREN/e-distribuzione CSV
# 2. Load cim_simulation.building_energy_results (from CESAR-P)
# 3. Filter buildings belonging to the substation's supply area
#    (via cim_vector.service_points spatial join)
# 4. Aggregate simulated electricity demand to substation level
# 5. Compute MBE, CV(RMSE), MAPE, Pearson r
# 6. Plot measured vs simulated time series
# 7. Optionally: run disaggregation to get per-building proxy and
#    identify which building types drive the error

import pandas as pd, numpy as np
from sklearn.metrics import mean_squared_error

def cv_rmse(measured, simulated):
    rmse = np.sqrt(mean_squared_error(measured, simulated))
    return rmse / np.mean(measured)

def mbe(measured, simulated):
    return (simulated - measured).sum() / measured.sum()
```

This script will become `grid_simulation/04_substation_validator.py` once the measured data agreement with IREN is in place.

---

### 6  Key References

- EnergyPlus: <https://energyplus.net>
- CESAR-P docs: <https://cesar-p-core.readthedocs.io> | GitHub: <https://github.com/hues-platform/cesar-p-core>
- SIA 2024 schedule reference: <https://cesar-p-core.readthedocs.io/en/latest/features/sia2024.html>
- Weather files: <https://climate.onebuilding.org> | <https://energyplus.net/weather>
- URBANopt: <https://docs.urbanopt.net>
- pandapower docs: <https://pandapower.readthedocs.io> | <https://www.pandapower.org>
- pandapower tutorials: <https://github.com/e2nIEE/pandapower/tree/master/tutorials>
- OpenDSS (`py-dss-interface`): <https://py-dss-interface.readthedocs.io>
- PyPSA: <https://pypsa.readthedocs.io>
- IREN open data: <https://www.irenenergia.it>
- Turin open data portal (aperTO): <https://aperto.comune.torino.it>
- ARERA Italian energy statistics: <https://www.arera.it/dati-e-statistiche>
- IEEE DataPort — Italian distribution profiles: <https://ieee-dataport.org/documents/pv-wind-and-load-profiles-italian-distribution-networks>
- ASHRAE Guideline 14 (calibration standard): <https://www.ashrae.org/technical-resources/bookstore/guideline-14>

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes (following the clarity-first principle)
4. Add error comments for potential issues
5. Submit a pull request

## License

MIT





install environment:
pip install -r requirements.txt
conda activate webgis

sudo docker-compose -f docker-compose.db.yml up -d

docker compose -f docker-compose.db.yml down


export DATABASE_URL="postgresql://cim_wizard_user:cim_wizard_password@localhost:5433/cim_wizard_integrated"

export POSTGRES_HOST="localhost"
export POSTGRES_PORT="5433"
export POSTGRES_DB="cim_wizard_integrated"
export POSTGRES_USER="cim_wizard_user"
export POSTGRES_PASSWORD="cim_wizard_password"

# Then run uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000





DATABASE_URL=postgresql://cim_wizard_user:cim_wizard_password@localhost:5433/cim_wizard_integrated uvicorn main:app --host 0.0.0.0 --port 8000




method1:
# Copy the development environment
cp env.development .env

# Start the application
./start_app.sh dev

method2:
# Set environment variables
export DATABASE_URL="postgresql://user:pass@host:port/db"
export DEBUG=True
export PORT=9000



Method3:
# Override settings for a single run
DATABASE_URL="postgresql://user:pass@host:port/db" PORT=9000 ./start_app.sh dev

for closing the dockerized database session
sudo docker compose -f docker-compose.db.yml down


# Basic shutdown (stops and removes containers)
docker compose -f docker-compose.db.yml down

# Remove volumes as well (⚠️ This will delete your database data!)
docker compose -f docker-compose.db.yml down -v

# Remove images as well
docker compose -f docker-compose.db.yml down --rmi all

# Force remove (doesn't wait for graceful shutdown)
docker compose -f docker-compose.db.yml down --timeout 0

# Remove orphaned containers
docker compose -f docker-compose.db.yml down --remove-orphans