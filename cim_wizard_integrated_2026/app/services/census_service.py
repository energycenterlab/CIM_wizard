"""
Census Service - Direct database access to census data
Replaces API calls with direct database queries
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text
from geoalchemy2.functions import ST_Intersects, ST_Contains, ST_AsGeoJSON, ST_GeomFromText
from shapely.geometry import shape, mapping, Polygon, MultiPolygon
import json

from app.models.census import CensusGeo
from app.db.database import SessionLocal


class CensusService:
    """Service for direct census data access"""
    
    def __init__(self, db_session: Session = None):
        """Initialize with optional database session"""
        self.db = db_session or SessionLocal()
        self.should_close_db = db_session is None
    
    def __del__(self):
        """Clean up database session if we created it"""
        if self.should_close_db and self.db:
            self.db.close()
    
    def get_census_by_polygon(self, polygon_coords: List[List[float]]) -> Dict[str, Any]:
        """
        Get census zones that intersect with a given polygon
        
        Args:
            polygon_coords: List of [lon, lat] coordinates
            
        Returns:
            GeoJSON FeatureCollection with census data
        """
        try:
            # Ensure polygon is closed
            if polygon_coords[0] != polygon_coords[-1]:
                polygon_coords.append(polygon_coords[0])
            
            # Create WKT polygon
            coords_str = ', '.join([f"{lon} {lat}" for lon, lat in polygon_coords])
            polygon_wkt = f"POLYGON(({coords_str}))"
            
            # Query census zones that intersect with the polygon
            census_zones = self.db.query(
                CensusGeo,
                ST_AsGeoJSON(CensusGeo.geometry).label('geojson')
            ).filter(
                ST_Intersects(
                    CensusGeo.geometry,
                    ST_GeomFromText(polygon_wkt, 4326)
                )
            ).all()
            
            # Format as GeoJSON FeatureCollection
            features = []
            for zone, geojson in census_zones:
                feature = {
                    "type": "Feature",
                    "properties": {
                        "SEZ2011": zone.SEZ2011,
                        "COMUNE": zone.COMUNE,
                        "P1": zone.P1,  # Total population
                        "PF1": zone.PF1,  # Total families
                        # Building age periods
                        "E8": zone.E8,   # Before 1918
                        "E9": zone.E9,   # 1919-1945
                        "E10": zone.E10, # 1946-1960
                        "E11": zone.E11, # 1961-1970
                        "E12": zone.E12, # 1971-1980
                        "E13": zone.E13, # 1981-1990
                        "E14": zone.E14, # 1991-2000
                        "E15": zone.E15, # 2001-2005
                        "E16": zone.E16, # After 2005
                        # Housing statistics
                        "E3": zone.E3,   # Total buildings
                        "E4": zone.E4,   # Residential buildings
                        "crs": zone.crs
                    },
                    "geometry": json.loads(geojson)
                }
                features.append(feature)
            
            return {
                "type": "FeatureCollection",
                "features": features
            }
            
        except Exception as e:
            # Possible errors: Invalid polygon, database connection issues
            print(f"Error getting census by polygon: {str(e)}")
            return {"type": "FeatureCollection", "features": []}
    
    def get_census_by_id(self, census_id: int) -> Optional[CensusGeo]:
        """
        Get census zone by SEZ2011 ID
        
        Args:
            census_id: SEZ2011 census ID
            
        Returns:
            CensusGeo object or None
        """
        try:
            return self.db.query(CensusGeo).filter(
                CensusGeo.SEZ2011 == census_id
            ).first()
        except Exception as e:
            # Possible errors: Invalid ID, database connection issues
            print(f"Error getting census by ID: {str(e)}")
            return None
    
    def get_census_population(self, census_ids: List[int]) -> Dict[int, int]:
        """
        Get population for multiple census zones
        
        Args:
            census_ids: List of SEZ2011 census IDs
            
        Returns:
            Dictionary mapping census_id to population
        """
        try:
            results = self.db.query(
                CensusGeo.SEZ2011,
                CensusGeo.P1
            ).filter(
                CensusGeo.SEZ2011.in_(census_ids)
            ).all()
            
            return {census_id: population for census_id, population in results}
        except Exception as e:
            # Possible errors: Database connection issues
            print(f"Error getting census population: {str(e)}")
            return {}
    
    def get_building_age_distribution(self, census_id: int) -> Dict[str, int]:
        """
        Get building age distribution for a census zone
        
        Args:
            census_id: SEZ2011 census ID
            
        Returns:
            Dictionary with building counts by period
        """
        try:
            zone = self.db.query(CensusGeo).filter(
                CensusGeo.SEZ2011 == census_id
            ).first()
            
            if not zone:
                return {}
            
            return {
                "before_1918": zone.E8 or 0,
                "1919_1945": zone.E9 or 0,
                "1946_1960": zone.E10 or 0,
                "1961_1970": zone.E11 or 0,
                "1971_1980": zone.E12 or 0,
                "1981_1990": zone.E13 or 0,
                "1991_2000": zone.E14 or 0,
                "2001_2005": zone.E15 or 0,
                "after_2005": zone.E16 or 0,
                "total_buildings": zone.E3 or 0,
                "residential_buildings": zone.E4 or 0
            }
        except Exception as e:
            # Possible errors: Invalid ID, database connection issues
            print(f"Error getting building age distribution: {str(e)}")
            return {}
    
    def get_census_statistics(self, polygon_coords: List[List[float]]) -> Dict[str, Any]:
        """
        Get aggregated statistics for census zones within a polygon
        
        Args:
            polygon_coords: List of [lon, lat] coordinates
            
        Returns:
            Dictionary with aggregated statistics
        """
        try:
            # Ensure polygon is closed
            if polygon_coords[0] != polygon_coords[-1]:
                polygon_coords.append(polygon_coords[0])
            
            # Create WKT polygon
            coords_str = ', '.join([f"{lon} {lat}" for lon, lat in polygon_coords])
            polygon_wkt = f"POLYGON(({coords_str}))"
            
            # Query aggregated statistics
            stats = self.db.query(
                func.sum(CensusGeo.P1).label('total_population'),
                func.sum(CensusGeo.PF1).label('total_families'),
                func.sum(CensusGeo.E3).label('total_buildings'),
                func.sum(CensusGeo.E4).label('residential_buildings'),
                func.count(CensusGeo.SEZ2011).label('census_zones_count'),
                func.avg(CensusGeo.P1).label('avg_population_per_zone')
            ).filter(
                ST_Intersects(
                    CensusGeo.geometry,
                    ST_GeomFromText(polygon_wkt, 4326)
                )
            ).first()
            
            return {
                "total_population": int(stats.total_population or 0),
                "total_families": int(stats.total_families or 0),
                "total_buildings": int(stats.total_buildings or 0),
                "residential_buildings": int(stats.residential_buildings or 0),
                "census_zones_count": stats.census_zones_count or 0,
                "avg_population_per_zone": float(stats.avg_population_per_zone or 0)
            }
            
        except Exception as e:
            # Possible errors: Invalid polygon, database connection issues
            print(f"Error getting census statistics: {str(e)}")
            return {
                "total_population": 0,
                "total_families": 0,
                "total_buildings": 0,
                "residential_buildings": 0,
                "census_zones_count": 0,
                "avg_population_per_zone": 0
            }
    
    def get_census_by_building_location(self, building_geometry) -> Optional[CensusGeo]:
        """
        Get census zone that contains a building
        
        Args:
            building_geometry: Building geometry (GeoAlchemy2 element or WKT)
            
        Returns:
            CensusGeo object or None
        """
        try:
            # If building_geometry is a string (WKT), use ST_GeomFromText
            if isinstance(building_geometry, str):
                census_zone = self.db.query(CensusGeo).filter(
                    ST_Contains(
                        CensusGeo.geometry,
                        ST_GeomFromText(building_geometry, 4326)
                    )
                ).first()
            else:
                # If it's already a geometry object
                census_zone = self.db.query(CensusGeo).filter(
                    ST_Contains(CensusGeo.geometry, building_geometry)
                ).first()
            
            return census_zone
            
        except Exception as e:
            # Possible errors: Invalid geometry, database connection issues
            print(f"Error getting census by building location: {str(e)}")
            return None