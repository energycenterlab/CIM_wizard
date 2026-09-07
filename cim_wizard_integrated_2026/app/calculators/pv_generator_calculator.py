"""
PV Generator Calculator - offset spatial join of PV polygons to buildings.

The PV polygons for Torino are digitised from building *roofprints*, while
``cim_wizard_building.building_geometry`` holds *footprints*.  Roofs overhang,
so a plain ST_Intersects misses polygons that sit just outside the footprint.
The join therefore uses a metric tolerance (``offset_m``) and ranks candidates
by the overlap against the buffered footprint.

Writes, all scoped to one project-scenario:
  - cim_vector.cim_wizard_building_properties.pv      -- pv_id list per building
  - cim_vector.pv.scenario_id                         -- scenarios using each PV
  - cim_vector.cim_wizard_project_scenario.pv_assigned

Idempotent: the scenario's previous assignments are withdrawn before each run.
"""
from typing import Any, Dict, Optional

from app.calculators.base_calculator import BaseCalculator

# Metric CRS for buffering / area ranking (UTM 32N, matches app.core.geo_metric)
METRIC_EPSG = 32632

# Roof overhang allowance in metres.  Roughly one eave width; wide enough to
# catch overhanging roof polygons without reaching the neighbouring building.
DEFAULT_OFFSET_M = 2.0


class PvGeneratorCalculator(BaseCalculator):

    def __init__(self, pipeline_executor):
        super().__init__(pipeline_executor)

    def assign_pv_to_buildings(
        self,
        project_id: str,
        scenario_id: str,
        lod: int = 0,
        offset_m: float = DEFAULT_OFFSET_M,
    ) -> Optional[Dict[str, Any]]:
        """Match PV polygons to the buildings of one project-scenario.

        A building may collect several PV polygons.  A PV polygon is given to
        at most one building per scenario -- the one whose buffered footprint
        it overlaps most -- so PV area is never counted twice.
        """
        self.log_info(
            f"PV spatial join for project={project_id}, scenario={scenario_id}, "
            f"lod={lod}, offset={offset_m} m"
        )

        session = self.data_manager._require_session()
        from sqlalchemy import text

        params = {
            "pid": project_id,
            "sid": scenario_id,
            "lod": lod,
            "offset": float(offset_m),
            "mcrs": METRIC_EPSG,
        }

        total_buildings = session.execute(text("""
            SELECT count(*)
            FROM cim_vector.cim_wizard_building_properties
            WHERE project_id = :pid
              AND scenario_id = CAST(:sid AS uuid)
              AND lod = :lod
        """), params).scalar() or 0

        if not total_buildings:
            self.log_warning("No buildings found for this scenario")
            return {
                "project_id": project_id,
                "scenario_id": scenario_id,
                "total_buildings": 0,
                "buildings_with_pv": 0,
                "pv_assigned": 0,
                "status": "no_buildings",
            }

        # ── Withdraw this scenario's previous assignments ────────────────
        session.execute(text("""
            UPDATE cim_vector.pv
            SET scenario_id = NULLIF(
                    array_remove(scenario_id, CAST(:sid AS uuid)), '{}'
                ),
                updated_at = now()
            WHERE scenario_id @> ARRAY[CAST(:sid AS uuid)]
        """), params)

        session.execute(text("""
            UPDATE cim_vector.cim_wizard_building_properties
            SET pv = NULL, updated_at = now()
            WHERE project_id = :pid
              AND scenario_id = CAST(:sid AS uuid)
              AND lod = :lod
              AND pv IS NOT NULL
        """), params)

        # ── Offset spatial join, best building per PV ────────────────────
        # ST_DWithin on the geography cast prefilters using the geography
        # GIST indexes; the metric overlap is then used only for ranking.
        matches = session.execute(text("""
            WITH scenario_buildings AS (
                SELECT b.building_id, b.building_geometry
                FROM cim_vector.cim_wizard_building b
                JOIN cim_vector.cim_wizard_building_properties bp
                  ON bp.building_id = b.building_id
                 AND bp.lod = b.lod
                WHERE bp.project_id = :pid
                  AND bp.scenario_id = CAST(:sid AS uuid)
                  AND bp.lod = :lod
            ),
            candidates AS (
                SELECT pv.pv_id,
                       sb.building_id,
                       ST_Area(ST_Intersection(
                           ST_Buffer(
                               ST_Transform(sb.building_geometry, :mcrs),
                               :offset
                           ),
                           ST_Transform(pv.pv_geometry, :mcrs)
                       )) AS overlap_m2,
                       ST_Distance(
                           ST_Transform(sb.building_geometry, :mcrs),
                           ST_Transform(pv.pv_geometry, :mcrs)
                       ) AS dist_m
                FROM scenario_buildings sb
                JOIN cim_vector.pv pv
                  ON ST_DWithin(
                         sb.building_geometry::geography,
                         pv.pv_geometry::geography,
                         :offset
                     )
            ),
            best AS (
                SELECT DISTINCT ON (pv_id)
                       pv_id, building_id, overlap_m2
                FROM candidates
                WHERE overlap_m2 > 0 OR dist_m <= :offset
                ORDER BY pv_id, overlap_m2 DESC, dist_m ASC, building_id
            )
            SELECT building_id,
                   ARRAY_AGG(pv_id ORDER BY pv_id) AS pv_ids
            FROM best
            GROUP BY building_id
        """), params).fetchall()

        pv_assigned = 0
        for building_id, pv_ids in matches:
            row_params = {
                **params,
                "bid": str(building_id),
                "pv_ids": [str(p) for p in pv_ids],
            }

            session.execute(text("""
                UPDATE cim_vector.cim_wizard_building_properties
                SET pv = CAST(:pv_ids AS uuid[]), updated_at = now()
                WHERE project_id = :pid
                  AND scenario_id = CAST(:sid AS uuid)
                  AND lod = :lod
                  AND building_id = CAST(:bid AS uuid)
            """), row_params)

            session.execute(text("""
                UPDATE cim_vector.pv
                SET scenario_id = COALESCE(scenario_id, '{}')
                                  || CAST(:sid AS uuid),
                    updated_at = now()
                WHERE pv_id = ANY(CAST(:pv_ids AS uuid[]))
                  AND NOT COALESCE(scenario_id, '{}')
                          @> ARRAY[CAST(:sid AS uuid)]
            """), row_params)

            pv_assigned += len(pv_ids)

        session.execute(text("""
            UPDATE cim_vector.cim_wizard_project_scenario
            SET pv_assigned = TRUE, updated_at = now()
            WHERE project_id = :pid AND scenario_id = CAST(:sid AS uuid)
        """), params)

        session.commit()

        result = {
            "project_id": project_id,
            "scenario_id": scenario_id,
            "lod": lod,
            "offset_m": float(offset_m),
            "total_buildings": total_buildings,
            "buildings_with_pv": len(matches),
            "pv_assigned": pv_assigned,
            "pv_assigned_flag": True,
            "status": "completed",
        }
        self.data_manager.set_feature("pv_generator", result)
        self.log_success(
            "assign_pv_to_buildings",
            f"{len(matches)}/{total_buildings} buildings matched "
            f"{pv_assigned} PV polygons (offset {offset_m} m)",
        )
        return result
