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
        
        print(f"\n=== DEBUG: Starting height calculation ===")
        
        # Get buildings
        building_geo = self.pipeline.get_feature_safely('building_geo')
        if not building_geo:
            print("ERROR: No building_geo data")
            return None
            
        buildings = building_geo.get('buildings', [])
        if not buildings:
            print("ERROR: No buildings in building_geo")
            return None
        
        print(f"DEBUG: Found {len(buildings)} buildings")
        
        # Get database
        db_session = getattr(self.data_manager, 'db_session', None)
        if not db_session:
            print("ERROR: No database session")
            return None
        
        print("DEBUG: Database session OK")
        
        # Test database tables exist
        try:
            dsm_test = db_session.execute(text("SELECT COUNT(*) FROM cim_raster.dsm_raster_tiles")).fetchone()
            print(f"DEBUG: DSM table has {dsm_test[0]} rows")
        except Exception as e:
            print(f"ERROR: DSM table issue: {e}")
            
        try:
            dtm_test = db_session.execute(text("SELECT COUNT(*) FROM cim_wizard.dtm_raster_tiles")).fetchone()
            print(f"DEBUG: DTM table has {dtm_test[0]} rows")
        except Exception as e:
            print(f"ERROR: DTM table issue: {e}")
        
        heights = []
        
        for i, building in enumerate(buildings):
            if i >= 3:  # Only debug first 3 buildings
                break
                
            print(f"\n--- Building {i} ---")
            
            # Get coordinates (simple centroid)
            geometry = building.get('geometry', {})
            coords = geometry.get('coordinates', [])
            
            print(f"DEBUG: Geometry type: {geometry.get('type')}")
            print(f"DEBUG: Coords structure: {type(coords)}, length: {len(coords) if coords else 0}")
            
            if not coords:
                print("ERROR: No coordinates")
                heights.append(12.0)  # default
                continue
                
            # Get first coordinate pair - fix coordinate extraction
            try:
                if geometry.get('type') == 'Polygon':
                    # For polygon: coords[0] is exterior ring, coords[0][0] is first point
                    lon, lat = coords[0][0][0], coords[0][0][1]
                elif geometry.get('type') == 'Point':
                    # For point: coords is [lon, lat]
                    lon, lat = coords[0], coords[1]
                else:
                    print(f"ERROR: Unknown geometry type: {geometry.get('type')}")
                    heights.append(12.0)
                    continue
                    
                print(f"DEBUG: Coordinates: lon={lon}, lat={lat}")
                    
            except Exception as e:
                print(f"ERROR: Coordinate extraction failed: {e}")
                heights.append(12.0)
                continue
            
            # Get DSM value
            try:
                dsm_query = text("""
                    SELECT ST_Value(rast, ST_SetSRID(ST_Point(:lon, :lat), 4326))
                    FROM cim_raster.dsm_raster_tiles
                    WHERE ST_Intersects(rast, ST_SetSRID(ST_Point(:lon, :lat), 4326))
                    LIMIT 1
                """)
                dsm_result = db_session.execute(dsm_query, {'lon': lon, 'lat': lat}).fetchone()
                dsm_value = dsm_result[0] if dsm_result and dsm_result[0] is not None else None
                print(f"DEBUG: DSM value: {dsm_value}")
            except Exception as e:
                print(f"ERROR: DSM query failed: {e}")
                dsm_value = None
            
            # Get DTM value  
            try:
                dtm_query = text("""
                    SELECT ST_Value(rast, ST_SetSRID(ST_Point(:lon, :lat), 4326))
                    FROM cim_wizard.dtm_raster_tiles
                    WHERE ST_Intersects(rast, ST_SetSRID(ST_Point(:lon, :lat), 4326))
                    LIMIT 1
                """)
                dtm_result = db_session.execute(dtm_query, {'lon': lon, 'lat': lat}).fetchone()
                dtm_value = dtm_result[0] if dtm_result and dtm_result[0] is not None else None
                print(f"DEBUG: DTM value: {dtm_value}")
            except Exception as e:
                print(f"ERROR: DTM query failed: {e}")
                dtm_value = None
            
            # Calculate height
            if dsm_value is not None and dtm_value is not None:
                height = dsm_value - dtm_value
                print(f"DEBUG: Raw height: {height}")
                
                if height < 3:
                    height = 3.0
                if height > 200:
                    height = 200.0
                    
                print(f"DEBUG: Final height: {height}")
                heights.append(height)
            else:
                print("DEBUG: Missing raster data, using default")
                heights.append(12.0)
        
        # Add remaining buildings with default height for now
        remaining = len(buildings) - len(heights)
        if remaining > 0:
            print(f"DEBUG: Adding {remaining} more buildings with default height")
            heights.extend([12.0] * remaining)
        
        print(f"\nDEBUG: Final heights: {heights[:10]}...")  # Show first 10
        
        # Store result
        self.data_manager.set_feature('building_height', heights)
        
        return heights