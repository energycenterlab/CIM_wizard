"""
Building Height Calculator - Integrated Version
Uses direct database access to raster service instead of API calls
"""

from typing import Optional, Dict, Any
import json


class BuildingHeightCalculator:
    """
    Building Height Calculator - calculates building height using integrated raster service
    
    Methods:
    1. calculate_from_raster_service - Uses integrated raster service (direct DB)
    2. calculate_from_osm_height - Falls back to OSM data if available
    3. calculate_default_estimate - Provides default estimate based on building type
    """
    
    def __init__(self, executor, data_manager):
        """Initialize calculator with executor and data manager"""
        self.executor = executor
        self.data_manager = data_manager
        self.calculator_name = "BuildingHeightCalculator"
    
    def calculate_from_raster_service(self) -> Optional[float]:
        """
        Calculate building height using integrated raster service
        Direct database access instead of API call
        """
        # Validate inputs
        building_geo = self.data_manager.get_context('building_geo_data')
        if not self.executor.validate_dict(building_geo, 'building_geo', self.calculator_name):
            return None
        
        # Get building ID if available
        building_id = self.data_manager.get_context('building_id')
        
        try:
            # Get raster service from data manager (direct DB access)
            raster_service = self.data_manager.get_raster_service()
            
            # Calculate height using integrated service
            self.executor.log_info(self.calculator_name, 
                                 "Calculating height using integrated raster service")
            
            result = raster_service.calculate_building_height(
                building_geometry=building_geo,
                building_id=building_id,
                use_cache=True
            )
            
            if result and result.get('building_height') is not None:
                height = result['building_height']
                
                # Validate the calculated height
                if self.executor.validate_numeric(height, 'building_height', 
                                                 self.calculator_name, 
                                                 min_val=0, max_val=500):
                    self.executor.log_info(self.calculator_name, 
                                         f"Height calculated from raster: {height}m")
                    
                    # Store additional metadata
                    self.data_manager.set_context('height_calculation_method', 'raster_integrated')
                    self.data_manager.set_context('dtm_height', result.get('dtm_avg_height'))
                    self.data_manager.set_context('dsm_height', result.get('dsm_avg_height'))
                    
                    return height
            
            self.executor.log_warning(self.calculator_name, 
                                    "No height data available from raster service")
            return None
            
        except Exception as e:
            # Possible errors: Database connection issues, raster data not available
            self.executor.log_error(self.calculator_name, 
                                  f"Error calculating from raster service: {str(e)}")
            return None
    
    def calculate_from_osm_height(self) -> Optional[float]:
        """
        Calculate height from OSM building data if available
        Fallback method when raster data is not available
        """
        building_geo = self.data_manager.get_context('building_geo_data')
        
        if not building_geo:
            self.executor.log_warning(self.calculator_name, 
                                    "No building geometry available for OSM height")
            return None
        
        # Check if OSM properties contain height information
        if isinstance(building_geo, dict) and 'properties' in building_geo:
            props = building_geo['properties']
            
            # Try different OSM height tags
            height_tags = ['height', 'building:height', 'building_height']
            
            for tag in height_tags:
                if tag in props:
                    try:
                        height_str = str(props[tag])
                        # Remove units if present (e.g., "10m" -> "10")
                        height_str = height_str.replace('m', '').replace('M', '').strip()
                        height = float(height_str)
                        
                        if self.executor.validate_numeric(height, f'OSM {tag}', 
                                                        self.calculator_name,
                                                        min_val=0, max_val=500):
                            self.executor.log_info(self.calculator_name, 
                                                f"Height from OSM {tag}: {height}m")
                            
                            # Store metadata
                            self.data_manager.set_context('height_calculation_method', 'osm')
                            
                            return height
                    except (ValueError, TypeError) as e:
                        # Possible errors: Invalid height format in OSM data
                        self.executor.log_warning(self.calculator_name, 
                                               f"Invalid OSM height value for {tag}: {props[tag]}")
            
            # Try to calculate from levels/floors
            if 'building:levels' in props or 'levels' in props:
                levels_str = props.get('building:levels', props.get('levels', ''))
                try:
                    levels = int(levels_str)
                    # Assume 3.5m per floor as default
                    height = levels * 3.5
                    
                    if self.executor.validate_numeric(height, 'calculated from levels', 
                                                    self.calculator_name,
                                                    min_val=0, max_val=500):
                        self.executor.log_info(self.calculator_name, 
                                            f"Height calculated from {levels} levels: {height}m")
                        
                        # Store metadata
                        self.data_manager.set_context('height_calculation_method', 'osm_levels')
                        
                        return height
                except (ValueError, TypeError):
                    # Possible errors: Invalid levels format
                    pass
        
        self.executor.log_warning(self.calculator_name, 
                                "No height information found in OSM data")
        return None
    
    def calculate_default_estimate(self) -> Optional[float]:
        """
        Provide default height estimate based on building type
        Last resort fallback method
        """
        # Get building type if available
        building_type = self.data_manager.get_context('building_type_data')
        
        # Default heights by building type (in meters)
        default_heights = {
            'residential': 10.5,  # ~3 floors
            'commercial': 14.0,   # ~4 floors
            'industrial': 8.0,    # ~2 floors
            'office': 17.5,       # ~5 floors
            'retail': 7.0,        # ~2 floors
            'house': 7.0,         # ~2 floors
            'apartment': 14.0,    # ~4 floors
            'yes': 10.5          # Generic building
        }
        
        if building_type and building_type in default_heights:
            height = default_heights[building_type]
            self.executor.log_info(self.calculator_name, 
                                f"Using default height for {building_type}: {height}m")
            
            # Store metadata
            self.data_manager.set_context('height_calculation_method', 'default_estimate')
            
            return height
        
        # If no type available, use generic default
        height = 10.5  # ~3 floors
        self.executor.log_info(self.calculator_name, 
                            f"Using generic default height: {height}m")
        
        # Store metadata
        self.data_manager.set_context('height_calculation_method', 'default_generic')
        
        return height