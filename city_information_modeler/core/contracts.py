"""
The contract between a stateless core method and the external parallel runner.

A core method stays an ordinary method: calling it directly runs the whole job in one
process, which is what a notebook wants. The ``parallelizable`` decorator only attaches a
``ParallelSpec`` describing how the work may be divided. The runner in ``parallel/`` reads
that description and decides, from the server's cores and RAM, whether and how far to
split. Core code never reads the compute configuration and never starts a worker.

To honour the contract a method must:

- keep no state on the instance and mutate no argument, so a worker can call it on a
  fresh copy and get the same answer;
- take its divisible work in one named argument, so the runner knows what to split;
- return a value whose parts can be recombined by the declared merge strategy.
"""

from dataclasses import dataclass
from typing import Any, Callable, Optional

# How the runner may divide the work.
SPLIT_SPATIAL_TILES = "spatial_tiles"  # split a boundary geometry into a grid of tiles
SPLIT_ROW_BATCHES = "row_batches"  # split a GeoDataFrame into batches of rows
SPLIT_SPATIAL_BLOCKS = "spatial_blocks"  # split several related frames along shared blocks
SPLIT_NONE = "none"  # indivisible, always runs in one worker

SPLIT_STRATEGIES = (
    SPLIT_SPATIAL_TILES,
    SPLIT_ROW_BATCHES,
    SPLIT_SPATIAL_BLOCKS,
    SPLIT_NONE,
)

# How the runner puts the partial answers back together.
MERGE_CONCAT = "concat"  # stack the frames in order
MERGE_CONCAT_DEDUP = "concat_dedup"  # stack, then drop rows repeated across splits
MERGE_NONE = "none"  # return the list of partial answers untouched

MERGE_STRATEGIES = (MERGE_CONCAT, MERGE_CONCAT_DEDUP, MERGE_NONE)

# What the method spends its time on, which decides threads against processes.
WORKLOAD_IO = "io"  # network or disk bound: many threads, not limited by cores
WORKLOAD_CPU = "cpu"  # geometry or numeric work: processes, limited by cores and RAM

WORKLOADS = (WORKLOAD_IO, WORKLOAD_CPU)


@dataclass(frozen=True)
class ParallelSpec:
    """How one core method may be divided across workers."""

    split: str
    merge: str
    workload: str
    split_arg: str
    dedup_on: Optional[str] = None
    min_rows_per_split: int = 1
    min_tile_side_m: float = 250.0

    def __post_init__(self) -> None:
        if self.split not in SPLIT_STRATEGIES:
            raise ValueError(f"unknown split strategy: {self.split!r}")
        if self.merge not in MERGE_STRATEGIES:
            raise ValueError(f"unknown merge strategy: {self.merge!r}")
        if self.workload not in WORKLOADS:
            raise ValueError(f"unknown workload: {self.workload!r}")
        if self.merge == MERGE_CONCAT_DEDUP and not self.dedup_on:
            raise ValueError("merge 'concat_dedup' needs dedup_on")
        if self.split != SPLIT_NONE and not self.split_arg:
            raise ValueError(f"split {self.split!r} needs split_arg")


def parallelizable(
    split: str,
    merge: str,
    workload: str,
    split_arg: str = "",
    dedup_on: Optional[str] = None,
    min_rows_per_split: int = 1,
    min_tile_side_m: float = 250.0,
) -> Callable:
    """Declare how a stateless core method may be parallelized.

    The method is returned unchanged, so a direct call still runs the whole job in this
    process. Only the description is attached.
    """
    spec = ParallelSpec(
        split=split,
        merge=merge,
        workload=workload,
        split_arg=split_arg,
        dedup_on=dedup_on,
        min_rows_per_split=min_rows_per_split,
        min_tile_side_m=min_tile_side_m,
    )

    def decorate(method: Callable) -> Callable:
        method.parallel_spec = spec
        return method

    return decorate


def parallel_spec_of(method: Any) -> Optional[ParallelSpec]:
    """The ParallelSpec a method declared, or None when it declared none."""
    return getattr(method, "parallel_spec", None)
