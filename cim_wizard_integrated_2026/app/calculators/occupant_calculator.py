"""
Occupant Calculator — assigns occupant counts and heat gains per building.

Methods
-------
typical_residential_it
    Apply typical Italian residential occupancy assumptions: total occupants
    come from ``n_people`` (already calculated by the demographic pipeline),
    occupant heat dissipation defaults follow UNI/TS 11300 and ISO 7730.
"""
from typing import Any, Dict, List, Optional

from app.calculators.base_calculator import BaseCalculator


# Typical Italian residential occupant heat gains (UNI/TS 11300, ISO 7730)
DEFAULT_HEAT_DISS_W            = 120.0   # total heat dissipation per occupant
DEFAULT_HEAT_DISS_CONV_W       =  60.0   # convective component
DEFAULT_HEAT_DISS_LAT_W        =  40.0   # latent component
DEFAULT_HEAT_DISS_RAD_W        =  20.0   # radiative component
DEFAULT_METABOLIC_RATE_W_M2    =  70.0   # metabolic rate at rest

# Average diet/income proxies (placeholders; can be tuned per scenario)
DEFAULT_AVG_DIET_TYPE          = "mixed-mediterranean"
DEFAULT_AVG_INCOME_LEVEL       = "medium"


def _occupant_template(num_people: int, num_family: int) -> Dict[str, Any]:
    return {
        "library_code": "IT_RESIDENTIAL_TYPICAL",
        "num_of_occupants": int(num_people) if num_people is not None else 0,
        "num_of_families": int(num_family) if num_family is not None else 0,
        "heat_dissipation_W": DEFAULT_HEAT_DISS_W,
        "heat_dissipation_uom": "W",
        "heat_dissipation_convective_W": DEFAULT_HEAT_DISS_CONV_W,
        "heat_dissipation_convective_uom": "W",
        "heat_dissipation_latent_W": DEFAULT_HEAT_DISS_LAT_W,
        "heat_dissipation_latent_uom": "W",
        "heat_dissipation_radiative_W": DEFAULT_HEAT_DISS_RAD_W,
        "heat_dissipation_radiative_uom": "W",
        "metabolic_rate_W_m2": DEFAULT_METABOLIC_RATE_W_M2,
        "avg_diet_type": DEFAULT_AVG_DIET_TYPE,
        "avg_income_level": DEFAULT_AVG_INCOME_LEVEL,
    }


class OccupantCalculator(BaseCalculator):
    """Assign occupant counts and typical heat-gain templates per building."""

    def __init__(self, pipeline_executor):
        super().__init__(pipeline_executor)

    # ------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------

    def typical_residential_it(self) -> Optional[Dict[str, Any]]:
        """Apply typical Italian residential occupant template.

        Reads ``building_geo``, ``building_population`` (n_people) and
        ``building_n_families`` (n_family) and produces one occupant
        template per residential building.  Non-residential buildings get
        ``None``.
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

            population = self.get_feature("building_population") or {}
            families = self.get_feature("building_n_families") or {}
            filter_res = self.get_feature("filter_res") or {}

            n_people_list: List[Any] = (
                population.get("n_people") or population.get("values") or []
                if isinstance(population, dict) else []
            )
            n_family_list: List[Any] = (
                families.get("n_family") or families.get("values") or []
                if isinstance(families, dict) else []
            )
            filter_values: List[bool] = (
                filter_res.get("filter_res", []) if isinstance(filter_res, dict) else []
            )

            assignments: List[Optional[Dict[str, Any]]] = []
            assigned_count = 0
            for i, b in enumerate(buildings):
                is_res = filter_values[i] if i < len(filter_values) else True
                if not is_res:
                    assignments.append(None)
                    continue
                np_i = n_people_list[i] if i < len(n_people_list) else None
                nf_i = n_family_list[i] if i < len(n_family_list) else None
                assignments.append({
                    "building_id": b.get("building_id"),
                    "occupants": _occupant_template(np_i or 0, nf_i or 0),
                })
                assigned_count += 1

            result = {
                "project_id": building_geo.get("project_id"),
                "scenario_id": building_geo.get("scenario_id"),
                "method": "typical_residential_it",
                "library_code": "IT_RESIDENTIAL_TYPICAL",
                "processed_count": len(buildings),
                "assigned_count": assigned_count,
                "assignments": assignments,
            }
            self.set_feature("occupants", result)
            self.log_success(
                "typical_residential_it",
                f"Assigned residential occupants to {assigned_count}/{len(buildings)} buildings",
            )
            return result
        except Exception as e:
            self.log_failure("typical_residential_it", str(e))
            return None
