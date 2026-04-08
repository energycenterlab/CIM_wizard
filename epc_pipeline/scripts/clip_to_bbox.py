#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import sys
import sqlite3

import fiona
import geopandas as gpd
from shapely.geometry import box
from shapely.ops import unary_union
import pandas as pd
from loguru import logger

ROOT = Path(__file__).parent.parent

def parse_args():
    defaults = {
        '--in-gpkg':r'C:\Users\Mocci\PycharmProjects\GeneralPurpose\to_building_energy\data\raw\clean_geocoded_data.gpkg',
        '--out-gpkg':r'C:\Users\Mocci\PycharmProjects\GeneralPurpose\to_building_energy\data\raw\test.gpkg',
    }
    p = argparse.ArgumentParser(
        description="Clip all spatial layers in a GeoPackage using bbox (if provided) else AOI. Non-spatial tables are skipped."
    )
    p.add_argument("--in-gpkg",default= defaults['--in-gpkg'], help="Input GeoPackage path")
    p.add_argument("--out-gpkg", default= defaults['--out-gpkg'], help="Output GeoPackage path")

    # bbox optional: 4 values
    p.add_argument(
        "--bbox",
        nargs=4,
        type=float,
        default=(7.6480207258492543, 45.0566249091594528, 7.6647201380294510, 45.0710368613256307),
        metavar=("XMIN", "YMIN", "XMAX", "YMAX"),
        help="Bounding box as 4 numbers: xmin ymin xmax ymax (if provided, has priority over AOI)",
    )

    p.add_argument(
        "--id-col",
        default="id_certificato",
        help="Name of the certified id column used to keep consistency across layers (e.g. id_certificato)",
    )
    return p.parse_args()


def load_aoi_geometry(aoi_path: str, aoi_layer: str):
    aoi = gpd.read_file(aoi_path, layer=aoi_layer) if aoi_layer else gpd.read_file(aoi_path)
    if aoi.empty:
        raise ValueError("AOI is empty.")
    aoi = aoi[aoi.geometry.notna()].copy()
    geom = unary_union(aoi.geometry)
    return geom, aoi.crs

def write_table(conn: sqlite3.Connection, name: str, df: pd.DataFrame):
    df.to_sql(name, conn, if_exists="replace", index=False)

def write_layer_gdf(gpkg_path: str, layer: str, gdf: gpd.GeoDataFrame):
    gdf.to_file(gpkg_path, layer=layer, driver="GPKG")

def build_clip_geometry(args):
    # bbox wins
    if args.bbox is not None:
        xmin, ymin, xmax, ymax = args.bbox
        geom = box(xmin, ymin, xmax, ymax)
        logger.info(f"[INFO] Using bbox clip: {args.bbox}")
        return geom

    # else AOI
    if not args.aoi_path:
        raise ValueError("Neither --bbox nor --aoi-path provided.")
    geom, crs = load_aoi_geometry(args.aoi_path, args.aoi_layer)
    logger.info(f"Using AOI clip from {args.aoi_path} layer={args.aoi_layer or 'default'}")
    return geom, crs


def main():
    args = parse_args()

    in_path = Path(args.in_gpkg).parent
    in_path.parent.mkdir(parents=True, exist_ok=True)
    # Clip geometry + CRS
    try:
        clip_geom = build_clip_geometry(args)
    except Exception as e:
        logger.error(f"[ERROR] Cannot build clip geometry: {e}")
        return 2

    # Decide work CRS #EPSG:4326
    work_crs = "EPSG:4326"
    if not work_crs:
        logger.error("[ERROR] Cannot determine work CRS. Provide --work-crs.")
        return 2
    clip_crs = work_crs # implicitly
    # Transform clip geometry to work CRS
    try:
        clip_geom_work = gpd.GeoSeries([clip_geom], crs=clip_crs).to_crs(work_crs).iloc[0]
    except Exception as e:
        logger.error(f"[ERROR] Cannot reproject clip geometry to work CRS ({work_crs}): {e}")
        return 2

    # Iterate layers
    in_gpkg_path = ROOT / Path(args.in_gpkg)
    try:
        layers = fiona.listlayers(in_gpkg_path)
    except Exception as e:
        logger.error(f"[ERROR] Cannot list layers in {in_gpkg_path}: {e}")
        return 2

    wrote_any = False
    # Write to output gpkg, keep same layer name
    out_gpkg_path = ROOT / Path(args.out_gpkg)
    # Processing gis layer
    ids_list = []
    for layer_gis in ["ape_dg",'ace']:
        try:
            gdf = gpd.read_file(in_gpkg_path, layer=layer_gis)
        except Exception as e:
            logger.info(f"[SKIP] Layer '{layer_gis}': read error: {e}")

        gdf = gdf[gdf.geometry.notna()].copy()
        if gdf.empty:
            logger.info(f"[OK] Layer '{layer_gis}': empty after dropping null geometries.")
        # CRS handling
        if gdf.crs is None:
            # se manca CRS, assumiamo work_crs (meglio che crashare)
            logger.warning(f"Layer '{layer_gis}': CRS missing; assuming {work_crs}.")
            gdf = gdf.set_crs(work_crs)
        else:
            try:
                gdf = gdf.to_crs(work_crs)
            except Exception as e:
                logger.info(f"[SKIP] Layer '{layer_gis}': cannot reproject to {work_crs}: {e}")

        # Clip geometry and confidence
        try:
            clipped = gpd.clip(gdf, clip_geom_work)
            clipped = clipped[(clipped.confidence == 'alta')&(clipped.status == 'matched')].copy()
        except Exception as e:
            logger.info(f"[SKIP] Layer '{layer_gis}': clip error: {e}")

        if clipped.empty:
            logger.info(f"[OK] Layer '{layer_gis}': no features intersect clip area.")
        ids_list=ids_list+clipped.id_certificato.tolist()

        try:
            clipped.to_file(out_gpkg_path, layer=layer_gis, driver="GPKG")
            wrote_any = True
            logger.info(f"[OK] Layer '{layer_gis}': wrote {len(clipped)} features.")
        except Exception as e:
            logger.error(f"Layer '{layer_gis}': write error: {e}")
        layers.remove(layer_gis)

    conn_out = sqlite3.connect(out_gpkg_path)

    # processing other layers

    #PROCESSING APE IMP LAYER
    # processing ape_im_codes
    ape_im_codes = set()
    if "ape_im_clean" in layers:
        ape_im_df = gpd.read_file(in_gpkg_path, layer="ape_im_clean")
        clipped = ape_im_df[ape_im_df[args.id_col].isin(ids_list)].copy()
        if "codice_impianto_cit" in ape_im_df.columns:
            ape_im_codes = set(
                clipped["codice_impianto_cit"].dropna().astype(int)
            )
        write_table(conn_out, "ape_im_clean", clipped)
        logger.info(f"[OK] Layer 'ape_im_clean': wrote {len(clipped)} features.")


    layers.remove("ape_im_clean")

    for lyr in layers:
        try:
            gdf = gpd.GeoDataFrame(gpd.read_file(in_gpkg_path, layer=lyr))
        except Exception as e:
            logger.info(f"[SKIP] Layer '{lyr}': read error: {e}")
            continue
        try:
            geom = gdf.geometry
            is_spatial = isinstance(gdf, gpd.GeoDataFrame) and geom is not None and geom.name in gdf.columns
        except AttributeError as e:
            is_spatial = False

        if "cit" in lyr:
            gdf["codice_impianto"] = gdf["codice_impianto"].astype(int)
            in_mask = gdf["codice_impianto"].isin(ape_im_codes)
            clipped = gdf.loc[in_mask].copy()
            write_table(conn_out, lyr, clipped)
        else:
            clipped = gdf[gdf[args.id_col].isin(ids_list)].copy()
            if is_spatial:
                write_layer_gdf(out_gpkg_path, lyr, clipped)
            else:
                write_table(conn_out, lyr, clipped)
        logger.info(f"[OK] Layer '{lyr}': wrote {len(clipped)} features.")

    if not wrote_any:
        # output vuoto “segnaposto” (evita che la pipeline fallisca)
        open(out_gpkg_path, "wb").close()
        logger.warning("No spatial layers produced any output; wrote empty file placeholder.")

    return 0


if __name__ == "__main__":
    main()
