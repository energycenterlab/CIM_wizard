"""Synthetic roofs from 2D building footprints.

Classifies each footprint as flat, gable or hipped and builds roof faces.
Lengths are measured in EPSG:32632; input and output stay EPSG:4326 with z in metres.
"""

import argparse
import math

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from pyproj import Transformer
from shapely.geometry import LineString, Polygon

METRIC_CRS = "EPSG:32632"
STORAGE_CRS = "EPSG:4326"

# TODO: move these roof rules into config
DEFAULT_EAVE_H_M = 9.0
SMALL_FLAT_M2 = 40.0
LARGE_FLAT_M2 = 1500.0
GABLE_MIN_ASPECT = 1.5
PITCH_DEG = 30.0
MIN_FACE_AREA_M2 = 0.01

_TO_STORAGE = Transformer.from_crs(METRIC_CRS, STORAGE_CRS, always_xy=True)


def _sample_footprints() -> gpd.GeoDataFrame:
    """Five Torino footprints: shed, elongated block, house, L, industrial box."""
    # TODO: stand-in footprints around lon 7.68, lat 45.07 until a GeoJSON is passed in
    to_metric = Transformer.from_crs(STORAGE_CRS, METRIC_CRS, always_xy=True)
    ox, oy = to_metric.transform(7.68, 45.07)
    shed = _box(ox, oy, 5.0, 6.0)
    block = shapely.affinity.rotate(_box(ox + 50.0, oy, 10.0, 25.0), 20.0, origin="centroid")
    house = shapely.affinity.rotate(_box(ox + 110.0, oy, 14.0, 16.0), 25.0, origin="centroid")
    ell = Polygon([
        (ox + 160.0, oy),
        (ox + 178.0, oy),
        (ox + 178.0, oy + 6.0),
        (ox + 166.0, oy + 6.0),
        (ox + 166.0, oy + 14.0),
        (ox + 160.0, oy + 14.0),
    ])
    industrial = _box(ox + 210.0, oy, 60.0, 40.0)
    frame = gpd.GeoDataFrame(
        {"height": [None, None, 8.0, None, 12.0]},
        geometry=[shed, block, house, ell, industrial],
        crs=METRIC_CRS,
    )
    return frame.to_crs(STORAGE_CRS)


def _box(x: float, y: float, width: float, height: float) -> Polygon:
    return Polygon([
        (x, y),
        (x + width, y),
        (x + width, y + height),
        (x, y + height),
    ])


def load_footprints(path: str | None) -> gpd.GeoDataFrame:
    if path is None:
        return _sample_footprints()
    frame = gpd.read_file(path)
    if frame.crs is None:
        return frame.set_crs(STORAGE_CRS)
    return frame.to_crs(STORAGE_CRS)


def footprint_parts(frame: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Explode multipolygons; keep the source feature index as building_idx."""
    metric = frame.to_crs(METRIC_CRS).reset_index(drop=True)
    metric["building_idx"] = metric.index.astype(int)
    if "height" not in metric.columns:
        metric["height"] = np.nan
    metric["height"] = pd.to_numeric(metric["height"], errors="coerce")
    parts = metric[["building_idx", "height", "geometry"]].explode(ignore_index=True)
    parts = parts[parts.geometry.geom_type == "Polygon"].copy()
    return parts[parts.geometry.area > 0].reset_index(drop=True)


def _rect_corners(rect: Polygon) -> list[tuple[float, float]]:
    corners = [(float(x), float(y)) for x, y, *_ in list(rect.exterior.coords)[:-1]]
    if len(corners) != 4:
        raise ValueError(f"minimum rotated rectangle has {len(corners)} corners; expected 4")
    return corners


def _side_lengths(corners: list[tuple[float, float]]) -> tuple[float, float, bool]:
    c0, c1, c2, c3 = corners
    along_01 = (math.hypot(c1[0] - c0[0], c1[1] - c0[1]) + math.hypot(c3[0] - c2[0], c3[1] - c2[1])) / 2.0
    along_12 = (math.hypot(c2[0] - c1[0], c2[1] - c1[1]) + math.hypot(c0[0] - c3[0], c0[1] - c3[1])) / 2.0
    if along_01 >= along_12:
        return along_01, along_12, True
    return along_12, along_01, False


def _classify(area: float, length: float, width: float) -> str:
    if area < SMALL_FLAT_M2 or area > LARGE_FLAT_M2 or width <= 0.0:
        return "flat"
    if length / width >= GABLE_MIN_ASPECT:
        return "gable"
    return "hipped"


def _unit(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    norm = math.hypot(dx, dy)
    return dx / norm, dy / norm


def _dedupe(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    cleaned: list[tuple[float, float]] = []
    for point in points:
        if cleaned and math.hypot(point[0] - cleaned[-1][0], point[1] - cleaned[-1][1]) < 1e-6:
            continue
        cleaned.append(point)
    if len(cleaned) >= 2 and math.hypot(cleaned[0][0] - cleaned[-1][0], cleaned[0][1] - cleaned[-1][1]) < 1e-6:
        cleaned.pop()
    return cleaned


def _region(
    points: list[tuple[float, float]],
    eave: tuple[tuple[float, float], tuple[float, float]],
) -> tuple[Polygon, LineString] | None:
    ring = _dedupe(points)
    if len(ring) < 3:
        return None
    poly = Polygon(ring)
    if poly.is_empty or poly.area < MIN_FACE_AREA_M2:
        return None
    return poly, LineString(eave)


def _keep_regions(
    specs: list[tuple[list[tuple[float, float]], tuple[tuple[float, float], tuple[float, float]]]],
) -> list[tuple[Polygon, LineString]]:
    regions = []
    for points, eave in specs:
        region = _region(points, eave)
        if region is not None:
            regions.append(region)
    return regions


def _gable_regions(
    corners: list[tuple[float, float]],
    long_first: bool,
) -> list[tuple[Polygon, LineString]]:
    c0, c1, c2, c3 = corners
    if long_first:
        mid_plus = ((c1[0] + c2[0]) / 2.0, (c1[1] + c2[1]) / 2.0)
        mid_minus = ((c3[0] + c0[0]) / 2.0, (c3[1] + c0[1]) / 2.0)
        specs = [
            ([c0, c1, mid_plus, mid_minus], (c0, c1)),
            ([c2, c3, mid_minus, mid_plus], (c2, c3)),
        ]
    else:
        mid_plus = ((c2[0] + c3[0]) / 2.0, (c2[1] + c3[1]) / 2.0)
        mid_minus = ((c0[0] + c1[0]) / 2.0, (c0[1] + c1[1]) / 2.0)
        specs = [
            ([c1, c2, mid_plus, mid_minus], (c1, c2)),
            ([c3, c0, mid_minus, mid_plus], (c3, c0)),
        ]
    return _keep_regions(specs)


def _hip_regions(
    corners: list[tuple[float, float]],
    length: float,
    width: float,
    long_first: bool,
) -> list[tuple[Polygon, LineString]]:
    c0, c1, c2, c3 = corners
    if long_first:
        direction = _unit(c0, c1)
        long_a, long_b = (c0, c1), (c2, c3)
        short_minus, short_plus = (c3, c0), (c1, c2)
    else:
        direction = _unit(c1, c2)
        long_a, long_b = (c1, c2), (c3, c0)
        short_minus, short_plus = (c0, c1), (c2, c3)
    centre = (
        (c0[0] + c1[0] + c2[0] + c3[0]) / 4.0,
        (c0[1] + c1[1] + c2[1] + c3[1]) / 4.0,
    )
    half_ridge = (length - width) / 2.0
    ridge_minus = (centre[0] - direction[0] * half_ridge, centre[1] - direction[1] * half_ridge)
    ridge_plus = (centre[0] + direction[0] * half_ridge, centre[1] + direction[1] * half_ridge)
    specs = [
        ([long_a[0], long_a[1], ridge_plus, ridge_minus], long_a),
        ([long_b[0], long_b[1], ridge_minus, ridge_plus], long_b),
        ([short_plus[0], short_plus[1], ridge_plus], short_plus),
        ([short_minus[0], short_minus[1], ridge_minus], short_minus),
    ]
    return _keep_regions(specs)


def _polygon_parts(geom) -> list[Polygon]:
    if geom is None or geom.is_empty:
        return []
    kind = geom.geom_type
    if kind == "Polygon":
        parts = [geom]
    elif kind == "MultiPolygon":
        parts = list(geom.geoms)
    elif kind == "GeometryCollection":
        parts = []
        for piece in geom.geoms:
            parts.extend(_polygon_parts(piece))
    else:
        return []
    kept = []
    for part in parts:
        if part.area >= MIN_FACE_AREA_M2:
            kept.append(part)
    return kept


def _polygon_z(
    face: Polygon,
    eave: LineString | None,
    eave_h: float,
    rise: float,
    half_w: float,
) -> Polygon:
    # TODO: interiors (courtyards) are ignored; exterior ring only
    coords = []
    for x, y, *_rest in face.exterior.coords:
        if eave is None:
            z = eave_h
        else:
            distance = float(shapely.Point(x, y).distance(eave))
            distance = min(max(distance, 0.0), half_w)
            z = eave_h + rise * distance
        coords.append((float(x), float(y), z))
    return Polygon(coords)


def _faces_for_part(building_idx: int, poly: Polygon, eave_h: float) -> list[dict]:
    # 1. Axes of the minimum rotated rectangle, then the roof rule.
    rect = poly.minimum_rotated_rectangle
    corners = _rect_corners(rect)
    length, width, long_first = _side_lengths(corners)
    roof_type = _classify(float(poly.area), length, width)
    pitch = 0.0 if roof_type == "flat" else PITCH_DEG
    rise = math.tan(math.radians(pitch))
    half_w = width / 2.0
    ridge_h = eave_h + rise * half_w

    # 2. Flat: the footprint. Gable: two long halves. Hipped: two traps and two triangles.
    if roof_type == "flat":
        regions: list[tuple[Polygon, LineString | None]] = [(poly, None)]
    elif roof_type == "gable":
        regions = _gable_regions(corners, long_first)
    else:
        regions = _hip_regions(corners, length, width, long_first)

    # 3. Clip to the footprint and set z from the distance to that face's eave.
    faces = []
    for region, eave in regions:
        for part in _polygon_parts(poly.intersection(region)):
            geom = _polygon_z(part, eave, eave_h, rise, half_w)
            if geom.is_empty or shapely.force_2d(geom).area < MIN_FACE_AREA_M2:
                continue
            faces.append({
                "building_idx": building_idx,
                "roof_type": roof_type,
                "pitch_deg": pitch,
                "eave_h": eave_h,
                "ridge_h": ridge_h,
                "roof_source": "synthetic_rule",
                "geometry": geom,
            })
    return faces


def build_roofs(parts: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    records: list[dict] = []
    for row in parts.itertuples(index=False):
        eave_h = DEFAULT_EAVE_H_M if pd.isna(row.height) else float(row.height)
        records.extend(_faces_for_part(int(row.building_idx), row.geometry, eave_h))
    columns = [
        "building_idx", "face_idx", "roof_type", "pitch_deg",
        "eave_h", "ridge_h", "roof_source", "geometry",
    ]
    if not records:
        return gpd.GeoDataFrame(columns=columns, geometry="geometry", crs=METRIC_CRS)
    frame = pd.DataFrame(records)
    frame["face_idx"] = frame.groupby("building_idx").cumcount()
    return gpd.GeoDataFrame(frame[columns], geometry="geometry", crs=METRIC_CRS)


def _project_to_storage(coords: np.ndarray) -> np.ndarray:
    lon, lat = _TO_STORAGE.transform(coords[:, 0], coords[:, 1])
    return np.column_stack([lon, lat, coords[:, 2]])


def reproject_faces(faces: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    geoms = [
        shapely.transform(geom, _project_to_storage, include_z=True)
        for geom in faces.geometry
    ]
    return gpd.GeoDataFrame(
        faces.drop(columns="geometry"),
        geometry=geoms,
        crs=STORAGE_CRS,
    )


def _face_area(group: pd.DataFrame) -> float:
    return float(sum(shapely.force_2d(geom).area for geom in group.geometry))


def self_check(faces: gpd.GeoDataFrame, parts: gpd.GeoDataFrame) -> None:
    footprint_m2 = parts.geometry.area.groupby(parts["building_idx"]).sum()
    for building_idx, foot_area in footprint_m2.items():
        group = faces[faces["building_idx"] == building_idx]
        face_area = _face_area(group)
        foot_area = float(foot_area)
        assert len(group) > 0, f"building {building_idx} produced no roof faces"
        assert abs(face_area - foot_area) <= 0.01 * foot_area, (
            f"building {building_idx}: face area {face_area:.4f} m2 vs footprint {foot_area:.4f} m2"
        )
        for row in group.itertuples(index=False):
            zs = shapely.get_coordinates(row.geometry, include_z=True)[:, 2]
            assert float(zs.min()) >= row.eave_h, (
                f"building {building_idx}: z {float(zs.min())} below eave {row.eave_h}"
            )
            assert float(zs.max()) <= row.ridge_h + 1e-6, (
                f"building {building_idx}: z {float(zs.max())} above ridge {row.ridge_h}"
            )


def print_summary(faces: gpd.GeoDataFrame, parts: gpd.GeoDataFrame) -> None:
    footprint_m2 = parts.geometry.area.groupby(parts["building_idx"]).sum()
    rows = []
    for building_idx, foot_area in footprint_m2.items():
        group = faces[faces["building_idx"] == building_idx]
        rows.append({
            "building_idx": int(building_idx),
            "roof_type": group["roof_type"].iloc[0],
            "pitch_deg": group["pitch_deg"].iloc[0],
            "eave_h": group["eave_h"].iloc[0],
            "ridge_h": group["ridge_h"].iloc[0],
            "n_faces": int(len(group)),
            "footprint_m2": float(foot_area),
            "face_m2": _face_area(group),
        })
    table = pd.DataFrame(rows)
    print(table.to_string(index=False, float_format=lambda value: f"{value:.3f}"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthetic roofs from building footprints")
    parser.add_argument("input", nargs="?", help="Footprint GeoJSON (EPSG:4326)")
    parser.add_argument("--out", help="Write roof-face GeoJSON (EPSG:4326, z in metres)")
    args = parser.parse_args()

    parts = footprint_parts(load_footprints(args.input))
    faces = build_roofs(parts)
    self_check(faces, parts)
    if args.out:
        reproject_faces(faces).to_file(args.out, driver="GeoJSON")
    else:
        print_summary(faces, parts)
    print("OK")


if __name__ == "__main__":
    main()
