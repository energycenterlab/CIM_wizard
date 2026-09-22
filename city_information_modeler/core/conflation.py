"""
Conflating several footprint sources into one building per footprint.

The approach is reference-plus-enrichment, not geometry merging. The first source in the
priority order defines what counts as one building and supplies the geometry; the others are
matched to it spatially and fill in the fields it left empty. Nothing is averaged and no new
geometry is invented, so every value in the result can still be traced to the source that
published it.

That choice follows from what the sources are. DBGT is surveyed at building detail, BDTRE is
derived from the cadastre at 1:2000, and their footprints do not correspond one to one: a
single BDTRE polygon often covers several DBGT buildings. Merging the outlines would produce
a geometry neither source stands behind. Picking one as the unit of account keeps the result
honest, and which one is a configuration choice.

Provenance is recorded per field group rather than per column, so fields that only make sense
together cannot be taken from different sources. A construction year never arrives from one
source with its range from another.

Stateless: the class holds immutable settings only, and every method returns new data.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Tuple

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

from city_information_modeler.core import schema
from city_information_modeler.core.contracts import (
    MERGE_CONCAT,
    SPLIT_NONE,
    SPLIT_SPATIAL_BLOCKS,
    WORKLOAD_CPU,
    parallelizable,
)
from city_information_modeler.core.geometry import METRIC_EPSG

CONFLATED_SOURCE_NAME = "conflated"

# Policies for deciding which source supplies a field group.
FILL_MISSING = "fill_missing"  # take the value only where the reference has none
ANY_TRUE = "any_true"  # a flag set by any source wins, since a source may simply not know


@dataclass(frozen=True)
class FieldGroup:
    """Fields that must come from the same source, and how to decide that source."""

    name: str
    fields: Tuple[str, ...]
    policy: str = FILL_MISSING

    @property
    def leader(self) -> str:
        """The field whose presence decides the whole group."""
        return self.fields[0]

    @property
    def origin_column(self) -> str:
        """Column naming the source this group's values came from."""
        return f"{self.name}_origin"


# Grouped so that related fields travel together. Anything not listed here stays as the
# reference published it, which is why identifiers and survey metadata are absent.
CONFLATION_GROUPS: Tuple[FieldGroup, ...] = (
    FieldGroup("usage", ("usage", "usage_raw")),
    FieldGroup("building_type", ("building_type",)),
    FieldGroup("status", ("status",)),
    FieldGroup("name", ("name",)),
    FieldGroup("height_m", ("height_m", "height_source")),
    FieldGroup("n_floors", ("n_floors",)),
    FieldGroup("elevations", ("ground_elevation_m", "eave_elevation_m")),
    FieldGroup(
        "construction_year",
        (
            "construction_year",
            "construction_period",
            "construction_year_from",
            "construction_year_to",
            "construction_year_source",
        ),
    ),
    FieldGroup("is_monument", ("is_monument",), policy=ANY_TRUE),
)

# "unknown" is what a source writes when it mapped a value it does not recognise. For
# conflation it means the same as missing, so another source may still fill it.
EMPTY_USAGE = "unknown"

MATCH_COLUMNS = [
    "reference_index",
    "candidate_index",
    "intersection_m2",
    "overlap_of_reference",
    "intersection_over_union",
]


@dataclass(frozen=True)
class SourceFrames:
    """The frames to conflate, with the priority that decides who wins.

    The first name in ``priority`` is the reference: it defines the buildings and supplies
    the geometry. The rest enrich it, in the order given.

    This travels as one object because the parallel runner has to divide all the frames
    together, along the same spatial blocks, and cannot do that without knowing which frame
    is the reference.
    """

    frames: Mapping[str, gpd.GeoDataFrame]
    priority: Tuple[str, ...]

    def __post_init__(self) -> None:
        if len(self.priority) < 1:
            raise ValueError("priority needs at least the reference source")
        missing = [name for name in self.priority if name not in self.frames]
        if missing:
            raise ValueError(f"no frame given for source(s): {', '.join(missing)}")

    @property
    def reference_source(self) -> str:
        """The source whose footprints define one building."""
        return self.priority[0]

    @property
    def enrichment_sources(self) -> Tuple[str, ...]:
        """The sources that fill in what the reference left empty."""
        return self.priority[1:]

    @property
    def reference(self) -> gpd.GeoDataFrame:
        """The reference frame."""
        return self.frames[self.reference_source]

    def replace(self, frames: Mapping[str, gpd.GeoDataFrame]) -> "SourceFrames":
        """The same priority over a different set of frames, for splitting."""
        return SourceFrames(frames=frames, priority=self.priority)

    def __len__(self) -> int:
        """Number of reference buildings, which is the number of result rows."""
        return len(self.reference)


@dataclass(frozen=True)
class BuildingConflator:
    """Match footprint sources to one another and resolve their fields.

    Args:
        min_overlap: Least share of a reference footprint that a candidate must cover to be
            considered the same building. Guards against slivers where two footprints merely
            touch.
        require_best_match: Keep only the best candidate per reference building. Turning this
            off is only useful for inspecting the raw matches.
    """

    min_overlap: float = 0.3
    require_best_match: bool = True

    @parallelizable(
        split=SPLIT_SPATIAL_BLOCKS,
        merge=MERGE_CONCAT,
        workload=WORKLOAD_CPU,
        split_arg="source_frames",
        min_rows_per_split=2000,
    )
    def conflate(self, source_frames: SourceFrames) -> gpd.GeoDataFrame:
        """Resolve several sources into one building per reference footprint.

        Returns:
            A GeoDataFrame with ``schema.STANDARD_COLUMNS`` plus the provenance columns from
            ``conflated_columns``: which source each field group came from, which sources
            matched at all, and how well they overlapped.
        """
        reference = source_frames.reference.reset_index(drop=True)
        if reference.empty:
            return empty_conflated(source_frames.priority)

        result = self._start_from_reference(reference, source_frames)

        for source_name in source_frames.enrichment_sources:
            candidate = source_frames.frames[source_name].reset_index(drop=True)
            if candidate.empty:
                continue
            result = self._enrich(result, reference, candidate, source_name)

        return result[conflated_columns(source_frames.priority)]

    @parallelizable(split=SPLIT_NONE, merge=MERGE_CONCAT, workload=WORKLOAD_CPU)
    def match(
        self,
        reference_gdf: gpd.GeoDataFrame,
        candidate_gdf: gpd.GeoDataFrame,
    ) -> pd.DataFrame:
        """Pair reference footprints with the candidate footprints covering them.

        Overlaps are measured in EPSG:32632. Several reference buildings may share one
        candidate, which is the normal case when the candidate is the coarser source: one
        cadastral polygon legitimately describes a whole row of surveyed buildings.

        Returns:
            A frame of positional index pairs with their overlap measures, at most one row
            per reference building unless ``require_best_match`` is off.
        """
        if reference_gdf.empty or candidate_gdf.empty:
            return pd.DataFrame(columns=MATCH_COLUMNS)

        reference_metric = reference_gdf.geometry.to_crs(epsg=METRIC_EPSG).reset_index(
            drop=True
        )
        candidate_metric = candidate_gdf.geometry.to_crs(epsg=METRIC_EPSG).reset_index(
            drop=True
        )

        reference_positions, candidate_positions = candidate_metric.sindex.query(
            reference_metric, predicate="intersects"
        )
        if len(reference_positions) == 0:
            return pd.DataFrame(columns=MATCH_COLUMNS)

        reference_geometries = reference_metric.to_numpy()[reference_positions]
        candidate_geometries = candidate_metric.to_numpy()[candidate_positions]

        intersection_area = shapely.area(
            shapely.intersection(reference_geometries, candidate_geometries)
        )
        reference_area = shapely.area(reference_geometries)
        candidate_area = shapely.area(candidate_geometries)
        union_area = reference_area + candidate_area - intersection_area

        matches = pd.DataFrame(
            {
                "reference_index": reference_positions,
                "candidate_index": candidate_positions,
                "intersection_m2": intersection_area,
                "overlap_of_reference": _safe_ratio(intersection_area, reference_area),
                "intersection_over_union": _safe_ratio(intersection_area, union_area),
            }
        )
        matches = matches[matches["overlap_of_reference"] >= self.min_overlap]

        if self.require_best_match:
            matches = matches.sort_values(
                ["reference_index", "intersection_m2"], ascending=[True, False]
            ).drop_duplicates("reference_index", keep="first")

        return matches.reset_index(drop=True)

    def match_report(self, source_frames: SourceFrames) -> pd.DataFrame:
        """How completely each enrichment source matched the reference.

        Read this before trusting a conflation: a low match rate means the sources disagree
        about where buildings are, and no field resolution can repair that.
        """
        reference = source_frames.reference
        rows: List[Dict[str, Any]] = []

        for source_name in source_frames.enrichment_sources:
            candidate = source_frames.frames[source_name]
            matches = self.match(reference, candidate)
            matched_candidates = set(matches["candidate_index"])

            rows.append(
                {
                    "source": source_name,
                    "reference_buildings": len(reference),
                    "candidate_buildings": len(candidate),
                    "matched_reference": len(matches),
                    "matched_reference_share": _share(len(matches), len(reference)),
                    "unmatched_candidates": len(candidate) - len(matched_candidates),
                    "median_overlap": (
                        float(matches["overlap_of_reference"].median())
                        if len(matches)
                        else float("nan")
                    ),
                    "median_iou": (
                        float(matches["intersection_over_union"].median())
                        if len(matches)
                        else float("nan")
                    ),
                }
            )

        return pd.DataFrame(rows).set_index("source")

    # --- internals ---

    def _start_from_reference(
        self,
        reference: gpd.GeoDataFrame,
        source_frames: SourceFrames,
    ) -> gpd.GeoDataFrame:
        """The result before enrichment: the reference, relabelled and given provenance."""
        result = reference[schema.STANDARD_COLUMNS].copy()
        reference_source = source_frames.reference_source

        result["source"] = CONFLATED_SOURCE_NAME
        result["reference_source"] = reference_source
        result["matched_sources"] = reference_source

        for source_name in source_frames.priority:
            column = source_id_column(source_name)
            result[column] = pd.Series(
                pd.NA, index=result.index, dtype="string"
            )
        result[source_id_column(reference_source)] = reference["source_id"].astype("string")

        for source_name in source_frames.enrichment_sources:
            result[overlap_column(source_name)] = pd.Series(
                pd.NA, index=result.index, dtype="Float64"
            )

        for group in CONFLATION_GROUPS:
            present = _has_value(result[group.leader])
            result[group.origin_column] = pd.Series(
                np.where(present, reference_source, pd.NA), index=result.index, dtype="string"
            )

        return result

    def _enrich(
        self,
        result: gpd.GeoDataFrame,
        reference: gpd.GeoDataFrame,
        candidate: gpd.GeoDataFrame,
        source_name: str,
    ) -> gpd.GeoDataFrame:
        """Fill the gaps in the result from one matched source, recording where each came from."""
        matches = self.match(reference, candidate)
        if matches.empty:
            return result

        reference_rows = matches["reference_index"].to_numpy()
        candidate_rows = matches["candidate_index"].to_numpy()

        result.loc[reference_rows, overlap_column(source_name)] = matches[
            "overlap_of_reference"
        ].to_numpy()
        result.loc[reference_rows, source_id_column(source_name)] = (
            candidate["source_id"].astype("string").to_numpy()[candidate_rows]
        )
        result.loc[reference_rows, "matched_sources"] = (
            result.loc[reference_rows, "matched_sources"] + f",{source_name}"
        )

        for group in CONFLATION_GROUPS:
            incoming = _incoming_values(
                candidate, group.fields, reference_rows, candidate_rows, result.index
            )
            taken = self._rows_to_take(result, group, incoming[group.leader])
            if not taken.any():
                continue

            for field in group.fields:
                result[field] = result[field].where(~taken, incoming[field])
            result.loc[taken, group.origin_column] = source_name

        return result

    @staticmethod
    def _rows_to_take(
        result: gpd.GeoDataFrame,
        group: FieldGroup,
        incoming_leader: pd.Series,
    ) -> pd.Series:
        """Which rows should take this group from the candidate, under the group's policy."""
        if group.policy == ANY_TRUE:
            return incoming_leader.fillna(False).astype(bool) & ~result[
                group.leader
            ].fillna(False).astype(bool)

        return ~_has_value(result[group.leader]) & _has_value(incoming_leader)


def conflated_columns(priority: Tuple[str, ...]) -> List[str]:
    """Columns a conflated frame carries: the standard schema plus its provenance."""
    columns = list(schema.STANDARD_COLUMNS)
    columns.append("reference_source")
    columns.append("matched_sources")
    for group in CONFLATION_GROUPS:
        columns.append(group.origin_column)
    for source_name in priority:
        columns.append(source_id_column(source_name))
    for source_name in priority[1:]:
        columns.append(overlap_column(source_name))
    return columns


def empty_conflated(priority: Tuple[str, ...]) -> gpd.GeoDataFrame:
    """An empty conflated result that still carries the full schema."""
    empty = schema.empty_buildings()
    for column in conflated_columns(priority):
        if column not in empty.columns:
            empty[column] = pd.Series([], dtype="string")
    return empty[conflated_columns(priority)]


def source_id_column(source_name: str) -> str:
    """Column holding one source's own identifier for a conflated building."""
    return f"source_id_{source_name}"


def overlap_column(source_name: str) -> str:
    """Column holding how much of the reference footprint that source's match covered."""
    return f"match_overlap_{source_name}"


def _incoming_values(
    candidate: gpd.GeoDataFrame,
    fields: Tuple[str, ...],
    reference_rows: np.ndarray,
    candidate_rows: np.ndarray,
    index: pd.Index,
) -> Dict[str, pd.Series]:
    """Candidate values lined up against the reference rows they matched.

    Reindexing keeps each column's dtype, so an integer year stays an integer instead of
    landing in an object column.
    """
    lined_up: Dict[str, pd.Series] = {}
    for field in fields:
        values = candidate[field].iloc[candidate_rows]
        values.index = pd.Index(reference_rows)
        lined_up[field] = values[~values.index.duplicated()].reindex(index)
    return lined_up


def _has_value(values: pd.Series) -> pd.Series:
    """Whether a field actually carries information.

    A source writes "unknown" where it could not map a value it did read. That is no more
    informative than a null, so another source is allowed to fill it.
    """
    present = values.notna()
    if values.dtype == "object" or str(values.dtype) == "string":
        present = present & (values.astype("string") != EMPTY_USAGE)
    return present


def _safe_ratio(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    """Ratio that returns zero instead of failing on a zero-area footprint."""
    return np.divide(
        numerator,
        denominator,
        out=np.zeros_like(numerator, dtype=float),
        where=denominator > 0,
    )


def _share(count: int, total: int) -> Optional[float]:
    """Fraction, or None when there is nothing to divide by."""
    if total == 0:
        return None
    return count / total
