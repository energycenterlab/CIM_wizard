"""
PostGIS database helpers for the CIM Datalake UI.

DATABASE_URL must be set in .streamlit/secrets.toml or as an environment variable.
Example:
    DATABASE_URL = "postgresql://datalake:datalake@localhost:35432/datalake"
"""
from __future__ import annotations

import json
import os
from contextlib import contextmanager
from typing import Any

import psycopg2
import psycopg2.extras


def _db_uri() -> str:
    try:
        import streamlit as st
        return st.secrets.get("DATABASE_URL", os.getenv("DATABASE_URL", ""))
    except Exception:
        return os.getenv("DATABASE_URL", "")


@contextmanager
def get_conn():
    uri = _db_uri()
    if not uri:
        raise ValueError(
            "DATABASE_URL is not configured. "
            "Add it to .streamlit/secrets.toml or export it as an environment variable."
        )
    conn = psycopg2.connect(uri)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# DDL kept in sync with postgres/init/01_init.sql.
# Uses IF NOT EXISTS so it is safe to call on every app start.
_INIT_SQL = """
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS public.meta_table (
    id                UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    name              TEXT          NOT NULL,
    description       TEXT          NOT NULL DEFAULT '',
    tags              TEXT[]        NOT NULL DEFAULT '{}',
    source_type       TEXT          NOT NULL DEFAULT 'file',
    ogc_url           TEXT,
    ogc_type          TEXT,
    is_spatial        BOOLEAN       NOT NULL DEFAULT FALSE,
    spatial_type      TEXT,
    crs               TEXT          NOT NULL DEFAULT 'EPSG:4326',
    spatial_footprint GEOMETRY(POLYGON, 4326),
    temporal_start    DATE,
    temporal_end      DATE,
    location          TEXT,
    filename          TEXT          NOT NULL DEFAULT '',
    file_size_bytes   BIGINT,
    file_path         TEXT,
    uploaded_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_meta_spatial
    ON public.meta_table USING GIST (spatial_footprint);

CREATE INDEX IF NOT EXISTS idx_meta_tags
    ON public.meta_table USING GIN (tags);

CREATE INDEX IF NOT EXISTS idx_meta_temporal
    ON public.meta_table (temporal_start, temporal_end);
"""


def init_db() -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(_INIT_SQL)


def insert_record(
    name: str,
    description: str,
    tags: list[str],
    source_type: str,
    ogc_url: str | None,
    ogc_type: str | None,
    is_spatial: bool,
    spatial_type: str | None,
    crs: str,
    footprint_geojson: dict | None,
    temporal_start: Any,
    temporal_end: Any,
    location: str | None,
    filename: str,
    file_size_bytes: int | None,
    file_path: str | None,
) -> str:
    """Insert one row into meta_table and return the generated UUID."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO public.meta_table (
                    name, description, tags,
                    source_type, ogc_url, ogc_type,
                    is_spatial, spatial_type, crs,
                    spatial_footprint,
                    temporal_start, temporal_end,
                    location,
                    filename, file_size_bytes, file_path
                )
                VALUES (
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    CASE WHEN %s IS NOT NULL
                         THEN ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)
                         ELSE NULL END,
                    %s, %s,
                    %s,
                    %s, %s, %s
                )
                RETURNING id
                """,
                (
                    name, description, tags,
                    source_type, ogc_url, ogc_type,
                    is_spatial, spatial_type, crs,
                    json.dumps(footprint_geojson) if footprint_geojson else None,
                    json.dumps(footprint_geojson) if footprint_geojson else None,
                    temporal_start, temporal_end,
                    location,
                    filename, file_size_bytes, file_path,
                ),
            )
            return str(cur.fetchone()[0])


def query_records(
    study_area_geojson: dict | None = None,
    tags: list[str] | None = None,
    source_type: str | None = None,
    is_spatial: bool | None = None,
    temporal_start: Any = None,
    temporal_end: Any = None,
) -> list[dict]:
    """Query meta_table with optional spatial, tag, type and date filters."""
    conditions: list[str] = []
    params: list[Any] = []

    if study_area_geojson:
        conditions.append(
            "spatial_footprint IS NOT NULL AND "
            "ST_Intersects(spatial_footprint, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))"
        )
        params.append(json.dumps(study_area_geojson))

    if tags:
        conditions.append("tags && %s")
        params.append(tags)

    if source_type:
        conditions.append("source_type = %s")
        params.append(source_type)

    if is_spatial is not None:
        conditions.append("is_spatial = %s")
        params.append(is_spatial)

    if temporal_start:
        conditions.append("(temporal_end IS NULL OR temporal_end >= %s)")
        params.append(temporal_start)

    if temporal_end:
        conditions.append("(temporal_start IS NULL OR temporal_start <= %s)")
        params.append(temporal_end)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT
                    id,
                    name,
                    description,
                    tags,
                    source_type,
                    ogc_url,
                    ogc_type,
                    is_spatial,
                    spatial_type,
                    crs,
                    ST_AsGeoJSON(spatial_footprint) AS spatial_footprint,
                    temporal_start,
                    temporal_end,
                    location,
                    filename,
                    file_size_bytes,
                    file_path,
                    uploaded_at
                FROM public.meta_table
                {where}
                ORDER BY uploaded_at DESC
                """,
                params,
            )
            return [dict(r) for r in cur.fetchall()]


def get_all_tags() -> list[str]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT DISTINCT unnest(tags) AS tag FROM public.meta_table ORDER BY tag"
            )
            return [row[0] for row in cur.fetchall()]
