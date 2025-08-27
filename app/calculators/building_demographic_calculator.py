"""
Building Demographic Calculator - Orchestrates census-OSM integration
"""
from typing import Optional, Dict, Any
import geopandas as gpd
from shapely.geometry import shape, mapping
import requests
import json
import pandas as pd


class BuildingDemographicCalculator:
    """Orchestrate building demographics by integrating census data with OSM buildings"""
    
    def __init__(self, pipeline_executor):
        self.pipeline = pipeline_executor
        self.data_manager = pipeline_executor.data_manager
        self.calculator_name = self.__class__.__name__
    
    def by_census_osm(self) -> Optional[Dict[str, Any]]:
        """
        Calculate building demographics (simplified for pipeline)
        """
        try:
            # Get required data
            building_geo = self.pipeline.get_feature_safely('building_geo', calculator_name=self.calculator_name)
            building_population_data = self.pipeline.get_feature_safely('building_population', calculator_name=self.calculator_name)
            building_families_data = self.pipeline.get_feature_safely('building_n_families', calculator_name=self.calculator_name)
            
            if not building_geo:
                self.pipeline.log_error(self.calculator_name, "No building_geo data available")
                return None
            
            self.pipeline.log_info(self.calculator_name, "Calculating building demographics")
            
            # Get buildings
            buildings = building_geo.get('buildings', [])
            if not buildings:
                self.pipeline.log_error(self.calculator_name, "No buildings found in building_geo")
                return None
            
            # Create demographic data for each building
            building_demographics = []
            for i, building in enumerate(buildings):
                building_id = building.get('building_id')
                
                # Get population and families for this building
                population = 0
                families = 0
                
                if building_population_data:
                    populations = building_population_data.get('building_populations', [])
                    if i < len(populations):
                        population = populations[i]
                
                if building_families_data:
                    families_list = building_families_data.get('building_families', [])
                    if i < len(families_list):
                        families = families_list[i]
                
                # Create demographic record
                demographic = {
                    'building_id': building_id,
                    'population': population,
                    'families': families,
                    'avg_family_size': 2.5 if families > 0 else 0,
                    'demographic_type': 'residential'
                }
                
                building_demographics.append(demographic)
            
            # Create result
            result = {
                'project_id': building_geo.get('project_id'),
                'scenario_id': building_geo.get('scenario_id'),
                'building_demographics': building_demographics,
                'total_population': sum(d['population'] for d in building_demographics),
                'total_families': sum(d['families'] for d in building_demographics),
                'calculation_method': 'simplified_pipeline'
            }
            
            # Store in data manager
            self.data_manager.set_feature('building_demographic', result)
            
            self.pipeline.log_info(self.calculator_name, f"Calculated demographics for {len(building_demographics)} buildings")
            return result
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to calculate demographics: {str(e)}")
            return None
    
    def _get_project_boundary(self) -> Optional[Dict[str, Any]]:
        """Get project boundary from scenario_geo or data_manager"""
        scenario_geo = self.pipeline.get_feature_safely('scenario_geo', calculator_name=self.calculator_name)
        if scenario_geo and 'project_boundary' in scenario_geo:
            self.pipeline.log_info(self.calculator_name, "Retrieved project_boundary from scenario_geo result")
            return scenario_geo['project_boundary']
        elif hasattr(self.data_manager, 'project_boundary'):
            self.pipeline.log_info(self.calculator_name, "Retrieved project_boundary from data_manager")
            return getattr(self.data_manager, 'project_boundary')
        else:
            self.pipeline.log_error(self.calculator_name, "project_boundary not found in scenario_geo result or data_manager")
            return None
    
    def _get_scenario_census_boundary(self, project_boundary: Dict[str, Any], project_id: str, scenario_id: str) -> Optional[Dict[str, Any]]:
        """Get or create scenario_census_boundary"""
        scenario_census_boundary = self.pipeline.get_feature_safely('scenario_census_boundary', calculator_name=self.calculator_name)
        if not scenario_census_boundary:
            # Call census service to get boundary data
            self.pipeline.log_info(self.calculator_name, "scenario_census_boundary not found, calling census service")
            scenario_census_boundary = self._call_census_service(project_boundary, project_id, scenario_id)
            if not scenario_census_boundary:
                self.pipeline.log_error(self.calculator_name, "Failed to get census boundary data from service")
                return None
        else:
            self.pipeline.log_info(self.calculator_name, "Using existing scenario_census_boundary from pipeline context")
        
        return scenario_census_boundary
    
    def _process_demographics_with_calculators(self, census_gdf: gpd.GeoDataFrame, 
                                             census_building_gdf: gpd.GeoDataFrame,
                                             project_boundary: Dict[str, Any],
                                             project_id: str, scenario_id: str) -> Dict[str, Any]:
        """Process demographics using the new modular calculators"""
        try:
            # Import new calculators
            from .building_type_calculator import BuildingTypeCalculator
            from .building_construction_year_calculator import BuildingConstructionYearCalculator
            from .building_population_calculator import BuildingPopulationCalculator
            from .building_n_families_calculator import BuildingNFamiliesCalculator
            
            # Initialize calculators
            type_calc = BuildingTypeCalculator(self.pipeline)
            year_calc = BuildingConstructionYearCalculator(self.pipeline)
            pop_calc = BuildingPopulationCalculator(self.pipeline)
            family_calc = BuildingNFamiliesCalculator(self.pipeline)
            
            # Step 1: Assign building types
            census_building_gdf = type_calc.by_census_osm(census_gdf, census_building_gdf)
            
            # Step 2: Distribute construction years
            census_building_gdf, year_accuracy = year_calc.by_census_osm(census_gdf, census_building_gdf)
            
            # Step 3: Calculate residential volumes for census zones
            census_gdf = self._calculate_residential_volumes(census_gdf, census_building_gdf)
            
            # Step 4: Distribute population
            census_building_gdf, pop_accuracy = pop_calc.by_census_osm(census_gdf, census_building_gdf)
            
            # Step 5: Calculate families
            census_building_gdf, family_accuracy = family_calc.by_census_osm(census_building_gdf)
            
            # Step 6: Filter buildings to project_boundary
            final_buildings = self._filter_to_project_boundary(census_building_gdf, project_boundary)
            if final_buildings is None or final_buildings.empty:
                self.pipeline.log_error(self.calculator_name, "No buildings found within project boundary")
                return None
            
            # Step 7: Update database
            self._update_database(final_buildings, project_id, scenario_id)
            
            # Step 8: Create result
            result = self._create_result(final_buildings, census_gdf, year_accuracy, pop_accuracy, family_accuracy, project_id, scenario_id, type_calc)
            
            self.pipeline.log_info(self.calculator_name, f"Successfully processed {len(final_buildings)} buildings with demographics")
            return result
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to process demographics with calculators: {str(e)}")
            return None
    
    def _call_census_service(self, project_boundary: Dict[str, Any], project_id: str, scenario_id: str) -> Optional[Dict[str, Any]]:
        """Call census service to get scenario_census_boundary"""
        try:
            # Import and use the scenario census boundary calculator
            from .scenario_census_boundary_calculator import ScenarioCensusBoundaryCalculator
            census_calc = ScenarioCensusBoundaryCalculator(self.pipeline)
            
            # Create temporary data for census calculation
            census_inputs = {
                'project_id': project_id,
                'scenario_id': scenario_id,
                'project_boundary': project_boundary
            }
            
            # Store inputs in data manager temporarily
            original_data = {}
            for key, value in census_inputs.items():
                if hasattr(self.data_manager, key):
                    original_data[key] = getattr(self.data_manager, key)
                setattr(self.data_manager, key, value)
            
            try:
                # Call census boundary calculation
                result = census_calc.calculate_from_census_api()
                if result:
                    self.pipeline.log_info(self.calculator_name, "Successfully obtained census boundary data")
                    return result
                else:
                    self.pipeline.log_error(self.calculator_name, "Census service returned empty result")
                    return None
                    
            finally:
                # Restore original data manager state
                for key, value in original_data.items():
                    setattr(self.data_manager, key, value)
                for key in census_inputs:
                    if key not in original_data and hasattr(self.data_manager, key):
                        delattr(self.data_manager, key)
                        
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to call census service: {str(e)}")
            return None

    def _create_census_gdf(self, scenario_census_boundary: Dict[str, Any]) -> Optional[gpd.GeoDataFrame]:
        """Create census GeoDataFrame from scenario_census_boundary"""
        try:
            census_zones = scenario_census_boundary.get('properties', {}).get('census_zones', [])
            if not census_zones:
                self.pipeline.log_error(self.calculator_name, "No census zones found in scenario_census_boundary")
                return None
            
            # Create GeoDataFrame from census zones
            census_data = []
            for zone in census_zones:
                zone_props = zone.get('properties', {})
                # Get E3 and E4 values, defaulting to 0 if not present
                e3 = zone_props.get('E3', 0) or 0  # Handle None values
                e4 = zone_props.get('E4', 0) or 0  # Handle None values
                
                # Get zone geometry, fallback to boundary geometry if not available
                zone_geom = zone.get('geometry')
                if not zone_geom:
                    zone_geom = scenario_census_boundary['geometry']
                
                census_data.append({
                    'zone_id': zone.get('zone_id'),
                    'zone_geometry': shape(zone_geom),  # Use zone-specific geometry
                    'total_n_buildings': 0,  # Will be calculated later
                    'E3': e3,  # Residential buildings
                    'E4': e4,  # Production buildings
                    'total_n_res_buildings': e3 + e4,
                    'E8': zone_props.get('E8', 0) or 0,
                    'E9': zone_props.get('E9', 0) or 0,
                    'E10': zone_props.get('E10', 0) or 0,
                    'E11': zone_props.get('E11', 0) or 0,
                    'E12': zone_props.get('E12', 0) or 0,
                    'E13': zone_props.get('E13', 0) or 0,
                    'E14': zone_props.get('E14', 0) or 0,
                    'E15': zone_props.get('E15', 0) or 0,
                    'E16': zone_props.get('E16', 0) or 0,
                    'total_v_buildings': 0,  # Will be calculated later
                    'total_v_res_buildings': 0,  # Will be calculated later
                    'P1': zone_props.get('P1', 0) or 0,  # Total population
                    'PF1': zone_props.get('PF1', 0) or 0  # Total families
                })
            
            census_gdf = gpd.GeoDataFrame(census_data, geometry='zone_geometry', crs='EPSG:4326')
            self.pipeline.log_info(self.calculator_name, f"Created census GeoDataFrame with {len(census_gdf)} zones")
            return census_gdf
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to create census GeoDataFrame: {str(e)}")
            return None
    
    def _query_osm_buildings_in_census_boundary(self, scenario_census_boundary: Dict[str, Any], scenario_id: str) -> Optional[gpd.GeoDataFrame]:
        """Query OSM for all buildings within scenario_census_boundary"""
        try:
            # Get boundary geometry for OSM query
            boundary_geom = scenario_census_boundary.get('geometry', {})
            if not boundary_geom:
                self.pipeline.log_error(self.calculator_name, "No geometry found in scenario_census_boundary")
                return None
            
            # Use existing OSM query method from building_geo_calculator
            from .building_geo_calculator import BuildingGeoCalculator
            building_geo_calc = BuildingGeoCalculator(self.pipeline)
            
            # Query OSM buildings - prioritize osmnx over Overpass API
            self.pipeline.log_info(self.calculator_name, "Attempting to query OSM buildings using osmnx first")
            osm_buildings = building_geo_calc._query_osm_buildings_with_osmnx(boundary_geom, scenario_id)
            if not osm_buildings:
                self.pipeline.log_warning(self.calculator_name, "osmnx query returned no buildings, trying Overpass API fallback")
                osm_buildings = building_geo_calc._query_osm_buildings(boundary_geom, scenario_id)
            
            if not osm_buildings:
                self.pipeline.log_error(self.calculator_name, "No buildings returned from any OSM query method")
                return None
            
            # Convert to GeoDataFrame
            buildings_data = []
            for building in osm_buildings:
                buildings_data.append({
                    'building_id': building['building_id'],
                    'scenario_id': scenario_id,
                    'geometry': shape(building['geometry']),
                    'osm_tags': building.get('properties', {}).get('osm_tags', {}),
                    'osm_usage': building.get('properties', {}).get('osm_usage', 'probably_residential_complex'),
                    'source': 'osm',
                    'lod': 0,
                    # Demographics fields to be calculated
                    'building_type': None,
                    'cont_year': None,
                    'height': None,
                    'area': None,
                    'volume': None,
                    'number_of_floors': None,
                    'n_people': 0.0,
                    'n_family': 0.0,
                    'census_zone_id': None
                })
            
            census_building_gdf = gpd.GeoDataFrame(buildings_data, geometry='geometry', crs='EPSG:4326')
            self.pipeline.log_info(self.calculator_name, f"Created building GeoDataFrame with {len(census_building_gdf)} buildings from OSM")
            return census_building_gdf
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to query OSM buildings: {str(e)}")
            return None
    
    def _calculate_building_properties(self, census_building_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Calculate area, height, and volume for all buildings"""
        try:
            # Import existing calculators
            from .building_area_calculator import BuildingAreaCalculator
            
            area_calc = BuildingAreaCalculator(self.pipeline)
            
            # Calculate area for each building
            for idx, building in census_building_gdf.iterrows():
                try:
                    # Calculate area using existing method
                    geom_dict = mapping(building.geometry)
                    area = area_calc._calculate_polygon_area(geom_dict)
                    census_building_gdf.at[idx, 'area'] = area
                    
                except Exception as e:
                    self.pipeline.log_warning(self.calculator_name, f"Failed to calculate area for building {building.building_id}: {str(e)}")
                    # Set default area
                    census_building_gdf.at[idx, 'area'] = 100.0
            
            # MANDATORY: Use raster service for height calculation - DIRECT IMPLEMENTATION
            self.pipeline.log_info(self.calculator_name, "=== STARTING DIRECT RASTER SERVICE IMPLEMENTATION ===")
            
            # Get raster service URL from configuration
            raster_service_url = self.data_manager.configuration.get('raster_service_url')
            if not raster_service_url:
                # Try alternative configuration paths
                services_config = self.data_manager.configuration.get('services', {})
                raster_gateway = services_config.get('raster_gateway', {})
                raster_service_url = raster_gateway.get('url')
            
            self.pipeline.log_info(self.calculator_name, f"DEBUG: raster_service_url from config = {raster_service_url}")
            
            if not raster_service_url:
                error_msg = "CRITICAL ERROR: No raster_service_url found in configuration! Cannot proceed without raster service."
                self.pipeline.log_error(self.calculator_name, error_msg)
                raise ValueError(error_msg)
            
            # Direct raster service implementation
            try:
                self.pipeline.log_info(self.calculator_name, f"DEBUG: Calling raster service directly for {len(census_building_gdf)} buildings")
                
                # Process buildings in chunks to avoid timeout
                chunk_size = 100
                total_buildings = len(census_building_gdf)
                num_chunks = (total_buildings + chunk_size - 1) // chunk_size
                
                self.pipeline.log_info(self.calculator_name, f"DEBUG: Processing {total_buildings} buildings in {num_chunks} chunks of {chunk_size}")
                
                # Store heights directly in GeoDataFrame
                heights_calculated = 0
                
                for chunk_idx in range(num_chunks):
                    start_idx = chunk_idx * chunk_size
                    end_idx = min((chunk_idx + 1) * chunk_size, total_buildings)
                    chunk_buildings = census_building_gdf.iloc[start_idx:end_idx]
                    
                    self.pipeline.log_info(self.calculator_name, f"DEBUG: Processing chunk {chunk_idx + 1}/{num_chunks} ({len(chunk_buildings)} buildings)")
                    
                    # Create FeatureCollection for this chunk
                    payload = {
                        "type": "FeatureCollection",
                        "features": []
                    }
                    
                    # Map building index to building_id for this chunk
                    chunk_building_map = {}
                    
                    for idx, building in chunk_buildings.iterrows():
                        building_id = building['building_id']
                        chunk_building_map[building_id] = idx
                        
                        payload["features"].append({
                            "type": "Feature",
                            "geometry": mapping(building.geometry),
                            "properties": {
                                "building_id": building_id
                            }
                        })
                    
                    # Log sample for first chunk
                    if chunk_idx == 0 and payload["features"]:
                        sample_coords = payload["features"][0]["geometry"]["coordinates"]
                        self.pipeline.log_info(self.calculator_name, f"DEBUG: Sample coordinates being sent: {sample_coords}")
                    
                    # Call raster service for this chunk
                    try:
                        response = requests.post(
                            raster_service_url,
                            json=payload,
                            headers={'Content-Type': 'application/json'},
                            timeout=300  # 5 minutes per chunk
                        )
                        
                        self.pipeline.log_info(self.calculator_name, f"DEBUG: Chunk {chunk_idx + 1} HTTP response status: {response.status_code}")
                        
                        if response.status_code == 200:
                            response_data = response.json()
                            results = response_data.get('results', [])
                            
                            self.pipeline.log_info(self.calculator_name, f"DEBUG: Chunk {chunk_idx + 1} received {len(results)} height results")
                            
                            # Update GeoDataFrame directly with heights
                            for result in results:
                                building_id = result.get('building_id')
                                height = result.get('height')
                                
                                if building_id and height is not None:
                                    # Find the building index in our GeoDataFrame
                                    building_idx = chunk_building_map.get(building_id)
                                    if building_idx is not None:
                                        census_building_gdf.at[building_idx, 'height'] = round(float(height), 2)
                                        heights_calculated += 1
                                        
                                        # Log first few heights for debugging
                                        if heights_calculated <= 3:
                                            self.pipeline.log_info(self.calculator_name, f"DEBUG: Set height {height} for building {building_id}")
                            
                            # Log sample response for first chunk
                            if chunk_idx == 0:
                                response_text = response.text[:500] if len(response.text) > 500 else response.text
                                self.pipeline.log_info(self.calculator_name, f"DEBUG: Sample response data: {response_text}")
                        else:
                            self.pipeline.log_error(self.calculator_name, f"DEBUG: Chunk {chunk_idx + 1} failed with status {response.status_code}")
                            self.pipeline.log_error(self.calculator_name, f"DEBUG: Response content: {response.text}")
                            # Continue with other chunks
                            
                    except requests.exceptions.RequestException as e:
                        self.pipeline.log_error(self.calculator_name, f"DEBUG: Chunk {chunk_idx + 1} HTTP request failed: {str(e)}")
                        # Continue with other chunks
                    except json.JSONDecodeError as e:
                        self.pipeline.log_error(self.calculator_name, f"DEBUG: Chunk {chunk_idx + 1} JSON parse failed: {str(e)}")
                        # Continue with other chunks
                    except Exception as e:
                        self.pipeline.log_error(self.calculator_name, f"DEBUG: Chunk {chunk_idx + 1} processing failed: {str(e)}")
                        # Continue with other chunks
                
                self.pipeline.log_info(self.calculator_name, f"DEBUG: Successfully calculated heights for {heights_calculated} buildings")
                
                # Set default height for buildings that didn't get heights from raster service
                buildings_without_height = census_building_gdf['height'].isna().sum()
                if buildings_without_height > 0:
                    self.pipeline.log_warning(self.calculator_name, f"DEBUG: {buildings_without_height} buildings didn't get heights from raster service, using fallback")
                    
                    for idx, building in census_building_gdf.iterrows():
                        if pd.isna(building['height']):
                            # Use fallback estimation
                            area = building['area']
                            osm_tags = building['osm_tags']
                            fallback_height = self._estimate_building_height(osm_tags, area)
                            census_building_gdf.at[idx, 'height'] = fallback_height
                
                if heights_calculated == 0:
                    error_msg = "CRITICAL ERROR: No heights were calculated by raster service!"
                    self.pipeline.log_error(self.calculator_name, error_msg)
                    raise ValueError(error_msg)
                
                self.pipeline.log_info(self.calculator_name, "=== DIRECT RASTER SERVICE IMPLEMENTATION COMPLETED SUCCESSFULLY ===")
                
            except Exception as e:
                error_msg = f"CRITICAL ERROR: Direct raster service implementation failed: {str(e)}"
                self.pipeline.log_error(self.calculator_name, error_msg)
                raise ValueError(error_msg)
            
            # Calculate volume and floors for each building
            for idx, building in census_building_gdf.iterrows():
                try:
                    area = census_building_gdf.at[idx, 'area']
                    height = census_building_gdf.at[idx, 'height']
                    
                    # Calculate volume
                    volume = area * height
                    census_building_gdf.at[idx, 'volume'] = volume
                    
                    # Calculate floors
                    floors = max(1, int(height / 3.0))  # 3m per floor
                    census_building_gdf.at[idx, 'number_of_floors'] = floors
                    
                except Exception as e:
                    self.pipeline.log_warning(self.calculator_name, f"Failed to calculate volume/floors for building {building.building_id}: {str(e)}")
                    # Set default values
                    census_building_gdf.at[idx, 'volume'] = 1200.0
                    census_building_gdf.at[idx, 'number_of_floors'] = 4
            
            self.pipeline.log_info(self.calculator_name, f"Calculated properties for {len(census_building_gdf)} buildings")
            return census_building_gdf
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to calculate building properties: {str(e)}")
            return census_building_gdf
    
    def _update_heights_from_database(self, census_building_gdf: gpd.GeoDataFrame):
        """Update heights in GeoDataFrame from database after raster service calculation"""
        try:
            from cim_wizard.models import BuildingProperties
            
            project_id = getattr(self.data_manager, 'project_id', 'temp')
            scenario_id = getattr(self.data_manager, 'scenario_id', 'temp')
            
            self.pipeline.log_info(self.calculator_name, f"DEBUG: _update_heights_from_database called")
            self.pipeline.log_info(self.calculator_name, f"DEBUG: project_id = {project_id}")
            self.pipeline.log_info(self.calculator_name, f"DEBUG: scenario_id = {scenario_id}")
            self.pipeline.log_info(self.calculator_name, f"DEBUG: Processing {len(census_building_gdf)} buildings")
            
            heights_found = 0
            heights_missing = 0
            
            for idx, building in census_building_gdf.iterrows():
                try:
                    building_id = building['building_id']
                    lod = building['lod']
                    
                    self.pipeline.log_info(self.calculator_name, f"DEBUG: Looking for building_id={building_id}, lod={lod}")
                    
                    building_props = BuildingProperties.objects.get(
                        building_id=building_id,
                        project_id=project_id,
                        scenario_id=scenario_id,
                        lod=lod
                    )
                    
                    if building_props.height is not None:
                        census_building_gdf.at[idx, 'height'] = building_props.height
                        heights_found += 1
                        self.pipeline.log_info(self.calculator_name, f"DEBUG: Found height {building_props.height} for building {building_id}")
                    else:
                        heights_missing += 1
                        self.pipeline.log_warning(self.calculator_name, f"DEBUG: Building {building_id} found in DB but height is None")
                        # Use fallback estimation
                        height = self._estimate_building_height(building['osm_tags'], building['area'])
                        census_building_gdf.at[idx, 'height'] = height
                        
                except BuildingProperties.DoesNotExist:
                    heights_missing += 1
                    self.pipeline.log_warning(self.calculator_name, f"DEBUG: Building {building_id} NOT found in database")
                    # Use fallback estimation
                    height = self._estimate_building_height(building['osm_tags'], building['area'])
                    census_building_gdf.at[idx, 'height'] = height
                except Exception as e:
                    heights_missing += 1
                    self.pipeline.log_error(self.calculator_name, f"DEBUG: Error retrieving building {building_id}: {str(e)}")
                    # Use fallback estimation
                    height = self._estimate_building_height(building['osm_tags'], building['area'])
                    census_building_gdf.at[idx, 'height'] = height
            
            self.pipeline.log_info(self.calculator_name, f"DEBUG: Heights summary - Found: {heights_found}, Missing: {heights_missing}")
                    
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"DEBUG: Failed to update heights from database: {str(e)}")
            # Fall back to estimation for all buildings
            self._calculate_heights_fallback(census_building_gdf, None)
    
    def _calculate_heights_fallback(self, census_building_gdf: gpd.GeoDataFrame, height_calc=None):
        """Fallback height calculation using OSM tags and estimation"""
        for idx, building in census_building_gdf.iterrows():
            try:
                # Try OSM height first, then estimation
                height = None
                
                # Check OSM tags for height
                osm_tags = building['osm_tags']
                if 'height' in osm_tags:
                    try:
                        height_str = osm_tags['height'].replace('m', '').replace(' ', '')
                        height = float(height_str)
                    except:
                        pass
                
                if height is None and 'levels' in osm_tags:
                    try:
                        levels = int(osm_tags['levels'])
                        height = levels * 3.0  # 3m per floor
                    except:
                        pass
                
                # If still no height, use estimation
                if height is None:
                    area = census_building_gdf.at[idx, 'area']
                    height = self._estimate_building_height(osm_tags, area)
                
                census_building_gdf.at[idx, 'height'] = height
                
            except Exception as e:
                self.pipeline.log_warning(self.calculator_name, f"Failed to calculate height for building {building.building_id}: {str(e)}")
                # Set default height
                census_building_gdf.at[idx, 'height'] = 12.0
    
    def _estimate_building_height(self, osm_tags: Dict[str, Any], area: float) -> float:
        """Estimate building height from OSM tags and area"""
        # Check for height tag
        if 'height' in osm_tags:
            try:
                height_str = osm_tags['height'].replace('m', '').replace(' ', '')
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
    
    def _update_census_building_counts(self, census_gdf: gpd.GeoDataFrame, census_building_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Update census zones with actual building counts and assign census_zone_id to buildings"""
        try:
            # Spatial join to assign census zone to each building
            buildings_with_zones = gpd.sjoin(census_building_gdf, census_gdf[['zone_id', 'zone_geometry']], 
                                           how='left', predicate='within')
            
            # Update building GeoDataFrame with census zone assignments
            for idx, building in buildings_with_zones.iterrows():
                zone_id = building.get('zone_id')
                if zone_id:
                    census_building_gdf.at[idx, 'census_zone_id'] = zone_id
            
            # Count buildings per census zone
            for idx, zone in census_gdf.iterrows():
                zone_id = zone.zone_id
                buildings_in_zone = census_building_gdf[census_building_gdf['census_zone_id'] == zone_id]
                count = len(buildings_in_zone)
                census_gdf.at[idx, 'total_n_buildings'] = count
                
                # Calculate total volume in zone
                total_volume = float(buildings_in_zone['volume'].sum()) if count > 0 else 0.0
                census_gdf.at[idx, 'total_v_buildings'] = total_volume
            
            self.pipeline.log_info(self.calculator_name, f"Updated census zones with building counts")
            return census_gdf
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to update census building counts: {str(e)}")
            return census_gdf
    
    def _calculate_residential_volumes(self, census_gdf: gpd.GeoDataFrame, census_building_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Calculate total residential volumes for each census zone"""
        try:
            for idx, zone in census_gdf.iterrows():
                zone_id = zone.zone_id
                residential_buildings = census_building_gdf[
                    (census_building_gdf['census_zone_id'] == zone_id) & 
                    (census_building_gdf['building_type'] == 'residential')
                ]
                
                total_residential_volume = residential_buildings['volume'].sum() if len(residential_buildings) > 0 else 0
                census_gdf.at[idx, 'total_v_res_buildings'] = total_residential_volume
            
            self.pipeline.log_info(self.calculator_name, f"Calculated residential volumes for {len(census_gdf)} census zones")
            return census_gdf
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to calculate residential volumes: {str(e)}")
            return census_gdf
    
    def _filter_to_project_boundary(self, census_building_gdf: gpd.GeoDataFrame, project_boundary: Dict[str, Any]) -> Optional[gpd.GeoDataFrame]:
        """Filter buildings to only include those within project_boundary"""
        try:
            # Convert project_boundary to shapely geometry
            if isinstance(project_boundary, dict):
                if 'geometry' in project_boundary:
                    boundary_geom = shape(project_boundary['geometry'])
                else:
                    boundary_geom = shape(project_boundary)
            else:
                self.pipeline.log_error(self.calculator_name, "Invalid project_boundary format")
                return None
            
            # Filter buildings within project boundary
            within_boundary = census_building_gdf[census_building_gdf.geometry.within(boundary_geom)]
            
            self.pipeline.log_info(self.calculator_name, f"Filtered to {len(within_boundary)} buildings within project boundary")
            return within_boundary
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to filter to project boundary: {str(e)}")
            return None
    
    def _update_database(self, buildings_gdf: gpd.GeoDataFrame, project_id: str, scenario_id: str):
        """Update database with building demographics"""
        try:
            # Filter out buildings with no census_zone_id
            buildings_gdf = buildings_gdf[buildings_gdf['census_zone_id'].notnull()]
            
            # Import Django models
            try:
                from cim_wizard.models import Building, BuildingProperties
                from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
                import json
                import pandas as pd
                from shapely.geometry import mapping
            except ImportError:
                self.pipeline.log_warning(self.calculator_name, "Django models not available - skipping database save")
                return
            
            self.pipeline.log_info(self.calculator_name, f"Updating database with {len(buildings_gdf)} buildings")
            
            # Convert census_id to integer, replacing nan with None
            buildings_gdf['census_id'] = buildings_gdf['census_zone_id'].apply(
                lambda x: int(x) if pd.notnull(x) else None
            )
            
            # Update each building in the database
            successful_updates = 0
            for idx, building in buildings_gdf.iterrows():
                try:
                    # Convert geometry to GeoJSON format for database
                    geom_json = mapping(building.geometry)
                    
                    # 1. Create/update Building record (geometry only)
                    building_obj, building_created = Building.objects.get_or_create(
                        building_id=building['building_id'],
                        lod=building['lod'],
                        defaults={
                            'building_geometry': GEOSGeometry(json.dumps(geom_json)),
                            'building_geometry_source': building['source'],
                            'census_id': building['census_id']
                        }
                    )
                    
                    if not building_created:
                        # Update existing building geometry
                        building_obj.building_geometry = GEOSGeometry(json.dumps(geom_json))
                        building_obj.building_geometry_source = building['source']
                        building_obj.census_id = building['census_id']
                        building_obj.save()
                    
                    # 2. Create/update BuildingProperties record (all demographic data)
                    props_obj, props_created = BuildingProperties.objects.get_or_create(
                        building_id=building['building_id'],
                        project_id=project_id,
                        scenario_id=scenario_id,
                        lod=building['lod'],
                        defaults={
                            'height': float(building['height']) if pd.notnull(building['height']) else None,
                            'area': float(building['area']) if pd.notnull(building['area']) else None,
                            'volume': float(building['volume']) if pd.notnull(building['volume']) else None,
                            'number_of_floors': int(building['number_of_floors']) if pd.notnull(building['number_of_floors']) else None,
                            'type': building['building_type'],
                            'const_period_census': building['const_period_census'] if pd.notnull(building['const_period_census']) else None,
                            'const_year': int(building['const_year']) if pd.notnull(building['const_year']) else None,
                            'const_TABULA': building['const_TABULA'] if pd.notnull(building['const_TABULA']) else None,
                            'n_people': int(building['n_people']) if pd.notnull(building['n_people']) else 0,
                            'n_family': int(building['n_family']) if pd.notnull(building['n_family']) else 0
                        }
                    )
                    
                    if not props_created:
                        # Update existing building properties
                        props_obj.height = float(building['height']) if pd.notnull(building['height']) else None
                        props_obj.area = float(building['area']) if pd.notnull(building['area']) else None
                        props_obj.volume = float(building['volume']) if pd.notnull(building['volume']) else None
                        props_obj.number_of_floors = int(building['number_of_floors']) if pd.notnull(building['number_of_floors']) else None
                        props_obj.type = building['building_type']
                        props_obj.const_period_census = building['const_period_census'] if pd.notnull(building['const_period_census']) else None
                        props_obj.const_year = int(building['const_year']) if pd.notnull(building['const_year']) else None
                        props_obj.const_TABULA = building['const_TABULA'] if pd.notnull(building['const_TABULA']) else None
                        props_obj.n_people = int(building['n_people']) if pd.notnull(building['n_people']) else 0
                        props_obj.n_family = int(building['n_family']) if pd.notnull(building['n_family']) else 0
                        props_obj.save()
                    
                    successful_updates += 1
                    
                except Exception as e:
                    self.pipeline.log_error(self.calculator_name, f"Failed to update building {building['building_id']}: {str(e)}")
                    continue
            
            self.pipeline.log_info(self.calculator_name, f"Successfully updated database with {successful_updates}/{len(buildings_gdf)} buildings")
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to update database: {str(e)}")
            raise
    
    def _create_result(self, final_buildings, census_gdf, year_accuracy, pop_accuracy, family_accuracy, project_id, scenario_id, type_calc):
        """Create the final result dictionary"""
        # Get building type assignment errors from type_calc
        building_type_errors = getattr(type_calc, 'zone_assignment_errors', [])
        
        return {
            'project_id': project_id,
            'scenario_id': scenario_id,
            'building_demographics': {
                'total_buildings': len(final_buildings),
                'residential_buildings': len(final_buildings[final_buildings['building_type'] == 'residential']),
                'total_population': float(final_buildings['n_people'].sum()),
                'total_families': float(final_buildings['n_family'].sum()),
                'total_volume': float(final_buildings['volume'].sum()),
                'total_area': float(final_buildings['area'].sum())
            },
            'accuracy_report': {
                'total_buildings_processed': len(final_buildings),
                'census_zones_processed': len(census_gdf),
                'construction_years_accuracy': f"Assigned years to {year_accuracy.get('buildings_assigned', 0)} buildings",
                'population_distribution_accuracy': f"Distributed {pop_accuracy.get('population_distributed', 0):.0f} people across {pop_accuracy.get('zones_processed', 0)} zones",
                'building_type_assignment': {
                    'method': 'strict_criteria',
                    'criteria': 'height > 8m AND area > 100m²',
                    'total_actual_residential': len(final_buildings[final_buildings['building_type'] == 'residential']),
                    'total_census_residential': int(census_gdf['total_n_res_buildings'].sum()),
                    'overall_error': len(final_buildings[final_buildings['building_type'] == 'residential']) - int(census_gdf['total_n_res_buildings'].sum()),
                    'zone_errors': building_type_errors
                }
            },
            'census_summary': {
                'total_zones': len(census_gdf),
                'total_population': float(census_gdf['P1'].sum()),
                'total_families': float(census_gdf['PF1'].sum()),
                'total_residential_volume': float(census_gdf['total_v_res_buildings'].sum())
            },
            'status': 'success',
            'message': f'Successfully processed demographics for {len(final_buildings)} buildings in {len(census_gdf)} census zones'
        }
    
    def save_to_database(self):
        """Save building demographic data to database - required by pipeline"""
        return True  # Database save is handled in _update_database 