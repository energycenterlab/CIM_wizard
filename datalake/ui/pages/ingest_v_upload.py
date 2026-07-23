"""
ingest_v_upload.py  —  Warehouse Ingest Wizard
===============================================
5-step wizard:

  Step 1  Datasource classification
            spatial? → file/OGC → vector/raster → format
            non-spatial? → file/API → format

  Step 2  Manifest metadata
            standard metadata (ISO 19139 / OGC API Records / CSW fetch)
            OR manual registry fields

  Step 3  Profiling  (file sources only — bypassed for OGC/API)
            CRS detection, geometry type, feature count, column list

  Step 4  Column mapping
            PK · FK (default none) · spatial column · non-spatial → JSONB

  Step 5  Output
            upload original file to MinIO → object_uri on meta_table
            download manifest JSON
            download ingested-row JSON
            POST to separate API endpoints (manifest + data) with custom headers
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

from db import init_db, insert_record  # noqa: E402
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

# ── page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Ingest — Warehouse Wizard", layout="wide")

# ── constants ────────────────────────────────────────────────────────────────
VECTOR_FORMATS   = ["GeoJSON", "Shapefile (zip)", "GeoPackage", "CSV", "CityJSON"]
RASTER_FORMATS   = ["GeoTIFF", "COG", "NetCDF", "HDF5", "Other raster"]
NONSPATIAL_FMTS  = ["JSON", "CSV", "Excel", "Parquet", "Other"]
OGC_TYPES        = ["WFS", "OGC API Features", "WMS", "WCS", "WMTS"]

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
    "5 · Output",
]
TOTAL_STEPS = len(STEP_LABELS)


# ── session state ─────────────────────────────────────────────────────────────
def _init():
    defaults: dict[str, Any] = {
        # wizard
        "step":            1,
        # step 1
        "is_spatial":      None,      # True | False
        "source_type":     None,      # "file" | "ogc" | "api"
        "data_class":      None,      # "vector" | "raster" | "nonspatial"
        "data_format":     None,      # e.g. "GeoJSON", "CSV", …
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
        # step 3 (profiling)
        "columns":         [],
        "detected_crs":    None,
        "geom_type":       None,
        "feature_count":   None,
        "geom_col":        None,
        # step 4 (mapping)
        "pk_policy":       PK_POLICIES[0],
        "pk_natural_col":  None,
        "fk_cols":         [],        # default: empty (none)
        "spatial_col":     None,
        "target_crs":      "EPSG:4326",
        "nonspatial_cols": [],
        "dropped_cols":    [],
        # step 5 (output)
        "manifest":        {},
        "ingested_rows":   [],
        "object_uri":      None,
        "dataset_id":      None,
        "manifest_api_url":    "",
        "manifest_api_token":  "",
        "manifest_api_headers":"",
        "data_api_url":        "",
        "data_api_token":      "",
        "data_api_headers":    "",
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
                lbl = f"[done] {label}" + (" [skipped]" if skip else "")
                st.button(lbl, key=f"nav_{i}", use_container_width=True,
                          on_click=_goto, args=(i,))
            elif i == S.step:
                st.button(f">> {label}", key=f"nav_{i}",
                          use_container_width=True, disabled=True)
            else:
                lbl = label + (" [skip]" if skip else "")
                st.button(lbl, key=f"nav_{i}",
                          use_container_width=True, disabled=True)


def _back_next(back_step: int, next_step: int, next_label: str = "Next",
               next_disabled: bool = False):
    b, n = st.columns([1, 5])
    with b:
        if st.button("Back", key=f"back_{back_step}"):
            _goto(back_step)
    with n:
        if st.button(next_label, type="primary",
                     disabled=next_disabled, key=f"next_{next_step}"):
            _goto(next_step)


# ── file profilers ────────────────────────────────────────────────────────────
def _crs_to_epsg(crs_obj: Any) -> str | None:
    if crs_obj is None:
        return None
    if hasattr(crs_obj, "to_epsg"):
        try:
            e = crs_obj.to_epsg()
            if e:
                return f"EPSG:{e}"
        except Exception:
            pass
    if hasattr(crs_obj, "to_authority"):
        try:
            a = crs_obj.to_authority()
            if a:
                return f"{a[0]}:{a[1]}"
        except Exception:
            pass
    if hasattr(crs_obj, "to_wkt"):
        try:
            return _wkt_epsg(crs_obj.to_wkt())
        except Exception:
            pass
    if isinstance(crs_obj, dict):
        init = crs_obj.get("init", "")
        return init.upper() if init else None
    if isinstance(crs_obj, str):
        return _wkt_epsg(crs_obj) or crs_obj
    return str(crs_obj)


def _wkt_epsg(wkt: str) -> str | None:
    for pattern in [r'AUTHORITY\["EPSG",\s*"(\d+)"\]', r'ID\["EPSG",\s*(\d+)\]']:
        m = re.search(pattern, wkt, re.IGNORECASE)
        if m:
            return f"EPSG:{m.group(1)}"
    return None


ProfileResult = tuple[list[str], str | None, str | None, str | None, int | None]


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
            return props + ["__geometry__"], "__geometry__", \
                   _crs_to_epsg(src.crs), src.schema["geometry"], \
                   (len(src) if len(src) < 500_000 else None)


def _gpkg_layers(raw: bytes) -> list[str]:
    if not HAS_FIONA:
        return []
    with tempfile.NamedTemporaryFile(suffix=".gpkg", delete=False) as tmp:
        tmp.write(raw); path = tmp.name
    try:
        return list(fiona.listlayers(path))
    finally:
        os.unlink(path)


def _profile_gpkg(raw: bytes, layer: str) -> ProfileResult:
    if not HAS_FIONA:
        return [], None, None, None, None
    with tempfile.NamedTemporaryFile(suffix=".gpkg", delete=False) as tmp:
        tmp.write(raw); path = tmp.name
    try:
        with fiona.open(path, layer=layer) as src:
            props = sorted(src.schema["properties"].keys())
            return props + ["__geometry__"], "__geometry__", \
                   _crs_to_epsg(src.crs), src.schema["geometry"], \
                   (len(src) if len(src) < 500_000 else None)
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
    meta = data.get("metadata") or {}
    ref = meta.get("referenceSystem") or ""
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
    return sorted(cols) + ["__geometry__"], "__geometry__", crs, \
           (", ".join(sorted(geom_types)) or None), len(objs)


def _profile_wfs(url: str, ogc_type: str) -> ProfileResult:
    try:
        if ogc_type == "OGC API Features":
            r = requests.get(url, params={"limit": 1, "f": "json"}, timeout=10)
        else:
            r = requests.get(url, params={
                "service": "WFS", "version": "2.0.0",
                "request": "GetFeature", "count": "1",
                "outputFormat": "application/json",
            }, timeout=10)
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
    if parsed.get("name"):          S.meta_name    = parsed["name"]
    if parsed.get("desc"):          S.meta_desc    = parsed["desc"]
    if parsed.get("tags"):          S.meta_tags    = parsed["tags"]
    if parsed.get("crs"):           S.meta_crs     = parsed["crs"]
    if parsed.get("temporal_start"):
        try:
            S.meta_t_start = date.fromisoformat(parsed["temporal_start"][:10])
        except Exception:
            pass
    if parsed.get("temporal_end"):
        try:
            S.meta_t_end = date.fromisoformat(parsed["temporal_end"][:10])
        except Exception:
            pass


# ── manifest + ingested-rows builders ────────────────────────────────────────
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
        else [{"value": None, "note": "no FK in source — dataset_id auto-assigned at load time"}]
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
            "is_spatial":   S.is_spatial,
            "data_class":   S.data_class,
            "format":       S.data_format,
            "source_type":  S.source_type,
        },
        "source": source,
        "profile": {
            "detected_crs":  S.detected_crs,
            "geom_type":     S.geom_type,
            "feature_count": S.feature_count,
        },
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
                "strategy":       "jsonb",
                "target_column":  "attributes",
                "include":        S.nonspatial_cols,
                "exclude":        S.dropped_cols,
            },
        },
        "standard_metadata": S.std_meta_parsed if S.has_std_meta else None,
    }


def _build_ingested_rows(manifest: dict) -> list[dict]:
    """
    Build a list of preview/template rows matching the warehouse schema.
    If the file is available, produce real rows (up to 5 samples).
    Otherwise produce one template row showing the column layout.
    """
    wm = manifest.get("warehouse_mapping", {})
    pk  = wm.get("pk", {})
    fk  = wm.get("fk", [{}])
    sp  = wm.get("spatial")
    ns  = wm.get("non_spatial", {})

    def _make_row(raw_props: dict, raw_geom: Any) -> dict:
        row: dict = {}
        # PK
        if pk.get("policy") == "uuid_per_row":
            row["id"] = str(uuid.uuid4())
        elif pk.get("policy") == "natural_key" and pk.get("source_column"):
            row["id"] = raw_props.get(pk["source_column"], "<pk>")
        else:
            row["id"] = "<serial>"
        # FK
        fk_entry = fk[0] if fk else {}
        if fk_entry.get("source_column"):
            row["dataset_id"] = raw_props.get(fk_entry["source_column"], None)
        else:
            row["dataset_id"] = None
        # geometry
        if sp:
            row["geometry"] = raw_geom
        # attributes JSONB
        include = ns.get("include") or []
        exclude = set(ns.get("exclude") or [])
        attrs = {k: v for k, v in raw_props.items()
                 if k in include and k not in exclude}
        row["attributes"] = attrs
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
                        rows.append(_make_row(obj.get("attributes") or {},
                                              {"type": "CityObject", "id": cid}))
                else:
                    for f in (data.get("features") or [])[:5]:
                        rows.append(_make_row(f.get("properties") or {},
                                              f.get("geometry")))
            elif fmt == "CSV" and HAS_PANDAS:
                df = pd.read_csv(io.BytesIO(raw), nrows=5)
                for _, row_s in df.iterrows():
                    props = row_s.to_dict()
                    geom = None
                    if S.csv_lon and S.csv_lat and S.csv_lon in props:
                        geom = {"type": "Point",
                                "coordinates": [props.get(S.csv_lon),
                                                props.get(S.csv_lat)]}
                    rows.append(_make_row(props, geom))
    except Exception:
        pass

    if not rows:
        rows = [_make_row({c: f"<{c}>" for c in (ns.get("include") or [])}, None)]

    return rows


# ── shared UI helpers ─────────────────────────────────────────────────────────
def _registry_form(prefix: str = ""):
    """Render the dataset registry form. Mutates S.meta_* directly."""
    c1, c2 = st.columns(2)
    with c1:
        S.meta_name  = st.text_input("Dataset name *",
                                      value=S.meta_name,
                                      placeholder="e.g. Turin Buildings 2024",
                                      key=f"{prefix}meta_name")
        S.meta_desc  = st.text_area("Description", value=S.meta_desc,
                                     height=80, key=f"{prefix}meta_desc")
        S.meta_tags  = st.text_input("Tags (comma-separated)",
                                      value=S.meta_tags,
                                      placeholder="buildings, urban, 2024",
                                      key=f"{prefix}meta_tags")
    with c2:
        S.meta_crs     = st.text_input("CRS", value=S.meta_crs,
                                        key=f"{prefix}meta_crs")
        S.meta_t_start = st.date_input("Temporal start", value=S.meta_t_start,
                                        key=f"{prefix}t_start")
        S.meta_t_end   = st.date_input("Temporal end",   value=S.meta_t_end,
                                        key=f"{prefix}t_end")


def _guess_content_type(filename: str) -> str:
    name = filename.lower()
    if name.endswith(".geojson") or name.endswith(".json"):
        return "application/geo+json"
    if name.endswith(".csv"):
        return "text/csv"
    if name.endswith(".zip"):
        return "application/zip"
    if name.endswith(".gpkg"):
        return "application/geopackage+sqlite3"
    if name.endswith((".tif", ".tiff")):
        return "image/tiff"
    return "application/octet-stream"


def _register_to_meta(object_uri: str | None, dataset_id: str) -> str:
    """Insert registry row into public.meta_table; return dataset UUID."""
    init_db()
    tags = [t.strip() for t in S.meta_tags.split(",") if t.strip()]
    filename = S.uploaded_file.name if S.uploaded_file else ""
    size = None
    if S.uploaded_file:
        raw = S.uploaded_file.read()
        S.uploaded_file.seek(0)
        size = len(raw)

    ogc_url = S.ogc_url.strip() or None if S.source_type == "ogc" else None
    ogc_type = S.ogc_type if S.source_type == "ogc" else None

    return insert_record(
        name=S.meta_name or filename or "unnamed",
        description=S.meta_desc or "",
        tags=tags,
        source_type=S.source_type or "file",
        ogc_url=ogc_url,
        ogc_type=ogc_type,
        is_spatial=bool(S.is_spatial),
        spatial_type=S.geom_type,
        crs=S.target_crs or S.meta_crs or "EPSG:4326",
        footprint_geojson=None,
        temporal_start=S.meta_t_start,
        temporal_end=S.meta_t_end,
        location=None,
        filename=filename,
        file_size_bytes=size,
        file_path=None,
        object_uri=object_uri,
        record_id=dataset_id,
    )


def _post_result(resp: requests.Response):
    if resp.ok:
        st.success(f"API responded {resp.status_code}")
        try:
            st.json(resp.json())
        except Exception:
            st.text(resp.text[:2000])
    else:
        st.error(f"HTTP {resp.status_code}: {resp.text[:500]}")


def _extra_headers(raw: str) -> dict:
    """Parse 'Key: Value' lines into a header dict."""
    out: dict = {}
    for line in raw.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip()
    return out


# ─────────────────────────────────────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.title("Ingest — Warehouse Wizard")
st.caption(
    "Classify your datasource, describe it, profile the schema, map columns, "
    "then download or POST the ingest manifest and data payload."
)
_nav_bar()
st.divider()


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — DATASOURCE CLASSIFICATION
# ─────────────────────────────────────────────────────────────────────────────
if S.step == 1:
    st.subheader("Step 1 — Datasource classification")

    # ── 1a: spatial? ─────────────────────────────────────────────────────────
    st.markdown("#### Is the datasource spatial?")
    sp_choice = st.radio("Spatial data?",
                         ["Yes — contains geographic / geometry data",
                          "No  — tabular / non-spatial data"],
                         index=0 if S.is_spatial in (None, True) else 1,
                         horizontal=True)
    S.is_spatial = sp_choice.startswith("Yes")

    st.divider()

    # ── 1b: branches ─────────────────────────────────────────────────────────
    if not S.is_spatial:
        # NON-SPATIAL BRANCH
        st.markdown("#### Non-spatial source type")
        ns_src = st.radio("Source type",
                          ["File upload", "API / web service"],
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
            S.api_url     = st.text_input("API / service URL", value=S.api_url,
                                           placeholder="https://api.example.org/data")
            S.data_format = st.selectbox("Response format",
                                          ["JSON", "CSV", "Other"])

    else:
        # SPATIAL BRANCH
        st.markdown("#### Spatial source type")
        sp_src = st.radio("Source type",
                           ["File upload", "OGC service (WFS / OGC API Features)"],
                           horizontal=True,
                           index=0 if S.source_type != "ogc" else 1)
        S.source_type = "file" if sp_src == "File upload" else "ogc"

        if S.source_type == "ogc":
            # OGC path — no file needed
            S.data_class = "vector"
            S.ogc_type   = st.selectbox("OGC service type", OGC_TYPES,
                                         index=OGC_TYPES.index(S.ogc_type))
            S.ogc_url    = st.text_input("Service base URL", value=S.ogc_url,
                                          placeholder="https://example.org/wfs")
            if S.ogc_url.strip():
                if st.button("List layers"):
                    with st.spinner("Fetching capabilities…"):
                        S.ogc_layers = _list_wfs_layers(S.ogc_url.strip(), S.ogc_type)
                if S.ogc_layers:
                    S.ogc_layer  = st.selectbox("Select layer", S.ogc_layers)
                    S.data_format = f"OGC/{S.ogc_type}"
                elif S.ogc_url.strip():
                    st.info("Click List layers to fetch the available layers.")

        else:
            # FILE path — vector or raster
            st.markdown("#### Spatial data class")
            dc = st.radio("Data class", ["Vector", "Raster"],
                           horizontal=True,
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
                # auto-detect format
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

            if S.data_format in fmt_list:
                idx = fmt_list.index(S.data_format)
            else:
                idx = 0
            S.data_format = st.selectbox(
                "Format" + (" (auto-detected, override if wrong)" if S.uploaded_file else ""),
                fmt_list, index=idx)

            # CSV coordinate columns
            if S.data_class == "vector" and S.data_format == "CSV" and S.uploaded_file:
                raw = S.uploaded_file.read(); S.uploaded_file.seek(0)
                csv_cols, _ = _profile_csv(raw)
                st.markdown("**CSV coordinate columns**")
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

            # GPKG layer selector
            if S.data_class == "vector" and S.data_format == "GeoPackage" and S.uploaded_file:
                raw = S.uploaded_file.read(); S.uploaded_file.seek(0)
                layers = _gpkg_layers(raw)
                if layers:
                    S.gpkg_layer = st.selectbox("GPKG layer", layers)
                else:
                    S.gpkg_layer = st.text_input("GPKG layer name (fiona unavailable)")

    # ── readiness check ───────────────────────────────────────────────────────
    st.divider()
    ready = (
        S.is_spatial is not None
        and S.source_type is not None
        and S.data_format is not None
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

    # ── standard metadata toggle ──────────────────────────────────────────────
    S.has_std_meta = st.toggle(
        "I have standard catalog metadata (ISO 19139 XML / OGC API Records JSON / CSW)",
        value=S.has_std_meta,
    )

    if S.has_std_meta:
        S.std_meta_mode = st.radio(
            "Metadata source", ["Paste text", "Fetch from CSW endpoint"],
            horizontal=True,
            index=0 if S.std_meta_mode == "paste" else 1,
        )

        if S.std_meta_mode == "Paste text":
            fmt_radio = st.radio("Format",
                                  ["ISO 19139 (XML)", "OGC API Records (JSON)"],
                                  horizontal=True)
            S.std_meta_raw = st.text_area(
                "Paste metadata", value=S.std_meta_raw, height=200,
                placeholder="<MD_Metadata …>  or  { \"title\": \"…\" }")
            if st.button("Parse and pre-fill"):
                parsed = (_parse_iso19139(S.std_meta_raw)
                          if fmt_radio.startswith("ISO")
                          else _parse_ogc_records(S.std_meta_raw))
                S.std_meta_parsed = parsed
                _apply_meta(parsed)
                S.meta_approved   = False
                st.success(f"Parsed {len(parsed)} field(s): {list(parsed.keys())}")

        else:
            csw_url   = st.text_input("CSW base URL",
                                       placeholder="https://geonetwork.example.org/csw")
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
                        S.meta_approved   = False
                        st.success(f"Fetched and parsed {len(parsed)} field(s).")
                    except Exception as exc:
                        st.error(f"CSW fetch failed: {exc}")
                else:
                    st.warning("Provide both a CSW URL and a record ID.")

        # ── approval panel ────────────────────────────────────────────────────
        if S.std_meta_parsed:
            st.divider()
            st.markdown("#### Review auto-filled fields")
            st.caption(
                "The fields below have been pre-filled from the standard metadata. "
                "Edit them if needed, then confirm."
            )
            _registry_form(prefix="approve_")

            approved = st.checkbox("I confirm these fields are correct",
                                    value=S.meta_approved)
            S.meta_approved = approved
            if not approved:
                st.info("Tick the confirmation checkbox to proceed.")
        else:
            st.info("Parse or fetch metadata first, then review and confirm the fields.")

    else:
        # ── manual form ───────────────────────────────────────────────────────
        st.markdown("#### Dataset registry fields")
        st.caption("These become one row in the dataset registry (`meta_table` / `dim_dataset`).")
        _registry_form(prefix="manual_")

    st.divider()
    can_next = (
        bool(S.meta_name.strip())
        and (not S.has_std_meta or S.meta_approved or not S.std_meta_parsed)
    )
    _back_next(1, 3, next_disabled=not can_next)
    if not can_next:
        st.caption("Dataset name is required. " +
                   ("Confirm the auto-filled fields to proceed." if S.has_std_meta else ""))


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — PROFILING  (bypassed for OGC / API sources)
# ─────────────────────────────────────────────────────────────────────────────
elif S.step == 3:
    is_file_source = S.source_type == "file"

    if not is_file_source:
        # ── BYPASS for OGC/API ────────────────────────────────────────────────
        st.subheader("Step 3 — Profiling  [OGC/API source — partial profile]")
        st.info(
            f"Source type is **{S.source_type.upper()}** — no local file to profile. "
            "Fetching one sample record to extract property names and CRS."
        )
        if not S.columns:
            with st.spinner("Sampling remote service…"):
                url = S.ogc_url if S.source_type == "ogc" else S.api_url
                if S.source_type == "ogc":
                    if S.ogc_type == "OGC API Features" and S.ogc_layer:
                        url = S.ogc_url.rstrip("/") + f"/collections/{S.ogc_layer}/items"
                    cols, geom_col, crs, geom_type, _ = _profile_wfs(url, S.ogc_type)
                    S.columns      = cols
                    S.geom_col     = geom_col
                    S.detected_crs = crs
                    S.geom_type    = geom_type
                else:
                    try:
                        r = requests.get(url, timeout=10)
                        r.raise_for_status()
                        data = r.json()
                        if isinstance(data, list) and data:
                            S.columns = sorted(data[0].keys())
                        elif isinstance(data, dict):
                            S.columns = sorted(data.keys())
                    except Exception as exc:
                        st.error(f"API fetch failed: {exc}")

        if S.columns:
            st.success(f"Found {len(S.columns)} column(s).")
            g = st.columns(4)
            for i, c in enumerate(S.columns):
                g[i % 4].code(c)
        else:
            st.warning("No columns found. Enter them manually below.")
            mc = st.text_area("Column names (one per line)")
            if mc.strip():
                S.columns = [c.strip() for c in mc.splitlines() if c.strip()]

        _back_next(2, 4)

    else:
        # ── FILE PROFILE ──────────────────────────────────────────────────────
        st.subheader("Step 3 — Profiling")
        st.caption("Reads columns, CRS, geometry type and feature count from a file sample.")

        if S.uploaded_file and not S.columns:
            with st.spinner("Profiling…"):
                raw = S.uploaded_file.read()
                S.uploaded_file.seek(0)
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
                    S.geom_col = None
                    S.detected_crs = None

                else:
                    if HAS_PANDAS:
                        try:
                            df = pd.read_json(io.BytesIO(raw))
                            S.columns = list(df.columns)
                        except Exception:
                            pass

        # ── CRS panel ─────────────────────────────────────────────────────────
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
                st.markdown(f"**Detected from file:** `{S.detected_crs or 'not found'}`")
                needs = (S.detected_crs and S.meta_crs
                         and S.detected_crs.upper() != S.meta_crs.upper())
                if needs:
                    st.warning(f"Source `{S.detected_crs}` differs from target `{S.meta_crs}`. "
                               "ETL will reproject.")
                elif S.detected_crs:
                    st.success("Source and target CRS match — no reprojection needed.")
                else:
                    st.info("CRS not auto-detected — set it manually.")
            with cr2:
                ov = st.text_input("Override source CRS (if wrong)",
                                    value=S.detected_crs or "",
                                    key="crs_ov")
                if ov.strip():
                    S.detected_crs = ov.strip()
                tgt = st.text_input("Target storage CRS",
                                     value=S.meta_crs or "EPSG:4326",
                                     key="tgt_crs")
                S.meta_crs   = tgt
                S.target_crs = tgt

            st.divider()
            st.markdown("#### Columns detected")
            g = st.columns(4)
            for i, c in enumerate(S.columns):
                tag = " [geom]" if c == S.geom_col else ""
                g[i % 4].code(f"{c}{tag}")

        else:
            st.warning("No columns detected. Enter them manually.")
            mc = st.text_area("Column names (one per line)",
                               placeholder="id\nname\ngeometry\npopulation")
            if mc.strip():
                S.columns = [c.strip() for c in mc.splitlines() if c.strip()]
            ov = st.text_input("Source CRS (manual)", placeholder="EPSG:4326",
                                key="manual_crs")
            if ov.strip():
                S.detected_crs = ov.strip()

        if st.button("Re-profile"):
            for k in ("columns", "geom_col", "detected_crs", "geom_type", "feature_count"):
                setattr(S, k, None if k != "columns" else [])
            st.rerun()

        _back_next(2, 4)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — COLUMN MAPPING
# ─────────────────────────────────────────────────────────────────────────────
elif S.step == 4:
    st.subheader("Step 4 — Column mapping")
    st.caption(
        "Assign every detected column to its warehouse role. "
        "Unassigned columns default to the JSONB `attributes` column."
    )

    cols    = S.columns or []
    geom_col = S.geom_col

    # ── PK ────────────────────────────────────────────────────────────────────
    st.markdown("### Primary Key (PK)")
    pk_idx = PK_POLICIES.index(S.pk_policy) if S.pk_policy in PK_POLICIES else 0
    S.pk_policy = st.radio("PK strategy", PK_POLICIES, index=pk_idx)
    if "natural_key" in S.pk_policy:
        nat_opts = ["—"] + [c for c in cols if c != geom_col]
        nat_sel  = S.pk_natural_col if S.pk_natural_col in nat_opts else "—"
        sel = st.selectbox("Natural key column", nat_opts,
                            index=nat_opts.index(nat_sel))
        S.pk_natural_col = None if sel == "—" else sel

    st.divider()

    # ── FK ────────────────────────────────────────────────────────────────────
    st.markdown("### Foreign Key(s) (FK)")
    st.caption(
        "Default is **none** — the `dataset_id` FK is auto-assigned by the ingest worker. "
        "Select only if the file already contains explicit relationship keys."
    )
    fk_opts   = [c for c in cols if c != geom_col]
    S.fk_cols = st.multiselect(
        "FK column(s) from the source file",
        fk_opts,
        default=[c for c in S.fk_cols if c in fk_opts],
    )
    if not S.fk_cols:
        st.info("No FK selected — dataset_id will be auto-assigned at load time.")

    st.divider()

    # ── Spatial ───────────────────────────────────────────────────────────────
    if S.is_spatial and S.data_class == "vector":
        st.markdown("### Spatial column")
        S.target_crs = st.text_input("Target storage CRS", value=S.target_crs)

        if S.data_format == "CSV":
            st.info(
                f"Geometry built from columns set in Step 1: "
                f"lon=`{S.csv_lon}`  lat=`{S.csv_lat}`"
                + (f"  wkt=`{S.csv_wkt}`" if S.csv_wkt else "")
            )
            S.spatial_col = "__geometry__"
        else:
            geom_opts = [c for c in cols if "geom" in c.lower() or c == geom_col] or cols
            default_g = geom_col if geom_col in geom_opts else (geom_opts[0] if geom_opts else None)
            S.spatial_col = st.selectbox(
                "Geometry column",
                geom_opts,
                index=geom_opts.index(default_g) if default_g in geom_opts else 0,
            )
        st.divider()

    # ── Non-spatial JSONB ────────────────────────────────────────────────────
    st.markdown("### Non-spatial columns  →  `attributes` JSONB")
    reserved = {S.spatial_col or "", geom_col or ""} | set(S.fk_cols) | \
               ({S.pk_natural_col} if S.pk_natural_col else set())
    remaining = [c for c in cols if c not in reserved]

    ns1, ns2 = st.columns(2)
    with ns1:
        st.markdown("**Include in JSONB**")
        default_inc = ([c for c in S.nonspatial_cols if c in remaining]
                        or remaining)
        S.nonspatial_cols = st.multiselect(
            "Include", remaining, default=default_inc,
            label_visibility="collapsed")
    with ns2:
        st.markdown("**Drop (exclude entirely)**")
        droppable     = [c for c in remaining if c not in S.nonspatial_cols]
        S.dropped_cols = st.multiselect(
            "Drop", droppable,
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
        if st.button("Build manifest", type="primary", key="next_5"):
            S.manifest = _build_manifest()
            _goto(5)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 — OUTPUT
# ─────────────────────────────────────────────────────────────────────────────
elif S.step == 5:
    st.subheader("Step 5 — Output")

    if not S.manifest:
        S.manifest = _build_manifest()

    manifest_str = json.dumps(S.manifest, indent=2, default=str)

    # Build ingested-rows preview
    ingested_rows = _build_ingested_rows(S.manifest)
    ingested_str  = json.dumps(ingested_rows, indent=2, default=str)

    # ── Summary ───────────────────────────────────────────────────────────────
    wm  = S.manifest.get("warehouse_mapping", {})
    reg = S.manifest.get("registry", {})
    st.markdown(
        f"**Dataset:** {reg.get('name', '—')}  \n"
        f"**Format:** `{S.data_format}` · class `{S.data_class}` · source `{S.source_type}`  \n"
        f"**PK policy:** `{wm.get('pk',{}).get('policy','—')}`  \n"
        f"**Spatial:** `{S.is_spatial}` · geometry `{S.geom_type or '—'}`  \n"
        f"**Detected CRS:** `{S.detected_crs or '—'}` → target `{S.target_crs}`  \n"
        f"**JSONB attributes:** {len(wm.get('non_spatial',{}).get('include',[]))} column(s)  \n"
        f"**Manifest ID:** `{S.manifest.get('manifest_id', '')}`"
    )

    if st.button("Regenerate manifest"):
        S.manifest = _build_manifest()
        st.rerun()

    st.divider()

    # ── Download section ──────────────────────────────────────────────────────
    st.markdown("### Download")
    dl1, dl2 = st.columns(2)
    with dl1:
        st.markdown("**Ingest manifest** — warehouse mapping contract")
        st.download_button(
            "Download manifest JSON",
            data=manifest_str,
            file_name=f"manifest_{S.manifest.get('manifest_id','x')[:8]}.json",
            mime="application/json",
            use_container_width=True,
        )
    with dl2:
        st.markdown("**Ingested data** — sample rows in warehouse schema (PK / FK / geom / JSONB)")
        st.download_button(
            "Download ingested JSON",
            data=ingested_str,
            file_name=f"ingested_{S.manifest.get('manifest_id','x')[:8]}.json",
            mime="application/json",
            use_container_width=True,
        )

    st.divider()

    # ── JSON viewers ──────────────────────────────────────────────────────────
    with st.expander("Manifest JSON"):
        st.code(manifest_str, language="json")
    with st.expander("Ingested rows JSON  (up to 5 sample rows)"):
        st.code(ingested_str, language="json")

    st.divider()

    # ── MinIO + meta_table ────────────────────────────────────────────────────
    st.markdown("### Store file in MinIO + register meta_table")
    st.caption(
        "Uploads the original file to the `datawh` bucket and inserts a registry row "
        "with `object_uri` (e.g. `s3://datawh/<dataset_id>/<filename>`)."
    )

    if S.dataset_id:
        st.success(f"Registered — dataset_id `{S.dataset_id}`")
        if S.object_uri:
            st.code(S.object_uri, language="text")
        else:
            st.caption("No file uploaded (OGC/API source) — meta_table row only.")
    else:
        minio_ok = minio_store.is_configured()
        if minio_ok:
            st.info("MinIO configured — ready to upload.")
        else:
            st.warning(
                "MinIO not configured. Add a `[minio]` section to "
                "`.streamlit/secrets.toml` (see secrets.toml.example)."
            )

        can_store = bool(S.meta_name.strip()) and (
            S.source_type != "file" or S.uploaded_file is not None
        )
        if st.button(
            "Upload to MinIO & register",
            type="primary",
            key="minio_register",
            disabled=not can_store,
        ):
            if not S.meta_name.strip():
                st.error("Dataset name is required (Step 2).")
            else:
                try:
                    dataset_id = str(uuid.uuid4())
                    object_uri = None

                    if S.source_type == "file" and S.uploaded_file:
                        if not minio_store.is_configured():
                            raise RuntimeError("MinIO is not configured.")
                        raw = S.uploaded_file.read()
                        S.uploaded_file.seek(0)
                        with st.spinner("Uploading to MinIO…"):
                            object_uri = minio_store.upload(
                                raw,
                                S.uploaded_file.name,
                                prefix=dataset_id,
                                content_type=_guess_content_type(S.uploaded_file.name),
                            )

                    with st.spinner("Writing meta_table…"):
                        _register_to_meta(object_uri, dataset_id)

                    S.dataset_id = dataset_id
                    S.object_uri = object_uri
                    # Refresh manifest so source.object_uri is included
                    S.manifest = _build_manifest()
                    st.success(
                        f"Done — dataset_id `{dataset_id}`"
                        + (f" · `{object_uri}`" if object_uri else " (no file upload)")
                    )
                    st.rerun()
                except Exception as exc:
                    st.error(f"Store failed: {exc}")

    st.divider()

    # ── POST section ──────────────────────────────────────────────────────────
    st.markdown("### Send to API endpoints")
    st.caption(
        "Optionally POST the manifest and/or the ingested data to separate endpoints. "
        "Extra headers (e.g. Content-Type, X-Custom-Header) go in the 'Additional headers' box "
        "as `Key: Value` lines."
    )

    tab_manifest, tab_data = st.tabs(["Manifest endpoint", "Data endpoint"])

    with tab_manifest:
        S.manifest_api_url   = st.text_input(
            "Manifest API URL",
            value=S.manifest_api_url,
            placeholder="http://localhost:8000/api/v1/ingest/manifest",
            key="mapi_url")
        S.manifest_api_token = st.text_input(
            "Bearer token", value=S.manifest_api_token,
            type="password", key="mapi_tok")
        S.manifest_api_headers = st.text_area(
            "Additional headers (Key: Value, one per line)",
            value=S.manifest_api_headers,
            height=80, key="mapi_hdrs",
            placeholder="X-Workspace: myteam\nX-Schema: dw_main")
        if st.button("POST manifest", type="primary", key="post_manifest"):
            hdrs = {"Content-Type": "application/json"}
            if S.manifest_api_token.strip():
                hdrs["Authorization"] = f"Bearer {S.manifest_api_token.strip()}"
            hdrs.update(_extra_headers(S.manifest_api_headers))
            try:
                with st.spinner("Posting…"):
                    resp = requests.post(S.manifest_api_url, json=S.manifest,
                                         headers=hdrs, timeout=30)
                _post_result(resp)
            except requests.exceptions.ConnectionError:
                st.error("Could not connect — is the API running?")
            except Exception as exc:
                st.error(f"Request failed: {exc}")

    with tab_data:
        S.data_api_url   = st.text_input(
            "Data API URL",
            value=S.data_api_url,
            placeholder="http://localhost:8000/api/v1/ingest/data",
            key="dapi_url")
        S.data_api_token = st.text_input(
            "Bearer token", value=S.data_api_token,
            type="password", key="dapi_tok")
        S.data_api_headers = st.text_area(
            "Additional headers (Key: Value, one per line)",
            value=S.data_api_headers,
            height=80, key="dapi_hdrs",
            placeholder="X-Dataset-ID: abc123\nX-Schema: dw_main")
        if st.button("POST ingested data", type="primary", key="post_data"):
            hdrs = {"Content-Type": "application/json"}
            if S.data_api_token.strip():
                hdrs["Authorization"] = f"Bearer {S.data_api_token.strip()}"
            hdrs.update(_extra_headers(S.data_api_headers))
            try:
                with st.spinner("Posting…"):
                    resp = requests.post(S.data_api_url, json=ingested_rows,
                                         headers=hdrs, timeout=30)
                _post_result(resp)
            except requests.exceptions.ConnectionError:
                st.error("Could not connect — is the API running?")
            except Exception as exc:
                st.error(f"Request failed: {exc}")

    st.divider()
    col_back, col_over = st.columns(2)
    with col_back:
        if st.button("Back", key="back_5_btn"):
            _goto(4)
    with col_over:
        if st.button("Start over", use_container_width=True, key="startover"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
