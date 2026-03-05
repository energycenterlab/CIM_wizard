"""
Building Envelope Efficiency Calculator - Independent class with pipeline executor injection
Assigns random envelope efficiency (low/medium/high) per building.
"""
import random
from typing import Optional, Dict, Any

from app.calculators.base_calculator import BaseCalculator


class EnvelopeEfficiencyCalculator(BaseCalculator):
    """Assign envelope efficiency (low/medium/high) per building"""

    VALID_VALUES = ("low", "medium", "high")

    def __init__(self, pipeline_executor):
        super().__init__(pipeline_executor)

    def assign_random(self) -> Optional[Dict[str, Any]]:
        """Assign random envelope efficiency (low/medium/high) per building"""
        try:
            building_geo = self.pipeline.get_feature_safely(
                "building_geo", calculator_name=self.calculator_name
            )
            if not building_geo:
                self.pipeline.log_error(
                    self.calculator_name, "No building_geo data available"
                )
                return None

            buildings = building_geo.get("buildings", [])
            if not buildings:
                self.pipeline.log_error(
                    self.calculator_name, "No buildings in building_geo"
                )
                return None

            project_id = building_geo.get("project_id")
            scenario_id = building_geo.get("scenario_id")
            if not project_id or not scenario_id:
                self.pipeline.log_error(
                    self.calculator_name,
                    "Missing project_id or scenario_id in building_geo",
                )
                return None

            envelope_values = [random.choice(self.VALID_VALUES) for _ in buildings]

            result = {
                "project_id": project_id,
                "scenario_id": scenario_id,
                "envelope_efficiency": envelope_values,
                "processed_count": len(buildings),
            }
            self.data_manager.set_feature("envelope_efficiency", result)

            # Persist via DataManager
            try:
                self.data_manager.upsert_building_properties_batch(
                    buildings, project_id, scenario_id,
                    "envelope_efficiency", envelope_values,
                )
            except Exception as db_err:
                self.pipeline.log_warning(
                    self.calculator_name, f"DB save failed: {db_err}"
                )

            self.pipeline.log_calculation_success(
                self.calculator_name,
                "assign_random",
                f"Assigned envelope efficiency for {len(buildings)} buildings",
            )
            return result
        except Exception as e:
            self.pipeline.log_calculation_failure(
                self.calculator_name, "assign_random", str(e)
            )
            return None
