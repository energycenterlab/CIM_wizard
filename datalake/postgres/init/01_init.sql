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
    file_path         TEXT,         -- full path on the FTP server

    uploaded_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- Spatial index on bounding polygon (ST_Intersects queries)
CREATE INDEX IF NOT EXISTS idx_meta_spatial
    ON public.meta_table USING GIST (spatial_footprint);

-- Array index on tags (overlap operator &&)
CREATE INDEX IF NOT EXISTS idx_meta_tags
    ON public.meta_table USING GIN (tags);

-- B-tree index for temporal range queries
CREATE INDEX IF NOT EXISTS idx_meta_temporal
    ON public.meta_table (temporal_start, temporal_end);
