"""Surfaces of LoD1 buildings, one thermal zone per building.

Each building is one thermal zone: `thermal_zone_id` is the building's `building_id`.
Surfaces are one wall per footprint edge (exterior ring and courtyards), one roof and
one ground floor per footprint part. Geometry is built in EPSG:32632 and returned in
EPSG:4326 with z = absolute elevation in metres.

Winding follows the right-hand rule so every polygon's normal points out of the zone:
walls outwards, roof up, floor down.
"""

import uuid
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
import yaml

COMPUTE_CONFIG_PATH = Path(__file__).parents[1] / "config" / "compute.yaml"
METRIC_CRS = "EPSG:32632"
STORAGE_CRS = "EPSG:4326"
SURFACE_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "cim_wizard/surface")
MIN_EDGE_LENGTH_M = 0.01

U_VALUE_COLUMNS = {"wall": "u_wall", "roof": "u_roof", "floor": "u_floor"}
SURFACE_TYPE_ORDER = {"wall": 0, "roof": 1, "floor": 2}


def _sort_surfaces(surfaces: pd.DataFrame) -> pd.DataFrame:
    return surfaces.sort_values(
        ["building_id", "surface_type", "surface_index"],
        key=lambda column: column.map(SURFACE_TYPE_ORDER) if column.name == "surface_type" else column,
    ).reset_index(drop=True)


def load_compute_profile(
    config_path: Path = COMPUTE_CONFIG_PATH,
    profile: str | None = None,
) -> dict:
    config = yaml.safe_load(Path(config_path).read_text())
    name = profile or config["active_profile"]
    if name not in config["profiles"]:
        raise KeyError(f"Profile '{name}' not in {config_path}; add it under 'profiles'.")
    return config["profiles"][name]


def read_building_footprints(csv_path: str | Path) -> gpd.GeoDataFrame:
    """building_id + footprint from a CSV that stores geometry as WKT in EPSG:4326."""
    footprints = pd.read_csv(csv_path, usecols=["building_id", "geometry"])
    return gpd.GeoDataFrame(
        footprints[["building_id"]],
        geometry=gpd.GeoSeries.from_wkt(footprints["geometry"]),
        crs=STORAGE_CRS,
    )


def _wall_surfaces(parts: gpd.GeoDataFrame) -> pd.DataFrame:
    # normalize: exterior clockwise, holes counter-clockwise, so the outward
    # normal of every edge (dx, dy) is its left-hand side (-dy, dx).
    polygons = shapely.normalize(parts.geometry.values)
    rings, ring_part = shapely.get_rings(polygons, return_index=True)
    coords, coord_ring = shapely.get_coordinates(rings, return_index=True)

    same_ring = coord_ring[:-1] == coord_ring[1:]
    start = coords[:-1][same_ring]
    end = coords[1:][same_ring]
    part_index = ring_part[coord_ring[:-1][same_ring]]

    dx = end[:, 0] - start[:, 0]
    dy = end[:, 1] - start[:, 1]
    length = np.hypot(dx, dy)
    keep = length > MIN_EDGE_LENGTH_M
    start, end, dx, dy, length, part_index = (
        start[keep], end[keep], dx[keep], dy[keep], length[keep], part_index[keep]
    )

    z_bottom = parts["z_ground"].to_numpy()[part_index]
    z_top = parts["z_roof"].to_numpy()[part_index]

    # p0 bottom -> p0 top -> p1 top -> p1 bottom -> close
    quads = np.empty((len(start), 5, 3))
    quads[:, 0] = np.column_stack([start, z_bottom])
    quads[:, 1] = np.column_stack([start, z_top])
    quads[:, 2] = np.column_stack([end, z_top])
    quads[:, 3] = np.column_stack([end, z_bottom])
    quads[:, 4] = quads[:, 0]

    return pd.DataFrame({
        "building_id": parts["building_id"].to_numpy()[part_index],
        "surface_type": "wall",
        "area_m2": length * (z_top - z_bottom),
        "azimuth_deg": np.degrees(np.arctan2(-dy, dx)) % 360,
        "tilt_deg": 90.0,
        "geometry": shapely.polygons(quads),
    })


def _horizontal_surfaces(parts: gpd.GeoDataFrame) -> pd.DataFrame:
    polygons = shapely.normalize(parts.geometry.values)  # clockwise from above = normal down
    building_ids = parts["building_id"].to_numpy()
    area = shapely.area(polygons)

    roofs = pd.DataFrame({
        "building_id": building_ids,
        "surface_type": "roof",
        "area_m2": area,
        "azimuth_deg": np.nan,
        "tilt_deg": 0.0,
        "geometry": shapely.reverse(shapely.force_3d(polygons, parts["z_roof"].to_numpy())),
    })
    floors = pd.DataFrame({
        "building_id": building_ids,
        "surface_type": "floor",
        "area_m2": area,
        "azimuth_deg": np.nan,
        "tilt_deg": 180.0,
        "geometry": shapely.force_3d(polygons, parts["z_ground"].to_numpy()),
    })
    return pd.concat([roofs, floors], ignore_index=True)


def build_surfaces(
    buildings: gpd.GeoDataFrame,
    height_column: str = "building_height_m",
    ground_elevation_column: str = "ground_elevation_m",
) -> gpd.GeoDataFrame:
    """Vectorized surfaces for one chunk of buildings (no per-building Python loop)."""
    # 1. Keep buildings that can be extruded, in metres.
    metric = buildings.to_crs(METRIC_CRS)
    height = pd.to_numeric(metric[height_column], errors="coerce")
    is_polygonal = metric.geometry.geom_type.isin(["Polygon", "MultiPolygon"])
    metric = metric[(height > 0) & is_polygonal & ~metric.geometry.is_empty]

    # TODO: buildings with no published ground elevation are placed at z = 0.
    ground = pd.to_numeric(metric[ground_elevation_column], errors="coerce").fillna(0.0)
    metric = metric.assign(
        z_ground=ground,
        z_roof=ground + pd.to_numeric(metric[height_column], errors="coerce"),
    )

    # 2. One row per footprint part, so multipolygons get a roof/floor per part.
    parts = metric[["building_id", "z_ground", "z_roof", "geometry"]].explode(
        index_parts=False
    ).reset_index(drop=True)

    # 3. Walls, roofs and floors.
    surfaces = pd.concat(
        [_wall_surfaces(parts), _horizontal_surfaces(parts)],
        ignore_index=True,
    )

    # 4. Thermal zone and deterministic surface ids.
    surfaces["thermal_zone_id"] = surfaces["building_id"]
    surfaces["surface_index"] = surfaces.groupby(["building_id", "surface_type"]).cumcount()
    surfaces["surface_id"] = [
        str(uuid.uuid5(SURFACE_NAMESPACE, f"{building_id}|{surface_type}|{index}"))
        for building_id, surface_type, index in zip(
            surfaces["building_id"], surfaces["surface_type"], surfaces["surface_index"]
        )
    ]

    # 5. U-value of the zone's construction for that surface type, if assigned.
    surfaces["u_value"] = np.nan
    surfaces["u_value_method"] = None
    zone_values = metric.set_index("building_id")
    for surface_type, column in U_VALUE_COLUMNS.items():
        if column not in zone_values.columns:
            continue
        is_type = surfaces["surface_type"] == surface_type
        building_ids = surfaces.loc[is_type, "building_id"]
        surfaces.loc[is_type, "u_value"] = building_ids.map(zone_values[column]).to_numpy()
        method_column = f"{column}_method"
        if method_column in zone_values.columns:
            surfaces.loc[is_type, "u_value_method"] = building_ids.map(
                zone_values[method_column]
            ).to_numpy()

    columns = [
        "surface_id", "thermal_zone_id", "building_id", "surface_type", "surface_index",
        "area_m2", "azimuth_deg", "tilt_deg", "u_value", "u_value_method", "geometry",
    ]
    result = gpd.GeoDataFrame(_sort_surfaces(surfaces[columns]), geometry="geometry", crs=METRIC_CRS)
    return result.to_crs(STORAGE_CRS)


def generate_surfaces(
    buildings: gpd.GeoDataFrame,
    n_workers: int = 1,
    chunk_size: int = 1000,
) -> gpd.GeoDataFrame:
    """Split buildings into chunks and build their surfaces on `n_workers` processes.

    A building's surfaces depend on that building only, so any chunking gives the same
    result as one call to build_surfaces.
    """
    chunks = [
        buildings.iloc[start:start + chunk_size]
        for start in range(0, len(buildings), chunk_size)
    ]

    if n_workers <= 1 or len(chunks) <= 1:
        results = [build_surfaces(chunk) for chunk in chunks]
    else:
        with ProcessPoolExecutor(max_workers=n_workers) as pool:
            results = list(pool.map(build_surfaces, chunks))

    return gpd.GeoDataFrame(
        _sort_surfaces(pd.concat(results, ignore_index=True)),
        geometry="geometry",
        crs=STORAGE_CRS,
    )
