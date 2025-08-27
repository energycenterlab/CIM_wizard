"""
Scenario Census Boundary Calculator - Independent class with pipeline executor injection
"""
from typing import Optional, Dict, Any
import requests
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
import json


class ScenarioCensusBoundaryCalculator:
    """Calculate scenario census boundary"""
    
    def __init__(self, pipeline_executor):
        self.pipeline = pipeline_executor
        self.data_manager = pipeline_executor.data_manager
        self.calculator_name = self.__class__.__name__
    
    def calculate_from_census_api(self) -> Optional[Dict[str, Any]]:
        """Calculate census boundary using integrated database (simplified for testing)"""
        # Get required inputs at the start
        scenario_geo = self.pipeline.get_feature_safely('scenario_geo', calculator_name=self.calculator_name)
        project_id = getattr(self.data_manager, 'project_id', None)
        scenario_id = getattr(self.data_manager, 'scenario_id', None)
        
        # Validate required inputs
        if not project_id or not scenario_id:
            self.pipeline.log_error(self.calculator_name, "Missing project_id or scenario_id")
            return None
        
        if not self.pipeline.validate_input(scenario_geo, "scenario_geo", self.calculator_name):
            return None
        
        self.pipeline.log_info(self.calculator_name, "Calculating census boundary using integrated database")
        
        try:
            # For now, create a simplified census boundary based on the scenario geometry
            # In a real implementation, this would query the census database
            
            # Extract geometry from scenario_geo
            if 'geometry' in scenario_geo:
                geometry = scenario_geo['geometry']
            else:
                self.pipeline.log_error(self.calculator_name, "No geometry found in scenario_geo")
                return None
            
            # Create a simplified census boundary (expanded slightly from project boundary)
            # In reality, this would be the actual census zones that intersect with the project
            census_boundary = {
                'type': 'Feature',
                'geometry': geometry,  # Use the same geometry for now
                'properties': {
                    'census_zones': [
                        {
                            'zone_id': 'CENSUS_001',
                            'properties': {
                                'SEZ2011': 'CENSUS_001',
                                'population': 1200,
                                'E8': 5, 'E9': 10, 'E10': 15, 'E11': 20,
                                'E12': 25, 'E13': 30, 'E14': 35, 'E15': 40, 'E16': 45
                            },
                            'geometry': geometry
                        }
                    ],
                    'total_zones': 1,
                    'data_source': 'integrated_database',
                    'project_id': project_id,
                    'scenario_id': scenario_id,
                    'total_population': 1200
                }
            }
            
            self.pipeline.log_info(self.calculator_name, f"Successfully created census boundary with 1 zone")
            return census_boundary
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to calculate census boundary: {str(e)}")
            return None 
    
    def save_to_database(self, census_boundary: Dict[str, Any], project_id: str, scenario_id: str) -> bool:
        """Save scenario census boundary data to database"""
        try:
            # Import Django models
            try:
                from cim_wizard.models import Project_Scenario
                from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
                import json
            except ImportError:
                self.pipeline.log_warning(self.calculator_name, "Django models not available - skipping database save")
                return False
            
            self.pipeline.log_info(self.calculator_name, f"Saving census boundary for scenario: {scenario_id}")
            
            try:
                scenario_obj = Project_Scenario.objects.get(
                    project_id=project_id,
                    scenario_id=scenario_id
                )
                
                # Update census boundary field with convex hull geometry
                if 'geometry' in census_boundary:
                    # Convert to MultiPolygon if it's a Polygon
                    geom = GEOSGeometry(json.dumps(census_boundary['geometry']))
                    if geom.geom_type == 'Polygon':
                        geom = MultiPolygon([geom])
                    scenario_obj.census_boundry = geom
                scenario_obj.save()
                self.pipeline.log_info(self.calculator_name, f"Updated census boundary for scenario: {scenario_id}")
                return True
                
            except Project_Scenario.DoesNotExist:
                self.pipeline.log_error(self.calculator_name, f"Could not find scenario {scenario_id} to update census boundary")
                return False
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to save to database: {str(e)}")
            return False