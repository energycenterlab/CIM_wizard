"""
The external runner: executes a stateless core method across workers.

The runner is the only place that knows about the compute configuration, worker pools and
splitting. Core classes only declare what may be divided, so the same method runs
unchanged in a notebook cell, in one worker, or across a whole server.

    source = DbgtFootprintSource()
    runner = Runner()                               # reads config/compute.yaml
    buildings = runner.run(source.fetch_buildings, boundary_geojson)

A method with no ``ParallelSpec`` is simply called. Threads are used for network-bound work
and processes for CPU-bound work, because only processes escape the GIL and only they need
to be counted against RAM.
"""

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass, field
import inspect
from typing import Any, Callable, Dict, List, Optional

from city_information_modeler.core.contracts import (
    WORKLOAD_CPU,
    ParallelSpec,
    parallel_spec_of,
)
from city_information_modeler.parallel import splitters
from city_information_modeler.parallel.profile import ComputeProfile, load_profile


@dataclass
class RunReport:
    """What the runner did, so a parallel run can be explained after the fact."""

    method: str
    strategy: str
    workload: str
    workers: int
    pieces: int
    rows_out: Optional[int] = None
    notes: List[str] = field(default_factory=list)

    def describe(self) -> str:
        """One line for a log or a notebook cell."""
        rows = "?" if self.rows_out is None else str(self.rows_out)
        return (
            f"{self.method}: {self.strategy} into {self.pieces} piece(s) on "
            f"{self.workers} {self.workload} worker(s) -> {rows} rows"
        )


class Runner:
    """Runs core methods according to their declaration and this server's capacity."""

    def __init__(
        self,
        profile: Optional[ComputeProfile] = None,
        profile_name: Optional[str] = None,
    ) -> None:
        """
        Args:
            profile: A profile to use directly, mostly for tests.
            profile_name: Name of a profile in ``config/compute.yaml``. Defaults to the
                file's ``active_profile``.
        """
        self.profile = profile or load_profile(profile_name)
        self.last_report: Optional[RunReport] = None

    def run(self, method: Callable, *args: Any, **kwargs: Any) -> Any:
        """Execute a core method, splitting it when it declared that it can be split."""
        spec = parallel_spec_of(method)
        if spec is None or spec.split == "none":
            return self._run_whole(method, spec, args, kwargs)

        bound = self._bind(method, args, kwargs)
        if spec.split_arg not in bound.arguments:
            raise ValueError(
                f"{method.__qualname__} declared split_arg {spec.split_arg!r}, "
                "which was not passed"
            )

        workers = self.profile.workers_for(spec.workload)
        target_pieces = workers * max(1, self.profile.spatial_tile_oversubscribe)

        value = bound.arguments[spec.split_arg]
        pieces = splitters.split_value(value, spec, target_pieces)

        report = RunReport(
            method=method.__qualname__,
            strategy=spec.split,
            workload=spec.workload,
            workers=min(workers, len(pieces)),
            pieces=len(pieces),
        )

        if len(pieces) == 1:
            result = method(*args, **kwargs)
        else:
            results = self._map(method, bound, spec, pieces, report.workers)
            result = splitters.merge_results(results, spec)

        report.rows_out = self._row_count(result)
        self.last_report = report
        return result

    def explain(self, method: Callable, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Describe how a call would be divided, without running anything."""
        spec = parallel_spec_of(method)
        if spec is None or spec.split == "none":
            return {
                "method": method.__qualname__,
                "strategy": "none",
                "workers": 1,
                "pieces": 1,
                "profile": self.profile.describe(),
            }

        bound = self._bind(method, args, kwargs)
        workers = self.profile.workers_for(spec.workload)
        target_pieces = workers * max(1, self.profile.spatial_tile_oversubscribe)
        pieces = splitters.split_value(
            bound.arguments[spec.split_arg], spec, target_pieces
        )

        return {
            "method": method.__qualname__,
            "strategy": spec.split,
            "workload": spec.workload,
            "workers": min(workers, len(pieces)),
            "pieces": len(pieces),
            "merge": spec.merge,
            "profile": self.profile.describe(),
        }

    # --- internals ---

    def _run_whole(
        self,
        method: Callable,
        spec: Optional[ParallelSpec],
        args: tuple,
        kwargs: dict,
    ) -> Any:
        """Call a method that cannot be divided, still recording a report."""
        result = method(*args, **kwargs)
        self.last_report = RunReport(
            method=method.__qualname__,
            strategy="none",
            workload=spec.workload if spec else "unknown",
            workers=1,
            pieces=1,
            rows_out=self._row_count(result),
        )
        return result

    def _map(
        self,
        method: Callable,
        bound: inspect.BoundArguments,
        spec: ParallelSpec,
        pieces: List[Any],
        workers: int,
    ) -> List[Any]:
        """Run one piece per worker and collect the answers in the order of the pieces."""
        calls = []
        for piece in pieces:
            piece_arguments = dict(bound.arguments)
            piece_arguments[spec.split_arg] = piece
            calls.append(piece_arguments)

        executor_class = (
            ProcessPoolExecutor if spec.workload == WORKLOAD_CPU else ThreadPoolExecutor
        )
        with executor_class(max_workers=workers) as executor:
            futures = []
            for piece_arguments in calls:
                futures.append(executor.submit(_invoke, method, piece_arguments))
            return [future.result() for future in futures]

    @staticmethod
    def _bind(method: Callable, args: tuple, kwargs: dict) -> inspect.BoundArguments:
        """Name every argument, so the splitter can find the one it must divide."""
        bound = inspect.signature(method).bind(*args, **kwargs)
        bound.apply_defaults()
        return bound

    @staticmethod
    def _row_count(result: Any) -> Optional[int]:
        try:
            return len(result)
        except TypeError:
            return None


def _invoke(method: Callable, arguments: Dict[str, Any]) -> Any:
    """Module-level call so a process worker can pickle the job."""
    return method(**arguments)
