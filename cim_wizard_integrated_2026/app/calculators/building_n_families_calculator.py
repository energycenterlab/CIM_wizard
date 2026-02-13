"""
Building N Families Calculator - Enhanced for census integration  
"""
from typing import Optional, Dict, Any, Tuple
import pandas as pd
import geopandas as gpd
import math


class BuildingNFamiliesCalculator:
    """Calculate number of families from building population"""
    
    def __init__(self, pipeline_executor):
        self.pipeline = pipeline_executor
        self.data_manager = pipeline_executor.data_manager
        self.calculator_name = self.__class__.__name__
    
    def calculate_from_population(self) -> Optional[Dict[str, Any]]:
        """Calculate number of families based on building populations"""
        building_population_data = self.pipeline.get_feature_safely('building_population', calculator_name=self.calculator_name)
        building_geo = self.pipeline.get_feature_safely('building_geo', calculator_name=self.calculator_name)
        
        if not building_population_data:
            self.pipeline.log_error(self.calculator_name, "building_population not available")
            return None
        if not building_geo:
            self.pipeline.log_error(self.calculator_name, "building_geo not available")
            return None
        
        self.pipeline.log_info(self.calculator_name, "Calculating number of families from populations")
        
        try:
            # Get building populations
            building_populations = building_population_data.get('building_populations', [])
            buildings = building_geo.get('buildings', [])
            
            if not building_populations:
                self.pipeline.log_error(self.calculator_name, "No building populations found")
                return None
            
            # Average family size for residential buildings
            avg_family_size = 2.5  # Average family size
            
            # Calculate families for all buildings
            building_families = []
            for i, population in enumerate(building_populations):
                if population > 0:
                    # Calculate number of families
                    num_families = math.ceil(population / avg_family_size)
                    building_families.append(num_families)
                else:
                    building_families.append(0)
            
            # Create result
            result = {
                'project_id': building_geo.get('project_id'),
                'scenario_id': building_geo.get('scenario_id'),
                'building_families': building_families,
                'avg_family_size': avg_family_size,
                'total_families': sum(building_families),
                'calculation_method': 'population_based'
            }
            
            # Store in data manager
            self.data_manager.set_feature('building_n_families', result)
            
            self.pipeline.log_info(self.calculator_name, f"Calculated families for {len(building_families)} buildings")
            return result
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to calculate number of families: {str(e)}")
            return None
    
    def by_census_osm(self, buildings_gdf: gpd.GeoDataFrame = None) -> Optional[Dict[str, Any]]:
        """Calculate number of families from building population"""
        
        # If called without arguments (from pipeline), return a simplified result
        if buildings_gdf is None:
            self.pipeline.log_info(self.calculator_name, "Called without arguments - returning default families data")
            
            # Return default families data
            default_data = {
                'building_n_families': 1,  # Default families per building
                'families_method': 'default'
            }
            
            # Store in data manager
            self.pipeline.data_manager.set_feature('building_n_families', default_data)
            return default_data
        
        # Original implementation for when called with arguments
        """Calculate number of families based on population (assuming 3 people per family)"""
        try:
            average_family_size = 3.0
            accuracy_report = {'buildings_processed': 0, 'total_families': 0}
            
            self.pipeline.log_info(self.calculator_name, "Calculating families from population")
            
            residential_buildings = buildings_gdf[buildings_gdf['building_type'] == 'residential']
            
            for building_idx in residential_buildings.index:
                population = buildings_gdf.at[building_idx, 'n_people']
                families = population / average_family_size
                buildings_gdf.at[building_idx, 'n_family'] = round(families)
                
                accuracy_report['buildings_processed'] += 1
                accuracy_report['total_families'] += families
            
            self.pipeline.log_info(self.calculator_name, f"Calculated families for {accuracy_report['buildings_processed']} buildings")
            return buildings_gdf, accuracy_report
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to calculate families: {str(e)}")
            return buildings_gdf, {'error': str(e)} 