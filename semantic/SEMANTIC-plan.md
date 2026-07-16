# Semantic layer plan — CIM Wizard VKG / OBDA

Study the feasibility of **automatically** building and maintaining a **Virtual Knowledge Graph (VKG)** over the CityDB / energy schema (Ontop `.obda` / R2RML, e.g. `semantic/ontop/cim_citydb.obda`), so that when domain ontologies evolve, mappings can be regenerated or patched with validation rather than full manual rewrite.

**Approach:** fine-tune a spatial-SQL LLM on the CIM Wizard dataset (`ai4db/` → `txt2ssql/`), evaluate with `assist_cim/`, and use it to generate **source SQL** in Ontop mappings while ontology rules supply **target RDF templates** — see [Fine-tuned Text-to-SQL → OBDA pipeline](#fine-tuned-text-to-sql--obda-pipeline-project-repos).

**Reference stack (2025–2026):**

| Paper | File | Role in CIM VKG plan |
|-------|------|----------------------|
| LLM4VKG (IJCAI 2025) | `phd_proposal/llm4vkg.pdf` | Mapping bootstrap + ontology completion |
| RML Meets LLMs | `semantic/17_RML_Meets_LLMs_More_Structu.pdf` | LLM inside mappings for semi-structured UBEM fields |
| BLINKG (TGDK 2026) | `semantic/BLINKG.pdf` | Per-task mapping benchmark + O5 evaluation protocol |

---

## Ontology stack (three layers)

The stack below is the **target reference model** for smart-city / building digital twins. The **`semantic/ontop/`** folder currently materializes **layer 1 (partially)** and **layer 3 (core set)**; upper ontologies and Brick / SERAF are **not yet checked in** but are listed here because papers and OBDA roadmaps depend on them.

### Layer 1 — Meta-ontology (syntax, semantics, documentation)

Foundational vocabularies used to **express** ontologies and to annotate terms. They do not describe buildings themselves.

| Vocabulary | Role in this project |
|----------|----------------------|
| **RDF** | Graph data model; every triple in TTL/OBDA targets is RDF-shaped. |
| **RDFS** | `rdfs:Class`, `rdfs:subClassOf`, `rdfs:domain` / `range`, labels — used in stubs and in `alignment.ttl`. |
| **OWL** | `owl:Class`, `owl:ObjectProperty`, `owl:equivalentClass` — alignment and full `BOT.ttl` / `SOSA.ttl`. |
| **SKOS** | Definitions and examples on terms (e.g. `skos:definition` in `SOSA.ttl`). |
| **schema.org** | Lightweight datatype annotations on VKG individuals (`schema:name`, `schema:height`, dates) in `.obda` mappings. |
| **Dublin Core (`dcterms`)** | Ontology metadata (title, creator, license) in `BOT.ttl` and `SOSA.ttl`. |

**In `ontop/` today:** meta terms appear inside `BOT.ttl`, `SOSA.ttl`, and the Protégé ontology `citygml-bot-sosa-ssn-geosparql-time.rdf` (imports only). OBDA uses `schema:` and `rdfs:` prefixes directly on mapped individuals.

### Layer 2 — Upper ontology (domain-independent reality)

Abstract categories (object, process, quality, space, time) that **domain ontologies specialize**. None are fully vendored under `ontop/` yet; they guide future alignment and paper comparisons.

| Ontology | Purpose |
|----------|---------|
| **BFO** (Basic Formal Ontology) | Continuants vs occurrents; useful when linking **building parts** (continuants) to **observations / simulations** (occurrents). |
| **SUMO** (Suggested Upper Merged Ontology) | Broad upper-level classes and relations; optional bridge for cross-domain reasoning. |
| **DOLCE** | Descriptive upper ontology for linguistic/cognitive engineering; alternative to BFO for space/time/part-whole. |

**In `ontop/` today:** no BFO/SUMO/DOLCE files. Cross-domain glue is done pragmatically in `alignment.ttl` (BOT ↔ GeoSPARQL ↔ SOSA) instead of via an explicit upper import.

### Layer 3 — Smart city / building (domain layer)

Vocabularies that describe **built environment, city models, sensors, and time**. This is what Ontop maps CityDB tables to.

| Ontology | Role | In `ontop/` |
|----------|------|-------------|
| **GeoSPARQL** | `geo:Feature`, `geo:Geometry`, `geo:hasGeometry`, `geo:asWKT` for footprints and envelopes | `geosparql-stub.ttl` + SQL `ST_AsText` in `.obda` |
| **OWL-Time** | `time:Instant`, `time:Interval`, `time:hasBeginning` / `hasEnd` for time series periods | `time-stub.ttl` |
| **BOT** | Building topology: `bot:Building`, `bot:Space`, `bot:Zone`, `bot:containsZone` | `bot-stub.ttl` (minimal), `BOT.ttl` (full 0.3.2) |
| **SOSA / SSN** | Observations, features of interest, sensors, platforms | `sosa-stub.ttl`, `ssn-stub.ttl`, `SOSA.ttl` (full) |
| **CityGML** | Urban objects (`citygml:Building`, `citygml:Room`, …) | `citygml2.owl` (2.0 OWL), alignment to `bot:` |
| **Brick** | HVAC / equipment semantics (valves, AHUs, points) | **Not in repo** — used in Wu et al. BEM framework |
| **SERAF** | Semantic sensor / actuator framework for buildings | **Not in repo** — candidate for device mappings |
| **CIM extension** | Project energy vocabulary `cim:` (`http://data.cimwizard.org/energy/`) | Declared in `.obda` only |

**Alignment file** (`alignment.ttl`) ties domain modules:

- `citygml:Building` ≡ `bot:Building`
- `citygml:Room` ≡ `bot:Space`
- `citygml:CityObject` ⊑ `bot:Zone`
- `bot:Zone`, `bot:Element` ⊑ `geo:Feature`
- `bot:Space`, `bot:Element` ⊑ `sosa:FeatureOfInterest`

**Protégé shell ontology** `citygml-bot-sosa-ssn-geosparql-time.rdf` imports alignment + stubs (catalog in `catalog-v001.xml`).

```mermaid
flowchart TB
  subgraph L1["Layer 1 — Meta"]
    RDF[RDF / RDFS / OWL]
    SKOS[SKOS / DC / schema.org]
  end
  subgraph L2["Layer 2 — Upper (planned)"]
    BFO[BFO]
    SUMO[SUMO]
    DOLCE[DOLCE]
  end
  subgraph L3["Layer 3 — Domain (ontop/)"]
    CG[CityGML]
    BOT[BOT]
    GEO[GeoSPARQL]
    SOSA[SOSA / SSN]
    TIME[OWL-Time]
    CIM[cim: energy extension]
  end
  DB[(CityDB PostgreSQL)]
  OBDA[Ontop .obda / .r2rml]
  L1 --> L3
  L2 -.-> L3
  L3 --> OBDA
  DB --> OBDA
  OBDA --> SPARQL[SPARQL over VKG]
```

---

## `semantic/ontop/` inventory (aligned with TTL / OWL / OBDA)

| File | Type | Purpose |
|------|------|---------|
| `alignment.ttl` | OWL alignment | Equivalences / subsumptions between CityGML, BOT, GeoSPARQL, SOSA |
| `bot-stub.ttl` | Minimal BOT | Fast Ontop/Protégé reasoning without full BOT dependency chain |
| `geosparql-stub.ttl` | Minimal GeoSPARQL | Feature / geometry / WKT literal for spatial mappings |
| `time-stub.ttl` | Minimal OWL-Time | Instants and intervals for `ng2_time_series` |
| `sosa-stub.ttl` | Minimal SOSA | Observation / FOI / sensor for energy KPIs |
| `ssn-stub.ttl` | Minimal SSN | `ssn:System`, deployment hooks for devices |
| `BOT.ttl` | Full vocabulary | W3C LBD BOT 0.3.2 (metadata + full class/property set) |
| `SOSA.ttl` | Full vocabulary | W3C/OGC SOSA with SKOS definitions |
| `citygml2.owl` | Domain OWL | CityGML 2.0 OWL (Unige); large schema for city objects |
| `citygml-bot-sosa-ssn-geosparql-time.rdf` | Ontology document | Import hub for Protégé + Ontop |
| `cim_citydb.obda` | **Primary OBDA** | 63 mappings: CityDB → BOT / CityGML / GeoSPARQL / SOSA / Time / `cim:` |
| `cim_citydb.r2rml` | R2RML variant | Parallel mapping syntax to same VKG |
| `citygml-bot-sosa-ssn-geosparql-time.obda` | Slim OBDA | Subset / alternate join paths (e.g. `cityobject` vs `feature`) |
| `cim_citydb.properties` / `citygml-bot-sosa-ssn-geosparql-time.properties` | Ontop JDBC | DB connection for virtualisation |
| `catalog-v001.xml` | XML catalog | Resolves ontology IRIs to local stub/full files |
| `test-queries.sparql` | Validation | SPARQL over VKG (buildings, zones, observations, GeoSPARQL) |
| `../17_RML_Meets_LLMs_More_Structu.pdf` | Reference | RML-FNML + LLM-in-mapping for semi-structured fields |
| `../BLINKG.pdf` | Reference | LLM mapping-generation benchmark (task-level P/R/F1) |

**Mapping groups in `cim_citydb.obda`:** buildings & geometry; energy building attributes; thermal / usage zones (`bot:Zone`); building units (`bot:Space`); qualified attributes & resources as `sosa:Observation`; time series as `sosa:ObservationCollection` + `time:`; devices / solar / weather / EPC / simulation runs as observations.

---

## Related papers — three ontology-driven solutions (separate summaries)

### 1. Wu, Cheng & Wang — *Energy & Buildings* 296 (2023)  
`phd_proposal/1-s2.0-S0378778823004978-main.pdf` — DOI [10.1016/j.enbuild.2023.113267](https://doi.org/10.1016/j.enbuild.2023.113267)

**Problem:** BEM (Building Energy Modeling) needs weather, BIM geometry, internal gains, and HVAC schedules from **heterogeneous sources**; manual IDF/EnergyPlus preparation is slow; **thermal zoning** is mutable and poorly supported by static BIM exports.

**Solution (3-step framework):**

1. **Ontology model** — Four domains: weather, building, internal heat gain, HVAC. Reuses **Brick** (equipment) and **BOT** (topology); extends with weather classes (TMY / historical / forecast) storing **pointers** to EPW files (dynamic data stay at source URLs/paths).
2. **Thermal zoning** — **Cross-domain SWRL/rule reasoning** on the ontology (e.g. core vs perimeter, aggregation rules aligned with guidelines) to create thermal zone individuals and links, instead of one-space-one-zone shortcuts.
3. **Model translation** — **Instance-based mapping** from ontology individuals to EnergyPlus IDF with **dynamic data conversion** (schedules, setpoints from BMS).

**Case:** One campus building floor; reported **>99%** modeling time reduction vs manual workflow.

**Relevance to CIM Wizard:** Same problem class (BIM + sensors + simulation inputs). Your OBDA stack already maps partitions to zones and KPIs to `sosa:Observation`; Wu’s work suggests adding **Brick** + explicit **thermal-zone reasoning** before IDF export.

---

### 2. Shi et al. — *Advanced Engineering Informatics* 57 (2023)  
`phd_proposal/1-s2.0-S1474034623002422-main.pdf` — DOI [10.1016/j.aei.2023.102114](https://doi.org/10.1016/j.aei.2023.102114)

**Problem:** Digital twin cities need a **unified semantic layer** for BIM + GIS + IoT; conversion-only approaches (IFC ↔ CityGML) leave formats independent and IoT as visualization-only.

**Solution — OntoCIM (five steps):**

1. **Geometry processing** — Harmonize BIM/GIS geometries (often LoD3 CityGML from IFC).
2. **Data instantiation** — Populate RDF individuals (e.g. from **ifcOWL** via SPARQL extraction queries in the paper).
3. **Ontology construction** — General **CIM ontology** (`Feature`–`Facility`–`Element` hierarchy, links to spatial and sensor concepts).
4. **Ontology mapping** — Rules from CIM to **application ontologies** (housing queries, fire evacuation) without changing source DBs.
5. **Querying application** — SPARQL-driven analytics and twin UIs.

**Case studies:** Favorite-housing price/area queries; indoor–outdoor evacuation twin extending CIM → application ontology.

**Relevance to CIM Wizard:** Closest to your **CityDB + CityGML + OBDA** path: keep PostgreSQL authoritative, expose **linked data via Ontop**, use `alignment.ttl` like OntoCIM’s upper linking pattern. Shi’s ifcOWL SPARQL patterns complement (not replace) SQL-based `.obda`.

---

### 3. Ma et al. — *Sustainable Cities and Society* 106 (2024)  
`phd_proposal/1-s2.0-S2210670724002221-main.pdf` — DOI [10.1016/j.scs.2024.105394](https://doi.org/10.1016/j.scs.2024.105394)

**Problem:** **Urban BEM (UBEM)** lacks a cross-domain integration model; city-scale EnergyPlus workflows are heavy and siloed (CityGML, GeoJSON, gbXML).

**Solution — Two ontologies + lightweight simulation route:**

1. **Building Template Ontology (BTO)** — Templates for EnergyPlus/OpenStudio inputs (materials, zone settings, schedules) as RDF individuals (`bto:`), extensible per building type (e.g. office).
2. **Urban Building Ontology (UBO)** — Building **instances** with **GeoSPARQL** geometry and links to templates (`rdf:type` → `bto:Office`, etc.).
3. **Pipeline** — SPARQL via **RDFLib** (Python) → generate simulation files → batch EnergyPlus → city-scale retrofit scenarios.

**Case:** 5,000+ buildings in three US cities; envelope / lighting / HVAC retrofits quantified (roughly 0.1–10% savings bands depending on measure and city).

**Relevance to CIM Wizard:** `cim:` properties and `sosa:Observation` mappings mirror UBO’s “instance + measurement” split; BTO-like **template graphs** could live beside CityDB for repeatable UBEM exports.

---

## Automating OBDA / VKG creation — LLM4VKG

`phd_proposal/llm4vkg.pdf` — Xiao et al., **IJCAI 2025** ([proceedings](https://www.ijcai.org/proceedings/2025/0525.pdf), [code](https://github.com/HomuraT/LLM4VKG))

**Problem:** VKG construction = ontology + relational schema + mappings; manual alignment fails on naming ambiguity and incomplete ontologies; rule bootstrappers (BootOX, IncMap, Ontop direct mapping) score poorly on hard **RODI** scenarios.

**LLM4VKG pipeline (two phases):**

```mermaid
flowchart LR
  DB[(DB schema Σ)]
  T0[(Seed ontology T0)]
  MP[1. Mapping pattern recognition]
  OC[2. Ontology completion and mapping bootstrap]
  P[(VKG spec T,M,Σ)]
  DB --> MP
  MP --> OC
  T0 --> OC
  OC --> P
```

1. **Mapping pattern recognition** — Convert schema to a DB graph `G_Σ`; run SPARQL to detect Calvanese et al. patterns:
   - **SE** — table ↔ class (entity + PK + attributes)
   - **SR** — FK join ↔ object property
   - **SRm** — merged relationship tables
   - **SH** — hierarchy between tables/classes
2. **Ontology completion & mapping bootstrapping** — For each pattern instance, LLM modules:
   - **Retriever** — sentence similarity → top‑n ontology candidates
   - **Matcher** — generative match (High/Medium/Low) for table/column ↔ class/property
   - **Namer** — mint missing class/property names consistent with ontology context  
   Then emit Ontop-style `(source SQL, target RDF template)` mappings.

**Results:** Average **+17% F1** vs BootOX on RODI; up to **+39%** on renamed schemas; still **~0.46 F1** with 25% ontology vocabulary removed — tolerates incomplete TBox.

**How this applies to CIM Wizard automatic `.obda`:**

| Step | Action for CityDB |
|------|-------------------|
| Input | PostgreSQL `information_schema` + sample stats; seed TBox = `alignment.ttl` + stubs + `cim:` |
| Pattern detection | Auto-detect FK graphs (`building` → `feature`, `ng2_*` → partitions, time series) as SE/SR instances |
| LLM alignment | Match column names (`measured_height`, `int_heat_gains`) to `schema:height`, `cim:internalHeatGains`, `sosa:hasSimpleResult` |
| Generate | Draft `.obda` mapping blocks; human or CI validates with `test-queries.sparql` + GeoSPARQL spot checks |
| Evolution | On BOT/SOSA/CityGML release: diff ontology IRIs/axioms → re-run alignment on **changed** mappings only (research gap vs one-shot LLM4VKG) |

**Caveats for spatial OBDA:** LLM4VKG targets relational **schema.org**-style benchmarks; **GeoSPARQL SQL expressions** (`ST_AsText`, CRS prefixes) still need template rules or a fine-tuned spatial-SQL model (your proposed novelty). Combine LLM4VKG alignment with **Bereta & Koubarakis (Ontop spatial, ISWC 2016)** patterns for geometry literals.

**Complementary papers (2025–2026):** LLM4VKG automates *mapping authoring*; **RML Meets LLMs** embeds LLMs *inside* mappings for semi-structured fields; **BLINKG** benchmarks *mapping-task* accuracy — see sections below. Use all three together in the O5 pipeline.

---

## RML meets LLMs — hybrid structured + unstructured mappings

`semantic/17_RML_Meets_LLMs_More_Structu.pdf` — *RML Meets LLMs: More Structure, Fewer Errors* (medicines-information use-case; RML-FNML + Ontop-style notation)

**Problem:** Real UBEM/CityDB data is **semi-structured**: many columns are typed and joinable (height, storeys, `objectclass_id`), but others are **free text** (OSM tag strings, EPC narrative fields, census descriptions, method documentation in calculator configs). Pure RML/OBDA cannot parse these; pure LLM JSON→RDF sacrifices correctness guarantees and hallucinates (≈40% error rate on small pharma JSON in the paper vs ≈2.5% for hybrid).

**Core idea:** Integrate LLM calls **inside** RML mapping rules via **RML-FNML** user-defined functions (`getAnswerFromLLM`, `getFloatFromLLM`, …). Structured attributes use standard triple maps; unstructured attributes call the LLM on **short, focused snippets** computed by the mapping `source` clause.

```mermaid
flowchart LR
  subgraph structured["Structured path — correctness guaranteed"]
    COL[citydb.building.measured_height]
    RML[Standard RML / OBDA triple map]
    RDF1[schema:height literal]
    COL --> RML --> RDF1
  end
  subgraph unstructured["Unstructured path — LLM in mapping"]
    TXT[OSM tag / EPC text field]
    FNML[RML-FNML getAnswerFromLLM]
    RDF2[Parsed datatype property]
    TXT --> FNML --> RDF2
  end
  subgraph audit["Auditability"]
    DESC[Store original text in cim:description / prov]
    FNML -.-> DESC
  end
```

**Formal pattern (from paper):** For property `P` extracted from unstructured attribute `U`:

```text
target  :entity/{id} :hasP getAnswerFromLLM(concat(PROMPT_P, {U})) .
source  SELECT id, U FROM ...
```

- `PROMPT_P` — zero-shot or few-shot template per property (dosage amount, safety level, building use from OSM `building=*` tag, …).
- `functions.ttl` — declares Java/Python UDF implementing LLM call + typed extraction (JSON `{"answer": ...}`).
- **Provenance:** store raw `U` in a `description` / `xxxDesc` property alongside LLM-extracted value (paper’s MI ontology pattern) — aligns with Paper 2 O6 lineage.

**Evaluation (paper):** 20 JSON drugs, 1,384 triples, 550 LLM-extracted; DeepSeek-32B: **34 errors (2.5%)** vs Claude Sonnet end-to-end **561 errors (40%)**. SPARQL query answers: hybrid beats NL-over-JSON and NL-over-LLM on dosage queries.

**Relevance to CIM Wizard / CityDB:**

| CIM data | Structured (standard OBDA) | Semi-structured (RML-FNML + LLM) |
|----------|---------------------------|----------------------------------|
| `citydb.building.measured_height` | `schema:height` | — |
| `citydb.building.objectclass_id` + lookup | `a bot:Building` | — |
| `ng2_*` thermal zone labels | datatype props | — |
| OSM `building:use` free tags | — | infer `cim:buildingType` / TABULA archetype |
| EPC / certificate narrative fields | — | extract U-value proxy, heating system hints |
| Calculator `method` metadata strings | — | classify method tier for confidence (O6) |
| Unparsed census text attributes | — | map to `cim:censusAttribute` with LLM + store raw |

**Relation to LLM4VKG:** LLM4VKG **generates** mapping assertions; RML-Meets-LLMs **executes** LLM inside an existing mapping at materialisation time. CIM Wizard 2.0 needs **both**: LLM4VKG + fine-tuned SQL for `.obda` bootstrap, RML-FNML for columns that stay textual in the warehouse.

**Implementation note:** Ontop supports OBDA (SQL source); full RML-FNML UDFs may require **RMLMapper** or a post-processing step for JSON/API sources. For PostgreSQL CityDB, prototype LLM-in-mapping on `assist_cim` agent repair loop first, then migrate hot paths to FNML when RML stack is wired.

---

## BLINKG — benchmark for LLM mapping generation

`semantic/BLINKG.pdf` — Castedo et al., *BLINKG: A Benchmark for LLM-Integrated Knowledge Graph Generation* (TGDK 2026; [GitHub](https://github.com/citiususc/blinkg), DOI 10.4230/TGDK..?.?)

**Problem:** LLM mapping papers (Hofer RML+LLM, Schmidt YARRRML, R2RML-ChatGPT, ReMap, LLM4VKG) use **inconsistent tasks, metrics, and datasets** — hard to compare or tune CIM-specific automation.

**BLINKG contribution:** Domain-agnostic benchmark with **gold standards**, **three difficulty scenarios**, and **task-level** precision / recall / F1 (not only end-to-end SPARQL like RODI).

### Comparison with other benchmarks

| | RODI | SemTab | BLINKG |
|---|------|--------|--------|
| Focus | RDB → ontology (indirect via SPARQL) | Cell/entity/property annotation vs **existing KG** | Data → ontology **mapping decisions** |
| Granularity | Graph-level | Annotation-level | **Task-level** (class, property, join, …) |
| Requires populated KG | No | **Yes** (Wikidata) | No |
| Input formats | RDB | Tabular | **CSV, JSON, XML, SQL, …** |
| Expected output | R2RML file | Links | **Structured mapping table** (Table 6) |

**Implication for CIM Wizard:** Use BLINKG-style **tabular mapping output** from O5 agents before serialising to `.obda`; use RODI/SPARQL (`test-queries.sparql`) as **downstream** integration test, not the only metric.

### Three scenarios (difficulty ladder)

| Scenario | Alignment | CIM Wizard analogue |
|----------|-----------|-------------------|
| **1 — Basic** | Lexically similar column ↔ ontology term | `building_id` → `bot:Building`; 8 atomic cases (1A–1H): single column, self-join, multi-file join, language tags |
| **2 — Schema-aligned** | Input mirrors ontology (GTFS-Madrid) | Hypothetical: ontology built from CityGML ADE spec; `ng2_*` tables with obvious class names |
| **3 — Schema-distant** | Lexically/structurally far (ePO / CODICE XML) | **`citydb` + `objectclass_id` + `ng2_*` energy ADE** — closest to production CityDB OBDA |

CityDB OBDA (`cim_citydb.obda`) is predominantly **Scenario 3**: `objectclass_id = 26`, multi-hop joins (`building` → `feature` → `geometry_data`), PostGIS in source SQL, `cim:` extension properties.

### BLINKG mapping tasks → O5 agent decomposition

| BLINKG task | CIM Wizard O5 agent / tool | Example in `cim_citydb.obda` |
|------------|------------------------------|------------------------------|
| **Ontology class identification** | Schema + alignment agent | `citydb.building` → `bot:Building` |
| **Subject generation** (simple / composite PK) | Template engine | `:building/{id}` |
| **Ontology property identification** | LLM4VKG Matcher + `alignment.ttl` | `measured_height` → `schema:height` |
| **Data reference identification** | **Fine-tuned Q2SQL** (`txt2ssql`) | `SELECT id, measured_height FROM citydb.building WHERE …` |
| **Related entity class + joins** | Pattern detector (SR/SRm) + SQL agent | `MAP_Building_HasGeometry` FK path |
| **Datatype annotation** | Template rules | `^^xsd:double`, `geo:wktLiteral` |
| **Language annotation** | Low priority (mostly numeric UBEM) | `rdfs:label@en` for building names |
| **Transformation functions** | PostGIS + RML-FNML | `ST_AsText(geom)`, CRS prefix; future LLM parse |

### BLINKG experimental findings (relevant to design)

- **Strong:** entity class ID, ontology property ID (when lexical overlap exists), data reference (Scenario 1–2).
- **Weak:** **join conditions** (similarity 0.37–0.69 even in Scenario 1); **function name/output** (<0.20 F1 in Scenario 2); **schema-distant** Scenario 3 rarely exceeds 0.53 similarity.
- **Prompting:** few-shot helps local tasks; **does not fix joins/functions** (DeepSeek F1 = 0 on joins/functions in Scenario 3).
- **Evaluation:** similarity threshold **0.8** (max of Levenshtein, SBERT raw, SBERT verbalized) best matches expert labels; post-processing essential.
- **Recommendation:** **Hybrid + human-in-the-loop** — LLMs draft mappings; experts validate; symbolic constraints (OWL, SHACL) catch hallucinations.

### Proposed CIM BLINKG-style evaluation (extend `assist_cim` + `semantic/`)

1. Extract **gold mapping table** from `cim_citydb.obda` (63 mappings) — columns per Table 6: data ref, property, class, subject template, join, datatype.
2. Hold out N mappings; agents predict tabular rows; score per-task F1 (BLINKG macro-average over 3 runs).
3. Serialise accepted rows to `.obda`; run Ontop + `test-queries.sparql` (RODI-style downstream).
4. Optionally add **Scenario 1-style synthetic** `citydb` slices in `ai4db` for regression (lexically easy) before full CityDB (Scenario 3).
5. Publish subset alongside `paper2/ubem_benchmark/` or `semantic/blinkg_cim/` for reproducibility.

```mermaid
flowchart TB
  GOLD[Gold table from cim_citydb.obda]
  AGENTS[O5 agents → BLINKG tabular output]
  SCORE[Per-task P/R/F1 + similarity ≥ 0.8]
  HITL[Human approve diff]
  OBDA[Merge .obda]
  ONTOP[Ontop + test-queries.sparql]
  GOLD --> AGENTS --> SCORE --> HITL --> OBDA --> ONTOP
```

---

## Fine-tuned Text-to-SQL → OBDA pipeline (project repos)

Goal: use a **CIM Wizard fine-tuned spatial-SQL LLM** (not a generic model) to generate and maintain Ontop `.obda` mappings, producing a **Virtual Knowledge Graph** over `cim_wizard_integrated` without materialising RDF.

Three cloned repositories form a closed loop: **synthetic data → fine-tuning → evaluation → (planned) OBDA synthesis**.

```mermaid
flowchart LR
  subgraph ai4db["ai4db/ — dataset factory"]
    S1[stage1_cim_v2.py\nrule-based Q↔SQL]
    S3[stage3_v2.py\nLLM augmentation]
    MERGE[merge_datasets.py\ncurator.py]
    BENCH[benchmark_generator_v2.py]
    S1 --> S3 --> MERGE --> BENCH
  end
  subgraph txt2ssql["txt2ssql/ — fine-tuning"]
    CURATE[curate_cim_dataset_ftv2]
  FT[ftv2/*.py\nQ2SQL / Q2Inst / QInst2SQL]
    HF[(HuggingFace\nmodels + dataset)]
    CURATE --> FT --> HF
  end
  subgraph assist["assist_cim/ — runtime + eval"]
    EVAL[evaluator_v2.py\nEM / EX / SC / EA]
    AGENT[agent_cim_assist.py\nLangGraph SQL agent]
  end
  subgraph semantic["semantic/ontop/ — VKG"]
    OBDA[cim_citydb.obda\n*.obda mappings]
    ONTOP[Ontop + Protégé\nSPARQL over DB]
    OBDA --> ONTOP
  end
  MERGE --> CURATE
  HF --> EVAL
  HF --> AGENT
  EVAL --> OBDA
  AGENT --> OBDA
```

### `ai4db/` — CIM spatial-SQL benchmark & training data

| Script | Role |
|--------|------|
| `stage1_cim_v2.py` | Rule-based generator: question + PostGIS SQL pairs over **cim_vector**, **cim_census**, **cim_network**, **cim_raster** with **task taxonomy** (18 types: `SPATIAL_PREDICATE`, `RASTER_VECTOR`, …) and **domain taxonomy** (single/multi-schema) |
| `stage3_v2.py` | LLM augmentation via OpenRouter (paraphrase, sql_rewrite, question_to_sql, …) — scales diversity beyond templates |
| `merge_datasets.py` | Merges Stage 1 + Stage 3 positives with `negative_samples.jsonl` (ambiguous / out-of-scope) |
| `curator.py` | Taxonomy-aware train/val/test splits for Q→SQL fine-tuning |
| `benchmark_generator_v2.py` | Stratified evaluation benchmark with ground-truth execution |
| `generate_negative_samples.py` | Hard negatives for robustness |
| `schema_agnostic/` | Cross-schema spatial benchmark generator (generalisation experiments) |

**Current schema coverage:** `cim_vector.*`, `cim_census.censusgeo`, `cim_network.*`, `cim_raster.*`.

**Gap for OBDA:** no `citydb.*` / `ng2_*` templates yet — these are what `semantic/ontop/*.obda` maps. Extend `stage1_cim_v2.py` with a **CityDB + Energy ADE** schema block mirroring `cim_citydb.obda` sources.

### `txt2ssql/` — fine-tuning on CIM dataset

| Path | Role |
|------|------|
| `ftv2/qwen25_14b_q2sql.py` | Single-stage **Question → PostGIS SQL** (recommended baseline) |
| `ftv2/qwen25_14b_q2inst.py` + `qinst2sql.py` | Two-stage **Question → Instruction → SQL** (better on complex spatial joins) |
| `ftv2/qwen25_32b_unsloth_*.py` | 32B Unsloth variant (higher EX, fits 24 GB with 4-bit) |
| `ftv2/llama31_14b_*.py`, `sqlcoder_7b_*.py` | Alternative backbones |
| `hugging_face_dataset_repo.txt` | Dataset published as `taherdoust/txt2ssql_20july2025` |

Training targets CIM-specific prompts (full `schema.table` notation, PostGIS functions). Reported targets: **85–92% execution accuracy (EX)** on benchmark after fine-tuning; **90–96% eventual accuracy (EA)** with agentic self-correction.

### `assist_cim/` — evaluation & interactive agent

| Script | Role |
|--------|------|
| `evaluator_v2.py` | Unified evaluator: **EM**, **EX**, **Deep EM**, **SC**, **EA** with taxonomy breakdown (task type, domain, complexity, frequency); supports HF LoRA adapters and OpenRouter baselines |
| `evaluate_models.py` | Batch model comparison driver |
| `agent_cim_assist.py` | LangGraph ReAct agent: Ollama LLM + `SQLDatabaseToolkit` over `cim_wizard_integrated`; PostGIS-aware system prompt; iterative SQL repair |
| `CIM_DATABASE_SCHEMA.txt` | Human-readable schema card for agents / prompts |

**Role in OBDA loop:** validates that generated **source SQL** in mappings is executable and semantically correct before writing `.obda` blocks.

---

## From fine-tuned Text-to-SQL to `.obda` (proposed VKG automation)

An Ontop mapping is a pair `(source SQL, target RDF template)`. Your fine-tuned model is strongest at the **source** side; the **target** side needs ontology-aware templates.

### OBDA mapping anatomy (from `cim_citydb.obda`)

```text
mappingId   MAP_Building_Height
target      :building/{id} schema:height {measured_height}^^xsd:double .
source      SELECT id, measured_height FROM citydb.building
              WHERE objectclass_id = 26 AND measured_height IS NOT NULL
```

| OBDA part | Who generates it |
|-----------|-------------------|
| `source` SQL | **Fine-tuned CIM spatial-SQL LLM** (+ schema context from `citydb` / `ng2_*`) |
| `target` RDF template | **Rule library** from ontology alignment (`alignment.ttl`, BOT/SOSA/GeoSPARQL prefixes) + LLM4VKG-style column↔property matching |
| `mappingId` | Deterministic naming from table + property + ontology term |
| Validation | `assist_cim/evaluator_v2.py` (execute SQL) + Ontop + `test-queries.sparql` |

### Proposed 6-step OBDA synthesis pipeline (LLM4VKG + BLINKG + RML-FNML)

1. **Schema introspection** — `information_schema` + FK graph for `citydb`, `ng2_*`, `cim_vector`; seed ontology = `alignment.ttl` + stubs.
2. **BLINKG task planning** — Decompose each new table/column into BLINKG tasks (class, subject, property, data ref, join, datatype, transform); classify Scenario 1/2/3 difficulty.
3. **Mapping pattern + alignment** — LLM4VKG SE/SR/SRm/SH detection; Retriever/Matcher/Namer on seed TBox.
4. **Source SQL generation** — Fine-tuned CIM Q2SQL (`txt2ssql`) for **data reference + joins** (BLINKG’s hardest task — do not rely on generic LLM alone).
5. **Target template assembly** — Rule library: BOT / CityGML / SOSA / GeoSPARQL / `cim:`; **RML-FNML** UDFs for semi-structured columns (OSM tags, EPC text).
6. **Validate & merge** — BLINKG tabular scoring (per-task F1) → SQL EX (`evaluator_v2.py`) → Ontop → `test-queries.sparql` → human approves diff → commit `.obda`.

```mermaid
flowchart TB
  INTENT[BLINKG task plan\n(class, property, join, datatype)]
  PAT[LLM4VKG patterns\nSE / SR / SRm / SH]
  LLM[Fine-tuned CIM Q2SQL\n(txt2ssql) — joins + data ref]
  TPL[Target template engine\n(alignment.ttl rules)]
  FNML[RML-FNML LLM UDFs\n(semi-structured fields)]
  BLINKG[BLINKG tabular scorer\nper-task F1]
  VAL[assist_cim EX\n+ Ontop + SPARQL]
  OBDA_OUT[cim_citydb.obda]
  INTENT --> PAT
  PAT --> LLM
  PAT --> TPL
  TPL --> FNML
  LLM --> BLINKG
  TPL --> BLINKG
  FNML --> BLINKG
  BLINKG --> VAL
  VAL --> OBDA_OUT
```

### New training tasks to add (beyond ad-hoc SQL)

Extend `ai4db` with an **OBDA-aware** sample type so the fine-tuned model learns mapping-shaped SQL, not only analytics queries:

| Sample type | Input | Output |
|-------------|-------|--------|
| `OBDA_SOURCE` | Schema + mapping intent + target variable names | `SELECT id, col AS alias …` matching OBDA placeholder columns |
| `OBDA_SPATIAL` | Geometry column + CRS | `'<http://www.opengis.net/def/crs/EPSG/0/4326> ' \|\| ST_AsText(geom) AS wkt` |
| `OBDA_JOIN` | FK path (building → feature → geometry_data) | Multi-table SELECT for object properties |

Pair with **inverse** samples: given existing `source` from `cim_citydb.obda`, predict which ontology properties the `target` asserts (classification task for a smaller model or LLM4VKG Matcher).

### How this complements LLM4VKG, RML-Meets-LLMs, and BLINKG

| Component | LLM4VKG (IJCAI 2025) | RML Meets LLMs (2025) | BLINKG (TGDK 2026) | This project |
|-----------|----------------------|------------------------|-------------------|--------------|
| Role | Bootstrap mappings + ontology completion | LLM **inside** mappings for text fields | **Benchmark** mapping tasks | Integrate all three on CityDB |
| Schema ↔ ontology alignment | Generic LLM Retriever/Matcher/Namer | N/A (assumes mappings exist) | Task-level gold + metrics | CIM fine-tune + `alignment.ttl` |
| Source SQL | Not specialised for PostGIS | SQL/JSONPath in logical source | Data reference + join tasks | **Fine-tuned on CIM spatial SQL** |
| Target templates | Mapping patterns (SE/SR/…) | FNML + standard triple maps | Expected output table | BOT / CityGML / SOSA / GeoSPARQL / `cim:` |
| Semi-structured text | Limited | **Core contribution** | Transformation + function tasks | OSM/EPC/census text via FNML |
| Evaluation | RODI F1 | KG + SPARQL correctness | **Per-task P/R/F1** + similarity | BLINKG table + `evaluator_v2.py` + `test-queries.sparql` |
| Lifecycle | One-shot bootstrap | Runtime materialisation | Reusable benchmark | Incremental `.obda` diff on schema/ontology change |

---

## Research gap and novelty (updated)

| Prior work | Gap for this project |
|------------|----------------------|
| **Lembo et al., IJCAI 2017** | Formal OBDA **repair** under spec evolution — not LLM-generated mappings |
| **LLM4VKG, IJCAI 2025** | Strong **initial** VKG bootstrap — no Ontop `.obda` **lifecycle** on ontology version diffs |
| **RML Meets LLMs (2025)** | LLM-in-mapping for semi-structured fields — not applied to **CityDB / PostGIS / UBEM** |
| **BLINKG (TGDK 2026)** | Mapping-task benchmark — no **CIM / CityDB / GeoSPARQL** scenario published yet |
| **Hofer et al., ESWC 2024 workshop** | LLM RML case studies — not continuous sync with **GeoSPARQL / PostGIS** constraints |
| **Wu / Shi / Ma** | Ontology-centric **pipelines** — not automatic OBDA from **CityDB** with energy extensions |
| **Generic Text-to-SQL** (Spider, BIRD) | No **OBDA target templates**, no **CityDB/PostGIS** domain, no VKG validation loop |
| **This project (`ai4db` + `txt2ssql` + `assist_cim`)** | CIM spatial-SQL fine-tuning exists — **not yet wired** to `.obda` synthesis, BLINKG eval, or RML-FNML |

**Claimable contribution:** A **hybrid VKG automation stack** — LLM4VKG alignment + **BLINKG-task** agents + fine-tuned PostGIS SQL for sources + ontology templates + **RML-FNML** for semi-structured UBEM fields — with **per-task mapping metrics** and Ontop/GeoSPARQL integration tests on `cim_citydb.obda`.

---

## Manual geospatial OBDA (baseline references)

- **Bereta & Koubarakis, "Ontop of Geospatial Databases" (ISWC 2016)** — GeoSPARQL-to-SQL, geometry columns in mappings.
- **Kyzirakos et al., GeoTriples (*Web Semantics*, 2018)** — Practical geospatial R2RML/RML with user revision loops.

Manual OBDA workflow (current `cim_citydb.obda`):

1. Inspect each relevant table (and `objectclass` filters).
2. Map row keys to individual IRIs (`:building/{id}`, …).
3. Map columns to datatype / object properties (and `a` classes).
4. For geometries, map via `geo:asWKT` with SQL expressions producing `geo:wktLiteral`.

---

## Related automation papers (broader)

- **Xiao et al., LLM4VKG (IJCAI 2025)** — see above; primary reference for mapping bootstrap.
- **RML Meets LLMs (2025)** — `semantic/17_RML_Meets_LLMs_More_Structu.pdf`; RML-FNML + LLM for semi-structured fields; complements LLM4VKG (cited as only other LLM-in-OBDA work besides mapping generation).
- **Castedo et al., BLINKG (TGDK 2026)** — `semantic/BLINKG.pdf`; [github.com/citiususc/blinkg](https://github.com/citiususc/blinkg); task-level mapping benchmark; supersedes RODI-only eval for O5 development.
- **Hofer et al.** — LLM-generated RML from JSON (IMDB); evaluated with mapping accuracy; BLINKG cites as fragmented eval baseline.
- **Schmidt et al.** — YARRRML + LLM in manufacturing; schema evolution focus.
- **Freund et al., ReMap** — reverse-engineer RML from expected RDF; LLM mappings as baseline.
- **"From SQL to Knowledge Graphs: An LLM-Driven MultiAgent Approach…" (OpenReview)** — Multi-agent ETL / analyzer / graph agents with iterative quality checks: [OpenReview](https://openreview.net/forum?id=HYu0dGmj5x).

## Can a fine-tuned SQL / spatial-SQL LLM maintain `.obda`?

**Yes** — the project already has the training and evaluation stack; the missing piece is the **OBDA synthesis bridge**.

| Layer | Repo | Status |
|-------|------|--------|
| Training data (88K+ samples) | `ai4db/` | Done for `cim_vector` / census / network / raster |
| Fine-tuned models | `txt2ssql/ftv2/` | Qwen 14B/32B, Llama 14B; HF dataset `taherdoust/txt2ssql_20july2025` |
| Evaluation & agent | `assist_cim/` | `evaluator_v2.py` (EX/EA), `agent_cim_assist.py` |
| OBDA mappings | `semantic/ontop/` | Manual `cim_citydb.obda` (63 mappings) — **target for automation** |
| CityDB schema in training | `ai4db/` | **TODO** — extend `stage1_cim_v2.py` for `citydb.*`, `ng2_*` |
| OBDA generator script | — | **TODO** — BLINKG-task agents → tabular output → `.obda` |
| BLINKG gold extract | — | **TODO** — parse `cim_citydb.obda` → mapping table for eval |
| RML-FNML prototypes | — | **TODO** — semi-structured OSM/EPC fields (pilot via `assist_cim` first) |

---

## Protégé workstation runbook (local test with virtualized DB)

Use this section to run Protégé from your workstation home and execute SPARQL on top of the virtual graph defined by `semantic/ontop/citygml-bot-sosa-ssn-geosparql-time.obda`.

### Database host (remote)

PostgreSQL/PostGIS runs on the **eclab server**, not on your laptop:

| Item | Value |
|------|--------|
| Host | `130.192.238.11` |
| Port | `15432` |
| Database | `cim_wizard_integrated` |
| User / password | `cim_wizard_user` / `cim_wizard_password` |
| Container | `cim-integrateddb` (`cim-database:latest`) |
| SSH | `ssh eclabuser@130.192.238.11` |

JDBC URL for Protégé / Ontop:

```text
jdbc:postgresql://130.192.238.11:15432/cim_wizard_integrated
```

Properties files `semantic/ontop/citygml-bot-sosa-ssn-geosparql-time.properties` and `semantic/ontop/cim_citydb.properties` are configured for this host.

### 1) Verify remote DB (from your workstation)

You do **not** need to start `docker compose` locally. On the server the container is already up (`0.0.0.0:15432->5432/tcp`).

1. Confirm DB is reachable from your workstation:
   ```bash
   psql "postgresql://cim_wizard_user:cim_wizard_password@130.192.238.11:15432/cim_wizard_integrated" -c "SELECT now();"
   ```
2. Optional sanity check for data presence:
   ```bash
   psql "postgresql://cim_wizard_user:cim_wizard_password@130.192.238.11:15432/cim_wizard_integrated" \
     -c "SELECT count(*) FROM citydb.building WHERE objectclass_id = 26;"
   ```
3. If connection fails: check VPN/firewall to `130.192.238.11:15432`, or on the server:
   ```bash
   ssh eclabuser@130.192.238.11
   sudo docker ps --filter name=cim-integrateddb
   sudo docker logs --tail 50 cim-integrateddb
   ```
4. **If port 15432 is not open from your network**, use an SSH tunnel and point Protégé at `localhost`:
   ```bash
   ssh -N -L 15432:127.0.0.1:15432 eclabuser@130.192.238.11
   ```
   Keep that terminal open, then use JDBC URL:
   ```text
   jdbc:postgresql://localhost:15432/cim_wizard_integrated
   ```
   Test locally:
   ```bash
   psql "postgresql://cim_wizard_user:cim_wizard_password@localhost:15432/cim_wizard_integrated" -c "SELECT now();"
   ```

### 2) Launch Protégé from your workstation path

Detected install path on workstation: `/home/taherdoust/Protege-5.6.9`.

Run:
```bash
cd /home/taherdoust/Protege-5.6.9
./run.sh
```

If Java is missing:
```bash
sudo apt update && sudo apt install -y default-jre
```

### 3) Load ontology shell and mappings

1. In Protégé: **File -> Open**.
2. Open:
   - `/mnt/Data_HDD/00products/CIM_wizard/semantic/ontop/citygml-bot-sosa-ssn-geosparql-time.rdf`
3. Ensure `catalog-v001.xml` remains in the same folder (so imports resolve to local stubs).
4. Open Ontop panel (plugin): add datasource using:
   - **Direct** (when `130.192.238.11:15432` is reachable):
     - URL: `jdbc:postgresql://130.192.238.11:15432/cim_wizard_integrated`
   - **Via SSH tunnel** (when only SSH works):
     - URL: `jdbc:postgresql://localhost:15432/cim_wizard_integrated`
   - Driver: `org.postgresql.Driver`
   - User: `cim_wizard_user`
   - Password: `cim_wizard_password`
   - Or load properties file: `semantic/ontop/citygml-bot-sosa-ssn-geosparql-time.properties` (direct host; switch to `localhost` in the file if you use a tunnel)
5. Load mapping file:
   - `/mnt/Data_HDD/00products/CIM_wizard/semantic/ontop/citygml-bot-sosa-ssn-geosparql-time.obda`
6. Click **Test Connection** (must pass before querying).

### 4) Run first SPARQL smoke test

Open Ontop SPARQL tab and run:

```sparql
PREFIX bot: <https://w3id.org/bot#>
SELECT ?b WHERE {
  ?b a bot:Building .
}
LIMIT 10
```

Expected: IRIs like `http://data.cimwizard.org/building/{id}`.

### 5) Run project test query set

Use queries from:
- `/mnt/Data_HDD/00products/CIM_wizard/semantic/ontop/test-queries.sparql`

Recommended first query:

```sparql
PREFIX bot:    <https://w3id.org/bot#>
PREFIX schema: <https://schema.org/>
PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
PREFIX cim:    <http://data.cimwizard.org/energy/>

SELECT ?building ?label ?height ?storeys WHERE {
  ?building a bot:Building ;
            rdfs:label ?label .
  OPTIONAL { ?building schema:height ?height }
  OPTIONAL { ?building cim:storeysAboveGround ?storeys }
}
ORDER BY ?label
LIMIT 50
```

### 6) If query returns empty or errors

- Empty result: source tables may not be populated yet (`citydb.*`, `ng2_*`, `cim_vector.*`).
- SQL relation error: check schema/table names expected by OBDA (this OBDA uses both `citydb.feature` and `citydb.cityobject` joins).
- Connection error: from workstation run `psql ...@130.192.238.11:15432...`; on server verify `cim-integrateddb` is healthy and port `15432` is exposed.
- Wrong tab: use **Ontop SPARQL** tab, not only Protégé ontology browser.

### 7) Optional: keep a repeatable test checklist

1. Remote DB reachable (`130.192.238.11:15432`).
2. Protégé up.
3. Ontology shell loaded.
4. OBDA mapping loaded.
5. Test connection passed.
6. Smoke query returns rows.
7. Run Q1-Q6 from `test-queries.sparql`.

---

## Next steps (engineering)

1. **Extend `ai4db/stage1_cim_v2.py`** with `citydb` + `ng2_*` schema definitions and OBDA-shaped SQL templates (mirror `cim_citydb.obda` mapping groups).
2. **Extract BLINKG gold table** from `cim_citydb.obda` (63 mappings → Table 6 columns); add hold-out split for per-task F1 evaluation.
3. **Fine-tune or continue training** via `txt2ssql/ftv2/` on merged dataset including CityDB OBDA-source samples; evaluate with `assist_cim/evaluator_v2.py`.
4. **Build OBDA synthesis module** (`semantic/scripts/` or `semantic/agents/`): LLM4VKG alignment + BLINKG task agents + fine-tuned Q2SQL + target templates → tabular output → `.obda`.
5. **Pilot RML-FNML** on one semi-structured column (e.g. OSM `building` tag → `cim:buildingType`) using paper’s `getAnswerFromLLM` pattern; store raw text for O6 provenance.
6. **Validation loop:** BLINKG per-task F1 → SQL EX (`evaluator_v2.py`) → Ontop mapping load → `test-queries.sparql` on remote DB (`130.192.238.11:15432` or SSH tunnel).
7. Add **Brick** / **SERAF** stubs when HVAC / device mappings expand beyond `cim:` + `sosa:Sensor`.
8. Wire CI: Ontop smoke test + BLINKG subset + `assist_cim` benchmark on disposable CityDB snapshot.
9. **Optional:** contribute **CIM CityDB scenario** back to BLINKG community (Schema-distant + GeoSPARQL transforms) once gold table is stable.
