"""
Scenario Geo Calculator - Independent class with pipeline executor injection
"""
from typing import Optional, Dict, Any


class ScenarioGeoCalculator:
    """Calculate scenario geometry data"""
    
    def __init__(self, pipeline_executor):
        self.pipeline = pipeline_executor
        self.data_manager = pipeline_executor.data_manager
        self.calculator_name = self.__class__.__name__
    
    def calculate_from_scenario_geo(self) -> Optional[Dict[str, Any]]:
        """Create scenario geometry from UI project boundary input"""
        # Validate that we have scenario_geo data (from UI POST request)
        scenario_geo_input = self.pipeline.get_feature_safely('scenario_geo', calculator_name=self.calculator_name)
        if not self.pipeline.validate_dict(scenario_geo_input, "scenario_geo", self.calculator_name, ['type', 'geometry', 'properties']):
            return None
        
        self.pipeline.log_info(self.calculator_name, "Creating scenario geometry from UI project boundary input")
        
        try:
            import uuid
            
            # Get project_id and scenario_id from data_manager (already set by API route)
            project_id = getattr(self.data_manager, 'project_id', None)
            scenario_id = getattr(self.data_manager, 'scenario_id', None)
            
            # If not provided, generate new ones
            if not project_id:
                project_id = str(uuid.uuid4())
            if not scenario_id:
                scenario_id = project_id  # Default to same as project for baseline
            
            # Extract geometry and properties from GeoJSON Feature
            geometry = scenario_geo_input.get('geometry', {})
            properties = scenario_geo_input.get('properties', {})
            
            # Validate geometry
            if not self.pipeline.validate_geometry(geometry, "project_boundary", self.calculator_name):
                return None
            
            # Calculate project center from geometry or use provided map center
            project_center = None
            if 'map_center_lon' in properties and 'map_center_lat' in properties:
                project_center = {
                    'type': 'Point',
                    'coordinates': [
                        float(properties['map_center_lon']),
                        float(properties['map_center_lat'])
                    ]
                }
            else:
                # Calculate centroid from polygon coordinates
                coords = geometry.get('coordinates', [[]])[0]
                if coords:
                    center_lon = sum(coord[0] for coord in coords) / len(coords)
                    center_lat = sum(coord[1] for coord in coords) / len(coords)
                    project_center = {
                        'type': 'Point',
                        'coordinates': [center_lon, center_lat]
                    }
            
            # Get project and scenario names from data_manager
            project_name = getattr(self.data_manager, 'project_name', f'Project_{project_id[:8]}')
            scenario_name = getattr(self.data_manager, 'scenario_name', 'baseline')
            
            # Build scenario geometry result
            scenario_geo = {
                'scenario_id': scenario_id,
                'project_id': project_id,
                'project_name': project_name,
                'scenario_name': scenario_name,
                'project_boundary': geometry,
                'project_center': project_center,
                'project_crs': properties.get('crs', 4326),
                'project_zoom': properties.get('zoom', 15),
                'created_from': 'ui_project_boundary'
            }
            
            # Ensure data manager has the IDs
            self.data_manager.scenario_id = scenario_id
            self.data_manager.project_id = project_id
            
            self.pipeline.log_calculation_success(self.calculator_name, "scenario_geo_from_ui", scenario_geo, 
                                        f"Project ID: {project_id[:8]}..., Scenario ID: {scenario_id[:8]}...")
            return scenario_geo
            
        except Exception as e:
            self.pipeline.log_calculation_failure(self.calculator_name, "scenario_geo_from_ui", str(e))
            return None
    
    def calculate_from_building_geo(self):
        """Alias for calculate_from_buildings_geo"""
        return self.calculate_from_buildings_geo()
    
    def calculate_from_buildings_geo(self):
        """Calculate scenario geometry from building geometry"""
        try:
            self.pipeline.log_info(self.calculator_name, "Starting calculate_from_buildings_geo")
            
            # Get building_geo from pipeline
            building_geo = self.pipeline.get_feature_safely('building_geo')
            self.pipeline.log_info(self.calculator_name, f"Retrieved building_geo: {building_geo is not None}")
            
            if not building_geo:
                self.pipeline.log_error(self.calculator_name, "No building_geo data available")
                return None

            # Extract building_id and lod from building_geo
            if not building_geo.get('buildings'):
                self.pipeline.log_error(self.calculator_name, "No buildings in building_geo data")
                return None
        
            building = building_geo['buildings'][0]  # Get first building
            self.pipeline.log_info(self.calculator_name, f"First building: {building}")
            
            building_id = building.get('building_id')
            lod = building.get('lod', 0)
            
            self.pipeline.log_info(self.calculator_name, f"Building ID: {building_id}, LOD: {lod}")
            
            # Generate project_id and scenario_id if not present
            import uuid
            project_id = str(uuid.uuid4())  # Always generate new UUID
            scenario_id = str(uuid.uuid4())  # Always generate new UUID
            
            self.pipeline.log_info(self.calculator_name, f"Generated project_id: {project_id}, scenario_id: {scenario_id}")

            if not building_id:
                self.pipeline.log_error(self.calculator_name, "No building_id in building_geo data")
                return None

            # Get building geometry
            building_geom = building.get('geometry')
            if not building_geom:
                self.pipeline.log_error(self.calculator_name, "No geometry in building_geo data")
                return None
            
            # Get project_name and scenario_name from inputs
            project_name = self.pipeline.get_feature_safely('project_name') or f'Project from Buildings {building_id[:8]}'
            scenario_name = self.pipeline.get_feature_safely('scenario_name') or f'Scenario from Building {building_id[:8]}'
            
            self.pipeline.log_info(self.calculator_name, f"Using project_name: {project_name}, scenario_name: {scenario_name}")

            try:
                # Create project boundary by creating envelope around all building footprints
                from shapely.geometry import shape, mapping
                import geopandas as gpd
                
                self.pipeline.log_info(self.calculator_name, "Starting geometry processing")
                
                # Convert all building geometries to Shapely objects
                building_geoms = []
                for b in building_geo['buildings']:
                    if 'geometry' in b:
                        try:
                            geom = shape(b['geometry'])
                            building_geoms.append(geom)
                            self.pipeline.log_info(self.calculator_name, f"Successfully converted building geometry to Shapely")
                        except Exception as e:
                            self.pipeline.log_error(self.calculator_name, f"Error converting building geometry: {str(e)}")
                            continue
                
                if not building_geoms:
                    self.pipeline.log_error(self.calculator_name, "No valid building geometries found")
                    return None
                    
                self.pipeline.log_info(self.calculator_name, f"Successfully converted {len(building_geoms)} building geometries")
                
                # Create GeoSeries and get envelope
                gdf = gpd.GeoSeries(building_geoms)
                project_boundary = gdf.unary_union.convex_hull
                
                # Convert back to GeoJSON
                project_boundary_geojson = mapping(project_boundary)
                
                self.pipeline.log_info(self.calculator_name, "Successfully created project boundary using convex hull")

                # Create scenario geometry
                scenario_geo = {
                    'project_id': project_id,
                    'scenario_id': scenario_id,
                    'building_id': building_id,
                    'lod': lod,
                    'geometry': building_geom,
                    'data_source': 'building_geo',
                    'created_from': 'building_geo',
                    'project_name': project_name,
                    'scenario_name': scenario_name,
                    'project_boundary': project_boundary_geojson
                }

                self.pipeline.log_info(self.calculator_name, "Created scenario_geo object")

                # Store result
                self.pipeline.store_result('scenario_geo', scenario_geo)
                self.pipeline.log_info(self.calculator_name, "Stored scenario_geo result")
                
                # Save to database
                try:
                    from cim_wizard.models import Project, Scenario
                    self.pipeline.log_info(self.calculator_name, "Attempting to save to database")
                    
                    # Create or update project
                    project, project_created = Project.objects.update_or_create(
                        project_id=project_id,
                        defaults={
                            'name': project_name,
                            'project_boundary': project_boundary_geojson
                        }
                    )
                    
                    # Create or update scenario
                    scenario, scenario_created = Scenario.objects.update_or_create(
                        scenario_id=scenario_id,
                        defaults={
                            'project_id': project,
                            'name': scenario_name,
                            'building_id': building_id,
                            'lod': lod
                        }
                    )
                    
                    self.pipeline.log_info(self.calculator_name, f"{'Created' if project_created else 'Updated'} project and scenario in database")
                except Exception as e:
                    self.pipeline.log_error(self.calculator_name, f"Failed to save to database: {str(e)}")
                    # Don't return None here, continue with the result

                self.pipeline.log_calculation_success(self.calculator_name, 'calculate_from_buildings_geo', scenario_geo)
                return scenario_geo  # Always return the result even if database save fails

            except Exception as e:
                self.pipeline.log_error(self.calculator_name, f"Error in geometry processing: {str(e)}")
                return None
            
        except Exception as e:
            self.pipeline.log_calculation_failure(self.calculator_name, 'calculate_from_buildings_geo', str(e))
            return None
    
    def save_to_database(self):
        """Save scenario geometry data to database"""
        try:
            # Import Django models
            try:
                from cim_wizard.models import Project_Scenario
                from django.contrib.gis.geos import GEOSGeometry
                import json
            except ImportError:
                self.pipeline.log_warning(self.calculator_name, "Django models not available - skipping database save")
                return False

            # Get scenario_geo data from data manager
            scenario_data = self.pipeline.get_feature_safely('scenario_geo', calculator_name=self.calculator_name)
            if not scenario_data:
                self.pipeline.log_error(self.calculator_name, "No scenario_geo data to save")
                return False
            
            self.pipeline.log_info(self.calculator_name, f"Saving scenario_geo with project_id: {scenario_data.get('project_id')}, scenario_id: {scenario_data.get('scenario_id')}")
            
            # Use both project_id and scenario_id as per the model's unique_together constraint
            scenario_obj, created = Project_Scenario.objects.get_or_create(
                project_id=scenario_data.get('project_id'),
                scenario_id=scenario_data.get('scenario_id'),
                defaults={
                    'project_name': scenario_data.get('project_name', ''),
                    'scenario_name': scenario_data.get('scenario_name', ''),
                    'project_crs': scenario_data.get('project_crs', 4326),
                    'project_zoom': scenario_data.get('project_zoom', 15)
                }
            )
            
            # Update geometry fields if available
            if 'project_boundary' in scenario_data:
                scenario_obj.project_boundary = GEOSGeometry(json.dumps(scenario_data['project_boundary']))
            if 'project_center' in scenario_data:
                scenario_obj.project_center = GEOSGeometry(json.dumps(scenario_data['project_center']))
            
            scenario_obj.save()
            
            self.pipeline.log_info(self.calculator_name, f"{'Created' if created else 'Updated'} scenario in database")
            return True
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to save to database: {str(e)}")
            return False