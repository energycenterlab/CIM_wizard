"""
Census Population Calculator - Independent class with pipeline executor injection
"""
from typing import Optional, Dict, Any


class CensusPopulationCalculator:
    """Calculate census population"""
    
    def __init__(self, pipeline_executor):
        self.pipeline = pipeline_executor
        self.data_manager = pipeline_executor.data_manager
        self.calculator_name = self.__class__.__name__
    
    def calculate_from_census_boundary(self) -> Optional[float]:
        """Calculate total population from census boundary data"""
        try:
            # Get scenario_census_boundary from data manager
            census_boundary = self.pipeline.get_feature_safely('scenario_census_boundary', calculator_name=self.calculator_name)
            
            if not census_boundary:
                self.pipeline.log_error(self.calculator_name, "No scenario_census_boundary data available")
                return None
            
            self.pipeline.log_info(self.calculator_name, "Calculating population from census boundary")
            
            # Get total population from census boundary
            total_population = census_boundary.get('total_population', 0)
            
            if total_population > 0:
                self.pipeline.log_info(self.calculator_name, f"Found total population: {total_population}")
                return float(total_population)
            
            # If no total population, sum from zones
            census_zones = census_boundary.get('census_zones', [])
            zone_population = sum(zone.get('population', 0) for zone in census_zones)
            
            if zone_population > 0:
                self.pipeline.log_info(self.calculator_name, f"Calculated population from zones: {zone_population}")
                return float(zone_population)
            
            self.pipeline.log_error(self.calculator_name, "No population data found in census boundary")
            return None
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to calculate census population: {str(e)}")
            return None 