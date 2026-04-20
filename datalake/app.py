import json
import os
import sys
import uuid
from datetime import date, datetime, time, timedelta, timezone

import folium
import pandas as pd
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import st_folium

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pymongo import MongoClient

from datalake import load_geojson

MONGO_URI = "mongodb://localhost:27018/"
DB_NAME   = "datalake"
RAWDATA   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rawdata")

DATA_TYPES   = ["geojson", "vector", "raster", "csv", "json", "ifc", "hdf5", "wfs", "wms", "wcs"]
SOURCE_TYPES = ["file", "api", "ogc"]

TURIN = [45.0703, 7.6869]   # default map centre


@st.cache_resource
def _mongo_client():
    return MongoClient(MONGO_URI)

def _db():
    return _mongo_client()[DB_NAME]

def _distinct(field: str) -> list[str]:
    try:
        return sorted(v for v in _db()["datasources"].distinct(field) if v)
    except Exception:
        return []


# ── Page ──────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Datalake4Raw", layout="wide")
st.title("Datalake4Raw")

tab_ingest, tab_query = st.tabs(["Ingest", "Query"])


# ── Ingest ────────────────────────────────────────────────────────────────

with tab_ingest:
    uploaded = st.file_uploader("GeoJSON file", type=["geojson", "json"])

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        name        = st.text_input("Name", placeholder="leave blank to use filename")
        description = st.text_area("Description", height=110)
        location    = st.text_input("Location", placeholder="Turin, Piedmont, Italy")
        crs         = st.text_input("CRS", value="EPSG:4326")
    with c2:
        source_type = st.selectbox("Source type", SOURCE_TYPES)
        data_type   = st.selectbox("Data type",   DATA_TYPES)
        collection  = st.text_input("Collection", value="default")
        tags_raw    = st.text_input("Tags (comma-separated)", placeholder="urban, buildings, 2024")

    if st.button("Ingest", type="primary", disabled=uploaded is None):
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

        upload_id  = str(uuid.uuid4())
        date_path  = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        save_dir   = os.path.join(RAWDATA, data_type, date_path, upload_id)
        os.makedirs(save_dir, exist_ok=True)
        saved_path = os.path.join(save_dir, uploaded.name)

        with open(saved_path, "wb") as f:
            f.write(uploaded.getbuffer())

        with st.spinner("Ingesting…"):
            try:
                ds_id = load_geojson(
                    file_path=saved_path,
                    name=name or None,
                    description=description,
                    collection=collection,
                    tags=tags,
                    crs=crs,
                    location=location or None,
                )
                st.success(f"Ingested — datasource_id: `{ds_id}`")
            except Exception as exc:
                st.error(str(exc))


# ── Query ─────────────────────────────────────────────────────────────────

with tab_query:

    # ── Attribute filters ──────────────────────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Date range**")
        date_from = st.date_input("From", value=date.today() - timedelta(days=365), key="qfrom")
        date_to   = st.date_input("To",   value=date.today(),                        key="qto")
    with c2:
        sel_types = st.multiselect("Data type",  DATA_TYPES)
        sel_colls = st.multiselect("Collection", _distinct("properties.dl4r:collection"))
        ingested  = st.checkbox("Ingested only")

    st.divider()

    # ── Spatial filter — interactive drawing map ───────────────────────
    st.markdown("**Spatial filter** — draw a polygon or rectangle to restrict the search area")

    draw_map = folium.Map(location=TURIN, zoom_start=12, tiles="CartoDB positron")
    Draw(
        draw_options={
            "polygon":      {"allowIntersection": False},
            "rectangle":    True,
            "circle":       False,
            "circlemarker": False,
            "polyline":     False,
            "marker":       False,
        },
        edit_options={"edit": True, "remove": True},
    ).add_to(draw_map)

    map_data = st_folium(draw_map, key="draw_map", use_container_width=True, height=460)

    # Persist drawn polygon across re-runs in session state
    drawings = (map_data or {}).get("all_drawings") or []
    if drawings:
        st.session_state["search_poly"] = drawings[-1].get("geometry")

    geo_filter = st.session_state.get("search_poly")

    col_info, col_clear = st.columns([6, 1])
    with col_info:
        if geo_filter:
            coords_preview = json.dumps(geo_filter["coordinates"][0][:3])[:-1] + ", …]"
            st.caption(f"Search polygon captured — first coords: {coords_preview}")
        else:
            st.caption("No polygon drawn — query will not apply a spatial filter.")
    with col_clear:
        if st.button("Clear polygon"):
            st.session_state.pop("search_poly", None)
            geo_filter = None

    st.divider()
    run_query = st.button("Query", type="primary")

    # ── Execute query ──────────────────────────────────────────────────
    if run_query:
        q: dict = {}

        dt_from = datetime.combine(date_from, time.min).replace(tzinfo=timezone.utc).isoformat()
        dt_to   = datetime.combine(date_to,   time.max).replace(tzinfo=timezone.utc).isoformat()
        q["properties.datetime"] = {"$gte": dt_from, "$lte": dt_to}

        if sel_types:
            q["properties.dl4r:data_type"] = {"$in": sel_types}
        if sel_colls:
            q["properties.dl4r:collection"] = {"$in": sel_colls}
        if ingested:
            q["properties.dl4r:ingested"] = True
        if geo_filter:
            q["geometry"] = {"$geoIntersects": {"$geometry": geo_filter}}

        docs = list(_db()["datasources"].find(q))

        if not docs:
            st.info("No results.")
        else:
            st.success(f"{len(docs)} datasource(s) found.")

            # ── Results table ──────────────────────────────────────────
            rows = []
            for d in docs:
                p = d.get("properties", {})
                rows.append({
                    "_id":        str(d.get("_id", "")),
                    "name":       p.get("title", ""),
                    "datetime":   (p.get("datetime") or "")[:19],
                    "data_type":  p.get("dl4r:data_type", ""),
                    "collection": p.get("dl4r:collection", ""),
                    "geo_type":   p.get("dl4r:geo_type", ""),
                    "crs":        p.get("dl4r:crs", ""),
                    "location":   p.get("dl4r:location", ""),
                    "features":   (d.get("_mongo") or {}).get("feature_count"),
                    "ingested":   p.get("dl4r:ingested", False),
                    "bbox":       d.get("bbox"),
                })

            df = pd.DataFrame(rows)
            st.dataframe(df.drop(columns=["bbox"]), use_container_width=True, hide_index=True)

            with st.expander("Raw STAC documents"):
                for d in docs:
                    d["_id"] = str(d["_id"])
                st.json(docs)

            # ── Results footprint map ──────────────────────────────────
            bbox_rows = [r for r in rows if r["bbox"]]
            if bbox_rows:
                st.subheader("Footprints")

                # Compute bounds for auto-zoom
                all_lons = [c for r in bbox_rows for c in (r["bbox"][0], r["bbox"][2])]
                all_lats = [c for r in bbox_rows for c in (r["bbox"][1], r["bbox"][3])]
                sw = [min(all_lats), min(all_lons)]
                ne = [max(all_lats), max(all_lons)]

                res_map = folium.Map(tiles="CartoDB positron")
                res_map.fit_bounds([sw, ne], padding=(30, 30))

                # Draw the search polygon if one was used
                if geo_filter:
                    folium.GeoJson(
                        geo_filter,
                        style_function=lambda _: {
                            "fillColor": "none",
                            "color": "#e65c00",
                            "weight": 2,
                            "dashArray": "6 4",
                        },
                        name="Search area",
                    ).add_to(res_map)

                # Draw each result footprint
                for r in bbox_rows:
                    xmin, ymin, xmax, ymax = r["bbox"]
                    folium.GeoJson(
                        {
                            "type": "Feature",
                            "geometry": {
                                "type": "Polygon",
                                "coordinates": [[
                                    [xmin, ymin], [xmax, ymin], [xmax, ymax],
                                    [xmin, ymax], [xmin, ymin],
                                ]],
                            },
                            "properties": {
                                "name":      r["name"],
                                "data_type": r["data_type"],
                                "features":  r["features"],
                                "datetime":  r["datetime"],
                            },
                        },
                        style_function=lambda _: {
                            "fillColor": "#3388ff",
                            "fillOpacity": 0.25,
                            "color": "#1a66cc",
                            "weight": 2,
                        },
                        tooltip=folium.GeoJsonTooltip(
                            fields=["name", "data_type", "features", "datetime"],
                            aliases=["Name", "Type", "Features", "Date"],
                            sticky=True,
                        ),
                    ).add_to(res_map)

                st_folium(res_map, key="results_map", use_container_width=True, height=460)
