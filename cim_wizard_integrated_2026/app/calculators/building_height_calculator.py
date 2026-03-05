"""
Simple Building Height Calculator - DSM minus DTM
Uses cim_raster.dsm and cim_raster.dtm tables from PostGIS database.
"""
from typing import Optional, List
from sqlalchemy import text

from app.calculators.base_calculator import BaseCalculator


class BuildingHeightCalculator(BaseCalculator):
    
    def __init__(self, pipeline_executor):
        super().__init__(pipeline_executor)

    # ── Raster table configuration ──────────────────────────────────
    # Change these if your raster tables have different names/schemas.
    DSM_TABLE = "cim_raster.dsm"
    DTM_TABLE = "cim_raster.dtm"
    DEFAULT_HEIGHT = 12.0   # Fallback when raster data unavailable
    MIN_HEIGHT = 3.0
    MAX_HEIGHT = 200.0
    # ────────────────────────────────────────────────────────────────
        
    def calculate_from_raster_tiles(self) -> Optional[List[float]]:
        """Calculate heights: DSM - DTM for each building centroid."""
        
        self.pipeline.log_info(self.calculator_name, "Starting height calculation")
        
        # Get buildings
        building_geo = self.pipeline.get_feature_safely('building_geo')
        if not building_geo:
            self.pipeline.log_error(self.calculator_name, "No building_geo data")
            return None
            
        buildings = building_geo.get('buildings', [])
        if not buildings:
            self.pipeline.log_error(self.calculator_name, "No buildings in building_geo")
            return None
        
        self.pipeline.log_info(self.calculator_name, f"Found {len(buildings)} buildings")
        
        # Get database session
        db_session = getattr(self.data_manager, 'db_session', None)
        if not db_session:
            self.pipeline.log_error(self.calculator_name, "No database session")
            return None
        
        # ── Verify raster tables exist ──────────────────────────────
        dsm_ok = self._check_raster_table(db_session, self.DSM_TABLE)
        dtm_ok = self._check_raster_table(db_session, self.DTM_TABLE)
        
        if not dsm_ok or not dtm_ok:
            self.pipeline.log_warning(
                self.calculator_name,
                f"Raster tables missing (DSM={dsm_ok}, DTM={dtm_ok}). "
                f"All buildings will get default height {self.DEFAULT_HEIGHT}m"
            )
            heights = [self.DEFAULT_HEIGHT] * len(buildings)
            self.data_manager.set_feature('building_height', heights)
            return heights
        
        # ── Calculate height per building ───────────────────────────
        heights = []
        raster_hits = 0
        
        for i, building in enumerate(buildings):
            lon, lat = self._get_centroid(building)
            if lon is None or lat is None:
                heights.append(self.DEFAULT_HEIGHT)
                continue
            
            height = self._query_height(db_session, lon, lat)
            if height is not None:
                raster_hits += 1
            else:
                height = self.DEFAULT_HEIGHT
            heights.append(height)
        
        self.pipeline.log_info(
            self.calculator_name,
            f"Height calculation complete: {raster_hits}/{len(buildings)} from raster, "
            f"{len(buildings) - raster_hits} default ({self.DEFAULT_HEIGHT}m)"
        )
        
        # Store result
        self.data_manager.set_feature('building_height', heights)
        return heights
    
    # ── Helper methods ──────────────────────────────────────────────
    
    def _check_raster_table(self, db_session, table_name: str) -> bool:
        """Check if a raster table exists and has data. Rolls back on error."""
        try:
            result = db_session.execute(
                text(f"SELECT COUNT(*) FROM {table_name}")
            ).fetchone()
            count = result[0] if result else 0
            self.pipeline.log_info(self.calculator_name, f"{table_name}: {count} rows")
            return count > 0
        except Exception as e:
            self.pipeline.log_warning(self.calculator_name, f"{table_name} not available: {e}")
            db_session.rollback()  # Critical: clear the failed transaction
            return False
    
    def _get_centroid(self, building: dict):
        """Extract a representative point (centroid) from building geometry."""
        geometry = building.get('geometry', {})
        coords = geometry.get('coordinates', [])
        geom_type = geometry.get('type', '')
        
        try:
            if geom_type == 'Polygon' and coords:
                # Average all ring vertices for a simple centroid
                ring = coords[0]
                if ring:
                    lons = [p[0] for p in ring]
                    lats = [p[1] for p in ring]
                    return sum(lons) / len(lons), sum(lats) / len(lats)
            elif geom_type == 'Point' and len(coords) >= 2:
                return coords[0], coords[1]
        except Exception:
            pass
        return None, None
    
    def _query_height(self, db_session, lon: float, lat: float) -> Optional[float]:
        """Query DSM and DTM at a point, return height = DSM - DTM (clamped)."""
        dsm_value = self._query_raster_value(db_session, self.DSM_TABLE, lon, lat)
        if dsm_value is None:
            return None
        
        dtm_value = self._query_raster_value(db_session, self.DTM_TABLE, lon, lat)
        if dtm_value is None:
            return None
        
        height = dsm_value - dtm_value
        height = max(self.MIN_HEIGHT, min(self.MAX_HEIGHT, height))
        return round(height, 2)
    
    def _query_raster_value(self, db_session, table_name: str, lon: float, lat: float) -> Optional[float]:
        """Get raster cell value at a point. Rolls back on error to keep session clean."""
        try:
            query = text(f"""
                SELECT ST_Value(rast, ST_SetSRID(ST_Point(:lon, :lat), 4326))
                FROM {table_name}
                WHERE ST_Intersects(rast, ST_SetSRID(ST_Point(:lon, :lat), 4326))
                LIMIT 1
            """)
            result = db_session.execute(query, {'lon': lon, 'lat': lat}).fetchone()
            if result and result[0] is not None:
                return float(result[0])
            return None
        except Exception:
            db_session.rollback()  # Clear failed transaction
            return None
