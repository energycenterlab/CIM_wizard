"""
PV Generator Calculator - Spatial join of PV polygons to buildings.

For each building in a project-scenario, finds PV polygons whose geometry
intersects the building footprint.  Updates:
  - cim_vector.pv.building_id  (set once; used as guard against re-assignment)
  - cim_vector.cim_wizard_building.pv_ids  (reverse lookup array)

Idempotent: previous assignments for the scenario are cleared before each run.
"""
from typing import Optional, Dict, Any

from app.calculators.base_calculator import BaseCalculator


class PvGeneratorCalculator(BaseCalculator):

    def __init__(self, pipeline_executor):
        super().__init__(pipeline_executor)

    def assign_pv_to_buildings(
        self, project_id: str, scenario_id: str
    ) -> Optional[Dict[str, Any]]:
        """Spatial join: for each building in the scenario, find intersecting PVs.

        Idempotent — clears any previous assignment for this scenario's buildings
        before running the spatial join, so repeated calls never duplicate data.
        Each PV is assigned to at most one building (first spatial match wins via
        the building_id IS NULL guard).
        """

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
        self.log_info(f"Found {len(building_ids)} buildings — clearing previous PV assignments")

        # ── Reset previous assignments for this scenario ──────────────────────
        # 1. Nullify building_id on PVs that were previously assigned to these buildings
        session.execute(text("""
            UPDATE cim_vector.pv
            SET building_id = NULL, updated_at = now()
            WHERE building_id = ANY(CAST(:bids AS uuid[]))
        """), {"bids": building_ids})

        # 2. Clear pv_ids array on the buildings themselves
        session.execute(text("""
            UPDATE cim_vector.cim_wizard_building
            SET pv_ids = '{}', updated_at = now()
            WHERE building_id = ANY(CAST(:bids AS uuid[]))
        """), {"bids": building_ids})

        # ── Spatial join: only unassigned PVs (building_id IS NULL) ──────────
        # This prevents a PV from being claimed by more than one building.
        matches = session.execute(text("""
            SELECT b.building_id,
                   ARRAY_AGG(pv.pv_id ORDER BY pv.pv_id) AS pv_ids
            FROM cim_vector.cim_wizard_building b
            JOIN cim_vector.pv pv
              ON ST_Intersects(b.building_geometry, pv.pv_geometry)
             AND pv.building_id IS NULL
            WHERE b.building_id = ANY(CAST(:bids AS uuid[]))
            GROUP BY b.building_id
        """), {"bids": building_ids}).fetchall()

        updated = 0
        for row in matches:
            bid = str(row[0])
            pv_ids = [str(p) for p in row[1]]

            # Mark each PV with its owning building
            session.execute(text("""
                UPDATE cim_vector.pv
                SET building_id = CAST(:bid AS uuid), updated_at = now()
                WHERE pv_id = ANY(CAST(:pv_ids AS uuid[]))
                  AND building_id IS NULL
            """), {"bid": bid, "pv_ids": pv_ids})

            # Store the reverse lookup on the building
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
