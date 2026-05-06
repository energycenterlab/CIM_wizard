# Local Datalake Architecture (Current)

Goal: build a local (non-cluster) datalake so company teams can upload, discover, and download shared datasets with spatial and temporal metadata.

## Stack

- **Database:** Dockerized PostgreSQL + PostGIS
- **Frontend:** Streamlit + streamlit-folium
- **Spatial operations:** PostGIS (`ST_Intersects`, `ST_GeomFromGeoJSON`, GiST index)
- **Storage model:** dataset metadata + footprint in table columns, original JSON payload in `JSONB`

## Implemented UI

The Streamlit app is under `datalake/ui/` and currently provides two pages:

1. **Upload (`pages/1_📤_Upload.py`)**
   - Upload JSON/GeoJSON file
   - Enter dataset metadata: name, description, tags
   - Draw spatial footprint (CRS **EPSG:4326**) on map
   - Set temporal footprint (`temporal_start`, `temporal_end`)
   - Insert into PostGIS table

2. **Explore/Download (`pages/2_📥_Explore.py`)**
   - Filter by tags and temporal range
   - Draw study-area polygon on map
   - Query datasets where `ST_Intersects(spatial_footprint, study_area)` is true
   - Visualize matching footprints on the map
   - Download matching dataset JSON

## Data model (PostGIS)

Single table (`datasets`) used by the Streamlit frontend:

- `id UUID PRIMARY KEY`
- `name TEXT`
- `description TEXT`
- `tags TEXT[]`
- `spatial_footprint GEOMETRY(POLYGON, 4326)`
- `temporal_start DATE`
- `temporal_end DATE`
- `data JSONB` (raw uploaded JSON payload)
- `filename TEXT`
- `uploaded_at TIMESTAMPTZ`

Indexes:

- GiST index on `spatial_footprint`
- GIN index on `tags`
- B-tree index on `(temporal_start, temporal_end)`

## Flow

1. User uploads dataset and draws footprint in Upload page.
2. App stores metadata + geometry + JSON payload in PostGIS.
3. User defines filters + study area in Explore page.
4. App returns and maps all intersecting datasets.
5. User downloads selected JSON data directly from UI.

## Architecture decision table (updated)

| Feature / Requirement | Current Choice: PostGIS + Streamlit/Folium | MongoDB Single-Collection Pattern | MinIO + pgSTAC |
|---|---|---|---|
| Primary use case | Internal collaborative geospatial datalake with map-first querying | Flexible JSON app with low relational constraints | Cataloging large geospatial assets/files at scale |
| Storage model | Structured columns + `JSONB` for raw payload + PostGIS geometry | Entire payload and geometry in document collections | Binary files in object storage + STAC metadata in database |
| Spatial filtering in UI | Native `ST_Intersects` against user-drawn study polygon | Requires geospatial indexes but weaker relational joins across collections | Great for item-level extents; file-internal geometry needs extra processing |
| Temporal + tag filtering | Straightforward SQL + array/date indexes | Feasible, but complex multi-criteria analytics can become less transparent | Strong metadata filtering, best when data already STAC-compliant |
| Footprint visualization | Direct from `GEOMETRY(POLYGON,4326)` to map layers | Possible, but model consistency must be enforced in app logic | Usually metadata-centric; footprint resolution depends on catalog detail |
| Operational complexity (local setup) | Low to medium; one DB container + Streamlit app | Low; easy local bootstrap | Medium to high; storage service + catalog services |
| Best fit for this project now | **Yes**: aligns with current 2-page workflow (upload/explore/download) | Useful alternative if schema freedom becomes top priority | Better as a future evolution for very large multi-format archives |