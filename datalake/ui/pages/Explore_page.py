"""
Explore page — discover and inspect datasets registered in meta_table.
"""
from __future__ import annotations

import json
import os
import sys

import folium
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import st_folium

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_all_tags, query_records  # noqa: E402

st.set_page_config(page_title="Explore Datalake", layout="wide")

_PALETTE = [
    "#e63946", "#2a9d8f", "#e9c46a", "#f4a261",
    "#457b9d", "#a8dadc", "#6a4c93", "#1982c4",
    "#8ac926", "#ff595e", "#6a994e", "#bc4749",
    "#ffca3a", "#3a86ff",
]


def _color(idx: int) -> str:
    return _PALETTE[idx % len(_PALETTE)]


def _safe_tags() -> list[str]:
    try:
        return get_all_tags()
    except Exception:
        return []


def _fmt_size(n: int | None) -> str:
    if n is None:
        return "—"
    if n < 1024:
        return f"{n} B"
    if n < 1024 ** 2:
        return f"{n / 1024:.1f} KB"
    return f"{n / 1024 ** 2:.1f} MB"


if "study_area" not in st.session_state:
    st.session_state.study_area = None
if "results" not in st.session_state:
    st.session_state.results = []

st.title("Explore Datalake")
st.caption(
    "Filter datasets by tags, source type, date range, or spatial coverage. "
    "Draw a study-area polygon on the map to restrict results to intersecting footprints."
)

st.subheader("1 — Filters")
col_tags, col_src, col_spatial = st.columns([3, 1.5, 1.5])
with col_tags:
    selected_tags = st.multiselect("Tags", options=_safe_tags(), placeholder="Any tag")
with col_src:
    source_type_filter = st.selectbox("Source type", options=["Any", "file", "ogc"], index=0)
with col_spatial:
    spatial_filter = st.selectbox("Spatial", options=["Any", "Spatial only", "Non-spatial only"], index=0)

col_d1, col_d2, col_search, col_clear = st.columns([2, 2, 1, 1])
with col_d1:
    filter_start = st.date_input("Temporal from", value=None, key="f_start")
with col_d2:
    filter_end = st.date_input("Temporal to", value=None, key="f_end")
with col_search:
    st.write("")
    search_btn = st.button("Search", type="primary", use_container_width=True)
with col_clear:
    st.write("")
    clear_btn = st.button("Clear", use_container_width=True)

if search_btn:
    src = source_type_filter if source_type_filter != "Any" else None
    is_spatial_q: bool | None = None
    if spatial_filter == "Spatial only":
        is_spatial_q = True
    elif spatial_filter == "Non-spatial only":
        is_spatial_q = False

    try:
        st.session_state.results = query_records(
            study_area_geojson=st.session_state.study_area,
            tags=selected_tags if selected_tags else None,
            source_type=src,
            is_spatial=is_spatial_q,
            temporal_start=filter_start,
            temporal_end=filter_end,
        )
    except Exception as exc:
        st.error(f"Query failed: {exc}")
        st.session_state.results = []

if clear_btn:
    st.session_state.study_area = None
    st.session_state.results = []
    st.rerun()

st.divider()
n_results = len(st.session_state.results)
st.subheader("2 — Map")
st.caption(
    "Draw a polygon or rectangle to define a study area. "
    + (f"{n_results} dataset(s) shown." if n_results else "No results yet — click Search.")
)

m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB positron")
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
).add_to(m)

if st.session_state.study_area:
    folium.GeoJson(
        {"type": "Feature", "geometry": st.session_state.study_area},
        name="Study area",
        style_function=lambda _: {"fillColor": "none", "color": "#ff6b00", "weight": 2.5, "dashArray": "7 5"},
        tooltip="Your study area",
    ).add_to(m)

all_bounds: list[list[float]] = []
for idx, row in enumerate(st.session_state.results):
    fp_str = row.get("spatial_footprint")
    if not fp_str:
        continue
    geom = json.loads(fp_str)
    color = _color(idx)
    tags_str = ", ".join(row.get("tags") or []) or "—"
    t_start = str(row.get("temporal_start") or "—")
    t_end = str(row.get("temporal_end") or "—")

    folium.GeoJson(
        {
            "type": "Feature",
            "geometry": geom,
            "properties": {
                "name": row["name"],
                "source": row.get("source_type", ""),
                "tags": tags_str,
                "period": f"{t_start} to {t_end}",
                "uploaded": str(row.get("uploaded_at") or "")[:19],
                "description": (row.get("description") or "")[:140],
            },
        },
        name=row["name"],
        style_function=lambda _, c=color: {"fillColor": c, "color": c, "fillOpacity": 0.22, "weight": 2},
        highlight_function=lambda _, c=color: {"fillColor": c, "fillOpacity": 0.50, "weight": 3},
        tooltip=folium.GeoJsonTooltip(
            fields=["name", "source", "tags", "period", "description"],
            aliases=["Dataset:", "Source:", "Tags:", "Period:", "Description:"],
            sticky=True,
            max_width=360,
        ),
    ).add_to(m)

    coords = geom.get("coordinates") or []
    if coords:
        ring = coords[0]
        lons = [c[0] for c in ring]
        lats = [c[1] for c in ring]
        all_bounds.extend([[lat, lon] for lat, lon in zip(lats, lons)])

if all_bounds:
    m.fit_bounds(all_bounds, padding=(30, 30))
if st.session_state.results:
    folium.LayerControl(collapsed=False).add_to(m)

map_data = st_folium(m, key="explore_map", use_container_width=True, height=520)

drawings = (map_data or {}).get("all_drawings") or []
poly_drawings = [f for f in drawings if f.get("geometry", {}).get("type") in ("Polygon", "MultiPolygon")]
if poly_drawings:
    new_geom = poly_drawings[-1]["geometry"]
    if new_geom != st.session_state.study_area:
        st.session_state.study_area = new_geom

if st.session_state.study_area:
    st.success("Study area defined. Click Search to find intersecting datasets.")
else:
    st.info("No study area — Search returns datasets matching only the above filters.")

if st.session_state.results:
    st.divider()
    st.subheader(f"3 — Results ({n_results} dataset{'s' if n_results != 1 else ''})")
    for row in st.session_state.results:
        label = f"[{row.get('source_type', '').upper()}] {row['name']}"
        with st.expander(label, expanded=False):
            col_info, col_meta = st.columns([3, 2])
            with col_info:
                if row.get("description"):
                    st.write(row["description"])
                tags_list = row.get("tags") or []
                if tags_list:
                    st.markdown("**Tags:** " + " ".join(f"`{t}`" for t in tags_list))
                t_start = row.get("temporal_start") or "—"
                t_end = row.get("temporal_end") or "—"
                st.markdown(f"**Period:** {t_start} to {t_end}")
                if row.get("location"):
                    st.markdown(f"**Location:** {row['location']}")
                if row.get("is_spatial"):
                    parts = [row.get("spatial_type") or "unknown geometry"]
                    if row.get("crs"):
                        parts.append(row["crs"])
                    st.markdown(f"**Spatial:** {' — '.join(parts)}")
            with col_meta:
                if row.get("source_type") == "ogc":
                    if row.get("ogc_type"):
                        st.markdown(f"**Service:** {row['ogc_type']}")
                    if row.get("ogc_url"):
                        st.markdown(f"**URL:** [{row['ogc_url']}]({row['ogc_url']})")
                elif row.get("source_type") == "file":
                    if row.get("filename"):
                        st.markdown(f"**File:** `{row['filename']}`")
                    if row.get("file_size_bytes") is not None:
                        st.markdown(f"**Size:** {_fmt_size(row['file_size_bytes'])}")
                    if row.get("file_path"):
                        st.markdown(f"**FTP path:** `{row['file_path']}`")
                st.markdown(f"**ID:** `{row['id']}`")
                st.markdown(f"**Uploaded:** {str(row.get('uploaded_at') or '')[:19]} UTC")
elif search_btn:
    st.info("No datasets match the current filters.")
