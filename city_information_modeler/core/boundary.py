"""
Boundary handling: read a boundary GeoJSON, measure it, clip to it, divide it.

``split_into_tiles`` lives here rather than in ``parallel/`` because it is geometry work.
The runner decides how many tiles to ask for; this module knows how to cut them.

Stateless: functions take GeoJSON or frames and return frames or GeoJSON.
"""

import math
from typing import Any, Dict, List, Tuple

import geopandas as gpd
from shapely import union_all
from shapely.geometry import box, mapping, shape

from city_information_modeler.core.geometry import GEODETIC_EPSG


def to_gdf(boundary_geojson: Dict[str, Any]) -> gpd.GeoDataFrame:
    """Wrap a boundary GeoJSON as a single-row GeoDataFrame in EPSG:4326.

    Accepts a FeatureCollection, a Feature, or a bare Polygon or MultiPolygon.
    """
    geometry = _geometry_of(boundary_geojson)
    if geometry.is_empty:
        raise ValueError("boundary geometry is empty")
    if not geometry.is_valid:
        raise ValueError("boundary geometry is not valid")

    return gpd.GeoDataFrame(geometry=[geometry], crs=f"EPSG:{GEODETIC_EPSG}")


def bbox_in_crs(
    boundary_gdf: gpd.GeoDataFrame,
    epsg: int,
) -> Tuple[float, float, float, float]:
    """Bounding box of the boundary in the CRS a service expects."""
    x_min, y_min, x_max, y_max = boundary_gdf.to_crs(epsg=epsg).total_bounds
    return float(x_min), float(y_min), float(x_max), float(y_max)


def clip(
    buildings_gdf: gpd.GeoDataFrame,
    boundary_gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Keep the buildings that intersect the boundary, using its spatial index."""
    inside = gpd.sjoin(
        buildings_gdf,
        boundary_gdf[["geometry"]],
        how="inner",
        predicate="intersects",
    )
    inside = inside.drop(columns=["index_right"])
    return inside.reset_index(drop=True)


def split_into_tiles(
    boundary_geojson: Dict[str, Any],
    target_tiles: int,
    metric_epsg: int,
    min_tile_side_m: float = 250.0,
) -> List[Dict[str, Any]]:
    """Cut a boundary into up to ``target_tiles`` pieces that together cover it.

    The grid is built in metres so the tiles are square on the ground. Tiles that miss the
    boundary are dropped, so a thin or L-shaped boundary yields fewer tiles than asked.
    A boundary too small to divide comes back as a single piece.

    The grid rectangles are reprojected back before being cut against the boundary, so the
    outer edge of the tiles is the original boundary geometry itself. Cutting in metres and
    reprojecting afterwards would leave reprojection slivers along that edge, and a building
    sitting exactly on it would be picked up by a whole-boundary run but missed by a tiled
    one. The tiles must cover exactly what the whole boundary covers.

    A building touching an inner tile edge lands in both neighbouring tiles, so whoever
    recombines the pieces has to drop repeated buildings.
    """
    if target_tiles <= 1:
        return [boundary_geojson]

    boundary_gdf = to_gdf(boundary_geojson)
    boundary_geometry = boundary_gdf.geometry.iloc[0]
    in_metres = boundary_gdf.to_crs(epsg=metric_epsg)
    x_min, y_min, x_max, y_max = in_metres.total_bounds

    width = x_max - x_min
    height = y_max - y_min
    steps = max(1, int(math.ceil(math.sqrt(target_tiles))))

    if width / steps < min_tile_side_m or height / steps < min_tile_side_m:
        steps = max(
            1,
            min(
                int(width // min_tile_side_m) or 1,
                int(height // min_tile_side_m) or 1,
            ),
        )
    if steps <= 1:
        return [boundary_geojson]

    tile_width = width / steps
    tile_height = height / steps

    rectangles = []
    for row in range(steps):
        for column in range(steps):
            rectangles.append(
                box(
                    x_min + column * tile_width,
                    y_min + row * tile_height,
                    x_min + (column + 1) * tile_width,
                    y_min + (row + 1) * tile_height,
                )
            )

    grid = gpd.GeoDataFrame(geometry=rectangles, crs=in_metres.crs)
    grid = grid.to_crs(epsg=GEODETIC_EPSG)

    tile_geojson: List[Dict[str, Any]] = []
    for rectangle in grid.geometry:
        piece = rectangle.intersection(boundary_geometry)
        if piece.is_empty:
            continue
        tile_geojson.append(mapping(piece))

    if len(tile_geojson) <= 1:
        return [boundary_geojson]
    return tile_geojson


def _geometry_of(boundary_geojson: Dict[str, Any]):
    """Pull a single shapely geometry out of any accepted boundary GeoJSON shape."""
    if not isinstance(boundary_geojson, dict):
        raise ValueError("boundary must be a GeoJSON dict")

    geojson_type = boundary_geojson.get("type")

    if geojson_type == "FeatureCollection":
        features = boundary_geojson.get("features") or []
        if not features:
            raise ValueError("boundary FeatureCollection has no features")
        geometries = []
        for feature in features:
            geometries.append(shape(feature["geometry"]))
        return union_all(geometries)

    if geojson_type == "Feature":
        return shape(boundary_geojson["geometry"])

    if geojson_type in ("Polygon", "MultiPolygon", "GeometryCollection"):
        return shape(boundary_geojson)

    raise ValueError(f"unsupported boundary GeoJSON type: {geojson_type!r}")
