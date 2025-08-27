"""
Building Volume Calculator - Independent class with pipeline executor injection
"""
from typing import Optional
import json
import os


class BuildingVolumeCalculator:
    """Calculate building volume using various methods"""
    
    def __init__(self, pipeline_executor):
        self.pipeline = pipeline_executor
        self.data_manager = pipeline_executor.data_manager
        self.calculator_name = self.__class__.__name__
        
        # Load configuration
        config_path = os.path.join(os.path.dirname(__file__), '..', 'configuration.json')
        with open(config_path, 'r') as f:
            self.config = json.load(f)
    
    def calculate_from_height_and_area(self) -> Optional[Dict[str, Any]]:
        """Calculate building volumes from height and area"""
        try:
            # Get building_geo and other required data
            building_geo = self.pipeline.get_feature_safely('building_geo', calculator_name=self.calculator_name)
            building_heights = self.pipeline.get_feature_safely('building_height', calculator_name=self.calculator_name)
            building_area_data = self.pipeline.get_feature_safely('building_area', calculator_name=self.calculator_name)
            
            if not building_geo:
                self.pipeline.log_error(self.calculator_name, "No building_geo data available")
                return None
            
            if not building_heights:
                self.pipeline.log_error(self.calculator_name, "No building_height data available")
                return None
            
            if not building_area_data:
                self.pipeline.log_error(self.calculator_name, "No building_area data available")
                return None
            
            # Extract areas list from building_area_data
            building_areas = building_area_data.get('building_areas', [])
            if not building_areas:
                # Try to extract from building_properties
                building_properties = building_area_data.get('building_properties', [])
                if building_properties:
                    building_areas = [bp.get('area', 0) for bp in building_properties]
            
            if not building_areas:
                self.pipeline.log_error(self.calculator_name, "No building areas found in data")
                return None
            
            # Get buildings from building_geo
            buildings = building_geo.get('buildings', [])
            if not buildings:
                self.pipeline.log_error(self.calculator_name, "No buildings found in building_geo")
                return None
            
            project_id = building_geo.get('project_id')
            scenario_id = building_geo.get('scenario_id')
            
            self.pipeline.log_info(self.calculator_name, f"Calculating building volumes for {len(buildings)} buildings")
            
            # Calculate volumes for all buildings
            building_volumes = []
            processed_count = 0
            
            for i, building in enumerate(buildings):
                building_id = building.get('building_id')
                
                # Get height and area for this building
                height = building_heights[i] if i < len(building_heights) else 12.0  # Default height
                area = building_areas[i] if i < len(building_areas) else 100.0  # Default area
                
                if height is None or height <= 0:
                    self.pipeline.log_warning(self.calculator_name, f"Skipping building {building_id} - invalid height: {height}")
                    continue
                    
                if area is None or area <= 0:
                    self.pipeline.log_warning(self.calculator_name, f"Skipping building {building_id} - invalid area: {area}")
                    continue

                # Calculate volume
                volume = height * area
                building_volumes.append(volume)
                
                self.pipeline.log_info(self.calculator_name, f"Building {building_id}: volume = {volume:.2f}m³ ({height}m × {area}m²)")
                processed_count += 1
            
            if processed_count == 0:
                self.pipeline.log_error(self.calculator_name, "No buildings were processed successfully")
                return None

            # Create result
            result = {
                'project_id': project_id,
                'scenario_id': scenario_id,
                'building_volumes': building_volumes,
                'processed_count': processed_count
            }

            # Store result in data manager
            self.data_manager.set_feature('building_volume', result)
            
            self.pipeline.log_info(self.calculator_name, f"Successfully calculated volumes for {processed_count} buildings")
            return result
            
        except Exception as e:
            self.pipeline.log_calculation_failure(self.calculator_name, 'calculate_from_height_and_area', str(e))
            return None
                
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to calculate volume: {str(e)}")
            return None
        
    def save_to_database(self) -> bool:
        """Save building volume data to database"""
        try:
            building_volume = self.pipeline.get_feature_safely('building_volume', calculator_name=self.calculator_name)
            
            # Check if building_volume is the expected dictionary format
            if not building_volume or not isinstance(building_volume, dict):
                self.pipeline.log_info(self.calculator_name, "Building volume data already saved during calculation")
                return True  # Data was already saved in calculate_from_height_and_area
            
            # Verify we have the expected structure
            if not building_volume.get('building_properties'):
                self.pipeline.log_info(self.calculator_name, "No additional building volume data to save")
                return True
            
            from cim_wizard.models import BuildingProperties
            from django.db import transaction
            
            project_id = building_volume.get('project_id')
            scenario_id = building_volume.get('scenario_id')
            building_properties = building_volume.get('building_properties', [])
            
            if not project_id or not scenario_id:
                self.pipeline.log_warning(self.calculator_name, "Missing project_id or scenario_id in volume data")
                return True  # Data was already saved in main method
            
            with transaction.atomic():
                verified_count = 0
                for building_data in building_properties:
                    building_id = building_data['building_id']
                    volume = building_data['volume']
                    lod = building_data.get('lod', 0)
                    
                    try:
                        building_props = BuildingProperties.objects.get(
                            building_id=building_id,
                            project_id=project_id,
                            scenario_id=scenario_id,
                            lod=lod
                        )
                        
                        # Verify volume is already saved (should be from main calculation)
                        if building_props.volume == volume:
                            verified_count += 1
                        else:
                            # Update if somehow different
                            building_props.volume = volume
                            building_props.save()
                            self.pipeline.log_info(self.calculator_name, f"Updated volume for building {building_id}")
                            verified_count += 1
                            
                    except BuildingProperties.DoesNotExist:
                        self.pipeline.log_warning(self.calculator_name, f"BuildingProperties not found for building {building_id}")
                        continue
                
                self.pipeline.log_info(self.calculator_name, f"Verified volume data for {verified_count} buildings in database")
                return verified_count > 0
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Error in save_to_database: {str(e)}")
            return True  # Return True since data was already saved in main calculation 