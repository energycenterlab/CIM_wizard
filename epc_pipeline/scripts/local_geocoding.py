#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import re
import unicodedata
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial
from typing import Dict, List, Optional, Tuple
import geopandas as gpd
import numpy as np
import pandas as pd
from rapidfuzz import fuzz, process
from tqdm import tqdm
from loguru import logger
# opzionale per KNN geografico
try:
    from sklearn.neighbors import BallTree
    _HAS_SKLEARN = True
except Exception:
    _HAS_SKLEARN = False
    BallTree = None

# ----------------------------
# Utility
# ----------------------------

ABBREV = {
    r"\bC\.?SO\b": "CORSO",
    r"\bP\.?ZZA\b": "PIAZZA",
    r"\bP\.?ZA\b": "PIAZZA",
    r"\bV\.?LE\b": "VIALE",
    r"\bV\.?IA\b": "VIA",
    r"\bSTRADA\s+COMUNALE\b": "STRADA",
    r"\bSTRADA\s+PROVINCIALE\b": "SP",
    r"\bSTRADA\s+STATALE\b": "SS",
}

CIVICO_RE = re.compile(r"(?<!\w)(?P<num>\d{1,5})(?:\s*[/\-]?\s*(?P<suf>[A-Z]{1,3}))?(?!\w)")

def unaccent(s: str) -> str:
    if s is None: return ""
    return "".join(c for c in unicodedata.normalize("NFKD", str(s)) if not unicodedata.combining(c))

def norm_comune(s: str) -> str:
    return unaccent(s).upper().strip() if s is not None else ""

def norm_cap(s: str) -> str:  # non usato nel matching, ma lo tengo se serve in futuro
    if s is None: return ""
    m = re.search(r"\b(\d{5})\b", str(s))
    return m.group(1) if m else ""

def norm_via(s: str) -> str:
    if s is None: return ""
    s = unaccent(s).upper()
    s = re.sub(r"[\,\.;:]", " ", s)
    for pat, rep in ABBREV.items():
        s = re.sub(pat, rep, s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def norm_civico(s: str) -> str:
    if s is None: return ""
    s = unaccent(str(s)).upper().strip()
    if s in {"", "SNC", "0", "S.N.C."}: return ""
    s = s.replace("/", "").replace(" ", "")
    m = re.match(r"^0*(\d{1,5})([A-Z]{0,3})$", s)
    if m:
        num, suf = m.group(1), m.group(2) or ""
        return f"{int(num)}{suf}"
    return s

# Compila regex una volta (performance)
RE_MAIN = re.compile(r'^\s*(\d{1,5})')  # numero principale all'inizio (più comune)
RE_ANYNUM = re.compile(r'(\d{1,5})')    # fallback se il numero non è all'inizio

RE_SCALA = re.compile(r'\bSC(?:ALA)?\.?\s*[:\-]?\s*(\d{1,3})\b')
RE_INT_NUM = re.compile(r'\bINT(?:ERNO)?\.?\s*[:\-]?\s*(\d{1,4})\b')
RE_INT_LET = re.compile(r'\bINT(?:ERNO)?\.?\s*[:\-]?\s*([A-Z])\b')

# slash-lettera: "/A" oppure " / A "
RE_SLASH_LET = re.compile(r'/?\s*/\s*([A-Z])\b')

# bis con eventuale slash-lettera: "BIS/A" o "BIS A" o "BIS /A"
RE_BIS = re.compile(r'\bBIS\b(?:\s*/?\s*([A-Z]))?')

# Pattern "12A" attaccato (lettera subito dopo numero principale)
RE_NUM_LET_SUFFIX = re.compile(r'^\s*(\d{1,5})\s*([A-Z])\b')

def norm_civico2(raw: str):
    """
    Ritorna dict con:
      - civico (int o None)
      - civico_sub (str o None) in una delle forme ammesse
      - canon (str o None): civico + civico_sub (senza spazi extra)
    """
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return None
        #return {"civico": None, "civico_sub": None, "canon": None, "raw_clean": None}

    s = str(raw).upper().strip()

    # Normalizzazioni base
    s = s.replace(",", " ").replace(";", " ").replace(".", ".")  # manteniamo il punto per INT.
    s = re.sub(r"\s+", " ", s)
    s = s.replace("INTERNO", "INT").replace("INT ", "INT. ")
    s = re.sub(r"\bINT\.?\b", "INT.", s)        # INT -> INT.
    s = re.sub(r"\bSC\.?\b", "SCALA", s)        # SC -> SCALA
    s = re.sub(r"\s*/\s*", "/", s)              # normalizza slash: " / " -> "/"
    s = re.sub(r"\s*-\s*", "-", s)

    raw_clean = s

    # 1) Numero principale
    m = RE_MAIN.search(s)
    if not m:
        m = RE_ANYNUM.search(s)
    civico = int(m.group(1)) if m else None
    if civico is None:
        return {"civico": None, "civico_sub": None, "canon": None, "raw_clean": raw_clean}

    civico_sub = None

    # 2) Decide la sub secondo priorità (più “strutturato” vince)
    # 2a) SCALA <num>
    m = RE_SCALA.search(s)
    if m:
        civico_sub = f"SCALA {int(m.group(1))}"

    # 2b) INT. <num> [e opzionalmente INT. <lettera>] oppure INT. <num>/<lettera>
    if civico_sub is None:
        m_int_num = RE_INT_NUM.search(s)
        if m_int_num:
            int_num = int(m_int_num.group(1))

            # caso "INT. 3/A" o "INT. 3A" (gestiamo /A)
            m_after = re.search(rf"\bINT\.\s*{int_num}\s*/\s*([A-Z])\b", s)
            if m_after:
                civico_sub = f"INT. {int_num}/{m_after.group(1)}"
            else:
                # caso "INT. 3 INT. A" (o "INT. 3 INT A")
                m_int_let = re.search(r"\bINT\.\s*[0-9]{1,4}\s+INT\.\s*([A-Z])\b", s)
                if m_int_let:
                    civico_sub = f"INT. {int_num} INT. {m_int_let.group(1)}"
                else:
                    civico_sub = f"INT. {int_num}"

    # 2c) BIS[/<lettera>]
    if civico_sub is None:
        m = RE_BIS.search(s)
        if m:
            let = m.group(1)
            civico_sub = f"BIS/{let}" if let else "BIS"

    # 2d) "/<lettera>" (slash lettera) — ma evita di prendere la lettera attaccata al numero tipo "12A"
    if civico_sub is None:
        # cerca una slash-lettera non immediatamente dopo il numero principale già preso
        m = re.search(r"\b" + str(civico) + r"\b.*?/([A-Z])\b", s)
        if m:
            civico_sub = f"/{m.group(1)}"

    # 2e) lettera attaccata al civico "12A" -> trasformiamo in "/A" (compatibile con la tua struttura)
    if civico_sub is None:
        m = RE_NUM_LET_SUFFIX.match(s)
        if m and int(m.group(1)) == civico:
            civico_sub = f"/{m.group(2)}"

    # 3) Stringa canonica unica
    # Nota: niente spazi tra civico e civico_sub, perché civico_sub include già eventuali spazi (INT. 3, SCALA 2)
    canon = f"{civico}{civico_sub or ''}"
    return canon
    #return {"civico": civico, "civico_sub": civico_sub, "canon": canon, "raw_clean": raw_clean}

def civico_num(civ: str) -> Optional[int]:
    if not civ: return None
    m = re.match(r"^(\d+)", civ)
    return int(m.group(1)) if m else None

def split_street_number(via_raw: str) -> Tuple[str, str]:
    via = norm_via(via_raw)
    m_last = None
    for m in CIVICO_RE.finditer(via):
        m_last = m
    if not m_last:
        return via, ""
    num = m_last.group("num")
    suf = m_last.group("suf") or ""
    civico = f"{int(num)}{suf}"
    start, end = m_last.span()
    via_wo = (via[:start] + " " + via[end:]).strip()
    via_wo = re.sub(r"\s+", " ", via_wo)
    via_wo = re.sub(r"[,\.;:\-]\s*$", "", via_wo).strip()
    return via_wo, civico

# ----------------------------
# Indice locale (CAP ignorato)
# ----------------------------

class AddressIndex:
    """
    Indice locale per TORINO (o più comuni), CAP facoltativo/ignorato:
      - exact[(comune, via, civico)] -> (lat, lon)
      - vie_per_comune[comune] -> [via_normalizzate]
      - knn[(comune, via)] -> struttura ausiliaria per fallback (civici e coordinate)
    """
    def __init__(self, df_rubrica: pd.DataFrame,
                 comune_col="comune", cap_col="cap",
                 via_col="via", civico_col="civico", civico_sub_col=None,
                 lat_col="lat", lon_col="lon"):
        df = df_rubrica.copy()

        df["comune_n"] = df[comune_col].map(norm_comune)
        df["via_n"]    = df[via_col].map(norm_via)
        df["civico_n"] = (df[civico_col].astype(str) + df[civico_sub_col].fillna('')
).map(norm_civico) if civico_sub_col else df[civico_col].map(norm_civico)
        df["lat"] = pd.to_numeric(df[lat_col], errors="coerce")
        df["lon"] = pd.to_numeric(df[lon_col], errors="coerce")
        df = df.dropna(subset=["lat","lon"])
        self.df = df

        # match ESATTO per (comune, via, civico)
        self.index_exact: Dict[Tuple[str,str,str], Tuple[float,float]] = {}
        for _, r in df.iterrows():
            if r["via_n"]:
                key = (r["comune_n"], r["via_n"], r["civico_n"])
                self.index_exact[key] = (float(r["lat"]), float(r["lon"]))

        # liste vie per fuzzy (per COMUNE)
        vie_per_comune = defaultdict(set)
        for _, r in df.iterrows():
            if r["via_n"]:
                vie_per_comune[r["comune_n"]].add(r["via_n"])
        self.vie_per_comune: Dict[str, List[str]] = {k: sorted(v) for k, v in vie_per_comune.items()}

        # strutture KNN per (comune, via): civici + coords (+ BallTree se disponibile)
        self.knn: Dict[Tuple[str,str], Dict[str, object]] = {}
        grp = df.groupby(["comune_n", "via_n"], dropna=False)
        for (c, v), g in grp:
            civs = g["civico_n"].fillna("").tolist()
            lats = g["lat"].astype(float).to_numpy()
            lons = g["lon"].astype(float).to_numpy()
            civ_nums = [civico_num(x) for x in civs]
            data = {"civici": civs, "civ_nums": civ_nums, "lats": lats, "lons": lons,
                    "tree": None, "coords_rad": None}
            if _HAS_SKLEARN and len(g) >= 2:
                coords_rad = np.vstack([np.radians(lats), np.radians(lons)]).T[:, ::-1]  # (lon,lat) in rad
                data["coords_rad"] = coords_rad
                data["tree"] = BallTree(coords_rad, metric="haversine")
            self.knn[(c, v)] = data

        # BallTree per COMUNE (fallback geometrico quando manca il civico)
        self.tree_by_comune: Dict[str, Dict[str, object]] = {}
        grp_c = df.groupby(["comune_n"], dropna=False)
        for c, g in grp_c:
            lats = g["lat"].astype(float).to_numpy()
            lons = g["lon"].astype(float).to_numpy()
            vias = g["via_n"].fillna("").tolist()
            civs = g["civico_n"].fillna("").tolist()
            entry = {
                "lats": lats, "lons": lons,
                "vias": vias, "civici": civs,
                "tree": None, "coords_rad": None
            }
            if _HAS_SKLEARN and len(g) >= 1:
                coords_rad = np.vstack([np.radians(lats), np.radians(lons)]).T[:, ::-1]  # (lon,lat) in rad
                entry["coords_rad"] = coords_rad
                entry["tree"] = BallTree(coords_rad, metric="haversine")
            self.tree_by_comune[c[0]] = entry

    def _nearest_by_number(self, key, target_num: int) -> Optional[Tuple[float,float,str]]:
        data = self.knn.get(key)
        if not data: return None
        best = None; bestd = 10**9; best_civ=""
        for civ, n, lat, lon in zip(data["civici"], data["civ_nums"], data["lats"], data["lons"]):
            if n is None: continue
            d = abs(n - target_num)
            if d < bestd:
                bestd = d; best = (lat, lon); best_civ = civ
        if best is None: return None
        return best[0], best[1], best_civ

    @staticmethod
    def _haversine_meters(lat1, lon1, lat2, lon2) -> float:
        # distanza approssimata in metri
        R = 6371000.0
        phi1, phi2 = np.radians([lat1, lat2])
        dphi = np.radians(lat2 - lat1)
        dlmb = np.radians(lon2 - lon1)
        a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlmb / 2) ** 2
        return float(2 * R * np.arcsin(np.sqrt(a)))

    def _nearest_in_comune(self, comune_n: str, lat0: float, lon0: float) -> Optional[
        Tuple[float, float, str, str, float]]:
        data = self.tree_by_comune.get(comune_n)
        if not data or np.isnan(lat0) or np.isnan(lon0):
            return None
        if data.get("tree") is not None and data.get("coords_rad") is not None:
            q = np.array([[np.radians(lon0), np.radians(lat0)]])  # (lon,lat) in rad
            dist_rad, idx = data["tree"].query(q, k=1)
            i = int(idx[0, 0]);
            d_m = float(dist_rad[0, 0] * 6371000.0)
            return float(data["lats"][i]), float(data["lons"][i]), data["vias"][i], data["civici"][i], d_m
        # fallback senza sklearn: ricerca lineare
        best_i, best_d = None, float("inf")
        for i, (la, lo) in enumerate(zip(data["lats"], data["lons"])):
            d = self._haversine_meters(lat0, lon0, la, lo)
            if d < best_d:
                best_d, best_i = d, i
        if best_i is None:
            return None
        return float(data["lats"][best_i]), float(data["lons"][best_i]), data["vias"][best_i], data["civici"][
            best_i], float(best_d)

    def _median_on_street(self, key) -> Optional[Tuple[float,float,str]]:
        data = self.knn.get(key)
        if not data: return None
        idxs = [i for i, n in enumerate(data["civ_nums"]) if n is not None]
        if idxs:
            ord_idx = sorted(idxs, key=lambda i: data["civ_nums"][i])
            mid = ord_idx[len(ord_idx)//2]
            return float(data["lats"][mid]), float(data["lons"][mid]), data["civici"][mid]
        mid = len(data["civici"])//2
        return float(data["lats"][mid]), float(data["lons"][mid]), data["civici"][mid]

    def match_one(self, comune: str, cap: str, via: str, civico: str,
                  sim_threshold: int = 90,
                  fallback_lat: Optional[float] = None,
                  fallback_lon: Optional[float] = None
                  ) -> Tuple[Optional[float], Optional[float], str, str, str, float, str]:
        """
        CAP è ignorato. Ritorna: lat, lon, provider, via_match, civico_match, score, conf
        """
        c = norm_comune(comune)
        v = norm_via(via)
        h = norm_civico(civico)
        h_num = civico_num(h)

        # 1) esatto
        hit = self.index_exact.get((c, v, h))
        if hit:
            lat, lon = hit
            return lat, lon, "local_exact", v, h, 100.0, "alta"



        # 2) fuzzy via nel COMUNE
        candidates = self.vie_per_comune.get(c, [])
        best_via, best_score = None, 0
        if candidates:
            best_via, best_score, _ = process.extractOne(v, candidates, scorer=fuzz.token_set_ratio)

        # 2a) civico esatto sulla via migliore
        if best_via and best_score >= sim_threshold and h:
            # prova civico esatto su via migliore
            hit2 = self.index_exact.get((c, best_via, h))
            if hit2:
                lat, lon = hit2
                return lat, lon, "local_fuzzy_comune", best_via, h, float(best_score), ("alta" if best_score >= 95 else "media")
        # 4) FALLBACK GEOMETRICO: se NON c'è civico e ho coords di default → nearest in COMUNE
        if (h_num is None) and (fallback_lat is not None) and (fallback_lat is not None) and (
        not np.isnan(fallback_lat)) and (not np.isnan(fallback_lon)):
            res = self._nearest_in_comune(c, float(fallback_lat), float(fallback_lon))
            if res:
                lat, lon, via_found, civ_found, d_m = res
                # confidenza basata sulla distanza
                if d_m < 50:
                    conf = "alta"
                elif d_m < 150:
                    conf = "media"
                else:
                    conf = "bassa"
                # score "sintetico": se non avevo via valida, uso 0; altrimenti il best_score (anche se < soglia)
                score = float(best_score or 0)
                return lat, lon, "local_nearest_coord", via_found or "", civ_found or "", score, conf

        # 3) KNN intra-via (per civico non trovato)
        if best_via:
            key = (c, best_via)
            if h_num is not None:
                res = self._nearest_by_number(key, h_num)
                if res:
                    lat, lon, civ_found = res
                    conf = "media" if best_score >= 92 else "bassa"
                    return lat, lon, "local_knn_num", best_via, civ_found, float(best_score), conf
            # senza numero richiesto → mediano della via
            res = self._median_on_street(key)
            if res:
                lat, lon, civ_found = res
                return lat, lon, "local_knn_proxy", best_via, civ_found, float(best_score), "bassa"

        return None, None, "not_found", "", "", 0.0, "scarsa"

# ----------------------------
# Batch runner
# ----------------------------

def prepare_input_df(df: pd.DataFrame, addr_col: str, cap_col: Optional[str], comune_default: str,
                     comune_col: Optional[str] = None, civico_col: Optional[str] = None,
                     lat0_col: Optional[str] = None, lon0_col: Optional[str] = None) -> pd.DataFrame:
    out = df.copy()
    out["_comune"] = out[comune_col].fillna(comune_default) if (comune_col and comune_col in out.columns) else comune_default

    if civico_col and civico_col in out.columns:
        out["_civico"] = out[civico_col].map(norm_civico)
        out["_via"] = out[addr_col].map(norm_via)
    else:
        via_wo, civ = [], []
        for s in out[addr_col].astype(str).tolist():
            v, h = split_street_number(s)
            via_wo.append(v); civ.append(h)
        out["_via"] = via_wo; out["_civico"] = civ

    # CAP opzionale, non usato: lo normalizzo e lo conservo solo per audit
    if cap_col and cap_col in out.columns:
        out["_cap"] = out[cap_col].map(norm_cap)
    else:
        out["_cap"] = ""

        # Coordinate di default (fallback geometrico)
    if lat0_col and lat0_col in out.columns and lon0_col and lon0_col in out.columns:
        out["_lat0"] = pd.to_numeric(out[lat0_col], errors="coerce")
        out["_lon0"] = pd.to_numeric(out[lon0_col], errors="coerce")
    else:
        out["_lat0"] = np.nan
        out["_lon0"] = np.nan

    return out

def process_chunk(df_chunk: pd.DataFrame, idx: AddressIndex,
                  id_col: str, sim_threshold: int) -> pd.DataFrame:
    lat, lon, prov, via_m, civ_m, score, conf, status = [], [], [], [], [], [], [], []
    for _, r in df_chunk.iterrows():
        la, lo, pr, vm, hm, sc, cf = idx.match_one(
            r["_comune"], r.get("_cap",""), r["_via"], r["_civico"], sim_threshold=sim_threshold,
            fallback_lat=r.get("_lat0", np.nan),
            fallback_lon=r.get("_lon0", np.nan)
        )
        lat.append(la); lon.append(lo); prov.append(pr)
        via_m.append(vm); civ_m.append(hm); score.append(sc); conf.append(cf)
        status.append("matched" if la is not None and sc >= 80 else ("low_conf_match" if la is not None else "not_found"))
    out = df_chunk.copy()
    out["lat"] = lat; out["lon"] = lon
    out["provider"] = prov
    out["via_match"] = via_m; out["civico_match"] = civ_m
    out["similarity_score"] = score; out["confidence"] = conf; out["status"] = status
    return out

def read_any(path: str,sep=',',**kwargs) -> pd.DataFrame:

    p = path.lower()
    if p.endswith((".parquet",".gpq")): return pd.read_parquet(path)
    if p.endswith(".csv"): return pd.read_csv(path, dtype=str, sep=sep)
    if p.endswith(".gpkg"): return gpd.read_file(path, layer= kwargs.get('layer',0))
    if p.endswith(".xlsx"): return pd.read_excel(path, dtype=str)

def write_any(df: pd.DataFrame, path: str,**kwargs):
    p = path.lower()
    if p.endswith((".parquet",".gpq")): df.to_parquet(path, index=False)
    elif p.endswith(".csv"): df.to_csv(path, index=False)
    elif p.endswith(".gpkg"): gpd.GeoDataFrame(df).to_file(path, layer= kwargs.get('layer',0), driver="GPKG")
    else: df.to_parquet(path + ".parquet", index=False)

def main(args=None):
    defaults = {
        '--rubrica': r'C:\Users\Mocci\PycharmProjects\GeneralPurpose\siatel_pipeline\addresses_ped_buffer.csv',
        '--addr-col': "desc_indirizzo",
        '--comune-col': 'desc_comune',
        '--civico-col': 'num_civico',
        '--lat0-col': 'coord_n',  # <-- se esistono
        '--lon0-col': 'coord_e',  # <-- se esistono
        '--layer': 'ace_clean'
    }
    ap = argparse.ArgumentParser(description="Geocoding locale Torino (CAP facoltativo/ignorato)")
    ap.add_argument("--rubrica",default=defaults["--rubrica"], help="CSV TORINO: comune, via, civico, lat, lon (+cap opzionale)")
    ap.add_argument("--in", dest="inp", required=True, help="Dataset da geocodificare")
    ap.add_argument("--layer", dest="layer",default=defaults["--layer"] , help="Dataset da geocodificare")
    ap.add_argument("--out", dest="outp", required=True, help="Output (parquet/csv)")
    ap.add_argument("--addr-col", default=defaults["--addr-col"], help="Colonna indirizzo testo")
    ap.add_argument("--cap-col", default=None, help="Colonna CAP (facoltativa, ignorata nel match)")
    ap.add_argument("--comune-col", default=defaults['--comune-col'], help="Colonna comune; se assente usa --comune")
    ap.add_argument("--civico-col", default=defaults['--civico-col'], help="Se già separato, altrimenti lo estraggo dall'indirizzo")
    ap.add_argument("--comune", default="TORINO", help="Default comune se manca la colonna")
    ap.add_argument("--id-col", default="Codice Identificativo", help="Campo ID per audit")
    ap.add_argument("--sim-threshold", type=int, default=90, help="Soglia similarità via (fuzzy)")
    ap.add_argument("--workers", type=int, default=max(1, os.cpu_count() // 2))
    ap.add_argument("--chunksize", type=int, default=200_000)
    ap.add_argument("--lat0-col", default=defaults["--lat0-col"], help="Colonna LAT di default (fallback geometrico)")
    ap.add_argument("--lon0-col", default=defaults["--lon0-col"], help="Colonna LON di default (fallback geometrico)")
    args = ap.parse_args(args)

    logger.info("Loading address index...")
    rubrica = pd.read_csv(args.rubrica, dtype=str)
    idx = AddressIndex(rubrica, comune_col="comune", cap_col="CAP" if "CAP" in rubrica.columns else "cap",
                       via_col="strada_comunale", civico_col="civico_num", civico_sub_col="civico_sub", lat_col="ycoord", lon_col="xcoord")
    logger.info(f"Loading database with layer {args.layer}...")
    df_all = read_any(args.inp,sep=';', layer=args.layer)
    df_all = prepare_input_df(df_all, addr_col=args.addr_col, cap_col=args.cap_col,
                              comune_default=args.comune, comune_col=args.comune_col,
                              civico_col=args.civico_col, lat0_col = args.lat0_col, lon0_col=args.lon0_col)

    n = len(df_all)
    starts = list(range(0, n, args.chunksize))
    worker = partial(process_chunk, idx=idx, id_col=args.id_col, sim_threshold=args.sim_threshold)

    logger.info(f"Starting geocoding with {args.workers} workers...")
    results = []
    if args.workers > 1 and len(starts) > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            futs = [ex.submit(worker, df_all.iloc[s:min(s+args.chunksize, n)].copy()) for s in starts]
            for f in tqdm(as_completed(futs), total=len(futs), desc="Geocoding (local, no CAP)"):
                results.append(f.result())
    else:
        for s in tqdm(starts, desc="Geocoding (local, no CAP)"):
            results.append(worker(df_all.iloc[s:min(s+args.chunksize, n)].copy()))

    if len(results) == 1:
        out_df = results[0]
    else:
        out_df = pd.concat(results, ignore_index=True)

    geom = gpd.points_from_xy(out_df["lon"], out_df["lat"])
    out_gdf = gpd.GeoDataFrame(out_df, geometry=geom, crs="EPSG:4326")
    # filter out rows without geometry
    out_gdf = out_gdf[~out_gdf["geometry"].isna()]
    write_any(out_gdf, args.outp, layer=args.layer)

    vc = out_df["status"].value_counts(dropna=False)
    logger.info(f"\n=== REPORT GEOCODING LOCALE {args.layer} ===\n {vc.to_string()}")
    if "similarity_score" in out_df.columns:
        logger.info(f"\nScore (descr.): \n {out_df["similarity_score"].describe(percentiles=[0.5,0.8,0.9,0.95,0.99]).to_string()}")


if __name__ == "__main__":
    # #rubrica = r'C:\Users\Mocci\PycharmProjects\GeneralPurpose\siatel_pipeline\civici_WGS84_EPSG4326_csv_202211.csv'
    # # input = r'C:\Users\Mocci\PycharmProjects\GeneralPurpose\siatel_pipeline\all.parquet'
    # # output = r'C:\Users\Mocci\PycharmProjects\GeneralPurpose\siatel_pipeline\all_geocoded_local.parquet'
    # rubrica = r'C:\Users\Mocci\PycharmProjects\GeneralPurpose\siatel_pipeline\addresses_ped.csv'
    # # #input = r'C:\Users\Mocci\Documents\QgisProjects\PED_TO\data\regpie-Sicee_v_t_export_bo_ace_18894-all.csv'
    # # # #input = r'C:\Users\Mocci\PycharmProjects\GeneralPurpose\siatel_pipeline\epc_ped.csv'
    # # # output = r'C:\Users\Mocci\PycharmProjects\GeneralPurpose\siatel_pipeline\provaepc.parquet'
    # # #import sys
    # input = r"C:\Users\Mocci\PycharmProjects\GeneralPurpose\to_building_energy\data\raw\test.gpkg"
    # output = r"C:\Users\Mocci\PycharmProjects\GeneralPurpose\to_building_energy\data/raw/prova.gpkg"
    # main(['--rubrica', rubrica,
    #       '--in', input,
    #       '--out', output,
    #       '--layer', 'ace',
    #       '--addr-col', 'desc_indirizzo',
    #       '--comune-col', 'desc_comune',
    #         '--civico-col', 'num_civico',
    #       '--lat0-col', 'coord_n',  # <-- se esistono
    #       '--lon0-col', 'coord_e'  # <-- se esistono
    # ])
    #
    main()
