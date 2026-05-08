"""
Upload page — register a new dataset in the datalake.

Two source modes:
  - File   : upload a file via FTP; metadata stored in meta_table.
  - OGC    : register a WFS / WMS / WCS / WMTS service URL.

Both modes share the same metadata fields and the optional spatial footprint map.
"""
from __future__ import annotations

import datetime
import os
import sys

import folium
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import st_folium

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import insert_record  # noqa: E402
from ftp import is_configured, upload  # noqa: E402

st.set_page_config(page_title="Upload Dataset", layout="wide")

ACCEPTED_EXTENSIONS = [
    "geojson", "json", "csv", "gpkg", "shp", "zip",
    "tif", "tiff", "nc", "hdf5", "h5", "ifc",
]

GEOM_TYPES = [
    "Point", "MultiPoint", "LineString", "MultiLineString",
    "Polygon", "MultiPolygon", "GeometryCollection", "Raster", "Unknown",
]

OGC_TYPES = ["WFS", "WMS", "WCS", "WMTS", "OGC API - Features", "OGC API - Maps"]

if "upload_footprint" not in st.session_state:
    st.session_state.upload_footprint = None

st.title("Upload Dataset")
st.caption(
    "Register a dataset in the datalake. "
    "Choose File to upload a file to the server storage, or OGC to register a service endpoint."
)

source_type = st.radio(
    "Source type",
    options=["File", "OGC"],
    horizontal=True,
    help="File: upload any spatial or non-spatial file. OGC: register a WFS/WMS/WCS/WMTS URL.",
)
source_type_key = source_type.lower()

st.divider()
st.subheader("1 — Source")

uploaded_file = None
file_bytes: bytes | None = None
ogc_url: str = ""
ogc_type: str | None = None

if source_type_key == "file":
    col_file, col_hint = st.columns([3, 2])
    with col_file:
        uploaded_file = st.file_uploader(
            "Dataset file *",
            type=ACCEPTED_EXTENSIONS,
            help="Any spatial or non-spatial file. It will be transferred to the FTP server.",
        )
    with col_hint:
        if is_configured():
            st.success("FTP server is configured.")
        else:
            st.warning(
                "FTP is not configured. The file metadata will be saved in the database "
                "but the file will not be transferred. Add [ftp] to .streamlit/secrets.toml."
            )
    if uploaded_file:
        file_bytes = uploaded_file.read()
        st.caption(f"Selected: {uploaded_file.name} — {len(file_bytes) / 1024:.1f} KB")
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
st.subheader("2 — Metadata")

col_name, col_tags = st.columns([3, 2])
with col_name:
    name = st.text_input("Name *", placeholder="e.g. Turin Building Footprints 2024")
with col_tags:
    tags_raw = st.text_input("Tags (comma-separated)", placeholder="e.g. buildings, urban, 2024")

description = st.text_area(
    "Description",
    placeholder="Source, content, methodology, known limitations",
    height=100,
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
st.subheader("3 — Spatial properties")

col_sp, col_gt = st.columns([1, 2])
with col_sp:
    is_spatial = st.checkbox("Spatial dataset", value=True)
with col_gt:
    spatial_type = st.selectbox("Geometry type", GEOM_TYPES) if is_spatial else None

st.caption(
    "Draw the spatial footprint (bounding polygon) of the dataset on the map below. "
    "Leave it blank for non-spatial datasets."
)

m_upload = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB positron")
if st.session_state.upload_footprint:
    folium.GeoJson(
        {"type": "Feature", "geometry": st.session_state.upload_footprint},
        name="Footprint",
        style_function=lambda _: {
            "fillColor": "#3a86ff",
            "color": "#023e8a",
            "fillOpacity": 0.30,
            "weight": 2,
        },
        tooltip="Captured footprint",
    ).add_to(m_upload)

Draw(
    position="topleft",
    draw_options={
        "polygon": {"allowIntersection": False, "showArea": True},
        "rectangle": True,
        "polyline": False,
        "circle": False,
        "circlemarker": False,
        "marker": False,
    },
    edit_options={"edit": True, "remove": True},
).add_to(m_upload)

map_data = st_folium(m_upload, key="upload_map", use_container_width=True, height=420)
drawings = (map_data or {}).get("all_drawings") or []
poly_drawings = [
    f for f in drawings if f.get("geometry", {}).get("type") in ("Polygon", "MultiPolygon")
]
if poly_drawings:
    st.session_state.upload_footprint = poly_drawings[-1]["geometry"]

fp_col, clear_col = st.columns([5, 1])
with fp_col:
    if st.session_state.upload_footprint:
        st.success("Footprint captured.")
    else:
        st.info("No footprint drawn.")
with clear_col:
    if st.session_state.upload_footprint and st.button("Clear", key="clear_fp", use_container_width=True):
        st.session_state.upload_footprint = None
        st.rerun()

st.divider()
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
                footprint_geojson=st.session_state.upload_footprint,
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
            st.session_state.upload_footprint = None
        except Exception as exc:
            st.error(f"Registration failed: {exc}")
