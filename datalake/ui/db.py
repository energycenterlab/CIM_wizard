"""
PostGIS database helpers for the CIM Datalake UI.

DATABASE_URL must be set in .streamlit/secrets.toml  →  [secrets] DATABASE_URL = "..."
or as an environment variable.
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


_INIT_SQL = """
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS datasets (
    id                UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    name              TEXT         NOT NULL,
    description       TEXT         NOT NULL DEFAULT '',
    tags              TEXT[]       NOT NULL DEFAULT '{}',
    spatial_footprint GEOMETRY(POLYGON, 4326),
    temporal_start    DATE,
    temporal_end      DATE,
    data              JSONB,
    filename          TEXT         NOT NULL DEFAULT '',
    uploaded_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_datasets_spatial
    ON datasets USING GIST (spatial_footprint);

CREATE INDEX IF NOT EXISTS idx_datasets_tags
    ON datasets USING GIN (tags);

CREATE INDEX IF NOT EXISTS idx_datasets_temporal
    ON datasets (temporal_start, temporal_end);
"""


def init_db() -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(_INIT_SQL)


def insert_dataset(
    name: str,
    description: str,
    tags: list[str],
    footprint_geojson: dict,
    temporal_start: Any,
    temporal_end: Any,
    data: Any,
    filename: str = "",
) -> str:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO datasets
                    (name, description, tags, spatial_footprint,
                     temporal_start, temporal_end, data, filename)
                VALUES
                    (%s, %s, %s,
                     ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326),
                     %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    name,
                    description,
                    tags,
                    json.dumps(footprint_geojson),
                    temporal_start,
                    temporal_end,
                    json.dumps(data),
                    filename,
                ),
            )
            return str(cur.fetchone()[0])


def query_datasets(
    study_area_geojson: dict | None = None,
    tags: list[str] | None = None,
    temporal_start: Any = None,
    temporal_end: Any = None,
) -> list[dict]:
    conditions: list[str] = []
    params: list[Any] = []

    if study_area_geojson:
        conditions.append(
            "ST_Intersects(spatial_footprint, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))"
        )
        params.append(json.dumps(study_area_geojson))

    if tags:
        conditions.append("tags && %s")
        params.append(tags)

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
                    ST_AsGeoJSON(spatial_footprint) AS spatial_footprint,
                    temporal_start,
                    temporal_end,
                    filename,
                    uploaded_at,
                    data
                FROM datasets
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
                "SELECT DISTINCT unnest(tags) AS tag FROM datasets ORDER BY tag"
            )
            return [row[0] for row in cur.fetchall()]
