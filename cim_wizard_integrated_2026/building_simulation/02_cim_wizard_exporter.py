"""
02 — Export a CIM Wizard scenario to CESAR-P input files.

What this script does
---------------------
  Reads building geometry and properties from the CIM Wizard PostGIS database
  for a given (project_id, scenario_id) and writes the two CSV files that
  CESAR-P requires:
    • SiteVertices.csv   — building footprint polygon vertices
    • BuildingInformation.csv — per-building attributes

Usage
-----
    # Set env vars (same as CIM Wizard backend)
    export DATABASE_URL="postgresql://user:pass@localhost:5433/cim_wizard_integrated"

    python 02_cim_wizard_exporter.py \
        --project_id  my_project \
        --scenario_id scenario_001 \
        --output_dir  ./data/exported/my_project_scenario_001
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import mapping
from sqlalchemy import create_engine, text


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def _get_engine(database_url: str | None = None):
    import os
    url = database_url or os.environ["DATABASE_URL"]
    return create_engine(url)


def load_buildings(engine, project_id: str, scenario_id: str) -> gpd.GeoDataFrame:
    """
    Load building geometries and properties from CIM Wizard for one scenario.

    Joins cim_vector buildings with calculated properties from
    cim_wizard_building_properties.
    """
    sql = text("""
        SELECT
            b.id                            AS egid,
            b.geometry                      AS geom,
            bp.building_height              AS height,
            bp.building_n_floors            AS floors_above_ground,
            bp.building_construction_year   AS year_of_construction,
            bp.building_type                AS raw_building_type,
            bp.building_residential_filter  AS is_residential,
            bp.building_area                AS gross_floor_area_m2
        FROM cim_vector.buildings b
        JOIN cim_vector.cim_wizard_building_properties bp
            ON bp.building_id = b.id
        JOIN cim_vector.scenarios s
            ON s.id = bp.scenario_id
        JOIN cim_vector.projects p
            ON p.id = s.project_id
        WHERE p.project_id = :project_id
          AND s.scenario_id = :scenario_id
          AND b.geometry IS NOT NULL
          AND bp.building_height IS NOT NULL
    """)
    gdf = gpd.read_postgis(
        sql,
        engine,
        geom_col="geom",
        params={"project_id": project_id, "scenario_id": scenario_id},
    )
    return gdf


# ---------------------------------------------------------------------------
# Building type mapping  (CIM Wizard → SIA 2024)
# ---------------------------------------------------------------------------
# Adapt this mapping to match your building_type values.
_BUILDING_TYPE_MAP: dict[str, str] = {
    # CIM Wizard value      : SIA 2024 type
    "residential_sfh"       : "SFH",
    "residential_mfh"       : "MFH",
    "residential"           : "MFH",    # default residential → MFH
    "sfh"                   : "SFH",
    "mfh"                   : "MFH",
    "office"                : "OFFICE",
    "commercial"            : "SHOP",
    "retail"                : "SHOP",
    "school"                : "SCHOOL",
    "education"             : "SCHOOL",
    "hospital"              : "HOSPITAL",
    "industrial"            : "INDUSTRY",
    "sports"                : "SPORTS",
    "unknown"               : "MFH",    # safe fallback
}

SIA_TYPES = {
    "SFH": "Single-family house",
    "MFH": "Multi-family house",
    "OFFICE": "Office building",
    "SCHOOL": "School",
    "SHOP": "Retail / shop",
    "RESTAURANT": "Restaurant / canteen",
    "HOSPITAL": "Hospital",
    "INDUSTRY": "Industrial / warehouse",
    "SPORTS": "Sports hall",
    "INDOOR_SWIMMING": "Indoor swimming pool",
}


def map_building_type(raw_type: str | None, is_residential: bool | None) -> str:
    if raw_type:
        key = str(raw_type).lower().strip()
        if key in _BUILDING_TYPE_MAP:
            return _BUILDING_TYPE_MAP[key]
    if is_residential:
        return "MFH"
    return "MFH"


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def extract_vertices(gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Explode building polygons to a flat vertex table (CESAR-P SiteVertices format).

    Returns
    -------
    pd.DataFrame with columns: TARGET_FID, SHAPE_X, SHAPE_Y
    """
    rows = []
    for _, row in gdf.iterrows():
        geom = row["geom"]
        if geom is None:
            continue
        # Take the exterior ring of the (first) polygon
        if geom.geom_type == "MultiPolygon":
            geom = max(geom.geoms, key=lambda g: g.area)
        coords = list(geom.exterior.coords)[:-1]  # drop closing duplicate
        for x, y in coords:
            rows.append({"TARGET_FID": row["egid"], "SHAPE_X": round(x, 2), "SHAPE_Y": round(y, 2)})
    return pd.DataFrame(rows)


def find_neighbours(gdf: gpd.GeoDataFrame, buffer_m: float = 30.0) -> dict[int, list[int]]:
    """
    For each building, find neighbours within buffer_m metres.

    Returns
    -------
    dict mapping egid → list of neighbour egids
    """
    neighbours: dict[int, list[int]] = {}
    buffered = gdf.copy()
    buffered["buffer"] = buffered["geom"].buffer(buffer_m)

    for _, row in gdf.iterrows():
        fid = row["egid"]
        buf = buffered.loc[buffered["egid"] == fid, "buffer"].iloc[0]
        nearby = gdf[
            (gdf["egid"] != fid) & gdf["geom"].intersects(buf)
        ]["egid"].tolist()
        neighbours[fid] = nearby
    return neighbours


# ---------------------------------------------------------------------------
# Main export
# ---------------------------------------------------------------------------

def export_to_cesarp(
    project_id: str,
    scenario_id: str,
    output_dir: Path,
    database_url: str | None = None,
) -> tuple[Path, Path]:
    """
    Export CIM Wizard scenario buildings to CESAR-P input CSVs.

    Parameters
    ----------
    project_id : str
    scenario_id : str
    output_dir : Path
        Destination folder; created if missing.
    database_url : str, optional
        Falls back to DATABASE_URL env var.

    Returns
    -------
    (site_vertices_path, building_info_path)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    engine = _get_engine(database_url)

    print(f"Loading buildings for project={project_id}, scenario={scenario_id} ...")
    gdf = load_buildings(engine, project_id, scenario_id)
    print(f"  Loaded {len(gdf)} buildings.")

    if gdf.empty:
        raise ValueError(
            f"No buildings found for project={project_id!r}, scenario={scenario_id!r}. "
            "Run the CIM Wizard pipeline first."
        )

    # --- SiteVertices.csv -------------------------------------------------
    vertices_df = extract_vertices(gdf)
    site_vertices_path = output_dir / "SiteVertices.csv"
    vertices_df.to_csv(site_vertices_path, index=False)
    print(f"  SiteVertices → {site_vertices_path}  ({len(vertices_df)} rows)")

    # --- BuildingInformation.csv ------------------------------------------
    neighbour_map = find_neighbours(gdf, buffer_m=30.0)

    info_rows = []
    for _, row in gdf.iterrows():
        fid = row["egid"]
        sia_type = map_building_type(row.get("raw_building_type"), row.get("is_residential"))
        nbs = neighbour_map.get(fid, [])
        info_rows.append({
            "EGID": fid,
            "HEIGHT": round(float(row["height"]), 2) if row["height"] else 6.0,
            "FLOORS_ABOVE_GROUND": int(row["floors_above_ground"]) if row["floors_above_ground"] else 2,
            "YEAR_OF_CONSTRUCTION": int(row["year_of_construction"]) if row["year_of_construction"] else 1980,
            "SIA_BLDG_TYPE": sia_type,
            "GROSS_FLOOR_AREA_M2": round(float(row["gross_floor_area_m2"]), 1) if row["gross_floor_area_m2"] else None,
            "NEIGHBOURS": ",".join(str(n) for n in nbs),
        })

    info_df = pd.DataFrame(info_rows)
    bldg_info_path = output_dir / "BuildingInformation.csv"
    info_df.to_csv(bldg_info_path, index=False)
    print(f"  BuildingInformation → {bldg_info_path}  ({len(info_df)} buildings)")

    # --- Summary stats -----------------------------------------------------
    print("\nBuilding type distribution:")
    print(info_df["SIA_BLDG_TYPE"].value_counts().to_string())
    print(f"\nConstruction year range: {info_df['YEAR_OF_CONSTRUCTION'].min()} – {info_df['YEAR_OF_CONSTRUCTION'].max()}")
    print(f"Height range: {info_df['HEIGHT'].min():.1f} – {info_df['HEIGHT'].max():.1f} m")

    return site_vertices_path, bldg_info_path


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export CIM Wizard scenario to CESAR-P inputs.")
    parser.add_argument("--project_id",  required=True)
    parser.add_argument("--scenario_id", required=True)
    parser.add_argument("--output_dir",  default="./data/exported")
    parser.add_argument("--database_url", default=None)
    args = parser.parse_args()

    site_v, bldg_i = export_to_cesarp(
        project_id=args.project_id,
        scenario_id=args.scenario_id,
        output_dir=Path(args.output_dir),
        database_url=args.database_url,
    )
    print(f"\nExport complete.\n  {site_v}\n  {bldg_i}")
