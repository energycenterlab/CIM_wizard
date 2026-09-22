"""
WFS reading, in the two flavours the Piemonte services actually need.

Some servers answer a GetFeature in full; others silently cap one response and need
paging. The cap is not advertised anywhere, so which function a source uses is a measured
property of that server, recorded in the source module.

Stateless: functions take a URL and a bounding box and return a GeoDataFrame.
"""

from typing import Any, Dict, List, Tuple

import geopandas as gpd
import pandas as pd
import requests

REQUEST_TIMEOUT_S = 180
MAX_PAGES = 500


def fetch_single(
    url: str,
    layer: str,
    bbox: Tuple[float, float, float, float],
    epsg: int,
    timeout_s: int = REQUEST_TIMEOUT_S,
) -> gpd.GeoDataFrame:
    """Read a WFS 1.0.0 layer in one GetFeature request.

    For servers that return every matching feature at once.
    """
    x_min, y_min, x_max, y_max = bbox
    params = {
        "service": "WFS",
        "version": "1.0.0",
        "request": "GetFeature",
        "typeName": layer,
        "BBOX": f"{x_min:.0f},{y_min:.0f},{x_max:.0f},{y_max:.0f}",
        "outputFormat": "geojson",
    }
    response = requests.get(url, params=params, timeout=timeout_s)
    response.raise_for_status()
    return features_to_gdf(response.json().get("features", []), epsg)


def fetch_paged(
    url: str,
    layer: str,
    bbox: Tuple[float, float, float, float],
    epsg: int,
    page_size: int,
    timeout_s: int = REQUEST_TIMEOUT_S,
    max_pages: int = MAX_PAGES,
) -> gpd.GeoDataFrame:
    """Read a WFS 2.0.0 layer page by page with ``startIndex``.

    For servers that silently cap one response at ``page_size`` features. Pages are
    requested until one comes back short.
    """
    x_min, y_min, x_max, y_max = bbox
    bbox_param = (
        f"{x_min:.0f},{y_min:.0f},{x_max:.0f},{y_max:.0f},urn:ogc:def:crs:EPSG::{epsg}"
    )

    pages: List[gpd.GeoDataFrame] = []
    start_index = 0

    for _ in range(max_pages):
        params = {
            "service": "WFS",
            "version": "2.0.0",
            "request": "GetFeature",
            "typeNames": layer,
            "BBOX": bbox_param,
            "outputFormat": "geojson",
            "count": page_size,
            "startIndex": start_index,
        }
        response = requests.get(url, params=params, timeout=timeout_s)
        response.raise_for_status()
        features = response.json().get("features", [])

        if features:
            pages.append(features_to_gdf(features, epsg))
        if len(features) < page_size:
            return concat_pages(pages, epsg)
        start_index += page_size

    raise RuntimeError(
        f"WFS layer {layer!r} still returning full pages after {max_pages} pages; "
        "use a smaller boundary"
    )


def features_to_gdf(features: List[Dict[str, Any]], epsg: int) -> gpd.GeoDataFrame:
    """Read a list of GeoJSON features into a GeoDataFrame with an explicit CRS."""
    if not features:
        return gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs=f"EPSG:{epsg}")
    return gpd.GeoDataFrame.from_features(features, crs=f"EPSG:{epsg}")


def concat_pages(pages: List[gpd.GeoDataFrame], epsg: int) -> gpd.GeoDataFrame:
    """Stack the pages of one layer into a single GeoDataFrame with a clean index."""
    if not pages:
        return gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs=f"EPSG:{epsg}")
    stacked = pd.concat(pages, ignore_index=True)
    return gpd.GeoDataFrame(stacked, geometry="geometry", crs=f"EPSG:{epsg}")
