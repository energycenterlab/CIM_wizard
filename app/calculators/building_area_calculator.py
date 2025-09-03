"""
Building Area Calculator
"""
from typing import Optional, Dict, Any


class BuildingAreaCalculator:
    """Calculate building area from geometry"""
    
    def __init__(self, pipeline_executor):
        self.pipeline = pipeline_executor
        self.data_manager = pipeline_executor.data_manager
        self.calculator_name = self.__class__.__name__
    
    def calculate_from_geometry(self) -> Optional[Dict[str, Any]]:
        """Calculate area directly from building geometry for ALL buildings"""
        try:
            # Get building_geo from pipeline
            building_geo = self.pipeline.get_feature_safely('building_geo')
            if not building_geo:
                self.pipeline.log_error(self.calculator_name, "No building_geo data available")
                return None
        
            # Extract building data
            buildings = building_geo.get('buildings', [])
            if not buildings:
                self.pipeline.log_error(self.calculator_name, "No buildings in building_geo data")
                return None

            project_id = building_geo.get('project_id')
            scenario_id = building_geo.get('scenario_id')

            if not project_id or not scenario_id:
                self.pipeline.log_error(self.calculator_name, "Missing required project_id or scenario_id")
                return None
            
            # Calculate area for ALL buildings
            building_properties_list = []
            updated_count = 0
            
            # Calculate areas for all buildings (simplified for FastAPI)
            building_areas = []
            last_five_logs = []  # Track last 5 for summary
            
            for idx, building in enumerate(buildings):
                building_id = building.get('building_id')
                lod = building.get('lod', 0)

                if not building_id:
                    self.pipeline.log_error(self.calculator_name, f"Building at index {idx} has no building_id - this should have been set by building_geo_calculator")
                    continue  # Skip buildings without IDs instead of generating new ones
                
                # Calculate area from geometry using proper geographic projection
                geometry = building.get('geometry', {})
                area = self._calculate_polygon_area(geometry)
                
                # Add to result list
                building_properties_list.append({
                    'building_id': building_id,
                    'scenario_id': scenario_id,
                    'lod': lod,
                    'area': area
                })
                
                building_areas.append(area)
                updated_count += 1
                
                # Track last 5 for logging
                log_msg = f"Building {building_id}: area = {area:.2f}m²"
                last_five_logs.append(log_msg)
                if len(last_five_logs) > 5:
                    last_five_logs.pop(0)
            
            # Log last 5 samples
            if last_five_logs:
                self.pipeline.log_info(self.calculator_name, "Last 5 building areas:")
                for log_msg in last_five_logs:
                    self.pipeline.log_info(self.calculator_name, f"  {log_msg}")
            
            self.pipeline.log_info(self.calculator_name, f"Calculated areas for {updated_count} buildings")

            # Create result
            result = {
                'project_id': project_id,
                'scenario_id': scenario_id,
                'building_properties': building_properties_list,
                'building_areas': building_areas  # Add areas list for compatibility
            }

            # Store result in data manager
            self.data_manager.set_feature('building_area', result)
            # Also store the areas list directly for easier access
            self.data_manager.set_feature('building_areas', building_areas)
            
            # Save to database immediately
            db_session = getattr(self.data_manager, 'db_session', None)
            if db_session and project_id and scenario_id:
                self._save_areas_to_database(db_session, building_properties_list, project_id, scenario_id)

            self.pipeline.log_calculation_success(self.calculator_name, 'calculate_from_geometry', f"Calculated areas for {len(building_properties_list)} buildings")
            return result
            
        except Exception as e:
            self.pipeline.log_calculation_failure(self.calculator_name, 'calculate_from_geometry', str(e))
            return None
    
    def _save_areas_to_database(self, db_session, building_props_list, project_id, scenario_id):
        """Save calculated areas to database"""
        try:
            from app.models.vector import BuildingProperties
            from sqlalchemy import and_
            
            updated_count = 0
            created_count = 0
            
            for prop_data in building_props_list:
                building_id = prop_data['building_id']
                area = prop_data['area']
                lod = prop_data.get('lod', 0)
                
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
                        if props.area != area:  # Only update if different
                            props.area = area
                            db_session.add(props)  # Mark as dirty
                            updated_count += 1
                    else:
                        # Create new properties record
                        new_props = BuildingProperties(
                            building_id=building_id,
                            project_id=project_id,
                            scenario_id=scenario_id,
                            lod=lod,
                            area=area
                        )
                        db_session.add(new_props)
                        created_count += 1
                
                except Exception as e:
                    self.pipeline.log_warning(self.calculator_name, 
                        f"Failed to save area for building {building_id}: {str(e)}")
                    db_session.rollback()
                    raise
            
            if updated_count > 0 or created_count > 0:
                db_session.commit()
                db_session.flush()  # Force write
                self.pipeline.log_info(self.calculator_name, 
                    f"Database commit complete: {updated_count} updated, {created_count} created")
            else:
                self.pipeline.log_warning(self.calculator_name, "No area changes to save")
            
        except Exception as e:
            db_session.rollback()
            self.pipeline.log_error(self.calculator_name, f"Failed to save areas to database: {str(e)}")
            raise
    
    def save_to_database(self):
        """Save building area data to database - required by pipeline"""
        return True  # Database save is already handled in calculate_from_geometry
    
    def _calculate_polygon_area(self, geometry: Dict[str, Any]) -> float:
        """Calculate area of polygon geometry in square meters using proper geographic projection"""
        if geometry.get('type') not in ['Polygon', 'MultiPolygon']:
            return 0.0
        
        try:
            from shapely.geometry import shape
            import pyproj
            from shapely.ops import transform
            
            # Create shapely geometry from GeoJSON
            geom = shape(geometry)
            
            # Project to UTM zone 32N for Turin area (accurate area calculation)
            project = pyproj.Transformer.from_crs(
                pyproj.CRS('EPSG:4326'),  # WGS84
                pyproj.CRS('EPSG:32632'),  # UTM 32N for Northern Italy
                always_xy=True
            ).transform
            
            # Transform geometry to UTM for accurate area calculation
            geom_utm = transform(project, geom)
            
            # Calculate area in square meters
            area = geom_utm.area
            
            # Only log once, not for every building
            # self.pipeline.log_debug(self.calculator_name, f"Used UTM projection for accurate area calculation")
            return area
            
        except ImportError:
            # Fallback to approximate calculation if shapely/pyproj not available
            self.pipeline.log_warning(self.calculator_name, "Shapely/pyproj not available, using approximate area calculation")
            return self._calculate_polygon_area_approximate(geometry)
        except Exception as e:
            self.pipeline.log_warning(self.calculator_name, f"Error in precise area calculation: {str(e)}, using fallback")
            return self._calculate_polygon_area_approximate(geometry)
    
    def _calculate_polygon_area_approximate(self, geometry: Dict[str, Any]) -> float:
        """Approximate polygon area calculation for WGS84 coordinates"""
        if geometry.get('type') not in ['Polygon', 'MultiPolygon']:
            return 0.0
        
        coordinates = geometry.get('coordinates', [])
        if not coordinates:
            return 0.0
        
        # Conversion factors for Turin area (45°N latitude)
        # 1 degree longitude ≈ 78,700m, 1 degree latitude ≈ 111,000m at 45°N
        lon_to_m = 78700
        lat_to_m = 111000
        
        # For MultiPolygon, sum areas of all polygons
        if geometry.get('type') == 'MultiPolygon':
            total_area = 0.0
            for polygon_coords in coordinates:
                area = 0.0
                coords = polygon_coords[0]  # Outer ring
                n = len(coords)
                for i in range(n - 1):
                    x1, y1 = coords[i][0] * lon_to_m, coords[i][1] * lat_to_m
                    x2, y2 = coords[i + 1][0] * lon_to_m, coords[i + 1][1] * lat_to_m
                    area += x1 * y2 - x2 * y1
                total_area += abs(area) / 2.0
            return total_area
        
        # For single Polygon
        coords = coordinates[0]  # Outer ring
        area = 0.0
        n = len(coords)
        
        for i in range(n - 1):
            x1, y1 = coords[i][0] * lon_to_m, coords[i][1] * lat_to_m
            x2, y2 = coords[i + 1][0] * lon_to_m, coords[i + 1][1] * lat_to_m
            area += x1 * y2 - x2 * y1
        
        return abs(area) / 2.0 