"""
db.py -- data-access layer for the MongoDB warehouse API.

Purpose
-------
This module is the only place that talks to MongoDB. FastAPI routes in main.py
call these functions; they never import pymongo directly.

Why mirror insert_meta / update_meta / delete_meta from the PostGIS db.py?
--------------------------------------------------------------------------
The PostGIS API (datalake/api/db.py) exposes the same function names so that
main.py stays almost identical between backends. Each name maps to one CRUD
operation on the datasource *registry* (the `meta` collection):

  insert_meta   -> CREATE  one registry document when a datasource is registered
  update_meta   -> UPDATE  editable registry fields (name, tags, footprint, ...)
  delete_meta   -> DELETE  registry document AND cascade-delete its data rows
  get_meta_by_id / list_meta -> READ registry documents

MongoDB has no foreign keys, so delete_meta() must manually delete related
documents in the `data` collection (PostGIS does this via ON DELETE CASCADE).

Collections
-----------
  meta  -- one document per registered datasource (+ embedded latest manifest)
  data  -- many flat feature documents, each tagged with dataset_id

Environment
-----------
  MONGO_URI  default mongodb://localhost:27018/  (docker host port)
  MONGO_DB   default datalake
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Any

from pymongo import DESCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------

def get_mongo_uri() -> str:
    return os.getenv("MONGO_URI", "mongodb://localhost:27018/")


def get_db_name() -> str:
    return os.getenv("MONGO_DB", "datalake")


def get_client() -> MongoClient:
    # NOTE: each call opens a new client today. For production, reuse one
    # client for the app lifetime (see lifespan in main.py).
    return MongoClient(get_mongo_uri())


def get_db() -> Database:
    return get_client()[get_db_name()]


def meta_col() -> Collection:
    """Registry collection: datasource metadata + latest ingest manifest."""
    return get_db()["meta"]


def data_col() -> Collection:
    """Feature collection: ingested rows as flat BSON documents."""
    return get_db()["data"]


def init_indexes() -> None:
    """
    Create indexes on startup. Safe to call repeatedly (create_index is idempotent).

    2dsphere indexes are required for $geoIntersects on spatial_footprint / geometry.
    dataset_id index speeds up feature lookups and cascade deletes.
    """
    db = get_db()
    db["meta"].create_index([("spatial_footprint", "2dsphere")], sparse=True)
    db["meta"].create_index("tags")
    db["meta"].create_index("uploaded_at")
    db["data"].create_index("dataset_id")
    db["data"].create_index([("geometry", "2dsphere")], sparse=True)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# Fields stored on meta but returned separately via get_manifest_by_dataset()
_MANIFEST_FIELDS = {"manifest", "manifest_id", "manifest_created_at"}


def _clean(doc: dict | None, *, strip_manifest: bool = False) -> dict | None:
    """
    Convert a MongoDB document into a JSON-friendly API dict.

    - Renames _id -> id (REST clients expect 'id', not Mongo's '_id')
    - Converts datetime values to ISO strings
    - Optionally hides embedded manifest fields from registry responses
    """
    if not doc:
        return None
    out = dict(doc)
    _id = out.pop("_id", None)
    if _id is not None:
        out["id"] = str(_id)
    if strip_manifest:
        for k in _MANIFEST_FIELDS:
            out.pop(k, None)
    for k, v in list(out.items()):
        if isinstance(v, datetime):
            out[k] = v.isoformat()
    return out


# ---------------------------------------------------------------------------
# Registry CRUD  (meta collection)
# ---------------------------------------------------------------------------

def insert_meta(payload: dict) -> str:
    """
    Register a new datasource in the meta collection.

    Called by POST /api/v1/datasources before manifest and features are stored.
    Returns the new dataset_id (string UUID used as MongoDB _id).

    We use string UUIDs as _id so API responses match the PostGIS backend,
    which also returns UUID strings.
    """
    dataset_id = str(uuid.uuid4())
    doc = {
        "_id": dataset_id,
        "name": payload.get("name", ""),
        "description": payload.get("description", ""),
        "tags": payload.get("tags") or [],
        "source_type": payload.get("source_type", "file"),
        "ogc_url": payload.get("ogc_url"),
        "ogc_type": payload.get("ogc_type"),
        "is_spatial": bool(payload.get("is_spatial", False)),
        "spatial_type": payload.get("spatial_type"),
        "crs": payload.get("crs", "EPSG:4326"),
        # GeoJSON Polygon/MultiPolygon -- must stay a dict for 2dsphere queries
        "spatial_footprint": payload.get("spatial_footprint"),
        "temporal_start": payload.get("temporal_start"),
        "temporal_end": payload.get("temporal_end"),
        "location": payload.get("location"),
        "filename": payload.get("filename", ""),
        "file_size_bytes": payload.get("file_size_bytes"),
        "file_path": payload.get("file_path"),
        "uploaded_at": _utcnow(),
        # Manifest slots -- filled later by insert_manifest()
        "manifest": None,
        "manifest_id": None,
        "manifest_created_at": None,
    }
    meta_col().insert_one(doc)
    return dataset_id


def update_meta(dataset_id: str, payload: dict) -> bool:
    """
    Partial update of registry fields (PUT /api/v1/datasources/{id}).

    Only keys in `allowed` are written. Unknown keys in the request body are
    silently ignored -- this is intentional in the simple version; a production
    app would validate and reject unknown fields.
    """
    allowed = {
        "name", "description", "tags", "source_type", "ogc_url", "ogc_type",
        "is_spatial", "spatial_type", "crs", "temporal_start", "temporal_end",
        "location", "filename", "file_size_bytes", "file_path", "spatial_footprint",
    }
    updates = {k: v for k, v in payload.items() if k in allowed}
    if not updates:
        return False
    result = meta_col().update_one({"_id": dataset_id}, {"$set": updates})
    return result.matched_count > 0


def delete_meta(dataset_id: str) -> bool:
    """
    Delete a datasource registry entry and all its ingested data rows.

    PostGIS does this with FOREIGN KEY ... ON DELETE CASCADE.
    MongoDB has no FKs, so we delete from `data` manually here.
    """
    result = meta_col().delete_one({"_id": dataset_id})
    if result.deleted_count:
        data_col().delete_many({"dataset_id": dataset_id})
        return True
    return False


def get_meta_by_id(dataset_id: str) -> dict | None:
    """Return one registry document, without embedded manifest fields."""
    doc = meta_col().find_one({"_id": dataset_id})
    return _clean(doc, strip_manifest=True)


def list_meta(
    tags: list[str] | None = None,
    source_type: str | None = None,
    is_spatial: bool | None = None,
    temporal_start: str | None = None,
    temporal_end: str | None = None,
    footprint_intersects: dict | None = None,
) -> list[dict]:
    """
    List registry documents with optional filters (GET /api/v1/datasources).

    footprint_intersects uses MongoDB $geoIntersects on spatial_footprint.
    Equivalent to PostGIS ST_Intersects(spatial_footprint, polygon).
    """
    query: dict[str, Any] = {}

    if tags:
        query["tags"] = {"$in": tags}
    if source_type:
        query["source_type"] = source_type
    if is_spatial is not None:
        query["is_spatial"] = is_spatial
    if temporal_start:
        query.setdefault("$and", []).append(
            {"$or": [{"temporal_end": None}, {"temporal_end": {"$gte": temporal_start}}]}
        )
    if temporal_end:
        query.setdefault("$and", []).append(
            {"$or": [{"temporal_start": None}, {"temporal_start": {"$lte": temporal_end}}]}
        )
    if footprint_intersects is not None:
        query["spatial_footprint"] = {
            "$geoIntersects": {"$geometry": footprint_intersects}
        }

    cursor = meta_col().find(query).sort("uploaded_at", DESCENDING)
    return [_clean(doc, strip_manifest=True) for doc in cursor]


# ---------------------------------------------------------------------------
# Manifest  (embedded on meta document -- no separate collection)
# ---------------------------------------------------------------------------

def insert_manifest(dataset_id: str, manifest: dict) -> str:
    """
    Store the ingest manifest on the meta document.

    PostGIS keeps manifests in a separate dw_manifests table with history.
    This simple version overwrites the latest manifest on the meta doc only.
    """
    manifest_id = str(uuid.uuid4())
    meta_col().update_one(
        {"_id": dataset_id},
        {"$set": {
            "manifest_id": manifest_id,
            "manifest": manifest,
            "manifest_created_at": _utcnow(),
        }},
    )
    return manifest_id


def get_manifest_by_dataset(dataset_id: str) -> dict | None:
    """Return manifest in the same shape the PostGIS API uses for compatibility."""
    doc = meta_col().find_one(
        {"_id": dataset_id},
        {"manifest_id": 1, "manifest": 1, "manifest_created_at": 1},
    )
    if not doc or not doc.get("manifest"):
        return None
    created = doc.get("manifest_created_at")
    return {
        "id": doc.get("manifest_id"),
        "dataset_id": dataset_id,
        "manifest": doc.get("manifest"),
        "created_at": created.isoformat() if isinstance(created, datetime) else created,
    }


# ---------------------------------------------------------------------------
# Feature rows  (data collection -- flat documents, no attributes JSONB blob)
# ---------------------------------------------------------------------------

def _normalize_row(dataset_id: str, row: dict) -> dict:
    """
    Convert an incoming feature dict into a flat MongoDB document.

    The ingest wizard may send PostGIS-style rows:
      { "id": "...", "geometry": {...}, "attributes": {"name": "A", "area": 1} }

    In MongoDB we flatten attributes to the top level because documents are
    naturally schemaless -- there is no need for a separate JSONB column.
    """
    doc: dict[str, Any] = {
        "dataset_id": dataset_id,
        "loaded_at": _utcnow(),
    }
    if row.get("geometry") is not None:
        doc["geometry"] = row["geometry"]
    if row.get("id") is not None:
        doc["feature_id"] = row["id"]

    attrs = row.get("attributes")
    if isinstance(attrs, dict):
        for k, v in attrs.items():
            if k not in doc:
                doc[k] = v
    else:
        # Already-flat row from a future client
        skip = {"id", "dataset_id", "geometry", "attributes", "loaded_at", "_id"}
        for k, v in row.items():
            if k not in skip:
                doc[k] = v
    return doc


def insert_features(dataset_id: str, rows: list[dict]) -> int:
    """Bulk-insert feature documents linked to dataset_id."""
    if not rows:
        return 0
    docs = [_normalize_row(dataset_id, r) for r in rows]
    data_col().insert_many(docs)
    return len(docs)


def list_features(dataset_id: str, limit: int = 1000) -> list[dict]:
    """Return ingested rows for one datasource."""
    cursor = data_col().find({"dataset_id": dataset_id}).limit(limit)
    out = []
    for doc in cursor:
        row = _clean(doc)
        if row:
            out.append(row)
    return out


def delete_features(dataset_id: str) -> int:
    """Purge all data rows for a datasource (registry entry is kept)."""
    result = data_col().delete_many({"dataset_id": dataset_id})
    return result.deleted_count
