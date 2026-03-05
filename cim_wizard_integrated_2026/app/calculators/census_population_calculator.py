"""
Census Population Calculator - Independent class with pipeline executor injection
"""
from typing import Optional, Dict, Any

from app.calculators.base_calculator import BaseCalculator


class CensusPopulationCalculator(BaseCalculator):
    """Calculate census population"""
    
    def __init__(self, pipeline_executor):
        super().__init__(pipeline_executor)
    
    def calculate_from_census_boundary(self) -> Optional[float]:
        """Calculate total population from census boundary data"""
        try:
            # Get scenario_census_boundary from data manager
            census_boundary = self.pipeline.get_feature_safely('scenario_census_boundary', calculator_name=self.calculator_name)
            
            if not census_boundary:
                self.pipeline.log_error(self.calculator_name, "No scenario_census_boundary data available")
                return None
            
            self.pipeline.log_info(self.calculator_name, "Calculating population from census boundary")
            
            # Census boundary may nest data under 'properties' (GeoJSON Feature format)
            props = census_boundary.get('properties', {})
            
            # Check top-level first, then properties
            total_population = (
                census_boundary.get('total_population', 0)
                or props.get('total_population', 0)
            )
            
            if total_population and total_population > 0:
                self.pipeline.log_info(self.calculator_name, f"Found total population: {total_population}")
                self.data_manager.set_feature('census_population', float(total_population))
                return float(total_population)
            
            # If no total population, sum from zones (check both levels)
            census_zones = (
                census_boundary.get('census_zones', [])
                or props.get('census_zones', [])
            )
            zone_population = 0
            for zone in census_zones:
                # Population may be at zone level or inside zone properties
                pop = zone.get('population', 0)
                if not pop:
                    zone_props = zone.get('properties', {})
                    pop = zone_props.get('population', 0)
                zone_population += pop
            
            if zone_population > 0:
                self.pipeline.log_info(self.calculator_name, f"Calculated population from {len(census_zones)} zones: {zone_population}")
                self.data_manager.set_feature('census_population', float(zone_population))
                return float(zone_population)
            
            self.pipeline.log_error(self.calculator_name, "No population data found in census boundary")
            return None
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to calculate census population: {str(e)}")
            return None 