"""
Metric-CRS helpers for LoD 1.2 geometry.

Footprints are stored in EPSG:4326 (degrees) while LoD 1.2 heights are in
metres.  Mixing the two produces areas in square degrees and 3D models whose
vertical axis is ~25000x the horizontal extent, so every area, volume and 3D
export has to be computed in a projected CRS.

EPSG:32632 (UTM zone 32N) is used to match ``logic/stand_alone_CIM.ipynb``,
which calls ``to_crs(32632)`` before measuring or plotting.
"""

from functools import lru_cache
from typing import Any, Dict, List, Optional, Sequence, Tuple

GEODETIC_EPSG = 4326
METRIC_EPSG = 32632

Coord = Sequence[float]
Ring = Sequence[Coord]


@lru_cache(maxsize=4)
def _transformer(from_epsg: int, to_epsg: int):
    from pyproj import Transformer

    return Transformer.from_crs(
        f"EPSG:{from_epsg}", f"EPSG:{to_epsg}", always_xy=True
    )


def to_metric(lon: float, lat: float) -> Tuple[float, float]:
    """Project a single lon/lat pair to METRIC_EPSG easting/northing."""
    return _transformer(GEODETIC_EPSG, METRIC_EPSG).transform(lon, lat)


def to_geodetic(x: float, y: float) -> Tuple[float, float]:
    """Inverse of :func:`to_metric`."""
    return _transformer(METRIC_EPSG, GEODETIC_EPSG).transform(x, y)


def ring_to_metric(ring: Ring) -> List[List[float]]:
    """Project a ring's X/Y to metres, preserving any Z (already in metres)."""
    tr = _transformer(GEODETIC_EPSG, METRIC_EPSG)
    out: List[List[float]] = []
    for c in ring:
        x, y = tr.transform(c[0], c[1])
        out.append([x, y, c[2]] if len(c) > 2 else [x, y])
    return out


def ring_length_m(p1: Coord, p2: Coord) -> float:
    """Planimetric distance in metres between two lon/lat points."""
    x1, y1 = to_metric(p1[0], p1[1])
    x2, y2 = to_metric(p2[0], p2[1])
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


def ring_area_m2(ring: Ring) -> float:
    """Planimetric area (m2) of a lon/lat ring via the shoelace formula."""
    coords = ring_to_metric(ring)
    if len(coords) < 4:
        return 0.0
    area = 0.0
    for i in range(len(coords) - 1):
        area += coords[i][0] * coords[i + 1][1]
        area -= coords[i + 1][0] * coords[i][1]
    return abs(area) / 2.0


def polygon_area_m2(geometry: Optional[Dict[str, Any]]) -> float:
    """Planimetric area (m2) of a GeoJSON Polygon/MultiPolygon in EPSG:4326."""
    if not geometry:
        return 0.0
    gtype = geometry.get("type")
    coords = geometry.get("coordinates") or []
    if gtype == "Polygon":
        return ring_area_m2(coords[0]) if coords else 0.0
    if gtype == "MultiPolygon":
        return sum(ring_area_m2(poly[0]) for poly in coords if poly)
    return 0.0


def polygon_area_3d_m2(coords: Ring) -> float:
    """True 3D area (m2) of a planar ring, using Newell's method.

    Works for vertical walls as well as horizontal slabs, unlike a plain
    projection onto the XY plane.
    """
    pts = ring_to_metric(coords)
    if len(pts) < 4:
        return 0.0
    nx = ny = nz = 0.0
    for i in range(len(pts) - 1):
        x1, y1 = pts[i][0], pts[i][1]
        z1 = pts[i][2] if len(pts[i]) > 2 else 0.0
        x2, y2 = pts[i + 1][0], pts[i + 1][1]
        z2 = pts[i + 1][2] if len(pts[i + 1]) > 2 else 0.0
        nx += (y1 - y2) * (z1 + z2)
        ny += (z1 - z2) * (x1 + x2)
        nz += (x1 - x2) * (y1 + y2)
    return ((nx * nx + ny * ny + nz * nz) ** 0.5) / 2.0
