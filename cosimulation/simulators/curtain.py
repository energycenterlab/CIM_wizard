"""Curtain: occupant opens it fully when present and there is daylight.

Inputs:  present, is_day
Output:  curtain_open  (1 = fully open, 0 = closed)
"""

from __future__ import annotations

import mosaik_api_v3

META = {
    "type": "time-based",
    "models": {
        "Curtain": {
            "public": True,
            "params": ["eid"],
            "attrs": ["present", "is_day", "curtain_open"],
        },
    },
}


class CurtainSim(mosaik_api_v3.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = "Curtain_"
        self.entities: dict[str, dict] = {}
        self.step_size = 3600

    def init(self, sid, time_resolution=1.0, step_size=3600):
        self.sid = sid
        self.step_size = step_size
        return self.meta

    def create(self, num, model, eid=None):
        if num != 1:
            raise ValueError("Create one Curtain at a time.")
        eid = eid or f"{self.eid_prefix}{len(self.entities)}"
        if eid in self.entities:
            raise ValueError(f"Duplicate curtain eid: {eid}")
        self.entities[eid] = {"present": 0, "is_day": 0, "curtain_open": 0}
        return [{"eid": eid, "type": model}]

    def step(self, time, inputs, max_advance):
        for eid, entity in self.entities.items():
            attrs = inputs.get(eid, {})
            present = _first(attrs.get("present"), entity["present"])
            is_day = _first(attrs.get("is_day"), entity["is_day"])
            entity["present"] = present
            entity["is_day"] = is_day
            entity["curtain_open"] = int(present and is_day)
        return time + self.step_size

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {attr: self.entities[eid][attr] for attr in attrs}
        return data


def _first(src, default):
    if not src:
        return default
    return next(iter(src.values()))
