import json
import os
import sys

# Make `models/` importable regardless of where the script is invoked from
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pymongo import MongoClient

from models.datasource import new_datasource_item

MONGO_URI = "mongodb://localhost:27018/"
DB_NAME   = "datalake"


# ── Coordinate / bbox helpers ──────────────────────────────────────────────

def _iter_coords(obj):
    """Recursively yield [lon, lat] pairs from any GeoJSON coordinates value."""
    if isinstance(obj, list):
        if obj and isinstance(obj[0], (int, float)):
            yield obj[0], obj[1]
        else:
            for item in obj:
                yield from _iter_coords(item)


def _compute_bbox(features: list[dict]) -> list[float] | None:
    lons, lats = [], []
    for feat in features:
        geom = (feat.get("geometry") or {})
        for lon, lat in _iter_coords(geom.get("coordinates", [])):
            lons.append(lon)
            lats.append(lat)
    return [min(lons), min(lats), max(lons), max(lats)] if lons else None


def _detect_geo_type(features: list[dict]) -> str | None:
    for feat in features:
        geom = feat.get("geometry") or {}
        if geom.get("type"):
            return geom["type"]
    return None


# ── Main ingestion function ────────────────────────────────────────────────

def load_geojson(
    file_path: str,
    name: str | None = None,
    description: str = "",
    collection: str = "default",
    tags: list[str] | None = None,
) -> str:
    """
    Load a GeoJSON file into MongoDB.

    - `datasources` collection receives one STAC Item (metadata).
    - `geodata`     collection receives all features, each tagged with
                    `datasource_id` for back-referencing.

    Returns the datasource _id (= STAC item id).
    """
    name      = name or os.path.splitext(os.path.basename(file_path))[0]
    file_size = os.path.getsize(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        geojson = json.load(f)

    # Normalise to a flat feature list
    gtype = geojson.get("type")
    if gtype == "FeatureCollection":
        features = geojson.get("features", [])
    elif gtype == "Feature":
        features = [geojson]
    else:
        # Plain geometry — wrap it
        features = [{"type": "Feature", "geometry": geojson, "properties": {}}]

    bbox     = geojson.get("bbox") or _compute_bbox(features)
    geo_type = _detect_geo_type(features)

    # Build the STAC datasource item
    item = new_datasource_item(
        name=name,
        description=description,
        source_type="file",
        data_type="geojson",
        is_geo=True,
        file_path=os.path.abspath(file_path),
        crs="EPSG:4326",
        bbox=bbox,
        geo_type=geo_type,
        collection=collection,
        tags=tags,
        file_size_bytes=file_size,
    )
    datasource_id = item.id

    # Tag every feature so it can be queried back to its datasource
    enriched = [{**feat, "datasource_id": datasource_id} for feat in features]

    client = MongoClient(MONGO_URI)
    db     = client[DB_NAME]

    if enriched:
        geo_result = db["geodata"].insert_many(enriched)
        item.mongo_meta.feature_count = len(geo_result.inserted_ids)

    db["datasources"].insert_one(item.to_mongo())
    client.close()

    print(
        f"[datalake] '{name}' ingested — "
        f"{len(enriched)} features | datasource_id={datasource_id}"
    )
    return datasource_id


# ── CLI entry point ────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python datalake.py <path_to_geojson> [name] [description]")
        sys.exit(1)

    load_geojson(
        file_path=sys.argv[1],
        name=sys.argv[2]        if len(sys.argv) > 2 else None,
        description=sys.argv[3] if len(sys.argv) > 3 else "",
    )
