"""
Building Type Calculator - Determine building types based on census data
"""
from typing import Optional, Dict, Any
import pandas as pd
import geopandas as gpd


class BuildingTypeCalculator:
    """Calculate building types based on census residential data"""
    
    def __init__(self, pipeline_executor):
        self.pipeline = pipeline_executor
        self.calculator_name = self.__class__.__name__
        self.zone_assignment_errors = []  # Store error statistics for final report
    
    def by_census_osm(self, census_gdf: gpd.GeoDataFrame, buildings_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Assign building types based on OSM usage + strict criteria: exclude non-residential OSM buildings, then height > 8 AND area > 100 = residential"""
        try:
            self.pipeline.log_info(self.calculator_name, "Assigning building types based on OSM usage + strict criteria")
            
            # Step 1: Filter out buildings that are clearly non-residential based on OSM tags
            osm_non_residential_mask = buildings_gdf['osm_usage'] == 'not_residential_based_on_osm'
            buildings_gdf.loc[osm_non_residential_mask, 'building_type'] = 'non-residential'
            
            osm_non_residential_count = osm_non_residential_mask.sum()
            self.pipeline.log_info(self.calculator_name, f"Step 1: Excluded {osm_non_residential_count} buildings as non-residential based on OSM usage tags")
            
            # Step 2: Apply strict area and height criteria to remaining buildings
            remaining_buildings_mask = ~osm_non_residential_mask
            area_height_criteria = (buildings_gdf['height'] > 8.0) & (buildings_gdf['area'] > 100.0)
            
            # Final residential criteria: NOT excluded by OSM AND meets area/height criteria
            final_residential_mask = remaining_buildings_mask & area_height_criteria
            
            # Assign building types
            buildings_gdf.loc[final_residential_mask, 'building_type'] = 'residential'
            buildings_gdf.loc[remaining_buildings_mask & ~area_height_criteria, 'building_type'] = 'non-residential'
            
            # Calculate accuracy/error statistics per zone for reporting
            zone_errors = []
            total_actual_residential = len(buildings_gdf[buildings_gdf['building_type'] == 'residential'])
            total_census_residential = census_gdf['total_n_res_buildings'].sum()
            
            for idx, zone in census_gdf.iterrows():
                zone_id = zone.zone_id
                buildings_in_zone = buildings_gdf[buildings_gdf['census_zone_id'] == zone_id]
                
                if len(buildings_in_zone) == 0:
                    continue
                
                # Count actual residential buildings in this zone
                actual_residential_in_zone = len(buildings_in_zone[buildings_in_zone['building_type'] == 'residential'])
                census_residential_in_zone = zone.total_n_res_buildings
                
                # Calculate error for this zone
                error = actual_residential_in_zone - census_residential_in_zone
                error_percentage = (abs(error) / max(census_residential_in_zone, 1)) * 100
                
                zone_errors.append({
                    'zone_id': zone_id,
                    'census_residential': census_residential_in_zone,
                    'actual_residential': actual_residential_in_zone,
                    'error': error,
                    'error_percentage': error_percentage
                })
            
            # Store zone errors for final report
            self.zone_assignment_errors = zone_errors
            
            # Log summary
            residential_count = len(buildings_gdf[buildings_gdf['building_type'] == 'residential'])
            non_residential_count = len(buildings_gdf[buildings_gdf['building_type'] == 'non-residential'])
            osm_excluded_count = len(buildings_gdf[buildings_gdf['osm_usage'] == 'not_residential_based_on_osm'])
            criteria_excluded_count = len(buildings_gdf[
                (buildings_gdf['osm_usage'] != 'not_residential_based_on_osm') & 
                (buildings_gdf['building_type'] == 'non-residential')
            ])
            
            self.pipeline.log_info(self.calculator_name, f"Building type assignment summary:")
            self.pipeline.log_info(self.calculator_name, f"  - Residential: {residential_count} buildings (OSM eligible + height > 8 + area > 100)")
            self.pipeline.log_info(self.calculator_name, f"  - Non-residential (OSM usage): {osm_excluded_count} buildings")
            self.pipeline.log_info(self.calculator_name, f"  - Non-residential (size criteria): {criteria_excluded_count} buildings") 
            self.pipeline.log_info(self.calculator_name, f"  - Total non-residential: {non_residential_count} buildings")
            self.pipeline.log_info(self.calculator_name, f"  - Total census residential expected: {total_census_residential}")
            self.pipeline.log_info(self.calculator_name, f"  - Overall error: {total_actual_residential - total_census_residential} buildings")
            
            return buildings_gdf
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to assign building types: {str(e)}")
            return buildings_gdf 