"""
Upload page — register a new dataset in the datalake.

Two source modes:
  - File : upload a file via FTP; metadata stored in meta_table.
  - OGC  : register a WFS / WMS / WCS / WMTS service URL.

Bounding box is entered manually or calculated from an uploaded GeoJSON file.
"""
from __future__ import annotations

import datetime
import json
import os
import sys
from typing import Iterator

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import insert_record  # noqa: E402
from ftp import is_configured, upload  # noqa: E402

st.set_page_config(page_title="Upload — CIM Datalake", layout="wide")

ACCEPTED_EXTENSIONS = [
    "geojson", "json", "csv", "gpkg", "shp", "zip",
    "tif", "tiff", "nc", "hdf5", "h5", "ifc",
]
GEOM_TYPES = [
    "Point", "MultiPoint", "LineString", "MultiLineString",
    "Polygon", "MultiPolygon", "GeometryCollection", "Raster", "Unknown",
]
OGC_TYPES = ["WFS", "WMS", "WCS", "WMTS", "OGC API - Features", "OGC API - Maps"]


# ── Bbox helpers ─────────────────────────────────────────────────────────────

def _iter_coords(obj) -> Iterator[tuple[float, float]]:
    """Recursively yield (lon, lat) pairs from any GeoJSON coordinates value."""
    if isinstance(obj, list):
        if obj and isinstance(obj[0], (int, float)):
            yield float(obj[0]), float(obj[1])
        else:
            for item in obj:
                yield from _iter_coords(item)


def _bbox_from_geojson(data: dict) -> tuple[float, float, float, float] | None:
    """Return (xmin, ymin, xmax, ymax) from any GeoJSON object, or None."""
    lons: list[float] = []
    lats: list[float] = []

    geom_type = data.get("type")
    if geom_type == "FeatureCollection":
        features = data.get("features", [])
    elif geom_type == "Feature":
        features = [data]
    else:
        features = [{"type": "Feature", "geometry": data, "properties": {}}]

    for feat in features:
        geom = feat.get("geometry") or {}
        for lon, lat in _iter_coords(geom.get("coordinates", [])):
            lons.append(lon)
            lats.append(lat)

    if not lons:
        return None
    return min(lons), min(lats), max(lons), max(lats)


def _bbox_to_polygon(xmin: float, ymin: float, xmax: float, ymax: float) -> dict:
    return {
        "type": "Polygon",
        "coordinates": [[
            [xmin, ymin], [xmax, ymin], [xmax, ymax],
            [xmin, ymax], [xmin, ymin],
        ]],
    }


# ── Session state ─────────────────────────────────────────────────────────────
# Keys prefixed with "_val_" are plain storage, not widget keys.
# This avoids the Streamlit restriction against modifying a session_state key
# that is bound to a rendered widget.
for _k, _v in [
    ("_val_xmin", 0.0), ("_val_ymin", 0.0),
    ("_val_xmax", 0.0), ("_val_ymax", 0.0),
    ("bbox_set",  False),
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── Page header ───────────────────────────────────────────────────────────────
st.title("Upload Dataset")
st.caption(
    "Register a dataset in the datalake. "
    "Choose File to upload a file to the server, or OGC to register a service endpoint."
)

# ── Source type ───────────────────────────────────────────────────────────────
source_type = st.radio(
    "Source type",
    options=["File", "OGC"],
    horizontal=True,
)
source_type_key = source_type.lower()

st.divider()

# ── Source input ──────────────────────────────────────────────────────────────
uploaded_file = None
file_bytes: bytes | None = None
ogc_url = ""
ogc_type: str | None = None

if source_type_key == "file":
    col_file, col_ftp = st.columns([3, 2])
    with col_file:
        uploaded_file = st.file_uploader(
            "Dataset file *",
            type=ACCEPTED_EXTENSIONS,
            help="Any spatial or non-spatial file. It will be transferred to the FTP server.",
        )
    with col_ftp:
        if is_configured():
            st.success("FTP server is configured.")
        else:
            st.warning(
                "FTP not configured — metadata will be saved but file will not be transferred. "
                "Add [ftp] to .streamlit/secrets.toml."
            )
    if uploaded_file:
        file_bytes = uploaded_file.read()
        st.caption(f"{uploaded_file.name} — {len(file_bytes) / 1024:.1f} KB")
else:
    col_url, col_type = st.columns([3, 1])
    with col_url:
        ogc_url = st.text_input(
            "OGC service URL *",
            placeholder="https://example.com/geoserver/wfs?service=WFS&request=GetCapabilities",
        )
    with col_type:
        ogc_type = st.selectbox("Service type", OGC_TYPES)

st.divider()

# ── Metadata ──────────────────────────────────────────────────────────────────
col_name, col_tags = st.columns([3, 2])
with col_name:
    name = st.text_input("Name *", placeholder="e.g. Turin Building Footprints 2024")
with col_tags:
    tags_raw = st.text_input("Tags (comma-separated)", placeholder="buildings, urban, 2024")

description = st.text_area(
    "Description",
    placeholder="Source, content, methodology, known limitations",
    height=90,
)

col_loc, col_crs = st.columns([3, 1])
with col_loc:
    location = st.text_input("Location", placeholder="e.g. Turin, Piedmont, Italy")
with col_crs:
    crs = st.text_input("CRS", value="EPSG:4326")

col_t1, col_t2 = st.columns(2)
with col_t1:
    temporal_start = st.date_input("Temporal start", value=None)
with col_t2:
    temporal_end = st.date_input("Temporal end", value=None)

st.divider()

# ── Spatial properties ────────────────────────────────────────────────────────
col_sp, col_gt = st.columns([1, 2])
with col_sp:
    is_spatial = st.checkbox("Spatial dataset", value=True)
with col_gt:
    spatial_type = st.selectbox("Geometry type", GEOM_TYPES) if is_spatial else None

# Bounding box — shown only for spatial datasets
if is_spatial:
    st.markdown("**Bounding box** (EPSG:4326 — decimal degrees)")
    st.caption(
        "The bbox is stored as EPSG:4326 (decimal degrees). "
        "The 'Calculate from file' button reads raw coordinates from the GeoJSON "
        "without reprojection. If your file uses a projected CRS (e.g. UTM / EPSG:32632), "
        "reproject it to EPSG:4326 before uploading, or enter the bbox manually in degrees."
    )

    col_xmin, col_ymin, col_xmax, col_ymax, col_calc = st.columns([2, 2, 2, 2, 2])

    with col_xmin:
        xmin = st.number_input("West (xmin)",  value=st.session_state._val_xmin, format="%.6f")
    with col_ymin:
        ymin = st.number_input("South (ymin)", value=st.session_state._val_ymin, format="%.6f")
    with col_xmax:
        xmax = st.number_input("East (xmax)",  value=st.session_state._val_xmax, format="%.6f")
    with col_ymax:
        ymax = st.number_input("North (ymax)", value=st.session_state._val_ymax, format="%.6f")

    with col_calc:
        st.write("")
        st.write("")
        calc_btn = st.button(
            "Calculate from file",
            use_container_width=True,
            help="Parse the uploaded GeoJSON and fill the bbox automatically.",
            disabled=(file_bytes is None),
        )

    if calc_btn and file_bytes:
        try:
            data = json.loads(file_bytes)
            result = _bbox_from_geojson(data)
            if result:
                st.session_state._val_xmin = result[0]
                st.session_state._val_ymin = result[1]
                st.session_state._val_xmax = result[2]
                st.session_state._val_ymax = result[3]
                st.session_state.bbox_set  = True
                st.rerun()
            else:
                st.warning("No coordinates found in the uploaded file.")
        except json.JSONDecodeError:
            st.warning("Uploaded file is not valid JSON — cannot calculate bbox.")

    if st.session_state.bbox_set:
        st.caption(
            f"Bbox calculated from file: "
            f"({st.session_state._val_xmin:.4f}, {st.session_state._val_ymin:.4f}, "
            f"{st.session_state._val_xmax:.4f}, {st.session_state._val_ymax:.4f})"
        )
else:
    xmin = ymin = xmax = ymax = 0.0

st.divider()

# ── Submit ────────────────────────────────────────────────────────────────────
submit = st.button("Register dataset", type="primary", use_container_width=True)

if submit:
    errors: list[str] = []

    if not name.strip():
        errors.append("Dataset name is required.")
    if source_type_key == "file" and not uploaded_file:
        errors.append("A file must be selected for source type File.")
    if source_type_key == "ogc" and not ogc_url.strip():
        errors.append("An OGC service URL is required for source type OGC.")
    if temporal_start and temporal_end and temporal_start > temporal_end:
        errors.append("Temporal start must be on or before temporal end.")

    if errors:
        for err in errors:
            st.error(err)
    else:
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        ftp_path: str | None = None
        stored_filename = ""
        stored_size: int | None = None

        # Build footprint polygon from bbox when dataset is spatial
        footprint: dict | None = None
        if is_spatial and not (xmin == ymin == xmax == ymax == 0.0):
            footprint = _bbox_to_polygon(xmin, ymin, xmax, ymax)

        try:
            if source_type_key == "file" and file_bytes is not None:
                stored_filename = uploaded_file.name
                stored_size = len(file_bytes)
                if is_configured():
                    today = datetime.date.today()
                    subdir = f"{today.year}/{today.month:02d}/{today.day:02d}"
                    ftp_path = upload(file_bytes, stored_filename, subdir=subdir)

            record_id = insert_record(
                name=name.strip(),
                description=description.strip(),
                tags=tags,
                source_type=source_type_key,
                ogc_url=ogc_url.strip() or None,
                ogc_type=ogc_type if source_type_key == "ogc" else None,
                is_spatial=is_spatial,
                spatial_type=spatial_type if is_spatial else None,
                crs=crs.strip() or "EPSG:4326",
                footprint_geojson=footprint,
                temporal_start=temporal_start or None,
                temporal_end=temporal_end or None,
                location=location.strip() or None,
                filename=stored_filename,
                file_size_bytes=stored_size,
                file_path=ftp_path,
            )

            st.success(f"Dataset registered. ID: `{record_id}`")
            if ftp_path:
                st.caption(f"File stored at: {ftp_path}")

            # Reset bbox storage for next upload
            for _k in ("_val_xmin", "_val_ymin", "_val_xmax", "_val_ymax"):
                st.session_state[_k] = 0.0
            st.session_state.bbox_set = False

        except Exception as exc:
            st.error(f"Registration failed: {exc}")
