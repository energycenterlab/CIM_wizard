"""
ingest_v_upload.py  —  Warehouse Vector Ingest Wizard
======================================================
A step-by-step Streamlit wizard that:

  Step 1  Source        file upload  OR  OGC service URL
  Step 2  Classification  spatial / non-spatial  ·  vector / raster
  Step 3  Standard metadata  optional CSW / ISO 19139 / OGC API Records pre-fill
  Step 4  Format & profile   read column names from the file (no full parse)
  Step 5  Column mapping      PK · FK · spatial · non-spatial
  Step 6  Manifest preview    build & show the JSON POST payload

Supported vector formats:
  GeoJSON · Shapefile (zip) · GeoPackage · CSV (with lon/lat or WKT) · CityJSON
"""
from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import uuid
import zipfile
from datetime import date
from typing import Any

import requests
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── optional geo imports (graceful degradation) ─────────────────────────────
try:
    import fiona
    HAS_FIONA = True
except ImportError:
    HAS_FIONA = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import geopandas as gpd
    HAS_GPD = True
except ImportError:
    HAS_GPD = False

# ── page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ingest Vector",
    layout="wide",
)

# ── constants ────────────────────────────────────────────────────────────────
VECTOR_FORMATS = ["GeoJSON", "Shapefile (zip)", "GeoPackage", "CSV", "CityJSON"]
RASTER_FORMATS = ["GeoTIFF", "COG", "NetCDF", "HDF5", "Other"]

OGC_TYPES = ["WFS", "WMS", "WCS", "WMTS", "OGC API Features"]

PK_POLICIES = [
    "uuid_per_row   — generate UUID for every feature",
    "natural_key    — use an existing column as PK",
    "serial         — let the DB assign a sequential integer",
]

STEP_LABELS = [
    "1 · Source",
    "2 · Classification",
    "3 · Standard metadata",
    "4 · Profile",
    "5 · Column mapping",
    "6 · Manifest",
]

TOTAL_STEPS = len(STEP_LABELS)


# ── session state helpers ────────────────────────────────────────────────────
def _init():
    defaults: dict[str, Any] = {
        "step":            1,
        "source_type":     None,     # "file" | "ogc"
        "uploaded_file":   None,
        "ogc_url":         "",
        "ogc_type":        "WFS",
        "ogc_layers":      [],
        "ogc_layer":       None,
        "is_spatial":      True,
        "data_class":      "vector",  # "vector" | "raster"
        "vector_format":   None,
        "raster_format":   None,
        "csv_lon":         None,
        "csv_lat":         None,
        "csv_wkt":         None,
        "gpkg_layer":      None,
        "has_std_meta":    False,
        "std_meta_mode":   "paste",   # "paste" | "csw"
        "std_meta_raw":    "",
        "std_meta_parsed": {},
        "meta_name":       "",
        "meta_desc":       "",
        "meta_tags":       "",
        "meta_crs":        "EPSG:4326",
        "meta_t_start":    None,
        "meta_t_end":      None,
        "columns":         [],        # profiled column list
        "detected_crs":    None,      # CRS string read from the file
        "geom_type":       None,      # geometry type detected from file
        "feature_count":   None,      # feature count (sample or exact)
        "pk_policy":       PK_POLICIES[0],
        "pk_natural_col":  None,
        "fk_cols":         [],
        "spatial_cols":    [],
        "nonspatial_cols": [],
        "dropped_cols":    [],
        "geom_col":        None,
        "target_crs":      "EPSG:4326",
        "manifest":        {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()
S = st.session_state  # shorthand


# ── nav helpers ──────────────────────────────────────────────────────────────
def _goto(step: int):
    S.step = max(1, min(step, TOTAL_STEPS))
    st.rerun()


def _nav_bar():
    cols = st.columns(TOTAL_STEPS)
    for i, label in enumerate(STEP_LABELS, start=1):
        with cols[i - 1]:
            if i < S.step:
                st.button(f"[done] {label}", key=f"nav_{i}", use_container_width=True,
                          on_click=_goto, args=(i,))
            elif i == S.step:
                st.button(f">> {label}", key=f"nav_{i}", use_container_width=True,
                          disabled=True)
            else:
                st.button(label, key=f"nav_{i}", use_container_width=True,
                          disabled=True)


# ── file profilers ────────────────────────────────────────────────────────────

def _profile_geojson(raw: bytes) -> tuple[list[str], str | None, str | None, str | None, int | None]:
    """Return (columns, geom_col, detected_crs, geom_type, feature_count)."""
    data = json.loads(raw)
    features = data.get("features") or []
    cols: set[str] = set()
    geom_col = "__geometry__"
    for f in features[:50]:
        cols.update((f.get("properties") or {}).keys())

    # GeoJSON spec: CRS is always EPSG:4326 unless a legacy `crs` member is present
    crs = "EPSG:4326"
    crs_member = data.get("crs") or {}
    props_crs = (crs_member.get("properties") or {})
    if props_crs.get("name"):
        crs = props_crs["name"]  # e.g. "urn:ogc:def:crs:EPSG::3857"

    geom_type = None
    if features:
        geom_type = (features[0].get("geometry") or {}).get("type")

    return sorted(cols) + [geom_col], geom_col, crs, geom_type, len(features)


def _profile_shapefile_zip(raw: bytes) -> tuple[list[str], str | None, str | None, str | None, int | None]:
    if not HAS_FIONA:
        st.warning("fiona not installed — cannot profile shapefile. Install it with `pip install fiona`.")
        return [], None, None, None, None
    with tempfile.TemporaryDirectory() as tmp:
        zpath = os.path.join(tmp, "upload.zip")
        with open(zpath, "wb") as f:
            f.write(raw)
        with zipfile.ZipFile(zpath) as zf:
            zf.extractall(tmp)
        shps = [os.path.join(tmp, n) for n in os.listdir(tmp) if n.endswith(".shp")]
        if not shps:
            st.error("No .shp file found inside the zip.")
            return [], None, None, None, None
        with fiona.open(shps[0]) as src:
            props = list(src.schema["properties"].keys())
            geom_type = src.schema["geometry"]
            crs = _crs_to_epsg(src.crs)
            count = len(src) if len(src) < 200_000 else None
            return sorted(props) + ["__geometry__"], "__geometry__", crs, geom_type, count


def _profile_gpkg(raw: bytes) -> tuple[list[str], str | None, list[str]]:
    """Returns (columns, geom_col, available_layers)."""
    if not HAS_FIONA:
        st.warning("fiona not installed — cannot profile GPKG.")
        return [], None, []
    with tempfile.NamedTemporaryFile(suffix=".gpkg", delete=False) as tmp:
        tmp.write(raw)
        tmp_path = tmp.name
    try:
        layers = fiona.listlayers(tmp_path)
        return [], None, layers
    finally:
        os.unlink(tmp_path)


def _profile_gpkg_layer(raw: bytes, layer: str) -> tuple[list[str], str | None, str | None, str | None, int | None]:
    if not HAS_FIONA:
        return [], None, None, None, None
    with tempfile.NamedTemporaryFile(suffix=".gpkg", delete=False) as tmp:
        tmp.write(raw)
        tmp_path = tmp.name
    try:
        with fiona.open(tmp_path, layer=layer) as src:
            props = list(src.schema["properties"].keys())
            geom_type = src.schema["geometry"]
            crs = _crs_to_epsg(src.crs)
            count = len(src) if len(src) < 200_000 else None
            return sorted(props) + ["__geometry__"], "__geometry__", crs, geom_type, count
    finally:
        os.unlink(tmp_path)


def _profile_csv(raw: bytes) -> tuple[list[str], int | None]:
    if not HAS_PANDAS:
        st.warning("pandas not installed — cannot profile CSV.")
        return [], None
    df_head = pd.read_csv(io.BytesIO(raw), nrows=5)
    try:
        total = sum(1 for _ in io.BytesIO(raw)) - 1  # subtract header
    except Exception:
        total = None
    return list(df_head.columns), total


def _profile_cityjson(raw: bytes) -> tuple[list[str], str | None, str | None, str | None, int | None]:
    data = json.loads(raw)
    cols: set[str] = set()
    geom_col = "__geometry__"
    city_objects = data.get("CityObjects") or {}
    for obj in list(city_objects.values())[:50]:
        cols.update((obj.get("attributes") or {}).keys())

    # CityJSON stores CRS in metadata.referenceSystem
    crs = None
    meta = data.get("metadata") or {}
    ref_sys = meta.get("referenceSystem") or ""
    if ref_sys:
        # normalise "https://www.opengis.net/def/crs/EPSG/0/28992" → "EPSG:28992"
        parts = ref_sys.rstrip("/").split("/")
        if len(parts) >= 2 and parts[-2].upper() == "EPSG":
            crs = f"EPSG:{parts[-1]}"
        elif "EPSG" in ref_sys.upper():
            import re
            m = re.search(r"EPSG[:/](\d+)", ref_sys, re.IGNORECASE)
            crs = f"EPSG:{m.group(1)}" if m else ref_sys
        else:
            crs = ref_sys
    if not crs:
        crs = "EPSG:4326"

    geom_types: set[str] = set()
    for obj in list(city_objects.values())[:50]:
        for g in obj.get("geometry") or []:
            if g.get("type"):
                geom_types.add(g["type"])
    geom_type = ", ".join(sorted(geom_types)) or None

    return sorted(cols) + [geom_col], geom_col, crs, geom_type, len(city_objects)


# ── CRS normaliser ────────────────────────────────────────────────────────────

def _crs_to_epsg(crs_obj: Any) -> str | None:
    """Convert a fiona CRS object / dict / string to a human-readable EPSG string."""
    if crs_obj is None:
        return None
    # fiona >= 1.9 returns a CRS object with .to_epsg() or .to_wkt()
    if hasattr(crs_obj, "to_epsg"):
        try:
            epsg = crs_obj.to_epsg()
            if epsg:
                return f"EPSG:{epsg}"
        except Exception:
            pass
    if hasattr(crs_obj, "to_authority"):
        try:
            auth = crs_obj.to_authority()
            if auth:
                return f"{auth[0]}:{auth[1]}"
        except Exception:
            pass
    if hasattr(crs_obj, "to_wkt"):
        try:
            return _wkt_to_epsg_label(crs_obj.to_wkt())
        except Exception:
            pass
    # dict form {"init": "epsg:4326"} (fiona < 1.9)
    if isinstance(crs_obj, dict):
        init = crs_obj.get("init", "")
        if init:
            return init.upper().replace("EPSG:", "EPSG:")
    if isinstance(crs_obj, str):
        return _wkt_to_epsg_label(crs_obj) or crs_obj
    return str(crs_obj)


def _wkt_to_epsg_label(wkt: str) -> str | None:
    """Try to extract AUTHORITY["EPSG","XXXX"] from WKT string."""
    import re
    m = re.search(r'AUTHORITY\["EPSG",\s*"(\d+)"\]', wkt, re.IGNORECASE)
    if m:
        return f"EPSG:{m.group(1)}"
    m = re.search(r'ID\["EPSG",\s*(\d+)\]', wkt, re.IGNORECASE)
    if m:
        return f"EPSG:{m.group(1)}"
    return None


def _profile_wfs_crs(url: str, ogc_type: str) -> str | None:
    """Attempt to read CRS from a WFS DescribeFeatureType / OGC API conformance."""
    try:
        if ogc_type == "OGC API Features":
            r = requests.get(url, params={"limit": 1, "f": "json"}, timeout=10)
            r.raise_for_status()
            crs_uri = r.json().get("crs") or r.json().get("storageCrs")
            if crs_uri:
                import re
                m = re.search(r"EPSG[:/](\d+)", str(crs_uri), re.IGNORECASE)
                return f"EPSG:{m.group(1)}" if m else str(crs_uri)
            return "EPSG:4326"  # OGC API default
    except Exception:
        pass
    return None


def _profile_wfs(url: str, ogc_type: str) -> list[str]:
    """Fetch first page of a WFS / OGC API Features and extract property names."""
    try:
        if ogc_type == "OGC API Features":
            r = requests.get(url, params={"limit": 1, "f": "json"}, timeout=10)
            r.raise_for_status()
            fc = r.json()
        else:
            params = {
                "service": "WFS", "version": "2.0.0",
                "request": "GetFeature", "count": "1", "outputFormat": "application/json",
            }
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            fc = r.json()
        features = fc.get("features") or []
        if features:
            props = list((features[0].get("properties") or {}).keys())
            return sorted(props) + ["__geometry__"]
    except Exception as exc:
        st.warning(f"Could not fetch WFS sample: {exc}")
    return []


def _list_wfs_layers(url: str, ogc_type: str) -> list[str]:
    try:
        if ogc_type == "OGC API Features":
            r = requests.get(url.rstrip("/") + "/collections", params={"f": "json"}, timeout=10)
            r.raise_for_status()
            return [c["id"] for c in r.json().get("collections", [])]
        else:
            params = {"service": "WFS", "version": "2.0.0", "request": "GetCapabilities"}
            r = requests.get(url, params=params, timeout=12)
            r.raise_for_status()
            import xml.etree.ElementTree as ET
            root = ET.fromstring(r.content)
            ns = {"wfs": "http://www.opengis.net/wfs/2.0"}
            names = [
                el.text.strip()
                for el in root.findall(".//wfs:FeatureType/wfs:Name", ns)
                if el.text
            ]
            return names
    except Exception as exc:
        st.warning(f"Could not list WFS layers: {exc}")
    return []


# ── standard metadata parsers ─────────────────────────────────────────────────

def _parse_iso19139(xml_text: str) -> dict:
    import xml.etree.ElementTree as ET
    out: dict = {}
    try:
        root = ET.fromstring(xml_text)
        ns = {
            "gmd": "http://www.isotc211.org/2005/gmd",
            "gco": "http://www.isotc211.org/2005/gco",
            "gml": "http://www.opengis.net/gml",
        }
        def _txt(path):
            el = root.find(path, ns)
            return el.text.strip() if el is not None and el.text else None

        out["name"]  = _txt(".//gmd:title/gco:CharacterString")
        out["desc"]  = _txt(".//gmd:abstract/gco:CharacterString")
        out["crs"]   = _txt(".//gmd:referenceSystemIdentifier//gmd:code/gco:CharacterString")

        kw_els = root.findall(".//gmd:keyword/gco:CharacterString", ns)
        out["tags"] = ", ".join(el.text.strip() for el in kw_els if el.text)

        t_begin = _txt(".//gmd:temporalElement//gml:beginPosition")
        t_end   = _txt(".//gmd:temporalElement//gml:endPosition")
        out["temporal_start"] = t_begin[:10] if t_begin else None
        out["temporal_end"]   = t_end[:10]   if t_end   else None
    except Exception as exc:
        st.warning(f"ISO 19139 parse warning: {exc}")
    return {k: v for k, v in out.items() if v}


def _parse_ogc_records(json_text: str) -> dict:
    out: dict = {}
    try:
        rec = json.loads(json_text)
        out["name"]  = rec.get("title", "")
        out["desc"]  = rec.get("description", "")
        themes = rec.get("themes", [])
        kws = [c for t in themes for c in t.get("concepts", [])]
        out["tags"] = ", ".join(str(k.get("id", k)) if isinstance(k, dict) else str(k) for k in kws)
        time_obj = rec.get("time", {})
        out["temporal_start"] = (time_obj.get("interval") or [None, None])[0]
        out["temporal_end"]   = (time_obj.get("interval") or [None, None])[-1]
    except Exception as exc:
        st.warning(f"OGC Records parse warning: {exc}")
    return {k: v for k, v in out.items() if v}


def _apply_parsed_meta(parsed: dict):
    if parsed.get("name"):        S.meta_name  = parsed["name"]
    if parsed.get("desc"):        S.meta_desc  = parsed["desc"]
    if parsed.get("tags"):        S.meta_tags  = parsed["tags"]
    if parsed.get("crs"):         S.meta_crs   = parsed["crs"]
    if parsed.get("temporal_start"): S.meta_t_start = date.fromisoformat(parsed["temporal_start"][:10])
    if parsed.get("temporal_end"):   S.meta_t_end   = date.fromisoformat(parsed["temporal_end"][:10])


# ── manifest builder ──────────────────────────────────────────────────────────

def _build_manifest() -> dict:
    pk_policy_key = S.pk_policy.split()[0]  # "uuid_per_row" | "natural_key" | "serial"

    source: dict = {"type": S.source_type}
    if S.source_type == "file" and S.uploaded_file:
        source["filename"]    = S.uploaded_file.name
        source["file_format"] = S.vector_format or S.raster_format
        if S.vector_format == "GeoPackage" and S.gpkg_layer:
            source["layer"] = S.gpkg_layer
    elif S.source_type == "ogc":
        source["url"]      = S.ogc_url
        source["ogc_type"] = S.ogc_type
        if S.ogc_layer:
            source["layer"] = S.ogc_layer

    registry: dict = {
        "name":           S.meta_name,
        "description":    S.meta_desc,
        "tags":           [t.strip() for t in S.meta_tags.split(",") if t.strip()],
        "crs":            S.meta_crs,
        "temporal_start": str(S.meta_t_start) if S.meta_t_start else None,
        "temporal_end":   str(S.meta_t_end)   if S.meta_t_end   else None,
    }

    pk_block: dict = {"policy": pk_policy_key}
    if pk_policy_key == "natural_key":
        pk_block["source_column"] = S.pk_natural_col
    elif pk_policy_key == "uuid_per_row":
        pk_block["warehouse_column"] = "id"

    fk_block = [
        {"source_column": c, "references": "dim_dataset.dataset_id"}
        for c in S.fk_cols
    ] if S.fk_cols else [
        {"generated": True, "references": "dim_dataset.dataset_id",
         "note": "dataset_id auto-assigned by ingest worker from registry row"}
    ]

    spatial_block: dict | None = None
    if S.is_spatial and S.data_class == "vector":
        spatial_block = {
            "source_crs":  S.detected_crs or S.meta_crs or "unknown",
            "target_crs":  S.target_crs,
            "reproject":   (
                bool(S.detected_crs)
                and bool(S.target_crs)
                and S.detected_crs.upper() != S.target_crs.upper()
            ),
        }
        if S.geom_col and S.geom_col != "__geometry__":
            spatial_block["source_type"] = "columns"
            if S.vector_format == "CSV":
                spatial_block["lon_column"] = S.csv_lon
                spatial_block["lat_column"] = S.csv_lat
                if S.csv_wkt:
                    spatial_block["wkt_column"] = S.csv_wkt
            else:
                spatial_block["geom_column"] = S.geom_col
        else:
            spatial_block["source_type"] = "native"
            spatial_block["geom_column"] = "__geometry__"

    nonspatial_block = {
        "strategy":    "jsonb",
        "target_column": "attributes",
        "include": S.nonspatial_cols,
        "exclude": S.dropped_cols,
    }

    return {
        "ingest_manifest_version": "1.0",
        "manifest_id":             str(uuid.uuid4()),
        "source":                  source,
        "profile": {
            "detected_crs":  S.detected_crs,
            "geom_type":     S.geom_type,
            "feature_count": S.feature_count,
        },
        "registry":                registry,
        "warehouse_mapping": {
            "pk":          pk_block,
            "fk":          fk_block,
            "spatial":     spatial_block,
            "non_spatial": nonspatial_block,
        },
        "standard_metadata": S.std_meta_parsed if S.has_std_meta else None,
    }


# ────────────────────────────────────────────────────────────────────────────
# PAGE HEADER
# ────────────────────────────────────────────────────────────────────────────
st.title("Ingest Vector — Warehouse Wizard")
st.caption(
    "Step-by-step ingest: define source → classify data → map columns → "
    "generate the **ingest manifest JSON** for the warehouse loader."
)
_nav_bar()
st.divider()


# ────────────────────────────────────────────────────────────────────────────
# STEP 1 — SOURCE
# ────────────────────────────────────────────────────────────────────────────
if S.step == 1:
    st.subheader("Step 1 — Data source")

    src = st.radio(
        "Where is the data coming from?",
        ["File upload", "OGC service (WFS / OGC API Features)"],
        horizontal=True,
        index=0 if S.source_type != "ogc" else 1,
    )
    S.source_type = "file" if src == "File upload" else "ogc"

    if S.source_type == "file":
        uploaded = st.file_uploader(
            "Upload your dataset",
            type=["geojson", "json", "zip", "gpkg", "csv", "gz"],
            help="Supported: GeoJSON, Shapefile (.zip), GeoPackage (.gpkg), CSV, CityJSON (.json/.json.gz)",
        )
        if uploaded:
            S.uploaded_file = uploaded
            st.success(f"File loaded: **{uploaded.name}**  ({uploaded.size / 1024:.1f} KB)")
    else:
        S.ogc_url  = st.text_input("Service base URL", value=S.ogc_url,
                                   placeholder="https://example.org/wfs?")
        S.ogc_type = st.selectbox("Service type", OGC_TYPES,
                                  index=OGC_TYPES.index(S.ogc_type))
        if S.ogc_url.strip():
            if st.button("List layers", key="list_layers"):
                with st.spinner("Fetching capabilities…"):
                    S.ogc_layers = _list_wfs_layers(S.ogc_url.strip(), S.ogc_type)
            if S.ogc_layers:
                S.ogc_layer = st.selectbox("Select layer", S.ogc_layers)
            elif S.ogc_url.strip():
                st.info("Click **List layers** to fetch the available layers.")

    st.divider()
    ready = (S.source_type == "file" and S.uploaded_file) or \
            (S.source_type == "ogc"  and S.ogc_url.strip())
    if st.button("Next →", type="primary", disabled=not ready):
        _goto(2)


# ────────────────────────────────────────────────────────────────────────────
# STEP 2 — CLASSIFICATION
# ────────────────────────────────────────────────────────────────────────────
elif S.step == 2:
    st.subheader("Step 2 — Classify the dataset")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Spatial or non-spatial?**")
        S.is_spatial = st.toggle("This dataset contains spatial data", value=S.is_spatial)

    if S.is_spatial:
        with col_b:
            data_class = st.radio(
                "Data class",
                ["Vector", "Raster"],
                index=0 if S.data_class == "vector" else 1,
                horizontal=True,
            )
            S.data_class = data_class.lower()

    if S.is_spatial and S.data_class == "vector":
        st.markdown("**Vector format**")

        if S.source_type == "file" and S.uploaded_file:
            name = S.uploaded_file.name.lower()
            auto = None
            if name.endswith((".geojson", ".json")):
                auto = "GeoJSON"
                try:
                    raw = S.uploaded_file.read()
                    data = json.loads(raw)
                    S.uploaded_file.seek(0)
                    if "CityObjects" in data:
                        auto = "CityJSON"
                except Exception:
                    pass
            elif name.endswith(".zip"):
                auto = "Shapefile (zip)"
            elif name.endswith(".gpkg"):
                auto = "GeoPackage"
            elif name.endswith(".csv"):
                auto = "CSV"

            if auto and not S.vector_format:
                S.vector_format = auto
                st.info(f"Format auto-detected: **{auto}**")

            S.vector_format = st.selectbox(
                "Vector format",
                VECTOR_FORMATS,
                index=VECTOR_FORMATS.index(S.vector_format) if S.vector_format in VECTOR_FORMATS else 0,
            )

            if S.vector_format == "CSV":
                st.markdown("**CSV coordinate columns**")
                cols_csv = _profile_csv(S.uploaded_file.read())
                S.uploaded_file.seek(0)
                coord_col1, coord_col2, coord_col3 = st.columns(3)
                with coord_col1:
                    S.csv_lon = st.selectbox("Longitude column", ["—"] + cols_csv,
                                              index=(cols_csv.index(S.csv_lon) + 1) if S.csv_lon in cols_csv else 0)
                with coord_col2:
                    S.csv_lat = st.selectbox("Latitude column",  ["—"] + cols_csv,
                                              index=(cols_csv.index(S.csv_lat) + 1) if S.csv_lat in cols_csv else 0)
                with coord_col3:
                    S.csv_wkt = st.selectbox("WKT column (optional)", ["—"] + cols_csv)
                S.csv_lon = None if S.csv_lon == "—" else S.csv_lon
                S.csv_lat = None if S.csv_lat == "—" else S.csv_lat
                S.csv_wkt = None if S.csv_wkt == "—" else S.csv_wkt

            if S.vector_format == "GeoPackage":
                raw = S.uploaded_file.read()
                S.uploaded_file.seek(0)
                _, _, layers = _profile_gpkg(raw)
                if layers:
                    S.gpkg_layer = st.selectbox("GPKG layer", layers)
                else:
                    S.gpkg_layer = st.text_input("GPKG layer name (fiona not available)")

        elif S.source_type == "ogc":
            st.info(f"Source type: OGC **{S.ogc_type}** — format will be profiled at next step.")
            S.vector_format = "OGC"

    elif S.is_spatial and S.data_class == "raster":
        S.raster_format = st.selectbox("Raster format", RASTER_FORMATS)
        st.info("Raster ingestion produces a catalogue record only (no feature row ETL). Column mapping step will be skipped.")

    elif not S.is_spatial:
        st.info("Non-spatial datasets are stored as plain JSONB rows (no geometry column). Column mapping still applies.")
        if S.source_type == "file" and S.uploaded_file:
            name = S.uploaded_file.name.lower()
            S.vector_format = "GeoJSON" if name.endswith((".json", ".geojson")) else "CSV"

    st.divider()
    col_back, col_next = st.columns([1, 5])
    with col_back:
        if st.button("← Back"):
            _goto(1)
    with col_next:
        if st.button("Next →", type="primary"):
            _goto(3)


# ────────────────────────────────────────────────────────────────────────────
# STEP 3 — STANDARD METADATA (optional)
# ────────────────────────────────────────────────────────────────────────────
elif S.step == 3:
    st.subheader("Step 3 — Standard metadata  *(optional)*")

    st.markdown(
        "If you have an **ISO 19139 XML** record or an **OGC API Records** JSON for this dataset, "
        "paste it below and the wizard will pre-fill the registry fields automatically. "
        "Skip this step if you want to fill the form manually."
    )

    S.has_std_meta = st.toggle(
        "I have machine-readable catalog metadata (ISO 19139 / OGC API Records)",
        value=S.has_std_meta,
    )

    if S.has_std_meta:
        S.std_meta_mode = st.radio(
            "Metadata source",
            ["Paste text", "Fetch from CSW endpoint"],
            horizontal=True,
            index=0 if S.std_meta_mode == "paste" else 1,
        )

        if S.std_meta_mode == "Paste text":
            meta_format = st.radio(
                "Format",
                ["ISO 19139 (XML)", "OGC API Records (JSON)"],
                horizontal=True,
            )
            S.std_meta_raw = st.text_area(
                "Paste metadata here",
                value=S.std_meta_raw,
                height=220,
                placeholder="<MD_Metadata …>  or  { \"type\": \"Feature\", … }",
            )
            if st.button("Parse & pre-fill", key="parse_meta"):
                with st.spinner("Parsing…"):
                    if meta_format.startswith("ISO"):
                        S.std_meta_parsed = _parse_iso19139(S.std_meta_raw)
                    else:
                        S.std_meta_parsed = _parse_ogc_records(S.std_meta_raw)
                    _apply_parsed_meta(S.std_meta_parsed)
                st.success(f"Parsed {len(S.std_meta_parsed)} field(s): {list(S.std_meta_parsed.keys())}")

        else:  # CSW fetch
            csw_url = st.text_input(
                "CSW base URL",
                placeholder="https://csw.example.org/geonetwork/srv/eng/csw",
            )
            record_id = st.text_input("Record identifier (fileIdentifier)")
            if st.button("Fetch from CSW", key="fetch_csw"):
                if csw_url and record_id:
                    try:
                        params = {
                            "service": "CSW", "version": "2.0.2",
                            "request": "GetRecordById",
                            "id": record_id,
                            "elementSetName": "full",
                            "outputSchema": "http://www.isotc211.org/2005/gmd",
                        }
                        r = requests.get(csw_url, params=params, timeout=15)
                        r.raise_for_status()
                        S.std_meta_parsed = _parse_iso19139(r.text)
                        _apply_parsed_meta(S.std_meta_parsed)
                        st.success(f"Fetched and parsed {len(S.std_meta_parsed)} field(s).")
                    except Exception as exc:
                        st.error(f"CSW fetch failed: {exc}")
                else:
                    st.warning("Provide both a CSW URL and a record ID.")

    st.divider()
    st.markdown("### Dataset registry fields")
    st.caption("These become a row in `public.meta_table` (or `dw.dim_dataset`). Pre-filled from standard metadata when available.")

    fm_col1, fm_col2 = st.columns(2)
    with fm_col1:
        S.meta_name  = st.text_input("Dataset name *",   value=S.meta_name,
                                      placeholder="e.g. Turin Buildings 2024")
        S.meta_desc  = st.text_area("Description",       value=S.meta_desc, height=90)
        S.meta_tags  = st.text_input("Tags (comma-separated)", value=S.meta_tags,
                                      placeholder="buildings, urban, 2024")
    with fm_col2:
        S.meta_crs     = st.text_input("CRS", value=S.meta_crs)
        S.meta_t_start = st.date_input("Temporal start", value=S.meta_t_start)
        S.meta_t_end   = st.date_input("Temporal end",   value=S.meta_t_end)

    st.divider()
    col_back, col_next = st.columns([1, 5])
    with col_back:
        if st.button("← Back"):
            _goto(2)
    with col_next:
        can_proceed = bool(S.meta_name.strip())
        if st.button("Next →", type="primary", disabled=not can_proceed):
            _goto(4)
        if not can_proceed:
            st.caption("Dataset name is required.")


# ────────────────────────────────────────────────────────────────────────────
# STEP 4 — PROFILE
# ────────────────────────────────────────────────────────────────────────────
elif S.step == 4:
    st.subheader("Step 4 — Profile the dataset")
    st.caption(
        "Reads column names, CRS, geometry type and feature count from the file "
        "(small sample only — no full parse)."
    )

    # ── Auto-profile on first arrival ────────────────────────────────────
    if S.source_type == "file" and S.uploaded_file and not S.columns:
        with st.spinner("Profiling…"):
            raw = S.uploaded_file.read()
            S.uploaded_file.seek(0)
            fmt = S.vector_format

            if fmt in ("GeoJSON", "CityJSON"):
                try:
                    data = json.loads(raw)
                    if "CityObjects" in data:
                        S.columns, S.geom_col, S.detected_crs, S.geom_type, S.feature_count = _profile_cityjson(raw)
                    else:
                        S.columns, S.geom_col, S.detected_crs, S.geom_type, S.feature_count = _profile_geojson(raw)
                except Exception as exc:
                    st.error(f"JSON parse error: {exc}")

            elif fmt == "Shapefile (zip)":
                S.columns, S.geom_col, S.detected_crs, S.geom_type, S.feature_count = _profile_shapefile_zip(raw)

            elif fmt == "GeoPackage":
                layer = S.gpkg_layer or ""
                S.columns, S.geom_col, S.detected_crs, S.geom_type, S.feature_count = _profile_gpkg_layer(raw, layer)

            elif fmt == "CSV":
                S.columns, S.feature_count = _profile_csv(raw)
                S.geom_col = None
                S.detected_crs = None
                S.geom_type = None

            else:
                S.columns = []

    elif S.source_type == "ogc" and S.ogc_url and not S.columns:
        with st.spinner("Sampling OGC service…"):
            url = S.ogc_url
            if S.ogc_type == "OGC API Features" and S.ogc_layer:
                url = S.ogc_url.rstrip("/") + f"/collections/{S.ogc_layer}/items"
            S.columns = _profile_wfs(url, S.ogc_type)
            if S.columns:
                S.geom_col = "__geometry__"
            S.detected_crs = _profile_wfs_crs(url, S.ogc_type)

    # ── Profile summary card ──────────────────────────────────────────────
    if S.columns:
        st.success(f"Found **{len(S.columns)}** column(s).")

        summary_cols = st.columns(4)
        with summary_cols[0]:
            st.metric("Columns", len(S.columns))
        with summary_cols[1]:
            count_label = str(S.feature_count) if S.feature_count is not None else "unknown"
            st.metric("Features (sample)", count_label)
        with summary_cols[2]:
            st.metric("Geometry type", S.geom_type or "—")
        with summary_cols[3]:
            st.metric("Detected CRS", S.detected_crs or "—")

        # ── CRS panel ─────────────────────────────────────────────────────
        st.divider()
        st.markdown("#### CRS / Coordinate Reference System")

        crs_col1, crs_col2 = st.columns([2, 3])
        with crs_col1:
            detected_label = S.detected_crs or "Could not detect"
            st.markdown(f"**Detected from file:** `{detected_label}`")

            needs_reproject = (
                S.detected_crs is not None
                and S.detected_crs.upper() != S.meta_crs.upper()
                and S.meta_crs.strip() != ""
            )
            if needs_reproject:
                st.warning(
                    f"Source CRS `{S.detected_crs}` differs from target CRS `{S.meta_crs}`. "
                    "The ETL worker will reproject."
                )
            elif S.detected_crs:
                st.success("Source and target CRS match — no reprojection needed.")
            else:
                st.info("CRS could not be auto-detected. Set it manually below.")

        with crs_col2:
            new_crs = st.text_input(
                "Override detected CRS (if wrong)",
                value=S.detected_crs or "",
                placeholder="e.g. EPSG:32632",
                key="crs_override",
            )
            if new_crs.strip():
                S.detected_crs = new_crs.strip()

            target_crs_step4 = st.text_input(
                "Target storage CRS (warehouse)",
                value=S.meta_crs or "EPSG:4326",
                key="target_crs_step4",
            )
            S.meta_crs = target_crs_step4
            S.target_crs = target_crs_step4

        # ── Column list ───────────────────────────────────────────────────
        st.divider()
        st.markdown("#### Columns detected")
        col_grid = st.columns(4)
        for i, c in enumerate(S.columns):
            marker = " [geom]" if c == S.geom_col else ""
            col_grid[i % 4].code(f"{c}{marker}")

    else:
        st.warning("No columns detected. You can still proceed and assign them manually.")
        manual_cols = st.text_area(
            "Enter column names manually (one per line)",
            placeholder="id\nname\ngeometry\npopulation\narea_sqm",
        )
        if manual_cols.strip():
            S.columns = [c.strip() for c in manual_cols.splitlines() if c.strip()]

        manual_crs = st.text_input(
            "Source CRS (manual)",
            placeholder="EPSG:4326",
            key="manual_crs",
        )
        if manual_crs.strip():
            S.detected_crs = manual_crs.strip()

    if st.button("Re-profile", key="reprofile"):
        S.columns = []
        S.geom_col = None
        S.detected_crs = None
        S.geom_type = None
        S.feature_count = None
        st.rerun()

    st.divider()
    col_back, col_next = st.columns([1, 5])
    with col_back:
        if st.button("← Back"):
            _goto(3)
    with col_next:
        if st.button("Next →", type="primary"):
            # Propagate detected CRS to meta_crs if user has not set it yet
            if S.detected_crs and not S.meta_crs:
                S.meta_crs = S.detected_crs
            _goto(5)


# ────────────────────────────────────────────────────────────────────────────
# STEP 5 — COLUMN MAPPING
# ────────────────────────────────────────────────────────────────────────────
elif S.step == 5:
    st.subheader("Step 5 — Column mapping")
    st.caption(
        "Assign each column to its warehouse role. "
        "Every non-assigned column goes into the `attributes` JSONB column."
    )

    cols = S.columns or []
    geom_col = S.geom_col

    # ── PK ────────────────────────────────────────────────────────────────
    st.markdown("### Primary Key (PK)")
    pk_idx = PK_POLICIES.index(S.pk_policy) if S.pk_policy in PK_POLICIES else 0
    S.pk_policy = st.radio("PK strategy", PK_POLICIES, index=pk_idx)
    if "natural_key" in S.pk_policy:
        S.pk_natural_col = st.selectbox(
            "Natural key column",
            ["—"] + [c for c in cols if c != geom_col],
        )
        S.pk_natural_col = None if S.pk_natural_col == "—" else S.pk_natural_col

    st.divider()

    # ── FK ────────────────────────────────────────────────────────────────
    st.markdown("### Foreign Key(s) (FK)")
    st.caption(
        "Typically **none** from the file itself — the FK to `dim_dataset` is auto-assigned "
        "by the ingest worker. Select here only if the file already contains relationship keys."
    )
    fk_options = [c for c in cols if c != geom_col]
    S.fk_cols = st.multiselect(
        "FK column(s) in the source file",
        fk_options,
        default=[c for c in S.fk_cols if c in fk_options],
    )

    st.divider()

    # ── Spatial ───────────────────────────────────────────────────────────
    if S.is_spatial and S.data_class == "vector":
        st.markdown("### Spatial column(s)")
        S.target_crs = st.text_input("Target storage CRS", value=S.target_crs)

        if S.vector_format == "CSV":
            st.info(
                f"Geometry will be built from lat/lon columns set in Step 2:  "
                f"**lon** = `{S.csv_lon}`  /  **lat** = `{S.csv_lat}`"
                + (f"  /  **WKT** = `{S.csv_wkt}`" if S.csv_wkt else "")
            )
        else:
            geom_options = [c for c in cols if "geom" in c.lower() or c == geom_col]
            if not geom_options:
                geom_options = cols
            default_geom = geom_col if geom_col in geom_options else (geom_options[0] if geom_options else None)
            S.geom_col = st.selectbox(
                "Geometry column",
                geom_options,
                index=geom_options.index(default_geom) if default_geom in geom_options else 0,
            )
        st.divider()

    # ── Non-spatial ───────────────────────────────────────────────────────
    st.markdown("### Non-spatial columns → `attributes` JSONB")
    reserved = set([S.geom_col or ""] + S.fk_cols +
                   ([S.pk_natural_col] if S.pk_natural_col else []))
    remaining = [c for c in cols if c not in reserved]

    sub1, sub2 = st.columns(2)
    with sub1:
        st.markdown("**Include in JSONB**")
        default_include = [c for c in S.nonspatial_cols if c in remaining] or remaining
        S.nonspatial_cols = st.multiselect(
            "Include",
            remaining,
            default=default_include,
            label_visibility="collapsed",
        )
    with sub2:
        st.markdown("**Drop (exclude entirely)**")
        droppable = [c for c in remaining if c not in S.nonspatial_cols]
        default_drop = [c for c in S.dropped_cols if c in droppable]
        S.dropped_cols = st.multiselect(
            "Drop",
            droppable,
            default=default_drop,
            label_visibility="collapsed",
        )

    unmapped = [c for c in remaining if c not in S.nonspatial_cols and c not in S.dropped_cols]
    if unmapped:
        st.warning(f"{len(unmapped)} column(s) are unmapped and will default to JSONB: {unmapped}")

    st.divider()
    col_back, col_next = st.columns([1, 5])
    with col_back:
        if st.button("← Back"):
            _goto(4)
    with col_next:
        if st.button("Build manifest →", type="primary"):
            S.manifest = _build_manifest()
            _goto(6)


# ────────────────────────────────────────────────────────────────────────────
# STEP 6 — MANIFEST
# ────────────────────────────────────────────────────────────────────────────
elif S.step == 6:
    st.subheader("Step 6 — Ingest manifest")
    st.caption(
        "Review the JSON payload below. Use **Regenerate** to rebuild after changes, "
        "**Download** to save locally, or **POST** to send directly to your ingest API."
    )

    if not S.manifest:
        S.manifest = _build_manifest()

    manifest_str = json.dumps(S.manifest, indent=2, default=str)

    # ── Summary card ─────────────────────────────────────────────────────
    m = S.manifest
    wm = m.get("warehouse_mapping", {})
    reg = m.get("registry", {})

    info_col, action_col = st.columns([3, 1])
    with info_col:
        st.markdown(
            f"**Dataset:** {reg.get('name', '—')}  \n"
            f"**Source:** `{m['source']['type']}`"
            + (f" · `{m['source'].get('filename', m['source'].get('url', ''))}`") + "  \n"
            f"**PK policy:** `{wm.get('pk', {}).get('policy', '—')}`  \n"
            f"**Spatial:** `{S.is_spatial}` · class `{S.data_class}`  \n"
            f"**JSONB attributes:** {len(wm.get('non_spatial', {}).get('include', []))} column(s)  \n"
            f"**Manifest ID:** `{m.get('manifest_id', '')}`"
        )
    with action_col:
        st.download_button(
            label="Download JSON",
            data=manifest_str,
            file_name=f"ingest_manifest_{m.get('manifest_id', 'out')[:8]}.json",
            mime="application/json",
            use_container_width=True,
        )
        if st.button("Regenerate", use_container_width=True):
            S.manifest = _build_manifest()
            st.rerun()

    st.divider()

    # ── JSON viewer ───────────────────────────────────────────────────────
    st.code(manifest_str, language="json")

    # ── POST section ──────────────────────────────────────────────────────
    st.divider()
    st.markdown("### Send to ingest API")
    st.caption("Optional — POST the manifest to your ingest worker / FastAPI endpoint.")

    api_url = st.text_input(
        "Ingest API endpoint",
        value="http://localhost:8000/api/v1/ingest",
        placeholder="http://your-api-host/api/v1/ingest",
    )
    api_token = st.text_input("Bearer token (optional)", type="password")

    if st.button("POST manifest", type="primary"):
        headers = {"Content-Type": "application/json"}
        if api_token.strip():
            headers["Authorization"] = f"Bearer {api_token.strip()}"
        try:
            with st.spinner("Sending…"):
                resp = requests.post(api_url, json=S.manifest, headers=headers, timeout=30)
            if resp.ok:
                st.success(f"API responded **{resp.status_code}**")
                try:
                    st.json(resp.json())
                except Exception:
                    st.text(resp.text[:2000])
            else:
                st.error(f"HTTP {resp.status_code}: {resp.text[:500]}")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the API. Is the ingest service running?")
        except Exception as exc:
            st.error(f"Request failed: {exc}")

    st.divider()
    if st.button("Start over", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
