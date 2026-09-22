"""Boundary parsing and clipping. No network needed."""

import geopandas as gpd
import pytest
from shapely.geometry import box, mapping

from city_information_modeler.core import boundary as boundary_module

POLYGON = {
    "type": "Polygon",
    "coordinates": [
        [[7.670, 45.060], [7.675, 45.060], [7.675, 45.065], [7.670, 45.065], [7.670, 45.060]]
    ],
}


def test_polygon_feature_and_collection_agree():
    feature = {"type": "Feature", "properties": {}, "geometry": POLYGON}
    collection = {"type": "FeatureCollection", "features": [feature]}

    from_polygon = boundary_module.to_gdf(POLYGON).geometry.iloc[0]
    from_feature = boundary_module.to_gdf(feature).geometry.iloc[0]
    from_collection = boundary_module.to_gdf(collection).geometry.iloc[0]

    assert from_polygon.equals(from_feature)
    assert from_polygon.equals(from_collection)


def test_collection_with_several_features_is_unioned():
    left = box(7.670, 45.060, 7.675, 45.065)
    right = box(7.675, 45.060, 7.680, 45.065)
    collection = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "properties": {}, "geometry": mapping(left)},
            {"type": "Feature", "properties": {}, "geometry": mapping(right)},
        ],
    }

    unioned = boundary_module.to_gdf(collection).geometry.iloc[0]
    assert unioned.area == pytest.approx(left.area + right.area)


@pytest.mark.parametrize(
    "bad",
    [
        "not a dict",
        {"type": "Point", "coordinates": [7.67, 45.06]},
        {"type": "FeatureCollection", "features": []},
    ],
)
def test_unusable_boundaries_are_rejected(bad):
    with pytest.raises(ValueError):
        boundary_module.to_gdf(bad)


def test_bbox_is_returned_in_the_requested_crs():
    boundary = boundary_module.to_gdf(POLYGON)

    x_min, y_min, x_max, y_max = boundary_module.bbox_in_crs(boundary, 32632)
    assert 300000 < x_min < 500000
    assert 4900000 < y_min < 5100000
    assert x_max > x_min and y_max > y_min


def test_clip_keeps_only_intersecting_buildings():
    boundary = boundary_module.to_gdf(POLYGON)
    inside = box(7.671, 45.061, 7.672, 45.062)
    outside = box(7.700, 45.090, 7.701, 45.091)
    buildings = gpd.GeoDataFrame(
        {"building_uuid": ["inside", "outside"]},
        geometry=[inside, outside],
        crs="EPSG:4326",
    )

    clipped = boundary_module.clip(buildings, boundary)
    assert clipped["building_uuid"].tolist() == ["inside"]
    assert "index_right" not in clipped.columns
