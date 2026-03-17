"""
PV Generator Calculator - Spatial join of PV polygons to buildings.

For each building in a project-scenario, finds PV polygons whose geometry
intersects the building footprint.  Updates:
  - cim_vector.pv.building_id  (sets the FK for matched PVs)
  - cim_vector.cim_wizard_building.pv_ids  (reverse lookup array)
"""
from typing import Optional, Dict, Any

from app.calculators.base_calculator import BaseCalculator


class PvGeneratorCalculator(BaseCalculator):

    def __init__(self, pipeline_executor):
        super().__init__(pipeline_executor)

    def assign_pv_to_buildings(
        self, project_id: str, scenario_id: str
    ) -> Optional[Dict[str, Any]]:
        """Spatial join: for each building in the scenario, find intersecting PVs."""

        self.log_info(f"PV spatial join for project={project_id}, scenario={scenario_id}")

        session = self.data_manager._require_session()
        from sqlalchemy import text

        building_rows = session.execute(text("""
            SELECT bp.building_id
            FROM cim_vector.cim_wizard_building_properties bp
            WHERE bp.project_id = :pid AND bp.scenario_id = :sid
        """), {"pid": project_id, "sid": scenario_id}).fetchall()

        if not building_rows:
            self.log_warning("No buildings found for this scenario")
            return {"matched": 0, "total_buildings": 0}

        building_ids = [str(r[0]) for r in building_rows]
        self.log_info(f"Found {len(building_ids)} buildings, running spatial join")

        matches = session.execute(text("""
            SELECT b.building_id,
                   ARRAY_AGG(pv.pv_id ORDER BY pv.pv_id) AS pv_ids
            FROM cim_vector.cim_wizard_building b
            JOIN cim_vector.pv pv
              ON ST_Intersects(b.building_geometry, pv.pv_geometry)
            WHERE b.building_id = ANY(CAST(:bids AS uuid[]))
            GROUP BY b.building_id
        """), {"bids": building_ids}).fetchall()

        updated = 0
        for row in matches:
            bid = str(row[0])
            pv_ids = [str(p) for p in row[1]]

            session.execute(text("""
                UPDATE cim_vector.pv
                SET building_id = CAST(:bid AS uuid), updated_at = now()
                WHERE pv_id = ANY(CAST(:pv_ids AS uuid[]))
            """), {"bid": bid, "pv_ids": pv_ids})

            session.execute(text("""
                UPDATE cim_vector.cim_wizard_building
                SET pv_ids = CAST(:pv_ids AS uuid[]), updated_at = now()
                WHERE building_id = CAST(:bid AS uuid)
            """), {"pv_ids": pv_ids, "bid": bid})

            updated += 1

        session.commit()

        result = {
            "project_id": project_id,
            "scenario_id": scenario_id,
            "total_buildings": len(building_ids),
            "buildings_with_pv": updated,
            "status": "completed",
        }
        self.data_manager.set_feature("pv_generator", result)
        self.log_success(
            "assign_pv_to_buildings",
            f"{updated}/{len(building_ids)} buildings matched PV polygons",
        )
        return result
