"""
Archetype mapping on recorded values, so the rules hold without live sources.

Periods follow the census (P1-P9); classes are SFH/MFH/Apartments with TH
deliberately unused. The frames below carry the columns the mapper reads.
"""

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box

from city_information_modeler.app.archetype_assignment import (
    assign_archetypes,
    load_references,
)
from city_information_modeler.core.archetypes import ArchetypeMapper
from city_information_modeler.parallel import Runner


def archetype_frame(rows):
    """A frame shaped like conflated footprints with census counts attached."""
    geometries = []
    for index in range(len(rows)):
        geometries.append(
            box(7.64 + index * 0.001, 45.02, 7.641 + index * 0.001, 45.021)
        )
    frame = pd.DataFrame(rows)
    return gpd.GeoDataFrame(frame, geometry=geometries, crs="EPSG:4326")


BASE_ROW = {
    "usage": "residential",
    "construction_year": 1965,
    "construction_year_from": 1961,
    "construction_year_to": 1970,
    "n_floors": 5,
    "height_m": 15.0,
    "n_dwellings": 20,
}

REFERENCES = load_references()
PERIODS = REFERENCES["periods"]
ENVELOPE = REFERENCES["envelope_archetypes"]
SYSTEMS = REFERENCES["systems"]


@pytest.mark.parametrize(
    "year,expected_period",
    [
        (1850, "P1"),
        (1918, "P1"),
        (1930, "P2"),
        (1950, "P3"),
        (1965, "P4"),
        (1978, "P5"),
        (1985, "P6"),
        (1995, "P7"),
        (2003, "P8"),
        (2015, "P9"),
    ],
)
def test_exact_years_hit_the_census_period(year, expected_period):
    row = dict(BASE_ROW, construction_year=year)
    result = ArchetypeMapper().assign_period(archetype_frame([row]), PERIODS)
    assert result.loc[0, "archetype_period_id"] == expected_period
    assert result.loc[0, "archetype_period_source"] == "construction_year"
    assert result.loc[0, "archetype_period_confidence"] == "high"


def test_range_without_representative_uses_its_midpoint():
    row = dict(
        BASE_ROW,
        construction_year=None,
        construction_year_from=1971,
        construction_year_to=1980,
    )
    result = ArchetypeMapper().assign_period(archetype_frame([row]), PERIODS)
    assert result.loc[0, "archetype_period_id"] == "P5"
    assert (
        result.loc[0, "archetype_period_source"]
        == "construction_year_range_midpoint"
    )


def test_open_lower_bound_uses_its_cap_with_low_confidence():
    row = dict(
        BASE_ROW,
        construction_year=None,
        construction_year_from=None,
        construction_year_to=1918,
    )
    result = ArchetypeMapper().assign_period(archetype_frame([row]), PERIODS)
    assert result.loc[0, "archetype_period_id"] == "P1"
    assert result.loc[0, "archetype_period_confidence"] == "low"


def test_missing_year_stays_null():
    row = dict(
        BASE_ROW,
        construction_year=None,
        construction_year_from=None,
        construction_year_to=None,
    )
    result = ArchetypeMapper().assign_period(archetype_frame([row]), PERIODS)
    assert pd.isna(result.loc[0, "archetype_period_id"])


@pytest.mark.parametrize(
    "dwellings,expected_class",
    [(1, "SFH"), (2, "MFH"), (8, "MFH"), (9, "Apartments"), (40, "Apartments")],
)
def test_census_counts_decide_the_class(dwellings, expected_class):
    row = dict(BASE_ROW, n_dwellings=dwellings)
    result = ArchetypeMapper().assign_class(archetype_frame([row]))
    assert result.loc[0, "archetype_class"] == expected_class
    assert result.loc[0, "archetype_class_source"] == "census_n_dwellings"


def test_height_fallback_is_low_confidence_without_census():
    row = dict(BASE_ROW, n_dwellings=None, n_floors=1, height_m=6.0)
    result = ArchetypeMapper().assign_class(archetype_frame([row]))
    assert result.loc[0, "archetype_class"] == "SFH"
    assert result.loc[0, "archetype_class_confidence"] == "low"


def test_non_residential_rows_are_skipped_not_misclassified():
    row = dict(BASE_ROW, usage="industrial")
    result = ArchetypeMapper().assign_class(archetype_frame([row]))
    assert pd.isna(result.loc[0, "archetype_class"])
    assert (
        result.loc[0, "archetype_class_source"] == "non_residential_skipped"
    )


def test_envelope_join_keeps_tabula_u_values():
    row = dict(BASE_ROW)  # 1965, 20 dwellings -> P4 Apartments -> AB_05
    frame = archetype_frame([row])
    mapper = ArchetypeMapper()
    result = mapper.attach_envelope(
        mapper.assign_class(mapper.assign_period(frame, PERIODS)), ENVELOPE
    )
    assert result.loc[0, "tabula_archetype"] == "AB_05"
    assert result.loc[0, "u_wall_primary"] == pytest.approx(1.086, abs=0.001)
    assert result.loc[0, "window_u_mean"] == pytest.approx(3.38, abs=0.01)


def test_sfh_rows_keep_windows_empty():
    row = dict(BASE_ROW, n_dwellings=1)  # P4 SFH -> SFH_05, no window source
    frame = archetype_frame([row])
    mapper = ArchetypeMapper()
    result = mapper.attach_envelope(
        mapper.assign_class(mapper.assign_period(frame, PERIODS)), ENVELOPE
    )
    assert result.loc[0, "tabula_archetype"] == "SFH_05"
    assert pd.isna(result.loc[0, "window_u_mean"])


def test_splitting_rows_does_not_change_the_answer():
    rows = [dict(BASE_ROW, construction_year=year) for year in (1930, 1985, 2015)]
    frame = archetype_frame(rows)
    mapper = ArchetypeMapper()
    whole = mapper.assign_period(frame, PERIODS)
    parts = [
        mapper.assign_period(frame.iloc[[0]], PERIODS),
        mapper.assign_period(frame.iloc[[1, 2]], PERIODS),
    ]
    batched = pd.concat(parts, ignore_index=True)
    assert (
        batched["archetype_period_id"].tolist()
        == whole["archetype_period_id"].tolist()
    )


def test_full_app_pipeline_runs_offline():
    rows = [
        dict(BASE_ROW, construction_year=1930, n_dwellings=1),
        dict(BASE_ROW, construction_year=2003, n_dwellings=25),
        dict(BASE_ROW, usage="industrial"),
    ]
    sequential = Runner(profile_name="sequential")
    result = assign_archetypes(archetype_frame(rows), runner=sequential)
    assert result.loc[0, "tabula_archetype"] == "SFH_03"
    assert result.loc[1, "tabula_archetype"] == "AB_07"
    assert pd.isna(result.loc[2, "archetype_class"])
