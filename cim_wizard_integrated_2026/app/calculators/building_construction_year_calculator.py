"""
Building Construction Year Calculator - Distribute construction years from census data
"""
from typing import Optional, Dict, Any, Tuple
import pandas as pd
import geopandas as gpd
import random

from app.calculators.base_calculator import BaseCalculator


class BuildingConstructionYearCalculator(BaseCalculator):
    """Calculate construction years based on census E8-E16 data"""
    
    def __init__(self, pipeline_executor):
        super().__init__(pipeline_executor)
        
        self.construction_year_ranges = {
            'E8': (1800, 1918),   # Before 1919
            'E9': (1919, 1945),   # 1919-1945
            'E10': (1946, 1960),  # 1946-1960
            'E11': (1961, 1970),  # 1961-1970
            'E12': (1971, 1980),  # 1971-1980
            'E13': (1981, 1990),  # 1981-1990
            'E14': (1991, 2000),  # 1991-2000
            'E15': (2001, 2005),  # 2001-2005
            'E16': (2006, 2023)   # After 2005
        }
        
        # TABULA period ranges
        self.tabula_periods = [
            (0, 1900, "TABULA_1"),
            (1901, 1920, "TABULA_2"),
            (1921, 1945, "TABULA_3"),
            (1946, 1960, "TABULA_4"),
            (1961, 1975, "TABULA_5"),
            (1976, 1990, "TABULA_6"),
            (1991, 2005, "TABULA_7")
        ]
    
    def _get_tabula_period(self, year):
        """Get TABULA period string for a given year"""
        for start, end, period in self.tabula_periods:
            if start <= year <= end:
                return period
        # Default for years after 2005
        return "TABULA_7"
    
    def by_census_osm(self, census_gdf: gpd.GeoDataFrame = None, buildings_gdf: gpd.GeoDataFrame = None) -> Optional[Dict[str, Any]]:
        """Distribute construction years E8-E16 to residential buildings and calculate related features"""
        
        # If called without arguments (from pipeline), distribute using census data
        if census_gdf is None or buildings_gdf is None:
            self.pipeline.log_info(self.calculator_name, "Pipeline mode: distributing construction years from census E8-E16 data")
            
            census_boundary = self.pipeline.get_feature_safely('scenario_census_boundary', calculator_name=self.calculator_name)
            filter_res_data = self.pipeline.get_feature_safely('filter_res', calculator_name=self.calculator_name)
            building_geo = self.pipeline.get_feature_safely('building_geo', calculator_name=self.calculator_name)
            
            if not census_boundary or not filter_res_data or not building_geo:
                self.pipeline.log_error(self.calculator_name,
                    "Required data not available (need scenario_census_boundary, filter_res, building_geo)")
                return None
            
            filter_values = filter_res_data.get('filter_res', [])
            buildings = building_geo.get('buildings', [])
            num_buildings = len(buildings)
            
            # Extract E8-E16 counts from census zones
            props = census_boundary.get('properties', {})
            census_zones = (
                census_boundary.get('census_zones', [])
                or props.get('census_zones', [])
            )
            
            period_keys = ['E8', 'E9', 'E10', 'E11', 'E12', 'E13', 'E14', 'E15', 'E16']
            total_by_period = {k: 0 for k in period_keys}
            for zone in census_zones:
                zone_props = zone.get('properties', {})
                for period in period_keys:
                    total_by_period[period] += (zone_props.get(period, 0) or 0)
            
            total_census_buildings = sum(total_by_period.values())
            self.pipeline.log_info(self.calculator_name,
                f"Census E8-E16 totals: {total_by_period} (sum={total_census_buildings})")
            
            # Calculate percentage distribution
            if total_census_buildings > 0:
                percentages = {p: c / total_census_buildings for p, c in total_by_period.items() if c > 0}
            else:
                percentages = {'E12': 1.0}  # Default to 1971-1980
            
            # Identify residential building indices
            residential_indices = [i for i in range(num_buildings) if i < len(filter_values) and filter_values[i]]
            num_residential = len(residential_indices)
            
            self.pipeline.log_info(self.calculator_name,
                f"Distributing construction years to {num_residential} residential buildings")
            
            # Create assignments for residential buildings based on census proportions
            building_assignments = []
            for period, pct in percentages.items():
                count = round(pct * num_residential)
                year_range = self.construction_year_ranges.get(period, (1970, 1980))
                for _ in range(count):
                    rand_year = random.randint(year_range[0], year_range[1])
                    tabula_period = self._get_tabula_period(rand_year)
                    building_assignments.append((period, rand_year, tabula_period))
            
            # Handle rounding discrepancies
            while len(building_assignments) < num_residential:
                rand_year = random.randint(1971, 1980)
                building_assignments.append(('E12', rand_year, self._get_tabula_period(rand_year)))
            building_assignments = building_assignments[:num_residential]
            random.shuffle(building_assignments)
            
            # Build per-building lists (None for non-residential)
            const_years = [None] * num_buildings
            const_periods = [None] * num_buildings
            const_tabulas = [None] * num_buildings
            
            for assign_idx, building_idx in enumerate(residential_indices):
                if assign_idx < len(building_assignments):
                    period, year, tabula = building_assignments[assign_idx]
                    const_years[building_idx] = year
                    const_periods[building_idx] = period
                    const_tabulas[building_idx] = tabula
            
            assigned_count = sum(1 for y in const_years if y is not None)
            self.pipeline.log_info(self.calculator_name,
                f"Assigned construction year data to {assigned_count} residential buildings")
            
            result = {
                'const_years': const_years,
                'const_periods': const_periods,
                'const_tabulas': const_tabulas,
                'total_assigned': assigned_count,
            }
            
            self.pipeline.data_manager.set_feature('building_construction_year', result)
            return result
        
        # Original implementation for when called with arguments
        """Distribute construction years E8-E16 to residential buildings and calculate related features"""
        try:
            accuracy_report = {'zones_processed': 0, 'buildings_assigned': 0, 'accuracy_issues': []}
            
            self.pipeline.log_info(self.calculator_name, "Distributing construction features to residential buildings")
            
            for idx, zone in census_gdf.iterrows():
                zone_id = zone.zone_id
                residential_buildings = buildings_gdf[
                    (buildings_gdf['census_zone_id'] == zone_id) & 
                    (buildings_gdf['building_type'] == 'residential')
                ]
                
                if len(residential_buildings) == 0:
                    continue
                
                # Get census construction year counts
                year_counts = {
                    'E8': zone.E8, 'E9': zone.E9, 'E10': zone.E10, 'E11': zone.E11,
                    'E12': zone.E12, 'E13': zone.E13, 'E14': zone.E14, 'E15': zone.E15, 'E16': zone.E16
                }
                
                total_census_buildings = sum(year_counts.values())
                total_residential = len(residential_buildings)
                
                # Calculate percentage distribution from census data
                year_percentages = {}
                if total_census_buildings > 0:
                    for period, count in year_counts.items():
                        year_percentages[period] = count / total_census_buildings
                else:
                    # If no census data, use uniform distribution
                    num_periods = len([count for count in year_counts.values() if count > 0])
                    if num_periods == 0:
                        year_percentages = {'E12': 1.0}  # Default to 1971-1980 period
                    else:
                        for period, count in year_counts.items():
                            year_percentages[period] = 1.0 / len(year_counts) if count >= 0 else 0
                
                # Calculate actual building assignments based on percentages
                period_building_counts = {}
                assigned_buildings = 0
                
                # Calculate counts for each period based on percentages
                for period, percentage in year_percentages.items():
                    if percentage > 0:
                        count = round(percentage * total_residential)
                        period_building_counts[period] = count
                        assigned_buildings += count
                
                # Handle rounding discrepancies - distribute remaining buildings to largest periods
                remaining = total_residential - assigned_buildings
                if remaining != 0:
                    # Sort periods by count (descending) and add remaining buildings
                    sorted_periods = sorted(period_building_counts.items(), key=lambda x: x[1], reverse=True)
                    for i in range(abs(remaining)):
                        period = sorted_periods[i % len(sorted_periods)][0]
                        if remaining > 0:
                            period_building_counts[period] += 1
                        else:
                            period_building_counts[period] = max(0, period_building_counts[period] - 1)
                
                # Create period distribution with all three features
                building_assignments = []
                for period, count in period_building_counts.items():
                    if count > 0:
                        year_range = self.construction_year_ranges[period]
                        for _ in range(int(count)):
                            # Generate random year within period range
                            random_year = random.randint(year_range[0], year_range[1])
                            # Get TABULA period for this year
                            tabula_period = self._get_tabula_period(random_year)
                            
                            building_assignments.append({
                                'const_period_census': period,
                                'const_year': random_year,
                                'const_TABULA': tabula_period
                            })
                
                # Record accuracy information
                if total_residential != total_census_buildings:
                    accuracy_report['accuracy_issues'].append({
                        'zone_id': zone_id,
                        'census_buildings': total_census_buildings,
                        'actual_buildings': total_residential,
                        'difference': total_residential - total_census_buildings,
                        'method': 'percentage_distribution'
                    })
                
                # Randomly assign all three features to buildings
                random.shuffle(building_assignments)
                for i, building_idx in enumerate(residential_buildings.index):
                    if i < len(building_assignments):
                        assignment = building_assignments[i]
                        buildings_gdf.at[building_idx, 'const_period_census'] = assignment['const_period_census']
                        buildings_gdf.at[building_idx, 'const_year'] = assignment['const_year']
                        buildings_gdf.at[building_idx, 'const_TABULA'] = assignment['const_TABULA']
                        accuracy_report['buildings_assigned'] += 1
                
                accuracy_report['zones_processed'] += 1
            
            self.pipeline.log_info(self.calculator_name, f"Distributed construction features for {accuracy_report['buildings_assigned']} buildings")
            return buildings_gdf, accuracy_report
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to distribute construction features: {str(e)}")
            return buildings_gdf, {'error': str(e)} 