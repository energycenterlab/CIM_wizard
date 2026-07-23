"""
ingest_api.py  —  Warehouse Ingest Wizard  (API-connected)
===========================================================
Identical 5-step flow to ingest_v_upload.py.
Steps 1-4 are unchanged.
Step 5 submits through the FastAPI backend instead of writing to the DB directly.

API base URL is read from:
  1. st.secrets["API_BASE_URL"]   (preferred — set in .streamlit/secrets.toml)
  2. Environment variable API_BASE_URL
  3. Fallback default "http://localhost:8000"
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
import tempfile
import uuid
import zipfile
from datetime import date
from typing import Any

import requests
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import minio_store  # noqa: E402

# ── optional geo deps ────────────────────────────────────────────────────────
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
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Ingest (API) — Warehouse Wizard", layout="wide")

# ── constants ─────────────────────────────────────────────────────────────────
VECTOR_FORMATS  = ["GeoJSON", "Shapefile (zip)", "GeoPackage", "CSV", "CityJSON"]
RASTER_FORMATS  = ["GeoTIFF", "COG", "NetCDF", "HDF5", "Other raster"]
NONSPATIAL_FMTS = ["JSON", "CSV", "Excel", "Parquet", "Other"]
OGC_TYPES       = ["WFS", "OGC API Features", "WMS", "WCS", "WMTS"]

PK_POLICIES = [
    "uuid_per_row   — generate UUID for every row",
    "natural_key    — use an existing column as PK",
    "serial         — let the DB assign a sequential integer",
]

STEP_LABELS = [
    "1 · Classification",
    "2 · Manifest",
    "3 · Profiling",
    "4 · Mapping",
    "5 · Submit",
]
TOTAL_STEPS = len(STEP_LABELS)


# ── API helpers ───────────────────────────────────────────────────────────────
def _api_base() -> str:
    try:
        url = st.secrets.get("API_BASE_URL", os.getenv("API_BASE_URL", "http://localhost:8000"))
    except Exception:
        url = os.getenv("API_BASE_URL", "http://localhost:8000")
    return url.rstrip("/")


def _api_headers(token: str = "") -> dict:
    h = {"Content-Type": "application/json"}
    if token.strip():
        h["Authorization"] = f"Bearer {token.strip()}"
    return h


@st.cache_data(ttl=30, show_spinner=False)
def _check_api(base: str) -> bool:
    try:
        r = requests.get(f"{base}/health", timeout=3)
        return r.ok
    except Exception:
        return False


# ── session state ─────────────────────────────────────────────────────────────
def _init():
    defaults: dict[str, Any] = {
        "step":            1,
        # step 1
        "is_spatial":      None,
        "source_type":     None,
        "data_class":      None,
        "data_format":     None,
        "uploaded_file":   None,
        "ogc_url":         "",
        "ogc_type":        "WFS",
        "ogc_layers":      [],
        "ogc_layer":       None,
        "api_url":         "",
        "csv_lon":         None,
        "csv_lat":         None,
        "csv_wkt":         None,
        "gpkg_layer":      None,
        # step 2
        "has_std_meta":    False,
        "std_meta_mode":   "paste",
        "std_meta_raw":    "",
        "std_meta_parsed": {},
        "meta_approved":   False,
        "meta_name":       "",
        "meta_desc":       "",
        "meta_tags":       "",
        "meta_crs":        "EPSG:4326",
        "meta_t_start":    None,
        "meta_t_end":      None,
        # bounding box (Step 2 — Manifest)
        "bbox":            None,   # {"west","south","east","north"} in EPSG:4326
        "bbox_corners":    None,   # {"SW","SE","NE","NW"} each [lon, lat]
        "spatial_footprint": None, # GeoJSON Polygon for meta_table / API
        # step 3
        "columns":         [],
        "detected_crs":    None,
        "geom_type":       None,
        "feature_count":   None,
        "geom_col":        None,
        # step 4
        "pk_policy":       PK_POLICIES[0],
        "pk_natural_col":  None,
        "fk_cols":         [],
        "spatial_col":     None,
        "target_crs":      "EPSG:4326",
        "nonspatial_cols": [],
        "dropped_cols":    [],
        # step 5 results
        "manifest":        {},
        "api_token":       "",
        "submit_result":   None,   # dict returned by POST /api/v1/datasources
        "object_uri":      None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init()
S = st.session_state


# ── navigation ────────────────────────────────────────────────────────────────
def _goto(step: int):
    S.step = max(1, min(step, TOTAL_STEPS))
    st.rerun()


def _nav_bar():
    cols = st.columns(TOTAL_STEPS)
    for i, label in enumerate(STEP_LABELS, start=1):
        skip = (i == 3 and S.source_type in ("ogc", "api"))
        with cols[i - 1]:
            if i < S.step:
                lbl = f"[done] {label}" + (" [skip]" if skip else "")
                st.button(lbl, key=f"nav_{i}", use_container_width=True,
                          on_click=_goto, args=(i,))
            elif i == S.step:
                st.button(f">> {label}", key=f"nav_{i}",
                          use_container_width=True, disabled=True)
            else:
                lbl = label + (" [skip]" if skip else "")
                st.button(lbl, key=f"nav_{i}",
                          use_container_width=True, disabled=True)


def _back_next(back: int, nxt: int, label: str = "Next", disabled: bool = False):
    b, n = st.columns([1, 5])
    with b:
        if st.button("Back", key=f"back_{back}"):
            _goto(back)
    with n:
        if st.button(label, type="primary", disabled=disabled, key=f"next_{nxt}"):
            _goto(nxt)


# ── profilers (identical to ingest_v_upload.py) ───────────────────────────────
def _crs_to_epsg(obj: Any) -> str | None:
    if obj is None:
        return None
    for method in ("to_epsg", "to_authority"):
        if hasattr(obj, method):
            try:
                v = getattr(obj, method)()
                if v:
                    return f"EPSG:{v}" if method == "to_epsg" else f"{v[0]}:{v[1]}"
            except Exception:
                pass
    if hasattr(obj, "to_wkt"):
        try:
            return _wkt_epsg(obj.to_wkt())
        except Exception:
            pass
    if isinstance(obj, dict):
        init = obj.get("init", "")
        return init.upper() if init else None
    if isinstance(obj, str):
        return _wkt_epsg(obj) or obj
    return str(obj)


def _wkt_epsg(wkt: str) -> str | None:
    for pat in [r'AUTHORITY\["EPSG",\s*"(\d+)"\]', r'ID\["EPSG",\s*(\d+)\]']:
        m = re.search(pat, wkt, re.IGNORECASE)
        if m:
            return f"EPSG:{m.group(1)}"
    return None


ProfileResult = tuple[list[str], str | None, str | None, str | None, int | None]


# ── bounding box helpers ──────────────────────────────────────────────────────

def _bbox_from_bounds(xmin: float, ymin: float, xmax: float, ymax: float,
                      source_crs: str | None = None) -> dict:
    """
    Normalise bounds to EPSG:4326 and return bbox + four corners + footprint.
    Corners are SW, SE, NE, NW as [lon, lat].
    """
    west, south, east, north = float(xmin), float(ymin), float(xmax), float(ymax)
    crs = (source_crs or "EPSG:4326").upper()

    if crs not in ("EPSG:4326", "WGS84", "CRS84") and HAS_GEOPANDAS:
        from shapely.geometry import box
        gdf = gpd.GeoDataFrame(geometry=[box(west, south, east, north)], crs=crs)
        gdf = gdf.to_crs("EPSG:4326")
        west, south, east, north = gdf.total_bounds

    # Guard against inverted axes after transform
    if west > east:
        west, east = east, west
    if south > north:
        south, north = north, south

    corners = {
        "SW": [west, south],
        "SE": [east, south],
        "NE": [east, north],
        "NW": [west, north],
    }
    footprint = {
        "type": "Polygon",
        "coordinates": [[
            [west, south],
            [east, south],
            [east, north],
            [west, north],
            [west, south],
        ]],
    }
    return {
        "west": west, "south": south, "east": east, "north": north,
        "crs": "EPSG:4326",
        "corners": corners,
        "footprint": footprint,
    }


def _iter_coords(obj: Any):
    """Yield [lon, lat, ...] pairs from nested GeoJSON coordinates."""
    if not isinstance(obj, (list, tuple)) or not obj:
        return
    if isinstance(obj[0], (int, float)):
        yield obj
        return
    for item in obj:
        yield from _iter_coords(item)


def _parse_json_documents(raw: bytes) -> list[Any]:
    """
    Parse one or more JSON values from bytes.

    Handles:
      - normal GeoJSON / CityJSON (single root object)
      - NDJSON / GeoJSON Text Sequences (one Feature per line / concatenated objects)
      - UTF-8 BOM
    """
    text = raw.decode("utf-8-sig").strip()
    if not text:
        raise ValueError("File is empty.")

    # Fast path: single JSON document
    try:
        return [json.loads(text)]
    except json.JSONDecodeError as exc:
        if "Extra data" not in str(exc):
            preview = text[:80].replace("\n", "\\n")
            raise ValueError(
                f"Invalid JSON ({exc}). File starts with: {preview!r}"
            ) from exc

    # Slow path: multiple JSON values (NDJSON / concatenated)
    decoder = json.JSONDecoder()
    docs: list[Any] = []
    idx = 0
    n = len(text)
    while idx < n:
        while idx < n and text[idx].isspace():
            idx += 1
        if idx >= n:
            break
        try:
            obj, end = decoder.raw_decode(text, idx)
        except json.JSONDecodeError as exc:
            preview = text[idx:idx + 80].replace("\n", "\\n")
            raise ValueError(
                f"Could not parse JSON starting at char {idx}: {exc}. "
                f"Snippet: {preview!r}"
            ) from exc
        docs.append(obj)
        idx = end
    if not docs:
        raise ValueError("No JSON documents found in file.")
    return docs


def _geoms_from_json_doc(data: Any) -> tuple[list[dict], str | None]:
    """
    Extract geometry dicts + optional CRS hint from one parsed JSON document.
    Returns (geoms, crs_or_None). Empty geoms means caller should try another strategy.
    """
    if isinstance(data, list):
        geoms: list[dict] = []
        for item in data:
            if isinstance(item, dict):
                if item.get("type") == "Feature":
                    g = item.get("geometry")
                    if g:
                        geoms.append(g)
                elif item.get("geometry"):
                    geoms.append(item["geometry"])
                elif item.get("type") in (
                    "Polygon", "MultiPolygon", "Point", "MultiPoint",
                    "LineString", "MultiLineString", "GeometryCollection",
                ):
                    geoms.append(item)
        return geoms, None

    if not isinstance(data, dict):
        return [], None

    if data.get("type") == "FeatureCollection":
        geoms = [f.get("geometry") or {} for f in (data.get("features") or [])]
        crs = None
        crs_m = (data.get("crs") or {}).get("properties", {})
        if crs_m.get("name"):
            crs = crs_m["name"]
        return geoms, crs

    if data.get("type") == "Feature":
        return [data.get("geometry") or {}], None

    if data.get("type") in (
        "Polygon", "MultiPolygon", "Point", "MultiPoint",
        "LineString", "MultiLineString", "GeometryCollection",
    ):
        return [data], None

    return [], None


def _bbox_from_cityjson(data: dict) -> dict:
    xs: list[float] = []
    ys: list[float] = []
    extent = (data.get("metadata") or {}).get("geographicalExtent")
    if extent and len(extent) >= 6:
        return _bbox_from_bounds(
            extent[0], extent[1], extent[3], extent[4],
            source_crs=_crs_hint_from_cityjson(data),
        )
    transform = data.get("transform") or {}
    scale = transform.get("scale") or [1, 1, 1]
    translate = transform.get("translate") or [0, 0, 0]
    for v in data.get("vertices") or []:
        xs.append(v[0] * scale[0] + translate[0])
        ys.append(v[1] * scale[1] + translate[1])
    if not xs:
        raise ValueError("CityJSON has no geographicalExtent or vertices.")
    return _bbox_from_bounds(
        min(xs), min(ys), max(xs), max(ys),
        source_crs=_crs_hint_from_cityjson(data),
    )


def _bbox_from_geojson_bytes(raw: bytes) -> dict:
    docs = _parse_json_documents(raw)

    # CityJSON is always a single object with CityObjects
    if len(docs) == 1 and isinstance(docs[0], dict) and "CityObjects" in docs[0]:
        return _bbox_from_cityjson(docs[0])

    xs: list[float] = []
    ys: list[float] = []
    crs: str | None = None

    for doc in docs:
        geoms, doc_crs = _geoms_from_json_doc(doc)
        if doc_crs:
            crs = doc_crs
        # NDJSON Feature without wrapping FeatureCollection
        if not geoms and isinstance(doc, dict) and doc.get("type") == "Feature":
            g = doc.get("geometry")
            if g:
                geoms = [g]
        for g in geoms:
            if not g:
                continue
            if g.get("type") == "GeometryCollection":
                for sub in g.get("geometries") or []:
                    for c in _iter_coords(sub.get("coordinates")):
                        xs.append(float(c[0])); ys.append(float(c[1]))
            else:
                for c in _iter_coords(g.get("coordinates")):
                    xs.append(float(c[0])); ys.append(float(c[1]))

    if not xs:
        # Last resort: open with fiona (handles some odd GeoJSON variants)
        if HAS_FIONA:
            with tempfile.NamedTemporaryFile(suffix=".geojson", delete=False) as tmp:
                tmp.write(raw)
                path = tmp.name
            try:
                return _bbox_from_fiona_path(path)
            except Exception as exc:
                raise ValueError(
                    "No coordinates found in JSON/GeoJSON "
                    f"(also tried fiona: {exc}). "
                    "If this is NDJSON, each line must be a Feature with a geometry."
                ) from exc
        raise ValueError("No coordinates found in GeoJSON / NDJSON.")

    return _bbox_from_bounds(
        min(xs), min(ys), max(xs), max(ys),
        source_crs=crs or "EPSG:4326",
    )


def _crs_hint_from_cityjson(data: dict) -> str:
    ref = (data.get("metadata") or {}).get("referenceSystem") or ""
    if not ref:
        return "EPSG:4326"
    parts = ref.rstrip("/").split("/")
    if len(parts) >= 2 and parts[-2].upper() == "EPSG":
        return f"EPSG:{parts[-1]}"
    m = re.search(r"EPSG[:/](\d+)", ref, re.IGNORECASE)
    return f"EPSG:{m.group(1)}" if m else "EPSG:4326"


def _bbox_from_fiona_path(path: str, layer: str | None = None) -> dict:
    if not HAS_FIONA:
        raise RuntimeError("fiona is required to compute bbox for Shapefile / GeoPackage.")
    kwargs = {"layer": layer} if layer else {}
    with fiona.open(path, **kwargs) as src:
        b = src.bounds  # (minx, miny, maxx, maxy)
        if not b or any(v is None for v in b):
            # Fall back to scanning geometries
            xmin = ymin = float("inf")
            xmax = ymax = float("-inf")
            for feat in src:
                g = feat.get("geometry") or {}
                for c in _iter_coords(g.get("coordinates")):
                    xmin = min(xmin, float(c[0])); xmax = max(xmax, float(c[0]))
                    ymin = min(ymin, float(c[1])); ymax = max(ymax, float(c[1]))
            if xmin == float("inf"):
                raise ValueError("No geometries found.")
            b = (xmin, ymin, xmax, ymax)
        return _bbox_from_bounds(b[0], b[1], b[2], b[3],
                                 source_crs=_crs_to_epsg(src.crs) or "EPSG:4326")


def _bbox_from_csv_bytes(raw: bytes) -> dict:
    if not HAS_PANDAS:
        raise RuntimeError("pandas is required to compute bbox from CSV.")
    df = pd.read_csv(io.BytesIO(raw))
    lon_col = S.csv_lon
    lat_col = S.csv_lat
    if not lon_col or not lat_col:
        # Heuristic
        lower = {c.lower(): c for c in df.columns}
        for lo, la in (("lon", "lat"), ("longitude", "latitude"), ("x", "y"), ("lng", "lat")):
            if lo in lower and la in lower:
                lon_col, lat_col = lower[lo], lower[la]
                break
    if not lon_col or not lat_col or lon_col not in df.columns or lat_col not in df.columns:
        raise ValueError(
            "CSV lon/lat columns unknown. Set them in Step 1 (vector CSV) "
            "or name columns lon/lat / longitude/latitude."
        )
    xs = pd.to_numeric(df[lon_col], errors="coerce").dropna()
    ys = pd.to_numeric(df[lat_col], errors="coerce").dropna()
    if xs.empty or ys.empty:
        raise ValueError("CSV lon/lat columns contain no numeric values.")
    return _bbox_from_bounds(float(xs.min()), float(ys.min()),
                             float(xs.max()), float(ys.max()),
                             source_crs=S.meta_crs or "EPSG:4326")


def _sniff_upload_format(filename: str, raw: bytes, declared: str) -> str:
    """Prefer real file signatures over the Step-1 format dropdown when they conflict."""
    name = (filename or "").lower()
    head = raw[:64]

    if head.startswith(b"PK\x03\x04") or name.endswith(".zip"):
        return "Shapefile (zip)"
    if head.startswith(b"SQLite format 3") or name.endswith(".gpkg"):
        return "GeoPackage"
    if name.endswith(".csv") or declared == "CSV":
        return "CSV"
    if declared in ("GeoJSON", "CityJSON", "Shapefile (zip)", "GeoPackage", "CSV"):
        return declared
    if name.endswith((".geojson", ".json")):
        return "GeoJSON"
    if name.endswith(".gpkg"):
        return "GeoPackage"
    return declared or "GeoJSON"


def _compute_bbox_from_upload() -> dict:
    """Compute EPSG:4326 bbox from the uploaded file (or raise)."""
    if S.source_type != "file" or not S.uploaded_file:
        raise RuntimeError("Upload a spatial file in Step 1 before calculating the bbox.")
    if not S.is_spatial:
        raise RuntimeError("Datasource is marked non-spatial — bbox does not apply.")

    raw = S.uploaded_file.getbuffer().tobytes()
    S.uploaded_file.seek(0)
    fmt = _sniff_upload_format(S.uploaded_file.name, raw, S.data_format or "")

    if fmt in ("GeoJSON", "CityJSON"):
        return _bbox_from_geojson_bytes(raw)

    if fmt == "CSV":
        return _bbox_from_csv_bytes(raw)

    if fmt == "Shapefile (zip)":
        with tempfile.TemporaryDirectory() as tmp:
            zpath = os.path.join(tmp, "up.zip")
            open(zpath, "wb").write(raw)
            with zipfile.ZipFile(zpath) as zf:
                zf.extractall(tmp)
            shps = [
                os.path.join(dp, f)
                for dp, _, fns in os.walk(tmp)
                for f in fns if f.lower().endswith(".shp")
            ]
            if not shps:
                raise ValueError("No .shp inside the zip.")
            return _bbox_from_fiona_path(shps[0])

    if fmt == "GeoPackage":
        with tempfile.NamedTemporaryFile(suffix=".gpkg", delete=False) as tmp:
            tmp.write(raw)
            path = tmp.name
        try:
            return _bbox_from_fiona_path(path, layer=S.gpkg_layer or None)
        finally:
            os.unlink(path)

    raise ValueError(
        f"Bbox calculation is not supported for format '{fmt}'. "
        "Use GeoJSON, Shapefile (zip), GeoPackage, CSV, or CityJSON."
    )


def _render_bbox_panel() -> None:
    """UI: calculate button + four corner coordinates (used in Step 2 — Manifest)."""
    st.markdown("#### Spatial bounding box")
    st.caption(
        "Compute the dataset envelope in EPSG:4326 from the uploaded file. "
        "Stored in the manifest and sent as `spatial_footprint` on submit."
    )

    col_btn, col_clear = st.columns([2, 1])
    with col_btn:
        calc = st.button("Calculate bounding box", key="calc_bbox",
                         disabled=not (S.source_type == "file" and S.uploaded_file
                                       and S.is_spatial))
    with col_clear:
        if S.bbox and st.button("Clear bbox", key="clear_bbox"):
            S.bbox = None
            S.bbox_corners = None
            S.spatial_footprint = None
            st.rerun()

    if calc:
        try:
            with st.spinner("Computing bounding box…"):
                result = _compute_bbox_from_upload()
            S.bbox = {
                "west": result["west"], "south": result["south"],
                "east": result["east"], "north": result["north"],
                "crs": result["crs"],
            }
            S.bbox_corners = result["corners"]
            S.spatial_footprint = result["footprint"]
            st.success("Bounding box calculated (EPSG:4326).")
        except Exception as exc:
            st.error(f"Bbox calculation failed: {exc}")

    if S.bbox and S.bbox_corners:
        b = S.bbox
        c = S.bbox_corners
        st.markdown(
            f"**Extent (W/S/E/N):** `{b['west']:.6f}` / `{b['south']:.6f}` / "
            f"`{b['east']:.6f}` / `{b['north']:.6f}`  ·  CRS `{b.get('crs', 'EPSG:4326')}`"
        )
        sw, se, ne, nw = st.columns(4)
        with sw:
            st.metric("SW (lon, lat)", f"{c['SW'][0]:.6f}, {c['SW'][1]:.6f}")
        with se:
            st.metric("SE (lon, lat)", f"{c['SE'][0]:.6f}, {c['SE'][1]:.6f}")
        with ne:
            st.metric("NE (lon, lat)", f"{c['NE'][0]:.6f}, {c['NE'][1]:.6f}")
        with nw:
            st.metric("NW (lon, lat)", f"{c['NW'][0]:.6f}, {c['NW'][1]:.6f}")
    elif S.source_type == "file" and S.is_spatial and not S.uploaded_file:
        st.info("Upload a file in Step 1 to enable bbox calculation.")
    elif S.source_type != "file":
        st.caption("Bbox from file is only available for file sources. "
                   "OGC footprints can be added later.")


def _profile_geojson(raw: bytes) -> ProfileResult:
    data = json.loads(raw)
    features = data.get("features") or []
    cols: set[str] = set()
    for f in features[:100]:
        cols.update((f.get("properties") or {}).keys())
    crs = "EPSG:4326"
    crs_m = (data.get("crs") or {}).get("properties", {})
    if crs_m.get("name"):
        crs = crs_m["name"]
    geom_type = ((features[0].get("geometry") or {}).get("type")) if features else None
    return sorted(cols) + ["__geometry__"], "__geometry__", crs, geom_type, len(features)


def _profile_shapefile(raw: bytes) -> ProfileResult:
    if not HAS_FIONA:
        st.warning("fiona not installed.")
        return [], None, None, None, None
    with tempfile.TemporaryDirectory() as tmp:
        zpath = os.path.join(tmp, "up.zip")
        open(zpath, "wb").write(raw)
        with zipfile.ZipFile(zpath) as zf:
            zf.extractall(tmp)
        shps = [os.path.join(tmp, n) for n in os.listdir(tmp) if n.endswith(".shp")]
        if not shps:
            st.error("No .shp inside the zip.")
            return [], None, None, None, None
        with fiona.open(shps[0]) as src:
            props = sorted(src.schema["properties"].keys())
            return (props + ["__geometry__"], "__geometry__",
                    _crs_to_epsg(src.crs), src.schema["geometry"],
                    len(src) if len(src) < 500_000 else None)


def _gpkg_layers(raw: bytes) -> list[str]:
    if not HAS_FIONA:
        return []
    with tempfile.NamedTemporaryFile(suffix=".gpkg", delete=False) as tmp:
        tmp.write(raw)
        path = tmp.name
    try:
        return list(fiona.listlayers(path))
    finally:
        os.unlink(path)


def _profile_gpkg(raw: bytes, layer: str) -> ProfileResult:
    if not HAS_FIONA:
        return [], None, None, None, None
    with tempfile.NamedTemporaryFile(suffix=".gpkg", delete=False) as tmp:
        tmp.write(raw)
        path = tmp.name
    try:
        with fiona.open(path, layer=layer) as src:
            props = sorted(src.schema["properties"].keys())
            return (props + ["__geometry__"], "__geometry__",
                    _crs_to_epsg(src.crs), src.schema["geometry"],
                    len(src) if len(src) < 500_000 else None)
    finally:
        os.unlink(path)


def _profile_csv(raw: bytes) -> tuple[list[str], int | None]:
    if not HAS_PANDAS:
        st.warning("pandas not installed.")
        return [], None
    df = pd.read_csv(io.BytesIO(raw), nrows=5)
    try:
        n = sum(1 for _ in io.BytesIO(raw)) - 1
    except Exception:
        n = None
    return list(df.columns), n


def _profile_cityjson(raw: bytes) -> ProfileResult:
    data = json.loads(raw)
    objs = data.get("CityObjects") or {}
    cols: set[str] = set()
    for o in list(objs.values())[:100]:
        cols.update((o.get("attributes") or {}).keys())
    ref = (data.get("metadata") or {}).get("referenceSystem") or ""
    crs = "EPSG:4326"
    if ref:
        parts = ref.rstrip("/").split("/")
        if len(parts) >= 2 and parts[-2].upper() == "EPSG":
            crs = f"EPSG:{parts[-1]}"
        else:
            m = re.search(r"EPSG[:/](\d+)", ref, re.IGNORECASE)
            crs = f"EPSG:{m.group(1)}" if m else ref
    geom_types = {g.get("type") for o in list(objs.values())[:100]
                  for g in (o.get("geometry") or []) if g.get("type")}
    return (sorted(cols) + ["__geometry__"], "__geometry__", crs,
            ", ".join(sorted(geom_types)) or None, len(objs))


def _profile_wfs(url: str, ogc_type: str) -> ProfileResult:
    try:
        if ogc_type == "OGC API Features":
            r = requests.get(url, params={"limit": 1, "f": "json"}, timeout=10)
        else:
            r = requests.get(url, params={"service": "WFS", "version": "2.0.0",
                                          "request": "GetFeature", "count": "1",
                                          "outputFormat": "application/json"}, timeout=10)
        r.raise_for_status()
        fc = r.json()
        feats = fc.get("features") or []
        cols = sorted((feats[0].get("properties") or {}).keys()) if feats else []
        crs_uri = fc.get("crs") or fc.get("storageCrs")
        crs = "EPSG:4326"
        if crs_uri:
            m = re.search(r"EPSG[:/](\d+)", str(crs_uri), re.IGNORECASE)
            if m:
                crs = f"EPSG:{m.group(1)}"
        return cols + ["__geometry__"], "__geometry__", crs, None, None
    except Exception as exc:
        st.warning(f"OGC sample fetch failed: {exc}")
        return [], None, None, None, None


def _list_wfs_layers(url: str, ogc_type: str) -> list[str]:
    try:
        if ogc_type == "OGC API Features":
            r = requests.get(url.rstrip("/") + "/collections",
                             params={"f": "json"}, timeout=10)
            r.raise_for_status()
            return [c["id"] for c in r.json().get("collections", [])]
        import xml.etree.ElementTree as ET
        r = requests.get(url, params={"service": "WFS", "version": "2.0.0",
                                      "request": "GetCapabilities"}, timeout=12)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        ns = {"wfs": "http://www.opengis.net/wfs/2.0"}
        return [el.text.strip()
                for el in root.findall(".//wfs:FeatureType/wfs:Name", ns) if el.text]
    except Exception as exc:
        st.warning(f"Layer listing failed: {exc}")
    return []


# ── metadata parsers ──────────────────────────────────────────────────────────
def _parse_iso19139(xml_text: str) -> dict:
    import xml.etree.ElementTree as ET
    out: dict = {}
    try:
        root = ET.fromstring(xml_text)
        ns = {"gmd": "http://www.isotc211.org/2005/gmd",
              "gco": "http://www.isotc211.org/2005/gco",
              "gml": "http://www.opengis.net/gml"}
        def _t(p):
            el = root.find(p, ns)
            return el.text.strip() if el is not None and el.text else None
        out["name"] = _t(".//gmd:title/gco:CharacterString")
        out["desc"] = _t(".//gmd:abstract/gco:CharacterString")
        out["crs"]  = _t(".//gmd:referenceSystemIdentifier//gmd:code/gco:CharacterString")
        kws = root.findall(".//gmd:keyword/gco:CharacterString", ns)
        out["tags"] = ", ".join(el.text.strip() for el in kws if el.text)
        tb = _t(".//gmd:temporalElement//gml:beginPosition")
        te = _t(".//gmd:temporalElement//gml:endPosition")
        out["temporal_start"] = tb[:10] if tb else None
        out["temporal_end"]   = te[:10] if te else None
    except Exception as exc:
        st.warning(f"ISO 19139 parse: {exc}")
    return {k: v for k, v in out.items() if v}


def _parse_ogc_records(json_text: str) -> dict:
    out: dict = {}
    try:
        rec = json.loads(json_text)
        out["name"] = rec.get("title", "")
        out["desc"] = rec.get("description", "")
        kws = [c for t in rec.get("themes", []) for c in t.get("concepts", [])]
        out["tags"] = ", ".join(
            str(k.get("id", k)) if isinstance(k, dict) else str(k) for k in kws)
        iv = (rec.get("time") or {}).get("interval") or [None, None]
        out["temporal_start"] = iv[0]
        out["temporal_end"]   = iv[-1]
    except Exception as exc:
        st.warning(f"OGC Records parse: {exc}")
    return {k: v for k, v in out.items() if v}


def _apply_meta(parsed: dict):
    if parsed.get("name"):  S.meta_name = parsed["name"]
    if parsed.get("desc"):  S.meta_desc = parsed["desc"]
    if parsed.get("tags"):  S.meta_tags = parsed["tags"]
    if parsed.get("crs"):   S.meta_crs  = parsed["crs"]
    for field in ("temporal_start", "temporal_end"):
        if parsed.get(field):
            try:
                val = date.fromisoformat(parsed[field][:10])
                setattr(S, f"meta_t_{'start' if 'start' in field else 'end'}", val)
            except Exception:
                pass


# ── manifest builder ──────────────────────────────────────────────────────────
def _build_manifest() -> dict:
    pk_key = S.pk_policy.split()[0]
    source: dict = {"type": S.source_type}
    if S.source_type == "file" and S.uploaded_file:
        source.update({"filename": S.uploaded_file.name, "format": S.data_format})
        if S.data_format == "GeoPackage" and S.gpkg_layer:
            source["layer"] = S.gpkg_layer
        if S.object_uri:
            source["object_uri"] = S.object_uri
    elif S.source_type == "ogc":
        source.update({"url": S.ogc_url, "ogc_type": S.ogc_type})
        if S.ogc_layer:
            source["layer"] = S.ogc_layer
    elif S.source_type == "api":
        source["url"] = S.api_url

    pk_block: dict = {"policy": pk_key}
    if pk_key == "natural_key":
        pk_block["source_column"] = S.pk_natural_col

    fk_block = (
        [{"source_column": c, "references": "dim_dataset.dataset_id"} for c in S.fk_cols]
        if S.fk_cols
        else [{"value": None, "note": "dataset_id auto-assigned at load time"}]
    )

    spatial_block = None
    if S.is_spatial and S.data_class == "vector":
        repro = bool(S.detected_crs and S.target_crs
                     and S.detected_crs.upper() != S.target_crs.upper())
        spatial_block = {
            "source_crs":  S.detected_crs or S.meta_crs or "unknown",
            "target_crs":  S.target_crs,
            "reproject":   repro,
            "source_type": "native" if S.spatial_col == "__geometry__" else "column",
            "geom_column": S.spatial_col,
        }
        if S.data_format == "CSV":
            spatial_block["lon_column"] = S.csv_lon
            spatial_block["lat_column"] = S.csv_lat
            if S.csv_wkt:
                spatial_block["wkt_column"] = S.csv_wkt

    return {
        "ingest_manifest_version": "1.0",
        "manifest_id": str(uuid.uuid4()),
        "datasource_class": {
            "is_spatial":  S.is_spatial,
            "data_class":  S.data_class,
            "format":      S.data_format,
            "source_type": S.source_type,
        },
        "source": source,
        "profile": {
            "detected_crs":  S.detected_crs,
            "geom_type":     S.geom_type,
            "feature_count": S.feature_count,
            "bbox":          S.bbox,
            "bbox_corners":  S.bbox_corners,
        },
        "spatial_footprint": S.spatial_footprint,
        "registry": {
            "name":           S.meta_name,
            "description":    S.meta_desc,
            "tags":           [t.strip() for t in S.meta_tags.split(",") if t.strip()],
            "crs":            S.meta_crs,
            "temporal_start": str(S.meta_t_start) if S.meta_t_start else None,
            "temporal_end":   str(S.meta_t_end)   if S.meta_t_end   else None,
        },
        "warehouse_mapping": {
            "pk":          pk_block,
            "fk":          fk_block,
            "spatial":     spatial_block,
            "non_spatial": {
                "strategy":      "jsonb",
                "target_column": "attributes",
                "include":       S.nonspatial_cols,
                "exclude":       S.dropped_cols,
            },
        },
        "standard_metadata": S.std_meta_parsed if S.has_std_meta else None,
    }


def _build_features(manifest: dict) -> list[dict]:
    """Build up to 5 sample warehouse rows from the uploaded file."""
    wm = manifest.get("warehouse_mapping", {})
    pk  = wm.get("pk", {})
    fk  = wm.get("fk", [{}])
    sp  = wm.get("spatial")
    ns  = wm.get("non_spatial", {})
    include = set(ns.get("include") or [])
    exclude = set(ns.get("exclude") or [])

    def _row(props: dict, geom: Any) -> dict:
        row: dict = {}
        row["id"] = (str(uuid.uuid4()) if pk.get("policy") == "uuid_per_row"
                     else props.get(pk.get("source_column", ""), "<pk>"))
        fk0 = fk[0] if fk else {}
        row["dataset_id"] = props.get(fk0.get("source_column", ""), None) if fk0.get("source_column") else None
        if sp:
            row["geometry"] = geom
        row["attributes"] = {k: v for k, v in props.items()
                              if (not include or k in include) and k not in exclude}
        return row

    rows: list[dict] = []
    try:
        if S.source_type == "file" and S.uploaded_file:
            raw = S.uploaded_file.read()
            S.uploaded_file.seek(0)
            fmt = S.data_format
            if fmt in ("GeoJSON", "CityJSON"):
                data = json.loads(raw)
                if fmt == "CityJSON":
                    for cid, obj in list((data.get("CityObjects") or {}).items())[:5]:
                        rows.append(_row(obj.get("attributes") or {},
                                         {"type": "CityObject", "id": cid}))
                else:
                    for f in (data.get("features") or [])[:5]:
                        rows.append(_row(f.get("properties") or {}, f.get("geometry")))
            elif fmt == "CSV" and HAS_PANDAS:
                df = pd.read_csv(io.BytesIO(raw), nrows=5)
                for _, r in df.iterrows():
                    props = r.to_dict()
                    geom = None
                    if S.csv_lon and S.csv_lat:
                        geom = {"type": "Point",
                                "coordinates": [props.get(S.csv_lon), props.get(S.csv_lat)]}
                    rows.append(_row(props, geom))
    except Exception:
        pass

    if not rows:
        rows = [_row({c: f"<{c}>" for c in include or ["col"]}, None)]
    return rows


# ── shared UI helpers ─────────────────────────────────────────────────────────
def _registry_form(prefix: str = ""):
    c1, c2 = st.columns(2)
    with c1:
        S.meta_name  = st.text_input("Dataset name *", value=S.meta_name,
                                      placeholder="e.g. Turin Buildings 2024",
                                      key=f"{prefix}meta_name")
        S.meta_desc  = st.text_area("Description", value=S.meta_desc,
                                     height=80, key=f"{prefix}meta_desc")
        S.meta_tags  = st.text_input("Tags (comma-separated)", value=S.meta_tags,
                                      placeholder="buildings, urban, 2024",
                                      key=f"{prefix}meta_tags")
    with c2:
        S.meta_crs     = st.text_input("CRS", value=S.meta_crs,
                                        key=f"{prefix}meta_crs")
        S.meta_t_start = st.date_input("Temporal start", value=S.meta_t_start,
                                        key=f"{prefix}t_start")
        S.meta_t_end   = st.date_input("Temporal end",   value=S.meta_t_end,
                                        key=f"{prefix}t_end")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE HEADER + API status badge
# ─────────────────────────────────────────────────────────────────────────────
base_url = _api_base()

title_col, badge_col = st.columns([5, 1])
with title_col:
    st.title("Ingest Wizard  (API)")
    st.caption(
        "Classify your datasource, describe it, profile the schema, map columns, "
        "then submit to the FastAPI backend."
    )
with badge_col:
    st.markdown("**API**")
    alive = _check_api(base_url)
    if alive:
        st.success(f"Online\n{base_url}")
    else:
        st.error(f"Unreachable\n{base_url}")
    if st.button("Check", key="hc"):
        _check_api.clear()
        st.rerun()

_nav_bar()
st.divider()


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — DATASOURCE CLASSIFICATION
# ─────────────────────────────────────────────────────────────────────────────
if S.step == 1:
    st.subheader("Step 1 — Datasource classification")

    sp_choice = st.radio(
        "Spatial data?",
        ["Yes — contains geographic / geometry data",
         "No  — tabular / non-spatial data"],
        index=0 if S.is_spatial in (None, True) else 1,
        horizontal=True,
    )
    S.is_spatial = sp_choice.startswith("Yes")
    st.divider()

    if not S.is_spatial:
        ns_src = st.radio("Source type", ["File upload", "API / web service"],
                           horizontal=True,
                           index=0 if S.source_type != "api" else 1)
        S.source_type = "file" if ns_src == "File upload" else "api"
        S.data_class  = "nonspatial"

        if S.source_type == "file":
            S.data_format = st.selectbox("File format", NONSPATIAL_FMTS,
                                          index=NONSPATIAL_FMTS.index(S.data_format)
                                          if S.data_format in NONSPATIAL_FMTS else 0)
            up = st.file_uploader("Upload file",
                                   type=["json", "csv", "xlsx", "parquet"])
            if up:
                S.uploaded_file = up
                st.success(f"File loaded: **{up.name}**  ({up.size/1024:.1f} KB)")
        else:
            S.api_url     = st.text_input("API / service URL", value=S.api_url)
            S.data_format = st.selectbox("Response format", ["JSON", "CSV", "Other"])

    else:
        sp_src = st.radio("Source type",
                           ["File upload", "OGC service (WFS / OGC API Features)"],
                           horizontal=True,
                           index=0 if S.source_type != "ogc" else 1)
        S.source_type = "file" if sp_src == "File upload" else "ogc"

        if S.source_type == "ogc":
            S.data_class = "vector"
            S.ogc_type   = st.selectbox("OGC service type", OGC_TYPES,
                                         index=OGC_TYPES.index(S.ogc_type))
            S.ogc_url    = st.text_input("Service base URL", value=S.ogc_url)
            if S.ogc_url.strip():
                if st.button("List layers"):
                    with st.spinner("Fetching capabilities…"):
                        S.ogc_layers = _list_wfs_layers(S.ogc_url.strip(), S.ogc_type)
                if S.ogc_layers:
                    S.ogc_layer   = st.selectbox("Select layer", S.ogc_layers)
                    S.data_format = f"OGC/{S.ogc_type}"
                elif S.ogc_url.strip():
                    st.info("Click List layers to fetch available layers.")
        else:
            dc = st.radio("Data class", ["Vector", "Raster"], horizontal=True,
                           index=0 if S.data_class in (None, "vector") else 1)
            S.data_class = dc.lower()

            fmt_list = VECTOR_FORMATS if S.data_class == "vector" else RASTER_FORMATS
            up = st.file_uploader(
                "Upload file",
                type=(["geojson", "json", "zip", "gpkg", "csv"]
                      if S.data_class == "vector"
                      else ["tif", "tiff", "nc", "h5", "hdf5"]),
            )
            if up:
                S.uploaded_file = up
                name = up.name.lower()
                auto = None
                if name.endswith((".geojson", ".json")):
                    try:
                        d = json.loads(up.read(4096)); up.seek(0)
                        auto = "CityJSON" if "CityObjects" in d else "GeoJSON"
                    except Exception:
                        auto = "GeoJSON"
                elif name.endswith(".zip"):   auto = "Shapefile (zip)"
                elif name.endswith(".gpkg"):  auto = "GeoPackage"
                elif name.endswith(".csv"):   auto = "CSV"
                elif name.endswith((".tif", ".tiff")): auto = "GeoTIFF"
                elif name.endswith(".nc"):    auto = "NetCDF"
                if auto and S.data_format != auto:
                    S.data_format = auto
                st.success(f"File loaded: **{up.name}**  ({up.size/1024:.1f} KB)")

            idx = fmt_list.index(S.data_format) if S.data_format in fmt_list else 0
            S.data_format = st.selectbox("Format", fmt_list, index=idx)

            if S.data_class == "vector" and S.data_format == "CSV" and S.uploaded_file:
                raw = S.uploaded_file.read(); S.uploaded_file.seek(0)
                csv_cols, _ = _profile_csv(raw)
                cc1, cc2, cc3 = st.columns(3)
                with cc1:
                    S.csv_lon = st.selectbox("Longitude column", ["—"] + csv_cols)
                    S.csv_lon = None if S.csv_lon == "—" else S.csv_lon
                with cc2:
                    S.csv_lat = st.selectbox("Latitude column", ["—"] + csv_cols)
                    S.csv_lat = None if S.csv_lat == "—" else S.csv_lat
                with cc3:
                    S.csv_wkt = st.selectbox("WKT column (optional)", ["—"] + csv_cols)
                    S.csv_wkt = None if S.csv_wkt == "—" else S.csv_wkt

            if S.data_class == "vector" and S.data_format == "GeoPackage" and S.uploaded_file:
                raw = S.uploaded_file.read(); S.uploaded_file.seek(0)
                layers = _gpkg_layers(raw)
                if layers:
                    S.gpkg_layer = st.selectbox("GPKG layer", layers)
                else:
                    S.gpkg_layer = st.text_input("GPKG layer name (fiona unavailable)")

    st.divider()
    ready = (
        S.is_spatial is not None and S.source_type and S.data_format
        and (
            (S.source_type == "file" and S.uploaded_file)
            or (S.source_type == "ogc" and S.ogc_url.strip())
            or (S.source_type == "api" and S.api_url.strip())
        )
    )
    if st.button("Next", type="primary", disabled=not ready):
        _goto(2)
    if not ready:
        st.caption("Fill in all fields and provide a file or service URL to continue.")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — MANIFEST METADATA
# ─────────────────────────────────────────────────────────────────────────────
elif S.step == 2:
    st.subheader("Step 2 — Manifest metadata")

    S.has_std_meta = st.toggle(
        "I have standard catalog metadata (ISO 19139 XML / OGC API Records JSON / CSW)",
        value=S.has_std_meta,
    )

    if S.has_std_meta:
        S.std_meta_mode = st.radio(
            "Metadata source", ["Paste text", "Fetch from CSW endpoint"],
            horizontal=True, index=0 if S.std_meta_mode == "paste" else 1,
        )
        if S.std_meta_mode == "Paste text":
            fmt_radio = st.radio("Format",
                                  ["ISO 19139 (XML)", "OGC API Records (JSON)"],
                                  horizontal=True)
            S.std_meta_raw = st.text_area("Paste metadata", value=S.std_meta_raw, height=200)
            if st.button("Parse and pre-fill"):
                parsed = (_parse_iso19139(S.std_meta_raw) if fmt_radio.startswith("ISO")
                          else _parse_ogc_records(S.std_meta_raw))
                S.std_meta_parsed = parsed
                _apply_meta(parsed)
                S.meta_approved = False
                st.success(f"Parsed {len(parsed)} field(s): {list(parsed.keys())}")
        else:
            csw_url   = st.text_input("CSW base URL")
            record_id = st.text_input("Record identifier (fileIdentifier)")
            if st.button("Fetch from CSW"):
                if csw_url and record_id:
                    try:
                        r = requests.get(csw_url, params={
                            "service": "CSW", "version": "2.0.2",
                            "request": "GetRecordById", "id": record_id,
                            "elementSetName": "full",
                            "outputSchema": "http://www.isotc211.org/2005/gmd",
                        }, timeout=15)
                        r.raise_for_status()
                        parsed = _parse_iso19139(r.text)
                        S.std_meta_parsed = parsed
                        _apply_meta(parsed)
                        S.meta_approved = False
                        st.success(f"Fetched and parsed {len(parsed)} field(s).")
                    except Exception as exc:
                        st.error(f"CSW fetch failed: {exc}")
                else:
                    st.warning("Provide both a CSW URL and a record ID.")

        if S.std_meta_parsed:
            st.divider()
            st.markdown("#### Review auto-filled fields")
            _registry_form(prefix="approve_")
            S.meta_approved = st.checkbox("I confirm these fields are correct",
                                           value=S.meta_approved)
            if not S.meta_approved:
                st.info("Tick the confirmation checkbox to proceed.")
        else:
            st.info("Parse or fetch metadata first.")
    else:
        st.markdown("#### Dataset registry fields")
        _registry_form(prefix="manual_")

    st.divider()
    _render_bbox_panel()

    st.divider()
    can_next = bool(S.meta_name.strip()) and (
        not S.has_std_meta or S.meta_approved or not S.std_meta_parsed)
    _back_next(1, 3, disabled=not can_next)
    if not can_next:
        st.caption("Dataset name is required." +
                   (" Confirm auto-filled fields to proceed." if S.has_std_meta else ""))


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — PROFILING  (bypassed for OGC / API)
# ─────────────────────────────────────────────────────────────────────────────
elif S.step == 3:
    if S.source_type != "file":
        st.subheader("Step 3 — Profiling  [OGC/API — partial]")
        st.info(f"Source type is **{S.source_type.upper()}** — sampling remote service.")
        if not S.columns:
            with st.spinner("Sampling…"):
                if S.source_type == "ogc":
                    url = S.ogc_url
                    if S.ogc_type == "OGC API Features" and S.ogc_layer:
                        url = S.ogc_url.rstrip("/") + f"/collections/{S.ogc_layer}/items"
                    cols, gc, crs, gt, _ = _profile_wfs(url, S.ogc_type)
                    S.columns = cols; S.geom_col = gc; S.detected_crs = crs; S.geom_type = gt
                else:
                    try:
                        r = requests.get(S.api_url, timeout=10); r.raise_for_status()
                        data = r.json()
                        S.columns = sorted((data[0] if isinstance(data, list) and data
                                            else data).keys())
                    except Exception as exc:
                        st.error(f"API fetch failed: {exc}")
        if S.columns:
            st.success(f"Found {len(S.columns)} column(s).")
            g = st.columns(4)
            for i, c in enumerate(S.columns):
                g[i % 4].code(c)
        else:
            mc = st.text_area("Column names (one per line)")
            if mc.strip():
                S.columns = [c.strip() for c in mc.splitlines() if c.strip()]
        _back_next(2, 4)

    else:
        st.subheader("Step 3 — Profiling")
        st.caption("Reads columns, CRS, geometry type and feature count from the file.")

        if S.uploaded_file and not S.columns:
            with st.spinner("Profiling…"):
                raw = S.uploaded_file.read(); S.uploaded_file.seek(0)
                fmt = S.data_format
                if fmt in ("GeoJSON", "CityJSON"):
                    data = json.loads(raw)
                    fn = _profile_cityjson if "CityObjects" in data else _profile_geojson
                    S.columns, S.geom_col, S.detected_crs, S.geom_type, S.feature_count = fn(raw)
                elif fmt == "Shapefile (zip)":
                    S.columns, S.geom_col, S.detected_crs, S.geom_type, S.feature_count = \
                        _profile_shapefile(raw)
                elif fmt == "GeoPackage":
                    S.columns, S.geom_col, S.detected_crs, S.geom_type, S.feature_count = \
                        _profile_gpkg(raw, S.gpkg_layer or "")
                elif fmt == "CSV":
                    S.columns, S.feature_count = _profile_csv(raw)
                    S.geom_col = S.detected_crs = None
                else:
                    if HAS_PANDAS:
                        try:
                            df = pd.read_json(io.BytesIO(raw))
                            S.columns = list(df.columns)
                        except Exception:
                            pass

        if S.columns:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Columns",       len(S.columns))
            m2.metric("Features",      str(S.feature_count) if S.feature_count else "—")
            m3.metric("Geometry type", S.geom_type or "—")
            m4.metric("Detected CRS",  S.detected_crs or "—")

            st.divider()
            st.markdown("#### CRS")
            cr1, cr2 = st.columns(2)
            with cr1:
                st.markdown(f"**Detected:** `{S.detected_crs or 'not found'}`")
                needs = (S.detected_crs and S.meta_crs
                         and S.detected_crs.upper() != S.meta_crs.upper())
                if needs:
                    st.warning(f"Source `{S.detected_crs}` differs from target `{S.meta_crs}`. ETL will reproject.")
                elif S.detected_crs:
                    st.success("Source and target CRS match.")
                else:
                    st.info("CRS not detected — set manually.")
            with cr2:
                ov = st.text_input("Override source CRS", value=S.detected_crs or "", key="crs_ov")
                if ov.strip(): S.detected_crs = ov.strip()
                tgt = st.text_input("Target storage CRS", value=S.meta_crs or "EPSG:4326", key="tgt_crs")
                S.meta_crs = tgt; S.target_crs = tgt

            st.divider()
            st.markdown("#### Columns detected")
            g = st.columns(4)
            for i, c in enumerate(S.columns):
                g[i % 4].code(f"{c}" + (" [geom]" if c == S.geom_col else ""))
        else:
            st.warning("No columns detected.")
            mc = st.text_area("Enter column names (one per line)")
            if mc.strip():
                S.columns = [c.strip() for c in mc.splitlines() if c.strip()]
            ov = st.text_input("Source CRS", placeholder="EPSG:4326", key="mcrs")
            if ov.strip(): S.detected_crs = ov.strip()

        if st.button("Re-profile"):
            for k in ("columns", "geom_col", "detected_crs", "geom_type", "feature_count"):
                setattr(S, k, [] if k == "columns" else None)
            st.rerun()

        _back_next(2, 4)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — COLUMN MAPPING
# ─────────────────────────────────────────────────────────────────────────────
elif S.step == 4:
    st.subheader("Step 4 — Column mapping")
    st.caption("Assign columns to warehouse roles. Unassigned columns go into JSONB `attributes`.")

    cols     = S.columns or []
    geom_col = S.geom_col

    st.markdown("### Primary Key (PK)")
    pk_idx  = PK_POLICIES.index(S.pk_policy) if S.pk_policy in PK_POLICIES else 0
    S.pk_policy = st.radio("PK strategy", PK_POLICIES, index=pk_idx)
    if "natural_key" in S.pk_policy:
        opts = ["—"] + [c for c in cols if c != geom_col]
        sel  = S.pk_natural_col if S.pk_natural_col in opts else "—"
        s    = st.selectbox("Natural key column", opts, index=opts.index(sel))
        S.pk_natural_col = None if s == "—" else s

    st.divider()
    st.markdown("### Foreign Key(s) (FK)")
    st.caption("Default is none — dataset_id FK is auto-assigned by the ingest worker.")
    fk_opts   = [c for c in cols if c != geom_col]
    S.fk_cols = st.multiselect("FK column(s) from source", fk_opts,
                                default=[c for c in S.fk_cols if c in fk_opts])
    if not S.fk_cols:
        st.info("No FK selected — dataset_id will be auto-assigned.")

    st.divider()
    if S.is_spatial and S.data_class == "vector":
        st.markdown("### Spatial column")
        S.target_crs = st.text_input("Target storage CRS", value=S.target_crs)
        if S.data_format == "CSV":
            st.info(f"Geometry from columns: lon=`{S.csv_lon}` lat=`{S.csv_lat}`"
                    + (f" wkt=`{S.csv_wkt}`" if S.csv_wkt else ""))
            S.spatial_col = "__geometry__"
        else:
            go = [c for c in cols if "geom" in c.lower() or c == geom_col] or cols
            dg = geom_col if geom_col in go else (go[0] if go else None)
            S.spatial_col = st.selectbox("Geometry column", go,
                                          index=go.index(dg) if dg in go else 0)
        st.divider()

    st.markdown("### Non-spatial columns  →  `attributes` JSONB")
    reserved  = {S.spatial_col or "", geom_col or ""} | set(S.fk_cols) | \
                ({S.pk_natural_col} if S.pk_natural_col else set())
    remaining = [c for c in cols if c not in reserved]
    ns1, ns2  = st.columns(2)
    with ns1:
        st.markdown("**Include in JSONB**")
        S.nonspatial_cols = st.multiselect("Include", remaining,
                                            default=[c for c in S.nonspatial_cols
                                                     if c in remaining] or remaining,
                                            label_visibility="collapsed")
    with ns2:
        st.markdown("**Drop (exclude entirely)**")
        droppable      = [c for c in remaining if c not in S.nonspatial_cols]
        S.dropped_cols = st.multiselect("Drop", droppable,
                                         default=[c for c in S.dropped_cols if c in droppable],
                                         label_visibility="collapsed")
    unmapped = [c for c in remaining
                if c not in S.nonspatial_cols and c not in S.dropped_cols]
    if unmapped:
        st.warning(f"{len(unmapped)} unmapped column(s) will default to JSONB: {unmapped}")

    st.divider()
    b, n = st.columns([1, 5])
    with b:
        if st.button("Back", key="back_4"):
            _goto(3)
    with n:
        if st.button("Build manifest", type="primary", key="build_manifest"):
            S.manifest = _build_manifest()
            _goto(5)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 — SUBMIT TO API
# ─────────────────────────────────────────────────────────────────────────────
elif S.step == 5:
    st.subheader("Step 5 — Submit to API")

    if not S.manifest:
        S.manifest = _build_manifest()

    manifest     = S.manifest
    features     = _build_features(manifest)
    manifest_str = json.dumps(manifest, indent=2, default=str)
    features_str = json.dumps(features, indent=2, default=str)

    # ── Summary ───────────────────────────────────────────────────────────────
    wm  = manifest.get("warehouse_mapping", {})
    reg = manifest.get("registry", {})
    st.markdown(
        f"**Dataset:** {reg.get('name','—')}  \n"
        f"**Format:** `{S.data_format}` · class `{S.data_class}` · source `{S.source_type}`  \n"
        f"**PK policy:** `{wm.get('pk',{}).get('policy','—')}`  \n"
        f"**Spatial:** `{S.is_spatial}` · geometry `{S.geom_type or '—'}`  \n"
        f"**Detected CRS:** `{S.detected_crs or '—'}` → target `{S.target_crs}`  \n"
        f"**JSONB attributes:** {len(wm.get('non_spatial',{}).get('include',[]))} column(s)  \n"
        f"**Bbox:** "
        + (
            f"`W {S.bbox['west']:.4f}  S {S.bbox['south']:.4f}  "
            f"E {S.bbox['east']:.4f}  N {S.bbox['north']:.4f}`"
            if S.bbox else "— (not calculated)"
        )
    )

    # ── Download (local, no API needed) ───────────────────────────────────────
    st.divider()
    st.markdown("### Download locally")
    dl1, dl2 = st.columns(2)
    with dl1:
        st.download_button("Download manifest JSON", data=manifest_str,
                            file_name=f"manifest_{manifest.get('manifest_id','x')[:8]}.json",
                            mime="application/json", use_container_width=True)
    with dl2:
        st.download_button("Download ingested rows JSON", data=features_str,
                            file_name=f"features_{manifest.get('manifest_id','x')[:8]}.json",
                            mime="application/json", use_container_width=True)

    # ── JSON previews ─────────────────────────────────────────────────────────
    with st.expander("Manifest JSON"):
        st.code(manifest_str, language="json")
    with st.expander("Ingested rows (up to 5 sample rows)"):
        st.code(features_str, language="json")

    # ── API submission ────────────────────────────────────────────────────────
    st.divider()
    st.markdown("### Submit to FastAPI backend")
    st.caption(f"Target: **{base_url}/api/v1/datasources**")

    minio_ok = minio_store.is_configured()
    if S.source_type == "file" and S.uploaded_file:
        if minio_ok:
            st.info(
                f"On submit, the file will be uploaded to MinIO "
                f"(`{minio_store.endpoint_url()}` / bucket from MINIO_URI) "
                "and `object_uri` will be stored on `meta_table`."
            )
            if S.object_uri:
                st.code(S.object_uri, language="text")
        else:
            st.warning(
                "MinIO is not configured — set `MINIO_URI` in `ingest.sh` "
                "or `[minio]` in `.streamlit/secrets.toml`. "
                "Submit will still register metadata without an object_uri."
            )

    S.api_token = st.text_input("Bearer token (optional)", value=S.api_token,
                                 type="password", key="submit_token")

    if st.button("Submit datasource", type="primary", key="submit_btn"):
        if not alive:
            st.error("API is not reachable. Start the backend first.")
        else:
            try:
                object_uri = S.object_uri
                file_size = None

                # Upload original file to MinIO before registering
                if S.source_type == "file" and S.uploaded_file and minio_store.is_configured():
                    raw = S.uploaded_file.getbuffer().tobytes()
                    S.uploaded_file.seek(0)
                    file_size = len(raw)
                    # provisional id for object key prefix; API assigns the real dataset_id
                    prefix = str(uuid.uuid4())
                    name = S.uploaded_file.name
                    ctype = "application/octet-stream"
                    lower = name.lower()
                    if lower.endswith((".geojson", ".json")):
                        ctype = "application/geo+json"
                    elif lower.endswith(".csv"):
                        ctype = "text/csv"
                    elif lower.endswith(".zip"):
                        ctype = "application/zip"
                    elif lower.endswith(".gpkg"):
                        ctype = "application/geopackage+sqlite3"
                    with st.spinner("Uploading file to MinIO…"):
                        object_uri = minio_store.upload(
                            raw, name, prefix=prefix, content_type=ctype,
                        )
                    S.object_uri = object_uri

                source = dict(manifest.get("source") or {})
                if object_uri:
                    source["object_uri"] = object_uri
                if file_size is not None:
                    source["file_size_bytes"] = file_size

                # Keep manifest in sync
                manifest = dict(manifest)
                manifest["source"] = source
                if object_uri:
                    prof = dict(manifest.get("profile") or {})
                    prof["object_uri"] = object_uri
                    manifest["profile"] = prof
                S.manifest = manifest

                payload = {
                    "registry": {
                        "name":           reg.get("name"),
                        "description":    reg.get("description", ""),
                        "tags":           reg.get("tags", []),
                        "crs":            reg.get("crs", "EPSG:4326"),
                        "temporal_start": reg.get("temporal_start"),
                        "temporal_end":   reg.get("temporal_end"),
                    },
                    "source": source,
                    "datasource_class": manifest.get("datasource_class", {}),
                    "spatial_footprint": S.spatial_footprint or manifest.get("spatial_footprint"),
                    "manifest": manifest,
                    "features": features,
                }
                with st.spinner("Posting to API…"):
                    resp = requests.post(
                        f"{base_url}/api/v1/datasources",
                        json=payload,
                        headers=_api_headers(S.api_token),
                        timeout=120,
                    )
                if resp.ok:
                    result = resp.json()
                    S.submit_result = result
                    msg = (
                        f"Submitted — dataset_id: `{result.get('dataset_id')}`  |  "
                        f"manifest_id: `{result.get('manifest_id')}`  |  "
                        f"features ingested: `{result.get('feature_count', 0)}`"
                    )
                    if object_uri:
                        msg += f"  \n**object_uri:** `{object_uri}`"
                    st.success(msg)
                else:
                    st.error(f"HTTP {resp.status_code}: {resp.text[:500]}")
            except requests.exceptions.ConnectionError:
                st.error("Connection refused — is the API running?")
            except Exception as exc:
                st.error(f"Request failed: {exc}")

    # ── Post-submit actions ───────────────────────────────────────────────────
    if S.submit_result:
        dataset_id = S.submit_result.get("dataset_id")
        st.divider()
        st.markdown("### Verify stored datasource")
        col_get, col_feat = st.columns(2)

        with col_get:
            if st.button("Fetch registry record from API", key="verify_reg"):
                try:
                    r = requests.get(f"{base_url}/api/v1/datasources/{dataset_id}",
                                     headers=_api_headers(S.api_token), timeout=10)
                    if r.ok:
                        st.json(r.json())
                    else:
                        st.error(f"HTTP {r.status_code}: {r.text[:300]}")
                except Exception as exc:
                    st.error(str(exc))

        with col_feat:
            if st.button("Fetch ingested features from API", key="verify_feat"):
                try:
                    r = requests.get(f"{base_url}/api/v1/datasources/{dataset_id}/features",
                                     headers=_api_headers(S.api_token), timeout=10)
                    if r.ok:
                        st.json(r.json())
                    else:
                        st.error(f"HTTP {r.status_code}: {r.text[:300]}")
                except Exception as exc:
                    st.error(str(exc))

    st.divider()
    back_col, over_col = st.columns(2)
    with back_col:
        if st.button("Back", key="back_5"):
            _goto(4)
    with over_col:
        if st.button("Start over", use_container_width=True, key="startover"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
