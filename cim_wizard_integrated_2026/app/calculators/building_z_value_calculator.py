"""
Building Z-Value Calculator - Average DTM height at building footprint
Clips DTM raster by building footprint and computes the mean value.
Stores result in cim_vector.cim_wizard_building.z_value
"""
from typing import Optional, List

from app.calculators.base_calculator import BaseCalculator


class BuildingZValueCalculator(BaseCalculator):

    DTM_TABLE = "cim_raster.dtm"
    DEFAULT_Z = 0.0

    def __init__(self, pipeline_executor):
        super().__init__(pipeline_executor)

    def calculate_from_dtm(self) -> Optional[List[float]]:
        """Clip DTM by each building footprint and compute mean z-value."""

        self.log_info("Starting z-value calculation from DTM")

        building_geo = self.get_feature("building_geo")
        if not building_geo:
            self.log_error("No building_geo data")
            return None

        buildings = building_geo.get("buildings", [])
        if not buildings:
            self.log_error("No buildings in building_geo")
            return None

        self.log_info(f"Processing {len(buildings)} buildings")

        dtm_ok = self.data_manager.check_raster_table(self.DTM_TABLE)
        if not dtm_ok:
            self.log_warning(f"DTM table missing. Using default z={self.DEFAULT_Z}")
            z_values = [self.DEFAULT_Z] * len(buildings)
            self.data_manager.set_feature("building_z_value", z_values)
            return z_values

        session = self.data_manager._require_session()
        from sqlalchemy import text

        z_values = []
        raster_hits = 0

        for building in buildings:
            geojson = building.get("geometry")
            if not geojson:
                z_values.append(self.DEFAULT_Z)
                continue

            import json
            geojson_str = json.dumps(geojson)

            sql = text("""
                SELECT AVG(val) FROM (
                    SELECT (ST_SummaryStatsAgg(
                        ST_Clip(r.rast, geom.geom), 1, true
                    )).mean AS val
                    FROM cim_raster.dtm r,
                         (SELECT ST_SetSRID(ST_GeomFromGeoJSON(:geojson), 4326) AS geom) geom
                    WHERE ST_Intersects(r.rast, geom.geom)
                ) sub
            """)

            try:
                row = session.execute(sql, {"geojson": geojson_str}).fetchone()
                if row and row[0] is not None:
                    z_values.append(round(float(row[0]), 2))
                    raster_hits += 1
                else:
                    z_values.append(self.DEFAULT_Z)
            except Exception as e:
                self.log_warning(f"DTM query failed for building: {e}")
                z_values.append(self.DEFAULT_Z)

        self.log_info(f"Z-value done: {raster_hits}/{len(buildings)} from DTM")

        self.data_manager.set_feature("building_z_value", z_values)

        # Persist to cim_wizard_building.z_value directly
        try:
            from app.models.vector import Building
            for i, building in enumerate(buildings):
                bid = building.get("building_id")
                if bid:
                    bldg = session.query(Building).filter_by(building_id=bid).first()
                    if bldg:
                        bldg.z_value = z_values[i]
            session.commit()
        except Exception as e:
            self.log_warning(f"DB save z_value failed: {e}")

        self.log_success("calculate_from_dtm",
                         f"Computed z-value for {len(buildings)} buildings")
        return z_values
