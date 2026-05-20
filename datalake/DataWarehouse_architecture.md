# Data warehouse & geospatial ingestion architecture

**Strategic direction (presented):** move from a **catalogue-first / STAC-datalake** emphasis toward an **operational data warehouse**: land vector (and other) data through **ETL**, store **normalized facts** (PK, FK, geometry, JSONB attributes), and use **standard catalog metadata only when it exists** to pre-fill dataset registry fields and distribution links.

The sections below still describe the existing PostGIS catalogue (`meta_table`) and optional STAC/pgSTAC paths for comparison — they are **alternatives or future API layers**, not the primary story of the new ingest flow.

---

## Current stack

| Layer | Technology |
|---|---|
| Spatial database | PostgreSQL 16 + PostGIS 3.4 (Dockerized, port 35432) |
| Document store | MongoDB Community (Dockerized, port 27018) |
| Frontend | Streamlit + streamlit-folium |
| File storage | FTP server (path stored in meta_table) |
| Spatial operations | PostGIS `ST_Intersects`, `ST_GeomFromGeoJSON`, GiST index |

---

## UI pages (`datalake/ui/`)

### Home.py
Minimal landing page with navigation links to Upload and Explore.

### Upload_page.py (catalogue-oriented)

- Choose source type: **File** (FTP upload) or **OGC** service URL (WFS / WMS / WCS / WMTS)
- Metadata form: name, description, tags, location, CRS, temporal range
- Spatial properties: geometry type, bounding box (manual or auto-calculated from uploaded GeoJSON)
- Registers record in `public.meta_table` in PostGIS

### `ingest_v_upload.py` (warehouse-oriented vector ingest — new approach)

Interactive **ingest wizard** (Streamlit): user uploads a vector file or provides an OGC service URL; the UI **profiles** the file and asks the user to confirm how it maps into the warehouse.

**Location:** `datalake/ui/pages/ingest_v_upload.py`
**Run:** `streamlit run datalake/ui/Home.py` (appears in sidebar) or `streamlit run datalake/ui/pages/ingest_v_upload.py` directly.

#### Wizard steps

| Step | What happens |
|---|---|
| **1 — Source** | Choose **File upload** (GeoJSON, Shapefile `.zip`, GPKG, CSV, CityJSON) or **OGC service URL** (WFS / OGC API Features). For OGC: `GetCapabilities` / `/collections` fetches available layers. |
| **2 — Classification** | Spatial / non-spatial toggle. If spatial: vector / raster radio. Auto-detects format from filename. CSV adds lon/lat/WKT column pickers. GPKG adds layer selector via `fiona.listlayers`. |
| **3 — Standard metadata** | Optional CSW / ISO 19139 / OGC API Records pre-fill. Paste XML/JSON or fetch from CSW `GetRecordById`. Pre-fills registry fields (name, description, tags, CRS, temporal range). Manual form always shown. |
| **4 — Profile (CRS)** | Reads columns, **CRS**, geometry type, and feature count from a small file sample — no full parse. Shows a CRS panel: detected source CRS, override field, target storage CRS, reprojection flag. Geometry column highlighted. |
| **5 — Column mapping** | User assigns each column to: **PK** (uuid/natural key/serial), **FK** (file-provided relationship keys), **spatial** (geometry column + CRS), **non-spatial** (include/drop from JSONB). Unmapped columns default to JSONB. |
| **6 — Manifest** | Builds and displays the **ingest manifest JSON**. Summary card, JSON viewer, Download button, optional POST to any FastAPI/ingest endpoint with Bearer token, Start over button. |

#### CRS detection per format (Step 4)

| Format | CRS detection method |
|---|---|
| GeoJSON | Legacy `crs.properties.name` member if present; otherwise `EPSG:4326` (OGC/RFC 7946 default) |
| Shapefile (zip) | `fiona.open().crs.to_epsg()` / `.to_authority()` / WKT `AUTHORITY["EPSG","..."]` regex fallback |
| GeoPackage | Same as shapefile via `fiona.open(layer=...)` |
| CityJSON | `metadata.referenceSystem` URI — extract EPSG code with regex; defaults to `EPSG:4326` |
| CSV | No CRS embedded — user sets manually via the override field |
| OGC API Features | `crs` / `storageCrs` from first-page JSON; defaults to `EPSG:4326` |

If detected source CRS differs from target warehouse CRS, a warning is shown and `"reproject": true` is set in the manifest `spatial` block.

#### Ingest manifest JSON structure

```json
{
  "ingest_manifest_version": "1.0",
  "manifest_id": "<uuid>",
  "source":  { "type": "file", "filename": "buildings.gpkg", "file_format": "GeoPackage", "layer": "buildings_2024" },
  "profile": { "detected_crs": "EPSG:32632", "geom_type": "MultiPolygon", "feature_count": 48302 },
  "registry": { "name": "Turin Buildings 2024", "tags": ["buildings","urban"], "temporal_start": "2024-01-01", "temporal_end": "2024-12-31" },
  "warehouse_mapping": {
    "pk":          { "policy": "uuid_per_row", "warehouse_column": "id" },
    "fk":          [{ "generated": true, "references": "dim_dataset.dataset_id" }],
    "spatial":     { "source_crs": "EPSG:32632", "target_crs": "EPSG:4326", "reproject": true,
                     "source_type": "native", "geom_column": "__geometry__" },
    "non_spatial": { "strategy": "jsonb", "target_column": "attributes",
                     "include": ["name","height"], "exclude": ["internal_id"] }
  },
  "standard_metadata": null
}
```

The wizard is the **default** when users do not have machine-readable catalog metadata. It replaces ad hoc assumptions with an explicit contract your loader implements.


### Explore_page.py
- Sidebar: attribute filters (tags, source type, spatial type, date range)
- Sidebar: spatial polygon filter — draw on map, active status shown with bbox
- Full-width interactive map viewer (Folium + Leaflet Draw)
- Spatial query: `ST_Intersects(spatial_footprint, drawn_polygon)`
- Results list with OGC URL / FTP path / metadata details

---

## Data model — `public.meta_table` (PostGIS)

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | auto-generated |
| `name` | TEXT | required |
| `description` | TEXT | |
| `tags` | TEXT[] | GIN-indexed |
| `source_type` | TEXT | `file` or `ogc` |
| `ogc_url` | TEXT | WFS / WMS / WCS endpoint |
| `ogc_type` | TEXT | WFS, WMS, WCS, WMTS, … |
| `is_spatial` | BOOLEAN | |
| `spatial_type` | TEXT | Point, Polygon, Raster, … |
| `crs` | TEXT | default EPSG:4326 |
| `spatial_footprint` | GEOMETRY(POLYGON,4326) | GiST-indexed |
| `temporal_start` | DATE | B-tree indexed |
| `temporal_end` | DATE | B-tree indexed |
| `location` | TEXT | free-text label |
| `filename` | TEXT | original filename |
| `file_size_bytes` | BIGINT | |
| `file_path` | TEXT | full path on FTP server |
| `uploaded_at` | TIMESTAMPTZ | auto |

---

## Standard metadata for automation — CSW and related specs

You asked whether something like **Catalogue Service for the Web (CSW)** is the standard metadata to “do it automatically.” Short answer:

- **CSW is not a metadata document format.** It is an **OGC web service interface** for **publishing and searching collections of descriptive metadata** about data, services, and related resources. Clients use operations such as **GetCapabilities**, **DescribeRecord**, **GetRecords**, **GetRecordById**, and (in transactional profiles) **Harvest**.
- The **records** exchanged through CSW are typically **XML** instances of **application schemas** — most commonly **ISO 19115** (conceptual) with **ISO 19139** (XML encoding / GMD), plus profiles (e.g. INSPIRE). **Dublin Core** is also common for simpler records.

So for **automatic** pre-fill of catalogue / dataset-dimension fields (title, abstract, keywords, temporal extent, geographic identifier, **online resource / distribution URLs**), the practical chain is:

**CSW endpoint + record identifier → GetRecordById / GetRecords → parse ISO 19139 (or DC) → map into your registry row**, then still run **`ingest_v_upload.py`** (or your ETL) for **PK / FK / geometry / JSONB column semantics**, because catalog metadata rarely specifies which CSV column is longitude.

### Is there “such” a standard?

| Piece | Standard | What it automates | What it does *not* automate alone |
|---|---|---|---|
| **Catalogue API** | **OGC CSW** | Finding and retrieving standardized **metadata records** | Parsing inside the vector file; PK/FK/column mapping |
| **Record content** | **ISO 19115 / 19139** (via CSW) | Rich dataset description, lineage, constraints, **CI_OnlineResource** links to files | Same — distribution links help locate files, not column semantics |
| **Modern JSON catalogue** | **OGC API Records** | Same *role* as CSW for discovery, with **JSON** and GeoJSON extents | Same |
| **Asset-oriented JSON** | **STAC** (optional in this architecture) | Spatiotemporal item + `assets` with MIME types | Still not a full warehouse column map; can complement links |
| **Format** | **IANA media types**, GDAL sniffing | Choice of reader (GeoJSON, GPKG, zip shapefile, CSV) | Attribute-to-JSONB mapping |

**Conclusion for your presentation:** Yes — **CSW + ISO 19139** (or **OGC API Records** as a JSON-first catalogue) is the classic OGC-aligned way to **automate dataset-level metadata and links**. There is still **no single OGC “data type catalog” enum** that replaces the **interactive ingest manifest** for warehouse **PK / FK / spatial / non-spatial** mapping; the two layers work **together**.

### Recommended combination for this project

1. **Default:** `ingest_v_upload.py` builds the **ingest manifest JSON** (PK policy, FK to `dataset_id`, geometry mapping, `JSONB` attribute projection).
2. **When the user has a catalogue:** optional fields **CSW base URL + record ID** (or paste **ISO 19139 XML** / **OGC API Records** JSON) → populate **dataset registry** (and pre-fill links / title / time) **before** or **alongside** the wizard.
3. **Optional:** STAC Item remains a possible **additional** source of links and bbox/time for teams already producing STAC — not required for the warehouse story.

### Summary flow

```
[CSW / ISO XML / OGC API Records JSON available?]
        |
        +-- yes --> fetch/parse -> fill dataset registry + distribution links;
        |           then ingest_v_upload (or server-side profile) for PK/FK/geom/JSONB
        |
        +-- no  --> minimal dataset form + ingest_v_upload wizard -> same warehouse load
```

### Decision note

| Approach | Pros | Cons |
|---|---|---|
| **CSW + ISO 19139** | Strong OGC / INSPIRE story; many institutional catalogues; rich online resources | XML parsing; not every internal team exposes CSW |
| **OGC API Records** | JSON-native catalogue; fits POST-oriented tooling | Fewer legacy deployments than CSW in some domains |
| **Interactive manifest only** | No external dependency; explicit warehouse contract | User types more discovery metadata |

---

## Alternative solutions

The table below compares the current stack against established open-source alternatives for a team **geospatial data warehouse / catalogue** setup.

### pygeoapi
**https://pygeoapi.io** — OGC-compliant Python geospatial API server

pygeoapi exposes any backend (PostGIS, GeoPackage, Elasticsearch, MongoDB, …) as standard OGC API endpoints (Features, Records, Coverages, Tiles, Processes). It is configuration-driven (one YAML file) and ships as a Docker image.

| Aspect | Detail |
|---|---|
| Standards | OGC API Features, OGC API Records, OGC API Coverages, OGC API Tiles, OGC API Processes, STAC |
| Data backends | PostGIS, GeoPackage, Elasticsearch, MongoDB, CSV, GeoTIFF, NetCDF, and more via plugins |
| Deployment | Docker (`ghcr.io/geopython/pygeoapi`), pip, conda |
| Frontend | None built-in — serves JSON/HTML; requires a separate map client (MapLibre, OpenLayers, etc.) |
| Configuration complexity | Low — single `pygeoapi-config.yml` |
| Best fit | Exposing the datalake as a machine-readable OGC API for external clients and GIS tools |
| Gap vs current stack | No upload UI or team-facing discovery UI; would need a separate frontend |

**How it could integrate:** run pygeoapi on top of the existing PostGIS `meta_table` to expose the catalogue as an OGC API Records / Features endpoint while keeping the Streamlit UI for data managers.

---

### GeoNode
**https://geonode.org** — full geospatial CMS, catalogue and OGC service publisher

GeoNode is a production-grade Django-based web platform that bundles GeoServer, PostGIS, a full web CMS, and a user / permissions system into a single deployable product. Institutions use it to build national/regional spatial data infrastructures.

#### What GeoNode does

- **Upload:** accepts Shapefile (zip), GeoTIFF, CSV, GeoPackage, and SLD styles directly through the web UI or REST API. It validates, reprojects (via OGR), and imports into the internal PostGIS schema automatically.
- **Metadata editing:** ISO 19115-compliant metadata forms (title, abstract, categories, keywords, regions, temporal extent, licence, constraints). Metadata can be harvested/exported as ISO 19139 XML or Dublin Core via a built-in CSW endpoint.
- **OGC publishing:** every ingested layer is published as WMS, WFS, WCS, and WMTS via GeoServer automatically — no manual layer configuration.
- **Maps:** users can compose web maps by combining any published layers and share them with roles/permissions.
- **Discovery:** spatial search (bounding box intersect), full-text, category, keyword, region, and date filters on a map-based catalogue page.
- **API:** REST API (`/api/v2/`) and CSW (`/catalogue/csw`) for machine-readable access.

| Aspect | Detail |
|---|---|
| Standards | CSW 2.0.2 (built-in), WMS, WFS, WCS, WMTS, OGC API (partial via GeoServer) |
| Data backends | GeoServer (vector/raster layers), PostGIS (vector storage), Django ORM (metadata) |
| Deployment | Docker Compose: GeoServer, Django/Uwsgi, PostGIS, RabbitMQ, Celery, Nginx — 6+ containers |
| Upload workflow | Web UI drag-and-drop or REST API; auto-import + auto-publish |
| Metadata standard | ISO 19115 / ISO 19139 with built-in forms; CSW for harvest/search |
| Spatial search | `ST_Intersects` backed by PostGIS on stored bounding boxes |
| Operational complexity | **High** — significant DevOps effort; each component needs tuning for local use |
| Best fit | Enterprise or agency data portal with dozens of users, public/private sharing, and full OGC service publishing |
| Gap vs current stack | Overkill for a small internal team; the upload/ingest workflow cannot easily be customised; warehouse-style column mapping (PK/FK/JSONB) is not supported |

**Integration path with this stack:** GeoNode could serve as the public-facing discovery and OGC publishing layer on top of the PostGIS database, while the custom `ingest_v_upload` wizard handles the warehouse-level ETL. You would bypass GeoNode's own upload for warehouse ingestion and use GeoServer's REST API to publish layers after the ETL.

---

### HALE Studio
**https://wetransform.to/halestudio/** — open-source spatial schema transformation IDE

HALE Studio (Humboldt Alignment Editor) is a desktop application designed for **schema mapping and data transformation** between heterogeneous spatial data models. It was originally developed for INSPIRE compliance (transforming national data to INSPIRE harmonised schemas) but works for any schema-to-schema mapping.

#### What HALE does

- **Schema import:** reads source and target schemas from GML Application Schema (XSD), GeoPackage, Shapefile, database (PostGIS, Oracle, SQL Server), WFS, or CSV.
- **Mapping functions:** hundreds of built-in transformation functions (rename, merge, split, type conversion, CRS reprojection, geometry transformation, aggregation, conditional mapping).
- **Alignment project (`.halex`):** the mapping is stored in a reusable project file — version-controllable, team-shareable.
- **Execution:** transforms the actual data (features) using the defined mapping. Outputs to GML, GeoPackage, Shapefile, GeoJSON, PostGIS, WFS-T.
- **Validation:** validates output against target schema and INSPIRE constraints.
- **CLI / headless mode:** `hale transform` command runs a `.halex` project file headlessly — suitable for batch ETL pipelines.

| Aspect | Detail |
|---|---|
| Standards | GML/XSD, INSPIRE schemas, ISO 19109, WFS, GeoPackage, PostGIS |
| Interface | Desktop GUI (Eclipse-based) + headless CLI |
| Deployment | Standalone `.jar` / installer (Windows, Linux, macOS) |
| Schema mapping | Explicit, visual, reusable alignment project |
| CRS handling | Automatic reprojection via EPSG registry |
| Automation | `hale transform -project mymap.halex -source data.gpkg -target output.gpkg` |
| Operational complexity | Low to medium — desktop app; CLI for headless runs |
| Best fit | One-time or recurring **complex schema transformations** (many-to-many column mappings, type conversions, INSPIRE harmonisation) where the mapping must be documented and reproducible |
| Gap vs current stack | No web UI; no catalogue/discovery layer; mapping project must be pre-built by a GIS specialist |

**Integration with this stack:** use HALE for the *transform* phase when the mapping is complex (e.g. national dataset to INSPIRE GML, then load to PostGIS). The `ingest_v_upload` wizard handles simple cases interactively; HALE handles complex ones via a pre-built `.halex` project.

---

### GeoKettle / Pentaho Spatial (now: Hop)
**https://github.com/enricofer/GeoKettle** / **https://hop.apache.org** — open-source spatial ETL pipeline engine

GeoKettle was a spatial extension of Pentaho Data Integration (PDI / Kettle). PDI has since been donated to Apache as **Apache Hop**, which includes built-in spatial transforms. These tools provide a visual, pipeline-based ETL approach similar to FME but open-source.

#### What Hop/GeoKettle does

- **Visual pipeline editor:** drag-and-drop workflow with hundreds of input, transform, and output "steps" (now called *transforms* in Hop).
- **Spatial steps (via GeoKettle / plugins):** read/write GeoJSON, Shapefile, PostGIS, WFS; reproject geometries; spatial joins (intersect, within, contains); buffer, union, clip.
- **Non-spatial ETL:** everything standard PDI/Hop covers — database lookups, HTTP calls, scripting (Groovy/JavaScript), conditional branching, looping, error handling.
- **Pipeline metadata:** pipelines are `.hpl` (Hop Pipeline) XML files — version-controllable and runnable headlessly.
- **Headless execution:** `hop-run.sh --file pipeline.hpl --runconfig local` — suitable for scheduled jobs.
- **Apache Hop GUI:** web-based IDE (Hop Web) runs in a browser; no desktop install needed.

| Aspect | Detail |
|---|---|
| Standards | PostGIS, GeoJSON, Shapefile, WFS, CSV, JDBC (any DB) |
| Interface | Web GUI (Hop Web) or desktop GUI (Hop GUI) + CLI |
| Deployment | Docker (`apache/hop`) or standalone |
| Schema mapping | Visual pipeline steps: explicit column selection, rename, type cast, geometry transform |
| CRS handling | Via GeoPandas/OGR plugin or custom script step |
| Automation | `hop-run.sh` CLI for scheduled/headless pipelines |
| Operational complexity | Medium — Hop itself is straightforward; spatial plugins need configuration |
| Best fit | **Recurring ETL** workflows (daily/weekly ingest from external sources) where the pipeline logic is complex but fixed — better than writing bespoke Python scripts for each source |
| Gap vs current stack | No catalogue or discovery UI; spatial CRS reprojection support is less mature than HALE; Hop's spatial ecosystem is smaller than FME |

**Integration with this stack:** Hop is a good fit as the **background ETL worker** that consumes the `ingest_v_upload` manifest JSON and actually performs the feature-level load into PostGIS — receiving the manifest via HTTP trigger or reading it from a queue, then executing the correct pipeline template.

---

### GeoServer
**https://geoserver.org** — OGC spatial data server

GeoServer publishes data from PostGIS, shapefiles, GeoTIFF, and more as WMS, WFS, WCS, WMTS, and OGC API endpoints. It includes a web admin UI for layer publishing but has no dataset catalogue or team workflow features.

| Aspect | Detail |
|---|---|
| Standards | WMS, WFS, WCS, WMTS, OGC API Features |
| Data backends | PostGIS, shapefiles, GeoTIFF, databases |
| Deployment | Docker (`docker.osgeo.org/geoserver`), WAR |
| Frontend | Admin UI for layer configuration only |
| Best fit | Publishing PostGIS layers as standard OGC services to desktop GIS tools (QGIS) or web clients |
| Gap vs current stack | No upload/discovery workflow; purely a service publisher |

---

### CKAN + ckanext-spatial
**https://ckan.org** — open data portal

CKAN is the platform behind data.gov and many national open data portals. The `ckanext-spatial` extension adds spatial search, WMS preview, and CSW harvesting.

| Aspect | Detail |
|---|---|
| Standards | DCAT, Dublin Core, CSW (via extension), INSPIRE (via extension) |
| Data backends | PostgreSQL (metadata), external storage for files |
| Deployment | Docker Compose |
| Frontend | Full data portal with dataset upload, search, API, user management |
| Best fit | Public-facing open data catalogue with harvesting from other sources |
| Gap vs current stack | Generalised data portal — spatial features need extension configuration; no native PostGIS spatial query |

---

### MinIO + pgSTAC
**https://min.io** + **https://github.com/stac-utils/pgstac**

MinIO provides S3-compatible object storage. pgSTAC is a PostGIS-based implementation of the STAC (SpatioTemporal Asset Catalog) specification. Together they form a cloud-native raster/vector archive.

| Aspect | Detail |
|---|---|
| Standards | STAC, OGC API Features (via stac-fastapi) |
| Data backends | S3 / MinIO for files, PostGIS for metadata |
| Deployment | Docker (MinIO + pgSTAC + optional stac-fastapi) |
| Frontend | None built-in — STAC browser clients (Radiant Earth STAC Browser) |
| Best fit | Large-scale multi-format archives (satellite imagery, LiDAR, time series) where STAC compliance is a requirement |
| Gap vs current stack | Over-engineered for small internal teams; requires all data to be STAC-compliant items |

---

### Terria / TerriaJS
**https://terria.io** — 3D/2D geospatial data exploration platform

TerriaJS is a React-based web map application that can connect to WMS, WFS, STAC, ArcGIS, and other services. It is not a catalogue or upload tool but a powerful visualisation frontend.

| Aspect | Detail |
|---|---|
| Standards | WMS, WFS, WCS, WMTS, STAC, OGC API Features, ArcGIS REST |
| Data backends | Any OGC-compatible service |
| Deployment | Docker or static build |
| Frontend | Rich 3D (Cesium) + 2D map viewer with catalogue sidebar |
| Best fit | Replacing the Streamlit Folium map with a production-grade spatial explorer connected to pygeoapi or GeoServer |
| Gap vs current stack | No data management — needs a separate backend for upload and metadata |

---

## Deep dive: stac-fastapi-pgstac

**Repository:** [github.com/stac-utils/stac-fastapi-pgstac](https://github.com/stac-utils/stac-fastapi-pgstac)
**Latest release:** 6.2.1 (January 2026)
**License:** MIT

### What it is

`stac-fastapi-pgstac` is a production-ready HTTP API server built on **FastAPI** that implements the [STAC API specification](https://stacspec.org) on top of **pgSTAC** — a PostgreSQL/PostGIS schema optimised for storing and querying SpatioTemporal Asset Catalog (STAC) items at scale.

The stack has three layers:

```
stac-fastapi-pgstac   ← FastAPI HTTP layer  (validates requests, adds HATEOAS links)
        |
    pgSTAC            ← PostgreSQL schema   (stores items as JSONB, spatial queries in SQL/plpgsql)
        |
  PostGIS (pg 16)     ← Database engine     (geometry types, GiST indexes, spatial functions)
```

All three run as a single Docker Compose stack. The API is available at `http://localhost:8082` after `make docker-run`.

---

### STAC data model — what you can store

STAC organises data into two levels:

#### Collections
A **Collection** is a named group of related datasets. Example: `building-footprints-2024`, `wms-services`, `dem-tiles`.

Required fields:
- `id` — unique identifier
- `description`
- `extent` — spatial bbox + temporal interval that covers all items
- `links`

#### Items
An **Item** is one dataset record. It is the equivalent of one row in `meta_table`. Example: one GeoJSON file, one raster, one WFS endpoint.

Mandatory STAC item fields:
- `id` — unique identifier (string)
- `geometry` — GeoJSON geometry (the spatial footprint, stored in PostGIS)
- `bbox` — bounding box `[xmin, ymin, xmax, ymax]`
- `datetime` — acquisition / reference date
- `properties` — any custom key/value metadata (free JSONB)
- `assets` — dictionary of named links to the actual files (URL or path)
- `links` — HATEOAS navigation links (added automatically by the API)

**Supported data types for assets:** any file format you can reference by URL or path:

| Format | Example asset key |
|---|---|
| GeoJSON | `"geojson": {"href": "ftp://server/path/to.geojson", "type": "application/geo+json"}` |
| GeoTIFF / raster | `"visual": {"href": "...", "type": "image/tiff"}` |
| Cloud-Optimised GeoTIFF (COG) | same, with `roles: ["data"]` |
| CSV | `"data": {"href": "...", "type": "text/csv"}` |
| Shapefile (zip) | `"data": {"href": "...", "type": "application/zip"}` |
| NetCDF / HDF5 | `"data": {"href": "...", "type": "application/netcdf"}` |
| IFC | `"ifc": {"href": "...", "type": "application/octet-stream"}` |
| WFS / WMS URL | store the URL string in `properties`, or as an `asset.href` |

The **files themselves are never stored inside PostGIS**. Assets are links. Files stay on your FTP server, local disk, MinIO, or any HTTP-accessible location — exactly as in the current datalake setup.

---

### How data is stored in PostGIS (pgSTAC schema)

pgSTAC creates its own dedicated schema named `pgstac` inside PostgreSQL. It does **not** use `public.meta_table`.

#### Main tables (simplified)

```
pgstac.collections      — one row per Collection (JSONB)
pgstac.items            — one row per Item       (JSONB + geometry column)
pgstac.searches         — cached search queries
pgstac.item_links       — materialised link metadata
```

#### How `pgstac.items` works

Each item is stored as a single `JSONB` column (`content`) alongside a PostGIS `geometry` column extracted from `content->>'geometry'`. This means:

- Full item JSON is preserved exactly as submitted (any custom `properties` fields are kept)
- Spatial queries run against the native PostGIS geometry column with a GiST index
- Temporal queries run against a `datetime` column extracted from `properties`
- All other property filters run against the JSONB column using GIN indexes

#### Is there a meta table / index table?

`pgstac.items` **is** the index table — it plays the same role as `public.meta_table` in the current stack but uses the STAC schema instead of a custom one.

The equivalent mapping:

| Current `meta_table` column | STAC / pgSTAC equivalent |
|---|---|
| `id` | `item.id` |
| `name` | `item.properties.title` |
| `description` | `item.properties.description` |
| `tags` | `item.properties.keywords` (array) |
| `source_type` | `item.properties.dl:source_type` (custom extension field) |
| `spatial_footprint` | `item.geometry` (PostGIS column, GiST indexed) |
| `temporal_start / end` | `item.properties.start_datetime` / `item.properties.end_datetime` |
| `crs` | `item.properties.proj:epsg` (STAC projection extension) |
| `ogc_url` | `item.assets.service.href` |
| `file_path` | `item.assets.data.href` |
| `uploaded_at` | `item.properties.created` |

Custom fields (like `source_type`, `location`, `file_size_bytes`) can be added freely to `properties` — pgSTAC stores JSONB so any extra key is preserved and queryable.

Everything lives in the `pgstac` schema; all collections and items share that schema. There is no per-dataset schema or table.

---

### Can you use stac-fastapi-pgstac for this datalake?

**Yes, with conditions:**

| Question | Answer |
|---|---|
| Can FTP-stored files be referenced? | Yes — any `href` (ftp://, http://, file://, s3://) works as an asset link |
| Can OGC service URLs be stored? | Yes — as an asset or as a custom property |
| Can non-spatial datasets be stored? | Yes — set `geometry: null` in the item; pgSTAC allows null geometry |
| Does it replace the Streamlit UI? | No — stac-fastapi-pgstac is an API only; you would keep or rebuild the UI to POST items to the API |
| Can QGIS connect to it? | Yes — QGIS has a STAC browser plugin; any STAC-aware client works |
| Can you explore data without writing code? | Yes — via [STAC Browser](https://radiantearth.github.io/stac-browser/) (hosted or local Docker) |
| Migration path from current stack? | Write a script that reads `meta_table` rows and POSTs them as STAC items to the API |

---

### Exploring stored datasets

stac-fastapi-pgstac exposes a full STAC API. Once running you can:

1. **STAC Browser** (`docker run -p 8080:8080 ghcr.io/radiantearth/stac-browser`) — visual map-based catalogue explorer, connects to `http://localhost:8082`
2. **QGIS STAC API Browser plugin** — search and load layers directly into QGIS
3. **HTTP / curl** — standard STAC API endpoints:
   - `GET /collections` — list all collections
   - `GET /collections/{id}/items` — list items in a collection
   - `POST /search` — spatial + temporal + property search (equivalent to the current Explore page query)
   - `GET /search?bbox=7.638,45.051,7.684,45.079` — bbox filter
4. **Custom Streamlit UI** — your existing Explore page can be adapted to call the STAC API instead of PostGIS directly

#### Example STAC search (equivalent to the current ST_Intersects query)

```json
POST /search
{
  "intersects": {
    "type": "Polygon",
    "coordinates": [[[7.638,45.051],[7.684,45.051],[7.684,45.079],[7.638,45.079],[7.638,45.051]]]
  },
  "filter": {
    "op": "=",
    "args": [{"property": "properties.dl:source_type"}, "file"]
  },
  "datetime": "2020-01-01T00:00:00Z/2025-12-31T23:59:59Z"
}
```

---

### Recommended migration path

If you decide to adopt stac-fastapi-pgstac in the future, the cleanest path is incremental:

```
Phase 1 (now — presented direction)
  Streamlit:  Upload_page / Explore_page  →  public.meta_table (PostGIS)
  Streamlit:  ingest_v_upload.py         →  ingest manifest JSON → ETL → warehouse facts (PK, FK, geom, JSONB)

Phase 2 (add API layer)
  Streamlit UI  →  stac-fastapi-pgstac API  →  pgstac schema (PostGIS)
  STAC Browser  →  stac-fastapi-pgstac API  →  pgstac schema (PostGIS)

Phase 3 (optional)
  replace FTP with MinIO (S3 assets)
  add STAC Browser as primary discovery UI
  keep Streamlit only for team data-manager upload workflow
```

The PostGIS container is shared — only the schema changes from `public.meta_table` to `pgstac.*`.

---

## Decision table

| Feature / Requirement | Current stack (PostGIS + Streamlit + `ingest_v_upload`) | pygeoapi | GeoNode | GeoServer | HALE Studio | Apache Hop (GeoKettle) | CKAN + spatial | MinIO + pgSTAC |
|---|---|---|---|---|---|---|---|---|
| Interactive upload wizard | Yes — 6-step wizard with CRS detection, column mapping, manifest | No | Yes (auto-import UI) | No | No (desktop mapping) | No (pipeline designer) | Yes (basic) | No |
| CRS auto-detection + reprojection flag | Yes — per-format (GeoJSON, SHP, GPKG, CityJSON, WFS) | No | Yes (auto via OGR) | No | Yes (core feature) | Via plugin | No | No |
| Warehouse column mapping (PK/FK/geom/JSONB) | Yes — explicit per-manifest | No | No | No | Yes (visual schema map) | Yes (pipeline steps) | No | No |
| Standard metadata (CSW / ISO 19139 / Records) | Optional pre-fill from CSW or paste | OGC API Records/STAC | ISO 19115 full + CSW endpoint | Minimal | ISO 19109 / INSPIRE | None | DCAT / Dublin Core | STAC |
| Spatial search (polygon intersect) | Native `ST_Intersects` | OGC bbox/intersects | Via GeoServer | Via WFS | No | No | Via ckanext-spatial | STAC spatial filter |
| OGC API / WFS / WMS publishing | No (Streamlit only) | Yes (core feature) | Yes (via GeoServer) | Yes (core feature) | No | No | Partial | Via stac-fastapi |
| Batch / headless ETL | Manual (run wizard) | No | No | No | CLI `hale transform` | CLI `hop-run.sh` | No | No |
| Operational complexity (local) | Low | Low | High (6+ containers) | Medium | Low (desktop) | Medium (Docker) | Medium | Medium–High |
| Custom team workflow | Full control | Config-driven | Limited | No | Mapping project file | Pipeline `.hpl` file | Limited | No |
| Best fit for this project now | Yes — primary ingestion path | Add as OGC API layer | Too heavy; use for public portal | Add for QGIS/WFS publishing | Complex schema mappings (INSPIRE) | Recurring headless ETL worker | If public open data portal needed | Future large-file archive |
