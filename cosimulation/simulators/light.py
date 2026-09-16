"""Electric light: occupant turns it on when present and it is cloudy and/or night.

Inputs:  present, is_day, is_cloudy
Output:  light_on
"""

from __future__ import annotations

import mosaik_api_v3

META = {
    "type": "time-based",
    "models": {
        "Light": {
            "public": True,
            "params": ["eid"],
            "attrs": ["present", "is_day", "is_cloudy", "light_on"],
        },
    },
}


class LightSim(mosaik_api_v3.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = "Light_"
        self.entities: dict[str, dict] = {}
        self.step_size = 3600

    def init(self, sid, time_resolution=1.0, step_size=3600):
        self.sid = sid
        self.step_size = step_size
        return self.meta

    def create(self, num, model, eid=None):
        if num != 1:
            raise ValueError("Create one Light at a time.")
        eid = eid or f"{self.eid_prefix}{len(self.entities)}"
        if eid in self.entities:
            raise ValueError(f"Duplicate light eid: {eid}")
        self.entities[eid] = {
            "present": 0,
            "is_day": 0,
            "is_cloudy": 1,
            "light_on": 0,
        }
        return [{"eid": eid, "type": model}]

    def step(self, time, inputs, max_advance):
        for eid, entity in self.entities.items():
            attrs = inputs.get(eid, {})
            present = _first(attrs.get("present"), entity["present"])
            is_day = _first(attrs.get("is_day"), entity["is_day"])
            is_cloudy = _first(attrs.get("is_cloudy"), entity["is_cloudy"])
            entity["present"] = present
            entity["is_day"] = is_day
            entity["is_cloudy"] = is_cloudy
            needs_light = (not is_day) or bool(is_cloudy)
            entity["light_on"] = int(present and needs_light)
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
