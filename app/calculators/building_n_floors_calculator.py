"""
Building Number of Floors Calculator
"""
from typing import Optional, Dict, Any
import math


class BuildingNFloorsCalculator:
    """Calculate number of floors from building height"""
    
    def __init__(self, pipeline_executor):
        self.pipeline = pipeline_executor
        self.data_manager = pipeline_executor.data_manager
        self.calculator_name = self.__class__.__name__
    
    def estimate_by_height(self) -> Optional[Dict[str, Any]]:
        """Estimate number of floors by dividing height by 3 and rounding down"""
        try:
            # Get building_geo and building_height data
            building_geo = self.pipeline.get_feature_safely('building_geo', calculator_name=self.calculator_name)
            building_heights = self.pipeline.get_feature_safely('building_heights', calculator_name=self.calculator_name)  # Note: plural 'building_heights'
            
            if not building_geo:
                self.pipeline.log_error(self.calculator_name, "No building_geo data available")
                return None
            
            if not building_heights:
                self.pipeline.log_error(self.calculator_name, "No building_height data available")
                return None
            
            # Get buildings from building_geo
            buildings = building_geo.get('buildings', [])
            if not buildings:
                self.pipeline.log_error(self.calculator_name, "No buildings found in building_geo")
                return None
            
            project_id = building_geo.get('project_id')
            scenario_id = building_geo.get('scenario_id')
            
            self.pipeline.log_info(self.calculator_name, f"Estimating number of floors for {len(buildings)} buildings")
            
            # Calculate number of floors for all buildings
            building_floors = []
            processed_count = 0
            
            for i, building in enumerate(buildings):
                building_id = building.get('building_id')
                
                # Get height for this building
                height = building_heights[i] if isinstance(building_heights, list) and i < len(building_heights) else 12.0
                
                if height is None or height <= 0:
                    self.pipeline.log_warning(self.calculator_name, f"Skipping building {building_id} - invalid height: {height}")
                    continue

                # Calculate number of floors
                number_of_floors = math.floor(height / 3)
                building_floors.append(number_of_floors)
                
                self.pipeline.log_info(self.calculator_name, f"Building {building_id}: {number_of_floors} floors (height: {height}m)")
                processed_count += 1
            
            if processed_count == 0:
                self.pipeline.log_error(self.calculator_name, "No buildings were processed successfully")
                return None

            # Create result
            result = {
                'project_id': project_id,
                'scenario_id': scenario_id,
                'building_floors': building_floors,
                'processed_count': processed_count
            }

            # Store result in data manager
            self.data_manager.set_feature('building_n_floors', result)

            self.pipeline.log_calculation_success(self.calculator_name, 'estimate_by_height', f"Estimated floors for {processed_count} buildings")
            return result

        except Exception as e:
            self.pipeline.log_calculation_failure(self.calculator_name, 'estimate_by_height', str(e))
            return None

    def save_to_database(self) -> bool:
        """Save building number of floors to database"""
        try:
            # Import Django models
            try:
                from cim_wizard.models import BuildingProperties
            except ImportError:
                self.pipeline.log_warning(self.calculator_name, "Django models not available - skipping database save")
                return False

            # Get building_n_floors data from the pipeline
            building_n_floors_data = self.pipeline.get_feature_safely('building_n_floors', calculator_name=self.calculator_name)
            if not building_n_floors_data:
                self.pipeline.log_error(self.calculator_name, "No building_n_floors data to save")
                return False

            # Get all building properties
            if not building_n_floors_data.get('building_properties'):
                self.pipeline.log_error(self.calculator_name, "No building properties in data")
                return False

            building_properties = building_n_floors_data['building_properties']
            project_id = building_n_floors_data['project_id']
            scenario_id = building_n_floors_data['scenario_id']
            
            # In this case, the data was already saved in estimate_by_height method
            # But we can still verify and log the status
            updated_count = 0
            
            try:
                from django.db import transaction
                
                with transaction.atomic():
                    for prop in building_properties:
                        building_id = prop['building_id']
                        lod = prop['lod']
                        number_of_floors = prop['number_of_floors']
                        
                        # Update BuildingProperties (should already be updated, but ensuring consistency)
                        try:
                            building_props = BuildingProperties.objects.get(
                                building_id=building_id,
                                project_id=project_id,
                                scenario_id=scenario_id,
                                lod=lod
                            )
                            
                            # Only update if different (shouldn't be the case)
                            if building_props.number_of_floors != number_of_floors:
                                building_props.number_of_floors = number_of_floors
                                building_props.save()
                                self.pipeline.log_info(self.calculator_name, f"Updated number of floors for building {building_id}")
                            
                            updated_count += 1
                            
                        except BuildingProperties.DoesNotExist:
                            self.pipeline.log_error(self.calculator_name, f"BuildingProperties not found for building {building_id}")
                            continue
                
                self.pipeline.log_info(self.calculator_name, f"Verified/updated number of floors for {updated_count} buildings")
                return True
                
            except Exception as e:
                self.pipeline.log_error(self.calculator_name, f"Failed to update BuildingProperties: {str(e)}")
                return False
                
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Error in save_to_database: {str(e)}")
            return False 