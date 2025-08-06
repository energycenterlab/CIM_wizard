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
        """Calculate census boundary using census API"""
        # Get required inputs at the start
        scenario_geo = self.pipeline.get_feature_safely('scenario_geo', calculator_name=self.calculator_name)
        project_id = getattr(self.data_manager, 'project_id', None)
        scenario_id = getattr(self.data_manager, 'scenario_id', None)
        
        # Validate required inputs
        if not project_id or not scenario_id:
            self.pipeline.log_error(self.calculator_name, "Missing project_id or scenario_id")
            return None
        
        # Get census service URL from data manager's configuration
        census_service_url = self.data_manager.configuration.get('services', {}).get('census_gateway', {}).get('url')
        if not census_service_url:
            self.pipeline.log_error(self.calculator_name, "Census service URL not found in configuration")
            return None
        
        if not self.pipeline.validate_input(scenario_geo, "scenario_geo", self.calculator_name):
            return None
        
        self.pipeline.log_info(self.calculator_name, f"Calculating census boundary from census API at {census_service_url}")
        
        try:
            # Extract polygon coordinates from scenario_geo
            if 'project_boundary' in scenario_geo:
                polygon_coords = scenario_geo['project_boundary']['coordinates'][0]
            elif 'geometry' in scenario_geo:
                polygon_coords = scenario_geo['geometry']['coordinates'][0]
            else:
                self.pipeline.log_error(self.calculator_name, "No geometry or project_boundary found in scenario_geo")
                return None
            
            # Prepare request to census API
            params = {
                'polygonArray': json.dumps(polygon_coords)
            }
            
            # Make request to census API
            response = requests.get(census_service_url, params=params)
            response.raise_for_status()
            
            # Parse response
            census_data = response.json()
            
            if census_data['type'] != 'FeatureCollection' or not census_data['features']:
                self.pipeline.log_error(self.calculator_name, "Invalid response from census API")
                return None
            
            # Create convex hull from all census zones
            census_zones = []
            geometries = []
            
            for feature in census_data['features']:
                # Store census zone data
                census_zones.append({
                    'zone_id': feature['properties'].get('SEZ2011'),
                    'properties': feature['properties'],
                    'geometry': feature['geometry']
                })
                
                # Convert to shapely geometry for convex hull calculation
                geom = shape(feature['geometry'])
                geometries.append(geom)
            
            # Create minimal boundary from all geometries (0.1% buffer instead of convex hull)
            if geometries:
                combined_geom = unary_union(geometries)
                # Use minimal buffer (0.1%) instead of convex hull to reduce area expansion
                buffer_distance = 0.000001  # 0.0001% in degrees (roughly ~110m at 45°N)
                minimal_boundary = combined_geom.buffer(buffer_distance)
                
                # Create final census boundary object
                census_boundary = {
                    'type': 'Feature',
                    'geometry': mapping(minimal_boundary),
                    'properties': {
                        'census_zones': census_zones,
                        'total_zones': len(census_zones),
                        'data_source': 'census_api',
                        'project_id': project_id,
                        'scenario_id': scenario_id
                    }
                }
                
                # Save to database
                if self.save_to_database(census_boundary, project_id, scenario_id):
                    self.pipeline.log_info(self.calculator_name, f"Successfully calculated census boundary with {len(census_zones)} zones")
                    return census_boundary
                else:
                    self.pipeline.log_error(self.calculator_name, "Failed to save census boundary to database")
                    return None
            
            return None
            
        except requests.exceptions.RequestException as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to call census API: {str(e)}")
            return None
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