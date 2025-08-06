"""
Building Props Calculator - Independent class with pipeline executor injection
"""
from typing import Optional, Dict, Any


class BuildingPropsCalculator:
    """Calculate building properties from building geometry"""
    
    def __init__(self, pipeline_executor):
        self.pipeline = pipeline_executor
        self.data_manager = pipeline_executor.data_manager
        self.calculator_name = self.__class__.__name__
    
    def init(self):
        """Initialize building properties from building geometry for ALL buildings"""
        try:
            # Get building_geo from pipeline
            building_geo = self.pipeline.get_feature_safely('building_geo')
            if not building_geo:
                self.pipeline.log_error(self.calculator_name, "No building_geo data available")
                return None

            # Get scenario_geo to extract project_id and scenario_id if not in building_geo
            scenario_geo = self.pipeline.get_feature_safely('scenario_geo')
            
            # Extract required fields
            project_id = building_geo.get('project_id') or (scenario_geo.get('project_id') if scenario_geo else None)
            scenario_id = building_geo.get('scenario_id') or (scenario_geo.get('scenario_id') if scenario_geo else None)
            
            if not project_id or not scenario_id:
                self.pipeline.log_error(self.calculator_name, "Missing required project_id or scenario_id in building_geo and scenario_geo")
                return None

            # Extract building data
            buildings = building_geo.get('buildings', [])
            if not buildings:
                self.pipeline.log_error(self.calculator_name, "No buildings in building_geo data")
                return None

            # Create building properties for ALL buildings
            building_properties_list = []
            created_count = 0
            updated_count = 0
            
            try:
                from cim_wizard.models import BuildingProperties
                from django.db import transaction
                
                with transaction.atomic():
                    for building in buildings:
                        building_id = building.get('building_id')
                        lod = building.get('lod', 0)

                        if not building_id:
                            self.pipeline.log_warning(self.calculator_name, f"Skipping building with missing building_id")
                            continue

                        # Create or get BuildingProperties for each building
                        building_props_obj, created = BuildingProperties.objects.update_or_create(
                            building_id=building_id,
                            project_id=project_id,
                            scenario_id=scenario_id,
                            lod=lod,
                            defaults={
                                'height': None,
                                'area': None,
                                'volume': None,
                                'number_of_floors': None
                            }
                        )
                        
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1
                        
                        # Add to result list
                        building_properties_list.append({
                            'building_id': building_id,
                            'scenario_id': scenario_id,
                            'lod': lod,
                            'height': None,
                            'area': None,
                            'volume': None,
                            'number_of_floors': None
                        })
                    
                    self.pipeline.log_info(self.calculator_name, f"Created {created_count} new BuildingProperties, updated {updated_count} existing")
                    
            except Exception as e:
                self.pipeline.log_error(self.calculator_name, f"Failed to save to database: {str(e)}")
                return None

            # Create result with all building properties
            building_props = {
                'project_id': project_id,
                'scenario_id': scenario_id,
                'building_properties': building_properties_list
            }

            # Store result
            self.pipeline.store_result('building_props', building_props)

            self.pipeline.log_calculation_success(self.calculator_name, 'init', f"Initialized {len(building_properties_list)} building properties")
            return building_props
            
        except Exception as e:
            self.pipeline.log_calculation_failure(self.calculator_name, 'init', str(e))
            return None

    def save_to_database(self) -> bool:
        """Save building properties to database"""
        try:
            # Import Django models
            try:
                from cim_wizard.models import BuildingProperties
            except ImportError:
                self.pipeline.log_warning(self.calculator_name, "Django models not available - skipping database save")
                return False

            # Get building_props data from the pipeline
            building_props_data = self.pipeline.get_feature_safely('building_props', calculator_name=self.calculator_name)
            if not building_props_data:
                self.pipeline.log_error(self.calculator_name, "No building_props data to save")
                return False

            # Get the first building property
            if not building_props_data.get('building_properties'):
                self.pipeline.log_error(self.calculator_name, "No building properties in data")
                return False

            prop = building_props_data['building_properties'][0]
            
            # Update BuildingProperties
            try:
                building_props = BuildingProperties.objects.get(
                    building_id=prop['building_id'],
                    project_id=building_props_data['project_id'],
                    scenario_id=building_props_data['scenario_id'],
                    lod=prop['lod']
                )
                # Update any properties that have changed
                for key, value in prop.items():
                    if hasattr(building_props, key) and getattr(building_props, key) != value:
                        setattr(building_props, key, value)
                building_props.save()
                self.pipeline.log_info(self.calculator_name, f"Updated BuildingProperties for building {prop['building_id']}")
                return True
            except BuildingProperties.DoesNotExist:
                self.pipeline.log_error(self.calculator_name, f"BuildingProperties not found for building {prop['building_id']}")
                return False
            except Exception as e:
                self.pipeline.log_error(self.calculator_name, f"Failed to update BuildingProperties: {str(e)}")
                return False
                
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Error in save_to_database: {str(e)}")
            return False

    def _serialize_building_props(self, building_props):
        """Convert BuildingProperties object to dictionary"""
        if isinstance(building_props, dict):
            return building_props
            
        return {
            'project_id': building_props.project_id,
            'scenario_id': building_props.scenario_id,
            'building_properties': [{
                'building_id': building_props.building_id,
                'scenario_id': building_props.scenario_id,
                'lod': building_props.lod,
                'height': building_props.height,
                'area': building_props.area,
                'volume': building_props.volume,
                'number_of_floors': building_props.number_of_floors
            }]
        }
    
    def _calculate_polygon_area(self, geometry: Dict[str, Any]) -> float:
        """Calculate approximate area of polygon geometry"""
        if geometry.get('type') != 'Polygon':
            return 0.0
        
        coordinates = geometry.get('coordinates', [])
        if not coordinates:
            return 0.0
        
        # Simple shoelace formula for polygon area
        coords = coordinates[0]  # Outer ring
        area = 0.0
        n = len(coords)
        
        for i in range(n - 1):
            area += coords[i][0] * coords[i + 1][1]
            area -= coords[i + 1][0] * coords[i][1]
        
        return abs(area) / 2.0
    
    def _calculate_polygon_perimeter(self, geometry: Dict[str, Any]) -> float:
        """Calculate approximate perimeter of polygon geometry"""
        if geometry.get('type') != 'Polygon':
            return 0.0
        
        coordinates = geometry.get('coordinates', [])
        if not coordinates:
            return 0.0
        
        coords = coordinates[0]  # Outer ring
        perimeter = 0.0
        
        for i in range(len(coords) - 1):
            x1, y1 = coords[i]
            x2, y2 = coords[i + 1]
            perimeter += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        
        return perimeter 