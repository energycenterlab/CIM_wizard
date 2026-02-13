"""
Raster Service - Direct database access to raster data
Replaces API calls with direct database queries for DTM/DSM data
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, func
from geoalchemy2.functions import ST_AsGeoJSON, ST_GeomFromText, ST_Intersects
import json
import base64
from shapely.geometry import shape, mapping
import numpy as np

from app.models.raster import DTMRaster, DSMRaster, BuildingHeightCache
from app.db.database import SessionLocal


class RasterService:
    """Service for direct raster data access"""
    
    def __init__(self, db_session: Session = None):
        """Initialize with optional database session"""
        self.db = db_session or SessionLocal()
        self.should_close_db = db_session is None
    
    def __del__(self):
        """Clean up database session if we created it"""
        if self.should_close_db and self.db:
            self.db.close()
    
    def calculate_building_height(self, building_geometry: Dict[str, Any], 
                                 building_id: str = None,
                                 use_cache: bool = True) -> Dict[str, Any]:
        """
        Calculate building height from DTM and DSM rasters
        
        Args:
            building_geometry: GeoJSON geometry of the building
            building_id: Optional building ID for caching
            use_cache: Whether to use cached values if available
            
        Returns:
            Dictionary with height information
        """
        try:
            # Check cache first if building_id provided
            if use_cache and building_id:
                cached = self.get_cached_height(building_id)
                if cached:
                    return cached
            
            # Convert GeoJSON to WKT
            geom_shape = shape(building_geometry)
            polygon_wkt = geom_shape.wkt
            
            # Calculate DTM average height
            dtm_query = text("""
                SELECT AVG((ST_SummaryStats(
                    ST_Clip(rast, ST_GeomFromText(:polygon, 4326))
                )).mean) as avg_height
                FROM cim_raster.dtm_raster
                WHERE ST_Intersects(rast, ST_GeomFromText(:polygon, 4326))
            """)
            
            dtm_result = self.db.execute(
                dtm_query, 
                {"polygon": polygon_wkt}
            ).first()
            
            dtm_avg = dtm_result.avg_height if dtm_result else None
            
            # Calculate DSM average height
            dsm_query = text("""
                SELECT AVG((ST_SummaryStats(
                    ST_Clip(rast, ST_GeomFromText(:polygon, 4326))
                )).mean) as avg_height
                FROM cim_raster.dsm_raster
                WHERE ST_Intersects(rast, ST_GeomFromText(:polygon, 4326))
            """)
            
            dsm_result = self.db.execute(
                dsm_query,
                {"polygon": polygon_wkt}
            ).first()
            
            dsm_avg = dsm_result.avg_height if dsm_result else None
            
            # Calculate building height
            building_height = None
            if dtm_avg is not None and dsm_avg is not None:
                building_height = dsm_avg - dtm_avg
                
                # Cache the result if building_id provided
                if building_id:
                    self.cache_building_height(
                        building_id=building_id,
                        dtm_avg=dtm_avg,
                        dsm_avg=dsm_avg,
                        building_height=building_height
                    )
            
            return {
                "building_id": building_id,
                "dtm_avg_height": dtm_avg,
                "dsm_avg_height": dsm_avg,
                "building_height": building_height,
                "status": "calculated" if building_height is not None else "no_data"
            }
            
        except Exception as e:
            # Possible errors: Invalid geometry, raster data not available, database issues
            print(f"Error calculating building height: {str(e)}")
            return {
                "building_id": building_id,
                "dtm_avg_height": None,
                "dsm_avg_height": None,
                "building_height": None,
                "status": "error",
                "error": str(e)
            }
    
    def calculate_building_heights_batch(self, features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate heights for multiple buildings in batch
        
        Args:
            features: List of GeoJSON features with building_id and geometry
            
        Returns:
            List of height calculation results
        """
        results = []
        
        for feature in features:
            building_id = feature.get("properties", {}).get("building_id")
            geometry = feature.get("geometry")
            
            if not geometry:
                results.append({
                    "building_id": building_id,
                    "status": "error",
                    "error": "Missing geometry"
                })
                continue
            
            height_data = self.calculate_building_height(
                building_geometry=geometry,
                building_id=building_id
            )
            results.append(height_data)
        
        return results
    
    def get_cached_height(self, building_id: str, 
                         project_id: str = None, 
                         scenario_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Get cached building height
        
        Args:
            building_id: Building identifier
            project_id: Optional project ID
            scenario_id: Optional scenario ID
            
        Returns:
            Cached height data or None
        """
        try:
            query = self.db.query(BuildingHeightCache).filter(
                BuildingHeightCache.building_id == building_id
            )
            
            if project_id:
                query = query.filter(BuildingHeightCache.project_id == project_id)
            if scenario_id:
                query = query.filter(BuildingHeightCache.scenario_id == scenario_id)
            
            cached = query.first()
            
            if cached:
                return {
                    "building_id": cached.building_id,
                    "dtm_avg_height": cached.dtm_avg_height,
                    "dsm_avg_height": cached.dsm_avg_height,
                    "building_height": cached.building_height,
                    "status": "cached",
                    "calculation_date": cached.calculation_date.isoformat() if cached.calculation_date else None
                }
            
            return None
            
        except Exception as e:
            # Possible errors: Database connection issues
            print(f"Error getting cached height: {str(e)}")
            return None
    
    def cache_building_height(self, building_id: str, 
                            dtm_avg: float, 
                            dsm_avg: float,
                            building_height: float,
                            project_id: str = "default",
                            scenario_id: str = "default"):
        """
        Cache calculated building height
        
        Args:
            building_id: Building identifier
            dtm_avg: Average DTM height
            dsm_avg: Average DSM height
            building_height: Calculated building height
            project_id: Project ID
            scenario_id: Scenario ID
        """
        try:
            # Check if cache entry exists
            existing = self.db.query(BuildingHeightCache).filter(
                and_(
                    BuildingHeightCache.building_id == building_id,
                    BuildingHeightCache.project_id == project_id,
                    BuildingHeightCache.scenario_id == scenario_id
                )
            ).first()
            
            if existing:
                # Update existing cache
                existing.dtm_avg_height = dtm_avg
                existing.dsm_avg_height = dsm_avg
                existing.building_height = building_height
            else:
                # Create new cache entry
                cache_entry = BuildingHeightCache(
                    building_id=building_id,
                    project_id=project_id,
                    scenario_id=scenario_id,
                    dtm_avg_height=dtm_avg,
                    dsm_avg_height=dsm_avg,
                    building_height=building_height
                )
                self.db.add(cache_entry)
            
            self.db.commit()
            
        except Exception as e:
            # Possible errors: Database connection issues, constraint violations
            print(f"Error caching building height: {str(e)}")
            self.db.rollback()
    
    def clip_raster(self, polygon_geometry: Dict[str, Any], 
                   raster_type: str = "DTM") -> Optional[str]:
        """
        Clip raster data to a polygon
        
        Args:
            polygon_geometry: GeoJSON polygon geometry
            raster_type: "DTM" or "DSM"
            
        Returns:
            Base64 encoded raster data or None
        """
        try:
            # Convert GeoJSON to WKT
            geom_shape = shape(polygon_geometry)
            polygon_wkt = geom_shape.wkt
            
            # Select appropriate table
            table_name = "cim_raster.dtm_raster" if raster_type.upper() == "DTM" else "cim_raster.dsm_raster"
            
            # Query to clip raster
            query = text(f"""
                SELECT ST_AsGDALRaster(
                    ST_Clip(rast, ST_GeomFromText(:polygon, 4326)),
                    'GTiff'
                ) AS clipped_raster
                FROM {table_name}
                WHERE ST_Intersects(rast, ST_GeomFromText(:polygon, 4326))
            """)
            
            result = self.db.execute(
                query,
                {"polygon": polygon_wkt}
            ).first()
            
            if result and result.clipped_raster:
                # Encode as base64
                return base64.b64encode(result.clipped_raster).decode('utf-8')
            
            return None
            
        except Exception as e:
            # Possible errors: Invalid geometry, raster data not available
            print(f"Error clipping raster: {str(e)}")
            return None
    
    def get_elevation_at_point(self, lon: float, lat: float, 
                              raster_type: str = "DTM") -> Optional[float]:
        """
        Get elevation value at a specific point
        
        Args:
            lon: Longitude
            lat: Latitude  
            raster_type: "DTM" or "DSM"
            
        Returns:
            Elevation value or None
        """
        try:
            # Create point WKT
            point_wkt = f"POINT({lon} {lat})"
            
            # Select appropriate table
            table_name = "cim_raster.dtm_raster" if raster_type.upper() == "DTM" else "cim_raster.dsm_raster"
            
            # Query to get value at point
            query = text(f"""
                SELECT ST_Value(rast, ST_GeomFromText(:point, 4326)) as elevation
                FROM {table_name}
                WHERE ST_Intersects(rast, ST_GeomFromText(:point, 4326))
            """)
            
            result = self.db.execute(
                query,
                {"point": point_wkt}
            ).first()
            
            return result.elevation if result else None
            
        except Exception as e:
            # Possible errors: Point outside raster bounds, database issues
            print(f"Error getting elevation at point: {str(e)}")
            return None
    
    def get_raster_statistics(self, polygon_geometry: Dict[str, Any],
                            raster_type: str = "DTM") -> Dict[str, Any]:
        """
        Get statistics for raster within a polygon
        
        Args:
            polygon_geometry: GeoJSON polygon geometry
            raster_type: "DTM" or "DSM"
            
        Returns:
            Dictionary with statistics (min, max, mean, stddev)
        """
        try:
            # Convert GeoJSON to WKT
            geom_shape = shape(polygon_geometry)
            polygon_wkt = geom_shape.wkt
            
            # Select appropriate table
            table_name = "cim_raster.dtm_raster" if raster_type.upper() == "DTM" else "cim_raster.dsm_raster"
            
            # Query to get statistics
            query = text(f"""
                SELECT 
                    (ST_SummaryStats(ST_Clip(rast, ST_GeomFromText(:polygon, 4326)))).min as min_val,
                    (ST_SummaryStats(ST_Clip(rast, ST_GeomFromText(:polygon, 4326)))).max as max_val,
                    (ST_SummaryStats(ST_Clip(rast, ST_GeomFromText(:polygon, 4326)))).mean as mean_val,
                    (ST_SummaryStats(ST_Clip(rast, ST_GeomFromText(:polygon, 4326)))).stddev as stddev_val
                FROM {table_name}
                WHERE ST_Intersects(rast, ST_GeomFromText(:polygon, 4326))
            """)
            
            result = self.db.execute(
                query,
                {"polygon": polygon_wkt}
            ).first()
            
            if result:
                return {
                    "raster_type": raster_type,
                    "min": result.min_val,
                    "max": result.max_val,
                    "mean": result.mean_val,
                    "stddev": result.stddev_val
                }
            
            return {
                "raster_type": raster_type,
                "min": None,
                "max": None,
                "mean": None,
                "stddev": None,
                "status": "no_data"
            }
            
        except Exception as e:
            # Possible errors: Invalid geometry, database issues
            print(f"Error getting raster statistics: {str(e)}")
            return {
                "raster_type": raster_type,
                "status": "error",
                "error": str(e)
            }