"""
Simple Building Height Calculator - DSM minus DTM
"""
from typing import Optional, List
from sqlalchemy import text


class BuildingHeightCalculator:
    
    def __init__(self, pipeline_executor):
        self.pipeline = pipeline_executor
        self.data_manager = pipeline_executor.data_manager
        self.calculator_name = self.__class__.__name__
        
    def calculate_from_raster_tiles(self) -> Optional[List[float]]:
        """Calculate heights: DSM - DTM"""
        
        # Get buildings
        building_geo = self.pipeline.get_feature_safely('building_geo')
        if not building_geo:
            return None
            
        buildings = building_geo.get('buildings', [])
        if not buildings:
            return None
        
        # Get database
        db_session = getattr(self.data_manager, 'db_session', None)
        if not db_session:
            return None
        
        heights = []
        
        for building in buildings:
            # Get coordinates (simple centroid)
            coords = building.get('geometry', {}).get('coordinates', [])
            if not coords:
                heights.append(12.0)  # default
                continue
                
            # Get first coordinate pair
            if coords and len(coords) > 0 and len(coords[0]) > 0:
                lon, lat = coords[0][0][0], coords[0][0][1]
            else:
                heights.append(12.0)
                continue
            
            # Get DSM value
            dsm_query = text("""
                SELECT ST_Value(rast, ST_SetSRID(ST_Point(:lon, :lat), 4326))
                FROM cim_raster.dsm_raster_tiles
                WHERE ST_Intersects(rast, ST_SetSRID(ST_Point(:lon, :lat), 4326))
                LIMIT 1
            """)
            dsm_result = db_session.execute(dsm_query, {'lon': lon, 'lat': lat}).fetchone()
            dsm_value = dsm_result[0] if dsm_result and dsm_result[0] else 0
            
            # Get DTM value  
            dtm_query = text("""
                SELECT ST_Value(rast, ST_SetSRID(ST_Point(:lon, :lat), 4326))
                FROM cim_wizard.dtm_raster_tiles
                WHERE ST_Intersects(rast, ST_SetSRID(ST_Point(:lon, :lat), 4326))
                LIMIT 1
            """)
            dtm_result = db_session.execute(dtm_query, {'lon': lon, 'lat': lat}).fetchone()
            dtm_value = dtm_result[0] if dtm_result and dtm_result[0] else 0
            
            # Calculate height
            height = dsm_value - dtm_value
            if height < 3:
                height = 3.0
            if height > 200:
                height = 200.0
                
            heights.append(height)
        
        # Store result
        self.data_manager.set_feature('building_height', heights)
        
        return heights