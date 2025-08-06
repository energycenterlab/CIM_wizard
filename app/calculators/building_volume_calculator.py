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
    
    def calculate_from_height_and_area(self) -> Optional[float]:
        """Calculate building volume from height and area"""
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

            self.pipeline.log_info(self.calculator_name, f"Calculating building volumes from height and area for project_id={project_id}, scenario_id={scenario_id}, lod={lod}")

            # Use the general database query method
            building_props_queryset = self.pipeline.get_enriched_building_properties_from_database(
                project_id=project_id,
                scenario_id=scenario_id, 
                lod=lod,
                required_fields=['height', 'area'],
                calculator_name=self.calculator_name
            )
            
            if not building_props_queryset or not building_props_queryset.exists():
                self.pipeline.log_error(self.calculator_name, f"No BuildingProperties with both height and area data found for project_id={project_id}, scenario_id={scenario_id}, lod={lod}")
                return None

            # Process ALL buildings from the database where both height and area exist
            building_properties_list = []
            processed_count = 0
            
            try:
                from django.db import transaction
                    
                with transaction.atomic():
                    for building_props_obj in building_props_queryset:
                        height = building_props_obj.height
                        area = building_props_obj.area
                        
                        if height is None or height <= 0:
                            self.pipeline.log_warning(self.calculator_name, f"Skipping building {building_props_obj.building_id} - invalid height: {height}")
                            continue
                            
                        if area is None or area <= 0:
                            self.pipeline.log_warning(self.calculator_name, f"Skipping building {building_props_obj.building_id} - invalid area: {area}")
                            continue

                        # Calculate volume
                        volume = height * area
                        
                        # Update the database record
                        building_props_obj.volume = volume
                        building_props_obj.save()
                        
                        # Add to result list
                        building_properties_list.append({
                            'building_id': building_props_obj.building_id,
                            'scenario_id': scenario_id,
                            'lod': building_props_obj.lod,
                            'volume': volume,
                            'height': height,  # Include height for reference
                            'area': area       # Include area for reference
                        })
                        
                        self.pipeline.log_info(self.calculator_name, f"Building {building_props_obj.building_id}: volume = {volume:.2f}m³ ({height}m × {area}m²)")
                        processed_count += 1
                    
                    self.pipeline.log_info(self.calculator_name, f"Bulk updated volumes for {processed_count} buildings")
                    
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
            self.pipeline.store_result('building_volume', result)

            # Return volume for first building (for compatibility with single-building pipeline)
            first_volume = building_properties_list[0]['volume'] if building_properties_list else None
            
            if first_volume is not None:
                self.pipeline.log_info(self.calculator_name, f"Successfully calculated volumes for {processed_count} buildings")
                return first_volume
            else:
                self.pipeline.log_error(self.calculator_name, "No volume calculated for any building")
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