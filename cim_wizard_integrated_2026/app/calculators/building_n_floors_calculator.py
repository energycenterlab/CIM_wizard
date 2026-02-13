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
            building_heights = self.pipeline.get_feature_safely('building_height', calculator_name=self.calculator_name)  # Note: singular 'building_height'
            filter_res_data = self.pipeline.get_feature_safely('filter_res', calculator_name=self.calculator_name)
            
            if not building_geo:
                self.pipeline.log_error(self.calculator_name, "No building_geo data available")
                return None
            
            if not building_heights:
                self.pipeline.log_error(self.calculator_name, "No building_height data available")
                return None
            
            if not filter_res_data:
                self.pipeline.log_error(self.calculator_name, "No filter_res data available - floor calculation requires residential filter first")
                return None
            
            # Get buildings from building_geo
            buildings = building_geo.get('buildings', [])
            if not buildings:
                self.pipeline.log_error(self.calculator_name, "No buildings found in building_geo")
                return None
            
            # Get filter_res values (residential filter)
            filter_res_values = filter_res_data.get('filter_res', [])
            if not filter_res_values:
                self.pipeline.log_error(self.calculator_name, "No filter_res values found in data")
                return None
            
            project_id = building_geo.get('project_id')
            scenario_id = building_geo.get('scenario_id')
            
            # Count residential buildings
            residential_count = sum(1 for f in filter_res_values if f is True)
            self.pipeline.log_info(self.calculator_name, f"Estimating number of floors for {residential_count} residential buildings (out of {len(buildings)} total)")
            
            # Calculate number of floors only for residential buildings
            building_floors = []
            processed_count = 0
            skipped_count = 0
            last_five_logs = []  # Track last 5 for summary
            
            for i, building in enumerate(buildings):
                building_id = building.get('building_id')
                
                # Check if this building is residential (filter_res = True)
                is_residential = filter_res_values[i] if i < len(filter_res_values) else False
                
                if not is_residential:
                    # Skip non-residential buildings - set floors to None
                    building_floors.append(None)
                    skipped_count += 1
                    continue
                
                # Get height for this building
                # Handle both list and dict structures for building_heights
                if isinstance(building_heights, list) and i < len(building_heights):
                    height = building_heights[i]
                elif isinstance(building_heights, dict) and str(i) in building_heights:
                    height = building_heights[str(i)]
                elif isinstance(building_heights, dict) and i in building_heights:
                    height = building_heights[i]
                else:
                    height = 12.0  # Default height
                    self.pipeline.log_warning(self.calculator_name, f"Using default height for building {i}: {type(building_heights)}")
                
                if height is None or height <= 0:
                    self.pipeline.log_warning(self.calculator_name, f"Skipping building {building_id} - invalid height: {height}")
                    continue

                # Calculate number of floors
                number_of_floors = math.floor(height / 3)
                building_floors.append(number_of_floors)
                processed_count += 1
                
                # Track last 5 for logging
                log_msg = f"Building {building_id}: {number_of_floors} floors (height: {height:.1f}m)"
                last_five_logs.append(log_msg)
                if len(last_five_logs) > 5:
                    last_five_logs.pop(0)
            
            if processed_count == 0:
                self.pipeline.log_error(self.calculator_name, "No buildings were processed successfully")
                return None
            
            # Log last 5 samples
            if last_five_logs:
                self.pipeline.log_info(self.calculator_name, "Last 5 building floor counts:")
                for log_msg in last_five_logs:
                    self.pipeline.log_info(self.calculator_name, f"  {log_msg}")

            # Create result
            result = {
                'project_id': project_id,
                'scenario_id': scenario_id,
                'building_floors': building_floors,
                'processed_count': processed_count
            }

            # Store result in data manager
            self.data_manager.set_feature('building_n_floors', result)
            self.data_manager.set_feature('building_floors', building_floors)  # Also store list
            
            # Save to database immediately
            db_session = getattr(self.data_manager, 'db_session', None)
            if db_session and project_id and scenario_id:
                self._save_floors_to_database(db_session, buildings, building_floors, project_id, scenario_id)

            self.pipeline.log_calculation_success(self.calculator_name, 'estimate_by_height', f"Estimated floors for {processed_count} residential buildings (skipped {skipped_count} non-residential)")
            return result

        except Exception as e:
            self.pipeline.log_calculation_failure(self.calculator_name, 'estimate_by_height', str(e))
            return None

    def _save_floors_to_database(self, db_session, buildings, floors, project_id, scenario_id):
        """Save calculated floor counts to database"""
        try:
            from app.models.vector import BuildingProperties
            from sqlalchemy import and_
            
            updated_count = 0
            created_count = 0
            
            for building, n_floors in zip(buildings, floors):
                building_id = building.get('building_id')
                if not building_id:
                    continue
                
                lod = building.get('lod', 0)
                
                try:
                    # Query with all composite key fields
                    props = db_session.query(BuildingProperties).filter(
                        and_(
                            BuildingProperties.building_id == building_id,
                            BuildingProperties.project_id == project_id,
                            BuildingProperties.scenario_id == scenario_id,
                            BuildingProperties.lod == lod
                        )
                    ).first()
                    
                    if props:
                        if props.number_of_floors != n_floors:  # Only update if different
                            props.number_of_floors = n_floors
                            db_session.add(props)  # Mark as dirty
                            updated_count += 1
                    else:
                        # Create if doesn't exist
                        new_props = BuildingProperties(
                            building_id=building_id,
                            project_id=project_id,
                            scenario_id=scenario_id,
                            lod=lod,
                            number_of_floors=n_floors
                        )
                        db_session.add(new_props)
                        created_count += 1
                
                except Exception as e:
                    self.pipeline.log_warning(self.calculator_name, 
                        f"Failed to save floors for building {building_id}: {str(e)}")
                    db_session.rollback()
                    raise
            
            if updated_count > 0 or created_count > 0:
                db_session.commit()
                db_session.flush()  # Force write
                self.pipeline.log_info(self.calculator_name, 
                    f"Database commit complete: {updated_count} updated, {created_count} created")
            else:
                self.pipeline.log_warning(self.calculator_name, "No floor count changes to save")
            
        except Exception as e:
            db_session.rollback()
            self.pipeline.log_error(self.calculator_name, f"Failed to save floors to database: {str(e)}")
            raise
    
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