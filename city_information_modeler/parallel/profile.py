"""
The compute profile: how much of this machine the runner is allowed to use.

Read from ``config/compute.yaml``. A profile describes the server, not the job, so the same
core code runs on a laptop and on a large server with no edit outside this file.

CPU-bound work is capped by three things at once: the configured ceiling, the cores left
after the reservation, and how many workers the RAM can hold. The smallest wins, which is
what stops a 32-worker pool from exhausting memory on a 16 GB box.
"""

from dataclasses import dataclass
import math
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "compute.yaml"

AUTO = "auto"


@dataclass(frozen=True)
class ComputeProfile:
    """One server's capacity, plus the splitting limits that follow from it."""

    name: str
    cpu_cores: int
    ram_gb: float
    reserve_cores: int
    ram_per_cpu_worker_gb: float
    max_cpu_workers: Optional[int]
    io_workers: int
    spatial_tile_oversubscribe: int
    min_tile_side_m: float
    min_rows_per_split: int

    @property
    def cpu_workers(self) -> int:
        """Process workers for CPU-bound work, limited by cores and by memory."""
        by_cores = self.cpu_cores - self.reserve_cores
        by_memory = math.floor(self.ram_gb / self.ram_per_cpu_worker_gb)

        workers = min(by_cores, by_memory)
        if self.max_cpu_workers is not None:
            workers = min(workers, self.max_cpu_workers)
        return max(1, workers)

    def workers_for(self, workload: str) -> int:
        """Worker count for a workload kind, as declared by a core method."""
        if workload == "io":
            return max(1, self.io_workers)
        return self.cpu_workers

    def describe(self) -> str:
        """One line for a log or a notebook cell."""
        return (
            f"profile={self.name} cores={self.cpu_cores} ram={self.ram_gb:.0f}GB "
            f"cpu_workers={self.cpu_workers} io_workers={self.io_workers}"
        )


def load_profile(
    name: Optional[str] = None,
    config_path: Path = CONFIG_PATH,
) -> ComputeProfile:
    """Read a profile from the compute configuration.

    Args:
        name: Profile to read. Defaults to the file's ``active_profile``.
        config_path: Location of the configuration file.
    """
    with open(config_path, "r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    profiles = config.get("profiles") or {}
    profile_name = name or config.get("active_profile")
    if profile_name not in profiles:
        available = ", ".join(sorted(profiles)) or "none"
        raise ValueError(
            f"compute profile {profile_name!r} not found in {config_path}; "
            f"available: {available}"
        )

    return _build_profile(profile_name, profiles[profile_name])


def detect_cpu_cores() -> int:
    """Cores this process may actually use."""
    if hasattr(os, "sched_getaffinity"):
        return max(1, len(os.sched_getaffinity(0)))
    return max(1, os.cpu_count() or 1)


def detect_ram_gb() -> float:
    """Total physical memory in GB, or a conservative guess when it cannot be read."""
    try:
        page_size = os.sysconf("SC_PAGE_SIZE")
        page_count = os.sysconf("SC_PHYS_PAGES")
        return (page_size * page_count) / (1024**3)
    except (ValueError, OSError, AttributeError):
        return 4.0


def _build_profile(name: str, values: Dict[str, Any]) -> ComputeProfile:
    """Turn one configuration entry into a profile, resolving the `auto` values."""
    cpu_cores = values.get("cpu_cores", AUTO)
    ram_gb = values.get("ram_gb", AUTO)

    return ComputeProfile(
        name=name,
        cpu_cores=detect_cpu_cores() if cpu_cores == AUTO else int(cpu_cores),
        ram_gb=detect_ram_gb() if ram_gb == AUTO else float(ram_gb),
        reserve_cores=int(values.get("reserve_cores", 1)),
        ram_per_cpu_worker_gb=float(values.get("ram_per_cpu_worker_gb", 2.0)),
        max_cpu_workers=(
            None
            if values.get("max_cpu_workers") is None
            else int(values["max_cpu_workers"])
        ),
        io_workers=int(values.get("io_workers", 4)),
        spatial_tile_oversubscribe=int(values.get("spatial_tile_oversubscribe", 2)),
        min_tile_side_m=float(values.get("min_tile_side_m", 250.0)),
        min_rows_per_split=int(values.get("min_rows_per_split", 5000)),
    )
