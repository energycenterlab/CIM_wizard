"""
Building Height Calculator - Direct integration with raster tiles database
Uses cim_raster.dsm_raster_tiles and cim_raster.dtm_raster_tiles tables
"""
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BuildingHeightCalculator:
    """Calculate building heights from integrated DSM/DTM raster tiles"""
    
    def __init__(self, pipeline_executor):
        self.pipeline = pipeline_executor
        self.data_manager = pipeline_executor.data_manager
        self.calculator_name = self.__class__.__name__
    
    def calculate_from_raster_service(self) -> Optional[List[float]]:
        """
        Calculate building heights directly from DSM/DTM raster tiles in database
        This is the PRIMARY method with priority 1 in configuration
        """
        self.pipeline.log_info(self.calculator_name, "=== STARTING RASTER-BASED HEIGHT CALCULATION ===")
        
        # Get building_geo data
        building_geo = self.pipeline.get_feature_safely('building_geo', calculator_name=self.calculator_name)
        if not building_geo:
            self.pipeline.log_error(self.calculator_name, "No building_geo data available")
            return None
        
        buildings = building_geo.get('buildings', [])
        if not buildings:
            self.pipeline.log_error(self.calculator_name, "No buildings found in building_geo")
            return None
        
        self.pipeline.log_info(self.calculator_name, f"Processing {len(buildings)} buildings for height calculation")
        
        # Get database session from data_manager (passed from API)
        db_session = getattr(self.data_manager, 'db_session', None)
        if not db_session:
            self.pipeline.log_error(self.calculator_name, "No database session available! Check if db_session is set in data_manager")
            # Try to get from context
            db_session = self.data_manager.get_context('db_session')
            if not db_session:
                self.pipeline.log_error(self.calculator_name, "Database session not found in context either!")
                return self._fallback_heights(buildings)
        
        try:
            from shapely.geometry import shape, Point, Polygon
            from shapely import wkt
            from sqlalchemy import text
            import numpy as np
            
            building_heights = []
            successful_calculations = 0
            failed_calculations = 0
            
            for idx, building in enumerate(buildings):
                building_id = building.get('building_id', f'unknown_{idx}')
                geometry = building.get('geometry')
                
                # Log progress every 10 buildings
                if idx % 10 == 0:
                    self.pipeline.log_info(self.calculator_name, f"Processing building {idx+1}/{len(buildings)}...")
                
                if not geometry:
                    self.pipeline.log_warning(self.calculator_name, f"Building {building_id} has no geometry")
                    building_heights.append(12.0)
                    failed_calculations += 1
                    continue
                
                try:
                    # Convert building geometry to shapely
                    building_shape = shape(geometry)
                    
                    # Get building footprint as WKT for PostGIS
                    building_wkt = building_shape.wkt
                    
                    # Calculate height using PostGIS raster functions
                    height = self._calculate_height_from_tiles(
                        db_session, 
                        building_wkt, 
                        building_shape,
                        building_id
                    )
                    
                    if height and height > 0:
                        # Validate and constrain height
                        if height > 150:  # Max 150m for buildings
                            self.pipeline.log_warning(self.calculator_name, 
                                f"Building {building_id}: Capping excessive height {height:.2f}m to 150m")
                            height = 150.0
                        elif height < 3:  # Min 3m (1 floor)
                            self.pipeline.log_warning(self.calculator_name,
                                f"Building {building_id}: Adjusting low height {height:.2f}m to 3m")
                            height = 3.0
                        
                        building_heights.append(round(height, 2))
                        successful_calculations += 1
                        self.pipeline.log_info(self.calculator_name, 
                            f"Building {building_id}: Calculated height = {height:.2f}m from raster")
                    else:
                        # Fallback for this building
                        fallback_height = self._get_fallback_height(building)
                        building_heights.append(fallback_height)
                        failed_calculations += 1
                        self.pipeline.log_warning(self.calculator_name, 
                            f"Building {building_id}: No raster data, using fallback = {fallback_height}m")
                
                except Exception as e:
                    self.pipeline.log_error(self.calculator_name, 
                        f"Building {building_id} height calculation error: {str(e)}")
                    building_heights.append(self._get_fallback_height(building))
                    failed_calculations += 1
            
            self.pipeline.log_info(self.calculator_name, 
                f"=== HEIGHT CALCULATION COMPLETE ===\n" +
                f"   Successful: {successful_calculations}/{len(buildings)}\n" +
                f"   Failed/Fallback: {failed_calculations}/{len(buildings)}")
            
            # Store heights for other calculators
            self.data_manager.set_feature('building_heights', building_heights)
            
            # Return the list
            return building_heights
            
        except ImportError as e:
            self.pipeline.log_error(self.calculator_name, f"Missing required libraries: {str(e)}")
            return self._fallback_heights(buildings)
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Critical error in height calculation: {str(e)}")
            return self._fallback_heights(buildings)
    
    def _calculate_height_from_tiles(self, db_session, building_wkt: str, 
                                    building_shape, building_id: str) -> Optional[float]:
        """
        Query DSM and DTM raster tiles to calculate building height
        Height = DSM (surface with buildings) - DTM (terrain without buildings)
        """
        from sqlalchemy import text
        
        try:
            # CRITICAL: Use ST_SummaryStats to get statistics from raster tiles
            # We need to clip the raster to the building footprint and get mean values
            
            # First, check if tables exist
            table_check = text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'cim_raster' 
                    AND table_name = 'dsm_raster_tiles'
                ) AS dsm_exists,
                EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'cim_raster' 
                    AND table_name = 'dtm_raster_tiles'
                ) AS dtm_exists;
            """)
            
            check_result = db_session.execute(table_check).first()
            if not check_result or not check_result[0] or not check_result[1]:
                self.pipeline.log_error(self.calculator_name, 
                    f"Raster tables not found! DSM exists: {check_result[0] if check_result else 'Unknown'}, "
                    f"DTM exists: {check_result[1] if check_result else 'Unknown'}")
                return None
            
            # Query for DSM (Digital Surface Model - includes buildings)
            dsm_query = text("""
                WITH building AS (
                    SELECT ST_GeomFromText(:wkt, 4326) AS geom
                ),
                clipped_rasters AS (
                    SELECT ST_Clip(dst.rast, b.geom, true) AS clipped_rast
                    FROM cim_raster.dsm_raster_tiles dst, building b
                    WHERE ST_Intersects(dst.rast, b.geom)
                ),
                stats AS (
                    SELECT (ST_SummaryStats(clipped_rast)).mean AS mean_value
                    FROM clipped_rasters
                    WHERE clipped_rast IS NOT NULL
                )
                SELECT AVG(mean_value) AS dsm_height
                FROM stats
                WHERE mean_value IS NOT NULL;
            """)
            
            # Query for DTM (Digital Terrain Model - ground level)
            dtm_query = text("""
                WITH building AS (
                    SELECT ST_GeomFromText(:wkt, 4326) AS geom
                ),
                clipped_rasters AS (
                    SELECT ST_Clip(dtt.rast, b.geom, true) AS clipped_rast
                    FROM cim_raster.dtm_raster_tiles dtt, building b
                    WHERE ST_Intersects(dtt.rast, b.geom)
                ),
                stats AS (
                    SELECT (ST_SummaryStats(clipped_rast)).mean AS mean_value
                    FROM clipped_rasters
                    WHERE clipped_rast IS NOT NULL
                )
                SELECT AVG(mean_value) AS dtm_height
                FROM stats
                WHERE mean_value IS NOT NULL;
            """)
            
            # Execute DSM query with better error handling
            try:
                dsm_result = db_session.execute(dsm_query, {"wkt": building_wkt}).first()
                dsm_height = dsm_result[0] if dsm_result and dsm_result[0] is not None else None
            except Exception as e:
                self.pipeline.log_warning(self.calculator_name, f"DSM query error: {str(e)}")
                dsm_height = None
            
            if dsm_height is None:
                self.pipeline.log_warning(self.calculator_name, 
                    f"Building {building_id}: No DSM data found for footprint")
                
                # Try alternative: sample at building centroid
                centroid = building_shape.centroid
                dsm_height = self._sample_raster_at_point(
                    db_session, 
                    centroid.x, 
                    centroid.y, 
                    'dsm_raster_tiles'
                )
            
            # Execute DTM query with better error handling
            try:
                dtm_result = db_session.execute(dtm_query, {"wkt": building_wkt}).first()
                dtm_height = dtm_result[0] if dtm_result and dtm_result[0] is not None else None
            except Exception as e:
                self.pipeline.log_warning(self.calculator_name, f"DTM query error: {str(e)}")
                dtm_height = None
            
            if dtm_height is None:
                self.pipeline.log_warning(self.calculator_name, 
                    f"Building {building_id}: No DTM data found for footprint")
                
                # Try alternative: sample at building centroid
                centroid = building_shape.centroid
                dtm_height = self._sample_raster_at_point(
                    db_session,
                    centroid.x,
                    centroid.y,
                    'dtm_raster_tiles'
                )
            
            # Calculate building height
            if dsm_height is not None and dtm_height is not None:
                height = dsm_height - dtm_height
                self.pipeline.log_info(self.calculator_name,
                    f"Building {building_id}: DSM={dsm_height:.2f}m, DTM={dtm_height:.2f}m, Height={height:.2f}m")
                return height
            else:
                self.pipeline.log_warning(self.calculator_name,
                    f"Building {building_id}: Missing raster data (DSM={dsm_height}, DTM={dtm_height})")
                return None
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, 
                f"Raster query error for building {building_id}: {str(e)}")
            return None
    
    def _sample_raster_at_point(self, db_session, lon: float, lat: float, 
                                table_name: str) -> Optional[float]:
        """
        Sample raster value at a specific point (fallback method)
        """
        from sqlalchemy import text
        
        try:
            query = text(f"""
                SELECT ST_Value(rast, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)) as value
                FROM cim_raster.{table_name}
                WHERE ST_Intersects(rast, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326))
                LIMIT 1;
            """)
            
            result = db_session.execute(query, {"lon": lon, "lat": lat}).first()
            
            if result and result[0] is not None:
                return float(result[0])
            return None
            
        except Exception as e:
            self.pipeline.log_warning(self.calculator_name,
                f"Point sampling failed at ({lon}, {lat}): {str(e)}")
            return None
    
    def _get_fallback_height(self, building: Dict[str, Any]) -> float:
        """Get fallback height from OSM tags or building type"""
        properties = building.get('properties', {})
        osm_tags = properties.get('osm_tags', {})
        
        # Try OSM height tag
        if 'height' in osm_tags:
            try:
                height_str = str(osm_tags['height']).replace('m', '').strip()
                height = float(height_str)
                if 3 <= height <= 150:
                    return height
            except:
                pass
        
        # Try OSM levels
        if 'building:levels' in osm_tags:
            try:
                levels = int(osm_tags['building:levels'])
                return levels * 3.0
            except:
                pass
        
        # Based on building type
        building_type = osm_tags.get('building', 'yes')
        
        height_by_type = {
            'house': 6.0,
            'detached': 6.0,
            'residential': 12.0,
            'apartments': 18.0,
            'commercial': 15.0,
            'office': 24.0,
            'industrial': 10.0,
            'warehouse': 8.0,
            'retail': 12.0,
            'hotel': 21.0,
            'school': 9.0,
            'university': 15.0,
            'hospital': 18.0,
            'church': 15.0,
            'yes': 12.0  # Generic building
        }
        
        return height_by_type.get(building_type, 12.0)
    
    def _fallback_heights(self, buildings: List[Dict[str, Any]]) -> List[float]:
        """Generate fallback heights for all buildings"""
        self.pipeline.log_warning(self.calculator_name, 
            "Using fallback heights for all buildings")
        
        return [self._get_fallback_height(b) for b in buildings]
    
    def calculate_from_osm_height(self) -> Optional[List[float]]:
        """Secondary method: try to get heights from OSM tags"""
        self.pipeline.log_info(self.calculator_name, "Attempting OSM height extraction")
        
        building_geo = self.pipeline.get_feature_safely('building_geo')
        if not building_geo:
            return None
        
        buildings = building_geo.get('buildings', [])
        heights = []
        
        for building in buildings:
            height = self._get_fallback_height(building)
            heights.append(height)
        
        return heights
    
    def calculate_default_estimate(self) -> Optional[List[float]]:
        """Tertiary method: default height estimates"""
        self.pipeline.log_info(self.calculator_name, "Using default height estimates")
        
        building_geo = self.pipeline.get_feature_safely('building_geo')
        if not building_geo:
            return None
        
        buildings = building_geo.get('buildings', [])
        return [12.0] * len(buildings)  # Default 4 floors
    
    def save_to_database(self) -> bool:
        """Heights are saved by the pipeline automatically"""
        return True