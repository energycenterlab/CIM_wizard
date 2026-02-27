"""
Building Envelope Efficiency Calculator - Independent class with pipeline executor injection
Assigns random envelope efficiency (low/medium/high) per building.
"""
import random
from typing import Optional, Dict, Any
from sqlalchemy import and_


class EnvelopeEfficiencyCalculator:
    """Assign envelope efficiency (low/medium/high) per building"""

    VALID_VALUES = ("low", "medium", "high")

    def __init__(self, pipeline_executor):
        self.pipeline = pipeline_executor
        self.data_manager = pipeline_executor.data_manager
        self.calculator_name = self.__class__.__name__

    def assign_random(self) -> Optional[Dict[str, Any]]:
        """Assign random envelope efficiency (low/medium/high) per building and save to BuildingProperties"""
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

            envelope_values = []
            for building in buildings:
                value = random.choice(self.VALID_VALUES)
                envelope_values.append(value)

            self.data_manager.set_feature(
                "envelope_efficiency",
                {
                    "project_id": project_id,
                    "scenario_id": scenario_id,
                    "envelope_efficiency": envelope_values,
                },
            )

            db_session = getattr(self.data_manager, "db_session", None)
            if db_session:
                self._save_to_database(
                    db_session, buildings, envelope_values, project_id, scenario_id
                )

            self.pipeline.log_calculation_success(
                self.calculator_name,
                "assign_random",
                f"Assigned envelope efficiency for {len(buildings)} buildings",
            )
            return {
                "project_id": project_id,
                "scenario_id": scenario_id,
                "envelope_efficiency": envelope_values,
                "processed_count": len(buildings),
            }
        except Exception as e:
            self.pipeline.log_calculation_failure(
                self.calculator_name, "assign_random", str(e)
            )
            return None

    def _save_to_database(
        self, db_session, buildings, envelope_values, project_id, scenario_id
    ):
        """Save envelope efficiency to BuildingProperties for each building"""
        try:
            from app.models.vector import BuildingProperties

            updated_count = 0
            for building, value in zip(buildings, envelope_values):
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
                    props.envelope_efficiency = value
                    db_session.add(props)
                    updated_count += 1

            if updated_count > 0:
                db_session.commit()
                db_session.flush()
                self.pipeline.log_info(
                    self.calculator_name,
                    f"Saved envelope_efficiency for {updated_count} buildings",
                )
        except Exception as e:
            db_session.rollback()
            self.pipeline.log_error(
                self.calculator_name, f"Failed to save envelope_efficiency: {str(e)}"
            )
            raise
