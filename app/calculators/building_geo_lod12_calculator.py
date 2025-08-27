"""
Building Geo LoD 1.2 Calculator - Generate 3DCityDB-compatible building surfaces
"""
from typing import Optional, Dict, Any, List
import math
import json


class BuildingGeoLod12Calculator:
    """Calculate LoD 1.2 building surfaces from footprint and height for 3DCityDB compatibility"""
    
    def __init__(self, pipeline_executor):
        self.pipeline = pipeline_executor
        self.data_manager = pipeline_executor.data_manager
        self.calculator_name = self.__class__.__name__
    
    def by_footprint_height(self) -> Optional[Dict[str, Any]]:
        """Generate LoD 1.2 semantic surfaces (simplified for pipeline)"""
        try:
            # Get required data
            building_geo = self.pipeline.get_feature_safely('building_geo', calculator_name=self.calculator_name)
            building_heights = self.pipeline.get_feature_safely('building_height', calculator_name=self.calculator_name)
            
            if not building_geo:
                self.pipeline.log_error(self.calculator_name, "No building_geo data available")
                return None
            
            self.pipeline.log_info(self.calculator_name, "Generating LoD 1.2 surfaces for buildings")
            
            # Get buildings
            buildings = building_geo.get('buildings', [])
            if not buildings:
                self.pipeline.log_error(self.calculator_name, "No buildings found in building_geo")
                return None
            
            # Generate LoD 1.2 surfaces for all buildings
            building_lod12_data = []
            for i, building in enumerate(buildings):
                building_id = building.get('building_id')
                geometry = building.get('geometry', {})
                
                # Get height for this building
                height = building_heights[i] if building_heights and i < len(building_heights) else 12.0
                
                # Create simplified LoD 1.2 surfaces
                surfaces = {
                    'wall_surfaces': [{'type': 'WallSurface', 'height': height}],
                    'roof_surface': {'type': 'RoofSurface', 'height': height},
                    'ground_surface': {'type': 'GroundSurface', 'height': 0}
                }
                
                lod12_data = {
                    'building_id': building_id,
                    'surfaces': surfaces,
                    'metadata': {
                        'total_surfaces': 3,  # walls + roof + floor
                        'wall_count': 1,
                        'building_height': height,
                        'surface_types': ['WallSurface', 'RoofSurface', 'GroundSurface'],
                        'coordinate_system': 'EPSG:4326',
                        'lod_specification': '1.2',
                        'citydb_compatible': True,
                        'generated_from': 'simplified_pipeline'
                    }
                }
                
                building_lod12_data.append(lod12_data)
            
            # Create result
            result = {
                'project_id': building_geo.get('project_id'),
                'scenario_id': building_geo.get('scenario_id'),
                'building_lod12_data': building_lod12_data,
                'total_buildings': len(building_lod12_data),
                'lod': 1.2,
                'generation_method': 'simplified_pipeline'
            }
            
            # Store in data manager
            self.data_manager.set_feature('building_geo_lod12', result)
            
            self.pipeline.log_calculation_success(
                self.calculator_name, 
                'by_footprint_height', 
                result,
                f"Generated LoD 1.2 surfaces for {len(building_lod12_data)} buildings"
            )
            
            return result
            
        except Exception as e:
            self.pipeline.log_calculation_failure(self.calculator_name, 'by_footprint_height', str(e))
            return None
    
    def _get_building_geometry_from_database(self, building_id: str, lod: int) -> Optional[Dict[str, Any]]:
        """Get building geometry from database"""
        try:
            from cim_wizard.models import Building
            from django.contrib.gis.geos import GEOSGeometry
            import json
            
            try:
                building = Building.objects.get(building_id=building_id, lod=lod)
                
                # Convert GEOSGeometry to GeoJSON
                geom_geojson = json.loads(building.building_geometry.geojson)
                
                self.pipeline.log_info(
                    self.calculator_name, 
                    f"Retrieved building geometry from database for building {building_id}"
                )
                return geom_geojson
                
            except Building.DoesNotExist:
                self.pipeline.log_error(
                    self.calculator_name, 
                    f"Building with building_id={building_id} and lod={lod} not found in database"
                )
                return None
                
        except Exception as e:
            self.pipeline.log_error(
                self.calculator_name, 
                f"Failed to get building geometry from database: {str(e)}"
            )
            return None
    
    def _get_building_height_from_database(self, building_id: str, project_id: str, scenario_id: str, lod: int) -> Optional[float]:
        """Get building height from database"""
        try:
            from cim_wizard.models import BuildingProperties
            
            try:
                building_props = BuildingProperties.objects.get(
                    building_id=building_id,
                    project_id=project_id,
                    scenario_id=scenario_id,
                    lod=lod
                )
                
                if building_props.height is None or building_props.height <= 0:
                    self.pipeline.log_error(
                        self.calculator_name, 
                        f"Building {building_id} has invalid height: {building_props.height}"
                    )
                    return None
                
                self.pipeline.log_info(
                    self.calculator_name, 
                    f"Retrieved building height {building_props.height}m from database for building {building_id}"
                )
                return building_props.height
                
            except BuildingProperties.DoesNotExist:
                self.pipeline.log_error(
                    self.calculator_name, 
                    f"BuildingProperties for building_id={building_id}, project_id={project_id}, scenario_id={scenario_id}, lod={lod} not found in database"
                )
                return None
                
        except Exception as e:
            self.pipeline.log_error(
                self.calculator_name, 
                f"Failed to get building height from database: {str(e)}"
            )
            return None
    
    def _extract_footprint_from_context(self, building_geo: Dict[str, Any], building_id: str) -> Optional[Dict[str, Any]]:
        """Extract building footprint geometry from building_geo context"""
        try:
            buildings = building_geo.get('buildings', [])
            
            for building in buildings:
                if building.get('building_id') == building_id:
                    footprint_geometry = building.get('geometry')
                    if footprint_geometry:
                        self.pipeline.log_info(
                            self.calculator_name, 
                            f"Retrieved building footprint from context for building {building_id}"
                        )
                        return footprint_geometry
            
            self.pipeline.log_error(
                self.calculator_name, 
                f"Building footprint not found in context for building_id: {building_id}"
            )
            return None
            
        except Exception as e:
            self.pipeline.log_error(
                self.calculator_name, 
                f"Failed to extract footprint from context: {str(e)}"
            )
            return None
    
    def _extract_height_from_context(self, building_height: Dict[str, Any], building_id: str) -> Optional[float]:
        """Extract building height from building_height context"""
        try:
            # Handle different building_height formats
            if isinstance(building_height, (int, float)):
                return building_height
            
            if isinstance(building_height, dict):
                building_props = building_height.get('building_properties', [])
                for prop in building_props:
                    if prop.get('building_id') == building_id:
                        height_value = prop.get('height')
                        if height_value and height_value > 0:
                            self.pipeline.log_info(
                                self.calculator_name, 
                                f"Retrieved building height {height_value}m from context for building {building_id}"
                            )
                            return height_value
            
            self.pipeline.log_error(
                self.calculator_name, 
                f"Valid height not found in context for building_id: {building_id}"
            )
            return None
            
        except Exception as e:
            self.pipeline.log_error(
                self.calculator_name, 
                f"Failed to extract height from context: {str(e)}"
            )
            return None
    
    def _generate_lod12_surfaces(self, footprint_geometry: Dict[str, Any], height: float) -> Dict[str, Any]:
        """Generate LoD 1.2 semantic surfaces from footprint and height"""
        try:
            if footprint_geometry.get('type') != 'Polygon':
                self.pipeline.log_error(self.calculator_name, f"Unsupported geometry type: {footprint_geometry.get('type')}")
                return None
            
            coordinates = footprint_geometry.get('coordinates', [])
            if not coordinates or len(coordinates) == 0:
                self.pipeline.log_error(self.calculator_name, "Invalid footprint coordinates")
                return None
            
            # Get exterior ring coordinates
            exterior_ring = coordinates[0]
            if len(exterior_ring) < 4:  # Need at least 4 points for a closed polygon
                self.pipeline.log_error(self.calculator_name, "Insufficient coordinates for polygon")
                return None
            
            # Ensure polygon is closed
            if exterior_ring[0] != exterior_ring[-1]:
                exterior_ring.append(exterior_ring[0])
            
            # Generate surfaces
            surfaces = {
                'wall_surfaces': [],
                'roof_surface': None,
                'ground_surface': None,
                'building_volume': None
            }
            
            # 1. Generate Wall Surfaces
            wall_surfaces = self._generate_wall_surfaces(exterior_ring, height)
            surfaces['wall_surfaces'] = wall_surfaces
            
            # 2. Generate Roof Surface (top surface at height)
            roof_surface = self._generate_roof_surface(exterior_ring, height)
            surfaces['roof_surface'] = roof_surface
            
            # 3. Generate Ground Surface (bottom surface at ground level)
            ground_surface = self._generate_ground_surface(exterior_ring)
            surfaces['ground_surface'] = ground_surface
            
            # 4. Calculate building volume for validation
            area = self._calculate_polygon_area(footprint_geometry)
            volume = area * height
            surfaces['building_volume'] = {
                'volume_m3': volume,
                'base_area_m2': area,
                'height_m': height
            }
            
            self.pipeline.log_info(
                self.calculator_name, 
                f"Generated {len(wall_surfaces)} wall surfaces, 1 roof surface, 1 ground surface"
            )
            
            return surfaces
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to generate LoD 1.2 surfaces: {str(e)}")
            return None
    
    def _generate_wall_surfaces(self, exterior_ring: List[List[float]], height: float) -> List[Dict[str, Any]]:
        """Generate wall surfaces for each edge of the building footprint"""
        wall_surfaces = []
        
        try:
            # Process each edge of the polygon
            for i in range(len(exterior_ring) - 1):  # -1 because last point equals first point
                p1 = exterior_ring[i]
                p2 = exterior_ring[i + 1]
                
                # Create wall surface as a vertical rectangle
                wall_coordinates = [
                    [p1[0], p1[1], 0.0],        # bottom-left
                    [p2[0], p2[1], 0.0],        # bottom-right
                    [p2[0], p2[1], height],     # top-right
                    [p1[0], p1[1], height],     # top-left
                    [p1[0], p1[1], 0.0]         # close polygon
                ]
                
                # Calculate wall properties
                wall_length = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
                wall_area = wall_length * height
                
                # Calculate orientation (azimuth from north)
                dx = p2[0] - p1[0]
                dy = p2[1] - p1[1]
                azimuth = math.degrees(math.atan2(dx, dy))
                if azimuth < 0:
                    azimuth += 360
                
                wall_surface = {
                    'surface_id': f"wall_{i+1}",
                    'surface_type': 'WallSurface',
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [wall_coordinates]
                    },
                    'properties': {
                        'wall_index': i + 1,
                        'area_m2': wall_area,
                        'height_m': height,
                        'length_m': wall_length,
                        'azimuth_degrees': azimuth,
                        'orientation': self._get_cardinal_direction(azimuth),
                        'lod': 1.2,
                        'surface_material': 'unknown',  # For TABULA typology assignment
                        'construction_type': 'unknown'   # For TABULA typology assignment
                    },
                    'semantic': {
                        'surface_class': 'WallSurface',
                        'building_element': 'exterior_wall',
                        'thermal_properties': {
                            'u_value': None,  # To be filled by TABULA calculator
                            'thermal_resistance': None,
                            'thermal_capacity': None
                        }
                    }
                }
                
                wall_surfaces.append(wall_surface)
            
            return wall_surfaces
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to generate wall surfaces: {str(e)}")
            return []
    
    def _generate_roof_surface(self, exterior_ring: List[List[float]], height: float) -> Dict[str, Any]:
        """Generate roof surface (top surface at building height)"""
        try:
            # Create roof coordinates at the specified height
            roof_coordinates = []
            for point in exterior_ring:
                roof_coordinates.append([point[0], point[1], height])
            
            # Calculate roof area
            roof_area = self._calculate_polygon_area_3d(roof_coordinates)
            
            roof_surface = {
                'surface_id': 'roof_1',
                'surface_type': 'RoofSurface',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [roof_coordinates]
                },
                'properties': {
                    'area_m2': roof_area,
                    'height_m': height,
                    'roof_type': 'flat',  # LoD 1.2 typically has flat roofs
                    'slope_degrees': 0.0,
                    'lod': 1.2,
                    'surface_material': 'unknown',  # For TABULA typology assignment
                    'construction_type': 'unknown'   # For TABULA typology assignment
                },
                'semantic': {
                    'surface_class': 'RoofSurface',
                    'building_element': 'roof',
                    'thermal_properties': {
                        'u_value': None,  # To be filled by TABULA calculator
                        'thermal_resistance': None,
                        'thermal_capacity': None
                    }
                }
            }
            
            return roof_surface
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to generate roof surface: {str(e)}")
            return None
    
    def _generate_ground_surface(self, exterior_ring: List[List[float]]) -> Dict[str, Any]:
        """Generate ground surface (bottom surface at ground level)"""
        try:
            # Create ground coordinates at height 0
            ground_coordinates = []
            for point in exterior_ring:
                ground_coordinates.append([point[0], point[1], 0.0])
            
            # Reverse order for proper normal direction (pointing up)
            ground_coordinates.reverse()
            
            # Calculate ground area
            ground_area = self._calculate_polygon_area_3d(ground_coordinates)
            
            ground_surface = {
                'surface_id': 'ground_1',
                'surface_type': 'GroundSurface',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [ground_coordinates]
                },
                'properties': {
                    'area_m2': ground_area,
                    'height_m': 0.0,
                    'lod': 1.2,
                    'surface_material': 'unknown',  # For foundation/ground interface
                    'construction_type': 'slab_on_ground'
                },
                'semantic': {
                    'surface_class': 'GroundSurface',
                    'building_element': 'ground_slab',
                    'thermal_properties': {
                        'u_value': None,  # To be filled by TABULA calculator
                        'thermal_resistance': None,
                        'thermal_capacity': None
                    }
                }
            }
            
            return ground_surface
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to generate ground surface: {str(e)}")
            return None
    
    def _get_cardinal_direction(self, azimuth: float) -> str:
        """Convert azimuth angle to cardinal direction"""
        if azimuth >= 337.5 or azimuth < 22.5:
            return 'North'
        elif 22.5 <= azimuth < 67.5:
            return 'Northeast'
        elif 67.5 <= azimuth < 112.5:
            return 'East'
        elif 112.5 <= azimuth < 157.5:
            return 'Southeast'
        elif 157.5 <= azimuth < 202.5:
            return 'South'
        elif 202.5 <= azimuth < 247.5:
            return 'Southwest'
        elif 247.5 <= azimuth < 292.5:
            return 'West'
        elif 292.5 <= azimuth < 337.5:
            return 'Northwest'
        else:
            return 'Unknown'
    
    def _calculate_polygon_area(self, geometry: Dict[str, Any]) -> float:
        """Calculate area of polygon geometry using shoelace formula"""
        if geometry.get('type') != 'Polygon':
            return 0.0
        
        coordinates = geometry.get('coordinates', [])
        if not coordinates:
            return 0.0
        
        coords = coordinates[0]  # Exterior ring
        area = 0.0
        n = len(coords)
        
        for i in range(n - 1):
            area += coords[i][0] * coords[i + 1][1]
            area -= coords[i + 1][0] * coords[i][1]
        
        return abs(area) / 2.0
    
    def _calculate_polygon_area_3d(self, coordinates: List[List[float]]) -> float:
        """Calculate area of 3D polygon using projection to 2D"""
        if len(coordinates) < 3:
            return 0.0
        
        # Project to XY plane and calculate area
        area = 0.0
        n = len(coordinates)
        
        for i in range(n - 1):
            area += coordinates[i][0] * coordinates[i + 1][1]
            area -= coordinates[i + 1][0] * coordinates[i][1]
        
        return abs(area) / 2.0
    
    def _save_surfaces_to_database(self, building_id: str, surfaces: Dict[str, Any]) -> bool:
        """Save LoD 1.2 surfaces to database"""
        try:
            from cim_wizard.models import Building
            from django.db import transaction
            
            with transaction.atomic():
                try:
                    # Get the building record
                    building = Building.objects.get(building_id=building_id, lod=0)  # Start with LoD 0
                    
                    # Update with LoD 1.2 surfaces
                    building.building_surfaces_lod12 = surfaces
                    building.save()
                    
                    self.pipeline.log_info(
                        self.calculator_name, 
                        f"Successfully saved LoD 1.2 surfaces to database for building {building_id}"
                    )
                    return True
                    
                except Building.DoesNotExist:
                    self.pipeline.log_error(
                        self.calculator_name, 
                        f"Building not found in database: {building_id}"
                    )
                    return False
                    
        except Exception as e:
            self.pipeline.log_error(
                self.calculator_name, 
                f"Failed to save LoD 1.2 surfaces to database: {str(e)}"
            )
            return False 