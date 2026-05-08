# Datalake Architecture

Goal: build a local (non-cluster) datalake so the development team can upload, discover, and query shared spatial and non-spatial datasets with rich metadata.

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

### Upload_page.py
- Choose source type: **File** (FTP upload) or **OGC** service URL (WFS / WMS / WCS / WMTS)
- Metadata form: name, description, tags, location, CRS, temporal range
- Spatial properties: geometry type, bounding box (manual or auto-calculated from uploaded GeoJSON)
- Registers record in `public.meta_table` in PostGIS

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

## Alternative solutions

The table below compares the current stack against established open-source alternatives for a team geospatial datalake.

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
**https://geonode.org** — full geospatial CMS and catalogue

GeoNode is a Django-based platform that combines GeoServer, PostGIS, and a web CMS into a single system. It provides dataset upload, metadata editing, map composition, and user management out of the box.

| Aspect | Detail |
|---|---|
| Standards | CSW, WMS, WFS, WCS, OGC API (partial) |
| Data backends | PostGIS + GeoServer |
| Deployment | Docker Compose (multi-container: GeoServer, Django, PostGIS, RabbitMQ, Nginx) |
| Frontend | Full web application with CRUD UI, maps, metadata forms, user roles |
| Configuration complexity | High — many services, significant DevOps overhead for local setup |
| Best fit | Enterprise data portal with public/private dataset sharing, role-based access, and OGC service publishing |
| Gap vs current stack | Heavy stack for a small internal team; harder to customise the workflow |

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
Phase 1 (now)
  current stack:  Streamlit UI  →  public.meta_table (PostGIS)

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

| Feature / Requirement | Current (PostGIS + Streamlit) | pygeoapi | GeoNode | GeoServer | CKAN + spatial | MinIO + pgSTAC |
|---|---|---|---|---|---|---|
| Upload workflow for team | Custom Streamlit form | No | Yes (full CMS) | No | Yes (data portal) | No |
| Spatial search (polygon intersect) | Native ST_Intersects | OGC bbox/intersects filter | Via GeoServer | Via WFS | Via ckanext-spatial | STAC spatial filter |
| OGC API / WFS / WMS publishing | No (Streamlit only) | Yes (core feature) | Yes (via GeoServer) | Yes (core feature) | Partial | Via stac-fastapi |
| File storage | FTP | External | GeoServer data dir | Data dir / PostGIS | External storage | MinIO (S3) |
| Metadata standard | Custom meta_table | OGC API Records / STAC | ISO 19115 / Dublin Core | Minimal | DCAT / Dublin Core | STAC |
| Operational complexity (local) | Low | Low | High | Medium | Medium | Medium–High |
| Custom team workflow | Full control | Config-driven | Limited | No | Limited | No |
| Best fit for this project now | Yes — full control, low overhead | Add as API layer on top of current stack | Too heavy for internal team | Useful if QGIS/desktop access needed | If public open data portal needed | Future evolution for large file archives |
