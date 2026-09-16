"""Sink that records every connected attribute to CSV + a PNG plot."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import mosaik_api_v3

META = {
    "type": "time-based",
    "models": {
        "Monitor": {
            "public": True,
            "any_inputs": True,
            "params": [],
            "attrs": [],
        },
    },
}


class CollectorSim(mosaik_api_v3.Simulator):
    def __init__(self):
        super().__init__(META)
        self.data: dict[int, dict] = defaultdict(dict)
        self.step_size = 3600
        self.out_dir = Path("output")

    def init(self, sid, time_resolution=1.0, step_size=3600, out_dir="output"):
        self.sid = sid
        self.step_size = step_size
        self.out_dir = Path(out_dir)
        return self.meta

    def create(self, num, model):
        if num != 1:
            raise ValueError("Only one Monitor is supported.")
        return [{"eid": "Monitor", "type": model}]

    def step(self, time, inputs, max_advance):
        row = self.data[time]
        for _eid, attrs in inputs.items():
            for attr, sources in attrs.items():
                for src, value in sources.items():
                    src_eid = src.split(".", 1)[-1]
                    row[f"{src_eid}.{attr}"] = value
        return time + self.step_size

    def get_data(self, outputs):
        return {}

    def finalize(self):
        self.out_dir.mkdir(parents=True, exist_ok=True)
        times = sorted(self.data)
        if not times:
            return
        fieldnames = ["time_s", "hour", "day"] + sorted(
            {k for row in self.data.values() for k in row}
        )
        csv_path = self.out_dir / "room_week.csv"
        with csv_path.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for t in times:
                hour_abs = t // 3600
                writer.writerow(
                    {
                        "time_s": t,
                        "hour": hour_abs % 24,
                        "day": hour_abs // 24,
                        **self.data[t],
                    }
                )
        print(f"Wrote {csv_path}")
        _plot(times, self.data, self.out_dir / "room_week.png")


def _series_ending(data, times, suffix: str) -> dict[str, list]:
    keys = sorted({k for row in data.values() for k in row if k.endswith(suffix)})
    return {k: [data[t].get(k, 0) for t in times] for k in keys}


def _plot(times, data, png_path: Path):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skip plot.")
        return

    hours = [t / 3600 for t in times]
    groups = [
        (".present", "Occupant present"),
        (".is_day", "Daylight (is_day)"),
        (".curtain_open", "Curtain open"),
        (".light_on", "Light on"),
        (".illuminance_lux", "Outdoor illuminance [lux]"),
    ]

    fig, axes = plt.subplots(len(groups), 1, figsize=(12, 10), sharex=True)
    for ax, (suffix, title) in zip(axes, groups):
        series = _series_ending(data, times, suffix)
        for name, values in series.items():
            ax.step(hours, values, where="post", label=name.split(".", 1)[0])
        ax.set_ylabel(title)
        ax.set_ylim(bottom=-0.05)
        if suffix != ".illuminance_lux":
            ax.set_yticks([0, 1])
        if len(series) > 1:
            ax.legend(loc="upper right", fontsize=8)
        ax.grid(True, alpha=0.3)
    axes[-1].set_xlabel("Hour from start")
    axes[0].set_title("Room co-simulation — YAML entities, 1 h step")
    fig.tight_layout()
    fig.savefig(png_path, dpi=120)
    plt.close(fig)
    print(f"Wrote {png_path}")
