"""Compute profiles, splitting and merging. No network needed."""

import geopandas as gpd
import pandas as pd
import pytest
from shapely import union_all
from shapely.geometry import box, shape

from city_information_modeler.core import boundary as boundary_module
from city_information_modeler.core.contracts import (
    ParallelSpec,
    parallelizable,
)
from city_information_modeler.core.geometry import METRIC_EPSG
from city_information_modeler.parallel import Runner, load_profile
from city_information_modeler.parallel.profile import ComputeProfile
from city_information_modeler.parallel import splitters

TORINO_BOX = {
    "type": "Polygon",
    "coordinates": [
        [
            [7.650, 45.050],
            [7.690, 45.050],
            [7.690, 45.070],
            [7.650, 45.070],
            [7.650, 45.050],
        ]
    ],
}


def profile(**overrides) -> ComputeProfile:
    values = {
        "name": "test",
        "cpu_cores": 8,
        "ram_gb": 16.0,
        "reserve_cores": 1,
        "ram_per_cpu_worker_gb": 2.0,
        "max_cpu_workers": None,
        "io_workers": 4,
        "spatial_tile_oversubscribe": 2,
        "min_tile_side_m": 250.0,
        "min_rows_per_split": 10,
    }
    values.update(overrides)
    return ComputeProfile(**values)


# --- compute profile ---


def test_shipped_profiles_all_load():
    for name in ("auto", "laptop", "workstation", "sequential"):
        assert load_profile(name).cpu_workers >= 1


def test_unknown_profile_is_rejected():
    with pytest.raises(ValueError):
        load_profile("does_not_exist")


def test_cpu_workers_limited_by_cores():
    assert profile(cpu_cores=8, reserve_cores=1, ram_gb=1000).cpu_workers == 7


def test_cpu_workers_limited_by_memory():
    """A big core count must not spawn more workers than the RAM can hold."""
    limited = profile(cpu_cores=64, reserve_cores=0, ram_gb=8, ram_per_cpu_worker_gb=2.0)
    assert limited.cpu_workers == 4


def test_cpu_workers_limited_by_ceiling():
    assert profile(cpu_cores=64, ram_gb=1000, max_cpu_workers=3).cpu_workers == 3


def test_cpu_workers_never_below_one():
    assert profile(cpu_cores=1, reserve_cores=4, ram_gb=0.5).cpu_workers == 1


def test_io_workers_are_not_capped_by_cores():
    """Network-bound work waits rather than computes, so it may exceed the core count."""
    assert profile(cpu_cores=2, io_workers=16).workers_for("io") == 16


# --- spatial splitting ---


def test_tiles_cover_exactly_the_boundary():
    """The decisive property: tiling must not change what the boundary covers."""
    tiles = boundary_module.split_into_tiles(TORINO_BOX, 16, METRIC_EPSG)
    assert len(tiles) > 1

    covered = union_all([shape(tile) for tile in tiles])
    original = shape(TORINO_BOX)
    assert covered.symmetric_difference(original).area == pytest.approx(0.0, abs=1e-12)


def test_tiny_boundary_is_not_split():
    tiny = {
        "type": "Polygon",
        "coordinates": [
            [[7.6700, 45.0600], [7.6701, 45.0600], [7.6701, 45.0601], [7.6700, 45.0601], [7.6700, 45.0600]]
        ],
    }
    assert boundary_module.split_into_tiles(tiny, 16, METRIC_EPSG) == [tiny]


def test_one_tile_requested_returns_the_boundary():
    assert boundary_module.split_into_tiles(TORINO_BOX, 1, METRIC_EPSG) == [TORINO_BOX]


def test_non_rectangular_boundary_drops_empty_tiles():
    triangle = {
        "type": "Polygon",
        "coordinates": [[[7.650, 45.050], [7.690, 45.050], [7.650, 45.070], [7.650, 45.050]]],
    }
    tiles = boundary_module.split_into_tiles(triangle, 16, METRIC_EPSG)
    covered = union_all([shape(tile) for tile in tiles])
    assert covered.symmetric_difference(shape(triangle)).area == pytest.approx(0.0, abs=1e-12)


# --- row splitting ---


def test_row_batches_preserve_every_row():
    frame = pd.DataFrame({"value": range(100)})
    batches = splitters.split_rows(frame, pieces=4, min_rows_per_split=10)
    assert len(batches) == 4
    assert sum(len(batch) for batch in batches) == 100
    assert pd.concat(batches)["value"].tolist() == list(range(100))


def test_small_frame_is_not_split_below_the_minimum():
    frame = pd.DataFrame({"value": range(10)})
    assert len(splitters.split_rows(frame, pieces=8, min_rows_per_split=5000)) == 1


def test_empty_frame_is_not_split():
    assert len(splitters.split_rows(pd.DataFrame({"value": []}), 4, 1)) == 1


# --- merging ---


def test_merge_drops_buildings_repeated_across_tiles():
    """Tiles overlap at their edges, so the same building arrives twice."""
    spec = ParallelSpec(
        split="spatial_tiles",
        merge="concat_dedup",
        workload="io",
        split_arg="boundary_geojson",
        dedup_on="building_uuid",
    )
    first = gpd.GeoDataFrame(
        {"building_uuid": ["a", "b"]}, geometry=[box(0, 0, 1, 1), box(1, 0, 2, 1)], crs="EPSG:4326"
    )
    second = gpd.GeoDataFrame(
        {"building_uuid": ["b", "c"]}, geometry=[box(1, 0, 2, 1), box(2, 0, 3, 1)], crs="EPSG:4326"
    )

    merged = splitters.merge_results([first, second], spec)
    assert merged["building_uuid"].tolist() == ["a", "b", "c"]
    assert merged.crs == first.crs


def test_merge_concat_keeps_duplicates():
    spec = ParallelSpec(
        split="row_batches", merge="concat", workload="cpu", split_arg="frame"
    )
    frame = pd.DataFrame({"value": [1, 1]})
    assert len(splitters.merge_results([frame, frame], spec)) == 4


def test_merge_on_missing_column_is_an_error():
    spec = ParallelSpec(
        split="spatial_tiles",
        merge="concat_dedup",
        workload="io",
        split_arg="boundary_geojson",
        dedup_on="absent",
    )
    frame = pd.DataFrame({"value": [1]})
    with pytest.raises(ValueError):
        splitters.merge_results([frame, frame], spec)


# --- runner ---


class Adder:
    """Stands in for a core class: immutable, and its method declares how to split."""

    @parallelizable(
        split="row_batches",
        merge="concat",
        workload="cpu",
        split_arg="frame",
        min_rows_per_split=10,
    )
    def add_one(self, frame: pd.DataFrame) -> pd.DataFrame:
        result = frame.copy()
        result["value"] = result["value"] + 1
        return result


def test_runner_parallel_matches_sequential():
    frame = pd.DataFrame({"value": range(200)})
    adder = Adder()

    sequential = Runner(profile=profile(max_cpu_workers=1)).run(adder.add_one, frame)
    parallel = Runner(profile=profile(max_cpu_workers=4)).run(adder.add_one, frame)

    assert sequential["value"].tolist() == parallel["value"].tolist()
    assert parallel["value"].tolist() == list(range(1, 201))


def test_runner_reports_what_it_did():
    runner = Runner(profile=profile(max_cpu_workers=4))
    runner.run(Adder().add_one, pd.DataFrame({"value": range(200)}))

    report = runner.last_report
    assert report.pieces > 1
    assert report.workload == "cpu"
    assert report.rows_out == 200


def test_runner_explains_without_running():
    runner = Runner(profile=profile(max_cpu_workers=4))
    plan = runner.explain(Adder().add_one, pd.DataFrame({"value": range(200)}))

    assert plan["strategy"] == "row_batches"
    assert plan["pieces"] > 1
    assert runner.last_report is None


def test_runner_needs_the_declared_argument():
    runner = Runner(profile=profile())
    with pytest.raises(TypeError):
        runner.run(Adder().add_one)
