"""
Grid Generator Calculator - Assigns a grid_id to a project scenario
Links cim_vector.cim_wizard_project_scenario.grid_id → cim_network.network_scenarios.grid_id
"""
from typing import Optional, Dict, Any

from app.calculators.base_calculator import BaseCalculator


class GridGeneratorCalculator(BaseCalculator):

    def __init__(self, pipeline_executor):
        super().__init__(pipeline_executor)

    def assign_grid(self, project_id: str, scenario_id: str,
                    grid_id: str) -> Optional[Dict[str, Any]]:
        """Assign grid_id to the given project_scenario row."""

        self.log_info(f"Assigning grid_id={grid_id} to project={project_id}, scenario={scenario_id}")

        session = self.data_manager._require_session()
        from sqlalchemy import text

        # Verify grid exists
        row = session.execute(
            text("SELECT grid_id FROM cim_network.network_scenarios WHERE grid_id = :gid"),
            {"gid": grid_id}
        ).fetchone()
        if not row:
            self.log_error(f"grid_id {grid_id} not found in network_scenarios")
            return None

        session.execute(
            text("""
                UPDATE cim_vector.cim_wizard_project_scenario
                SET grid_id = :grid_id, updated_at = now()
                WHERE project_id = :pid AND scenario_id = :sid
            """),
            {"grid_id": grid_id, "pid": project_id, "sid": scenario_id}
        )
        session.commit()

        result = {
            "project_id": project_id,
            "scenario_id": scenario_id,
            "grid_id": grid_id,
            "status": "assigned",
        }
        self.data_manager.set_feature("grid_generator", result)
        self.log_success("assign_grid", f"grid_id={grid_id} assigned")
        return result
