"""
The building schema every footprint source returns.

Sources publish different fields under different names, so each one maps its answer onto
``STANDARD_COLUMNS``. A source that does not publish a field leaves it null rather than
inventing a value, which keeps the frames comparable and makes conflation possible later.

Stateless: functions take frames and return frames.
"""

import hashlib
from typing import List, Optional
import uuid

import geopandas as gpd
import pandas as pd
import shapely

from city_information_modeler.core.geometry import GEODETIC_EPSG, METRIC_EPSG

# Deterministic namespace so the same building always gets the same building_uuid.
BUILDING_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "https://cimwizard.polito.it/building")

# Centimetre rounding for ids derived from geometry. Applied in METRIC_EPSG, because
# rounding degrees to two decimals would merge footprints a kilometre apart.
GEOMETRY_KEY_PRECISION = 2

# Values that mean "no value" in the Piemonte open datasets.
NULL_TOKENS = ("", "non conosciuto", "Non conosciuto")

STANDARD_COLUMNS: List[str] = [
    "building_uuid",
    "source",
    "source_id",
    "usage",
    "usage_raw",
    "building_type",
    "building_group",
    "is_minor_building",
    "status",
    "name",
    "is_monument",
    "height_m",
    "height_source",
    "n_floors",
    "ground_elevation_m",
    "eave_elevation_m",
    "construction_year",
    "construction_period",
    "construction_year_from",
    "construction_year_to",
    "construction_year_source",
    "volume_units",
    "survey_year",
    "survey_date",
    "update_date",
    "valid_until",
    "data_supplier",
    "data_producer",
    "production_method",
    "acquisition_scale",
    "geometry",
]

# Dtype for a column a source does not publish. Without this an absent column would be
# object-dtype NA, and a later conflation filling it from another source would leave
# integers and floats sitting in an object column.
STANDARD_DTYPES = {
    "height_m": "Float64",
    "ground_elevation_m": "Float64",
    "eave_elevation_m": "Float64",
    "n_floors": "Int64",
    "construction_year": "Int64",
    "construction_year_from": "Int64",
    "construction_year_to": "Int64",
    "survey_year": "Int64",
    "volume_units": "Int64",
    "is_monument": "boolean",
    "is_minor_building": "boolean",
}
DEFAULT_STANDARD_DTYPE = "string"


def clean_text(values: pd.Series) -> pd.Series:
    """Trim a text column and turn the datasets' "no value" tokens into NA."""
    cleaned = values.astype("string").str.strip()
    return cleaned.replace(list(NULL_TOKENS), pd.NA)


def geometry_keys(buildings_gdf: gpd.GeoDataFrame) -> pd.Series:
    """Short, stable keys derived from the footprints themselves.

    Used for sources that publish no identifier. The same footprint always produces the
    same key, so ids stay stable between fetches as long as the geometry does not move.
    The footprints are projected to metres first, so the key does not depend on the CRS
    the caller happens to be holding and the rounding stays at one centimetre.
    """
    in_metres = buildings_gdf.geometry.to_crs(epsg=METRIC_EPSG)
    well_known_text = shapely.to_wkt(
        in_metres.values, rounding_precision=GEOMETRY_KEY_PRECISION
    )

    keys: List[str] = []
    for text in well_known_text:
        keys.append(hashlib.sha1(text.encode("utf-8")).hexdigest()[:16])
    return pd.Series(keys, index=buildings_gdf.index, dtype="string")


def building_uuid(source: str, source_id: Optional[str]) -> Optional[str]:
    """Deterministic building id from a source name and that source's identifier."""
    if source_id is None or pd.isna(source_id):
        return None
    return str(uuid.uuid5(BUILDING_NAMESPACE, f"{source}:{source_id}"))


def building_uuids(source: str, source_ids: pd.Series) -> pd.Series:
    """Deterministic building ids for a whole column of source identifiers."""
    return source_ids.map(lambda source_id: building_uuid(source, source_id))


def to_standard_schema(buildings_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Add the standard columns a source did not fill and put them in a fixed order.

    An added column is empty but typed, so a source that publishes no construction year
    still hands back an integer column rather than an object one.
    """
    standard = buildings_gdf.copy()
    for column in STANDARD_COLUMNS:
        if column not in standard.columns:
            standard[column] = pd.Series(pd.NA, index=standard.index, dtype=dtype_of(column))
    return standard[STANDARD_COLUMNS]


def dtype_of(column: str) -> str:
    """Dtype an empty standard column should carry."""
    return STANDARD_DTYPES.get(column, DEFAULT_STANDARD_DTYPE)


def empty_buildings() -> gpd.GeoDataFrame:
    """An empty result that still carries the standard schema."""
    columns = {}
    for column in STANDARD_COLUMNS:
        if column == "geometry":
            columns[column] = gpd.GeoSeries([], crs=f"EPSG:{GEODETIC_EPSG}")
        else:
            columns[column] = pd.Series([], dtype=dtype_of(column))

    return gpd.GeoDataFrame(columns, geometry="geometry", crs=f"EPSG:{GEODETIC_EPSG}")
