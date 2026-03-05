"""
FMU Assign Calculator - Assigns FMU file identifier to building properties
"""
from typing import Optional, Dict, Any
from sqlalchemy import and_

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
            self.data_manager.set_feature(
                "fmu_assign",
                {
                    "project_id": project_id,
                    "scenario_id": scenario_id,
                    "fmu_file": value,
                    "processed_count": len(buildings),
                },
            )

            db_session = getattr(self.data_manager, "db_session", None)
            if db_session:
                self._save_to_database(
                    db_session, buildings, value, project_id, scenario_id
                )

            self.pipeline.log_calculation_success(
                self.calculator_name,
                "frassinetto",
                f"Assigned fmu_file='{value}' for {len(buildings)} buildings",
            )
            return {
                "project_id": project_id,
                "scenario_id": scenario_id,
                "fmu_file": value,
                "processed_count": len(buildings),
            }
        except Exception as e:
            self.pipeline.log_calculation_failure(
                self.calculator_name, "frassinetto", str(e)
            )
            return None

    def _save_to_database(
        self, db_session, buildings, value, project_id, scenario_id
    ):
        """Save fmu_file to BuildingProperties for each building"""
        try:
            from app.models.vector import BuildingProperties

            updated_count = 0
            for building in buildings:
                building_id = building.get("building_id")
                if not building_id:
                    continue
                lod = building.get("lod", 0)

                props = db_session.query(BuildingProperties).filter(
                    and_(
                        BuildingProperties.building_id == building_id,
                        BuildingProperties.project_id == project_id,
                        BuildingProperties.scenario_id == scenario_id,
                        BuildingProperties.lod == lod,
                    )
                ).first()

                if props:
                    props.fmu_file = value
                    db_session.add(props)
                    updated_count += 1

            if updated_count > 0:
                db_session.commit()
                db_session.flush()
                self.pipeline.log_info(
                    self.calculator_name,
                    f"Saved fmu_file for {updated_count} buildings",
                )
        except Exception as e:
            db_session.rollback()
            self.pipeline.log_error(
                self.calculator_name, f"Failed to save fmu_file: {str(e)}"
            )
            raise
