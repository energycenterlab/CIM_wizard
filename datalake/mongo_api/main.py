"""
main.py -- CIM Datalake FastAPI backend (MongoDB)

Architecture (two layers)
-------------------------
  main.py  -> HTTP routes only (parse request, call db.*, return JSON)
  db.py    -> MongoDB access only (no FastAPI imports)

This mirrors datalake/api/ (PostGIS version) so both backends share the same
REST contract and can be swapped without changing the Streamlit ingest UI.

Run
---
    export MONGO_URI="mongodb://localhost:27018/"
    export MONGO_DB="datalake"
    uvicorn main:app --host 0.0.0.0 --port 8001 --reload

Collections
-----------
    meta  -- datasource registry + latest ingest manifest
    data  -- ingested rows (flat documents; geometry + fields at top level)

Endpoints
---------
    POST   /api/v1/datasources
    GET    /api/v1/datasources
    GET    /api/v1/datasources/{id}
    PUT    /api/v1/datasources/{id}
    DELETE /api/v1/datasources/{id}
    GET    /api/v1/datasources/{id}/features
    DELETE /api/v1/datasources/{id}/features
    GET    /health

Minimum-standard improvements (not implemented here -- see module docstring in db.py)
------------------------------------------------------------------------------------
    1. Pydantic models for request/response bodies (replaces raw dict + _require)
    2. Reuse one MongoClient in app lifespan instead of per-call get_client()
    3. Structured logging (not print / bare except)
    4. pytest + httpx test client for each endpoint
    5. .env loading via pydantic-settings
    6. Pagination on list endpoints (skip/limit)
    7. Auth middleware if exposed beyond localhost
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import date, datetime
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure indexes exist. Shutdown: close shared client (future improvement).
    db.init_indexes()
    yield


app = FastAPI(
    title="CIM Datalake API (MongoDB)",
    version="0.1.0",
    description="Warehouse ingest and discovery endpoints backed by MongoDB.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Response helpers
# ---------------------------------------------------------------------------

def _serial(obj):
    """json.dumps default= handler for datetime and UUID values from MongoDB."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    raise TypeError(f"Not serialisable: {type(obj)}")


def ok(data, status: int = 200) -> JSONResponse:
    return JSONResponse(
        content=__import__("json").loads(__import__("json").dumps(data, default=_serial)),
        status_code=status,
    )


def _require(body: dict, *keys: str):
    """Minimal required-field check. Replace with Pydantic models later."""
    missing = [k for k in keys if k not in body or body[k] is None]
    if missing:
        raise HTTPException(422, detail=f"Missing required field(s): {missing}")


# ---------------------------------------------------------------------------
# Datasource registry
# ---------------------------------------------------------------------------

@app.post("/api/v1/datasources", status_code=201)
async def create_datasource(request: Request):
    """
    Register datasource + store manifest + ingest feature rows in one call.

    Three-step flow inside db layer (same as PostGIS backend):
      1. insert_meta()      -> registry document in meta collection
      2. insert_manifest()  -> embed manifest on meta document
      3. insert_features()  -> flat rows in data collection
    """
    body = await request.json()

    registry = body.get("registry") or {}
    _require(registry, "name")

    source = body.get("source") or {}
    dc = body.get("datasource_class") or {}
    fp = body.get("spatial_footprint")
    manifest = body.get("manifest") or {}
    features = body.get("features") or []

    dataset_id = db.insert_meta({
        "name": registry.get("name"),
        "description": registry.get("description", ""),
        "tags": registry.get("tags", []),
        "source_type": source.get("type", "file"),
        "ogc_url": source.get("ogc_url"),
        "ogc_type": source.get("ogc_type"),
        "is_spatial": dc.get("is_spatial", False),
        "spatial_type": (manifest.get("profile") or {}).get("geom_type"),
        "crs": registry.get("crs", "EPSG:4326"),
        "spatial_footprint": fp,
        "temporal_start": registry.get("temporal_start"),
        "temporal_end": registry.get("temporal_end"),
        "location": registry.get("location"),
        "filename": source.get("filename", ""),
        "file_size_bytes": None,
        "file_path": source.get("file_path"),
    })

    manifest_id = None
    if manifest:
        manifest["registry_dataset_id"] = dataset_id
        manifest_id = db.insert_manifest(dataset_id, manifest)

    feature_count = db.insert_features(dataset_id, features) if features else 0

    return ok({
        "dataset_id": dataset_id,
        "manifest_id": manifest_id,
        "feature_count": feature_count,
    }, status=201)


@app.get("/api/v1/datasources")
async def list_datasources(
    tags: str | None = Query(None),
    source_type: str | None = Query(None),
    is_spatial: bool | None = Query(None),
    temporal_start: str | None = Query(None),
    temporal_end: str | None = Query(None),
    footprint_intersects: str | None = Query(
        None,
        description="URL-encoded GeoJSON Polygon/MultiPolygon filter on spatial_footprint",
    ),
):
    """Collection resource with optional filters (RESTful -- no operation-style paths)."""
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


@app.get("/api/v1/datasources/{dataset_id}")
async def get_datasource(dataset_id: str):
    """Return registry row + latest manifest as separate objects."""
    row = db.get_meta_by_id(dataset_id)
    if not row:
        raise HTTPException(404, detail=f"Datasource {dataset_id!r} not found.")
    manifest = db.get_manifest_by_dataset(dataset_id)
    return ok({"datasource": row, "manifest": manifest})


@app.put("/api/v1/datasources/{dataset_id}")
async def update_datasource(dataset_id: str, request: Request):
    """Partial update of registry fields only (not features or manifest)."""
    body = await request.json()
    if not body:
        raise HTTPException(400, detail="Empty request body.")
    updated = db.update_meta(dataset_id, body)
    if not updated:
        raise HTTPException(404, detail=f"Datasource {dataset_id!r} not found or no valid fields.")
    return ok({"updated": dataset_id})


@app.delete("/api/v1/datasources/{dataset_id}")
async def delete_datasource(dataset_id: str):
    """Delete registry entry and cascade-delete all data rows."""
    deleted = db.delete_meta(dataset_id)
    if not deleted:
        raise HTTPException(404, detail=f"Datasource {dataset_id!r} not found.")
    return ok({"deleted": dataset_id})


# ---------------------------------------------------------------------------
# Feature sub-resource  (/datasources/{id}/features)
# ---------------------------------------------------------------------------

@app.get("/api/v1/datasources/{dataset_id}/features")
async def get_features(
    dataset_id: str,
    limit: int = Query(1000, ge=1, le=10000),
):
    """List ingested rows. Documents are flat (no nested attributes blob)."""
    row = db.get_meta_by_id(dataset_id)
    if not row:
        raise HTTPException(404, detail=f"Datasource {dataset_id!r} not found.")
    features = db.list_features(dataset_id, limit=limit)
    return ok({"dataset_id": dataset_id, "count": len(features), "features": features})


@app.delete("/api/v1/datasources/{dataset_id}/features")
async def purge_features(dataset_id: str):
    """Remove all data rows; keep the datasource registry entry."""
    row = db.get_meta_by_id(dataset_id)
    if not row:
        raise HTTPException(404, detail=f"Datasource {dataset_id!r} not found.")
    n = db.delete_features(dataset_id)
    return ok({"dataset_id": dataset_id, "deleted_features": n})


# ---------------------------------------------------------------------------
# Ops
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    try:
        db.get_client().admin.command("ping")
        return ok({"status": "ok", "db": "connected", "backend": "mongodb"})
    except Exception as exc:
        return JSONResponse({"status": "error", "detail": str(exc)}, status_code=503)
