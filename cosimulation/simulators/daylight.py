"""Winter daylight as a toy equation; sunrise/sunset/cloudiness are create params."""

from __future__ import annotations

import mosaik_api_v3

META = {
    "type": "time-based",
    "models": {
        "Daylight": {
            "public": True,
            "params": ["eid", "sunrise", "sunset", "noon", "peak_lux", "cloudy"],
            "attrs": ["is_day", "is_cloudy", "illuminance_lux"],
        },
    },
}


def illuminance_lux(hour: int, sunrise, sunset, noon, peak_lux) -> float:
    if hour < sunrise or hour >= sunset:
        return 0.0
    half = max(noon - sunrise, sunset - noon)
    factor = 1.0 - abs(hour + 0.5 - noon) / half
    return max(0.0, peak_lux * factor)


class DaylightSim(mosaik_api_v3.Simulator):
    def __init__(self):
        super().__init__(META)
        self.entities: dict[str, dict] = {}
        self.step_size = 3600

    def init(self, sid, time_resolution=1.0, step_size=3600):
        self.sid = sid
        self.step_size = step_size
        return self.meta

    def create(
        self,
        num,
        model,
        eid=None,
        sunrise=8,
        sunset=17,
        noon=12,
        peak_lux=4000,
        cloudy=True,
    ):
        if num != 1:
            raise ValueError("Create one Daylight entity at a time.")
        eid = eid or f"Daylight_{len(self.entities)}"
        if eid in self.entities:
            raise ValueError(f"Duplicate daylight eid: {eid}")
        self.entities[eid] = {
            "sunrise": int(sunrise),
            "sunset": int(sunset),
            "noon": float(noon),
            "peak_lux": float(peak_lux),
            "cloudy": int(bool(cloudy)),
            "is_day": 0,
            "is_cloudy": int(bool(cloudy)),
            "illuminance_lux": 0.0,
        }
        return [{"eid": eid, "type": model}]

    def step(self, time, inputs, max_advance):
        hour = (time // 3600) % 24
        for entity in self.entities.values():
            lux = illuminance_lux(
                hour,
                entity["sunrise"],
                entity["sunset"],
                entity["noon"],
                entity["peak_lux"],
            )
            entity["illuminance_lux"] = lux
            entity["is_day"] = int(lux > 0)
            entity["is_cloudy"] = entity["cloudy"]
        return time + self.step_size

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {attr: self.entities[eid][attr] for attr in attrs}
        return data
