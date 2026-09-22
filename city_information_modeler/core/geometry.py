"""
Coordinate reference systems and metric helpers.

Payloads, WFS answers and stored geometry are geographic (EPSG:4326). Anything measured
in metres -- distance, area, volume, extrusion, geometry rounding -- is projected to
EPSG:32632 (UTM zone 32N), which covers Piemonte.

Stateless: functions take geometry and return geometry or numbers.
"""

import geopandas as gpd
import pandas as pd

GEODETIC_EPSG = 4326
METRIC_EPSG = 32632


def to_metric(geometry: gpd.GeoSeries) -> gpd.GeoSeries:
    """Project geometry to the metric CRS used for every measurement."""
    return geometry.to_crs(epsg=METRIC_EPSG)


def to_geodetic(geometry: gpd.GeoSeries) -> gpd.GeoSeries:
    """Project geometry back to the geographic CRS used for storage and payloads."""
    return geometry.to_crs(epsg=GEODETIC_EPSG)


def area_m2(geometry: gpd.GeoSeries) -> pd.Series:
    """Planimetric area in square metres, measured in the metric CRS."""
    return to_metric(geometry).area
