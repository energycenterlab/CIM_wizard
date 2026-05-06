"""Upload page — ingest a JSON dataset with metadata and spatial/temporal footprint."""
import json
import os
import sys

import folium
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import st_folium

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import insert_dataset  # noqa: E402

st.set_page_config(page_title="Upload Dataset", page_icon="📤", layout="wide")

# ── Session state defaults ──────────────────────────────────────────────────
if "upload_footprint" not in st.session_state:
    st.session_state.upload_footprint = None

# ── Page header ─────────────────────────────────────────────────────────────
st.title("📤 Upload Dataset")
st.caption("Store a JSON / GeoJSON dataset in the datalake with its spatial and temporal metadata.")

# ── Metadata form ────────────────────────────────────────────────────────────
st.subheader("1 — Dataset Metadata")

row1_col1, row1_col2 = st.columns([3, 2])
with row1_col1:
    name = st.text_input(
        "Dataset Name *",
        placeholder="e.g. Turin Building Footprints 2024",
    )
with row1_col2:
    tags_raw = st.text_input(
        "Tags (comma-separated)",
        placeholder="e.g. buildings, urban, 2024",
    )

description = st.text_area(
    "Description",
    placeholder="Briefly describe the dataset: source, content, methodology…",
    height=100,
)

row2_col1, row2_col2, row2_col3 = st.columns([2, 1, 1])
with row2_col1:
    uploaded_file = st.file_uploader(
        "JSON / GeoJSON File *",
        type=["json", "geojson"],
        help="The raw dataset that will be stored as JSONB in PostGIS.",
    )
with row2_col2:
    temporal_start = st.date_input("Temporal Start *")
with row2_col3:
    temporal_end = st.date_input("Temporal End *")

# ── Spatial footprint map ────────────────────────────────────────────────────
st.subheader("2 — Spatial Footprint  (EPSG:4326)")
st.caption(
    "Use the **polygon** or **rectangle** tool (top-left toolbar) to draw the spatial "
    "coverage of your dataset. One polygon per dataset. Drawing a new one replaces the previous."
)

m_upload = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB positron")

# Re-display already-captured footprint as a static layer
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
        "polygon":      {"allowIntersection": False, "showArea": True},
        "rectangle":    True,
        "polyline":     False,
        "circle":       False,
        "circlemarker": False,
        "marker":       False,
    },
    edit_options={"edit": True, "remove": True},
).add_to(m_upload)

map_data = st_folium(
    m_upload,
    key="upload_map",
    use_container_width=True,
    height=440,
)

# Capture the last drawn polygon
drawings = (map_data or {}).get("all_drawings") or []
poly_drawings = [
    f for f in drawings
    if f.get("geometry", {}).get("type") in ("Polygon", "MultiPolygon")
]
if poly_drawings:
    st.session_state.upload_footprint = poly_drawings[-1]["geometry"]

# Footprint status row
fp_status_col, fp_clear_col = st.columns([5, 1])
with fp_status_col:
    if st.session_state.upload_footprint:
        geom_type = st.session_state.upload_footprint.get("type", "")
        n_coords = len(
            (st.session_state.upload_footprint.get("coordinates") or [[]])[0]
        )
        st.success(f"✅ Footprint captured — {geom_type} with {n_coords} vertices.")
    else:
        st.info("ℹ️ No footprint drawn yet — draw a polygon on the map above.")
with fp_clear_col:
    if st.session_state.upload_footprint:
        if st.button("Clear", key="clear_fp", use_container_width=True):
            st.session_state.upload_footprint = None
            st.rerun()

# ── Submit ───────────────────────────────────────────────────────────────────
st.divider()
submit = st.button("⬆️  Upload Dataset", type="primary", use_container_width=True)

if submit:
    errors: list[str] = []

    if not name.strip():
        errors.append("Dataset name is required.")
    if not uploaded_file:
        errors.append("A JSON / GeoJSON file is required.")
    if not st.session_state.upload_footprint:
        errors.append("A spatial footprint must be drawn on the map.")
    if temporal_start > temporal_end:
        errors.append("Temporal start must be on or before temporal end.")

    if errors:
        for err in errors:
            st.error(err)
    else:
        try:
            raw_bytes = uploaded_file.read()
            json_data = json.loads(raw_bytes)
            tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

            with st.spinner("Uploading…"):
                dataset_id = insert_dataset(
                    name=name.strip(),
                    description=description.strip(),
                    tags=tags,
                    footprint_geojson=st.session_state.upload_footprint,
                    temporal_start=temporal_start,
                    temporal_end=temporal_end,
                    data=json_data,
                    filename=uploaded_file.name,
                )

            st.success(f"✅ Dataset uploaded successfully!  ID: `{dataset_id}`")
            # Reset footprint for next upload
            st.session_state.upload_footprint = None

        except json.JSONDecodeError as exc:
            st.error(f"Invalid JSON file: {exc}")
        except Exception as exc:
            st.error(f"Upload failed: {exc}")
