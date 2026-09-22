"""Spatial matching, field resolution and provenance. No network needed."""

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box

from city_information_modeler.core import schema
from city_information_modeler.core.conflation import (
    CONFLATION_GROUPS,
    BuildingConflator,
    SourceFrames,
    conflated_columns,
    overlap_column,
    source_id_column,
)
from city_information_modeler.parallel import Runner
from city_information_modeler.parallel.profile import ComputeProfile
from city_information_modeler.parallel.splitters import split_source_frames

METRIC_CRS = 32632


def buildings(source: str, squares, **fields) -> gpd.GeoDataFrame:
    """A standard-schema frame from metric squares, for readable test fixtures."""
    frame = gpd.GeoDataFrame(
        {"source": [source] * len(squares)}, geometry=list(squares), crs=f"EPSG:{METRIC_CRS}"
    ).to_crs(4326)

    frame["source_id"] = [f"{source}-{index}" for index in range(len(squares))]
    frame["building_uuid"] = schema.building_uuids(source, frame["source_id"])
    for name, values in fields.items():
        frame[name] = values
    return schema.to_standard_schema(frame)


def square(x: float, y: float, side: float = 10.0):
    """A square footprint with its lower left corner at (x, y), in metres."""
    return box(395000 + x, 4990000 + y, 395000 + x + side, 4990000 + y + side)


def profile(**overrides) -> ComputeProfile:
    values = {
        "name": "test",
        "cpu_cores": 8,
        "ram_gb": 16.0,
        "reserve_cores": 0,
        "ram_per_cpu_worker_gb": 2.0,
        "max_cpu_workers": 1,
        "io_workers": 4,
        "spatial_tile_oversubscribe": 1,
        "min_tile_side_m": 250.0,
        "min_rows_per_split": 1,
    }
    values.update(overrides)
    return ComputeProfile(**values)


# --- matching ---


def test_overlapping_footprints_match():
    reference = buildings("dbgt", [square(0, 0)])
    candidate = buildings("bdtre", [square(1, 1)])

    matches = BuildingConflator().match(reference, candidate)

    assert len(matches) == 1
    assert matches.iloc[0]["reference_index"] == 0
    assert matches.iloc[0]["candidate_index"] == 0
    assert matches.iloc[0]["overlap_of_reference"] == pytest.approx(0.81, abs=0.02)


def test_a_sliver_of_overlap_is_not_a_match():
    """Neighbouring buildings touch along a wall; that must not count as the same building."""
    reference = buildings("dbgt", [square(0, 0)])
    candidate = buildings("bdtre", [square(9.5, 0)])

    assert BuildingConflator(min_overlap=0.3).match(reference, candidate).empty
    assert len(BuildingConflator(min_overlap=0.01).match(reference, candidate)) == 1


def test_the_largest_overlap_wins():
    reference = buildings("dbgt", [square(0, 0)])
    candidate = buildings("bdtre", [square(6, 0), square(1, 0)])

    matches = BuildingConflator().match(reference, candidate)

    assert len(matches) == 1
    assert matches.iloc[0]["candidate_index"] == 1


def test_several_reference_buildings_may_share_one_candidate():
    """The coarser source legitimately describes a whole row of surveyed buildings."""
    reference = buildings("dbgt", [square(0, 0, 8), square(12, 0, 8)])
    candidate = buildings("bdtre", [square(0, 0, 30)])

    matches = BuildingConflator().match(reference, candidate)

    assert sorted(matches["reference_index"]) == [0, 1]
    assert matches["candidate_index"].tolist() == [0, 0]


def test_matching_empty_frames_gives_no_matches():
    reference = buildings("dbgt", [square(0, 0)])
    assert BuildingConflator().match(reference, schema.empty_buildings()).empty
    assert BuildingConflator().match(schema.empty_buildings(), reference).empty


# --- field resolution and provenance ---


def two_source_frames() -> SourceFrames:
    """A reference missing a construction year and a floor count, and a candidate with both."""
    reference = buildings(
        "dbgt",
        [square(0, 0), square(20, 0)],
        usage=["residential", "unknown"],
        height_m=[15.0, None],
        construction_year=pd.array([1950, None], dtype="Int64"),
        n_floors=pd.array([None, None], dtype="Int64"),
    )
    candidate = buildings(
        "bdtre",
        [square(1, 1), square(21, 1)],
        usage=["commercial", "industrial"],
        height_m=[99.0, 18.0],
        construction_year=pd.array([1800, 1975], dtype="Int64"),
        n_floors=pd.array([4, 6], dtype="Int64"),
        status=["costruito", "costruito"],
    )
    return SourceFrames(frames={"dbgt": reference, "bdtre": candidate}, priority=("dbgt", "bdtre"))


def test_conflation_keeps_one_row_per_reference_building():
    source_frames = two_source_frames()
    result = BuildingConflator().conflate(source_frames)

    assert len(result) == len(source_frames.reference)
    assert list(result.columns) == conflated_columns(source_frames.priority)
    assert result["source"].unique().tolist() == ["conflated"]
    assert result["reference_source"].unique().tolist() == ["dbgt"]


def test_the_reference_wins_where_it_has_a_value():
    result = BuildingConflator().conflate(two_source_frames())

    assert result.loc[0, "height_m"] == 15.0
    assert result.loc[0, "construction_year"] == 1950
    assert result.loc[0, "height_m_origin"] == "dbgt"
    assert result.loc[0, "construction_year_origin"] == "dbgt"


def test_the_candidate_fills_what_the_reference_left_empty():
    result = BuildingConflator().conflate(two_source_frames())

    assert result.loc[1, "height_m"] == 18.0
    assert result.loc[1, "construction_year"] == 1975
    assert result.loc[1, "height_m_origin"] == "bdtre"
    assert result.loc[1, "construction_year_origin"] == "bdtre"
    assert result["n_floors"].tolist() == [4, 6]


def test_unknown_usage_counts_as_missing():
    """A source writes 'unknown' when it could not map a value, which is no better than null."""
    result = BuildingConflator().conflate(two_source_frames())

    assert result.loc[0, "usage"] == "residential"
    assert result.loc[1, "usage"] == "industrial"
    assert result.loc[1, "usage_origin"] == "bdtre"


def test_a_field_group_never_splits_across_sources():
    """A construction year must not arrive from one source with its range from another."""
    reference = buildings(
        "dbgt",
        [square(0, 0)],
        construction_year=pd.array([None], dtype="Int64"),
        construction_period=[None],
    )
    candidate = buildings(
        "bdtre",
        [square(1, 1)],
        construction_year=pd.array([1932], dtype="Int64"),
        construction_period=["1919 - 1945"],
        construction_year_from=pd.array([1919], dtype="Int64"),
        construction_year_to=pd.array([1945], dtype="Int64"),
    )
    result = BuildingConflator().conflate(
        SourceFrames(frames={"dbgt": reference, "bdtre": candidate}, priority=("dbgt", "bdtre"))
    )

    assert result.loc[0, "construction_year"] == 1932
    assert result.loc[0, "construction_period"] == "1919 - 1945"
    assert result.loc[0, "construction_year_from"] == 1919
    assert result.loc[0, "construction_year_to"] == 1945


def test_a_monument_flagged_by_either_source_stays_flagged():
    """A source that does not record a monument is not asserting that it is not one."""
    reference = buildings("dbgt", [square(0, 0), square(20, 0)], is_monument=[False, True])
    candidate = buildings("bdtre", [square(1, 1), square(21, 1)], is_monument=[True, False])

    result = BuildingConflator().conflate(
        SourceFrames(frames={"dbgt": reference, "bdtre": candidate}, priority=("dbgt", "bdtre"))
    )

    assert result["is_monument"].tolist() == [True, True]
    assert result["is_monument_origin"].tolist() == ["bdtre", "dbgt"]


def test_filled_values_keep_their_dtype():
    """An integer year taken from another source must not land in an object column."""
    result = BuildingConflator().conflate(two_source_frames())

    assert str(result["construction_year"].dtype) == "Int64"
    assert str(result["n_floors"].dtype) == "Int64"
    assert str(result["height_m"].dtype) in ("float64", "Float64")


def test_every_source_id_and_overlap_is_recorded():
    result = BuildingConflator().conflate(two_source_frames())

    assert result[source_id_column("dbgt")].tolist() == ["dbgt-0", "dbgt-1"]
    assert result[source_id_column("bdtre")].tolist() == ["bdtre-0", "bdtre-1"]
    assert result[overlap_column("bdtre")].notna().all()
    assert result["matched_sources"].tolist() == ["dbgt,bdtre"] * 2


def test_an_unmatched_reference_building_is_kept_and_marked():
    reference = buildings("dbgt", [square(0, 0), square(500, 500)])
    candidate = buildings("bdtre", [square(1, 1)])

    result = BuildingConflator().conflate(
        SourceFrames(frames={"dbgt": reference, "bdtre": candidate}, priority=("dbgt", "bdtre"))
    )

    assert len(result) == 2
    assert result["matched_sources"].tolist() == ["dbgt,bdtre", "dbgt"]
    assert pd.isna(result.loc[1, overlap_column("bdtre")])


def test_reversing_the_priority_reverses_the_unit_of_account():
    source_frames = two_source_frames()
    reversed_frames = SourceFrames(frames=source_frames.frames, priority=("bdtre", "dbgt"))

    result = BuildingConflator().conflate(reversed_frames)

    assert result["reference_source"].unique().tolist() == ["bdtre"]
    assert result.loc[0, "height_m"] == 99.0


def test_empty_reference_gives_an_empty_result_with_the_full_schema():
    priority = ("dbgt", "bdtre")
    source_frames = SourceFrames(
        frames={"dbgt": schema.empty_buildings(), "bdtre": buildings("bdtre", [square(0, 0)])},
        priority=priority,
    )

    result = BuildingConflator().conflate(source_frames)
    assert result.empty
    assert list(result.columns) == conflated_columns(priority)


def test_priority_naming_a_missing_frame_is_rejected():
    with pytest.raises(ValueError):
        SourceFrames(frames={"dbgt": schema.empty_buildings()}, priority=("dbgt", "bdtre"))


def test_match_report_measures_the_match_not_the_fields():
    report = BuildingConflator().match_report(two_source_frames())

    assert report.loc["bdtre", "matched_reference"] == 2
    assert report.loc["bdtre", "matched_reference_share"] == 1.0
    assert report.loc["bdtre", "unmatched_candidates"] == 0


# --- splitting into spatial blocks ---


def grid_frames(count: int = 64) -> SourceFrames:
    """Reference buildings on a line, each with a candidate overlapping it."""
    reference_squares = [square(index * 12, 0) for index in range(count)]
    candidate_squares = [square(index * 12 + 1, 1) for index in range(count)]

    reference = buildings(
        "dbgt",
        reference_squares,
        construction_year=pd.array([None] * count, dtype="Int64"),
    )
    candidate = buildings(
        "bdtre",
        candidate_squares,
        construction_year=pd.array(range(1900, 1900 + count), dtype="Int64"),
    )
    return SourceFrames(frames={"dbgt": reference, "bdtre": candidate}, priority=("dbgt", "bdtre"))


def test_blocks_partition_the_reference_exactly_once():
    """Double counting here would duplicate buildings in the merged result."""
    source_frames = grid_frames()
    blocks = split_source_frames(source_frames, pieces=8, min_rows_per_split=1)

    assert len(blocks) > 1
    total = sum(len(block.reference) for block in blocks)
    assert total == len(source_frames.reference)

    seen = pd.concat([block.reference["building_uuid"] for block in blocks])
    assert seen.is_unique


def test_blocks_keep_the_candidates_their_reference_needs():
    """A match across a block edge must survive the split, or fields go missing."""
    source_frames = grid_frames()
    blocks = split_source_frames(source_frames, pieces=8, min_rows_per_split=1)

    conflator = BuildingConflator()
    matched = 0
    for block in blocks:
        matched += len(conflator.match(block.reference, block.frames["bdtre"]))

    assert matched == len(source_frames.reference)


def test_a_small_job_is_not_split():
    source_frames = grid_frames(count=4)
    assert len(split_source_frames(source_frames, pieces=8, min_rows_per_split=5000)) == 1


def test_parallel_conflation_equals_sequential():
    source_frames = grid_frames()
    conflator = BuildingConflator()

    sequential = Runner(profile=profile(max_cpu_workers=1)).run(conflator.conflate, source_frames)
    parallel = Runner(profile=profile(max_cpu_workers=4, spatial_tile_oversubscribe=2)).run(
        conflator.conflate, source_frames
    )

    assert len(parallel) == len(sequential)

    ordered_sequential = sequential.sort_values("building_uuid").reset_index(drop=True)
    ordered_parallel = parallel.sort_values("building_uuid").reset_index(drop=True)
    for column in conflated_columns(source_frames.priority):
        if column == "geometry":
            continue
        assert ordered_sequential[column].tolist() == ordered_parallel[column].tolist(), column


def test_parallel_conflation_loses_no_provenance():
    """The point of the split is that it changes nothing a caller can observe."""
    source_frames = grid_frames()
    conflator = BuildingConflator()

    parallel = Runner(profile=profile(max_cpu_workers=4, spatial_tile_oversubscribe=2)).run(
        conflator.conflate, source_frames
    )

    for group in CONFLATION_GROUPS:
        if group.name == "construction_year":
            assert (parallel[group.origin_column] == "bdtre").all()
    assert parallel["construction_year"].notna().all()
