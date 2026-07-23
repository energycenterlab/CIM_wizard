-- Executed automatically by the postgis/postgis Docker image on first startup.
-- Safe to re-run because every statement uses IF NOT EXISTS.

CREATE EXTENSION IF NOT EXISTS postgis;

-- Central metadata registry for all spatial and non-spatial datasets.
CREATE TABLE IF NOT EXISTS public.meta_table (
    id                UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    name              TEXT          NOT NULL,
    description       TEXT          NOT NULL DEFAULT '',
    tags              TEXT[]        NOT NULL DEFAULT '{}',

    -- Source classification
    source_type       TEXT          NOT NULL DEFAULT 'file',  -- 'file' | 'ogc'
    ogc_url           TEXT,                                   -- WFS / WMS / WCS endpoint
    ogc_type          TEXT,                                   -- WFS | WMS | WCS | WCS | WMTS

    -- Spatial metadata
    is_spatial        BOOLEAN       NOT NULL DEFAULT FALSE,
    spatial_type      TEXT,                                   -- geometry type: Point, Polygon, etc.
    crs               TEXT          NOT NULL DEFAULT 'EPSG:4326',
    spatial_footprint GEOMETRY(POLYGON, 4326),                -- user-drawn bounding polygon

    -- Temporal coverage
    temporal_start    DATE,
    temporal_end      DATE,

    -- Geographic label (free text, e.g. "Turin, Piedmont")
    location          TEXT,

    -- File storage (populated for source_type = 'file')
    filename          TEXT          NOT NULL DEFAULT '',
    file_size_bytes   BIGINT,
    file_path         TEXT,         -- legacy FTP / local path
    object_uri        TEXT,         -- MinIO/S3 URI, e.g. s3://datawh/<id>/file.geojson
    uploaded_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- Safe on existing volumes that were created before object_uri existed.
ALTER TABLE public.meta_table
    ADD COLUMN IF NOT EXISTS object_uri TEXT;

-- ── Warehouse extension tables (added by api/db.py on startup) ──────────────

-- Stores the full ingest manifest JSON per datasource load.
CREATE TABLE IF NOT EXISTS public.dw_manifests (
    id           UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id   UUID         REFERENCES public.meta_table(id) ON DELETE CASCADE,
    manifest     JSONB        NOT NULL,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dw_manifests_dataset
    ON public.dw_manifests (dataset_id);

-- Stores ingested feature rows: surrogate PK, dataset FK, geometry, JSONB attributes.
CREATE TABLE IF NOT EXISTS public.dw_features (
    id           UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id   UUID         REFERENCES public.meta_table(id) ON DELETE CASCADE,
    geometry     GEOMETRY,
    attributes   JSONB        NOT NULL DEFAULT '{}',
    loaded_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dw_features_dataset
    ON public.dw_features (dataset_id);

CREATE INDEX IF NOT EXISTS idx_dw_features_geom
    ON public.dw_features USING GIST (geometry);
