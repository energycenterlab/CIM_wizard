# TABULA Archetype Extraction Guide

**Project:** CIM Wizard Integrated  
**Purpose:** Guide for a new calculator that loads **all extractable TABULA data** per building and persists it on `cim_vector.cim_wizard_building_properties` (and later maps to CityDB / Energy ADE).  
**Prerequisite calculator:** `BuildingTabulaTypeCalculator` → `tabula_type` (e.g. `IT.RES.TABULA_5`)  
**Source data:** `cim-database/materiale-tabula/materiale tabula/`  
**Related docs:** [`citygml-energyade-attribute-matrix.md`](citygml-energyade-attribute-matrix.md), [`citygml-energyade-field-mapping.csv`](citygml-energyade-field-mapping.csv), `cim-database/citydb_schema_dictionary.csv`

---

## 1. What you have today vs what TABULA offers

| Layer | Today (`building_tabula_type_calculator`) | Full TABULA (`materiale-tabula/`) |
|-------|-------------------------------------------|-------------------------------------|
| Building period | `const_tabula` = `TABULA_1…7` | Same, aligned with `Epoca` in catalog |
| Building label | `tabula_type` = `IT.RES.TABULA_5` | Catalog row = `SFH_05`, `MFH_05`, `TH_05`, `AB_05` |
| Envelope U-values | 3 scalars in code (`TABULA_U_VALUES` in mapper) | **Per-component U** from Politecnico XLS (46 construction codes) |
| Layer stacks | Not stored | **3–10 layers** per wall/roof/floor/ceiling (s, ρ, μ, c, λ) |
| Dynamic / hygro | Not stored | Ammettenza, trasmittanza periodica, Glaser, condensa |
| Per surface | LOD1.2 geometry only | U + construction code **per wall/roof/floor/ceiling** |

The new calculator should close the gap between `tabula_type` and the **Italian TABULA construction catalog**.

---

## 2. TABULA file inventory (`cim-database/materiale-tabula/`)

### 2.1 Master catalog — `TABULA_Codici_costruzioni.xlsx`

**32 building archetypes** × **8 construction periods**:

| Prefix | Meaning | Rows |
|--------|---------|------|
| `SFH` | Single-family house | `SFH_01` … `SFH_08` |
| `MFH` | Multi-family house | `MFH_01` … `MFH_08` |
| `TH` | Terraced house | `TH_01` … `TH_08` |
| `AB` | Apartment block | `AB_01` … `AB_08` |

**Period (`Epoca`) mapping** (matches `const_tabula` / `TABULA_1…7`):

| Catalog suffix | Epoca | `const_tabula` |
|----------------|-------|----------------|
| `_01` | Fino al 1900 | `TABULA_1` |
| `_02` | 1901–1920 | `TABULA_2` |
| `_03` | 1921–1945 | `TABULA_3` |
| `_04` | 1946–1960 | `TABULA_4` |
| `_05` | 1961–1975 | `TABULA_5` |
| `_06` | 1976–1990 | `TABULA_6` |
| `_07` | 1991–2005 | `TABULA_7` |
| `_08` | Dopo il 2005 | `TABULA_7` (extend to `TABULA_8` if you add post-2005 U table) |

**Envelope slots per archetype row** (Italian labels in row 0):

| Slot | TABULA role | Maps to LOD1.2 | Typical code prefix |
|------|-------------|----------------|---------------------|
| **Copertura** | Roof | `surfaces.roof_surface` | `Roof_*` |
| **Ultimo solaio** (se sottotetto non risc.) | Ceiling under unheated attic | top `floor_surfaces` / attic boundary | `Ceiling_*` |
| **Parete1** | Main external wall | `wall_surfaces[0]` or largest area | `Wall_*` |
| **Parete2** | Second wall type | `wall_surfaces[1]` | `Wall_*` |
| **Parete3** | Third wall type | `wall_surfaces[2]` | `Wall_*` |
| **Solaio1** | Ground / main floor slab | `ground_surface` or `floor_surfaces[0]` | `Floor_*` |
| **Solaio2** | Upper floor slab | `floor_surfaces[1+]` | `Floor_*` |

**Example `SFH_01`:** `Roof_01.01`, `Wall_01.03`, `Floor_01.04`  
**Example `MFH_05`:** `Roof_03.01`, `Ceiling_03.01`, `Wall_03.01`, `Wall_04.01`, `Floor_03.01`  
**Example `AB_08`:** `Roof_07.02`, `Ceiling_08.01`, `Wall_08.01`, `Wall_08.02`, `Floor_08.01`

**46 unique construction codes** referenced across all archetypes:

| Element | Count in catalog |
|---------|------------------|
| `Wall_*` | 20 |
| `Floor_*` | 10 |
| `Ceiling_*` | 9 |
| `Roof_*` | 7 |

**101 local XLS/XLSX files** in the folder (one per construction code; all catalog codes are present).

### 2.2 Component workbooks — `Wall_01.03.xlsx`, `Roof_06.02.xlsx`, etc.

Each file follows the **Politecnico di Torino DENER** template (UNI EN ISO 13786 / 13788).

| Sheet | Extractable content |
|-------|---------------------|
| **Caratteristiche componente** | Component type; **layer stratigraphy** (name, thickness s [cm], ρ [kg/m³], μ [-], c [J/kg°C], λ [W/m°C]) |
| **Materiali** | Material library (type, name, ρ, cp, λ, vapour permeability, μ-factor) |
| **Dati** | **Trasmittanza** U [W/m²K]; **Ammettenza interna/esterna**; **Trasmittanza periodica** (dynamic) |
| **Calcoli componente** | Intermediate calculation tables |
| **Calcoli matriciali** | Matrix method for dynamic properties |
| **Glaser** | Interstitial condensation assessment |
| **Condensa** | Surface condensation risk |
| **Temperatura / Pressione vapore** | Profile charts (usually skip for DB; keep PDF export only) |
| **Grafici** | Charts (skip for DB) |

**Example extracted scalars (`Wall_01.03` / sheet `Dati`):**

| Parameter | Value | Unit |
|-----------|-------|------|
| Trasmittanza (U) | 1.611 | W/m²K |
| Ammettenza interna | 4.320 | W/m²K |
| Ammettenza esterna | 6.608 | W/m²K |
| Trasmittanza periodica | 0.266 | W/m²K |

**Example layer stack (`Wall_01.03` / Caratteristiche):**

| Layer | s (cm) | ρ (kg/m³) | μ | c (J/kg°C) | λ (W/m°C) |
|-------|--------|-----------|---|------------|-----------|
| intonaco int. | 2 | 1400 | 11.1 | 840 | 0.7 |
| muratura pietra-mattoni | 36 | 2000 | 5.3 | 840 | 0.9 |
| intonaco est. | 2 | 1800 | 23.5 | 840 | 0.9 |

---

## 3. Resolving `tabula_type` → archetype code

Current `tabula_type` format: `IT.{USAGE}.{PERIOD}` e.g. `IT.RES.TABULA_5`.

Catalog archetype code: `{CLASS}_{PERIOD_SUFFIX}` e.g. `SFH_05`.

### 3.1 Resolution table

| Step | Input | Output |
|------|-------|--------|
| 1 | `tabula_type` or `const_tabula` | period suffix `_01…_08` |
| 2 | Building class heuristic | prefix `SFH` / `MFH` / `TH` / `AB` |
| 3 | Join | `tabula_archetype_code` = e.g. `SFH_05` |
| 4 | Lookup | row in `TABULA_Codici_costruzioni.xlsx` |
| 5 | For each slot | construction code `Wall_06.02`, … |
| 6 | Open XLS | full layer + U data |

### 3.2 Building class heuristic (not in TABULA period alone)

`building_type` today is only `residential` / `non-residential`. To pick `SFH` vs `MFH` vs `TH` vs `AB`:

| Heuristic | Suggested class | Confidence |
|-----------|-----------------|------------|
| `filter_res=false` | No archetype (skip or `NRES` generic) | — |
| `number_of_floors == 1` and `n_family <= 1` | `SFH` | Medium |
| `number_of_floors == 1` and `n_family > 1` | `TH` | Low |
| `number_of_floors` 2–3 | `TH` or `MFH` | Low |
| `number_of_floors >= 4` | `AB` | Medium |
| `area` very large + many floors | `MFH` or `AB` | Low |
| User override column `tabula_building_class` | Exact | High |

**Recommendation:** add scalar `tabula_archetype_code` (e.g. `SFH_05`) on `cim_wizard_building_properties` and allow manual override in pgAdmin / API.

### 3.3 Period suffix from `const_tabula`

| `const_tabula` | Suffix | Notes |
|----------------|--------|-------|
| `TABULA_1` | `_01` | |
| `TABULA_2` | `_02` | |
| … | … | |
| `TABULA_7` + `const_year > 2005` | `_08` | Use `const_year` to distinguish `_07` vs `_08` |

---

## 4. Maximum extractable data (by target)

### 4.1 Building level → `cim_wizard_building_properties`

**Tier A — scalars (index / query columns)**

| Proposed column | Type | Source | Example |
|-----------------|------|--------|---------|
| `tabula_archetype_code` | `varchar(10)` | catalog | `SFH_05` |
| `tabula_building_class` | `varchar(4)` | heuristic | `SFH` |
| `tabula_u_roof` | `float` | `Roof_*` Dati | 2.22 |
| `tabula_u_wall` | `float` | primary `Parete1` | 1.61 |
| `tabula_u_wall_2` | `float` | `Parete2` if present | 1.26 |
| `tabula_u_ground` | `float` | `Solaio1` / ground | 1.60 |
| `tabula_u_ceiling` | `float` | `Ultimo solaio` | 0.97 |
| `tabula_constr_weight` | `varchar` | derived from period | `heavy` / `medium` / `light` |

**Tier B — JSON document (full envelope, recommended: `tabula_envelope_json` JSONB)**

```json
{
  "archetype_code": "SFH_05",
  "epoca": "1961-1975",
  "const_tabula": "TABULA_5",
  "tabula_type": "IT.RES.TABULA_5",
  "components": {
    "roof": {
      "slot": "Copertura",
      "code": "Roof_03.01",
      "description": "Tetto a falde in laterizio (U=2,2 W/m2K)",
      "u_value": 2.217,
      "layers": [
        {"name": "...", "thickness_m": 0.02, "density": 1400, "lambda": 0.7, "cp": 840, "mu": 11.1}
      ],
      "dynamic": {"y_internal": 4.32, "y_external": 6.61, "u_periodic": 0.266}
    },
    "wall_primary": { "code": "Wall_04.02", "u_value": 1.26, "layers": [] },
    "wall_secondary": null,
    "ceiling_attic": { "code": "Ceiling_03.01", "u_value": 0.97, "layers": [] },
    "floor_primary": { "code": "Floor_03.01", "u_value": 0.85, "layers": [] }
  },
  "envelope_kpi": {
    "u_opaque_area_weighted": 1.35,
    "source": "TABULA_Codici_costruzioni + Politecnico XLS"
  }
}
```

**Tier C — not on `building_properties` (too large / relational)**

- Full `Materiali` sheet (200+ rows per file) → keep in catalog cache on disk, not per building.
- Glaser / Condensa chart series → store boolean flags only: `tabula_condensation_risk: low|medium|high`.

### 4.2 Thermal zone level (one zone per storey — `building_surfaces_lod12.thermal_zones[]`)

TABULA does **not** define per-zone schedules or gains. You can still attach **zone-relevant envelope fragments**:

| Data | Source | Storage suggestion |
|------|--------|-------------------|
| `zone_id`, `storey_index` | LOD1.2 | already in JSON / `tz:*` genericattrib |
| Floor slab U below zone | `Solaio1` / `floor_surfaces` for storey | `tabula_envelope_json.zones[].u_floor` |
| Ceiling U above zone | `Ceiling_*` if top storey under attic | `tabula_envelope_json.zones[].u_ceiling` |
| `heat_capacity` proxy | zone `volume_m3` × air density × cp | `ng2_building_partition.heat_capacity` (CityDB) |
| `infiltration_rate` | TABULA typical (not in XLS) | deferred — national table |
| Occupants / schedules | not in TABULA | `DEFERRED-OCCUPANTS` / `DEFERRED-SCHEDULES` |

**Per-zone JSON snippet (inside `tabula_envelope_json`):**

```json
"zones": [
  {
    "zone_id": "z1",
    "storey_index": 0,
    "u_floor": 0.85,
    "u_ceiling": 2.22,
    "linked_surfaces": ["ground_surface", "floor_s1"]
  }
]
```

### 4.3 Thermal surface level (LOD1.2 walls / roof / floors)

Map each LOD1.2 surface to a TABULA component:

| LOD1.2 surface | TABULA slot | Properties to write |
|----------------|-------------|---------------------|
| `wall_surfaces[i]` | `Parete{i+1}` or area-ranked | `u_value`, `construction_code`, `layers[]`, `azimuth` (from LOD1.2) |
| `roof_surface` | `Copertura` | `u_value`, `construction_code`, `inclination` |
| `ground_surface` | `Solaio1` (ground contact) | `u_value`, `construction_code` |
| `floor_surfaces[i]` | `Solaio1/2` or `Ceiling_*` between storeys | `u_value`, `storey_index` |

**Maximum per surface (extractable from TABULA + LOD1.2):**

| Attribute | TABULA XLS | LOD1.2 | CityDB `ng2_thematic_surface` | CityDB `ng2_layered_construction` |
|-----------|------------|--------|--------------------------------|-----------------------------------|
| U-value | Dati.Trasmittanza | — | via construction link | `u_value` |
| Construction code | catalog | — | — | `library_code` |
| Area m² | — | `properties.area_m2` | `total_surf_area` | — |
| Azimuth | — | `properties.azimuth_degrees` | `azimuth` | — |
| Inclination | — | `properties.inclination_degrees` | `inclination` | — |
| Layer thickness | Caratteristiche | — | `thickness` (sum of s) | `ng2_layer.thickness` |
| λ, ρ, cp | Caratteristiche | — | `heat_capacity` (derived) | `ng2_material.*` |
| g-value (windows) | not in opaque XLS | — | — | `g_value` (separate window typology) |
| Dynamic Y | Dati | — | `ng2_qualified_attribute` | — |
| Glazing ratio | not in wall XLS | — | `open_to_surf_ratio` | `glazing_ratio` (TABULA default table) |

### 4.4 Materials (`ng2_material` + `ng2_layer`)

From each layer row in **Caratteristiche componente**:

| XLS column | `ng2_material` field | Transform |
|------------|-------------------|-----------|
| layer name | `library_code` | slugify name |
| λ | `thm_conductivity` | W/m°C |
| c | `spec_heat_capacity` | J/kgK |
| ρ | `density` | kg/m³ |
| μ | `permeance` / vapour factor | map per ISO 13788 |
| s [cm] | `ng2_layer.thickness` | ÷ 100 → m |

Up to **~10 layers × 6 component types × 32 archetypes** in catalog — per building you store **only the 4–6 components** assigned to that archetype.

---

## 5. CityDB / Energy ADE mapping summary

Cross-reference: [`citygml-energyade-field-mapping.csv`](citygml-energyade-field-mapping.csv).

| TABULA extraction | CityDB table.column | Calculator (planned) |
|-------------------|---------------------|----------------------|
| Archetype `SFH_05` | `ng2_building` + `library_code` genericattrib | `ctdb_ng2_building_calculator` |
| U roof/wall/floor | `ng2_layered_construction.u_value` | `ctdb_layered_construction_calculator` |
| Layer stack | `ng2_layer`, `ng2_material` | `ctdb_material_stack_calculator` |
| Surface area/azimuth | `ng2_thematic_surface` | `ctdb_thematic_surface_calculator` |
| Surface ↔ zone | `ng2_them_surf_to_thermal_zone` | `ctdb_surf_zone_adjacency_calculator` |
| U on surface | `cityobject_genericattrib.u_value_w_m2k` | `citydb_mapper_calculator` (today: 3 coarse U's) |
| TABULA KPIs | `ng2_qualified_attribute` | `ctdb_qualified_attribute_calculator` |
| Full mirror | `cityobject_genericattrib.tabula_*` | `ctdb_tabula_attrib_calculator` |
| Per-building JSON | `cim_wizard_building_properties.tabula_envelope_json` | **`building_tabula_archetype_calculator`** (new) |

---

## 6. Proposed calculator: `building_tabula_archetype_calculator`

### 6.1 Placement in pipeline

```
building_construction_year   → const_year, const_tabula
building_type                → type
building_tabula_type         → tabula_type
building_tabula_archetype    → tabula_archetype_code + tabula_envelope_json  ← NEW
building_geo_lod12           → surfaces (for per-surface assignment in Phase 2)
citydb_mapper / ctdb_*       → CityDB persistence
```

Register in `configuration.json` as feature `building_tabula_archetype` with method `from_tabula_catalog`.

### 6.2 Dependencies (injected via pipeline)

| Feature read | Used for |
|--------------|----------|
| `building_tabula_type` | period + usage label |
| `building_construction_year` | `const_year`, `const_tabula`, `const_period_census` |
| `building_type` | residential gate |
| `building_n_floors` | SFH/MFH/TH/AB heuristic |
| `building_n_families` | SFH vs TH hint |
| `filter_res` | skip non-residential |
| `building_geo` | building list for DB batch upsert |

### 6.3 Method skeleton

```python
class BuildingTabulaArchetypeCalculator(BaseCalculator):
    """Load TABULA catalog + component XLS for each building."""

    CATALOG_PATH = "cim-database/materiale-tabula/materiale tabula/TABULA_Codici_costruzioni.xlsx"
    COMPONENTS_DIR = "cim-database/materiale-tabula/materiale tabula"

    def from_tabula_catalog(self) -> Optional[Dict[str, Any]]:
        tabula_types = self.pipeline.get_feature_safely("building_tabula_type", ...)
        construction = self.pipeline.get_feature_safely("building_construction_year", ...)
        floors = self.pipeline.get_feature_safely("building_n_floors", ...)
        # ... load catalog once (cache on class or data_manager)

        archetype_codes = []
        envelope_jsons = []
        u_roofs, u_walls, u_grounds = [], [], []

        for i, building in enumerate(buildings):
            code = self._resolve_archetype_code(i, tabula_types, construction, floors, ...)
            row = catalog[catalog["Codice ed."] == code].iloc[0]
            components = self._components_from_row(row)
            envelope = self._build_envelope_json(code, row, components)
            archetype_codes.append(code)
            envelope_jsons.append(envelope)
            u_roofs.append(envelope["components"]["roof"]["u_value"])
            # ...

        result = {
            "tabula_archetype_codes": archetype_codes,
            "tabula_envelope_jsons": envelope_jsons,
            "tabula_u_roofs": u_roofs,
            "tabula_u_walls": u_walls,
            # ...
        }
        self.data_manager.set_feature("building_tabula_archetype", result)
        return result

    def _parse_component_xls(self, code: str) -> dict:
        """Read Caratteristiche + Dati sheets → u_value + layers."""
        ...
```

### 6.4 Supporting module (recommended)

`app/calculators/tabula/tabula_catalog_loader.py`:

- `load_archetype_catalog() -> pd.DataFrame`
- `get_archetype_row(code: str) -> dict`
- `parse_construction_code(code: str) -> dict`  # U + layers from XLS
- Cache parsed XLS in memory (`lru_cache`) — 46 files, parse once per process.

**Do not** put pandas/openpyxl in every calculator method call without caching.

### 6.5 Database columns (pgAdmin)

```sql
ALTER TABLE cim_vector.cim_wizard_building_properties
    ADD COLUMN IF NOT EXISTS tabula_archetype_code VARCHAR(10);

ALTER TABLE cim_vector.cim_wizard_building_properties
    ADD COLUMN IF NOT EXISTS tabula_envelope_json JSONB;

ALTER TABLE cim_vector.cim_wizard_building_properties
    ADD COLUMN IF NOT EXISTS tabula_u_roof DOUBLE PRECISION;

ALTER TABLE cim_vector.cim_wizard_building_properties
    ADD COLUMN IF NOT EXISTS tabula_u_wall DOUBLE PRECISION;

ALTER TABLE cim_vector.cim_wizard_building_properties
    ADD COLUMN IF NOT EXISTS tabula_u_ground DOUBLE PRECISION;

ALTER TABLE cim_vector.cim_wizard_building_properties
    ADD COLUMN IF NOT EXISTS tabula_u_ceiling DOUBLE PRECISION;

ALTER TABLE cim_vector.cim_wizard_building_properties
    ADD COLUMN IF NOT EXISTS tabula_building_class VARCHAR(4);
```

Update `app/models/vector.py` `BuildingProperties` to match.

### 6.6 Persistence pattern (same as `building_tabula_type`)

In `building_analysis_route.py`:

```python
elif feature_name == "building_tabula_archetype":
    for col, key in [
        ("tabula_archetype_code", "tabula_archetype_codes"),
        ("tabula_u_roof", "tabula_u_roofs"),
        ("tabula_u_wall", "tabula_u_walls"),
        ("tabula_u_ground", "tabula_u_grounds"),
        ("tabula_u_ceiling", "tabula_u_ceilings"),
        ("tabula_envelope_json", "tabula_envelope_jsons"),
    ]:
        data_manager.upsert_building_properties_batch(bldgs, project_id, scenario_id, col, vals)
```

Add JSON cast in `data_manager._CAST` for `tabula_envelope_json`.

---

## 7. Phase plan

### Phase 1 — Building envelope scalars + JSON (this calculator)

- [ ] `tabula_catalog_loader.py` parse catalog + 46 XLS U-values
- [ ] `building_tabula_archetype_calculator.from_tabula_catalog`
- [ ] DB columns + ORM + API editable fields
- [ ] Replace coarse `TABULA_U_VALUES` in mapper with `tabula_u_wall` etc. when present

### Phase 2 — Per LOD1.2 surface assignment

- [ ] After `building_geo_lod12`, map each `wall_surfaces[i]` → `Parete{i}` U and code
- [ ] Store in `building_surfaces_lod12` under `semantic.tabula` or separate `cim_wizard_building_surface_tabula` table
- [ ] Feed `ctdb_thematic_surface_calculator` + `ctdb_layered_construction_calculator`

### Phase 3 — Full layer stacks → CityDB

- [ ] `ng2_material`, `ng2_layer`, `ng2_layered_construction` from layer rows
- [ ] `ng2_qualified_attribute` for dynamic Y and periodic U

### Phase 4 — Hygrothermal flags

- [ ] Parse Glaser/Condensa sheets → boolean risk flags on envelope JSON

---

## 8. Data volume estimate (per building)

| Item | Count | Size |
|------|-------|------|
| Scalar TABULA fields | ~10 columns | ~100 bytes |
| `tabula_envelope_json` | 1 document | 4–15 KB (6 components × layers) |
| Per-surface overlay (Phase 2) | 6–20 surfaces | +2–5 KB in LOD1.2 JSON |
| CityDB rows (Phase 3) | ~4 constructions + 12 layers + 12 materials | relational |

---

## 9. Limits — what TABULA cannot give you

| Attribute | Status |
|-----------|--------|
| Occupant heat gains | `DEFERRED-OCCUPANTS` |
| HVAC / heat pump COP | FMU archetype (`fmu_file`), not TABULA XLS |
| Schedules | `DEFERRED-SCHEDULES` |
| Weather | `DEFERRED-WEATHER` |
| Window g-value per building | Not in opaque component XLS — use TABULA national window table or defaults |
| Exact SFH vs AB without heuristic | Needs `tabula_building_class` override or census typology |
| Post-retrofit U | Use `envelope_efficiency` + `ng2_refurbishment_measure`, not original archetype |

---

## 10. Quick reference — file → field

```
TABULA_Codici_costruzioni.xlsx
  └─ Codice ed. (SFH_05)
       ├─ Copertura      → Roof_03.01.xlsx  → u_value, layers[]
       ├─ Parete1        → Wall_04.02.xlsx  → u_value, layers[]
       ├─ Parete2        → Wall_03.01.xlsx  → optional
       ├─ Ultimo solaio  → Ceiling_03.01.xlsx
       ├─ Solaio1        → Floor_03.01.xlsx
       └─ Solaio2        → (if present)

cim_wizard_building_properties
  ├─ tabula_type              IT.RES.TABULA_5     (existing)
  ├─ tabula_archetype_code    SFH_05              (new)
  ├─ tabula_u_wall / roof / …                     (new scalars)
  └─ tabula_envelope_json     full document       (new JSONB)

building_surfaces_lod12 (Phase 2)
  └─ surfaces.wall_surfaces[].tabula → { code, u_value, layers }

citydb (Phase 3, via ctdb_*)
  ├─ ng2_layered_construction.u_value
  ├─ ng2_material.*
  ├─ ng2_thematic_surface.*
  └─ cityobject_genericattrib.u_value_w_m2k
```

---

## 11. Related files

| Path | Role |
|------|------|
| `cim-database/materiale-tabula/materiale tabula/TABULA_Codici_costruzioni.xlsx` | 32 archetypes → construction codes |
| `cim-database/materiale-tabula/materiale tabula/{Wall,Roof,Floor,Ceiling}_*.xlsx` | Layer stacks + U-values |
| `app/calculators/building_tabula_type_calculator.py` | Produces `tabula_type` (prerequisite) |
| `app/calculators/citydb_mapper_calculator.py` | Today: simplified `TABULA_U_VALUES` |
| `docs/citygml-energyade-attribute-matrix.md` | CityDB field matrix + `ctdb_*` plan |
| `docs/citygml-energyade-field-mapping.csv` | 687-row field mapping |
| `docs/sql/add_tabula_type_column.sql` | Example migration for `tabula_type` |

---

## 12. Maintenance

1. When adding TABULA columns, update `vector.py`, `data_manager._CAST`, `vector_routes._BP_EDITABLE_FIELDS`, and `generate_field_mapping.py`.
2. Re-run `python docs/generate_field_mapping.py` after CityDB mapping changes.
3. Keep XLS parser tolerant of `.xls` vs `.xlsx` (use `pd.ExcelFile`).
