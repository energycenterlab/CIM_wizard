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
            # Use the general context enrichment system
            required_inputs = ['project_id', 'scenario_id', 'lod']
            enriched_context = self.pipeline.enrich_context_from_inputs_or_database(required_inputs, self.calculator_name)
            
            # Check if we have the critical inputs
            if 'project_id' not in enriched_context or 'scenario_id' not in enriched_context:
                self.pipeline.log_error(self.calculator_name, "Missing required project_id or scenario_id after context enrichment")
                return None
            
            project_id = enriched_context['project_id']
            scenario_id = enriched_context['scenario_id']
            lod = enriched_context.get('lod', 0)

            # Use the general database query method
            building_props_queryset = self.pipeline.get_enriched_building_properties_from_database(
                project_id=project_id,
                scenario_id=scenario_id,
                lod=lod,
                required_fields=['height'],
                calculator_name=self.calculator_name
            )
            
            if not building_props_queryset or not building_props_queryset.exists():
                self.pipeline.log_error(self.calculator_name, f"No BuildingProperties with height data found for project_id={project_id}, scenario_id={scenario_id}, lod={lod}")
                return None

            # Process ALL buildings instead of just the first one
            building_properties_list = []
            processed_count = 0
            
            try:
                from django.db import transaction
                
                with transaction.atomic():
                    for building_props_obj in building_props_queryset:
                        height = building_props_obj.height
                        
                        if height is None or height <= 0:
                            self.pipeline.log_warning(self.calculator_name, f"Skipping building {building_props_obj.building_id} - invalid height: {height}")
                            continue

                        # Calculate number of floors
                        number_of_floors = math.floor(height / 3)
                        
                        # Update the database record
                        building_props_obj.number_of_floors = number_of_floors
                        building_props_obj.save()
                        
                        # Add to result list
                        building_properties_list.append({
                            'building_id': building_props_obj.building_id,
                            'scenario_id': scenario_id,
                            'lod': building_props_obj.lod,
                            'number_of_floors': number_of_floors,
                            'height': height  # Include height for reference
                        })
                        
                        processed_count += 1
                    
                    self.pipeline.log_info(self.calculator_name, f"Processed number of floors for {processed_count} buildings")
                    
            except Exception as e:
                self.pipeline.log_error(self.calculator_name, f"Failed to process buildings from database: {str(e)}")
                return None

            if processed_count == 0:
                self.pipeline.log_error(self.calculator_name, "No buildings were processed successfully")
                return None

            # Create result
            result = {
                'project_id': project_id,
                'scenario_id': scenario_id,
                'building_properties': building_properties_list
            }

            # Store result
            self.pipeline.store_result('building_n_floors', result)

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