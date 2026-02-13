# CIM Wizard - Integrated System Compliance Report

> **Date:** 2026-02-13  
> **Scope:** Cross-project API compliance analysis for the 4 core workflows  

---

## Table of Contents

- [1. Architecture Overview](#1-architecture-overview)
- [2. Project Structure](#2-project-structure)
- [3. Endpoint Compliance Analysis](#3-endpoint-compliance-analysis)
  - [3.1 GET Projects](#31-get-projects)
  - [3.2 POST Create Project by Boundary](#32-post-create-project-by-boundary)
  - [3.3 GET Project Scenarios](#33-get-project-scenarios)
  - [3.4 GET Project Scenario Buildings](#34-get-project-scenario-buildings)
- [4. Data Flow Diagrams](#4-data-flow-diagrams)
- [5. Database Schema](#5-database-schema)
- [6. Issues & Recommendations](#6-issues--recommendations)
- [7. Running the System](#7-running-the-system)

---

## 1. Architecture Overview

The CIM Wizard system consists of three interconnected projects:

| Project | Role | Technology | Port |
|---------|------|------------|------|
| **cim-database** | Dockerized PostgreSQL/PostGIS database | PostgreSQL 15 + PostGIS | `15432` |
| **cim_wizard_integrated_2026** | Backend API server | Python / FastAPI / SQLAlchemy | `8000` |
| **coesi-frontend-main_2026** | Frontend web application | React / TypeScript / Vite | `5173` |

```
┌───────────────────┐       HTTP/JSON        ┌──────────────────────────┐     SQLAlchemy      ┌─────────────────────┐
│                   │ ────────────────────▶  │                          │ ──────────────────▶ │                     │
│  coesi-frontend   │                        │  cim_wizard_integrated   │                     │    cim-database      │
│  (React/TS)       │ ◀────────────────────  │  (FastAPI)               │ ◀────────────────── │    (PostGIS)         │
│  :5173            │       JSON responses   │  :8000                   │    Query results    │    :15432            │
└───────────────────┘                        └──────────────────────────┘                     └─────────────────────┘
```

---

## 2. Project Structure

### cim-database/
```
cim-database/
├── Dockerfile                          # Base: taherdoust/cim:vector-census-raster-sansalva-purged
├── docker-compose.cimdb.yml            # Docker Compose (port 15432, persistent volume)
├── init-db/
│   ├── 00-restore-backup.sh            # Auto-restore backup on first startup
│   └── 01-init-schemas.sql             # Creates schemas: cim_vector, cim_census, cim_raster
├── populate_censusgeo.sql              # Census geometry data population
├── verify_census_schema.sql            # Schema verification queries
├── load_dsm.py                         # DSM raster loader script
└── create_backup.sh                    # Backup utility
```

### cim_wizard_integrated_2026/
```
cim_wizard_integrated_2026/
├── main.py                              # FastAPI app entry point
├── app/
│   ├── api/
│   │   ├── vector_routes.py             # GET /projects, /pscenarios, /get_buildings_geojson
│   │   ├── building_analysis_route.py   # POST /execute_building_analysis
│   │   ├── census_routes.py             # Census API endpoints
│   │   ├── raster_routes.py             # Raster API endpoints
│   │   ├── pipeline_routes.py           # Pipeline execution
│   │   └── complete_chain_route.py      # Complete chain execution
│   ├── models/
│   │   └── vector.py                    # SQLAlchemy models (ProjectScenario, Building, BuildingProperties)
│   ├── db/
│   │   └── database.py                  # DB connection (postgresql://...@localhost:15432/cim_wizard_integrated)
│   ├── core/
│   │   ├── settings.py                  # App settings
│   │   ├── data_manager.py              # CIM data manager
│   │   └── pipeline_executor.py         # Pipeline executor
│   ├── calculators/                     # Building analysis calculators
│   └── services/                        # Service layer
├── Dockerfile
├── docker-compose.db.yml
└── docker-compose.prod.yml
```

### coesi-frontend-main_2026/
```
coesi-frontend-main_2026/
├── src/
│   ├── config/
│   │   └── apiConfig.ts                 # API base URLs and endpoint definitions
│   ├── services/
│   │   └── cimWizard.ts                 # API service layer (getProjects, getScenarios, etc.)
│   ├── pages/
│   │   ├── Projects.tsx                 # Projects listing page
│   │   ├── Scenarios.tsx                # Scenarios listing page
│   │   └── InputEditor.tsx              # Building data editor
│   ├── components/
│   │   └── Projects/
│   │       └── ProjectGeoForm.jsx       # Project creation form (polygon draw / GeoJSON upload)
│   ├── lib/buildings/
│   │   ├── normalizers.ts               # Building data normalizer
│   │   └── useBuildingsData.ts          # Buildings React hook
│   └── slices/
│       └── scenarioLayersSlice.ts       # Redux state for GeoJSON layers
├── package.json
├── vite.config.ts
└── Dockerfile
```

---

## 3. Endpoint Compliance Analysis

### 3.1 GET Projects

> **Purpose:** Fetch all existing projects for display on the Projects page.

| Layer | Detail |
|-------|--------|
| **Frontend** | `getProjects()` → `GET {base}/api/v1/vector/projects` |
| **Backend** | `GET /api/v1/vector/projects` with `?limit=100&offset=0` |
| **Database** | `SELECT * FROM cim_vector.cim_wizard_project_scenario LIMIT :limit OFFSET :offset` |

#### Request Comparison

| Parameter | Frontend Sends | Backend Expects | Match |
|-----------|---------------|-----------------|-------|
| Method | `GET` | `GET` | ✅ |
| URL | `/api/v1/vector/projects` | `/api/v1/vector/projects` | ✅ |
| `limit` | *(not sent)* | `Query(100, ge=1, le=1000)` — defaults to 100 | ✅ Default works |
| `offset` | *(not sent)* | `Query(0, ge=0)` — defaults to 0 | ✅ Default works |

#### Response Comparison

| Field | Backend Returns | Frontend `ProjectScenario` Interface | DB Column | Compliant |
|-------|----------------|--------------------------------------|-----------|-----------|
| `project_id` | `str` | `project_id: string` | `VARCHAR(100)` PK | ✅ |
| `scenario_id` | `str` | `scenario_id: string` | `VARCHAR(100)` PK | ✅ |
| `project_name` | `str` | `project_name?: string` | `VARCHAR(255)` | ✅ |
| `scenario_name` | `str` | `scenario_name?: string` | `VARCHAR(255)` | ✅ |
| `project_boundary` | GeoJSON Polygon `dict` | `project_boundary?: any` | `GEOMETRY(POLYGON, 4326)` | ✅ |
| `project_center` | GeoJSON Point `dict` | `project_center?: any` | `GEOMETRY(POINT, 4326)` | ✅ |
| `project_zoom` | `int` | ⚠️ **Not in interface** | `INTEGER default 15` | ⚠️ Missing from TS type |
| `project_crs` | `int` | ⚠️ **Not in interface** | `INTEGER default 4326` | ⚠️ Missing from TS type |
| `created_at` | `datetime` | ⚠️ **Not in interface** | `TIMESTAMP WITH TIME ZONE` | ⚠️ Missing from TS type |
| `updated_at` | `datetime` | ⚠️ **Not in interface** | `TIMESTAMP WITH TIME ZONE` | ⚠️ Missing from TS type |
| `census_boundary` | *(not returned)* | *(not expected)* | `GEOMETRY(MULTIPOLYGON, 4326)` | ✅ Intentionally excluded |

#### Verdict: ✅ COMPLIANT (with minor type gaps)

**Notes:**
- The frontend `ProjectScenario` interface is incomplete — it omits `project_zoom`, `project_crs`, `created_at`, and `updated_at`. However, these fields **are accessed** in the component code via `proj.updated_at`, `proj.created_at`, etc. This works at runtime because TypeScript's structural typing doesn't prevent accessing untyped fields on `any`-like objects, but it lacks type safety.
- The frontend does not send `limit`/`offset` query params; the backend defaults handle this correctly.
- `project_center` coordinates are accessed as `proj.project_center?.coordinates?.[0]` (lng) and `[1]` (lat), which matches the GeoJSON Point format returned by the backend.

---

### 3.2 POST Create Project by Boundary

> **Purpose:** Create a new project with a geographic boundary, triggering building analysis pipeline.

| Layer | Detail |
|-------|--------|
| **Frontend** | `createBaselineScenario(payload)` → `POST {base}/api/v1/building/execute_building_analysis` |
| **Backend** | `POST /api/v1/building/execute_building_analysis` |
| **Database** | INSERTs into `cim_wizard_project_scenario`, `cim_wizard_building`, `cim_wizard_building_properties` |

#### Request Comparison

| Field | Frontend Sends | Backend Expects | Match |
|-------|---------------|-----------------|-------|
| Method | `POST` | `POST` | ✅ |
| URL | `/api/v1/building/execute_building_analysis` | `/api/v1/building/execute_building_analysis` | ✅ |
| Content-Type | `application/json` | `dict = Body(...)` | ✅ |
| `project_boundary` | GeoJSON `Feature` (Polygon) | GeoJSON Feature or FeatureCollection | ✅ |
| `project_name` | `string` (from form input) | `str`, default `"Building_Analysis"` | ✅ |
| `scenario_name` | `"baseline"` | `str`, null → defaults to `"baseline"` | ✅ |
| `save_to_db` | `true` | `bool`, default `True` | ✅ |

#### Frontend Request Body (from `ProjectGeoForm.jsx`)
```json
{
  "project_boundary": {
    "type": "Feature",
    "geometry": {
      "type": "Polygon",
      "coordinates": [[[lng1, lat1], [lng2, lat2], ..., [lng1, lat1]]]
    },
    "properties": {}
  },
  "project_name": "User-provided name",
  "scenario_name": "baseline",
  "save_to_db": true
}
```

#### Response Comparison

| Field | Backend Returns | Frontend Expects | Match |
|-------|----------------|------------------|-------|
| `project_id` | `str` (UUID) | Reads `response.project_id` | ✅ |
| `scenario_id` | `str` (UUID) | *(not explicitly read)* | ✅ |
| `project_name` | `str` | *(not explicitly read)* | ✅ |
| `scenario_name` | `str` | *(not explicitly read)* | ✅ |
| `execution_chain` | `list[dict]` | *(not explicitly read)* | ✅ |
| `summary` | `dict` | *(not explicitly read)* | ✅ |
| `metadata` | `dict` | *(not explicitly read)* | ✅ |

#### Database Operations (triggered by backend)

| Step | Table | Operation |
|------|-------|-----------|
| 1. `scenario_geo` | `cim_vector.cim_wizard_project_scenario` | INSERT with project_boundary, project_center (centroid) |
| 2. `building_geo` | `cim_vector.cim_wizard_building` | INSERT per building (geometry + source) |
| 3. `building_height` | `cim_vector.cim_wizard_building_properties` | UPDATE/INSERT height values |
| 4. `building_area` | `cim_vector.cim_wizard_building_properties` | UPDATE area values |
| 5. `filter_res` | `cim_vector.cim_wizard_building_properties` | ⚠️ Attempts to set `filter_res` attribute |
| 6. `building_volume` | `cim_vector.cim_wizard_building_properties` | UPDATE volume values |
| 7. `building_n_floors` | `cim_vector.cim_wizard_building_properties` | UPDATE number_of_floors values |

#### Verdict: ✅ COMPLIANT (with one backend bug)

**Notes:**
- The frontend only reads `response.project_id` and uses it to navigate to the scenarios page. All other response fields are logged but not consumed.
- **BUG:** In `building_analysis_route.py` line 281, the code sets `building_props.filter_res = bool(property_values[i])` but the `BuildingProperties` SQLAlchemy model has **no `filter_res` column**. The `type` column (VARCHAR 50) is where residential/non-residential classification should be stored. This means the `filter_res` calculation result is **never persisted to the database**.

---

### 3.3 GET Project Scenarios

> **Purpose:** Fetch all scenarios belonging to a specific project.

| Layer | Detail |
|-------|--------|
| **Frontend** | `getScenarios(projectId)` → `GET {base}/api/v1/vector/pscenarios/{project_id}` |
| **Backend** | `GET /api/v1/vector/pscenarios/{project_id}` |
| **Database** | `SELECT * FROM cim_vector.cim_wizard_project_scenario WHERE project_id = :project_id` |

#### Request Comparison

| Parameter | Frontend Sends | Backend Expects | Match |
|-----------|---------------|-----------------|-------|
| Method | `GET` | `GET` | ✅ |
| URL | `/api/v1/vector/pscenarios/{projectId}` | `/api/v1/vector/pscenarios/{project_id}` | ✅ |
| `project_id` | Path parameter (string) | Path parameter (str) | ✅ |

#### Response Comparison

Same response schema as [GET Projects](#31-get-projects) — the backend serializes `ProjectScenario` objects identically.

| Field | Backend Returns | Frontend Expects | Match |
|-------|----------------|------------------|-------|
| `project_id` | `str` | `ProjectScenario.project_id: string` | ✅ |
| `scenario_id` | `str` | `ProjectScenario.scenario_id: string` | ✅ |
| `project_name` | `str` | `ProjectScenario.project_name?: string` | ✅ |
| `scenario_name` | `str` | `ProjectScenario.scenario_name?: string` | ✅ |
| `project_boundary` | GeoJSON Polygon | `project_boundary?: any` | ✅ |
| `project_center` | GeoJSON Point | `project_center?: any` | ✅ |
| `project_zoom` | `int` | ⚠️ Not in interface | ⚠️ Missing from TS type |
| `project_crs` | `int` | ⚠️ Not in interface | ⚠️ Missing from TS type |
| `created_at` | `datetime` | ⚠️ Not in interface (but used in code) | ⚠️ Missing from TS type |
| `updated_at` | `datetime` | ⚠️ Not in interface (but used in code) | ⚠️ Missing from TS type |

#### Error Handling

| Scenario | Backend | Frontend |
|----------|---------|----------|
| Project not found | HTTP 404 `"Project not found"` | Caught by `!resp.ok` check, throws Error | ✅ |
| Database error | HTTP 500 `"Database error: ..."` | Caught by `!resp.ok` check, throws Error | ✅ |
| Network failure | N/A | Catches `TypeError("Failed to fetch")`, shows connection error | ✅ |

#### Verdict: ✅ COMPLIANT (same type gaps as GET Projects)

---

### 3.4 GET Project Scenario Buildings

> **Purpose:** Fetch all buildings for a project scenario as a GeoJSON FeatureCollection.

| Layer | Detail |
|-------|--------|
| **Frontend** | `getBuildingsGeoJSON(projectId, scenarioId)` → `GET {base}/api/v1/vector/get_buildings_geojson/{project_id}/{scenario_id}` |
| **Backend** | `GET /api/v1/vector/get_buildings_geojson/{project_id}/{scenario_id}` |
| **Database** | JOIN `cim_wizard_building_properties` ⟷ `cim_wizard_building` ON `building_id`, filtered by `project_id`, `scenario_id`, `lod` |

#### Request Comparison

| Parameter | Frontend Sends | Backend Expects | Match |
|-----------|---------------|-----------------|-------|
| Method | `GET` | `GET` | ✅ |
| URL | `/api/v1/vector/get_buildings_geojson/{projectId}/{scenarioId}` | `/api/v1/vector/get_buildings_geojson/{project_id}/{scenario_id}` | ✅ |
| `project_id` | Path param (string) | Path param (str) | ✅ |
| `scenario_id` | Path param (string) | Path param (str) | ✅ |
| `lod` | *(not sent)* | `Query(0)` — defaults to 0 | ✅ Default works |

#### Response Structure Comparison

**Backend returns:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Polygon", "coordinates": [...] },
      "properties": {
        "building_id": "uuid-string",
        "lod": 0,
        "height": 12.5,
        "area": 250.0,
        "volume": 3125.0,
        "type": "residential",
        "n_people": 15,
        "n_family": 5,
        "number_of_floors": 4.0,
        "const_year": 1970,
        "const_period_census": "1961-70"
      }
    }
  ]
}
```

**Frontend `BuildingFeature` interface:**
```typescript
interface BuildingFeature {
  type: 'Feature';
  geometry: any;
  properties: {
    building_id: string;
    lod?: number;
    height?: number;
    area?: number;
    volume?: number;
    filter_res?: boolean;    // ⚠️ Not returned by backend
    n_people?: number;
    n_family?: number;
    [key: string]: any;      // Catch-all for extra fields
  };
}
```

#### Building Normalizer Mapping (Frontend → Backend)

The frontend normalizes building properties through `normalizeBuilding()` in `normalizers.ts`. Here is the field mapping analysis:

| Frontend Field | Normalizer Looks For | Backend Returns | Compliant |
|----------------|---------------------|-----------------|-----------|
| `id` | `'ID', 'id', 'Id', 'fid'` | `building_id` | ❌ **MISMATCH** — backend key `building_id` is not in lookup list |
| `height` | `'Height', 'altezza_vo', 'height'` | `height` | ✅ |
| `surface_area` | `'Surface Area', 'superficie', 'surface_area'` | `area` | ❌ **MISMATCH** — backend returns `area`, not `surface_area` |
| `usage_category` | `'Usage Category', 'categ_uso', 'usage_category'` | `type` | ❌ **MISMATCH** — backend returns `type`, not `usage_category` |
| `construction_period` | `'Construction Period', 'epoca_cost', 'construction_period'` | `const_period_census` | ❌ **MISMATCH** — backend returns `const_period_census` |
| `number_of_floors` | `'Number of Floors', 'num_piani', 'number_of_floors'` | `number_of_floors` | ✅ |
| `section_number` | `'Section Number', 'nsez', 'section_number'` | *(not returned)* | ⚠️ Field not available |
| `net_leased_area` | `'Net Leased Area', 'net_leased_area'` | *(not returned)* | ⚠️ Field not available |
| `total_floors` | `'Total Floors', 'number_of_floors', 'total_floors'` | `number_of_floors` | ✅ (matched via `number_of_floors`) |
| `net_leased_volume` | `'Net Leased Volume', 'net_leased_volume'` | *(not returned)* | ⚠️ Field not available |
| `usage_type` | `'Usage Type', 'usage', 'usage_type'` | `type` | ❌ **MISMATCH** — backend returns `type`, not `usage` or `usage_type` |
| `year` | `'Year', 'year'` | `const_year` | ❌ **MISMATCH** — backend returns `const_year`, not `year` |
| `number_of_people` | `'Number of People', 'n_people'` | `n_people` | ✅ (matched via `n_people`) |
| `number_of_families` | `'Number of Families', 'n_families'` | `n_family` | ❌ **MISMATCH** — backend returns `n_family` (singular), normalizer expects `n_families` (plural) |
| `building_type` | `'Building Type', 'tab_type', 'building_type'` | *(not returned)* | ⚠️ Field not available |

#### Verdict: ⚠️ PARTIALLY COMPLIANT — 7 field mapping mismatches

**Critical issues:**
1. **`id` field:** The normalizer cannot find the building identifier because backend returns `building_id` but normalizer looks for `ID`, `id`, `Id`, or `fid`. All buildings will have `id: undefined`.
2. **`surface_area`:** Backend returns `area` but normalizer expects `surface_area`. Building areas will be `undefined`.
3. **`usage_category` and `usage_type`:** Backend returns `type` but normalizer doesn't look for that key.
4. **`construction_period`:** Backend returns `const_period_census` but normalizer expects `construction_period`.
5. **`year`:** Backend returns `const_year` but normalizer expects `year`.
6. **`number_of_families`:** Backend returns `n_family` (singular) but normalizer expects `n_families` (plural).
7. **`filter_res`:** Frontend interface expects it, backend doesn't return it, and the database column doesn't exist.

---

## 4. Data Flow Diagrams

### GET Projects Flow
```
Frontend (Projects.tsx)              Backend (vector_routes.py)           Database (cim_vector)
────────────────────────             ─────────────────────────            ─────────────────────
                                                                         
getProjects()                                                            
  │                                                                      
  ├─▶ GET /api/v1/vector/projects                                        
  │                                  @router.get("/projects")            
  │                                    │                                 
  │                                    ├─▶ db.query(ProjectScenario)     
  │                                    │     .offset(0).limit(100)       
  │                                    │                                  cim_wizard_project_scenario
  │                                    │                                  ├── project_id (PK)
  │                                    │                                  ├── scenario_id (PK)
  │                                    │                                  ├── project_name
  │                                    │                                  ├── project_boundary → GeoJSON
  │                                    │                                  └── project_center → GeoJSON
  │                                    │                                 
  │                                    ◀── serialized list               
  ◀── ProjectScenario[]                                                  
  │                                                                      
  └─▶ Transform to ProjectDisplayData                                    
        → ProjPreview cards                                              
```

### POST Create Project Flow
```
Frontend (ProjectGeoForm.jsx)         Backend (building_analysis_route.py)    Database (cim_vector)
─────────────────────────────         ──────────────────────────────────      ─────────────────────

User draws polygon / uploads GeoJSON
  │
  └─▶ createBaselineScenario({
        project_boundary: GeoJSON Feature,
        project_name: "...",
        scenario_name: "baseline",
        save_to_db: true
      })
        │
        ├─▶ POST /api/v1/building/execute_building_analysis
        │                              @router.post("/execute_building_analysis")
        │                                │
        │                                ├── Generate UUID (project_id = scenario_id)
        │                                ├── Step 1: scenario_geo
        │                                │     └─▶ INSERT cim_wizard_project_scenario
        │                                ├── Step 2: scenario_census_boundary
        │                                ├── Step 3: building_geo
        │                                │     └─▶ INSERT cim_wizard_building (per building)
        │                                ├── Step 4: building_props (init)
        │                                ├── Step 5: building_height
        │                                │     └─▶ UPSERT cim_wizard_building_properties.height
        │                                ├── Step 6: building_area
        │                                │     └─▶ UPSERT cim_wizard_building_properties.area
        │                                ├── Step 7: filter_res
        │                                │     └─▶ ⚠️ Attempts filter_res (no DB column)
        │                                ├── Step 8: building_volume
        │                                │     └─▶ UPSERT cim_wizard_building_properties.volume
        │                                └── Step 9: building_n_floors
        │                                      └─▶ UPSERT cim_wizard_building_properties.number_of_floors
        │
        ◀── { project_id: "uuid", ... }
        │
        └─▶ navigate(/scenarios/:projectId)
```

---

## 5. Database Schema

### Entity Relationship (Logical)

```
┌───────────────────────────────────────────────┐
│  cim_vector.cim_wizard_project_scenario       │
├───────────────────────────────────────────────┤
│  PK  project_id     VARCHAR(100)              │
│  PK  scenario_id    VARCHAR(100)              │
│      project_name   VARCHAR(255)              │
│      scenario_name  VARCHAR(255)              │
│      project_boundary  GEOMETRY(POLYGON,4326) │
│      project_center    GEOMETRY(POINT,4326)   │
│      project_zoom   INTEGER [default: 15]     │
│      project_crs    INTEGER [default: 4326]   │
│      census_boundary GEOMETRY(MULTIPOLY,4326) │
│      created_at     TIMESTAMP WITH TZ         │
│      updated_at     TIMESTAMP WITH TZ         │
└──────────────┬────────────────────────────────┘
               │ project_id + scenario_id (logical FK)
               ▼
┌───────────────────────────────────────────────┐
│  cim_vector.cim_wizard_building_properties    │
├───────────────────────────────────────────────┤
│  PK  scenario_id  VARCHAR(100)                │
│  PK  building_id  VARCHAR(100)  ──────────┐   │
│  PK  lod          INTEGER [default: 0]    │   │
│      project_id   VARCHAR(100)            │   │
│      height       FLOAT                   │   │
│      area         FLOAT                   │   │
│      volume       FLOAT                   │   │
│      number_of_floors  FLOAT              │   │
│      type         VARCHAR(50)             │   │
│      const_period_census  VARCHAR(10)     │   │
│      const_year   INTEGER                 │   │
│      const_tabula VARCHAR(15)             │   │
│      n_people     INTEGER                 │   │
│      n_family     INTEGER                 │   │
│      created_at   TIMESTAMP WITH TZ       │   │
│      updated_at   TIMESTAMP WITH TZ       │   │
└───────────────────────────────────────────┘   │
                                                │ building_id (logical FK)
                                                ▼
┌───────────────────────────────────────────────┐
│  cim_vector.cim_wizard_building               │
├───────────────────────────────────────────────┤
│  PK  building_id   VARCHAR(100)               │
│      lod           INTEGER [default: 0]       │
│      building_geometry  GEOMETRY(GEOM,4326)   │
│      building_geometry_source  VARCHAR(50)    │
│      census_id     BIGINT  ───────────────┐   │
│      building_surfaces_lod12   JSON       │   │
│      created_at    TIMESTAMP WITH TZ      │   │
│      updated_at    TIMESTAMP WITH TZ      │   │
└───────────────────────────────────────────┘   │
                                                │ census_id = SEZ2011 (logical FK)
                                                ▼
┌───────────────────────────────────────────────┐
│  cim_census.censusgeo                         │
├───────────────────────────────────────────────┤
│  PK  id       SERIAL                          │
│  UQ  SEZ2011  BIGINT                          │
│      geometry GEOMETRY(MULTIPOLYGON,4326)     │
│      (population, housing, building age cols) │
└───────────────────────────────────────────────┘
```

> **Note:** No explicit foreign keys are enforced in the database. All relationships are logical and maintained by application logic.

---

## 6. Issues & Recommendations

### Critical Issues

| # | Issue | Location | Impact | Recommendation |
|---|-------|----------|--------|----------------|
| 1 | **Building `id` normalizer mismatch** | `normalizers.ts` line 44 | Buildings cannot be identified — `id` is always `undefined` | Add `'building_id'` to the lookup list: `get('building_id', 'ID', 'id', 'Id', 'fid')` |
| 2 | **`surface_area` normalizer mismatch** | `normalizers.ts` line 46 | Building areas always `undefined` | Add `'area'` to lookup: `get('Surface Area', 'superficie', 'surface_area', 'area')` |
| 3 | **`filter_res` column missing** | `building_analysis_route.py` line 281 | Residential filter results never saved to DB | Either add `filter_res = Column(Boolean)` to `BuildingProperties` model, or save to the `type` column |
| 4 | **`n_family` vs `n_families` mismatch** | `normalizers.ts` line 57 | Family count always `undefined` | Add `'n_family'` to lookup: `get('Number of Families', 'n_families', 'n_family')` |
| 5 | **`year` vs `const_year` mismatch** | `normalizers.ts` line 55 | Construction year always `undefined` | Add `'const_year'` to lookup: `get('Year', 'year', 'const_year')` |
| 6 | **`usage_category` vs `type` mismatch** | `normalizers.ts` line 47 | Usage category always `undefined` | Add `'type'` to lookup: `get('Usage Category', 'categ_uso', 'usage_category', 'type')` |
| 7 | **`construction_period` vs `const_period_census`** | `normalizers.ts` line 48 | Construction period always `undefined` | Add `'const_period_census'` to lookup |

### Minor Issues

| # | Issue | Location | Impact | Recommendation |
|---|-------|----------|--------|----------------|
| 8 | **Incomplete `ProjectScenario` TS interface** | `cimWizard.ts` lines 3-11 | Missing `project_zoom`, `project_crs`, `created_at`, `updated_at` | Add fields to interface for type safety |
| 9 | **No pagination on frontend** | `Projects.tsx` line 116 | Always fetches up to 100 projects (default limit) | Add pagination support for large project lists |
| 10 | **No explicit foreign keys in DB** | `cim-database` schema | No referential integrity enforcement | Consider adding FK constraints with ON DELETE CASCADE |
| 11 | **`usage_type` normalizer** | `normalizers.ts` line 54 | Backend returns `type` but normalizer looks for `usage`, `usage_type` | Add `'type'` to lookup list |

### Recommended Fix for `normalizers.ts`

```typescript
export function normalizeBuilding(raw: any): Building {
  const p = raw || {};
  const get = (...keys: string[]) => keys.find(k => p[k] !== undefined) ? p[keys.find(k => p[k] !== undefined)!] : undefined;
  return {
    id: get('building_id', 'ID', 'id', 'Id', 'fid') ?? p.id,
    height: nf(get('Height', 'altezza_vo', 'height')),
    surface_area: nf(get('Surface Area', 'superficie', 'surface_area', 'area')),
    usage_category: ns(get('Usage Category', 'categ_uso', 'usage_category', 'type')),
    construction_period: ns(get('Construction Period', 'epoca_cost', 'construction_period', 'const_period_census')),
    number_of_floors: ns(get('Number of Floors', 'num_piani', 'number_of_floors')),
    section_number: get('Section Number', 'nsez', 'section_number'),
    net_leased_area: nf(get('Net Leased Area', 'net_leased_area')),
    total_floors: nf(get('Total Floors', 'number_of_floors', 'total_floors')),
    net_leased_volume: nf(get('Net Leased Volume', 'net_leased_volume')),
    usage_type: ns(get('Usage Type', 'usage', 'usage_type', 'type')),
    year: extractYear(get('Year', 'year', 'const_year')),
    number_of_people: nf(get('Number of People', 'n_people')),
    number_of_families: nf(get('Number of Families', 'n_families', 'n_family')),
    building_type: ns(get('Building Type', 'tab_type', 'building_type')),
    __raw: p,
  };
}
```

### Recommended Fix for `ProjectScenario` Interface

```typescript
export interface ProjectScenario {
  project_id: string;
  scenario_id: string;
  project_name?: string;
  scenario_name?: string;
  project_boundary?: any;
  project_center?: { type: string; coordinates: [number, number] };
  lod?: number;
  project_zoom?: number;
  project_crs?: number;
  created_at?: string;
  updated_at?: string;
}
```

---

## 7. Running the System

### Prerequisites
- Docker & Docker Compose
- Python 3.10+ with conda/pip
- Node.js 18+

### 1. Start the Database
```bash
cd cim-database
docker compose -f docker-compose.cimdb.yml up -d
# Verify: docker logs cim-integrateddb --tail 20
# Wait for "database system is ready to accept connections"
```

### 2. Start the Backend
```bash
cd cim_wizard_integrated_2026
# Using conda:
conda env create -f environment.yml
conda activate cim_wizard
# Or using pip with your venv

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
```env
VITE_CIM_WIZARD_BASE=http://localhost:8000
```

**Backend** (environment or `.env`):
```env
DATABASE_URL=postgresql://cim_wizard_user:cim_wizard_password@localhost:15432/cim_wizard_integrated
```

### Connection Summary

| Service | Host | Port | Credentials |
|---------|------|------|-------------|
| PostgreSQL/PostGIS | localhost | 15432 | `cim_wizard_user` / `cim_wizard_password` |
| FastAPI Backend | localhost | 8000 | — |
| React Frontend | localhost | 5173 | — |

---

## Compliance Summary

| Endpoint | Route | Status | Issues |
|----------|-------|--------|--------|
| **GET Projects** | `/api/v1/vector/projects` | ✅ Compliant | Minor: incomplete TS interface |
| **POST Create Project** | `/api/v1/building/execute_building_analysis` | ✅ Compliant | Bug: `filter_res` not persisted to DB |
| **GET Scenarios** | `/api/v1/vector/pscenarios/{project_id}` | ✅ Compliant | Minor: incomplete TS interface |
| **GET Buildings** | `/api/v1/vector/get_buildings_geojson/{project_id}/{scenario_id}` | ⚠️ Partial | **7 field normalizer mismatches** — buildings data cannot be properly displayed |

> **Bottom line:** The HTTP transport layer (URLs, methods, request/response formats) is fully aligned across all three projects. The critical gap is in the **frontend building normalizer** (`normalizers.ts`), which uses field names from an older/different data source that don't match the backend's output field names. This causes most building properties to resolve as `undefined` after normalization.
