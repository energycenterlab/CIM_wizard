#!/usr/bin/env python3
import argparse
from pathlib import Path
import os

import fiona
import geopandas as gpd
from loguru import logger



def main():
    p = argparse.ArgumentParser(description="Merge multiple per-layer GeoPackages into a single GeoPackage.")
    p.add_argument("--out-gpkg")
    p.add_argument("--in-gpkgs", nargs="+")
    args = p.parse_args()

    out_gpkg = Path(args.out_gpkg)
    out_gpkg.parent.mkdir(parents=True, exist_ok=True)

    if out_gpkg.exists():
        out_gpkg.unlink()

    written = set()
    logger.info(args.in_gpkgs)
    for in_path_str in args.in_gpkgs:
        in_path = Path(in_path_str)
        if not in_path.exists():
            logger.warning(f"Missing input gpkg: {in_path}")
            continue

        try:
            layers = list(fiona.listlayers(in_path))
        except Exception as e:
            logger.error(f"Cannot list layers in {in_path}: {e}")
            continue

        for lyr in layers:
            if lyr in written:
                # non dovrebbe succedere (ogni per-layer ha layer unici),
                # ma se succede, evitiamo collisione.
                new_name = f"{lyr}__dup"
                logger.warning(f"Layer name collision '{lyr}', writing as '{new_name}'")
                out_layer = new_name
            else:
                out_layer = lyr

            try:
                gdf = gpd.read_file(in_path, layer=lyr)
            except Exception as e:
                logger.error(f"Read error {in_path}:{lyr}: {e}")
                continue

            try:
                if isinstance(gdf, gpd.GeoDataFrame):
                    gdf.to_file(out_gpkg, layer=out_layer, driver="GPKG")
                else:
                    gpd.GeoDataFrame(gdf).to_file(out_gpkg, layer=out_layer, driver="GPKG")

                written.add(out_layer)
                logger.info(f"Wrote layer '{out_layer}' from {in_path.name}")
            except Exception as e:
                logger.error(f"Write error for layer '{out_layer}': {e}")

    if not written:
        out_gpkg.write_bytes(b"")
        logger.warning("No layers written. Created empty placeholder output.")


if __name__ == "__main__":
    main()
