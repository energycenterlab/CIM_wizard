# CityGML 2.0 + Energy ADE 2.0 Attribute Matrix

**Project:** CIM Wizard Integrated  
**Database schema:** `citydb` (3DCityDB v4 + Energy ADE 2.0)  
**Source of truth for columns:** `cim-database/citydb_schema_dictionary.csv`  
**Mapper implementation:** `app/calculators/citydb_mapper_calculator.py`  
**Last reviewed:** 2026-05-22

This document maps:

1. The **53 `citydb` tables** (24 CityGML core + 29 Energy ADE 2 `ng2_*` tables).
2. The **conceptual CityGML 2.0 / Energy ADE 1.0 attribute vocabulary** used in urban-energy workflows.
3. **CIM Wizard source objects** in `cim_vector` (`cim_wizard_building`, `cim_wizard_building_properties`, LOD1.2 JSON).
4. A **master field-mapping table** — one row per `citydb` column plus virtual `genericattrib` and CIM source rows ([`citygml-energyade-field-mapping.csv`](citygml-energyade-field-mapping.csv), **687 rows**).
5. A **`ctdb_*` calculator roadmap** — one method per fillable table group, with deferred classifications for data we cannot derive yet.

---

## 1. Status legend

### 1.1 Data lifecycle

| Code | Meaning |
|------|---------|
| `MAPPED` | Written to `citydb` by `map_scenario_to_citydb` (pre-sim mapper) |
| `CALCULATED` | Produced by a CIM Wizard calculator into `cim_vector` (or pipeline feature), not persisted to `citydb` |
| `CITYJSON` | Available in CityJSON export (`generate_cityjson` / `generate_cityjson_from_citydb`) but not stored as typed `citydb` columns |
| `SCHEMA` | Table/column exists in PostgreSQL; CIM Wizard does not populate it today |
| `PLANNED-1` | Phase 1 — TABULA/CIM envelope enrichment (`ng2_building`, `ng2_layered_construction`, `ng2_thematic_surface`, partitions) |
| `PLANNED-3` | Phase 3 — HVAC archetypes, materials, openings (`ng2_device`, `ng2_layer`, `ng2_material`, `ng2_opening`) |

### 1.2 Deferred domains (no `ctdb_*` method yet — classification only)

| Code | Meaning | Reason |
|------|---------|--------|
| `DEFERRED-OCCUPANTS` | Occupant behaviour not auto-filled | Requires external templates or user input beyond census volume distribution; `n_people` alone is insufficient for credible `ng2_occupants` heat-gain splits |
| `DEFERRED-SCHEDULES` | Schedules not auto-filled | No authoritative hourly profiles in CIM pipeline; needs EPW-linked or national standard library commitment |
| `DEFERRED-WEATHER` | Weather not auto-filled | No EPW/station binding in scenario; `ng2_weather_data` needs external climate file selection |
| `POSTSIM` | Post-simulation results | Populated only after simulators write to `outputs` schema; not part of pre-sim CIM derivation |

### 1.3 Geometry role (per table)

| Geo | Meaning |
|-----|---------|
| `GEO-DIRECT` | Table stores PostGIS geometry column(s) (`geometry`, `envelope`, `multi_point`, `ref_point`, `position`, …) |
| `GEO-FK` | Table stores foreign keys to `surface_geometry` / `geometry_data` / `implicit_geometry` (geometry lives elsewhere) |
| `GEO-NONE` | Pure semantic, relational, or metadata — no geometry columns or geometry FKs |

---

## 2. Schema inventory (53 tables)

### 2.1 CityGML core (24 tables)

| # | Table | Columns | Geo | CIM Wizard usage |
|---|-------|---------|-----|------------------|
| 1 | `address` | 15 | `GEO-DIRECT` (`multi_point`) | `SCHEMA` |
| 2 | `ade` | 4 | `GEO-NONE` | `SCHEMA` (metadata registry; populated at DB init) |
| 3 | `appear_to_surface_data` | 3 | `GEO-FK` | `SCHEMA` |
| 4 | `appearance` | 8 | `GEO-FK` (`implicit_geometry_id`) | `SCHEMA` |
| 5 | `building` | 18 | `GEO-FK` (`lod0_footprint_id` … `lod4_solid_id`) | **Partial `MAPPED`** (3 semantic columns; LOD FKs unused) |
| 6 | `citymodel` | 9 | `GEO-DIRECT` (`envelope`) | **Partial `MAPPED`** (3 of 9 columns; envelope not computed) |
| 7 | `cityobject` | 13 | `GEO-DIRECT` (`envelope`) | **Partial `MAPPED`** (identity + auto timestamp) |
| 8 | `cityobject_genericattrib` | 12 | `GEO-NONE` | **Active `MAPPED`** (thermal/energy/u-value keys) |
| 9 | `cityobject_member` | 2 | `GEO-NONE` | **Full `MAPPED`** |
| 10 | `codelist` | 4 | `GEO-NONE` | `SCHEMA` |
| 11 | `codelist_entry` | 4 | `GEO-NONE` | `SCHEMA` |
| 12 | `database_srs` | 2 | `GEO-NONE` | `SCHEMA` (DB init) |
| 13 | `datatype` | 7 | `GEO-NONE` | `SCHEMA` (DB init) |
| 14 | `feature` | 14 | `GEO-DIRECT` (`envelope`) | `SCHEMA` (CityGML 3 / v5 path; mapper uses v4 `cityobject`) |
| 15 | `geometry_data` | 5 | `GEO-DIRECT` (`geometry`, `implicit_geometry`) | `SCHEMA` |
| 16 | `implicit_geometry` | 7 | `GEO-FK` + binary (`library_object`) | `SCHEMA` |
| 17 | `namespace` | 4 | `GEO-NONE` | `SCHEMA` (DB init) |
| 18 | `objectclass` | 8 | `GEO-NONE` | `SCHEMA` (DB init; mapper references IDs 26, 32–35) |
| 19 | `property` | 24 | `GEO-FK` + `GEO-DIRECT` (`val_implicitgeom_refpoint`) | `SCHEMA` (v5 EAV; mapper uses `cityobject_genericattrib`) |
| 20 | `surface_data` | 19 | `GEO-DIRECT` (`gt_reference_point`) | `SCHEMA` |
| 21 | `surface_data_mapping` | 6 | `GEO-FK` (`geometry_data_id`) | `SCHEMA` |
| 22 | `surface_geometry` | 13 | `GEO-DIRECT` (`geometry`, `solid_geometry`) | **Partial `MAPPED`** (LOD1.2 polygon trees per surface) |
| 23 | `tex_image` | 5 | `GEO-NONE` | `SCHEMA` |
| 24 | `thematic_surface` | 8 | `GEO-FK` (`lod2_multi_surface_id` …) | **Partial `MAPPED`** (4 of 8 columns) |

### 2.2 Energy ADE 2.0 (29 `ng2_*` tables)

| # | Table | Columns | Geo | CIM Wizard usage |
|---|-------|---------|-----|------------------|
| 1 | `ng2_address_to_building_unit` | 2 | `GEO-NONE` | `SCHEMA` |
| 2 | `ng2_building` | 8 | `GEO-NONE` | `SCHEMA` / `PLANNED-1` |
| 3 | `ng2_building_partition` | 35 | `GEO-FK` (`lod1_solid_id` … `lod3_solid_id`) | `SCHEMA` / `PLANNED-1` |
| 4 | `ng2_cityobject` | 3 | `GEO-DIRECT` (`ref_point`) | `SCHEMA` / `PLANNED-1` |
| 5 | `ng2_ctyobj_relation` | 5 | `GEO-NONE` | `SCHEMA` |
| 6 | `ng2_device` | 31 | `GEO-NONE` | `SCHEMA` / `PLANNED-3` |
| 7 | `ng2_device_operation` | 6 | `GEO-NONE` | `SCHEMA` / `PLANNED-3` |
| 8 | `ng2_energy_perf_cert` | 12 | `GEO-NONE` | `SCHEMA` |
| 9 | `ng2_layer` | 5 | `GEO-NONE` | `SCHEMA` / `PLANNED-3` |
| 10 | `ng2_layered_construction` | 12 | `GEO-NONE` | `SCHEMA` / `PLANNED-1` |
| 11 | `ng2_library` | 6 | `GEO-NONE` | `SCHEMA` |
| 12 | `ng2_material` | 22 | `GEO-NONE` | `SCHEMA` / `PLANNED-3` |
| 13 | `ng2_occupants` | 20 | `GEO-NONE` | `DEFERRED-OCCUPANTS` |
| 14 | `ng2_opening` | 11 | `GEO-NONE` | `SCHEMA` / `PLANNED-3` |
| 15 | `ng2_optical_property` | 7 | `GEO-NONE` | `SCHEMA` / `PLANNED-3` |
| 16 | `ng2_qualified_attribute` | 10 | `GEO-NONE` | `SCHEMA` / `PLANNED-1` |
| 17 | `ng2_refurbishment_measure` | 9 | `GEO-NONE` | `SCHEMA` / `PLANNED-3` |
| 18 | `ng2_resource` | 34 | `GEO-NONE` | `POSTSIM` |
| 19 | `ng2_schedule` | 22 | `GEO-NONE` | `DEFERRED-SCHEDULES` |
| 20 | `ng2_schedule_component` | 8 | `GEO-NONE` | `DEFERRED-SCHEDULES` |
| 21 | `ng2_solar_collector` | 20 | `GEO-FK` (`lod2/lod3_multi_surface_id`) | `SCHEMA` / `PLANNED-3` (from `cim_vector.pv`) |
| 22 | `ng2_storage_device` | 14 | `GEO-NONE` | `POSTSIM` |
| 23 | `ng2_suitability` | 8 | `GEO-NONE` | `SCHEMA` |
| 24 | `ng2_them_surf_to_thermal_zone` | 2 | `GEO-NONE` | `SCHEMA` / `PLANNED-1` |
| 25 | `ng2_thematic_surface` | 20 | `GEO-NONE` | `SCHEMA` / `PLANNED-1` |
| 26 | `ng2_time_series` | 38 | `GEO-NONE` | `DEFERRED-SCHEDULES` / `DEFERRED-WEATHER` / `POSTSIM` |
| 27 | `ng2_urban_function_area` | 5 | `GEO-NONE` | `SCHEMA` |
| 28 | `ng2_utl_ntw_connection` | 11 | `GEO-NONE` | `SCHEMA` / `PLANNED-3` (from `cim_network`) |
| 29 | `ng2_weather_data` | 12 | `GEO-DIRECT` (`position`) | `DEFERRED-WEATHER` |

**Column totals:** 612 columns in schema dictionary + **75 virtual rows** (genericattrib attrnames, LOD1.2 JSON paths, CIM source inventory) = **687 mapping rows** in [`citygml-energyade-field-mapping.csv`](citygml-energyade-field-mapping.csv).

**Geometry summary:**

| Geo class | Table count | Tables |
|-----------|-------------|--------|
| `GEO-DIRECT` | 11 | `address`, `citymodel`, `cityobject`, `feature`, `geometry_data`, `surface_data`, `surface_geometry`, `property` (partial), `ng2_cityobject`, `ng2_weather_data` |
| `GEO-FK` | 9 | `building`, `appearance`, `thematic_surface`, `appear_to_surface_data`, `surface_data_mapping`, `implicit_geometry`, `property` (partial), `ng2_building_partition`, `ng2_solar_collector` |
| `GEO-NONE` | 33 | All remaining tables (semantic Energy ADE, metadata, junction tables) |

**Currently written geometry:** `surface_geometry.geometry` (PolygonZ per LOD1.2 surface) — **6+ polygons per building** typical. No `citymodel.envelope`, `cityobject.envelope`, or `ng2_cityobject.ref_point` yet.

---

## 3. CIM Wizard source objects (`cim_vector` schema)

CityDB mapping reads two building tables per scenario. **`building_surfaces_lod12`** is the critical JSON blob: it holds semantic wall/roof/ground/floor/ceiling geometries and **`thermal_zones[]`** (one zone per building level / storey).

### 3.1 `cim_vector.cim_wizard_building`

| Column | Type | Role in CityDB pipeline |
|--------|------|-------------------------|
| `building_id` | UUID (PK) | → `cityobject.gmlid` (building CityObject identity) |
| `lod` | integer | Geometry detail level; mirrored as `cim_lod` genericattrib |
| `building_geometry` | geometry | Footprint input to LOD1.2; centroid for `ng2_cityobject.ref_point` |
| `building_geometry_source` | text | Provenance tag → `cim_building_geometry_source` |
| `census_id` | bigint | Census tract link → `cim_census_id`; drives `const_tabula` |
| `building_surfaces_lod12` | jsonb | **Core geometry + physics** — see §3.3 |
| `z_value` | float | Floor height above sea level → ref_point Z, `cim_z_value` |
| `building_name` | text | → `cityobject.name` |
| `pv_ids` | uuid[] | Links to `cim_vector.pv` → `ng2_solar_collector` |
| `created_at` / `updated_at` | timestamptz | Pipeline metadata only |

### 3.2 `cim_vector.cim_wizard_building_properties`

Scenario-scoped attributes (PK: `scenario_id`, `building_id`, `lod`).

| Column | Type | Role in CityDB pipeline |
|--------|------|-------------------------|
| `height` | float | → `building.measured_height` |
| `area` | float | → `thermalZone_floorArea_m2` / `cim_area` |
| `volume` | float | → `thermalZone_volume_m3` / `cim_volume` |
| `number_of_floors` | float | → `building.storeys_above_ground`; LOD1.2 storey count |
| `type` | text | Usage (residential, others) → `ng2_building.type` |
| `const_tabula` | text | TABULA period `TABULA_1…7` → U-values, constructions, `tabula_*` attrs |
| `const_period_census` | text | Census construction band → `cim_const_period_census` |
| `const_year` | integer | Construction year → `yearOfConstruction` genericattrib |
| `envelope_efficiency` | text | low/medium/high → `energySystem_envelopeEfficiency` |
| `fmu_file` | text | HVAC archetype → `energySystem_fmuFile`, `ng2_device` |
| `n_people` | integer | Census population → `cim_n_people` (occupants table DEFERRED) |
| `n_family` | integer | Household count → `cim_n_family` |
| `filter_res` | boolean | Residential filter gate → `cim_filter_res`; drives `type` |

### 3.3 `building_surfaces_lod12` JSON structure

Generated by `building_geo_lod12_calculator`. Each building level is modelled as a **thermal zone** (`thermal_zones[]`).

```
building_surfaces_lod12
├── metadata          (building_height, method, coordinate_system, …)
├── surfaces
│   ├── wall_surfaces[]     geometry + properties.area_m2, azimuth_degrees, orientation
│   ├── roof_surface        geometry + properties.area_m2, inclination_degrees
│   ├── ground_surface      geometry + properties.area_m2
│   └── floor_surfaces[]    geometry + properties (inter-storey floors/ceilings)
└── thermal_zones[]
    ├── zone_id             (z1, z2, … one per storey)
    ├── storey_index        links surfaces to level
    ├── usage, volume_m3, floor_area_m2
    └── is_heated, is_cooled
```

| JSON path | Calculator | CityDB target | Status |
|-----------|------------|---------------|--------|
| `surfaces.*.geometry` | `citydb_mapper_calculator` | `surface_geometry.geometry` | `MAPPED` |
| `surfaces.*.properties.area_m2` | `ctdb_thematic_surface_calculator` | `ng2_thematic_surface.total_surf_area` | `PLANNED-1` |
| `surfaces.wall_surfaces[].properties.azimuth_degrees` | `ctdb_thematic_surface_calculator` | `ng2_thematic_surface.azimuth` | `PLANNED-1` |
| `surfaces.*.properties.inclination_degrees` | `ctdb_thematic_surface_calculator` | `ng2_thematic_surface.inclination` | `PLANNED-1` |
| `thermal_zones[]` (all fields) | `ctdb_thermal_partition_calculator` | `ng2_building_partition` + `tz:*` genericattrib | `PLANNED-1` / partial `MAPPED` |
| `thermal_zones[].storey_index` | `ctdb_surf_zone_adjacency_calculator` | `ng2_them_surf_to_thermal_zone` | `PLANNED-1` |

### 3.4 TABULA period (`const_tabula`) → energy attributes

`const_tabula` (e.g. `TABULA_3`) drives opaque U-values via `TABULA_U_VALUES` in `citydb_mapper_calculator.py`:

| TABULA code | wall U | roof U | ground U |
|-------------|--------|--------|----------|
| TABULA_1 | 1.70 | 2.20 | 1.60 |
| TABULA_2 | 1.60 | 2.00 | 1.50 |
| TABULA_3 | 1.48 | 1.80 | 1.40 |
| TABULA_4 | 1.30 | 1.60 | 1.20 |
| TABULA_5 | 1.10 | 1.20 | 1.00 |
| TABULA_6 | 0.80 | 0.80 | 0.80 |
| TABULA_7 | 0.50 | 0.40 | 0.50 |

**Calculators using `const_tabula`:**

| Calculator | Method | Output |
|------------|--------|--------|
| `citydb_mapper_calculator` | `map_scenario_to_citydb` | `u_value_w_m2k` on each surface genericattrib |
| `ctdb_tabula_attrib_calculator` | `ctdb_from_const_tabula` | `tabula_u_wall`, `tabula_u_roof`, `tabula_u_ground`, `tabula_g_window`, `tabula_period_code`, `tabula_envelope_class` genericattrib |

Full archetype extraction (layer stacks, per-component U, 32×8 catalog) is documented in [`tabula-archetype-extraction-guide.md`](tabula-archetype-extraction-guide.md).
| `ctdb_layered_construction_calculator` | `ctdb_from_tabula` | `ng2_layered_construction.u_value`, `g_value`, `library_code` |
| `ctdb_ng2_building_calculator` | `ctdb_from_tabula` | `ng2_building.constr_weight`, `type` |
| `ctdb_opening_calculator` | `ctdb_from_tabula` | `ng2_opening.area` from glazing ratio |
| `ctdb_qualified_attribute_calculator` | `ctdb_tabula_kpis` | `ng2_qualified_attribute` envelope KPIs |

### 3.5 Pipeline feature registry (pre-CityDB)

| CIM column / feature | Calculator | Used by mapper |
|----------------------|------------|----------------|
| `building_geometry` | `building_geo` | Indirect (footprint for LOD1.2) |
| `building_surfaces_lod12` | `building_geo_lod12` | Yes — surfaces + thermal zones |
| `height` | `building_height` | Yes — `building.measured_height` |
| `area` | `building_area` | Partial — genericattrib / CityJSON only |
| `volume` | `building_volume` | Partial — genericattrib / CityJSON only |
| `number_of_floors` | `building_n_floors` | Yes — `building.storeys_above_ground` |
| `type` | `building_type` | `CALCULATED` only |
| `const_year` | `building_construction_year` | `CITYJSON` only |
| `const_period_census` | `building_construction_year` | Not exported |
| `const_tabula` | `building_construction_year` | Yes — TABULA U-values on surfaces |
| `n_people` | `building_population` | Not mapped |
| `n_family` | `building_n_families` | Not mapped |
| `envelope_efficiency` | `envelope_efficiency` | Partial — genericattrib |
| `fmu_file` | `fmu_assign` | Partial — genericattrib |
| `z_value` | `building_z_value` | `CITYJSON` only |
| `building_name` | `building_name` | Yes — `cityobject.name` |
| `filter_res` | `filter_res` | Not mapped (→ `cim_filter_res` planned) |

---

## 4. Conceptual CityGML 2.0 + Energy ADE 1.0 vocabulary

This section maps the **semantic attributes** from the CityGML / Energy ADE 1.0 information model to CIM Wizard status. Energy ADE 1.0 names are aligned to **Energy ADE 2.0 (`ng2_*`)** storage where applicable.

### 4.1 Module: CityGML 2.0 Core

#### Table: `_CityObject` (abstract) → `citydb.cityobject`

| Attribute | Description | 3DCityDB target | Status | Notes |
|-----------|-------------|-----------------|--------|-------|
| creationDate | Date/time object added | `cityobject.creation_date` | `MAPPED` | DB default `now()` on insert |
| terminationDate | Date object retired | `cityobject.termination_date` | `SCHEMA` | — |
| relativeToTerrain | Relation to terrain | genericattrib / CityGML attr | `SCHEMA` | — |
| relativeToWater | Relation to water | genericattrib | `SCHEMA` | — |
| externalReference | External registry link | `external_ref` / genericattrib | `SCHEMA` | — |
| generalizesTo | Link to lower-LOD object | relation table | `SCHEMA` | — |

#### Table: `CityModel` → `citydb.citymodel`

| Attribute | Description | Target | Status | Notes |
|-----------|-------------|--------|--------|-------|
| boundedBy | Scene bounding box | `citymodel.envelope` | `PLANNED-1` | `ctdb_envelope_calculator.ctdb_citymodel_envelope` |
| cityObjectMember | Container of city objects | `cityobject_member` | `MAPPED` | One row per building |

---

### 4.2 Module: CityGML 2.0 Building

#### Table: `_AbstractBuilding` → `citydb.building` + `citydb.cityobject`

| Attribute | Description | Target | Status | CIM source |
|-----------|-------------|--------|--------|------------|
| class | Building classification | genericattrib / `ng2_building.type` | `CALCULATED` / `PLANNED-1` | `building_properties.type` |
| function | Intended purpose | genericattrib | `SCHEMA` | — |
| usage | Actual use | `ng2_building_partition.type` | `PLANNED-1` | Partial via `tz:*:usage` genericattrib today |
| yearOfConstruction | Year built | genericattrib | `CITYJSON` | `const_year` |
| yearOfDemolition | Year demolished | genericattrib | `SCHEMA` | — |
| roofType | Roof shape | genericattrib | `SCHEMA` | — |
| measuredHeight | Height ground to peak | `building.measured_height` | `MAPPED` | `height` |
| storeysAboveGround | Floors above ground | `building.storeys_above_ground` | `MAPPED` | `number_of_floors` |
| storeysBelowGround | Basement floors | `building.storeys_below_ground` | `CALCULATED` | Mixed-use LOD1.2 only; not mapped |

#### Table: `Room`

| Attribute | Status |
|-----------|--------|
| class | `SCHEMA` |
| function | `SCHEMA` |
| usage | `SCHEMA` |

#### Table: `_BoundarySurface` → `citydb.thematic_surface`

| Attribute | Description | Target | Status |
|-----------|-------------|--------|--------|
| opening | Link to window/door | `opening` + `ng2_opening` | `SCHEMA` / `PLANNED-3` |

---

### 4.3 Module: Energy ADE — Core building extensions

#### Table: `_AbstractBuilding` (Energy ADE injected) → `ng2_building` + partitions

| ADE 1.0 attribute | ADE 2.0 target | Status | CIM source |
|-------------------|----------------|--------|------------|
| buildingType | `ng2_building.type` | `PLANNED-1` | `type` |
| constructionWeight | `ng2_building.constr_weight` | `PLANNED-1` | `const_tabula` / `envelope_efficiency` |
| energyPerformanceCertification | `ng2_energy_perf_cert` | `SCHEMA` | — |
| floorArea | partition / genericattrib | `MAPPED` partial | `area` → `thermalZone_floorArea_m2` |
| heightAboveGround | genericattrib | `CITYJSON` | `z_value` as `terrainHeight` |
| isLandmarked | `ng2_building.is_protected` | `SCHEMA` | — |
| referencePoint | `ng2_cityobject.ref_point` | `PLANNED-1` | `ctdb_ref_point_calculator.ctdb_footprint_centroid` |
| refurbishmentMeasure | `ng2_refurbishment_measure` | `PLANNED-3` | `ctdb_refurbishment_calculator` |
| volume | partition / genericattrib | `MAPPED` partial | `volume` → `thermalZone_volume_m3` |

#### Table: `EnergyDemand` → `ng2_resource`

| Attribute | ADE 2.0 mapping | Status |
|-----------|-----------------|--------|
| endUse | `ng2_resource.enduse` | `SCHEMA` / `POSTSIM` |
| energyAmount | `ng2_resource.amount` | `SCHEMA` / `POSTSIM` |
| energyCarrierType | `ng2_resource.energy_carrier` | `SCHEMA` |
| maximumLoad | `ng2_resource.maximum_load` | `SCHEMA` / `POSTSIM` |

#### Table: `WeatherData` → `ng2_weather_data` + `ng2_time_series`

| Attribute | Target | Status |
|-----------|--------|--------|
| position | `ng2_weather_data.position` | `DEFERRED-WEATHER` |
| values | `ng2_time_series.values_list` | `DEFERRED-WEATHER` |
| weatherDataType | `ng2_weather_data.type` | `DEFERRED-WEATHER` |

#### Table: `AbstractEnergySystem` → `ng2_device`

| Attribute | Target | Status | Notes |
|-----------|--------|--------|-------|
| model | `ng2_device.model` | `SCHEMA` | `fmu_file` stored as `energySystem_fmuFile` genericattrib |
| numberOfDevices | `ng2_device.num_of_devices` | `SCHEMA` | — |
| serviceLife | — | `SCHEMA` | — |
| yearOfManufacture | `ng2_device.year_of_manufacture` | `SCHEMA` | — |

---

### 4.4 Module: Energy ADE — Building physics

#### Table: `ThermalZone` → `ng2_building_partition`

| Attribute | ADE 2.0 column | Status | Notes |
|-----------|----------------|--------|-------|
| additionalThermalBridgeUValue | `ng2_qualified_attribute` | `SCHEMA` | — |
| effectiveThermalCapacity | `heat_capacity` | `PLANNED-1` | Volume in `tz:*:volume_m3` genericattrib today |
| floorArea | `partition` / genericattrib | `MAPPED` partial | `thermalZone_floorArea_m2` or `tz:*:floor_area_m2` |
| indirectlyHeatedAreaRatio | — | `SCHEMA` | — |
| infiltrationRate | `infiltration_rate` | `DEFERRED-SCHEDULES` | Needs ventilation archetype; not in CIM today |
| isCooled | `is_cooled` | `MAPPED` partial | `tz:*:is_cooled` genericattrib |
| isHeated | `is_heated` | `MAPPED` partial | `tz:*:is_heated` genericattrib |

#### Table: `ThermalBoundary` → `ng2_thematic_surface` + `thematic_surface`

| Attribute | ADE 2.0 column | Status | Notes |
|-----------|----------------|--------|-------|
| area | `total_surf_area` | `PLANNED-1` | Computed in LOD1.2; not in citydb today |
| azimuth | `azimuth` | `PLANNED-1` | Computed in LOD1.2 |
| inclination | `inclination` | `PLANNED-1` | Computed in LOD1.2 |
| thermalBoundaryType | `thematic_surface.objectclass_id` | `MAPPED` | Wall=34, Roof=33, Ground=35, Floor=32 |
| *(extension)* u-value | `cityobject_genericattrib.u_value_w_m2k` | `MAPPED` | From TABULA via `const_tabula` |

#### Table: `ThermalOpening` → `ng2_opening`

| Attribute | Status |
|-----------|--------|
| area | `PLANNED-3` |
| indoorShading | `SCHEMA` |
| openableRatio | `SCHEMA` |
| outdoorShading | `SCHEMA` |

---

### 4.5 Module: Energy ADE — Occupant behaviour (`DEFERRED-OCCUPANTS`)

These attributes are **classified only**. No `ctdb_*` auto-fill method is planned until an external occupant template library is adopted.

#### Table: `UsageZone` → `ng2_building_partition` (usage-zone role)

| Attribute | Target | Status |
|-----------|--------|--------|
| averageInternalGains | `int_heat_gains` | `DEFERRED-OCCUPANTS` |
| coolingSchedule | `cooling_schedule_id` | `DEFERRED-SCHEDULES` |
| heatingSchedule | `heating_schedule_id` | `DEFERRED-SCHEDULES` |
| usageZoneType | `type` | Partial — `tz:*:usage` (`PLANNED-1` via `ctdb_thermal_partitions_from_lod12`) |
| usedFloors | genericattrib | Partial — `tz:*:storey_index` (`MAPPED`) |

#### Table: `Occupants` → `ng2_occupants`

| Attribute | ADE 2.0 column | Status | Notes |
|-----------|----------------|--------|-------|
| heatDissipation | `heat_diss` | `DEFERRED-OCCUPANTS` | No credible per-building split from census alone |
| numberOfOccupants | `num_of_occupants` | `CALCULATED` | `n_people` in `cim_vector`; not written to `ng2_occupants` |
| occupancyRate | `schedule_id` | `DEFERRED-SCHEDULES` | — |
| occupantType | `type` | `DEFERRED-OCCUPANTS` | — |

#### Table: `Household`

| Attribute | Status | Notes |
|-----------|--------|-------|
| householdType | `CALCULATED` | `n_family` in `cim_vector` only |
| residenceType | `DEFERRED-OCCUPANTS` | — |

#### Table: `Facilities` (abstract) → `ng2_device`

| Attribute | Status |
|-----------|--------|
| heatDissipation | `DEFERRED-OCCUPANTS` |
| operationSchedule | `DEFERRED-SCHEDULES` |

---

### 4.6 Module: Energy ADE — Time series and schedules (`DEFERRED-SCHEDULES`)

No `ctdb_*` method until national hourly profile libraries are bound to scenarios.

#### Table: `RegularTimeSeries` → `ng2_time_series`

| Attribute | ADE 2.0 column | Status |
|-----------|----------------|--------|
| temporalExtent | `temporal_extent` + `period_begin/end` | `DEFERRED-SCHEDULES` / `DEFERRED-WEATHER` |
| timeInterval | `time_interval` + `time_interval_unit` | `DEFERRED-SCHEDULES` / `DEFERRED-WEATHER` |
| values | `values_list` or `file_uri` | `DEFERRED-SCHEDULES` / `DEFERRED-WEATHER` / `POSTSIM` |

#### Table: `DualValueSchedule` → `ng2_schedule`

| Attribute | ADE 2.0 column | Status |
|-----------|----------------|--------|
| idleValue | `idle_value` | `DEFERRED-SCHEDULES` |
| usageDaysPerYear | composed via `ng2_schedule_component` | `DEFERRED-SCHEDULES` |
| usageHoursPerDay | `start_usage_time` / `end_usage_time` | `DEFERRED-SCHEDULES` |
| usageValue | `usage_value` | `DEFERRED-SCHEDULES` |

---

## 5. Currently mapped `citydb` fields (pre-simulation mapper)

### 5.1 Per scenario (`citymodel`)

| Column | Value | Status |
|--------|-------|--------|
| `gmlid` | `scenario_id` | `MAPPED` |
| `name` | `CIM-Scenario-{scenario_id[:8]}` | `MAPPED` |
| `description` | `project {project_id}` | `MAPPED` |
| `creation_date` | auto | `MAPPED` |

### 5.2 Per building (`cityobject` + `building` + `cityobject_member`)

| Column / attribute | Source | Status |
|--------------------|--------|--------|
| `cityobject.gmlid` | `building_id` (UUID) | `MAPPED` |
| `cityobject.name` | `building_name` or `BUI-{id[:8]}` | `MAPPED` |
| `cityobject.objectclass_id` | 26 (Building) | `MAPPED` |
| `building.measured_height` | `height` | `MAPPED` |
| `building.measured_height_unit` | `"m"` | `MAPPED` |
| `building.storeys_above_ground` | `number_of_floors` | `MAPPED` |
| `cityobject_member` link | scenario membership | `MAPPED` |

### 5.3 Per building — `cityobject_genericattrib` keys

**Single-zone mode** (no `thermal_zones` in LOD1.2):

| attrname | Source | Status |
|----------|--------|--------|
| `thermalZone_volume_m3` | `volume` | `MAPPED` |
| `thermalZone_floorArea_m2` | `area` | `MAPPED` |
| `thermalZone_numberOfFloors` | `number_of_floors` | `MAPPED` |
| `energySystem_envelopeEfficiency` | `envelope_efficiency` | `MAPPED` |
| `energySystem_fmuFile` | `fmu_file` | `MAPPED` |

**Multi-zone mode** (`by_footprint_height_floors` / `by_mixed_use`):

| attrname pattern | Source | Status |
|------------------|--------|--------|
| `thermalZone_count` | len(thermal_zones) | `MAPPED` |
| `tz:{zone_id}:usage` | zone dict | `MAPPED` |
| `tz:{zone_id}:volume_m3` | zone dict | `MAPPED` |
| `tz:{zone_id}:floor_area_m2` | zone dict | `MAPPED` |
| `tz:{zone_id}:is_heated` | zone dict | `MAPPED` |
| `tz:{zone_id}:is_cooled` | zone dict | `MAPPED` |
| `tz:{zone_id}:storey_index` | zone dict | `MAPPED` |
| `tz:{zone_id}:apartment_index` | zone dict (optional) | `MAPPED` |
| `energySystem_envelopeEfficiency` | `envelope_efficiency` | `MAPPED` |
| `energySystem_fmuFile` | `fmu_file` | `MAPPED` |

### 5.4 Per thematic surface

| Storage | Field | Source | Status |
|---------|-------|--------|--------|
| `cityobject` | `gmlid`, `name`, `objectclass_id` | surface_id + type | `MAPPED` |
| `thematic_surface` | `building_id`, `lod2_multi_surface_id` | parent building | `MAPPED` |
| `surface_geometry` | PolygonZ tree (`ms-*`, `poly-*`) | LOD1.2 GeoJSON | `MAPPED` |
| `cityobject_genericattrib` | `u_value_w_m2k` | TABULA from `const_tabula` | `MAPPED` |

**Typical surface count** (`by_footprint_height`): 4 walls + 1 roof + 1 ground = **6 surfaces** per building.

### 5.5 CityJSON-only building attributes (`generate_cityjson`)

These are exported when reading from `cim_vector` but are **not** persisted to typed `citydb` columns by the current mapper:

| CityJSON attribute | CIM source |
|--------------------|------------|
| `measuredHeight` | `height` |
| `footprintArea` | `area` |
| `volume` | `volume` |
| `yearOfConstruction` | `const_year` |
| `storeysAboveGround` | `number_of_floors` |
| `terrainHeight` | `z_value` |
| `name` | `building_name` |

Thermal zone children (`+Energy-ThermalZone`): `volume`, `floorArea`, `numberOfFloors`, `envelopeEfficiency`, `energySystemModel`, `isHeated`, `isCooled`, `usage`, `storeyIndex`, `apartmentIndex`.

---

## 6. Per-table column coverage (active vs schema-only)

### 6.1 Tables with active mapper writes

#### `citydb.building` (18 columns)

| Column | Status |
|--------|--------|
| `id` | `MAPPED` (FK to cityobject) |
| `objectclass_id` | `MAPPED` |
| `measured_height` | `MAPPED` |
| `measured_height_unit` | `MAPPED` |
| `storeys_above_ground` | `MAPPED` |
| `building_parent_id` | `SCHEMA` |
| `building_root_id` | `SCHEMA` |
| `storeys_below_ground` | `SCHEMA` |
| `lod0_footprint_id` … `lod4_solid_id` (10 LOD FKs) | `SCHEMA` |

#### `citydb.surface_geometry` (13 columns)

| Column | Status |
|--------|--------|
| `id`, `gmlid`, `parent_id`, `root_id` | `MAPPED` |
| `geometry` | `MAPPED` (leaf polygon) |
| `cityobject_id` | `MAPPED` |
| `is_solid`, `is_composite` | `MAPPED` (root node flags) |
| `is_triangulated`, `is_xlink`, `is_reverse`, `solid_geometry`, `gmlid_codespace` | `SCHEMA` |

#### `citydb.thematic_surface` (8 columns)

| Column | Status |
|--------|--------|
| `id`, `objectclass_id`, `building_id`, `lod2_multi_surface_id` | `MAPPED` |
| `room_id`, `building_installation_id`, `lod3/lod4_multi_surface_id` | `SCHEMA` |

### 6.2 Energy ADE tables — all columns `SCHEMA` today

Full column definitions are in `cim-database/citydb_schema_dictionary.csv`. Priority tables for extension:

| Table | Columns | Geo | Phase | Primary CIM inputs |
|-------|---------|-----|-------|-------------------|
| `ng2_building` | 8 | `GEO-NONE` | 1 | `type`, `const_tabula`, `envelope_efficiency` |
| `ng2_building_partition` | 35 | `GEO-FK` | 1 | LOD1.2 `thermal_zones` |
| `ng2_layered_construction` | 12 | `GEO-NONE` | 1 | TABULA U/g per wall/roof/ground/window |
| `ng2_thematic_surface` | 20 | `GEO-NONE` | 1 | LOD1.2 surface `properties.*` |
| `ng2_them_surf_to_thermal_zone` | 2 | `GEO-NONE` | 1 | surface–zone adjacency |
| `ng2_qualified_attribute` | 10 | `GEO-NONE` | 1 | TABULA envelope KPIs |
| `ng2_cityobject` | 3 | `GEO-DIRECT` | 1 | footprint centroid + `z_value` |
| `ng2_occupants` | 20 | `GEO-NONE` | — | `DEFERRED-OCCUPANTS` |
| `ng2_schedule` | 22 | `GEO-NONE` | — | `DEFERRED-SCHEDULES` |
| `ng2_schedule_component` | 8 | `GEO-NONE` | — | `DEFERRED-SCHEDULES` |
| `ng2_weather_data` | 12 | `GEO-DIRECT` | — | `DEFERRED-WEATHER` |
| `ng2_time_series` | 38 | `GEO-NONE` | — | `DEFERRED-SCHEDULES` / `DEFERRED-WEATHER` / `POSTSIM` |
| `ng2_device` | 31 | `GEO-NONE` | 3 | HVAC archetype from `fmu_file` |
| `ng2_device_operation` | 6 | `GEO-NONE` | 3 | device operation linked to archetype |
| `ng2_layer` | 5 | `GEO-NONE` | 3 | construction layers |
| `ng2_material` | 22 | `GEO-NONE` | 3 | material properties |
| `ng2_opening` | 11 | `GEO-NONE` | 3 | window/door areas from TABULA glazing ratio |
| `ng2_optical_property` | 7 | `GEO-NONE` | 3 | glazing optical data |
| `ng2_resource` | 34 | `GEO-NONE` | POSTSIM | simulation energy flows |
| `ng2_storage_device` | 14 | `GEO-NONE` | POSTSIM | battery state from `outputs.battery` |
| `ng2_solar_collector` | 20 | `GEO-FK` | 3 | `cim_vector.pv` roof polygons |
| `ng2_utl_ntw_connection` | 11 | `GEO-NONE` | 3 | `cim_network` grid link |

---

## 7. `ctdb_*` calculator development plan

Each new calculator is a Python module under `app/calculators/` named `ctdb_<domain>_calculator.py`. Each module exposes **one primary method** (also prefixed `ctdb_`). Methods run after the existing `map_scenario_to_citydb` geometry pass (or split from it over time).

**Pipeline order (pre-simulation, fillable today):**

```
map_scenario_to_citydb / ctdb_geometry_calculator.ctdb_map_lod12_surfaces   (existing)
  -> ctdb_envelope_calculator.ctdb_citymodel_envelope
  -> ctdb_attrib_calculator.ctdb_cim_genericattrib_mirror
  -> ctdb_tabula_attrib_calculator.ctdb_from_const_tabula
  -> ctdb_ng2_building_calculator.ctdb_from_tabula
  -> ctdb_layered_construction_calculator.ctdb_from_tabula
  -> ctdb_thematic_surface_calculator.ctdb_from_lod12
  -> ctdb_thermal_partition_calculator.ctdb_from_lod12
  -> ctdb_surf_zone_adjacency_calculator.ctdb_from_lod12
  -> ctdb_ref_point_calculator.ctdb_footprint_centroid
  -> ctdb_qualified_attribute_calculator.ctdb_tabula_kpis
  -> ctdb_material_stack_calculator.ctdb_from_tabula
  -> ctdb_opening_calculator.ctdb_from_tabula
  -> ctdb_optical_property_calculator.ctdb_from_tabula
  -> ctdb_hvac_calculator.ctdb_from_fmu_archetype
  -> ctdb_device_operation_calculator.ctdb_from_archetype
  -> ctdb_solar_collector_calculator.ctdb_from_pv
  -> ctdb_utility_connection_calculator.ctdb_from_grid
  -> ctdb_refurbishment_calculator.ctdb_from_envelope_efficiency   (optional)
  -> ctdb_building_semantic_calculator.ctdb_from_cim
```

**Post-simulation (`ctdb_postsim_calculator.py`):**

```
ctdb_postsim_calculator.ctdb_genericattrib_from_outputs
ctdb_postsim_calculator.ctdb_resource_from_outputs
ctdb_postsim_calculator.ctdb_storage_device_from_outputs
```

### 7.1 Pre-simulation calculators (CIM-derivable)

| Calculator module | Method | Target table(s) | Geo | Logic (one line) |
|-------------------|--------|-----------------|-----|------------------|
| `ctdb_geometry_calculator` | `ctdb_map_lod12_surfaces` | `cityobject`, `thematic_surface`, `surface_geometry`, `cityobject_genericattrib` | `GEO-DIRECT` | **Existing** in `map_scenario_to_citydb`: write LOD1.2 PolygonZ per wall/roof/ground/floor and TABULA `u_value_w_m2k` on each surface. |
| `ctdb_envelope_calculator` | `ctdb_citymodel_envelope` | `citymodel.envelope`, `cityobject.envelope` | `GEO-DIRECT` | `ST_Envelope(ST_Collect(all surface_geometry.geometry))` per CityModel and per building CityObject. |
| `ctdb_tabula_attrib_calculator` | `ctdb_from_const_tabula` | `cityobject_genericattrib` | `GEO-NONE` | Write `tabula_period_code`, `tabula_u_wall/roof/ground`, `tabula_g_window`, `tabula_envelope_class`, `tabula_constr_weight`, `tabula_glazing_ratio` from `const_tabula` lookup. |
| `ctdb_attrib_calculator` | `ctdb_cim_genericattrib_mirror` | `cityobject_genericattrib` | `GEO-NONE` | Copy all `cim_vector` building props (`type`, `const_*`, `n_people`, `area`, `volume`, `z_value`, `filter_res`, …) to `cim_*` keys on the building CityObject. |
| `ctdb_ng2_building_calculator` | `ctdb_from_tabula` | `ng2_building` | `GEO-NONE` | Set `type` from `building_properties.type`, `constr_weight` from `const_tabula` lookup (fallback `envelope_efficiency`), attic/basement thermal status from mixed-use LOD1.2 flags. |
| `ctdb_layered_construction_calculator` | `ctdb_from_tabula` | `ng2_layered_construction`, `cityobject` | `GEO-NONE` | One LayeredConstruction CityObject per building per element (`wall`, `roof`, `ground`, `window`) with TABULA `u_value`, window `g_value`, `library_code=const_tabula`. |
| `ctdb_thematic_surface_calculator` | `ctdb_from_lod12` | `ng2_thematic_surface` | `GEO-NONE` | For each mapped thematic surface, copy LOD1.2 `properties.area_m2`, `azimuth_degrees`, `inclination_degrees`; default flat roof inclination to 0 deg. |
| `ctdb_thermal_partition_calculator` | `ctdb_from_lod12` | `ng2_building_partition`, `cityobject` | `GEO-FK` | For each `thermal_zones[]` entry, create ThermalZone CityObject + partition with `type=usage`, `is_heated`/`is_cooled`, `heat_capacity=volume_m3`. |
| `ctdb_surf_zone_adjacency_calculator` | `ctdb_from_lod12` | `ng2_them_surf_to_thermal_zone` | `GEO-NONE` | Link each exterior surface to the thermal zone owning its storey (`storey_index` match); single-zone buildings link all surfaces to zone `z1`. |
| `ctdb_ref_point_calculator` | `ctdb_footprint_centroid` | `ng2_cityobject.ref_point` | `GEO-DIRECT` | Building reference point = footprint centroid (EPSG:4326) at terrain height `z_value` (or 0 if missing). |
| `ctdb_qualified_attribute_calculator` | `ctdb_tabula_kpis` | `ng2_qualified_attribute` | `GEO-NONE` | Write envelope KPIs (`avg_opaque_u`, `envelope_class`, `tabula_period_label`) as qualified attributes on `ng2_building`. |
| `ctdb_material_stack_calculator` | `ctdb_from_tabula` | `ng2_material`, `ng2_layer`, `ng2_layered_construction` | `GEO-NONE` | Synthesize one equivalent no-mass layer per construction: `thm_conductivity` from U-value, `library_code=TABULA_{element}`. |
| `ctdb_opening_calculator` | `ctdb_from_tabula` | `ng2_opening` | `GEO-NONE` | Estimate glazed area per wall from TABULA-period glazing ratio times `ng2_thematic_surface.total_surf_area`; copy wall azimuth/inclination. |
| `ctdb_optical_property_calculator` | `ctdb_from_tabula` | `ng2_optical_property` | `GEO-NONE` | Attach solar transmittance (`fraction=g_value`) to window layered construction from TABULA window defaults. |
| `ctdb_hvac_calculator` | `ctdb_from_fmu_archetype` | `ng2_device`, `cityobject` | `GEO-NONE` | Map `fmu_file` (e.g. `frassinetto`) to HeatPump device row with archetype COP/temperature from project FMU metadata. |
| `ctdb_device_operation_calculator` | `ctdb_from_archetype` | `ng2_device_operation` | `GEO-NONE` | Create operation record per `ng2_device` with `yearly_global_efficiency` from archetype; `schedule_id` left null until schedules are available. |
| `ctdb_solar_collector_calculator` | `ctdb_from_pv` | `ng2_solar_collector`, `surface_geometry` | `GEO-FK` | For each `cim_vector.pv` on building, write collector with `module_area`, azimuth/inclination from PV attrs, `lod2_multi_surface_id` from PV polygon. |
| `ctdb_utility_connection_calculator` | `ctdb_from_grid` | `ng2_utl_ntw_connection`, `ng2_cityobject` | `GEO-NONE` | If `project_scenario.grid_id` set, write electricity consumer connection on building energy cityobject. |
| `ctdb_refurbishment_calculator` | `ctdb_from_envelope_efficiency` | `ng2_refurbishment_measure` | `GEO-NONE` | When `envelope_efficiency=high`, insert synthetic wall/roof insulation measure with `library_code` pointing to TABULA post-retrofit class. |
| `ctdb_building_semantic_calculator` | `ctdb_from_cim` | `building`, `cityobject_genericattrib` | `GEO-FK` | Persist `yearOfConstruction`, `storeys_below_ground`, `class` as generic attributes; set `building.storeys_below_ground` from mixed-use LOD1.2 basement count. |

### 7.2 Deferred domains (classification only — no `ctdb_*` method)

| Domain | Tables affected | Classification | What would unblock a future method |
|--------|-----------------|----------------|-----------------------------------|
| **Occupants** | `ng2_occupants`, partition `int_heat_gains*` | `DEFERRED-OCCUPANTS` | Adopted national occupant template library + explicit user override per scenario |
| **Schedules** | `ng2_schedule`, `ng2_schedule_component`, partition `*_schedule_id` | `DEFERRED-SCHEDULES` | Committed hourly profile dataset (e.g. UNI/TS 11300 tables) bound to `scenario_id` |
| **Weather** | `ng2_weather_data`, `ng2_time_series` | `DEFERRED-WEATHER` | EPW file path or Meteonorm station ID stored on `cim_wizard_project_scenario` |
| **Post-simulation** | `ng2_resource`, `ng2_storage_device`, `cityobject_genericattrib` (`postSim_*`), `ng2_time_series` | `POSTSIM` | Simulator run completed; rows in `outputs.building_frassinetto3`, `outputs.battery`, `outputs.heating_frassinetto_hp2` |

### 7.3 Post-simulation calculator (`POSTSIM`)

| Calculator module | Method | Target table(s) | Geo | Logic (one line) |
|-------------------|--------|-----------------|-----|------------------|
| `ctdb_postsim_calculator` | `ctdb_genericattrib_from_outputs` | `cityobject_genericattrib` | `GEO-NONE` | Aggregate `outputs.*` hypertables per `building_id` and write `postSim_*` KPIs (temperature, heating load, SOC, COP). |
| `ctdb_postsim_calculator` | `ctdb_resource_from_outputs` | `ng2_resource` | `GEO-NONE` | Map annual or peak heating/electricity from simulation aggregates to `ng2_resource` (`enduse=heating`, `energy_carrier=electricity`). |
| `ctdb_postsim_calculator` | `ctdb_storage_device_from_outputs` | `ng2_storage_device`, `ng2_time_series` | `GEO-NONE` | When battery outputs exist, create storage device with capacity from scenario config and SOC series in `ng2_time_series`. |

### 7.4 Tables with no planned `ctdb_*` method (remain `SCHEMA`)

| Table | Geo | Reason |
|-------|-----|--------|
| `address`, `ng2_address_to_building_unit` | mixed | No address ingestion in CIM pipeline |
| `ade`, `codelist`, `codelist_entry`, `database_srs`, `datatype`, `namespace`, `objectclass` | `GEO-NONE` | DB bootstrap metadata |
| `feature`, `property`, `geometry_data` | mixed | CityGML v5 path; mapper uses v4 tables |
| `appearance`, `appear_to_surface_data`, `surface_data`, `surface_data_mapping`, `tex_image`, `implicit_geometry` | mixed | Appearance/texture pipeline not in scope |
| `ng2_ctyobj_relation` | `GEO-NONE` | Only needed for complex device–surface relations beyond current archetypes |
| `ng2_energy_perf_cert` | `GEO-NONE` | No EPC certificate data in CIM |
| `ng2_library` | `GEO-NONE` | Optional catalog; can reference TABULA codes inline without library rows |
| `ng2_suitability` | `GEO-NONE` | PV suitability already in `cim_vector.pv`; ADE suitability is optional |
| `ng2_urban_function_area` | `GEO-NONE` | Census land-use not mapped to ADE urban function |

---

## 8. Implementation phases (revised)

### Phase 1 — TABULA + LOD1.2 envelope

| Action | Calculator / method | Tables |
|--------|---------------------|--------|
| Geometry envelopes | `ctdb_envelope_calculator.ctdb_citymodel_envelope`, `ctdb_ref_point_calculator.ctdb_footprint_centroid` | `citymodel`, `cityobject`, `ng2_cityobject` |
| CIM + TABULA mirror | `ctdb_attrib_calculator.ctdb_cim_genericattrib_mirror`, `ctdb_qualified_attribute_calculator.ctdb_tabula_kpis` | `cityobject_genericattrib`, `ng2_qualified_attribute` |
| Energy ADE building | `ctdb_ng2_building_calculator.ctdb_from_tabula` | `ng2_building` |
| Constructions | `ctdb_layered_construction_calculator.ctdb_from_tabula` | `ng2_layered_construction` |
| Surfaces + zones | `ctdb_thematic_surface_calculator.ctdb_from_lod12`, `ctdb_thermal_partition_calculator.ctdb_from_lod12`, `ctdb_surf_zone_adjacency_calculator.ctdb_from_lod12` | `ng2_thematic_surface`, `ng2_building_partition`, `ng2_them_surf_to_thermal_zone` |

### Phase 2 — Materials, openings, HVAC archetypes

| Action | Calculator / method | Tables |
|--------|---------------------|--------|
| Material stacks | `ctdb_material_stack_calculator.ctdb_from_tabula` | `ng2_material`, `ng2_layer` |
| Glazing | `ctdb_opening_calculator.ctdb_from_tabula`, `ctdb_optical_property_calculator.ctdb_from_tabula` | `ng2_opening`, `ng2_optical_property` |
| HVAC + grid + PV | `ctdb_hvac_calculator.ctdb_from_fmu_archetype`, `ctdb_device_operation_calculator.ctdb_from_archetype`, `ctdb_solar_collector_calculator.ctdb_from_pv`, `ctdb_utility_connection_calculator.ctdb_from_grid` | `ng2_device`, `ng2_device_operation`, `ng2_solar_collector`, `ng2_utl_ntw_connection` |
| Retrofit hint | `ctdb_refurbishment_calculator.ctdb_from_envelope_efficiency` | `ng2_refurbishment_measure` |

### Phase 3 — Deferred + post-simulation (no pre-sim auto-fill)

| Domain | Classification | Methods |
|--------|----------------|---------|
| Occupants | `DEFERRED-OCCUPANTS` | — |
| Schedules | `DEFERRED-SCHEDULES` | — |
| Weather | `DEFERRED-WEATHER` | — |
| Simulation results | `POSTSIM` | `ctdb_postsim_calculator.*` (Section 7.3) |

---

## 9. Summary statistics

### 9.1 Conceptual attribute vocabulary (Section 4)

| Category | Attributes listed | Mapped / partial today | Calculated in CIM only | Schema / planned |
|----------|-------------------|------------------------|------------------------|------------------|
| CityGML Core + Building | 22 | 4 | 3 | 15 |
| Energy ADE building core | 9 | 2 partial | 2 | 5 |
| Energy demand / weather / system | 10 | 1 partial | 0 | 9 |
| ThermalZone / Boundary / Opening | 11 | 5 partial | 0 | 6 |
| Occupant behaviour | 11 | 2 partial | 2 | 7 |
| Time series / schedules | 7 | 0 | 0 | 7 |
| **Total** | **70** | **~14 partial/full** | **~7** | **~49** |

### 9.2 Physical storage per typical building (current mapper)

| Layer | Approximate scalar fields |
|-------|--------------------------|
| Building `cityobject` + `building` | 5–6 |
| Building `genericattrib` (single zone) | up to 5 |
| Building `genericattrib` (N zones) | 2 + 7N |
| Per surface (6 typical) | 1 U-value + geometry |
| **Total semantic scalars** | **~20–50** depending on zone count |

### 9.3 Full schema potential (all 53 tables populated)

When all phases are implemented for a typical Italian residential building with 6 surfaces and 1–4 thermal zones, expect on the order of **200–350 stored attribute values** across `citydb` (excluding raw geometry vertices).

---

## 10. Master field-mapping table (687 rows)

**Machine-readable file:** [`citygml-energyade-field-mapping.csv`](citygml-energyade-field-mapping.csv)  
**Regenerator:** `docs/generate_field_mapping.py` (run after schema dictionary changes)

Each row maps one **CityDB column**, **virtual genericattrib key**, **LOD1.2 JSON path**, or **CIM source column** to the calculator that should fill it.

### 10.1 Column definitions

| Column | Description |
|--------|-------------|
| `row_id` | Sequential row number |
| `citydb_address` | Target address: `citydb.<table>.<column>` or `citydb.cityobject_genericattrib.<attrname>→<valcol>` or `cim_vector.<path>` for sources |
| `pg_type` | PostgreSQL type from schema dictionary |
| `attribute_type` | Simplified type: `geometry`, `text`, `numeric`, `integer`, `boolean`, `fk`, `timestamp`, `json` |
| `geo_role` | `GEO-DIRECT`, `GEO-FK`, or `GEO-NONE` |
| `status` | `MAPPED`, `PLANNED-1`, `PLANNED-3`, `CALCULATED`, `SCHEMA`, `DB-INIT`, `DEFERRED-*`, `POSTSIM` |
| `calculator` | Python module name (e.g. `ctdb_ng2_building_calculator`) or `—` |
| `method` | Method name (e.g. `ctdb_from_tabula`, `map_scenario_to_citydb`) |
| `cim_source` | Source field path in `cim_vector` or derived constant |
| `logic` | One-line fill rule |

### 10.2 Row inventory summary

| Category | Rows | Description |
|----------|------|-------------|
| `citydb.*` schema columns | 612 | One row per column in `citydb_schema_dictionary.csv` |
| `cityobject_genericattrib.*` virtual keys | 46 | EAV attrnames: `cim_*`, `tabula_*`, `thermalZone_*`, `tz:*`, `u_value_w_m2k`, `postSim_*` |
| `building_surfaces_lod12.*` JSON paths | 9 | LOD1.2 geometry and physics leaf paths |
| `cim_vector.cim_wizard_*` source columns | 20 | Input inventory for building + building_properties |
| **Total** | **687** | |

### 10.3 Status breakdown

| Status | Rows | Meaning |
|--------|------|---------|
| `SCHEMA` | ~198 | No planned fill method |
| `PLANNED-1` | ~121 | TABULA + LOD1.2 envelope (`ctdb_*` Phase 1) |
| `PLANNED-3` | ~123 | Materials, openings, HVAC, PV (`ctdb_*` Phase 2) |
| `DEFERRED-SCHEDULES` | ~68 | Schedules / time series — classification only |
| `POSTSIM` | ~52 | Post-simulation outputs |
| `MAPPED` | ~38 | Written today by `map_scenario_to_citydb` |
| `DB-INIT` | ~33 | Database bootstrap tables |
| `DEFERRED-OCCUPANTS` | ~20 | Occupant behaviour |
| `DEFERRED-WEATHER` | ~12 | Weather / climate |
| `CALCULATED` | ~2 | CIM pipeline only, not yet in citydb |

### 10.4 Sample rows (illustrative — full list in CSV)

| citydb_address | attribute_type | calculator | method | cim_source | logic |
|----------------|----------------|------------|--------|------------|-------|
| `citydb.cityobject.gmlid` | text | `citydb_mapper_calculator` | `map_scenario_to_citydb` | `cim_wizard_building.building_id` | Map building UUID to CityObject gmlid |
| `citydb.building.measured_height` | numeric | `citydb_mapper_calculator` | `map_scenario_to_citydb` | `cim_wizard_building_properties.height` | Direct copy |
| `citydb.surface_geometry.geometry` | geometry | `citydb_mapper_calculator` | `map_scenario_to_citydb` | `building_surfaces_lod12.surfaces.*.geometry` | GeoJSON PolygonZ EPSG:4326 |
| `citydb.cityobject_genericattrib.u_value_w_m2k→realval` | numeric | `citydb_mapper_calculator` | `map_scenario_to_citydb` | `const_tabula → TABULA_U_VALUES` | TABULA U on each surface |
| `citydb.cityobject_genericattrib.tabula_u_wall→realval` | numeric | `ctdb_tabula_attrib_calculator` | `ctdb_from_const_tabula` | `const_tabula` | TABULA wall U-value W/m²K |
| `citydb.ng2_building.type` | text | `ctdb_ng2_building_calculator` | `ctdb_from_tabula` | `cim_wizard_building_properties.type` | Usage type |
| `citydb.ng2_building_partition.heat_capacity` | numeric | `ctdb_thermal_partition_calculator` | `ctdb_from_lod12` | `thermal_zones[].volume_m3` | One zone per building level |
| `citydb.ng2_thematic_surface.azimuth` | numeric | `ctdb_thematic_surface_calculator` | `ctdb_from_lod12` | `wall_surfaces[].properties.azimuth_degrees` | Wall orientation |
| `citydb.ng2_layered_construction.u_value` | numeric | `ctdb_layered_construction_calculator` | `ctdb_from_tabula` | `const_tabula` | TABULA opaque U per element |
| `citydb.ng2_device.model` | text | `ctdb_hvac_calculator` | `ctdb_from_fmu_archetype` | `fmu_file` | FMU archetype name |
| `citydb.ng2_occupants.num_of_occupants` | numeric | — | — | — | DEFERRED-OCCUPANTS |
| `citydb.ng2_schedule.usage_value` | numeric | — | — | — | DEFERRED-SCHEDULES |
| `citydb.ng2_weather_data.position` | geometry | — | — | — | DEFERRED-WEATHER |
| `citydb.ng2_resource.amount` | numeric | `ctdb_postsim_calculator` | `ctdb_resource_from_outputs` | `outputs.*` | POSTSIM heating/electricity |
| `cim_vector.cim_wizard_building.building_surfaces_lod12` | json | `building_geo_lod12_calculator` | `generate_lod12_surfaces` | footprint + height | Semantic surfaces + thermal zones |

### 10.5 `cityobject_genericattrib` virtual keys (46 rows)

Grouped by prefix — each becomes one EAV row (`attrname` + value column) on a building or surface CityObject:

| Prefix | Keys | Calculator | Source |
|--------|------|------------|--------|
| *(surface)* | `u_value_w_m2k` | `citydb_mapper_calculator` | `const_tabula` |
| `thermalZone_*` | `volume_m3`, `floorArea_m2`, `numberOfFloors`, `count` | `citydb_mapper_calculator` | properties / thermal_zones |
| `tz:{zone_id}:*` | `usage`, `volume_m3`, `floor_area_m2`, `is_heated`, `is_cooled`, `storey_index`, `apartment_index` | `citydb_mapper_calculator` | `thermal_zones[]` per level |
| `energySystem_*` | `envelopeEfficiency`, `fmuFile` | `citydb_mapper_calculator` | properties |
| `cim_*` | 19 mirrors of building + properties columns | `ctdb_attrib_calculator` | `cim_wizard_*` tables |
| `tabula_*` | `period_code`, `u_wall`, `u_roof`, `u_ground`, `g_window`, `envelope_class`, `constr_weight`, `glazing_ratio` | `ctdb_tabula_attrib_calculator` | `const_tabula` lookup |
| `postSim_*` | `meanIndoorTemp_C`, `annualHeating_kWh`, `batterySOC_pct`, `hpCOP` | `ctdb_postsim_calculator` | `outputs` schema |

---

## 11. Related files

| File | Role |
|------|------|
| [`tabula-archetype-extraction-guide.md`](tabula-archetype-extraction-guide.md) | TABULA XLS catalog → `cim_wizard_building_properties` + CityDB mapping plan |
| [`citygml-energyade-field-mapping.csv`](citygml-energyade-field-mapping.csv) | **687-row** master mapping (calculator, method, cim_source, logic per field) |
| `docs/generate_field_mapping.py` | Regenerate mapping CSV from schema dictionary + rules |
| `cim-database/citydb_schema_dictionary.csv` | Machine-readable column catalog (612 citydb columns) |
| `cim-database/init-db/energy_ade_2.sql` | Energy ADE 2.0 DDL |
| `cim-database/energyade` | Full deployed schema dump |
| `app/calculators/citydb_mapper_calculator.py` | Pre-sim mapper + CityJSON builder |
| `app/calculators/building_geo_lod12_calculator.py` | LOD1.2 surfaces and thermal zones |
| `app/core/configuration.json` | Pipeline calculator registry |
| `app/models/citydb.py` | SQLAlchemy models (subset of 53 tables) |

---

## 12. Maintenance

When extending the mapper:

1. Update the relevant table section in this document.
2. Add a row to `citydb_schema_dictionary.csv` if new columns are introduced.
3. Extend `app/models/citydb.py` ORM models for any newly written `ng2_*` table.
4. Register new `ctdb_*_calculator` modules in `app/core/configuration.json` and document their method in Section 7.1.
5. Re-run `python docs/generate_field_mapping.py` to refresh Section 10 CSV.
6. Keep conceptual Section 4 aligned with Energy ADE 1.0 teaching names and ADE 2.0 storage names.
