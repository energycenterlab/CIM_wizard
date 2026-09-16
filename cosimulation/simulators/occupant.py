"""Occupant presence from a per-entity schedule (YAML → create params).

present_hours are half-open windows [start, end) in hour-of-day 0..23.
"""

from __future__ import annotations

import mosaik_api_v3

META = {
    "type": "time-based",
    "models": {
        "Occupant": {
            "public": True,
            "params": ["eid", "present_hours"],
            "attrs": ["present"],
        },
    },
}

DEFAULT_HOURS = [{"start": 8, "end": 13}, {"start": 14, "end": 20}]


def _windows(present_hours) -> list[tuple[int, int]]:
    windows = []
    for item in present_hours or DEFAULT_HOURS:
        if isinstance(item, dict):
            windows.append((int(item["start"]), int(item["end"])))
        else:
            windows.append((int(item[0]), int(item[1])))
    return windows


def is_present(hour: int, windows: list[tuple[int, int]]) -> int:
    return int(any(start <= hour < end for start, end in windows))


class OccupantSim(mosaik_api_v3.Simulator):
    def __init__(self):
        super().__init__(META)
        self.entities: dict[str, dict] = {}
        self.step_size = 3600

    def init(self, sid, time_resolution=1.0, step_size=3600):
        self.sid = sid
        self.step_size = step_size
        return self.meta

    def create(self, num, model, eid=None, present_hours=None):
        if num != 1:
            raise ValueError("Create one Occupant at a time so each can have its own eid/schedule.")
        eid = eid or f"Occupant_{len(self.entities)}"
        if eid in self.entities:
            raise ValueError(f"Duplicate occupant eid: {eid}")
        self.entities[eid] = {
            "present": 0,
            "present_hours": _windows(present_hours),
        }
        return [{"eid": eid, "type": model}]

    def step(self, time, inputs, max_advance):
        hour = (time // 3600) % 24
        for entity in self.entities.values():
            entity["present"] = is_present(hour, entity["present_hours"])
        return time + self.step_size

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {attr: self.entities[eid][attr] for attr in attrs}
        return data
