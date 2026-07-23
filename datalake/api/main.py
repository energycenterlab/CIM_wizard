"""
main.py — CIM Datalake FastAPI backend
=======================================
Run:
    DATABASE_URL=postgresql://datalake:datalake@localhost:35432/datalake
    uvicorn main:app --host 0.0.0.0 --port 8008 --reload

Docs:  http://localhost:8000/docs
       http://localhost:8000/redoc

Endpoints
---------
POST   /api/v1/datasources                  Register datasource + store manifest + ingest features
GET    /api/v1/datasources                  List datasources (tags, time, footprint_intersects, …)
GET    /api/v1/datasources/{id}             Get one datasource with its manifest
PUT    /api/v1/datasources/{id}             Update registry fields
DELETE /api/v1/datasources/{id}             Delete datasource + manifest + features

GET    /api/v1/datasources/{id}/features    List ingested feature rows
DELETE /api/v1/datasources/{id}/features    Purge all feature rows for a datasource
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import db


# ── startup ───────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_schema()
    yield


app = FastAPI(
    title="CIM semi Data Warehouse API",
    version="0.1.0",
    description="Warehouse ingest and discovery endpoints for the CIM Data Warehouse.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── helpers ───────────────────────────────────────────────────────────────────

def _serial(obj):
    """Make psycopg2 types JSON-serialisable (dates, UUIDs)."""
    import datetime, uuid
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    if isinstance(obj, uuid.UUID):
        return str(obj)
    raise TypeError(f"Not serialisable: {type(obj)}")


def ok(data, status: int = 200) -> JSONResponse:
    import json
    return JSONResponse(
        content=json.loads(json.dumps(data, default=_serial)),
        status_code=status,
    )


def _require(body: dict, *keys: str):
    missing = [k for k in keys if k not in body or body[k] is None]
    if missing:
        raise HTTPException(422, detail=f"Missing required field(s): {missing}")


# ── POST /api/v1/datasources ──────────────────────────────────────────────────

@app.post("/api/v1/datasources", status_code=201)
async def create_datasource(request: Request):
    """
    Register a new datasource.

    Accepted body (all keys optional except `name`):

        {
          "registry": {
            "name":           "Turin Buildings 2024",    -- required
            "description":    "...",
            "tags":           ["buildings", "urban"],
            "crs":            "EPSG:4326",
            "temporal_start": "2024-01-01",
            "temporal_end":   "2024-12-31"
          },
          "source": {
            "type":      "file",           -- "file" | "ogc" | "api"
            "filename":  "buildings.gpkg",
            "format":    "GeoPackage",
            "ogc_url":   null,
            "ogc_type":  null
          },
          "spatial_footprint": { GeoJSON Polygon or null },
          "datasource_class": {
            "is_spatial":  true,
            "data_class":  "vector",
            "format":      "GeoPackage"
          },
          "manifest": { ...full ingest manifest JSON... },
          "features": [ ...list of warehouse rows... ]
        }

    The response returns the new `dataset_id`, `manifest_id`, and ingested feature count.
    """
    body = await request.json()

    registry = body.get("registry") or {}
    _require(registry, "name")

    source  = body.get("source") or {}
    dc      = body.get("datasource_class") or {}
    fp      = body.get("spatial_footprint")
    manifest = body.get("manifest") or {}
    features = body.get("features") or []

    # ── 1. Insert registry row ─────────────────────────────────────────────
    dataset_id = db.insert_meta({
        "name":           registry.get("name"),
        "description":    registry.get("description", ""),
        "tags":           registry.get("tags", []),
        "source_type":    source.get("type", "file"),
        "ogc_url":        source.get("ogc_url"),
        "ogc_type":       source.get("ogc_type"),
        "is_spatial":     dc.get("is_spatial", False),
        "spatial_type":   (manifest.get("profile") or {}).get("geom_type"),
        "crs":            registry.get("crs", "EPSG:4326"),
        "spatial_footprint": fp,
        "temporal_start": registry.get("temporal_start"),
        "temporal_end":   registry.get("temporal_end"),
        "location":       registry.get("location"),
        "filename":       source.get("filename", ""),
        "file_size_bytes": source.get("file_size_bytes"),
        "file_path":      source.get("file_path"),
        "object_uri":     source.get("object_uri"),
    })

    # ── 2. Store manifest ──────────────────────────────────────────────────
    manifest_id = None
    if manifest:
        manifest["registry_dataset_id"] = dataset_id
        manifest_id = db.insert_manifest(dataset_id, manifest)

    # ── 3. Ingest feature rows ─────────────────────────────────────────────
    feature_count = 0
    if features:
        feature_count = db.insert_features(dataset_id, features)

    return ok({
        "dataset_id":    dataset_id,
        "manifest_id":   manifest_id,
        "feature_count": feature_count,
    }, status=201)


# ── GET /api/v1/datasources ───────────────────────────────────────────────────

@app.get("/api/v1/datasources")
async def list_datasources(
    tags:                 str  | None = Query(None, description="Comma-separated tags filter"),
    source_type:          str  | None = Query(None),
    is_spatial:           bool | None = Query(None),
    temporal_start:       str  | None = Query(None, description="ISO date YYYY-MM-DD"),
    temporal_end:         str  | None = Query(None, description="ISO date YYYY-MM-DD"),
    footprint_intersects: str  | None = Query(
        None,
        description=(
            "GeoJSON Polygon or MultiPolygon (URL-encoded). "
            "Returns datasources whose spatial_footprint intersects this geometry."
        ),
    ),
):
    """
    List datasource registry entries (collection resource).

    All filters are optional and combined with AND. Spatial filtering is expressed
    as a property constraint on `spatial_footprint`, not a separate operation endpoint.

    Example:
      GET /api/v1/datasources?footprint_intersects={"type":"Polygon","coordinates":[[[7.6,45.0],[7.7,45.0],[7.7,45.1],[7.6,45.1],[7.6,45.0]]]}
    """
    import json as _json

    footprint = None
    if footprint_intersects:
        try:
            footprint = _json.loads(footprint_intersects)
        except Exception:
            raise HTTPException(400, detail="footprint_intersects is not valid JSON.")
        if footprint.get("type") not in ("Polygon", "MultiPolygon"):
            raise HTTPException(
                400,
                detail="footprint_intersects must be a GeoJSON Polygon or MultiPolygon.",
            )

    tag_list = [t.strip() for t in tags.split(",")] if tags else None
    rows = db.list_meta(
        tags=tag_list,
        source_type=source_type,
        is_spatial=is_spatial,
        temporal_start=temporal_start,
        temporal_end=temporal_end,
        footprint_intersects=footprint,
    )
    return ok({"count": len(rows), "results": rows})


# ── GET /api/v1/datasources/{id} ─────────────────────────────────────────────

@app.get("/api/v1/datasources/{dataset_id}")
async def get_datasource(dataset_id: str):
    """
    Return a single datasource registry row together with its latest ingest manifest.
    """
    row = db.get_meta_by_id(dataset_id)
    if not row:
        raise HTTPException(404, detail=f"Datasource {dataset_id!r} not found.")
    manifest = db.get_manifest_by_dataset(dataset_id)
    return ok({"datasource": row, "manifest": manifest})


# ── PUT /api/v1/datasources/{id} ─────────────────────────────────────────────

@app.put("/api/v1/datasources/{dataset_id}")
async def update_datasource(dataset_id: str, request: Request):
    """
    Update editable registry fields for a datasource.

    Only fields present in the body are changed. Spatial footprint can be updated
    by including a `spatial_footprint` GeoJSON Polygon.

    Example body:
        {
          "description": "Updated description",
          "tags": ["buildings", "2025"],
          "temporal_end": "2025-12-31",
          "spatial_footprint": { GeoJSON Polygon }
        }
    """
    body = await request.json()
    if not body:
        raise HTTPException(400, detail="Empty request body.")

    updated = db.update_meta(dataset_id, body)
    if not updated:
        raise HTTPException(404, detail=f"Datasource {dataset_id!r} not found or no valid fields.")
    return ok({"updated": dataset_id})


# ── DELETE /api/v1/datasources/{id} ──────────────────────────────────────────

@app.delete("/api/v1/datasources/{dataset_id}")
async def delete_datasource(dataset_id: str):
    """
    Delete a datasource and all associated manifests and feature rows
    (cascaded via FK constraints).
    """
    deleted = db.delete_meta(dataset_id)
    if not deleted:
        raise HTTPException(404, detail=f"Datasource {dataset_id!r} not found.")
    return ok({"deleted": dataset_id})


# ── GET /api/v1/datasources/{id}/features ────────────────────────────────────

@app.get("/api/v1/datasources/{dataset_id}/features")
async def get_features(
    dataset_id: str,
    limit: int = Query(1000, ge=1, le=10000, description="Max rows to return"),
):
    """
    Return ingested feature rows for a datasource in warehouse schema:
    id · dataset_id · geometry (GeoJSON string) · attributes (JSONB) · loaded_at.
    """
    row = db.get_meta_by_id(dataset_id)
    if not row:
        raise HTTPException(404, detail=f"Datasource {dataset_id!r} not found.")
    features = db.list_features(dataset_id, limit=limit)
    return ok({"dataset_id": dataset_id, "count": len(features), "features": features})


# ── DELETE /api/v1/datasources/{id}/features ─────────────────────────────────

@app.delete("/api/v1/datasources/{dataset_id}/features")
async def purge_features(dataset_id: str):
    """Delete all ingested feature rows for a datasource (keeps the registry entry)."""
    row = db.get_meta_by_id(dataset_id)
    if not row:
        raise HTTPException(404, detail=f"Datasource {dataset_id!r} not found.")
    n = db.delete_features(dataset_id)
    return ok({"dataset_id": dataset_id, "deleted_features": n})


# ── health ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return ok({"status": "ok", "db": "connected"})
    except Exception as exc:
        return JSONResponse({"status": "error", "detail": str(exc)}, status_code=503)
