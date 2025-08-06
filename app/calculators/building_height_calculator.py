"""
Building Height Calculator - Independent class with pipeline executor injection
"""
from typing import Optional
import random
import json
import os
import requests


class BuildingHeightCalculator:
    """Calculate building height using various methods"""
    
    def __init__(self, pipeline_executor):
        self.pipeline = pipeline_executor
        self.data_manager = pipeline_executor.data_manager
        self.calculator_name = self.__class__.__name__
        
        # Load configuration
        config_path = os.path.join(os.path.dirname(__file__), '..', 'configuration.json')
        with open(config_path, 'r') as f:
            self.config = json.load(f)
    
    def calculate_from_raster_service(self) -> Optional[float]:
        """Calculate building height from raster service (batch processing for multiple buildings)"""
        
        # CRITICAL DEBUG: Check if method is being called
        print("=== RASTER SERVICE METHOD CALLED ===")
        self.pipeline.log_info(self.calculator_name, "=== RASTER SERVICE METHOD CALLED ===")
        
        # Get raster service URL
        raster_service_url = getattr(self.data_manager, 'raster_service_url', None)
        print(f"DEBUG: raster_service_url = {raster_service_url}")
        self.pipeline.log_info(self.calculator_name, f"DEBUG: raster_service_url = {raster_service_url}")
        
        if not raster_service_url:
            error_msg = "No raster_service_url provided"
            print(f"ERROR: {error_msg}")
            self.pipeline.log_error(self.calculator_name, error_msg)
            return None
        
        building_geo = self.pipeline.get_feature_safely('building_geo', calculator_name=self.calculator_name)
        scenario_geo = self.pipeline.get_feature_safely('scenario_geo', calculator_name=self.calculator_name)
        
        # CRITICAL DEBUG: Check building_geo data
        print(f"DEBUG: building_geo from get_feature_safely = {building_geo}")
        self.pipeline.log_info(self.calculator_name, f"DEBUG: building_geo from get_feature_safely = {building_geo}")
        
        # Try getting building_geo directly from data_manager
        building_geo_direct = getattr(self.data_manager, 'building_geo', None)
        print(f"DEBUG: building_geo from data_manager direct = {building_geo_direct}")
        self.pipeline.log_info(self.calculator_name, f"DEBUG: building_geo from data_manager direct = {building_geo_direct}")
        
        # Use direct access if get_feature_safely failed
        if not building_geo and building_geo_direct:
            building_geo = building_geo_direct
            print(f"DEBUG: Using building_geo from direct data_manager access")
            self.pipeline.log_info(self.calculator_name, f"DEBUG: Using building_geo from direct data_manager access")
        
        if building_geo:
            buildings = building_geo.get('buildings', [])
            print(f"DEBUG: Found {len(buildings)} buildings in building_geo")
            self.pipeline.log_info(self.calculator_name, f"DEBUG: Found {len(buildings)} buildings in building_geo")
            
            if buildings:
                first_building = buildings[0]
                print(f"DEBUG: First building keys: {list(first_building.keys())}")
                self.pipeline.log_info(self.calculator_name, f"DEBUG: First building keys: {list(first_building.keys())}")
        else:
            print("ERROR: building_geo is None or empty!")
            self.pipeline.log_error(self.calculator_name, "building_geo is None or empty!")
        
        if not self.pipeline.validate_input(building_geo, "building_geo", self.calculator_name):
            print("ERROR: building_geo validation failed!")
            self.pipeline.log_error(self.calculator_name, "building_geo validation failed!")
            return None
            
        self.pipeline.log_info(self.calculator_name, f"Calculating building heights from raster service using batch processing")
        
        try:
            import geopandas as gpd
            from shapely.geometry import shape, mapping
            import requests
            import json
            
            # Extract all buildings and create GeoDataFrame
            buildings = building_geo.get('buildings', [])
            if not buildings:
                self.pipeline.log_error(self.calculator_name, "No buildings found in building_geo")
                return None

            project_id = building_geo.get('project_id')
            scenario_id = building_geo.get('scenario_id')
            
            if not project_id or not scenario_id:
                self.pipeline.log_error(self.calculator_name, "Missing project_id or scenario_id")
                return None

            # Create GeoDataFrame for batch processing
            buildings_data = []
            for building in buildings:
                buildings_data.append({
                    'building_id': building['building_id'],
                    'project_id': project_id,
                    'scenario_id': scenario_id,
                    'lod': building.get('lod', 0),
                    'geometry': shape(building['geometry'])
                })
            
            gdf = gpd.GeoDataFrame(buildings_data, crs='EPSG:4326')
            self.pipeline.log_info(self.calculator_name, f"Created GeoDataFrame with {len(gdf)} buildings for chunked processing")
            
            # Process buildings in chunks of 30 to avoid timeout issues
            chunk_size = 100
            total_buildings = len(gdf)
            num_chunks = (total_buildings + chunk_size - 1) // chunk_size  # Ceiling division
            
            self.pipeline.log_info(self.calculator_name, f"Processing {total_buildings} buildings in {num_chunks} chunks of {chunk_size}")
            
            # Create mapping of building_id to height for all chunks
            building_heights = {}
            
            for chunk_idx in range(num_chunks):
                start_idx = chunk_idx * chunk_size
                end_idx = min((chunk_idx + 1) * chunk_size, total_buildings)
                chunk_gdf = gdf.iloc[start_idx:end_idx]
                self.pipeline.log_info(self.calculator_name, f"Processing chunk {chunk_idx + 1}/{num_chunks} ({len(chunk_gdf)} buildings)")
                # Convert chunk to FeatureCollection
                payload = {
                    "type": "FeatureCollection",
                    "features": []
                }
                for _, row in chunk_gdf.iterrows():
                    payload["features"].append({
                        "type": "Feature",
                        "geometry": mapping(row.geometry),
                        "properties": {
                            "building_id": row.building_id,
                            "project_id": row.project_id,
                            "scenario_id": row.scenario_id,
                            "lod": row.lod
                        }
                    })
                # Debug: Log sample coordinates being sent for first chunk only
                if chunk_idx == 0 and payload["features"]:
                    sample_coords = payload["features"][0]["geometry"]["coordinates"]
                    self.pipeline.log_info(self.calculator_name, f"Sample coordinates being sent: {sample_coords}")
                # Make chunk HTTP request to raster service
                try:
                    response = requests.post(
                        raster_service_url,
                        json=payload,
                        headers={'Content-Type': 'application/json'},
                        timeout=300  # 5 minutes per chunk (much more reasonable)
                    )
                    self.pipeline.log_info(self.calculator_name, f"Chunk {chunk_idx + 1} HTTP response status: {response.status_code}")
                    # Debug: Log sample response data for first chunk only
                    if chunk_idx == 0 and response.status_code == 200:
                        response_text = response.text[:500] if len(response.text) > 500 else response.text
                        self.pipeline.log_info(self.calculator_name, f"Sample response data: {response_text}")
                    elif response.status_code != 200:
                        self.pipeline.log_error(self.calculator_name, f"Chunk {chunk_idx + 1} response content: {response.text}")
                    if response.status_code != 200:
                        self.pipeline.log_error(self.calculator_name, f"Chunk {chunk_idx + 1} failed with status {response.status_code}")
                        continue  # Skip this chunk but continue with others
                    # Parse chunk response
                    response_data = response.json()
                    results = response_data.get('results', [])
                    if not results:
                        self.pipeline.log_warning(self.calculator_name, f"No results returned for chunk {chunk_idx + 1}")
                        continue
                    self.pipeline.log_info(self.calculator_name, f"Chunk {chunk_idx + 1}: Received {len(results)} height results")
                    # Add chunk results to overall building_heights
                    for result in results:
                        building_id = result.get('building_id')
                        height = result.get('height')
                        if building_id and height is not None:
                            building_heights[building_id] = round(float(height), 2)
                except requests.exceptions.RequestException as e:
                    self.pipeline.log_error(self.calculator_name, f"Chunk {chunk_idx + 1} HTTP request failed: {str(e)}")
                    continue  # Skip this chunk but continue with others
                except json.JSONDecodeError as e:
                    self.pipeline.log_error(self.calculator_name, f"Chunk {chunk_idx + 1} JSON parse failed: {str(e)}")
                    continue  # Skip this chunk but continue with others
                except Exception as e:
                    self.pipeline.log_error(self.calculator_name, f"Chunk {chunk_idx + 1} processing failed: {str(e)}")
                    continue  # Skip this chunk but continue with others
            # Check if we got any results
            if not building_heights:
                self.pipeline.log_error(self.calculator_name, "No height results received from any chunks")
                return None
            self.pipeline.log_info(self.calculator_name, f"Successfully processed {len(building_heights)} buildings across {num_chunks} chunks")
            # Bulk database update
            try:
                from cim_wizard.models import BuildingProperties
                from django.db import transaction
                with transaction.atomic():
                    updated_count = 0
                    for building_id, height in building_heights.items():
                        # Find the corresponding building to get its lod
                        building_lod = 0
                        for building in buildings:
                            if building['building_id'] == building_id:
                                building_lod = building.get('lod', 0)
                                break
                        try:
                            building_props = BuildingProperties.objects.get(
                                building_id=building_id,
                                project_id=project_id,
                                scenario_id=scenario_id,
                                lod=building_lod
                            )
                            building_props.height = height
                            building_props.save()
                            updated_count += 1
                        except BuildingProperties.DoesNotExist:
                            self.pipeline.log_warning(self.calculator_name, f"BuildingProperties not found for building {building_id}")
                            continue
                    self.pipeline.log_info(self.calculator_name, f"Bulk updated heights for {updated_count} buildings")
            except Exception as e:
                self.pipeline.log_error(self.calculator_name, f"Failed to bulk update database: {str(e)}")
                return None
            # Return height for first building (for compatibility with single-building pipeline)
            first_building_id = buildings[0]['building_id']
            first_height = building_heights.get(first_building_id)
            if first_height is not None:
                self.pipeline.log_info(self.calculator_name, f"Successfully calculated heights for {len(building_heights)} buildings via batch processing")
                return first_height
            else:
                self.pipeline.log_error(self.calculator_name, f"No height found for first building {first_building_id}")
                return None
            
        except ImportError:
            self.pipeline.log_error(self.calculator_name, "GeoPandas not available for batch processing")
            return None
        except requests.exceptions.RequestException as e:
            self.pipeline.log_error(self.calculator_name, f"Batch HTTP request failed: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to parse batch JSON response: {str(e)}")
            return None
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to get heights from raster service: {str(e)}")
            return None
    
    def calculate_from_osm_height(self) -> Optional[float]:
        """Calculate building height from OSM data (improved to check individual building tags)"""
        building_geo = self.pipeline.get_feature_safely('building_geo', calculator_name=self.calculator_name)
        
        if not self.pipeline.validate_input(building_geo, "building_geo", self.calculator_name):
            return None
        
        self.pipeline.log_info(self.calculator_name, "Calculating building height from OSM data")
        
        try:
            # Get buildings from building_geo
            buildings = building_geo.get('buildings', [])
            if not buildings:
                self.pipeline.log_error(self.calculator_name, "No buildings in building_geo data")
                return None
            
            # Check first building for OSM height data
            building = buildings[0]
            building_properties = building.get('properties', {})
            osm_tags = building_properties.get('osm_tags', {})
            
            # Check for height in OSM tags
            height_value = osm_tags.get('height') or osm_tags.get('building:height') or osm_tags.get('est_height')
            
            if height_value:
                try:
                    # Parse height (could be "12.5", "12.5 m", "12,5", etc.)
                    import re
                    # Extract numeric value from string
                    height_match = re.search(r'(\d+[.,]?\d*)', str(height_value))
                    if height_match:
                        height_str = height_match.group(1).replace(',', '.')
                        height = float(height_str)
                        
                        self.pipeline.log_info(self.calculator_name, f"Found OSM height: {height}m for building {building['building_id']}")
                        
                        # Save to database
                        try:
                            from cim_wizard.models import BuildingProperties
                            project_id = building_geo.get('project_id')
                            scenario_id = building_geo.get('scenario_id')
                            building_id = building['building_id']
                            lod = building.get('lod', 0)
                            
                            building_props = BuildingProperties.objects.get(
                                building_id=building_id,
                                project_id=project_id,
                                scenario_id=scenario_id,
                                lod=lod
                            )
                            building_props.height = height
                            building_props.save()
                            
                            self.pipeline.log_info(self.calculator_name, f"Updated height for building {building_id}")
                            
                        except Exception as e:
                            self.pipeline.log_warning(self.calculator_name, f"Failed to save OSM height to database: {str(e)}")
                        
                    return height
                except ValueError:
                    self.pipeline.log_warning(self.calculator_name, f"Could not parse height value: {height_value}")
            
            # If no height found in OSM tags, return None to try next method
            self.pipeline.log_info(self.calculator_name, f"No height data found in OSM tags for building {building['building_id']}")
            return None
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to extract height from OSM: {str(e)}")
            return None
    
    def calculate_default_estimate(self) -> Optional[float]:
        """Calculate default building height estimate (fallback method)"""
        building_geo = self.pipeline.get_feature_safely('building_geo', calculator_name=self.calculator_name)
        
        if not self.pipeline.validate_input(building_geo, "building_geo", self.calculator_name):
            return None
        
        self.pipeline.log_info(self.calculator_name, "Calculating default building height estimate")
        
        try:
            # Default estimation based on building area or simple assumption
            default_height = 12.0  # Default 4-story building (3m per floor)
            
            self.pipeline.log_info(self.calculator_name, f"Using default height estimate: {default_height}m")
            return default_height
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to calculate default height: {str(e)}")
            return None

    def save_to_database(self) -> bool:
        """Save building height to database"""
        try:
            # Import Django models
            try:
                from cim_wizard.models import BuildingProperties
            except ImportError:
                self.pipeline.log_warning(self.calculator_name, "Django models not available - skipping database save")
                return False

            # Get building_geo and height data
            building_geo = self.pipeline.get_feature_safely('building_geo', calculator_name=self.calculator_name)
            height = self.pipeline.get_feature_safely('building_height', calculator_name=self.calculator_name)
            
            if not building_geo or height is None:
                self.pipeline.log_error(self.calculator_name, "Missing required data for database save")
                return False
            
            # Get required IDs
            project_id = building_geo.get('project_id')
            scenario_id = building_geo.get('scenario_id')
            
            if not project_id or not scenario_id:
                self.pipeline.log_error(self.calculator_name, "Missing project_id or scenario_id")
                return False
            
            # Get building_id from first building
            buildings = building_geo.get('buildings', [])
            if not buildings:
                self.pipeline.log_error(self.calculator_name, "No buildings in building_geo")
                return False
                
            building_id = buildings[0].get('building_id')
            lod = buildings[0].get('lod', 0)
            
            if not building_id:
                self.pipeline.log_error(self.calculator_name, "Missing building_id")
                return False
            
            # Update BuildingProperties with specific building_id
            try:
                building_props = BuildingProperties.objects.get(
                    building_id=building_id,
                    project_id=project_id,
                    scenario_id=scenario_id,
                    lod=lod
                )
                building_props.height = height
                building_props.save()
                self.pipeline.log_info(self.calculator_name, f"Updated building height to {height}m for building {building_id}")
                return True
            except BuildingProperties.DoesNotExist:
                self.pipeline.log_error(self.calculator_name, f"BuildingProperties record not found for building {building_id}")
                return False
            except Exception as e:
                self.pipeline.log_error(self.calculator_name, f"Failed to update BuildingProperties: {str(e)}")
                return False
                
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Error in save_to_database: {str(e)}")
            return False 