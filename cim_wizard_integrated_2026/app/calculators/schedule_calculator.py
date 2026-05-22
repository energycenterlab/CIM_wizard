"""
Schedule Calculator — assigns operation/usage schedules per building.

Methods
-------
typical_residential_it
    Apply a typical Italian residential schedule template to every
    residential building in the project-scenario.  Output is a feature dict
    consumed by the IDF exporter and (optionally) the CityDB mapper for
    Energy ADE ``ng2_schedule`` mapping.
"""
from typing import Any, Dict, List, Optional

from app.calculators.base_calculator import BaseCalculator


# ---------------------------------------------------------------------------
# Typical Italian residential schedule templates
# ---------------------------------------------------------------------------
# Values follow common assumptions used in TABULA / UNI/TS 11300 / EnergyPlus
# residential templates: heating Oct–Apr, cooling Jun–Sep, weekday/weekend
# split, DHW base load.  All schedules are 24-hour hourly profiles in [0, 1].

WEEKDAY_OCCUPANCY = [
    1.00, 1.00, 1.00, 1.00, 1.00, 1.00,   # 00..05 night occupancy
    0.90, 0.50, 0.30, 0.20, 0.20, 0.20,   # 06..11 leave for work
    0.30, 0.30, 0.20, 0.20, 0.30, 0.60,   # 12..17 partial return
    0.80, 1.00, 1.00, 1.00, 1.00, 1.00,   # 18..23 evening/night
]

WEEKEND_OCCUPANCY = [
    1.00, 1.00, 1.00, 1.00, 1.00, 1.00,
    1.00, 0.90, 0.80, 0.70, 0.70, 0.70,
    0.80, 0.80, 0.70, 0.70, 0.80, 0.90,
    1.00, 1.00, 1.00, 1.00, 1.00, 1.00,
]

# Heating: 06–08 morning, 18–22 evening (binary on/off pattern)
WEEKDAY_HEATING = [
    0, 0, 0, 0, 0, 0,
    1, 1, 1, 0, 0, 0,
    0, 0, 0, 0, 0, 1,
    1, 1, 1, 1, 1, 0,
]

WEEKEND_HEATING = [
    0, 0, 0, 0, 0, 0,
    1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 0,
]

WEEKDAY_COOLING = [
    0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0,
    1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 0, 0,
]

WEEKEND_COOLING = [
    0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 1,
    1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 0, 0,
]

# Continuous mechanical ventilation, slight day boost
WEEKDAY_VENTILATION = [
    0.30, 0.30, 0.30, 0.30, 0.30, 0.30,
    0.60, 0.60, 0.40, 0.40, 0.40, 0.40,
    0.40, 0.40, 0.40, 0.40, 0.40, 0.50,
    0.60, 0.60, 0.60, 0.40, 0.30, 0.30,
]

WEEKEND_VENTILATION = [
    0.30, 0.30, 0.30, 0.30, 0.30, 0.30,
    0.40, 0.50, 0.60, 0.60, 0.60, 0.60,
    0.60, 0.60, 0.60, 0.50, 0.50, 0.50,
    0.60, 0.60, 0.60, 0.40, 0.30, 0.30,
]

# Typical Italian residential DHW: morning + evening peaks
WEEKDAY_DHW = [
    0.05, 0.05, 0.05, 0.05, 0.05, 0.10,
    0.60, 0.80, 0.50, 0.20, 0.10, 0.20,
    0.40, 0.30, 0.20, 0.20, 0.30, 0.50,
    0.70, 0.80, 0.60, 0.40, 0.20, 0.10,
]

WEEKEND_DHW = [
    0.05, 0.05, 0.05, 0.05, 0.05, 0.10,
    0.30, 0.60, 0.80, 0.70, 0.60, 0.50,
    0.60, 0.60, 0.40, 0.30, 0.40, 0.50,
    0.70, 0.80, 0.60, 0.40, 0.20, 0.10,
]


def _residential_schedule_template() -> Dict[str, Any]:
    return {
        "library_code": "IT_RESIDENTIAL_TYPICAL",
        "calendar": {
            "heating_season": {"start_month": 10, "end_month": 4},
            "cooling_season": {"start_month": 6, "end_month": 9},
            "weekend_days": [5, 6],
        },
        "setpoints": {
            "heating_C": 20.0,
            "heating_setback_C": 16.0,
            "cooling_C": 26.0,
            "cooling_setback_C": 28.0,
            "dhw_C": 45.0,
        },
        "profiles": {
            "occupancy":   {"weekday": WEEKDAY_OCCUPANCY,   "weekend": WEEKEND_OCCUPANCY},
            "heating":     {"weekday": WEEKDAY_HEATING,     "weekend": WEEKEND_HEATING},
            "cooling":     {"weekday": WEEKDAY_COOLING,     "weekend": WEEKEND_COOLING},
            "ventilation": {"weekday": WEEKDAY_VENTILATION, "weekend": WEEKEND_VENTILATION},
            "dhw":         {"weekday": WEEKDAY_DHW,         "weekend": WEEKEND_DHW},
        },
    }


class ScheduleCalculator(BaseCalculator):
    """Assign operation schedules per building (heating, cooling, ventilation, DHW)."""

    def __init__(self, pipeline_executor):
        super().__init__(pipeline_executor)

    # ------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------

    def typical_residential_it(self) -> Optional[Dict[str, Any]]:
        """Apply the typical Italian residential schedule template.

        Reads ``building_geo`` (and optionally ``filter_res``) to identify
        residential buildings and assigns the template to each one.
        Non-residential buildings receive ``None``.  Output is stored as a
        feature for downstream consumers (IDF exporter, CityDB mapper).
        """
        try:
            building_geo = self.get_feature("building_geo")
            if not building_geo:
                self.log_error("No building_geo data available")
                return None

            buildings = building_geo.get("buildings", [])
            if not buildings:
                self.log_error("No buildings in building_geo")
                return None

            filter_res = self.get_feature("filter_res") or {}
            filter_values: List[bool] = filter_res.get("filter_res", []) if isinstance(filter_res, dict) else []

            template = _residential_schedule_template()
            assignments: List[Optional[Dict[str, Any]]] = []
            assigned_count = 0
            for i, b in enumerate(buildings):
                is_res = filter_values[i] if i < len(filter_values) else True
                if is_res:
                    assignments.append({
                        "building_id": b.get("building_id"),
                        "schedule": template,
                    })
                    assigned_count += 1
                else:
                    assignments.append(None)

            result = {
                "project_id": building_geo.get("project_id"),
                "scenario_id": building_geo.get("scenario_id"),
                "method": "typical_residential_it",
                "library_code": template["library_code"],
                "processed_count": len(buildings),
                "assigned_count": assigned_count,
                "template": template,
                "assignments": assignments,
            }
            self.set_feature("schedule", result)
            self.log_success(
                "typical_residential_it",
                f"Assigned residential schedule to {assigned_count}/{len(buildings)} buildings",
            )
            return result
        except Exception as e:
            self.log_failure("typical_residential_it", str(e))
            return None
