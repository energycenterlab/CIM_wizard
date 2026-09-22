"""
Dividing one job into pieces, and putting the pieces back together.

The runner picks a strategy from the ``ParallelSpec`` a core method declared, and the sizes
from the compute profile. Splitting never changes the data; running every piece and merging
gives the same answer as one sequential call.
"""

import math
from typing import Any, Dict, List

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import box

from city_information_modeler.core import boundary as boundary_module
from city_information_modeler.core.conflation import SourceFrames
from city_information_modeler.core.contracts import (
    MERGE_CONCAT,
    MERGE_CONCAT_DEDUP,
    MERGE_NONE,
    ParallelSpec,
)
from city_information_modeler.core.geometry import METRIC_EPSG


def split_value(
    value: Any,
    spec: ParallelSpec,
    pieces: int,
) -> List[Any]:
    """Divide the argument a core method declared as its unit of work."""
    if pieces <= 1:
        return [value]

    if spec.split == "spatial_tiles":
        return boundary_module.split_into_tiles(
            value,
            target_tiles=pieces,
            metric_epsg=METRIC_EPSG,
            min_tile_side_m=spec.min_tile_side_m,
        )

    if spec.split == "row_batches":
        return split_rows(value, pieces, spec.min_rows_per_split)

    if spec.split == "spatial_blocks":
        return split_source_frames(value, pieces, spec.min_rows_per_split)

    return [value]


def split_source_frames(
    source_frames: SourceFrames,
    pieces: int,
    min_rows_per_split: int,
) -> List[SourceFrames]:
    """Divide several related frames along shared spatial blocks.

    Row batches would be wrong here: a reference building can only be matched if the
    candidates near it are in the same piece, and batching each frame independently would
    separate them.

    Two properties make this lossless. Reference buildings are assigned to a block by their
    representative point, so every one lands in exactly one piece and none is counted twice.
    Candidates are then selected by intersecting the bounding box of the reference buildings
    actually assigned to that block, which cannot miss a candidate that overlaps one of them,
    so a match across a block edge still happens.
    """
    reference = source_frames.reference
    total = len(reference)
    if total == 0:
        return [source_frames]

    allowed = max(1, total // max(1, min_rows_per_split))
    pieces = max(1, min(pieces, allowed))
    if pieces == 1:
        return [source_frames]

    block_of_reference = _assign_blocks(reference, pieces)

    divided: List[SourceFrames] = []
    for block in pd.unique(block_of_reference):
        in_block = block_of_reference == block
        reference_block = reference[in_block]
        if reference_block.empty:
            continue

        frames = {source_frames.reference_source: reference_block}
        for source_name in source_frames.enrichment_sources:
            frames[source_name] = _candidates_near(
                source_frames.frames[source_name], reference_block
            )
        divided.append(source_frames.replace(frames))

    if len(divided) <= 1:
        return [source_frames]
    return divided


def _assign_blocks(reference: gpd.GeoDataFrame, pieces: int) -> np.ndarray:
    """Put every reference building in exactly one block of a metric grid.

    The building's representative point decides, so a footprint straddling a block edge is
    still assigned once and only once.
    """
    points = reference.geometry.to_crs(epsg=METRIC_EPSG).representative_point()
    x = points.x.to_numpy()
    y = points.y.to_numpy()

    steps = max(1, int(math.ceil(math.sqrt(pieces))))
    column = _band_index(x, steps)
    row = _band_index(y, steps)
    return row * steps + column


def _band_index(values: np.ndarray, steps: int) -> np.ndarray:
    """Which band of a ``steps``-wide grid each coordinate falls in."""
    lowest = values.min()
    span = values.max() - lowest
    if span <= 0:
        return np.zeros(len(values), dtype=int)

    band = ((values - lowest) / span * steps).astype(int)
    return np.clip(band, 0, steps - 1)


def _candidates_near(
    candidate: gpd.GeoDataFrame,
    reference_block: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Every candidate that could overlap a reference building in this block."""
    if candidate.empty:
        return candidate

    x_min, y_min, x_max, y_max = reference_block.total_bounds
    positions = candidate.geometry.sindex.query(
        box(x_min, y_min, x_max, y_max), predicate="intersects"
    )
    return candidate.iloc[np.sort(positions)]


def split_rows(
    frame: pd.DataFrame,
    pieces: int,
    min_rows_per_split: int,
) -> List[pd.DataFrame]:
    """Cut a frame into row batches, refusing to make them smaller than the minimum."""
    total = len(frame)
    if total == 0:
        return [frame]

    allowed = max(1, total // max(1, min_rows_per_split))
    pieces = max(1, min(pieces, allowed))
    if pieces == 1:
        return [frame]

    batch_size = -(-total // pieces)  # ceiling division

    batches: List[pd.DataFrame] = []
    for start in range(0, total, batch_size):
        batches.append(frame.iloc[start : start + batch_size])
    return batches


def merge_results(results: List[Any], spec: ParallelSpec) -> Any:
    """Recombine the partial answers as the core method declared."""
    if spec.merge == MERGE_NONE:
        return results
    if not results:
        return results

    if len(results) == 1:
        merged = results[0]
    else:
        merged = _concat(results)

    if spec.merge == MERGE_CONCAT_DEDUP and spec.dedup_on:
        merged = _drop_repeats(merged, spec.dedup_on)

    if spec.merge in (MERGE_CONCAT, MERGE_CONCAT_DEDUP) and isinstance(
        merged, pd.DataFrame
    ):
        merged = merged.reset_index(drop=True)
    return merged


def _concat(results: List[Any]) -> Any:
    """Stack frames, keeping the CRS of the first non-empty one."""
    frames = [frame for frame in results if frame is not None]
    if not frames:
        return results

    stacked = pd.concat(frames, ignore_index=True)

    crs = None
    for frame in frames:
        if isinstance(frame, gpd.GeoDataFrame) and frame.crs is not None:
            crs = frame.crs
            break
    if crs is None:
        return stacked
    return gpd.GeoDataFrame(stacked, geometry="geometry", crs=crs)


def _drop_repeats(frame: pd.DataFrame, column: str) -> pd.DataFrame:
    """Drop rows repeated across pieces.

    Spatial tiles overlap at their edges on purpose, so a building touching an edge is read
    by both neighbouring tiles. Without this the merged frame would count it twice.
    """
    if column not in frame.columns:
        raise ValueError(
            f"cannot drop repeats on {column!r}: not a column of the merged result"
        )
    return frame.drop_duplicates(subset=column, keep="first")


def describe_split(value: Any, spec: ParallelSpec, pieces: List[Any]) -> Dict[str, Any]:
    """A small summary of how a job was divided, for logs and notebooks."""
    return {
        "strategy": spec.split,
        "workload": spec.workload,
        "pieces": len(pieces),
        "rows_in": len(value) if isinstance(value, pd.DataFrame) else None,
    }
