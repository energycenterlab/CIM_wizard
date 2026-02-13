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
    
    def by_census_osm(self, census_gdf: gpd.GeoDataFrame = None, buildings_gdf: gpd.GeoDataFrame = None) -> Optional[Dict[str, Any]]:
        """Determine building types using Tabula classification"""
        
        # If called without arguments (from pipeline), derive types from filter_res
        if census_gdf is None or buildings_gdf is None:
            self.pipeline.log_info(self.calculator_name, "Pipeline mode: deriving building types from filter_res")
            
            filter_res_data = self.pipeline.get_feature_safely('filter_res', calculator_name=self.calculator_name)
            building_geo = self.pipeline.get_feature_safely('building_geo', calculator_name=self.calculator_name)
            
            if not filter_res_data or not building_geo:
                self.pipeline.log_error(self.calculator_name, "filter_res or building_geo not available")
                return None
            
            filter_values = filter_res_data.get('filter_res', [])
            buildings = building_geo.get('buildings', [])
            num_buildings = len(buildings)
            
            # Build per-building type list from filter_res boolean values
            building_types = []
            for i in range(num_buildings):
                if i < len(filter_values) and filter_values[i]:
                    building_types.append('residential')
                else:
                    building_types.append('non-residential')
            
            residential_count = sum(1 for t in building_types if t == 'residential')
            non_residential_count = num_buildings - residential_count
            
            self.pipeline.log_info(self.calculator_name,
                f"Assigned building types: {residential_count} residential, "
                f"{non_residential_count} non-residential out of {num_buildings} buildings")
            
            result = {
                'building_types': building_types,
                'total_buildings': num_buildings,
                'residential_count': residential_count,
                'non_residential_count': non_residential_count,
            }
            
            # Store in data manager
            self.pipeline.data_manager.set_feature('building_type', result)
            return result
        
        # Original implementation for when called with arguments
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