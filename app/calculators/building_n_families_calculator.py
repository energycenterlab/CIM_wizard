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
    
    def calculate_from_population(self) -> Optional[int]:
        """Calculate number of families based on building population - single building"""
        building_population = getattr(self.data_manager, 'building_population', None)
        
        if not building_population:
            self.pipeline.log_error(self.calculator_name, "building_population not available")
            return None
        
        self.pipeline.log_info(self.calculator_name, "Calculating number of families from population")
        
        try:
            population = float(building_population)
            
            # Get building type to determine average family size
            building_type = 'residential'  # Default
            building_geo = getattr(self.data_manager, 'building_geo', None)
            if building_geo and isinstance(building_geo, dict):
                building_type = building_geo.get('building_type', 'residential')
            
            # Average family sizes by building type
            avg_family_sizes = {
                'residential': 2.5,   # Average family size
                'commercial': 1.0,    # Treat as individuals
                'office': 1.0,        # Treat as individuals
                'industrial': 1.0     # Treat as individuals
            }
            
            avg_family_size = avg_family_sizes.get(building_type, avg_family_sizes['residential'])
            
            # Calculate number of families
            if building_type == 'residential':
                num_families = math.ceil(population / avg_family_size)
            else:
                # For non-residential, count as individuals (1 family = 1 person)
                num_families = int(population)
            
            # Ensure at least 0 families
            num_families = max(0, num_families)
            
            self.pipeline.log_info(self.calculator_name, f"Calculated families: {num_families}")
            return num_families
            
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