"""
Assign census-period archetypes to building rows.

Reference-plus-enrichment again: the footprint sources define what counts as one
building, and these tables only fill in which archetype it belongs to and what
that archetype publishes. No value is averaged across sources and no geometry is
touched, so every attached value still traces to its config table.

The class holds immutable settings only (thresholds come from
``config/archetypes/mapping_rules.yaml`` through the app layer). Every method
takes its divisible work in ``buildings_gdf`` and returns a new frame, so an
external runner may split rows across workers without changing the answer.
"""

from dataclasses import dataclass
from typing import Tuple

import geopandas as gpd
import pandas as pd

from city_information_modeler.core.contracts import (
    MERGE_CONCAT,
    SPLIT_ROW_BATCHES,
    WORKLOAD_CPU,
    parallelizable,
)

PERIOD_ID_COLUMN = "archetype_period_id"
PERIOD_SOURCE_COLUMN = "archetype_period_source"
PERIOD_CONFIDENCE_COLUMN = "archetype_period_confidence"
CLASS_COLUMN = "archetype_class"
CLASS_SOURCE_COLUMN = "archetype_class_source"
CLASS_CONFIDENCE_COLUMN = "archetype_class_confidence"

SOURCE_YEAR_EXACT = "construction_year"
SOURCE_YEAR_MIDPOINT = "construction_year_range_midpoint"
SOURCE_YEAR_CAPPED = "open_lower_bound_capped"
SOURCE_YEAR_MISSING = "missing"

SOURCE_CENSUS = "census_n_dwellings"
SOURCE_FALLBACK = "height_floors_fallback"
SOURCE_NON_RESIDENTIAL = "non_residential_skipped"

CLASS_SFH = "SFH"
CLASS_MFH = "MFH"
CLASS_APARTMENTS = "Apartments"


@dataclass(frozen=True)
class ArchetypeMapper:
    """Map rows onto the census-period archetype tables.

    Frozen so a worker process can hold a copy and give the same answer as any
    other worker. Thresholds mirror ``mapping_rules.yaml``; the app layer builds
    the mapper from that file so the numbers live in exactly one place.
    """

    residential_usages: Tuple[str, ...] = ("residential",)
    mixed_residential_usages: Tuple[str, ...] = (
        "mixed_residential_commercial",
        "mixed_residential_industrial",
        "mixed_residential_public",
    )
    sfh_dwellings: int = 1
    mfh_max_dwellings: int = 8
    sfh_max_floors: int = 1
    sfh_max_height_m: float = 7.5
    mfh_max_floors: int = 3
    mfh_max_height_m: float = 12.0
    n_dwellings_column: str = "n_dwellings"

    @parallelizable(
        split=SPLIT_ROW_BATCHES,
        merge=MERGE_CONCAT,
        workload=WORKLOAD_CPU,
        split_arg="buildings_gdf",
        min_rows_per_split=1000,
    )
    def assign_period(
        self, buildings_gdf: gpd.GeoDataFrame, periods_df: pd.DataFrame
    ) -> gpd.GeoDataFrame:
        """Put each row into one canonical census period (P1-P9).

        Uses ``construction_year`` first, then the midpoint of the published
        range, then the cap of an open lower bound, else leaves the period null.
        """
        result = buildings_gdf.copy()
        years = self._representative_year(result)
        result[PERIOD_ID_COLUMN] = self._period_for_years(
            years["year"].tolist(), periods_df
        ).to_numpy()
        result[PERIOD_SOURCE_COLUMN] = years["source"]
        result[PERIOD_CONFIDENCE_COLUMN] = years["source"].map(
            {
                SOURCE_YEAR_EXACT: "high",
                SOURCE_YEAR_MIDPOINT: "medium",
                SOURCE_YEAR_CAPPED: "low",
                SOURCE_YEAR_MISSING: "missing",
            }
        )
        return result

    @parallelizable(
        split=SPLIT_ROW_BATCHES,
        merge=MERGE_CONCAT,
        workload=WORKLOAD_CPU,
        split_arg="buildings_gdf",
        min_rows_per_split=1000,
    )
    def assign_class(self, buildings_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Put each residential row into SFH, MFH or Apartments.

        Census dwelling counts decide first. Floor count and height are only a
        fallback and stay low confidence. Non-residential rows keep a null class
        so they are visibly skipped, never misclassified.
        """
        result = buildings_gdf.copy()
        is_residential = result["usage"].isin(self.residential_usages)
        is_mixed = result["usage"].isin(self.mixed_residential_usages)

        result[CLASS_COLUMN] = None
        result[CLASS_SOURCE_COLUMN] = SOURCE_NON_RESIDENTIAL
        result[CLASS_CONFIDENCE_COLUMN] = "missing"

        dwellings = self._dwellings(result)
        has_census = dwellings.notna()

        census_class = pd.Series(pd.NA, index=result.index, dtype="string")
        census_class[dwellings == self.sfh_dwellings] = CLASS_SFH
        census_class[
            (dwellings > self.sfh_dwellings)
            & (dwellings <= self.mfh_max_dwellings)
        ] = CLASS_MFH
        census_class[dwellings > self.mfh_max_dwellings] = CLASS_APARTMENTS

        fallback_class = self._fallback_class(result)

        in_scope = is_residential | is_mixed
        result.loc[in_scope & has_census, CLASS_COLUMN] = census_class[
            in_scope & has_census
        ]
        result.loc[in_scope & has_census, CLASS_SOURCE_COLUMN] = SOURCE_CENSUS
        result.loc[in_scope & has_census, CLASS_CONFIDENCE_COLUMN] = "high"

        needs_fallback = in_scope & ~has_census & fallback_class.notna()
        result.loc[needs_fallback, CLASS_COLUMN] = fallback_class[needs_fallback]
        result.loc[needs_fallback, CLASS_SOURCE_COLUMN] = SOURCE_FALLBACK
        result.loc[needs_fallback, CLASS_CONFIDENCE_COLUMN] = "low"

        mixed_fallback = in_scope & is_mixed & has_census
        result.loc[mixed_fallback, CLASS_CONFIDENCE_COLUMN] = (
            "low (mixed use: non-residential share ignored)"
        )
        return result

    @parallelizable(
        split=SPLIT_ROW_BATCHES,
        merge=MERGE_CONCAT,
        workload=WORKLOAD_CPU,
        split_arg="buildings_gdf",
        min_rows_per_split=1000,
    )
    def attach_envelope(
        self, buildings_gdf: gpd.GeoDataFrame, envelope_df: pd.DataFrame
    ) -> gpd.GeoDataFrame:
        """Join the TABULA/URBEM envelope row for each (period, class) pair."""
        return self._attach_reference(
            buildings_gdf, envelope_df, "period_id", "building_class"
        )

    @parallelizable(
        split=SPLIT_ROW_BATCHES,
        merge=MERGE_CONCAT,
        workload=WORKLOAD_CPU,
        split_arg="buildings_gdf",
        min_rows_per_split=1000,
    )
    def attach_systems(
        self, buildings_gdf: gpd.GeoDataFrame, systems_df: pd.DataFrame
    ) -> gpd.GeoDataFrame:
        """Join the URBEM system row for each (period, class) pair."""
        return self._attach_reference(
            buildings_gdf, systems_df, "period_id", "building_class"
        )

    def _representative_year(self, frame: gpd.GeoDataFrame) -> pd.DataFrame:
        """One usable year per row plus where it came from."""
        years = pd.DataFrame(
            {"year": pd.Series(pd.NA, index=frame.index), "source": SOURCE_YEAR_MISSING}
        )
        exact = pd.to_numeric(frame["construction_year"], errors="coerce")
        has_exact = exact.notna()
        years.loc[has_exact, "year"] = exact[has_exact]
        years.loc[has_exact, "source"] = SOURCE_YEAR_EXACT

        year_from = pd.to_numeric(
            frame["construction_year_from"], errors="coerce"
        )
        year_to = pd.to_numeric(frame["construction_year_to"], errors="coerce")

        needs_midpoint = years["year"].isna() & year_from.notna() & year_to.notna()
        midpoints = ((year_from + year_to) // 2).astype("Int64")
        years.loc[needs_midpoint, "year"] = midpoints[needs_midpoint]
        years.loc[needs_midpoint, "source"] = SOURCE_YEAR_MIDPOINT

        needs_cap = years["year"].isna() & year_from.isna() & year_to.notna()
        years.loc[needs_cap, "year"] = year_to[needs_cap]
        years.loc[needs_cap, "source"] = SOURCE_YEAR_CAPPED
        return years

    @staticmethod
    def _period_for_years(
        years, periods_df: pd.DataFrame
    ) -> pd.Series:
        """First canonical period whose year_to holds the year.

        Empty bounds in the periods table mean open ends: P1 starts at minus
        infinity and P9 runs to plus infinity.
        """
        bounds = periods_df.copy()
        bounds["upper"] = pd.to_numeric(bounds["year_to"], errors="coerce")
        bounds["upper"] = bounds["upper"].fillna(float("inf"))
        ordered = bounds.sort_values("upper").reset_index(drop=True)
        assigned = pd.Series(pd.NA, index=range(len(years)), dtype="string")
        year_value = pd.Series(list(years), dtype="Float64")
        for _, period in ordered.iterrows():
            unassigned = assigned.isna()
            inside = year_value <= float(period["upper"])
            assigned[unassigned & inside.fillna(False)] = period["period_id"]
        return assigned

    def _dwellings(self, frame: gpd.GeoDataFrame) -> pd.Series:
        """Census dwelling counts where the column exists, else all missing."""
        if self.n_dwellings_column not in frame.columns:
            return pd.Series(pd.NA, index=frame.index, dtype="Int64")
        return pd.to_numeric(
            frame[self.n_dwellings_column], errors="coerce"
        ).astype("Int64")

    def _fallback_class(self, frame: gpd.GeoDataFrame) -> pd.Series:
        """Height/floor-count class guess used only without census counts."""
        floors = pd.to_numeric(frame["n_floors"], errors="coerce")
        heights = pd.to_numeric(frame["height_m"], errors="coerce")
        guess = pd.Series(pd.NA, index=frame.index, dtype="string")

        is_sfh = (floors <= self.sfh_max_floors) | (
            heights <= self.sfh_max_height_m
        )
        guess[is_sfh.fillna(False)] = CLASS_SFH

        is_mfh = (floors <= self.mfh_max_floors) | (
            heights <= self.mfh_max_height_m
        )
        guess[guess.isna() & is_mfh.fillna(False)] = CLASS_MFH

        is_block = (floors > self.mfh_max_floors) | (
            heights > self.mfh_max_height_m
        )
        guess[guess.isna() & is_block.fillna(False)] = CLASS_APARTMENTS
        return guess

    @staticmethod
    def _attach_reference(
        buildings_gdf: gpd.GeoDataFrame,
        reference_df: pd.DataFrame,
        period_column: str,
        class_column: str,
    ) -> gpd.GeoDataFrame:
        """Left join on (period, class); rows without a pair keep nulls."""
        result = buildings_gdf.copy()
        joined = result.merge(
            reference_df,
            left_on=[PERIOD_ID_COLUMN, CLASS_COLUMN],
            right_on=[period_column, class_column],
            how="left",
        )
        joined = gpd.GeoDataFrame(
            joined, geometry="geometry", crs=buildings_gdf.crs
        )
        return joined
