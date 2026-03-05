"""
FMU Assign Calculator - Assigns FMU file identifier to building properties
"""
from typing import Optional, Dict, Any

from app.calculators.base_calculator import BaseCalculator


class FmuAssignCalculator(BaseCalculator):
    """Assign FMU file identifier to building properties"""

    def __init__(self, pipeline_executor):
        super().__init__(pipeline_executor)

    def frassinetto(self) -> Optional[Dict[str, Any]]:
        """Assign the string 'frassinetto' to fmu_file for all building-scenarios"""
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

            value = "frassinetto"
            result = {
                "project_id": project_id,
                "scenario_id": scenario_id,
                "fmu_file": value,
                "processed_count": len(buildings),
            }
            self.data_manager.set_feature("fmu_assign", result)

            # Persist via DataManager
            try:
                values = [value] * len(buildings)
                self.data_manager.upsert_building_properties_batch(
                    buildings, project_id, scenario_id, "fmu_file", values,
                )
            except Exception as db_err:
                self.pipeline.log_warning(
                    self.calculator_name, f"DB save failed: {db_err}"
                )

            self.pipeline.log_calculation_success(
                self.calculator_name,
                "frassinetto",
                f"Assigned fmu_file='{value}' for {len(buildings)} buildings",
            )
            return result
        except Exception as e:
            self.pipeline.log_calculation_failure(
                self.calculator_name, "frassinetto", str(e)
            )
            return None
