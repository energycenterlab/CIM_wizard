"""
db.py — raw psycopg2 helpers shared by the FastAPI backend.

DATABASE_URL must be set as an environment variable:
  export DATABASE_URL="postgresql://datalake:datalake@localhost:35432/datalake"
"""
from __future__ import annotations

import json
import os
from contextlib import contextmanager
from typing import Any

import psycopg2
import psycopg2.extras


def get_db_url() -> str:
    url = os.getenv("DATABASE_URL", "")
    if not url:
        raise RuntimeError("DATABASE_URL environment variable is not set.")
    return url


@contextmanager
def get_conn():
    conn = psycopg2.connect(get_db_url())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ── DDL ───────────────────────────────────────────────────────────────────────
# New tables that extend the existing 01_init.sql schema.
# Safe to call on every startup (all statements use IF NOT EXISTS).

EXTRA_DDL = """
CREATE EXTENSION IF NOT EXISTS postgis;

-- Stores the full ingest manifest JSON for each datasource load.
CREATE TABLE IF NOT EXISTS public.dw_manifests (
    id           UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id   UUID         REFERENCES public.meta_table(id) ON DELETE CASCADE,
    manifest     JSONB        NOT NULL,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dw_manifests_dataset
    ON public.dw_manifests (dataset_id);

-- Stores ingested feature rows in warehouse schema:
--   id (surrogate PK), dataset_id (FK), geometry, attributes JSONB.
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
"""


def init_schema() -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(EXTRA_DDL)


# ── meta_table helpers ────────────────────────────────────────────────────────

def insert_meta(payload: dict) -> str:
    """Insert a row into meta_table from a flat dict. Returns the UUID string."""
    fp = payload.get("spatial_footprint")
    fp_json = json.dumps(fp) if isinstance(fp, dict) else fp

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO public.meta_table (
                    name, description, tags, source_type,
                    ogc_url, ogc_type, is_spatial, spatial_type, crs,
                    spatial_footprint, temporal_start, temporal_end,
                    location, filename, file_size_bytes, file_path
                )
                VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    CASE WHEN %s IS NOT NULL
                         THEN ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)
                         ELSE NULL END,
                    %s, %s, %s, %s, %s, %s
                )
                RETURNING id
                """,
                (
                    payload.get("name", ""),
                    payload.get("description", ""),
                    payload.get("tags", []),
                    payload.get("source_type", "file"),
                    payload.get("ogc_url"),
                    payload.get("ogc_type"),
                    payload.get("is_spatial", False),
                    payload.get("spatial_type"),
                    payload.get("crs", "EPSG:4326"),
                    fp_json, fp_json,
                    payload.get("temporal_start"),
                    payload.get("temporal_end"),
                    payload.get("location"),
                    payload.get("filename", ""),
                    payload.get("file_size_bytes"),
                    payload.get("file_path"),
                ),
            )
            return str(cur.fetchone()[0])


def update_meta(dataset_id: str, payload: dict) -> bool:
    """Update editable fields of a meta_table row. Returns True if a row was updated."""
    allowed = {
        "name", "description", "tags", "source_type", "ogc_url", "ogc_type",
        "is_spatial", "spatial_type", "crs", "temporal_start", "temporal_end",
        "location", "filename", "file_size_bytes", "file_path",
    }
    updates = {k: v for k, v in payload.items() if k in allowed}
    if not updates:
        return False

    fp = payload.get("spatial_footprint")
    sets = [f"{k} = %s" for k in updates]
    vals = list(updates.values())

    if fp:
        sets.append("spatial_footprint = ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)")
        vals.append(json.dumps(fp) if isinstance(fp, dict) else fp)

    vals.append(dataset_id)

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE public.meta_table SET {', '.join(sets)} WHERE id = %s",
                vals,
            )
            return cur.rowcount > 0


def delete_meta(dataset_id: str) -> bool:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM public.meta_table WHERE id = %s", (dataset_id,))
            return cur.rowcount > 0


def get_meta_by_id(dataset_id: str) -> dict | None:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, name, description, tags, source_type,
                       ogc_url, ogc_type, is_spatial, spatial_type, crs,
                       ST_AsGeoJSON(spatial_footprint) AS spatial_footprint,
                       temporal_start, temporal_end, location,
                       filename, file_size_bytes, file_path, uploaded_at
                FROM public.meta_table WHERE id = %s
                """,
                (dataset_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None


def list_meta(
    tags: list[str] | None = None,
    source_type: str | None = None,
    is_spatial: bool | None = None,
    temporal_start: str | None = None,
    temporal_end: str | None = None,
    footprint_intersects: dict | None = None,
) -> list[dict]:
    conditions: list[str] = []
    params: list[Any] = []

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
    if footprint_intersects is not None:
        conditions.append(
            "spatial_footprint IS NOT NULL AND ST_Intersects("
            "spatial_footprint, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))"
        )
        params.append(json.dumps(footprint_intersects))

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT id, name, description, tags, source_type,
                       ogc_url, ogc_type, is_spatial, spatial_type, crs,
                       ST_AsGeoJSON(spatial_footprint) AS spatial_footprint,
                       temporal_start, temporal_end, location,
                       filename, file_size_bytes, file_path, uploaded_at
                FROM public.meta_table {where}
                ORDER BY uploaded_at DESC
                """,
                params,
            )
            return [dict(r) for r in cur.fetchall()]


# ── manifest helpers ──────────────────────────────────────────────────────────

def insert_manifest(dataset_id: str, manifest: dict) -> str:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO public.dw_manifests (dataset_id, manifest) VALUES (%s, %s) RETURNING id",
                (dataset_id, json.dumps(manifest)),
            )
            return str(cur.fetchone()[0])


def get_manifest_by_dataset(dataset_id: str) -> dict | None:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT id, dataset_id, manifest, created_at FROM public.dw_manifests "
                "WHERE dataset_id = %s ORDER BY created_at DESC LIMIT 1",
                (dataset_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None


# ── feature helpers ───────────────────────────────────────────────────────────

def insert_features(dataset_id: str, rows: list[dict]) -> int:
    """
    Bulk-insert warehouse feature rows.
    Each row must have: attributes (dict), optionally geometry (GeoJSON dict).
    Returns count of inserted rows.
    """
    if not rows:
        return 0
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Build individual INSERT statements to handle the CASE expression cleanly.
            for r in rows:
                geom_json = json.dumps(r["geometry"]) if r.get("geometry") else None
                cur.execute(
                    """
                    INSERT INTO public.dw_features (dataset_id, geometry, attributes)
                    VALUES (
                        %s,
                        CASE WHEN %s IS NOT NULL
                             THEN ST_GeomFromGeoJSON(%s)
                             ELSE NULL END,
                        %s
                    )
                    """,
                    (dataset_id, geom_json, geom_json, json.dumps(r.get("attributes") or {})),
                )
            return len(rows)


def list_features(dataset_id: str, limit: int = 1000) -> list[dict]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, dataset_id,
                       ST_AsGeoJSON(geometry) AS geometry,
                       attributes, loaded_at
                FROM public.dw_features
                WHERE dataset_id = %s
                ORDER BY loaded_at
                LIMIT %s
                """,
                (dataset_id, limit),
            )
            return [dict(r) for r in cur.fetchall()]


def delete_features(dataset_id: str) -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM public.dw_features WHERE dataset_id = %s", (dataset_id,)
            )
            return cur.rowcount
