# CIM Wizard - Integrated System Documentation

> **Date:** 2026-02-13  
> **Scope:** Architecture, calculator pipeline, API compliance, deployment  

---

## Table of Contents

- [1. System Overview](#1-system-overview)
- [2. Backend Architecture](#2-backend-architecture)
  - [2.1 Core Pattern: DataManager + PipelineExecutor + Calculators](#21-core-pattern-datamanager--pipelineexecutor--calculators)
  - [2.2 CimWizardDataManager](#22-cimwizarddatamanager)
  - [2.3 CimWizardPipelineExecutor](#23-cimwizardpipelineexecutor)
  - [2.4 Calculators](#24-calculators)
  - [2.5 configuration.json](#25-configurationjson)
  - [2.6 Endpoint Routes](#26-endpoint-routes)
- [3. Calculator Reference](#3-calculator-reference)
  - [3.1 Full Calculator Inventory](#31-full-calculator-inventory)
  - [3.2 Building Analysis Pipeline (9 steps)](#32-building-analysis-pipeline-9-steps)
  - [3.3 Complete Chain Pipeline (16 steps)](#33-complete-chain-pipeline-16-steps)
  - [3.4 What Is Missing from Building Analysis](#34-what-is-missing-from-building-analysis)
- [4. Database Schema](#4-database-schema)
- [5. API Endpoint Reference](#5-api-endpoint-reference)
- [6. Backend Field Normalizer](#6-backend-field-normalizer)
- [7. Issues and Recommendations](#7-issues-and-recommendations)
- [8. Running the System](#8-running-the-system)

---

## 1. System Overview

The CIM Wizard system consists of three interconnected projects:

| Project | Role | Technology | Port |
|---------|------|------------|------|
| **cim-database** | Dockerized PostgreSQL/PostGIS database | PostgreSQL 15 + PostGIS | `15432` |
| **cim_wizard_integrated_2026** | Backend API server | Python / FastAPI / SQLAlchemy | `8000` |
| **coesi-frontend-main_2026** | Frontend web application | React / TypeScript / Vite | `5173` |

```
Client (Frontend / Postman / Script)
         |
         | HTTP/JSON
         v
+---------------------------+
| FastAPI Endpoints         |      app/api/
| (vector_routes,           |      - building_analysis_route.py  (9-step pipeline)
|  building_analysis_route, |      - complete_chain_route.py     (16-step pipeline)
|  complete_chain_route,    |      - pipeline_routes.py          (generic pipeline API)
|  pipeline_routes)         |      - vector_routes.py            (CRUD + schema)
+---------------------------+
         |
         | Creates instances per request
         v
+---------------------------+       +---------------------------+
| CimWizardDataManager      | <---> | CimWizardPipelineExecutor |
| (context, features,       |       | (orchestration, deps,     |
|  configuration, DB)       |       |  calculator loading,      |
+---------------------------+       |  fallback methods)        |
                                    +---------------------------+
                                               |
                    Dynamically loads from configuration.json
                                               |
         +----------+----------+----------+----------+----------+
         |          |          |          |          |          |
     Calculator Calculator Calculator Calculator Calculator  ...
     (height)  (area)    (volume)  (population) (type)     (16 total)
         |          |          |          |          |
         v          v          v          v          v
+------------------------------------------------------------------+
| PostgreSQL/PostGIS (cim_vector, cim_census, cim_raster schemas)  |
+------------------------------------------------------------------+
```

---

## 2. Backend Architecture

### 2.1 Core Pattern: DataManager + PipelineExecutor + Calculators

The backend uses a three-layer pattern:

1. **CimWizardDataManager** -- Holds all state for a single pipeline execution: project/scenario IDs, calculated feature values, database session, and the loaded `configuration.json`.

2. **CimWizardPipelineExecutor** -- Orchestrates calculator execution. It reads `configuration.json` to know which calculator class to load for each feature, resolves dependencies between features, selects the right method (with fallback), and stores results back in the DataManager.

3. **Calculators** -- Independent classes, one per feature. Each calculator receives the PipelineExecutor in its constructor and uses it to read dependencies (`get_feature_safely`) and write results (`data_manager.set_feature`). A calculator can have multiple methods for the same feature (different data sources or algorithms), and the PipelineExecutor picks the right one based on priority or explicit instruction.

4. **Endpoint routes** -- Each FastAPI route creates a fresh DataManager + PipelineExecutor pair, defines a calculation chain (sequence of feature.method steps), and iterates through it. The route also handles saving results to the database.

```
Endpoint function
  |
  +-- Creates DataManager(db_session)
  +-- Creates PipelineExecutor(data_manager)
  +-- Sets context (project_id, scenario_id, boundary)
  +-- Defines calculation_chain = [{feature, method}, ...]
  |
  +-- For each step in chain:
  |     executor.execute_feature(feature_name, method_name)
  |       |
  |       +-- Loads calculator class from configuration.json
  |       +-- Checks dependencies via has_feature() / get_context()
  |       +-- Calls calculator.method()
  |       +-- Stores result in data_manager.calculated_features
  |
  +-- Saves results to database
  +-- Returns JSON response
```

### 2.2 CimWizardDataManager

**File:** `app/core/data_manager.py`

Responsibilities:
- **Context storage:** project_id, scenario_id, db_session, service references
- **Feature storage:** `calculated_features` dict holds all computed values
- **Configuration:** Loads and caches `configuration.json` at init
- **Feature access:** `set_feature()`, `get_feature()`, `has_feature()`
- **Config access:** `get_feature_config(name)`, `get_pipeline_config(name)`

Key methods:

| Method | Purpose |
|--------|---------|
| `set_context(**kwargs)` | Set project_id, scenario_id, db_session, etc. |
| `set_feature(name, value)` | Store a calculated feature result |
| `get_feature(name)` | Retrieve a calculated feature (checks `calculated_features` then `_data` attributes) |
| `has_feature(name)` | Check if a feature has been calculated |
| `get_feature_config(name)` | Get calculator config for a feature from configuration.json |

### 2.3 CimWizardPipelineExecutor

**File:** `app/core/pipeline_executor.py`

Responsibilities:
- **Calculator loading:** Dynamically imports calculator classes using `class_path` and `class_name` from configuration.json. Caches instances in `calculator_cache`.
- **Dependency resolution:** `check_dependencies()` verifies all inputs are available before running a calculator. `_topological_sort()` can order features by dependency graph.
- **Method selection with fallback:** When `execute_feature()` is called without an explicit method, it tries each method defined in configuration.json in priority order until one succeeds.
- **Pipeline execution:** `execute_pipeline()`, `execute_predefined_pipeline()`, `execute_explicit_pipeline()` for batch execution.

Key methods:

| Method | Purpose |
|--------|---------|
| `execute_feature(name, method)` | Run one calculator. If method is specified, only try that. Otherwise try methods in priority order. |
| `check_dependencies(deps)` | Returns True if all dependency features are available |
| `get_calculator_instance(name)` | Load and cache a calculator class from configuration.json |
| `execute_pipeline(features)` | Run multiple features with automatic dependency resolution |
| `execute_predefined_pipeline(name)` | Run a named pipeline from configuration.json `predefined_pipelines` |

**Fallback mechanism:** In configuration.json, each feature can define multiple methods with priorities:

```json
"building_population": {
  "methods": [
    {"priority": 1, "method_name": "calculate_from_volume_distribution",
     "input_dependencies": ["building_volume", "census_population"]},
    {"priority": 2, "method_name": "by_census_osm",
     "input_dependencies": ["scenario_census_boundary", "building_type", "building_volume"]}
  ]
}
```

If priority-1 method fails (e.g., missing `census_population`), the executor falls back to priority-2. This only works when `execute_feature()` is called without an explicit method name.

### 2.4 Calculators

**Directory:** `app/calculators/`

Each calculator is an independent class that:
1. Receives `pipeline_executor` in `__init__`
2. Reads dependencies via `self.pipeline.get_feature_safely(name)`
3. Performs computation
4. Stores result via `self.data_manager.set_feature(name, value)`
5. Returns the result (or None on failure)

Example structure:

```python
class BuildingVolumeCalculator:
    def __init__(self, pipeline_executor):
        self.pipeline = pipeline_executor
        self.data_manager = pipeline_executor.data_manager

    def calculate_from_height_and_area(self):
        heights = self.pipeline.get_feature_safely('building_height')
        areas = self.pipeline.get_feature_safely('building_area')
        filter_res = self.pipeline.get_feature_safely('filter_res')
        # ... compute volumes for residential buildings ...
        self.data_manager.set_feature('building_volume', result)
        return result
```

### 2.5 configuration.json

**File:** `app/core/configuration.json`

This file is the registry for all calculators. It defines:
- **features:** Each feature's calculator class, methods, dependencies, and constraints
- **predefined_pipelines:** Named sequences of features for common tasks
- **global_settings:** Timeouts, retries, caching, validation flags

The PipelineExecutor reads this at runtime to know how to load calculators and what dependencies to check. Adding a new calculator means adding an entry here and placing the Python class in `app/calculators/`.

### 2.6 Endpoint Routes

Three route files define different pipeline entry points:

| Route file | Endpoint | Steps | Purpose |
|------------|----------|-------|---------|
| `building_analysis_route.py` | `POST /api/v1/building/execute_building_analysis` | 16 | Full pipeline: physical properties + demographics + classification + LoD 1.2. Used by frontend. |
| `complete_chain_route.py` | `POST /api/v1/complete/execute_complete_chain` | 16 | **Deprecated.** Older implementation with known bugs (non-UUID IDs, no DB save). Use building_analysis instead. |
| `pipeline_routes.py` | `POST /api/v1/pipeline/execute` | Dynamic | Generic pipeline executor. Client specifies which features to run. |

Each route creates its own DataManager + PipelineExecutor and defines its own calculation chain. The chain is a list of `{feature_name, method_name}` dicts iterated sequentially.

---

## 3. Calculator Reference

### 3.1 Full Calculator Inventory

There are **16 calculators** registered in `configuration.json`. Each one targets specific columns in the database:

| # | Feature Name | Calculator Class | Method(s) | DB Column(s) Populated |
|---|-------------|-----------------|-----------|----------------------|
| 1 | `scenario_geo` | ScenarioGeoCalculator | `calculate_from_scenario_geo`, `calculate_from_buildings_geo` | `project_boundary`, `project_center` on `cim_wizard_project_scenario` |
| 2 | `scenario_census_boundary` | ScenarioCensusBoundaryCalculator | `calculate_from_census_api` | `census_boundary` on `cim_wizard_project_scenario` |
| 3 | `building_geo` | BuildingGeoCalculator | `calculate_from_scenario_census_geo`, `calculate_from_building_geo` | Rows in `cim_wizard_building` (building_id, geometry, source) |
| 4 | `building_props` | BuildingPropsCalculator | `init` | Initializes rows in `cim_wizard_building_properties` (skeleton records) |
| 5 | `building_height` | BuildingHeightCalculator | `calculate_from_raster_tiles` | `height` on `cim_wizard_building_properties` |
| 6 | `building_area` | BuildingAreaCalculator | `calculate_from_geometry` | `area` on `cim_wizard_building_properties` |
| 7 | `filter_res` | BuildingResidentialFilterCalculator | `calculate_filter_res` | `type` on `cim_wizard_building_properties` (residential vs non-residential) |
| 8 | `building_volume` | BuildingVolumeCalculator | `calculate_from_height_and_area` | `volume` on `cim_wizard_building_properties` |
| 9 | `building_n_floors` | BuildingNFloorsCalculator | `estimate_by_height` | `number_of_floors` on `cim_wizard_building_properties` |
| 10 | `census_population` | CensusPopulationCalculator | `calculate_from_census_boundary` | *(intermediate -- total population from census sections)* |
| 11 | `building_type` | BuildingTypeCalculator | `by_census_osm` | `type` on `cim_wizard_building_properties` (TABULA classification) |
| 12 | `building_population` | BuildingPopulationCalculator | `calculate_from_volume_distribution`, `by_census_osm` | `n_people` on `cim_wizard_building_properties` |
| 13 | `building_n_families` | BuildingNFamiliesCalculator | `calculate_from_population`, `by_census_osm` | `n_family` on `cim_wizard_building_properties` |
| 14 | `building_construction_year` | BuildingConstructionYearCalculator | `by_census_osm` | `const_year`, `const_period_census`, `const_tabula` on `cim_wizard_building_properties` |
| 15 | `building_demographic` | BuildingDemographicCalculator | `by_census_osm` | Orchestrates n_people + n_family from census integration |
| 16 | `building_geo_lod12` | BuildingGeoLod12Calculator | `by_footprint_height` | `building_surfaces_lod12` on `cim_wizard_building` (3D geometry) |

### 3.2 Building Analysis Pipeline (16 steps)

**Endpoint:** `POST /api/v1/building/execute_building_analysis`

This is the main pipeline used by the frontend and Postman. It runs all 16 calculators and populates every DB column:

```
Step  Feature                    Method                           DB Column
----  -------------------------  -------------------------------  -------------------------
 1    scenario_geo               calculate_from_scenario_geo      project_boundary, project_center
 2    scenario_census_boundary   calculate_from_census_api        census_boundary
 3    building_geo               calculate_from_scenario_census_geo   cim_wizard_building rows
 4    building_props             init                             building_properties (skeleton)
 5    building_height            calculate_from_raster_tiles      height
 6    building_area              calculate_from_geometry           area
 7    filter_res                 calculate_filter_res             type (residential filter)
 8    building_volume            calculate_from_height_and_area   volume
 9    building_n_floors          estimate_by_height               number_of_floors
10    census_population          calculate_from_census_boundary   (intermediate: total pop)
11    building_type              by_census_osm                    type (TABULA classification)
12    building_population        calculate_from_volume_distribution   n_people
13    building_n_families        calculate_from_population        n_family
14    building_construction_year by_census_osm                    const_year, const_period_census, const_tabula
15    building_demographic       by_census_osm                    (orchestrates n_people + n_family)
16    building_geo_lod12         by_footprint_height              building_surfaces_lod12
```

**Dependency chain for steps 10-16:**

```
census_population
  depends on: scenario_census_boundary

building_population
  depends on: building_volume, census_population

building_n_families
  depends on: building_population

building_construction_year
  depends on: scenario_census_boundary, building_type

building_demographic
  depends on: building_population, building_n_families

building_geo_lod12
  depends on: building_geo, building_height
```

### 3.3 Legacy Complete Chain (deprecated)

**Endpoint:** `POST /api/v1/complete/execute_complete_chain`

This is an older implementation in `complete_chain_route.py`. It has known issues (non-UUID IDs, wrong method names, no DB saving) and should not be used. Use the building analysis endpoint above instead.

---

## 4. Database Schema

### Entity Relationship (Logical)

```
+-----------------------------------------------+
|  cim_vector.cim_wizard_project_scenario       |
|-----------------------------------------------|
|  PK  project_id     VARCHAR(100)              |
|  PK  scenario_id    VARCHAR(100)              |
|      project_name   VARCHAR(255)              |
|      scenario_name  VARCHAR(255)              |
|      project_boundary  GEOMETRY(POLYGON,4326) |
|      project_center    GEOMETRY(POINT,4326)   |
|      project_zoom   INTEGER [default: 15]     |
|      project_crs    INTEGER [default: 4326]   |
|      census_boundary GEOMETRY(MULTIPOLY,4326) |
|      created_at     TIMESTAMP WITH TZ         |
|      updated_at     TIMESTAMP WITH TZ         |
+--------------+--------------------------------+
               | project_id + scenario_id (logical FK)
               v
+-----------------------------------------------+
|  cim_vector.cim_wizard_building_properties    |
|-----------------------------------------------|
|  PK  scenario_id  VARCHAR(100)                |
|  PK  building_id  VARCHAR(100)  ----------+   |
|  PK  lod          INTEGER [default: 0]    |   |
|      project_id   VARCHAR(100)            |   |
|      height       FLOAT                   |   |  <-- building_height calculator
|      area         FLOAT                   |   |  <-- building_area calculator
|      volume       FLOAT                   |   |  <-- building_volume calculator
|      number_of_floors  FLOAT              |   |  <-- building_n_floors calculator
|      type         VARCHAR(50)             |   |  <-- filter_res / building_type calculator
|      const_period_census  VARCHAR(10)     |   |  <-- building_construction_year calculator
|      const_year   INTEGER                 |   |  <-- building_construction_year calculator
|      const_tabula VARCHAR(15)             |   |  <-- building_construction_year calculator
|      n_people     INTEGER                 |   |  <-- building_population calculator
|      n_family     INTEGER                 |   |  <-- building_n_families calculator
|      created_at   TIMESTAMP WITH TZ       |   |
|      updated_at   TIMESTAMP WITH TZ       |   |
+-------------------------------------------+   |
                                                | building_id (logical FK)
                                                v
+-----------------------------------------------+
|  cim_vector.cim_wizard_building               |
|-----------------------------------------------|
|  PK  building_id   VARCHAR(100)               |
|      lod           INTEGER [default: 0]       |
|      building_geometry  GEOMETRY(GEOM,4326)   |  <-- building_geo calculator
|      building_geometry_source  VARCHAR(50)    |
|      census_id     BIGINT  ---------------+   |
|      building_surfaces_lod12   JSON       |   |  <-- building_geo_lod12 calculator
|      created_at    TIMESTAMP WITH TZ      |   |
|      updated_at    TIMESTAMP WITH TZ      |   |
+-------------------------------------------+   |
                                                | census_id = SEZ2011 (logical FK)
                                                v
+-----------------------------------------------+
|  cim_census.censusgeo                         |
|-----------------------------------------------|
|  PK  id       SERIAL                          |
|  UQ  SEZ2011  BIGINT                          |
|      geometry GEOMETRY(MULTIPOLYGON,4326)     |
|      P1..P66  (population columns)            |
|      E1..E31  (building age columns)          |
|      ST1..ST15 (housing stock columns)        |
+-----------------------------------------------+
```

No explicit foreign keys are enforced in the database. All relationships are logical and maintained by application logic.

---

## 5. API Endpoint Reference

### Core Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/api/v1/vector/projects` | List all projects (with pagination) |
| GET | `/api/v1/vector/pscenarios/{project_id}` | Get scenarios for a project |
| GET | `/api/v1/vector/get_buildings_geojson/{project_id}/{scenario_id}` | Get buildings as GeoJSON FeatureCollection |
| GET | `/api/v1/vector/schema` | Get normalization schema (all entities) |
| GET | `/api/v1/vector/schema/{entity_name}` | Get normalization schema for one entity |
| POST | `/api/v1/building/execute_building_analysis` | Create project + run full 16-step pipeline (physical + demographic + 3D) |
| POST | `/api/v1/complete/execute_complete_chain` | *Deprecated* -- use building_analysis endpoint instead |

### Pipeline Endpoints (Generic)

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/v1/pipeline/execute` | Execute pipeline with feature list |
| POST | `/api/v1/pipeline/execute_explicit` | Execute with explicit feature.method plan |
| POST | `/api/v1/pipeline/execute_predefined` | Execute a named pipeline from configuration.json |
| POST | `/api/v1/pipeline/calculate_feature` | Calculate a single feature |
| GET | `/api/v1/pipeline/configuration` | Get full configuration.json |
| GET | `/api/v1/pipeline/available_features` | List available calculated features |
| GET | `/api/v1/pipeline/predefined_pipelines` | List predefined pipelines |

### POST Create Project Request

```
POST /api/v1/building/execute_building_analysis
Content-Type: application/json

{
  "project_boundary": {
    "type": "Feature",
    "geometry": {
      "type": "Polygon",
      "coordinates": [[[lng1, lat1], [lng2, lat2], ..., [lng1, lat1]]]
    },
    "properties": {}
  },
  "project_name": "My Project",
  "scenario_name": "baseline",
  "save_to_db": true
}
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `project_boundary` | GeoJSON Feature | Yes | -- | Polygon boundary in EPSG:4326 |
| `project_name` | string | No | `"Building_Analysis"` | Human-readable project name |
| `scenario_name` | string or null | No | `"baseline"` | If null, defaults to "baseline" with scenario_id = project_id |
| `save_to_db` | boolean | No | `true` | Whether to persist results to database |

---

## 6. Backend Field Normalizer

### Problem

Different clients send the same data using different field names:
- Frontend (React): `projectName`, `scenarioName`, `n_families`
- Postman users: `project_name`, `Project_Name`
- GIS tools / Italian datasets: `altezza_vo`, `superficie`, `epoca_cost`

Without centralized normalization, every client must independently figure out the correct field names, leading to drift and silent data loss.

### Solution: Config-Driven Normalizer

```
app/core/
+-- normalization_config.json   <-- JSON config: canonical names + all known aliases
+-- normalizer.py               <-- Python module: normalize, validate, schema export
```

**On input (POST/PUT):** The normalizer maps any known alias to the canonical name before processing. A client can send `projectName` or `proj_name` or `ProjectName` -- they all resolve to `project_name`.

**On output (GET):** The backend always returns canonical names (matching DB columns). Clients can query the `/schema` endpoint to discover what those names are.

### Schema Discovery Endpoint

Any client can fetch the full normalization schema:

```
GET /api/v1/vector/schema                       -- Full schema (all entities)
GET /api/v1/vector/schema/building_properties   -- Single entity schema
```

### Entities Covered

| Entity | DB Table | Fields | Description |
|--------|----------|--------|-------------|
| `project_scenario` | `cim_vector.cim_wizard_project_scenario` | 11 | Project/scenario metadata + boundaries |
| `building` | `cim_vector.cim_wizard_building` | 8 | Building geometry records |
| `building_properties` | `cim_vector.cim_wizard_building_properties` | 15 | Physical + demographic properties per scenario |

### Adding New Aliases

Edit `normalization_config.json`:

```json
"height": {
  "aliases": ["Height", "altezza_vo", "building_height", "h",
              "NEW_ALIAS_HERE"]
}
```

No Python code changes needed. Restart the server or call `reload_config()`.

---

## 7. Issues and Recommendations

### Critical Issues

| # | Issue | Location | Impact | Status |
|---|-------|----------|--------|--------|
| 1 | `filter_res` column missing in DB model | `vector.py`, `building_analysis_route.py` | Residential filter results never saved to DB | TODO: Add `filter_res = Column(Boolean)` to BuildingProperties model |
| 2 | `complete_chain_route.py` is deprecated | `complete_chain_route.py` | Non-UUID IDs, no DB saving, wrong method names | Use `building_analysis_route.py` which now runs all 16 steps |

### Minor Issues

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 5 | No explicit foreign keys in DB | cim-database schema | No referential integrity enforcement |
| 6 | Frontend normalizer field mismatches | `normalizers.ts` | Frontend should call `GET /schema` to get canonical names |

---

## 8. Running the System

### Prerequisites
- Docker and Docker Compose
- Python 3.10+ with conda or pip
- Node.js 18+

### 1. Start the Database
```bash
cd cim-database
docker compose -f docker-compose.cimdb.yml up -d
# Verify: docker logs cim-integrateddb --tail 20
```

### 2. Start the Backend
```bash
cd cim_wizard_integrated_2026
conda env create -f environment.yml
conda activate cim_wizard
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# API docs at: http://localhost:8000/docs
```

### 3. Start the Frontend
```bash
cd coesi-frontend-main_2026
npm install
npm run dev
# Frontend at: http://localhost:5173
```

### Environment Variables

**Frontend** (`.env` in `coesi-frontend-main_2026/`):
```
VITE_CIM_WIZARD_BASE=http://localhost:8000
```

**Backend** (environment or `.env`):
```
DATABASE_URL=postgresql://cim_wizard_user:cim_wizard_password@localhost:15432/cim_wizard_integrated
```

### Connection Summary

| Service | Host | Port | Credentials |
|---------|------|------|-------------|
| PostgreSQL/PostGIS | localhost | 15432 | `cim_wizard_user` / `cim_wizard_password` |
| FastAPI Backend | localhost | 8000 | -- |
| React Frontend | localhost | 5173 | -- |
