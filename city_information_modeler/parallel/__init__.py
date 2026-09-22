"""
The external tool that parallelizes core methods.

It reads ``config/compute.yaml``, sizes its pools from the server's cores and RAM, splits
the work as the core method declared, and merges the pieces. Core code imports nothing from
here.
"""

from city_information_modeler.parallel.profile import (
    ComputeProfile,
    detect_cpu_cores,
    detect_ram_gb,
    load_profile,
)
from city_information_modeler.parallel.runner import Runner, RunReport

__all__ = [
    "ComputeProfile",
    "Runner",
    "RunReport",
    "detect_cpu_cores",
    "detect_ram_gb",
    "load_profile",
]
