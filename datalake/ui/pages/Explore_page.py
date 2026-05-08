"""
Explore page — spatial dataset discovery.

Layout:
  Sidebar  : filters, spatial-filter status, search/clear, results list.
  Main area: full-width interactive map.

Polygon-filter flow:
  1. Draw a polygon or rectangle on the map with the Draw toolbar.
  2. The drawn shape is captured into session_state.study_area on the next
     Streamlit rerun (triggered by the map interaction itself).
  3. Click Search — the sidebar query runs with study_area already in
     session_state, passes it to ST_Intersects in PostGIS, and returns
     all matching records with their spatial_footprint geometries.
  4. Footprints are rendered on the map as coloured overlays.

Note on map key versioning:
  When the user clicks Clear, st.session_state.map_version is incremented.
  This changes the key passed to st_folium, forcing a fresh Leaflet component
  instance that has no drawings — preventing the old all_drawings from being
  re-read and re-captured into study_area.
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

st.set_page_config(page_title="Explore — CIM Datalake", layout="wide")

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


def _bbox_str(geom: dict) -> str:
    """Return a compact bbox string from a GeoJSON geometry."""
    try:
        ring = geom["coordinates"][0]
        lons = [c[0] for c in ring]
        lats = [c[1] for c in ring]
        return (
            f"W {min(lons):.3f}  S {min(lats):.3f}  "
            f"E {max(lons):.3f}  N {max(lats):.3f}"
        )
    except Exception:
        return ""


# ── Session state defaults ───────────────────────────────────────────────────
for _k, _v in [
    ("study_area",   None),
    ("results",      []),
    ("map_version",  0),
    ("search_done",  False),
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("CIM Datalake")
    st.divider()

    # -- Attribute filters ----------------------------------------------------
    st.markdown("**Filters**")

    selected_tags = st.multiselect("Tags", options=_safe_tags(), placeholder="Any tag")

    source_type_filter = st.selectbox("Source type", options=["Any", "file", "ogc"])

    spatial_filter = st.selectbox(
        "Spatial", options=["Any", "Spatial only", "Non-spatial only"]
    )

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        filter_start = st.date_input("From", value=None, key="f_start")
    with col_d2:
        filter_end = st.date_input("To", value=None, key="f_end")

    st.divider()

    # -- Spatial polygon filter -----------------------------------------------
    st.markdown("**Spatial polygon filter**")

    if st.session_state.study_area:
        st.success("Polygon active")
        bbox_info = _bbox_str(st.session_state.study_area)
        if bbox_info:
            st.caption(bbox_info)
        if st.button("Remove polygon", use_container_width=True):
            st.session_state.study_area = None
            st.session_state.map_version += 1   # resets map drawings
            st.rerun()
    else:
        st.info("Draw a polygon on the map to add a spatial filter.")

    st.divider()

    # -- Action buttons -------------------------------------------------------
    search_btn   = st.button("Search", type="primary", use_container_width=True)
    show_all_btn = st.button("Show all datasets", use_container_width=True,
                             help="Ignore all filters and show every registered dataset.")
    clear_btn    = st.button("Clear all filters and results", use_container_width=True)

    # -- Query execution ------------------------------------------------------
    if search_btn:
        src = source_type_filter if source_type_filter != "Any" else None
        is_spatial_q: bool | None = None
        if spatial_filter == "Spatial only":
            is_spatial_q = True
        elif spatial_filter == "Non-spatial only":
            is_spatial_q = False

        try:
            with st.spinner("Querying PostGIS..."):
                st.session_state.results = query_records(
                    study_area_geojson=st.session_state.study_area,
                    tags=selected_tags if selected_tags else None,
                    source_type=src,
                    is_spatial=is_spatial_q,
                    temporal_start=filter_start,
                    temporal_end=filter_end,
                )
            st.session_state.search_done = True
        except Exception as exc:
            st.error(f"Query failed: {exc}")
            st.session_state.results = []

    if show_all_btn:
        try:
            with st.spinner("Loading all datasets..."):
                st.session_state.results = query_records()
            st.session_state.search_done = True
        except Exception as exc:
            st.error(f"Query failed: {exc}")
            st.session_state.results = []

    if clear_btn:
        st.session_state.study_area  = None
        st.session_state.results     = []
        st.session_state.search_done = False
        st.session_state.map_version += 1   # resets map drawings
        st.rerun()

    # -- Results list ---------------------------------------------------------
    n = len(st.session_state.results)

    if n:
        st.divider()
        poly_note = " (spatial filter applied)" if st.session_state.study_area else ""
        st.markdown(f"**{n} dataset{'s' if n != 1 else ''} found{poly_note}**")

        for idx, row in enumerate(st.session_state.results):
            src_label = (row.get("source_type") or "").upper()
            color     = _color(idx)
            dot       = f'<span style="color:{color};font-size:1.1em;">&#9632;</span>'

            with st.expander(
                f"{src_label}  {row['name']}",
                expanded=False,
            ):
                st.markdown(dot + f" **{row['name']}**", unsafe_allow_html=True)

                if row.get("description"):
                    st.write(row["description"])

                tags_list = row.get("tags") or []
                if tags_list:
                    st.markdown("**Tags:** " + " ".join(f"`{t}`" for t in tags_list))

                t_start = row.get("temporal_start") or "—"
                t_end   = row.get("temporal_end")   or "—"
                st.markdown(f"**Period:** {t_start} to {t_end}")

                if row.get("location"):
                    st.markdown(f"**Location:** {row['location']}")

                if row.get("is_spatial"):
                    parts = [row.get("spatial_type") or "unknown geometry"]
                    if row.get("crs"):
                        parts.append(row["crs"])
                    st.markdown(f"**Spatial:** {' — '.join(parts)}")

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

                st.caption(f"ID: {row['id']}")
                st.caption(f"Uploaded: {str(row.get('uploaded_at') or '')[:19]} UTC")

    elif st.session_state.search_done:
        st.divider()
        msg = "No datasets match the current filters."
        if st.session_state.study_area:
            msg += (
                " The spatial polygon filter may be excluding results — "
                "check that your uploaded datasets have a valid EPSG:4326 bounding box, "
                "or click 'Show all datasets' to see everything regardless of filters."
            )
        st.info(msg)

# ── Main area — map viewer ───────────────────────────────────────────────────

# Build map
m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB positron")

# Draw plugin — polygon and rectangle only
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
).add_to(m)

# Overlay the active spatial filter polygon from session_state
# (drawn in a previous run and persisted; shown here so the user always sees it)
if st.session_state.study_area:
    folium.GeoJson(
        {"type": "Feature", "geometry": st.session_state.study_area},
        name="Spatial filter",
        style_function=lambda _: {
            "fillColor": "#ff6b00",
            "fillOpacity": 0.08,
            "color":     "#ff6b00",
            "weight":    2.5,
            "dashArray": "8 5",
        },
        tooltip="Spatial filter polygon",
    ).add_to(m)

# Overlay dataset footprints from query results
all_bounds: list[list[float]] = []

for idx, row in enumerate(st.session_state.results):
    fp_str = row.get("spatial_footprint")
    if not fp_str:
        continue

    geom  = json.loads(fp_str)
    color = _color(idx)
    tags_str = ", ".join(row.get("tags") or []) or "—"
    t_start  = str(row.get("temporal_start") or "—")
    t_end    = str(row.get("temporal_end")   or "—")

    folium.GeoJson(
        {
            "type": "Feature",
            "geometry": geom,
            "properties": {
                "name":        row["name"],
                "source":      row.get("source_type", ""),
                "tags":        tags_str,
                "period":      f"{t_start} to {t_end}",
                "description": (row.get("description") or "")[:140],
            },
        },
        name=row["name"],
        style_function=lambda _, c=color: {
            "fillColor":   c,
            "color":       c,
            "fillOpacity": 0.25,
            "weight":      2,
        },
        highlight_function=lambda _, c=color: {
            "fillColor":   c,
            "fillOpacity": 0.55,
            "weight":      3,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["name", "source", "tags", "period", "description"],
            aliases=["Dataset:", "Source:", "Tags:", "Period:", "Description:"],
            sticky=True,
            max_width=360,
        ),
    ).add_to(m)

    # Collect bounds for auto-fit
    coords = geom.get("coordinates") or []
    if coords:
        ring = coords[0]
        all_bounds.extend([[c[1], c[0]] for c in ring])

# Auto-fit to result footprints
if all_bounds:
    m.fit_bounds(all_bounds, padding=(40, 40))

if st.session_state.results:
    folium.LayerControl(collapsed=False).add_to(m)

# Render the map.
# key includes map_version so that Clear / Remove polygon forces a fresh instance.
map_data = st_folium(
    m,
    key=f"explore_map_{st.session_state.map_version}",
    use_container_width=True,
    height=780,
)

# ── Capture drawn polygon from this run's map interaction ────────────────────
# all_drawings is the full list of current drawings on the Leaflet component.
# We always overwrite study_area when drawings are present; we deliberately do
# NOT clear it when the list is empty (that would erase the polygon on every
# rerun that wasn't triggered by a draw event).
drawings = (map_data or {}).get("all_drawings") or []
poly_drawings = [
    f for f in drawings
    if f.get("geometry", {}).get("type") in ("Polygon", "MultiPolygon")
]
if poly_drawings:
    captured = poly_drawings[-1]["geometry"]
    if captured != st.session_state.study_area:
        st.session_state.study_area = captured
        st.rerun()   # rerun so the sidebar immediately shows "Polygon active"
