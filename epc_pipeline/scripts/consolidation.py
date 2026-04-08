#!/usr/bin/env python3
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

import fiona
import geopandas as gpd
import pandas as pd
from loguru import logger

NULL_STRINGS = {"nan", "null", "none", ""}


def parse_args():
    p = argparse.ArgumentParser(description="Consolidate a GeoPackage using GeoPandas only, with special FK mapping for CIT.")
    p.add_argument("--in-gpkg", required=True)
    p.add_argument("--out-gpkg", required=True)
    p.add_argument("--out-spatial-orphans", required=True)
    p.add_argument("--out-table-orphans", required=True)
    p.add_argument("--report", required=True)

    p.add_argument("--id-col", default="id_certificato")
    p.add_argument("--cit-layer", default="cit")
    p.add_argument("--cit-fk", default="codice_impianto")

    p.add_argument("--ape-im-layer", default="ape_im")
    p.add_argument("--ape-im-fk", default="codice_impianto")
    p.add_argument("--ape-im-id", default="id_certificato")

    return p.parse_args()


def is_metadata_layer(name: str) -> bool:
    return name.lower().endswith("_metadata")


def normalize_str_series(s: pd.Series) -> pd.Series:
    s2 = s.astype("string").str.strip()
    mask = s2.isna() | s2.str.lower().isin(NULL_STRINGS)
    return s2.mask(mask, pd.NA)


def layer_has_real_geometry(gdf: gpd.GeoDataFrame) -> bool:
    return ("geometry" in gdf.columns) and (gdf.geometry is not None) and (gdf.geometry.notna().any())


def ensure_parent(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)


def safe_unlink(p: Path) -> None:
    if p.exists():
        p.unlink()


def write_layer(gdf: gpd.GeoDataFrame, gpkg_path: Path, layer_name: str) -> None:
    # NB: per tabelle (no geometry) a volte può fallire a seconda dello stack; qui rimaniamo GeoPandas-only.
    gdf.to_file(gpkg_path, layer=layer_name, driver="GPKG")


def collect_unique_ids(gdf: gpd.GeoDataFrame, id_col: str) -> Set[str]:
    if id_col not in gdf.columns:
        return set()
    ids = normalize_str_series(gdf[id_col]).dropna().astype(str).unique().tolist()
    return set(ids)


def pick_master(spatial_layers: Dict[str, gpd.GeoDataFrame], id_col: str) -> Tuple[str, Dict[str, Dict]]:
    stats = {}
    best = None
    best_unique = -1
    best_non_null = -1

    for name, gdf in spatial_layers.items():
        if id_col not in gdf.columns:
            non_null = 0
            unique = 0
        else:
            s = normalize_str_series(gdf[id_col])
            non_null = int(s.notna().sum())
            unique = int(s.dropna().astype(str).nunique())

        stats[name] = {"rows": int(len(gdf)), "non_null": non_null, "unique": unique}

        # pick by max unique; tie-break by non_null
        if (unique > best_unique) or (unique == best_unique and non_null > best_non_null):
            best = name
            best_unique = unique
            best_non_null = non_null

    if best is None:
        raise RuntimeError("Cannot pick a master layer (no spatial layers available).")

    return best, stats


def build_fk_map_from_ape_im(
    ape_im_gdf: gpd.GeoDataFrame,
    fk_col: str,
    id_col: str,
) -> Tuple[Dict[str, Set[str]], Dict[str, int]]:
    """
    Returns:
      fk_to_ids: dict codice_impianto -> set(id_certificato)
      stats: counts about mapping quality
    """
    stats = {"rows": int(len(ape_im_gdf)), "rows_used": 0, "fk_null": 0, "id_null": 0, "pairs": 0, "ambiguous_fk": 0}

    if fk_col not in ape_im_gdf.columns or id_col not in ape_im_gdf.columns:
        return {}, {**stats, "error": 1}

    fk_s = normalize_str_series(ape_im_gdf[fk_col])
    id_s = normalize_str_series(ape_im_gdf[id_col])

    mask_fk = fk_s.notna()
    mask_id = id_s.notna()

    stats["fk_null"] = int((~mask_fk).sum())
    stats["id_null"] = int((~mask_id).sum())

    use = mask_fk & mask_id
    stats["rows_used"] = int(use.sum())

    fk_to_ids: Dict[str, Set[str]] = {}
    for fk, idv in zip(fk_s[use].astype(str), id_s[use].astype(str)):
        fk_to_ids.setdefault(fk, set()).add(idv)
        stats["pairs"] += 1

    stats["ambiguous_fk"] = int(sum(1 for fk, ids in fk_to_ids.items() if len(ids) > 1))
    return fk_to_ids, stats


def filter_cit_by_master_ids(
    cit_df: pd.DataFrame,
    cit_fk: str,
    fk_to_ids: Dict[str, Set[str]],
    master_ids: Set[str],
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, int]]:
    """
    Keep cit rows whose codice_impianto maps to at least one id in master_ids.
    Orphans are rows with:
      - fk null-like
      - fk not in fk_to_ids (unmapped)
      - fk maps only to ids outside master
    """
    stats = {"rows": int(len(cit_df)), "fk_missing_col": 0, "fk_null": 0, "fk_unmapped": 0, "fk_mapped_outside_master": 0, "kept": 0, "orphans": 0}

    if cit_fk not in cit_df.columns:
        stats["fk_missing_col"] = 1
        # se manca FK, non posso collegare: tutto orphan
        return cit_df.iloc[0:0].copy(), cit_df.copy(), {**stats, "orphans": int(len(cit_df))}

    fk_s = normalize_str_series(cit_df[cit_fk])
    stats["fk_null"] = int(fk_s.isna().sum())

    keep_mask = []
    unmapped = 0
    outside = 0

    for fk in fk_s:
        if pd.isna(fk):
            keep_mask.append(False)
            continue
        fk_str = str(fk)
        ids = fk_to_ids.get(fk_str)
        if not ids:
            unmapped += 1
            keep_mask.append(False)
            continue
        # keep if any id in master
        if any(i in master_ids for i in ids):
            keep_mask.append(True)
        else:
            outside += 1
            keep_mask.append(False)

    stats["fk_unmapped"] = int(unmapped)
    stats["fk_mapped_outside_master"] = int(outside)

    keep_mask = pd.Series(keep_mask, index=cit_df.index)
    kept = cit_df.loc[keep_mask].copy()
    orph = cit_df.loc[~keep_mask].copy()
    stats["kept"] = int(len(kept))
    stats["orphans"] = int(len(orph))
    return kept, orph, stats


def main():
    args = parse_args()

    in_gpkg = Path(args.in_gpkg)
    out_gpkg = Path(args.out_gpkg)
    out_spatial_orphans = Path(args.out_spatial_orphans)
    out_table_orphans = Path(args.out_table_orphans)
    report_path = Path(args.report)

    for p in (out_gpkg, out_spatial_orphans, out_table_orphans, report_path):
        ensure_parent(p)
        safe_unlink(p)

    layers_all = [l for l in fiona.listlayers(in_gpkg) if not is_metadata_layer(l)]

    # load all layers into either spatial or table dict
    spatial_layers: Dict[str, gpd.GeoDataFrame] = {}
    table_layers: Dict[str, pd.DataFrame] = {}

    for lyr in layers_all:
        try:
            gdf = gpd.read_file(in_gpkg, layer=lyr)
        except Exception as e:
            logger.warning(f"Skip '{lyr}': read error: {e}")
            continue

        if layer_has_real_geometry(gdf):
            spatial_layers[lyr] = gdf
        else:
            df = pd.DataFrame(gdf.drop(columns=["geometry"], errors="ignore"))
            table_layers[lyr] = df

    if not spatial_layers:
        raise RuntimeError("No spatial layers found (excluding metadata).")

    # --- master selection based on id_certificato among spatial layers ---
    master_layer, spatial_stats = pick_master(spatial_layers, args.id_col)
    master_ids = collect_unique_ids(spatial_layers[master_layer], args.id_col)

    # --- build FK map from ape_im (can be spatial or table) ---
    ape_im_df: Optional[pd.DataFrame] = None
    if args.ape_im_layer in spatial_layers:
        ape_im_df = pd.DataFrame(spatial_layers[args.ape_im_layer].drop(columns=["geometry"], errors="ignore"))
    elif args.ape_im_layer in table_layers:
        ape_im_df = table_layers[args.ape_im_layer]
    else:
        ape_im_df = None

    fk_to_ids = {}
    map_stats = {"error": 1}
    if ape_im_df is not None:
        ape_im_gdf = gpd.GeoDataFrame(ape_im_df, geometry=None)
        fk_to_ids, map_stats = build_fk_map_from_ape_im(
            ape_im_gdf, fk_col=args.ape_im_fk, id_col=args.ape_im_id
        )

    logger.info(f"MASTER: {master_layer} | master_ids={len(master_ids)}")
    logger.info(f"APE_IM mapping: fk_to_ids={len(fk_to_ids)} | ambiguous_fk={map_stats.get('ambiguous_fk')}")

    # --- write master layer to consolidated ---
    write_layer(spatial_layers[master_layer], out_gpkg, master_layer)

    # --- spatial consolidation ---
    spatial_results = {}

    for lyr, gdf in spatial_layers.items():
        if lyr == master_layer:
            continue

        if args.id_col not in gdf.columns:
            kept = gdf.iloc[0:0].copy()
            orph = gdf.copy()
        else:
            ids = normalize_str_series(gdf[args.id_col])
            mask_in = ids.notna() & ids.astype(str).isin(master_ids)
            kept = gdf.loc[mask_in].copy()
            orph = gdf.loc[~mask_in].copy()

        spatial_results[lyr] = {"kept": int(len(kept)), "orphans": int(len(orph))}

        if len(kept) > 0:
            write_layer(kept, out_gpkg, lyr)
        if len(orph) > 0:
            write_layer(orph, out_spatial_orphans, lyr)

    # --- table consolidation (special-case CIT) ---
    table_results = {}
    cit_stats = None

    for lyr, df in table_layers.items():
        # Special case: CIT uses codice_impianto -> map via ape_im to master_ids
        if lyr == args.cit_layer:
            kept_df, orph_df, cit_stats = filter_cit_by_master_ids(
                cit_df=df, cit_fk=args.cit_fk, fk_to_ids=fk_to_ids, master_ids=master_ids
            )
            table_results[lyr] = {"kept": int(len(kept_df)), "orphans": int(len(orph_df))}
        else:
            if args.id_col not in df.columns:
                kept_df = df.iloc[0:0].copy()
                orph_df = df.copy()
            else:
                ids = normalize_str_series(df[args.id_col])
                mask_in = ids.notna() & ids.astype(str).isin(master_ids)
                kept_df = df.loc[mask_in].copy()
                orph_df = df.loc[~mask_in].copy()

            table_results[lyr] = {"kept": int(len(kept_df)), "orphans": int(len(orph_df))}

        # write kept to consolidated
        if len(kept_df) > 0:
            kept_gdf = gpd.GeoDataFrame(kept_df, geometry=None)
            write_layer(kept_gdf, out_gpkg, lyr)

        # write orphans to table-orphans gpkg
        if len(orph_df) > 0:
            orph_gdf = gpd.GeoDataFrame(orph_df, geometry=None)
            write_layer(orph_gdf, out_table_orphans, lyr)

    # --- report ---
    lines = []
    lines.append("GPKG CONSOLIDATION REPORT (GeoPandas-only)")
    lines.append(f"Input: {in_gpkg}")
    lines.append(f"Consolidated: {out_gpkg}")
    lines.append(f"Spatial orphans: {out_spatial_orphans}")
    lines.append(f"Table orphans: {out_table_orphans}")
    lines.append("")
    lines.append(f"Master selection id_col: {args.id_col}")
    lines.append(f"Master layer: {master_layer}")
    lines.append(f"Master unique ids: {len(master_ids)}")
    lines.append("")
    lines.append("Spatial layer stats (rows / non_null / unique):")
    for lyr, st in sorted(spatial_stats.items()):
        lines.append(f"  - {lyr}: rows={st['rows']} non_null={st['non_null']} unique={st['unique']}")
    lines.append("")
    lines.append("Spatial consolidation results:")
    for lyr, st in sorted(spatial_results.items()):
        lines.append(f"  - {lyr}: kept={st['kept']} orphans={st['orphans']}")
    lines.append("")
    lines.append("Table consolidation results:")
    for lyr, st in sorted(table_results.items()):
        lines.append(f"  - {lyr}: kept={st['kept']} orphans={st['orphans']}")

    lines.append("")
    lines.append("CIT special mapping (codice_impianto -> id_certificato via ape_im):")
    lines.append(f"  cit_layer={args.cit_layer} cit_fk={args.cit_fk}")
    lines.append(f"  ape_im_layer={args.ape_im_layer} ape_im_fk={args.ape_im_fk} ape_im_id={args.ape_im_id}")
    if map_stats.get("error"):
        lines.append("  [WARN] ape_im mapping not available (missing layer/columns). CIT will be mostly orphan.")
    else:
        lines.append(f"  mapping entries (unique FK): {len(fk_to_ids)}")
        lines.append(f"  ambiguous FK (FK -> multiple ids): {map_stats.get('ambiguous_fk', 0)}")
        lines.append(f"  ape_im rows_used: {map_stats.get('rows_used', 0)} (rows={map_stats.get('rows', 0)})")
    if cit_stats:
        lines.append(f"  CIT rows={cit_stats['rows']} kept={cit_stats['kept']} orphans={cit_stats['orphans']}")
        lines.append(f"    fk_null={cit_stats['fk_null']} fk_unmapped={cit_stats['fk_unmapped']} fk_mapped_outside_master={cit_stats['fk_mapped_outside_master']}")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"Report written: {report_path}")


if __name__ == "__main__":
    main()
