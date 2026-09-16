"""Build a mosaik world from YAML: classes stay in simulators/, instances come from config."""

from __future__ import annotations

import argparse
from pathlib import Path

import mosaik
import yaml

HERE = Path(__file__).resolve().parent

SIM_CONFIG = {
    "Occupant": {"python": "simulators.occupant:OccupantSim"},
    "Daylight": {"python": "simulators.daylight:DaylightSim"},
    "Curtain": {"python": "simulators.curtain:CurtainSim"},
    "Light": {"python": "simulators.light:LightSim"},
    "Collector": {"python": "simulators.collector:CollectorSim"},
}


def main(config_path: Path | None = None):
    config_path = config_path or HERE / "configs" / "room_week.yaml"
    cfg = yaml.safe_load(config_path.read_text())

    step = int(cfg.get("step_size_s", 3600))
    until = int(cfg.get("days", 7)) * 24 * step
    world = mosaik.World(SIM_CONFIG)

    occupant_sim = world.start("Occupant", step_size=step)
    daylight_sim = world.start("Daylight", step_size=step)
    curtain_sim = world.start("Curtain", step_size=step)
    light_sim = world.start("Light", step_size=step)
    collector_sim = world.start("Collector", step_size=step, out_dir=str(HERE / "output"))
    monitor = collector_sim.Monitor()

    dl = cfg["daylight"]
    daylight = daylight_sim.Daylight.create(
        1,
        eid=dl.get("id", "outdoor"),
        sunrise=dl.get("sunrise", 8),
        sunset=dl.get("sunset", 17),
        noon=dl.get("noon", 12),
        peak_lux=dl.get("peak_lux", 4000),
        cloudy=dl.get("cloudy", True),
    )[0]
    world.connect(daylight, monitor, "is_day", "is_cloudy", "illuminance_lux")

    for room in cfg["rooms"]:
        occupant = occupant_sim.Occupant.create(
            1,
            eid=room["occupant_id"],
            present_hours=room["present_hours"],
        )[0]
        curtain = curtain_sim.Curtain.create(1, eid=f"{room['id']}_curtain")[0]
        light = light_sim.Light.create(1, eid=f"{room['id']}_light")[0]

        world.connect(occupant, curtain, "present")
        world.connect(daylight, curtain, "is_day")
        world.connect(occupant, light, "present")
        world.connect(daylight, light, "is_day", "is_cloudy")

        world.connect(occupant, monitor, "present")
        world.connect(curtain, monitor, "curtain_open")
        world.connect(light, monitor, "light_on")

    world.run(until=until)
    print(f"Done. Config: {config_path}. Outputs: {HERE / 'output'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the room co-simulation from YAML.")
    parser.add_argument(
        "config",
        nargs="?",
        default=str(HERE / "configs" / "room_week.yaml"),
        help="Path to scenario YAML",
    )
    args = parser.parse_args()
    main(Path(args.config))
