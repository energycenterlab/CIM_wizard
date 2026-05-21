from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ── GeoJSON primitives ─────────────────────────────────────────────────────

class GeoJSONGeometry(BaseModel):
    type: str
    coordinates: Any


# ── STAC sub-models ────────────────────────────────────────────────────────

class STACAsset(BaseModel):
    href: str
    type: str
    roles: list[str]
    title: str


class STACLink(BaseModel):
    rel: str
    href: str
    type: str


class DatalakeProperties(BaseModel):
    """STAC `properties` block with a custom `dl4r:` extension namespace."""

    model_config = ConfigDict(populate_by_name=True)

    # STAC required
    datetime: datetime
    created: datetime
    updated: datetime
    title: str
    description: str
    license: str = "proprietary"
    providers: list[Any] = Field(default_factory=list)

    # dl4r custom extension — aliases carry the namespaced key to MongoDB
    source_type: str            = Field(alias="dl4r:source_type")   # "file" | "api" | "ogc"
    data_type: str              = Field(alias="dl4r:data_type")     # "geojson" | "vector" | ...
    is_geo: bool                = Field(alias="dl4r:is_geo")
    geo_type: Optional[str]     = Field(None,    alias="dl4r:geo_type")      # "Point" | "Polygon" | ...
    crs: Optional[str]          = Field(None,    alias="dl4r:crs")           # "EPSG:4326"
    location: Optional[str]     = Field(None,    alias="dl4r:location")      # "Turin, Italy"
    ingested: bool              = Field(False,   alias="dl4r:ingested")
    dl4r_collection: str        = Field("default", alias="dl4r:collection")  # logical grouping
    tags: list[str]             = Field(default_factory=list, alias="dl4r:tags")
    file_size_bytes: Optional[int] = Field(None, alias="dl4r:file_size_bytes")


class MongoMeta(BaseModel):
    """Internal MongoDB bookkeeping — not part of the STAC spec."""

    geodata_collection: str = "geodata"
    feature_count: Optional[int] = None


class STACItem(BaseModel):
    """
    STAC 1.0 Item aligned with the datalake4raw (dl4r) extension.
    Stored in the `datasources` MongoDB collection.
    The document `_id` equals the STAC item `id`.
    """

    model_config = ConfigDict(populate_by_name=True)

    stac_version: str           = "1.0.0"
    stac_extensions: list[str]  = Field(default_factory=list)
    type: Literal["Feature"]    = "Feature"
    id: str                     = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    geometry: Optional[GeoJSONGeometry] = None
    bbox: Optional[list[float]] = None
    properties: DatalakeProperties
    assets: dict[str, STACAsset] = Field(default_factory=dict)
    links: list[STACLink]       = Field(default_factory=list)
    mongo_meta: MongoMeta       = Field(default_factory=MongoMeta, alias="_mongo")

    @model_validator(mode="after")
    def _build_geometry_from_bbox(self) -> STACItem:
        """Auto-derive a bounding-box polygon geometry when only bbox is provided."""
        if self.bbox and self.geometry is None:
            xmin, ymin, xmax, ymax = self.bbox
            self.geometry = GeoJSONGeometry(
                type="Polygon",
                coordinates=[[
                    [xmin, ymin], [xmax, ymin], [xmax, ymax],
                    [xmin, ymax], [xmin, ymin],   # closed ring
                ]],
            )
        return self

    def to_mongo(self) -> dict:
        """Return a MongoDB-ready dict: aliased keys, JSON-serializable values."""
        return self.model_dump(by_alias=True, mode="json")


# ── Lookup tables ──────────────────────────────────────────────────────────

_MEDIA_TYPES: dict[str, str] = {
    "vector":  "application/octet-stream",
    "raster":  "image/tiff; application=geotiff",
    "csv":     "text/csv",
    "geojson": "application/geo+json",
    "json":    "application/json",
    "ifc":     "application/x-step",
    "hdf5":    "application/x-hdf5",
    "wfs":     "application/json",
    "wms":     "image/png",
    "wcs":     "image/tiff; application=geotiff",
}

_STAC_EXTENSIONS: dict[str, list[str]] = {
    "raster": ["https://stac-extensions.github.io/eo/v1.0.0/schema.json"],
}


def media_type(data_type: str) -> str:
    return _MEDIA_TYPES.get(data_type, "application/octet-stream")


def stac_extensions_for(data_type: str) -> list[str]:
    return _STAC_EXTENSIONS.get(data_type, [])


# ── Factory ────────────────────────────────────────────────────────────────

def new_datasource_item(
    name: str,
    description: str,
    source_type: str,
    data_type: str,
    is_geo: bool,
    file_path: Optional[str] = None,
    api_url: Optional[str] = None,
    crs: Optional[str] = None,
    bbox: Optional[list[float]] = None,
    geo_type: Optional[str] = None,
    location: Optional[str] = None,
    collection: str = "default",
    tags: Optional[list[str]] = None,
    file_size_bytes: Optional[int] = None,
) -> STACItem:
    item_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    assets: dict[str, STACAsset] = {}
    if file_path:
        assets["data"] = STACAsset(
            href=file_path,
            type=media_type(data_type),
            roles=["data"],
            title=name,
        )
    if api_url:
        assets["service"] = STACAsset(
            href=api_url,
            type=media_type(data_type),
            roles=["data"],
            title=name,
        )

    links = [
        STACLink(rel="self",     href=f"/datasources/{item_id}",          type="application/geo+json"),
        STACLink(rel="collection", href=f"/collections/{collection}",     type="application/json"),
        STACLink(rel="download", href=f"/datasources/{item_id}/download", type="application/octet-stream"),
        STACLink(rel="data",     href=f"/datasources/{item_id}/data",     type="application/geo+json"),
    ]

    props = DatalakeProperties.model_validate({
        "datetime":              now.isoformat(),
        "created":               now.isoformat(),
        "updated":               now.isoformat(),
        "title":                 name,
        "description":           description,
        "dl4r:source_type":      source_type,
        "dl4r:data_type":        data_type,
        "dl4r:is_geo":           is_geo,
        "dl4r:geo_type":         geo_type,
        "dl4r:crs":              crs,
        "dl4r:location":         location,
        "dl4r:collection":       collection,
        "dl4r:tags":             tags or [],
        "dl4r:file_size_bytes":  file_size_bytes,
    })

    return STACItem(
        id=item_id,
        stac_extensions=stac_extensions_for(data_type),
        bbox=bbox,
        properties=props,
        assets=assets,
        links=links,
    )
