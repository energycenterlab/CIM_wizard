"""
Building Geo Calculator - Independent class with pipeline executor injection

OSM Data Fetching:
- Primary method: osmnx library (faster, more reliable, built-in geometry processing)
- Fallback method: Overpass API (direct HTTP calls)
- To install osmnx: pip install osmnx
"""
from typing import Optional, Dict, Any, List
import uuid
import requests
import json
try:
    import osmnx as ox
    OSMNX_AVAILABLE = True
except ImportError:
    OSMNX_AVAILABLE = False


class BuildingGeoCalculator:
    """Calculate building geometry data"""
    
    def __init__(self, pipeline_executor):
        self.pipeline = pipeline_executor
        self.data_manager = pipeline_executor.data_manager
        self.calculator_name = self.__class__.__name__
    
    def calculate_from_scenario_census_geo(self) -> Optional[Dict[str, Any]]:
        """Get building footprints from integrated database (simplified for testing)"""
        # Validate required inputs
        project_id = getattr(self.data_manager, 'project_id', None)
        scenario_id = getattr(self.data_manager, 'scenario_id', None)
        scenario_census_boundary = self.pipeline.get_feature_safely('scenario_census_boundary', calculator_name=self.calculator_name)
        
        if not self.pipeline.validate_input(project_id, "project_id", self.calculator_name):
            return None
        if not self.pipeline.validate_input(scenario_id, "scenario_id", self.calculator_name):
            return None
        if not self.pipeline.validate_dict(scenario_census_boundary, "scenario_census_boundary", self.calculator_name):
            return None
        
        self.pipeline.log_info(self.calculator_name, f"Querying OSM for building footprints in scenario: {scenario_id}")
        
        try:
            # Extract boundary geometry for building generation
            boundary_geom = None
            if 'geometry' in scenario_census_boundary:
                boundary_geom = scenario_census_boundary['geometry']
            elif 'type' in scenario_census_boundary and 'coordinates' in scenario_census_boundary:
                boundary_geom = scenario_census_boundary
            else:
                self.pipeline.log_error(self.calculator_name, "Could not extract boundary geometry from scenario_census_boundary")
                return None
            
            # Validate the boundary geometry
            if not self.pipeline.validate_geometry(boundary_geom, "census_boundary_geometry", self.calculator_name):
                return None
            
            # Query OSM for real buildings
            osm_buildings = self._query_osm_buildings(boundary_geom, scenario_id)
            
            if not osm_buildings:
                self.pipeline.log_error(self.calculator_name, "No buildings found in OSM query!")
                # Return empty result instead of fake buildings
                return {
                    'project_id': project_id,
                    'scenario_id': scenario_id,
                    'buildings': [],
                    'total_buildings': 0,
                    'data_source': 'osm_query_failed',
                    'lod': 0,
                    'query_boundary': boundary_geom,
                    'created_from': 'osm_query_failed'
                }
            else:
                # Convert OSM buildings to GeoJSON format
                buildings = []
                for osm_building in osm_buildings:
                    building = {
                        'type': 'Feature',
                        'properties': {
                            'building_id': osm_building.get('building_id'),
                            'building': 'yes',
                            'building:type': osm_building.get('properties', {}).get('building_type', 'residential'),
                            'osm_id': osm_building.get('properties', {}).get('osm_id'),
                            'source': 'osm'
                        },
                        'geometry': osm_building.get('geometry')
                    }
                    buildings.append(building)
                data_source = 'osm_overpass_api'
            
            # Build result with metadata
            building_geo = {
                'project_id': project_id,
                'scenario_id': scenario_id,
                'buildings': buildings,
                'total_buildings': len(buildings),
                'data_source': data_source,
                'lod': 0,
                'query_boundary': boundary_geom,
                'created_from': data_source
            }
            
            self.pipeline.log_calculation_success(self.calculator_name, "osm_buildings_query", building_geo,
                                         f"Retrieved {len(buildings)} buildings from {data_source}")
            return building_geo
            
        except Exception as e:
            self.pipeline.log_calculation_failure(self.calculator_name, "osm_buildings_query", str(e))
            return None
    
    def calculate_from_building_geo(self) -> Optional[Dict[str, Any]]:
        """Process building GeoJSON from UI POST request"""
        # Get building GeoJSON data from UI POST request
        building_geojson = self.pipeline.get_feature_safely('building_geo', calculator_name=self.calculator_name)
        
        if not self.pipeline.validate_input(building_geojson, "building_geo", self.calculator_name):
            return None
        
        self.pipeline.log_info(self.calculator_name, "Processing building GeoJSON from UI POST request")
        
        try:
            buildings = []
            
            # Handle different GeoJSON formats
            if isinstance(building_geojson, dict):
                if building_geojson.get('type') == 'FeatureCollection':
                    # GeoJSON FeatureCollection
                    features = building_geojson.get('features', [])
                    for feature in features:
                        building = self._process_geojson_feature(feature)
                        if building:
                            buildings.append(building)
                            
                elif building_geojson.get('type') == 'Feature':
                    # Single GeoJSON Feature
                    building = self._process_geojson_feature(building_geojson)
                    if building:
                        buildings.append(building)
                        
                elif 'buildings' in building_geojson:
                    # Already processed building collection
                    existing_buildings = building_geojson['buildings']
                    for building_data in existing_buildings:
                        building = self._process_building_data(building_data)
                        if building:
                            buildings.append(building)
                            
                else:
                    # Try to process as single building data
                    building = self._process_building_data(building_geojson)
                    if building:
                        buildings.append(building)
                        
            elif isinstance(building_geojson, list):
                # List of building features or data
                for item in building_geojson:
                    if item.get('type') == 'Feature':
                        building = self._process_geojson_feature(item)
                    else:
                        building = self._process_building_data(item)
                    
                    if building:
                        buildings.append(building)
            
            if not buildings:
                self.pipeline.log_error(self.calculator_name, "No valid buildings could be processed from input data")
                return None
            
            # Get project and scenario IDs (may be provided or generated)
            project_id = getattr(self.data_manager, 'project_id', None) 
            scenario_id = getattr(self.data_manager, 'scenario_id', None)
            
            # Build result
            building_geo = {
                'project_id': project_id,
                'scenario_id': scenario_id,
                'buildings': buildings,
                'total_buildings': len(buildings),
                'data_source': 'ui_geojson_input',
                'lod': 0,
                'created_from': 'ui_building_geojson'
            }
            
            # Set building_id and lod on data_manager for downstream calculators
            if buildings and len(buildings) > 0:
                first_building = buildings[0]
                self.data_manager.building_id = first_building['building_id']
                self.data_manager.lod = first_building.get('lod', 0)
            
            self.pipeline.log_calculation_success(self.calculator_name, "ui_building_processing", building_geo,
                                        f"Processed {len(buildings)} buildings from UI input")
            return building_geo
            
        except Exception as e:
            self.pipeline.log_calculation_failure(self.calculator_name, "ui_building_processing", str(e))
            return None
    
    # === HELPER METHODS ===
    
    def _query_osm_buildings(self, boundary_geom: Dict[str, Any], scenario_id: str) -> List[Dict[str, Any]]:
        """Query OSM Overpass API for building footprints within boundary"""
        buildings = []
        
        try:
            # Extract coordinates from the boundary geometry
            if isinstance(boundary_geom, dict):
                if boundary_geom.get('type') == 'Feature':
                    geom = boundary_geom.get('geometry', {})
                else:
                    geom = boundary_geom
                
                # Handle different geometry types
                if geom.get('type') == 'MultiPolygon':
                    # For MultiPolygon, use the first polygon's coordinates
                    coords = geom.get('coordinates', [[[]]])[0][0]
                elif geom.get('type') == 'Polygon':
                    coords = geom.get('coordinates', [[]])[0]
                else:
                    self.pipeline.log_error(self.calculator_name, f"Unsupported geometry type: {geom.get('type')}")
                    return buildings
            else:
                self.pipeline.log_error(self.calculator_name, "Invalid boundary geometry format")
                return buildings
            
            if not coords:
                self.pipeline.log_error(self.calculator_name, "No valid coordinates found in boundary geometry")
                return buildings
            
            # Calculate boundary bounds for Overpass query
            lons = [coord[0] for coord in coords]
            lats = [coord[1] for coord in coords]
            min_lon, max_lon = min(lons), max(lons)
            min_lat, max_lat = min(lats), max(lats)
            
            # Construct Overpass QL query with better building filtering
            overpass_query = f"""
            [out:json][timeout:25];
            (
              way["building"]({min_lat},{min_lon},{max_lat},{max_lon});
              way["building:part"]({min_lat},{min_lon},{max_lat},{max_lon});
              relation["building"]({min_lat},{min_lon},{max_lat},{max_lon});
            );
            out body;
            >;
            out skel qt;
            """
            
            # Query Overpass API
            overpass_url = "https://overpass-api.de/api/interpreter"
            self.pipeline.log_info(self.calculator_name, f"Querying OSM Overpass API for buildings in bounds: {min_lat},{min_lon},{max_lat},{max_lon}")
            
            response = requests.post(overpass_url, data=overpass_query, timeout=30)
            
            if response.status_code != 200:
                self.pipeline.log_error(self.calculator_name, f"Overpass API request failed: {response.status_code}")
                return buildings
            
            osm_data = response.json()
            self.pipeline.log_info(self.calculator_name, f"Received {len(osm_data.get('elements', []))} elements from OSM")
            
            # Process OSM elements
            nodes = {node['id']: node for node in osm_data.get('elements', []) if node['type'] == 'node'}
            
            for element in osm_data.get('elements', []):
                if element['type'] == 'way':
                    tags = element.get('tags', {})
                    # Only include if 'building' tag is present (not 'building:part')
                    if 'building' not in tags:
                        continue  # Exclude if not a building
                    building_value = tags.get('building', '')
                    excluded_values = ['no', 'entrance', 'roof', 'bridge', 'tunnel']
                    if building_value not in excluded_values:
                        # Get building coordinates
                        building_coords = []
                        for node_id in element.get('nodes', []):
                            if node_id in nodes:
                                node = nodes[node_id]
                                building_coords.append([node['lon'], node['lat']])
                        if len(building_coords) >= 3:  # Need at least 3 points for a polygon
                            # Close the polygon if not already closed
                            if building_coords[0] != building_coords[-1]:
                                building_coords.append(building_coords[0])
                            # Classify building usage based on OSM tags
                            osm_usage = self._classify_building_usage_from_osm(tags)
                            osm_id = f"way/{element['id']}"
                            
                            # Generate consistent building_id based on OSM ID
                            building_id = f"osm_way_{element['id']}"
                            
                            building = {
                                'building_id': building_id,
                                'scenario_id': scenario_id,
                                'geometry': {
                                    'type': 'Polygon',
                                    'coordinates': [building_coords]
                                },
                                'properties': {
                                    'building_type': building_value if building_value != 'yes' else 'residential',
                                    'source': 'osm',
                                    'osm_id': osm_id,
                                    'osm_tags': tags,
                                    'osm_usage': osm_usage
                                },
                                'lod': 0
                            }
                            buildings.append(building)
            
            self.pipeline.log_info(self.calculator_name, f"Processed {len(buildings)} building footprints from OSM")
            
            # Filter buildings to only include those within the actual boundary polygon
            from shapely.geometry import shape
            try:
                boundary_shape = shape(boundary_geom)
                filtered_buildings = []
                
                for building in buildings:
                    # Check if building centroid is within the actual boundary
                    building_shape = shape(building['geometry'])
                    if boundary_shape.contains(building_shape.centroid):
                        filtered_buildings.append(building)
                
                self.pipeline.log_info(self.calculator_name, f"Filtered to {len(filtered_buildings)} buildings within actual boundary (from {len(buildings)} in bounding box)")
                
                # Height calculation removed - handled by dedicated building_height_calculator
                # This calculator should only focus on geometry extraction
                
                return filtered_buildings
                
            except Exception as e:
                self.pipeline.log_warning(self.calculator_name, f"Failed to filter buildings by boundary: {str(e)}, returning all buildings")
                # Return buildings without height calculation (handled by dedicated calculator)
                return buildings
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Error querying OSM buildings: {str(e)}")
            return buildings
    
    def _query_osm_buildings_with_osmnx(self, boundary_geom: Dict[str, Any], scenario_id: str) -> List[Dict[str, Any]]:
        """Query OSM buildings using osmnx library with strict criteria"""
        buildings = []
        
        if not OSMNX_AVAILABLE:
            self.pipeline.log_warning(self.calculator_name, "osmnx not available, falling back to Overpass API")
            return self._query_osm_buildings(boundary_geom, scenario_id)
        
        try:
            from shapely.geometry import shape, mapping
            import geopandas as gpd
            
            # Convert boundary geometry to shapely
            if isinstance(boundary_geom, dict):
                if boundary_geom.get('type') == 'Feature':
                    geom = boundary_geom.get('geometry', {})
                else:
                    geom = boundary_geom
                boundary_shape = shape(geom)
            else:
                self.pipeline.log_error(self.calculator_name, "Invalid boundary geometry format")
                return buildings
            
            self.pipeline.log_info(self.calculator_name, "Querying OSM buildings using osmnx")
            
            # Configure osmnx
            ox.config(log_console=False, use_cache=True)
            
            # Query buildings using osmnx
            try:
                # Get buildings within the boundary
                gdf_buildings = ox.geometries_from_polygon(
                    boundary_shape, 
                    tags={'building': True}
                )
                
                self.pipeline.log_info(self.calculator_name, f"osmnx returned {len(gdf_buildings)} buildings")
                
                # Filter and process buildings
                processed_count = 0
                for idx, building_row in gdf_buildings.iterrows():
                    try:
                        # Get OSM tags
                        osm_tags = {}
                        for col in gdf_buildings.columns:
                            if col not in ['geometry'] and building_row[col] is not None:
                                osm_tags[col] = str(building_row[col])
                        
                        # Apply strict filter: must have 'building' tag (not just building:part)
                        if 'building' not in osm_tags:
                            continue
                        
                        building_value = osm_tags.get('building', '')
                        excluded_values = ['no', 'entrance', 'roof', 'bridge', 'tunnel']
                        if building_value in excluded_values:
                            continue
                        
                        # Get geometry
                        geom = building_row.geometry
                        if geom.geom_type not in ['Polygon', 'MultiPolygon']:
                            continue
                        
                        # Convert to simple polygon if MultiPolygon
                        if geom.geom_type == 'MultiPolygon':
                            # Take the largest polygon
                            geom = max(geom.geoms, key=lambda p: p.area)
                        
                        # Calculate area (rough estimate in square meters)
                        # For more accurate area calculation, we'd need to project to appropriate CRS
                        area_sqm = geom.area * 111000 * 111000
                        
                        # Classify building usage based on OSM tags (don't filter out)
                        osm_usage = self._classify_building_usage_from_osm(osm_tags)
                        
                        # Get OSM ID from the index
                        osm_id = f"{idx[0]}/{idx[1]}" if isinstance(idx, tuple) else str(idx)
                        
                        # Check if building is within the actual boundary (not just bounding box)
                        if not boundary_shape.contains(geom.centroid):
                            continue
                        
                        # Convert geometry to GeoJSON format
                        geom_json = mapping(geom)
                        
                        # Generate a consistent building_id based on OSM ID
                        # This ensures the same building always gets the same ID
                        building_id = f"osm_{osm_id.replace('/', '_')}"
                        
                        building = {
                            'building_id': building_id,
                            'scenario_id': scenario_id,
                            'geometry': geom_json,
                            'properties': {
                                'building_type': building_value if building_value != 'yes' else 'residential',
                                'source': 'osmnx',
                                'osm_id': osm_id,
                                'osm_tags': osm_tags,
                                'estimated_area': area_sqm,
                                'osm_usage': osm_usage
                            },
                            'lod': 0
                        }
                        buildings.append(building)
                        processed_count += 1
                        
                    except Exception as e:
                        self.pipeline.log_warning(self.calculator_name, f"Failed to process building {idx}: {str(e)}")
                        continue
                
                self.pipeline.log_info(self.calculator_name, f"osmnx processed {processed_count} buildings successfully")
                
                # Return buildings without height calculation (handled by dedicated calculator)
                return buildings
                
            except Exception as e:
                self.pipeline.log_error(self.calculator_name, f"osmnx query failed: {str(e)}")
                # Fallback to Overpass API
                self.pipeline.log_info(self.calculator_name, "Falling back to Overpass API")
                return self._query_osm_buildings(boundary_geom, scenario_id)
                
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Error in osmnx building query: {str(e)}")
            # Fallback to Overpass API
            return self._query_osm_buildings(boundary_geom, scenario_id)
    
    def _estimate_height_from_tags(self, osm_tags: Dict[str, Any], area: float) -> float:
        """Estimate building height from OSM tags and area - same logic as in building_demographic_calculator"""
        # Check for height tag
        if 'height' in osm_tags:
            try:
                height_str = str(osm_tags['height']).replace('m', '').replace(' ', '')
                return float(height_str)
            except:
                pass
        
        # Check for levels tag
        if 'levels' in osm_tags:
            try:
                levels = int(osm_tags['levels'])
                return levels * 3.0  # 3m per floor
            except:
                pass
        
        # Estimate based on building type and area
        building_type = osm_tags.get('building', 'yes')
        
        if building_type in ['house', 'detached', 'residential']:
            return 6.0 if area < 200 else 9.0
        elif building_type in ['apartments', 'residential']:
            return 15.0 if area < 500 else 25.0
        elif building_type in ['commercial', 'retail']:
            return 4.0
        elif building_type in ['industrial', 'warehouse']:
            return 8.0
        else:
            # Default height based on area
            if area < 100:
                return 6.0
            elif area < 300:
                return 9.0
            elif area < 800:
                return 15.0
            else:
                return 20.0
    
    def _classify_building_usage_from_osm(self, osm_tags: Dict[str, Any]) -> str:
        """Classify building usage based on OSM tags - designed for Turin's mixed-use patterns"""
        
        # PURELY NON-RESIDENTIAL buildings (exclude these from residential consideration)
        non_residential_indicators = {
            # Institutional/Public buildings
            'amenity': ['school', 'university', 'college', 'hospital', 'clinic', 'church', 
                       'place_of_worship', 'fire_station', 'police', 'post_office', 'townhall',
                       'library', 'community_centre', 'social_facility'],
            
            # Large commercial/industrial
            'building': ['industrial', 'warehouse', 'factory', 'commercial', 'retail', 
                        'supermarket', 'school', 'hospital', 'church', 'mosque', 'synagogue',
                        'university', 'college', 'public', 'civic'],
            
            # Infrastructure
            'man_made': ['water_tower', 'pumping_station', 'reservoir_covered'],
            'power': ['substation', 'generator'],
            'railway': ['station'],
            'aeroway': ['terminal'],
            
            # Tourism (hotels/hostels are typically not residential)
            'tourism': ['hotel', 'motel', 'hostel'],
            
            # Healthcare facilities
            'healthcare': ['hospital', 'clinic', 'nursing_home'],
            
            # Large sports/leisure facilities
            'leisure': ['sports_centre', 'stadium', 'swimming_pool']
        }
        
        # Check for purely non-residential indicators
        for tag_key, excluded_values in non_residential_indicators.items():
            if tag_key in osm_tags:
                tag_value = str(osm_tags[tag_key]).lower()
                if tag_value in excluded_values:
                    return 'not_residential_based_on_osm'
        
        # MIXED-USE INDICATORS (keep as potentially residential)
        # These are common in Turin and should NOT be filtered out
        mixed_use_indicators = {
            'shop': True,  # Ground floor shops with apartments above
            'office': True,  # Offices with potential residential above
            'craft': True,  # Small workshops with residential
            'amenity': ['restaurant', 'cafe', 'bar', 'fast_food', 'pharmacy', 'bank', 'atm']
        }
        
        # Check for mixed-use indicators
        has_mixed_use = False
        for tag_key, values in mixed_use_indicators.items():
            if tag_key in osm_tags:
                if values is True or str(osm_tags[tag_key]).lower() in values:
                    has_mixed_use = True
                    break
        
        # RESIDENTIAL INDICATORS
        residential_indicators = {
            'building': ['residential', 'apartments', 'house', 'detached', 'semidetached', 
                        'terrace', 'bungalow', 'static_caravan', 'yes'],
            'building:use': ['residential'],
            'residential': True,
        }
        
        # Check for explicit residential indicators
        for tag_key, values in residential_indicators.items():
            if tag_key in osm_tags:
                tag_value = str(osm_tags[tag_key]).lower()
                if values is True or tag_value in values:
                    if has_mixed_use:
                        return 'probably_residential_complex'  # Mixed-use but likely residential
                    else:
                        return 'probably_residential_complex'  # Pure residential
        
        # If no specific indicators found but has mixed-use, assume residential potential
        if has_mixed_use:
            return 'probably_residential_complex'
        
        # Default: likely residential if it's just a generic building
        building_type = osm_tags.get('building', '').lower()
        if building_type in ['yes', '', 'building']:
            return 'probably_residential_complex'
        
        # Unknown/ambiguous cases - keep as potentially residential
        return 'probably_residential_complex'
    
    def _calculate_heights_with_raster_service_DEPRECATED(self, buildings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """DEPRECATED - Height calculation moved to dedicated building_height_calculator"""
        # This method is no longer used but kept for reference
        return buildings
    
    def _calculate_heights_with_raster_service_OLD(self, buildings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """OLD METHOD - Calculate building heights using raster service instead of OSM tag estimation"""
        try:
            # Get raster service URL from configuration
            raster_service_url = self.data_manager.configuration.get('raster_service_url')
            if not raster_service_url:
                # Try alternative configuration paths
                services_config = self.data_manager.configuration.get('services', {})
                raster_gateway = services_config.get('raster_gateway', {})
                raster_service_url = raster_gateway.get('url')
            
            if not raster_service_url:
                self.pipeline.log_warning(self.calculator_name, "No raster service URL found, falling back to OSM tag estimation")
                return self._fallback_to_osm_height_estimation(buildings)
            
            self.pipeline.log_info(self.calculator_name, f"Using raster service to calculate heights for {len(buildings)} buildings")
            
            # Process buildings in chunks to avoid timeout
            chunk_size = 100
            total_buildings = len(buildings)
            num_chunks = (total_buildings + chunk_size - 1) // chunk_size
            
            updated_buildings = []
            heights_calculated = 0
            
            for chunk_idx in range(num_chunks):
                start_idx = chunk_idx * chunk_size
                end_idx = min((chunk_idx + 1) * chunk_size, total_buildings)
                chunk_buildings = buildings[start_idx:end_idx]
                
                self.pipeline.log_info(self.calculator_name, f"Processing raster chunk {chunk_idx + 1}/{num_chunks} ({len(chunk_buildings)} buildings)")
                
                # Create FeatureCollection for this chunk
                payload = {
                    "type": "FeatureCollection",
                    "features": []
                }
                
                # Map building_id to building data for this chunk
                chunk_building_map = {}
                
                for building in chunk_buildings:
                    building_id = building['building_id']
                    chunk_building_map[building_id] = building
                    
                    payload["features"].append({
                        "type": "Feature",
                        "geometry": building['geometry'],
                        "properties": {
                            "building_id": building_id
                        }
                    })
                
                # Call raster service for this chunk
                try:
                    response = requests.post(
                        raster_service_url,
                        json=payload,
                        headers={'Content-Type': 'application/json'},
                        timeout=300  # 5 minutes per chunk
                    )
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        results = response_data.get('results', [])
                        
                        self.pipeline.log_info(self.calculator_name, f"Raster chunk {chunk_idx + 1} received {len(results)} height results")
                        
                        # Update buildings with raster service heights
                        for result in results:
                            building_id = result.get('building_id')
                            height = result.get('height')
                            
                            if building_id and height is not None:
                                building = chunk_building_map.get(building_id)
                                if building:
                                    # Update building properties with raster height
                                    building['properties']['estimated_height'] = round(float(height), 2)
                                    building['properties']['height_source'] = 'raster_service'
                                    heights_calculated += 1
                        
                        # Add all chunk buildings to updated list (with or without raster heights)
                        for building in chunk_buildings:
                            updated_buildings.append(building)
                            
                    else:
                        self.pipeline.log_error(self.calculator_name, f"Raster chunk {chunk_idx + 1} failed with status {response.status_code}")
                        # Add chunk buildings with fallback heights
                        for building in chunk_buildings:
                            updated_buildings.append(self._add_fallback_height(building))
                        
                except Exception as e:
                    self.pipeline.log_error(self.calculator_name, f"Raster chunk {chunk_idx + 1} failed: {str(e)}")
                    # Add chunk buildings with fallback heights
                    for building in chunk_buildings:
                        updated_buildings.append(self._add_fallback_height(building))
            
            self.pipeline.log_info(self.calculator_name, f"Raster service calculated heights for {heights_calculated}/{total_buildings} buildings")
            
            # Add fallback heights for buildings that didn't get raster heights
            for building in updated_buildings:
                if 'estimated_height' not in building['properties']:
                    building = self._add_fallback_height(building)
            
            return updated_buildings
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Raster service height calculation failed: {str(e)}")
            return self._fallback_to_osm_height_estimation(buildings)
    
    def _add_fallback_height(self, building: Dict[str, Any]) -> Dict[str, Any]:
        """Add fallback height estimation to a building"""
        try:
            osm_tags = building['properties'].get('osm_tags', {})
            area = building['properties'].get('estimated_area', 100.0)
            fallback_height = self._estimate_height_from_tags(osm_tags, area)
            building['properties']['estimated_height'] = fallback_height
            building['properties']['height_source'] = 'osm_estimation'
            return building
        except Exception as e:
            self.pipeline.log_warning(self.calculator_name, f"Fallback height calculation failed: {str(e)}")
            building['properties']['estimated_height'] = 12.0
            building['properties']['height_source'] = 'default'
            return building
    
    def _fallback_to_osm_height_estimation(self, buildings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fallback to OSM tag height estimation for all buildings"""
        self.pipeline.log_info(self.calculator_name, f"Using OSM tag estimation for {len(buildings)} buildings")
        updated_buildings = []
        for building in buildings:
            updated_buildings.append(self._add_fallback_height(building))
        return updated_buildings
    
    def _process_geojson_feature(self, feature: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a GeoJSON Feature into building data"""
        try:
            if not self.pipeline.validate_dict(feature, "geojson_feature", self.calculator_name, ['type', 'geometry']):
                return None
            
            geometry = feature.get('geometry', {})
            properties = feature.get('properties', {})
            
            if not self.pipeline.validate_geometry(geometry, "building_geometry", self.calculator_name):
                return None
            
            # Generate UUID for building_id if not provided
            building_id = properties.get('building_id') or properties.get('id') or str(uuid.uuid4())
            
            building = {
                'building_id': building_id,
                'scenario_id': getattr(self.data_manager, 'scenario_id', None),
                'geometry': geometry,
                'properties': {
                    'building_type': properties.get('building_type', 'unknown'),
                    'source': 'ui_input',
                    **properties  # Include all original properties
                },
                'lod': 0
            }
            
            return building
            
        except Exception as e:
            self.pipeline.log_warning(self.calculator_name, f"Failed to process GeoJSON feature: {str(e)}")
            return None
    
    def _process_building_data(self, building_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process building data that's already in our format"""
        try:
            if not self.pipeline.validate_dict(building_data, "building_data", self.calculator_name):
                return None
            
            # Generate UUID for building_id if not provided
            building_id = building_data.get('building_id') or str(uuid.uuid4())
            
            # Ensure we have geometry
            if 'geometry' not in building_data:
                self.pipeline.log_warning(self.calculator_name, "Building data missing geometry field")
                return None
            
            building = {
                'building_id': building_id,
                'scenario_id': getattr(self.data_manager, 'scenario_id', None),
                'geometry': building_data['geometry'],
                'properties': building_data.get('properties', {}),
                'lod': 0
            }
            
            # Copy any additional fields
            for key, value in building_data.items():
                if key not in ['building_id', 'scenario_id', 'geometry', 'properties', 'lod']:
                    building[key] = value
            
            return building
            
        except Exception as e:
            self.pipeline.log_warning(self.calculator_name, f"Failed to process building data: {str(e)}")
            return None
    
    def save_to_database(self):
        """Save building geometry data to database"""
        try:
            # Import Django models
            try:
                from cim_wizard.models import Building
                from django.contrib.gis.geos import GEOSGeometry
                import json
            except ImportError:
                self.pipeline.log_warning(self.calculator_name, "Django models not available - skipping database save")
                return False

            # Get building_geo data from data manager
            building_data = self.pipeline.get_feature_safely('building_geo', calculator_name=self.calculator_name)
            if not building_data:
                self.pipeline.log_error(self.calculator_name, "No building_geo data to save")
                return False
            
            buildings = building_data.get('buildings', [])
            if not buildings:
                self.pipeline.log_error(self.calculator_name, "No buildings found in building_geo data")
                return False
            
            self.pipeline.log_info(self.calculator_name, f"Saving {len(buildings)} buildings from building_geo")
            
            saved_count = 0
            for building in buildings:
                try:
                    # Create or update Building record only (BuildingProperties handled by BuildingPropsCalculator)
                    building_obj, created = Building.objects.get_or_create(
                        building_id=building['building_id'],
                        lod=building.get('lod', 0),
                        defaults={
                            'building_geometry': GEOSGeometry(json.dumps(building['geometry'])),
                            'building_geometry_source': building.get('properties', {}).get('source', 'ui_input')
                        }
                    )
                    
                    if not created:
                        # Update existing building
                        building_obj.building_geometry = GEOSGeometry(json.dumps(building['geometry']))
                        building_obj.building_geometry_source = building.get('properties', {}).get('source', 'ui_input')
                        building_obj.save()
                    
                    self.pipeline.log_info(self.calculator_name, f"{'Created' if created else 'Updated'} building with ID: {building['building_id']}")
                    saved_count += 1
                    
                except Exception as e:
                    self.pipeline.log_error(self.calculator_name, f"Failed to save building {building.get('building_id')}: {str(e)}")
                    continue
            
            self.pipeline.log_info(self.calculator_name, f"Successfully saved {saved_count}/{len(buildings)} buildings to database")
            return saved_count > 0
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to save to database: {str(e)}")
            return False