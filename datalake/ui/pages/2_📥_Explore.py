"""
Explore & Download page.

Workflow:
  1. (Optional) Adjust tag / date filters in the top bar.
  2. Draw a study-area polygon on the map.
  3. Click Search → matching dataset footprints appear on the map.
  4. Download any result as JSON from the results panel.
"""
import json
import os
import sys

import folium
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import st_folium

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_all_tags, query_datasets  # noqa: E402

st.set_page_config(
    page_title="Explore & Download",
    page_icon="📥",
    layout="wide",
)

# Distinct colours for up to 14 simultaneous footprints; cycles beyond that.
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


# ── Session state defaults ──────────────────────────────────────────────────
if "study_area" not in st.session_state:
    st.session_state.study_area = None
if "query_results" not in st.session_state:
    st.session_state.query_results = []

# ── Page header ─────────────────────────────────────────────────────────────
st.title("📥 Explore & Download")
st.caption(
    "Draw your study area on the map, set filters, and click **Search** to discover "
    "datasets whose spatial footprint intersects your area."
)

# ── Filter bar ───────────────────────────────────────────────────────────────
st.subheader("1 — Filters")
f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns([3, 1.5, 1.5, 1, 1])

with f_col1:
    selected_tags = st.multiselect(
        "Tags",
        options=_safe_tags(),
        placeholder="Any tag",
    )
with f_col2:
    filter_start = st.date_input("Temporal From", value=None, key="f_start")
with f_col3:
    filter_end = st.date_input("Temporal To", value=None, key="f_end")
with f_col4:
    st.write("")  # vertical alignment nudge
    search_btn = st.button("🔍 Search", type="primary", use_container_width=True)
with f_col5:
    st.write("")
    clear_btn = st.button("🗑️ Clear", use_container_width=True)

# ── Execute search BEFORE map renders so results are available immediately ──
if search_btn:
    try:
        with st.spinner("Querying PostGIS…"):
            st.session_state.query_results = query_datasets(
                study_area_geojson=st.session_state.study_area,
                tags=selected_tags if selected_tags else None,
                temporal_start=filter_start,
                temporal_end=filter_end,
            )
    except Exception as exc:
        st.error(f"Query failed: {exc}")
        st.session_state.query_results = []

if clear_btn:
    st.session_state.study_area = None
    st.session_state.query_results = []
    st.rerun()

# ── Map ──────────────────────────────────────────────────────────────────────
st.subheader("2 — Map")

n_results = len(st.session_state.query_results)
status_msg = (
    f"{n_results} dataset(s) currently shown on map."
    if n_results
    else "No results yet — draw a study area and click Search."
)
st.caption(
    "Use the **polygon / rectangle** tool (top-left) to draw your study area. "
    "The drawn shape is preserved after each Search. " + status_msg
)

# Build fresh Folium map on every run
m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB positron")

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

# Study-area layer
if st.session_state.study_area:
    folium.GeoJson(
        {"type": "Feature", "geometry": st.session_state.study_area},
        name="Study Area",
        style_function=lambda _: {
            "fillColor": "none",
            "color": "#ff6b00",
            "weight": 2.5,
            "dashArray": "7 5",
        },
        tooltip="Your study area",
    ).add_to(m)

# Dataset footprint layers
all_bounds: list[list[float]] = []

for idx, row in enumerate(st.session_state.query_results):
    fp_str = row.get("spatial_footprint")
    if not fp_str:
        continue

    geom = json.loads(fp_str)
    color = _color(idx)

    tags_str = ", ".join(row.get("tags") or []) or "—"
    t_start = str(row.get("temporal_start") or "—")
    t_end = str(row.get("temporal_end") or "—")

    feature = {
        "type": "Feature",
        "geometry": geom,
        "properties": {
            "name":        row["name"],
            "tags":        tags_str,
            "period":      f"{t_start} → {t_end}",
            "uploaded":    str(row.get("uploaded_at") or "")[:19],
            "description": (row.get("description") or "")[:120],
        },
    }

    folium.GeoJson(
        feature,
        name=row["name"],
        style_function=lambda _, c=color: {
            "fillColor": c,
            "color":     c,
            "fillOpacity": 0.25,
            "weight":    2,
        },
        highlight_function=lambda _, c=color: {
            "fillColor": c,
            "fillOpacity": 0.55,
            "weight":    3,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["name", "tags", "period", "description"],
            aliases=["Dataset:", "Tags:", "Period:", "Description:"],
            sticky=True,
            max_width=340,
        ),
    ).add_to(m)

    # Collect coordinates for auto-fit
    coords = geom.get("coordinates") or []
    if coords:
        ring = coords[0]
        lons = [c[0] for c in ring]
        lats = [c[1] for c in ring]
        all_bounds.extend([[lat, lon] for lat, lon in zip(lats, lons)])

# Auto-fit bounds when results are present
if all_bounds:
    m.fit_bounds(all_bounds, padding=(30, 30))

if st.session_state.query_results:
    folium.LayerControl(collapsed=False).add_to(m)

map_data = st_folium(
    m,
    key="explore_map",
    use_container_width=True,
    height=520,
)

# ── Capture drawn study area ─────────────────────────────────────────────────
drawings = (map_data or {}).get("all_drawings") or []
poly_drawings = [
    f for f in drawings
    if f.get("geometry", {}).get("type") in ("Polygon", "MultiPolygon")
]
if poly_drawings:
    new_geom = poly_drawings[-1]["geometry"]
    if new_geom != st.session_state.study_area:
        st.session_state.study_area = new_geom
        # No st.rerun() here — let the user click Search deliberately

# Study-area status
if st.session_state.study_area:
    st.success(
        "✅ Study area defined. Click **Search** (above) to find intersecting datasets."
    )
else:
    st.info(
        "ℹ️ No study area — Search will return datasets matching only the tag/date filters."
    )

# ── Results ──────────────────────────────────────────────────────────────────
if st.session_state.query_results:
    st.divider()
    st.subheader(f"3 — Results  ({n_results} dataset{'s' if n_results != 1 else ''})")

    for row in st.session_state.query_results:
        with st.expander(f"📦  {row['name']}", expanded=False):
            info_col, dl_col = st.columns([4, 1])

            with info_col:
                if row.get("description"):
                    st.write(row["description"])

                tags_list = row.get("tags") or []
                if tags_list:
                    st.markdown("**Tags:** " + "  ".join(f"`{t}`" for t in tags_list))

                t_start = row.get("temporal_start") or "—"
                t_end = row.get("temporal_end") or "—"
                st.markdown(f"**Period:** {t_start} → {t_end}")

                if row.get("filename"):
                    st.markdown(f"**Original file:** `{row['filename']}`")

                st.markdown(f"**ID:** `{row['id']}`")
                st.markdown(
                    f"**Uploaded:** {str(row.get('uploaded_at') or '')[:19]} UTC"
                )

            with dl_col:
                if row.get("data") is not None:
                    st.download_button(
                        label="⬇️ Download JSON",
                        data=json.dumps(row["data"], indent=2, default=str),
                        file_name=f"{row['name'].replace(' ', '_')}.json",
                        mime="application/json",
                        key=f"dl_{row['id']}",
                        use_container_width=True,
                    )
                else:
                    st.caption("No data stored.")

elif search_btn:
    st.info("No datasets match the current filters.")
