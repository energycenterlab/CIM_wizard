#!/usr/bin/env python3
"""
Load DSM raster (TIF) into cim_raster.dsm with tiling.
Usage: python load_dsm.py [tif_path] [--append]
"""
import subprocess
import os
import sys
import argparse

# Default: dsm2.tif in same directory as script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TIF = os.path.join(SCRIPT_DIR, "dsm2.tif")

DB = {
    "host": "localhost",
    "port": "15432",
    "dbname": "cim_wizard_integrated",
    "user": "cim_wizard_user",
    "password": "cim_wizard_password",
}

SCHEMA = "cim_raster"
TABLE = "dsm"
TILE_SIZE = "256x256"  # tile width x height (pixels)
SRID = 4326


def main():
    parser = argparse.ArgumentParser(description="Load DSM TIF into cim_raster.dsm (tiled)")
    parser.add_argument("tif_path", nargs="?", default=DEFAULT_TIF, help=f"Path to TIF file (default: {DEFAULT_TIF})")
    parser.add_argument("-a", "--append", action="store_true", help="Append to existing table (default: create new)")
    args = parser.parse_args()

    tif_path = os.path.abspath(args.tif_path)
    if not os.path.isfile(tif_path):
        sys.exit(f"Error: TIF file not found: {tif_path}")

    # Build raster2pgsql command
    # -c create new table (or -a append)
    # -I create spatial index (GIST)
    # -C add raster constraints
    # -M vacuum analyze after load
    # -F add filename column
    # -t tile size (improves spatial query performance)
    cmd = [
        "raster2pgsql",
        "-a" if args.append else "-c",
        "-I",
        "-C",
        "-M",
        "-F",
        "-t", TILE_SIZE,
        "-s", str(SRID),
        tif_path,
        f"{SCHEMA}.{TABLE}",
    ]

    psql_cmd = [
        "psql",
        "-h", DB["host"],
        "-p", DB["port"],
        "-U", DB["user"],
        "-d", DB["dbname"],
    ]

    env = os.environ.copy()
    if "password" in DB:
        env["PGPASSWORD"] = DB["password"]

    print(f"Loading {tif_path} into {SCHEMA}.{TABLE} (tiles {TILE_SIZE})...")
    print(f"Command: {' '.join(cmd)}")

    p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env)
    p2 = subprocess.Popen(psql_cmd, stdin=p1.stdout, env=env)
    p1.stdout.close()
    ret = p2.wait()

    if ret != 0:
        sys.exit(f"Loading failed with exit code {ret}")

    print(f"Load completed successfully. Data in {SCHEMA}.{TABLE}")


if __name__ == "__main__":
    main()