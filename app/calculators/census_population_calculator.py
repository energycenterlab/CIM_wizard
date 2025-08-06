"""
Census Population Calculator
"""
from typing import Optional
from ..simplified_base_feature import CimWizardBaseFeature


class CensusPopulationCalculator(CimWizardBaseFeature):
    """Calculate census population"""
    
    def calculate_from_census_boundary(self) -> Optional[float]:
        """Calculate total population from census boundary data"""
        if not self._validate_input(self.context.scenario_census_boundary, "scenario_census_boundary"):
            return None
        
        self._log_info("Calculating population from census boundary")
        
        try:
            census_boundary = self.context.scenario_census_boundary
            
            # Get total population from census boundary
            total_population = census_boundary.get('total_population', 0)
            
            if total_population > 0:
                self._log_info(f"Found total population: {total_population}")
                return float(total_population)
            
            # If no total population, sum from zones
            census_zones = census_boundary.get('census_zones', [])
            zone_population = sum(zone.get('population', 0) for zone in census_zones)
            
            if zone_population > 0:
                self._log_info(f"Calculated population from zones: {zone_population}")
                return float(zone_population)
            
            self._log_error("No population data found in census boundary")
            return None
            
        except Exception as e:
            self._log_error(f"Failed to calculate census population: {str(e)}")
            return None 