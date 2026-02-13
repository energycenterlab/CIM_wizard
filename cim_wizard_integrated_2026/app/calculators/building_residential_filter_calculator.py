"""
Building Residential Filter Calculator - Filter residential vs non-residential buildings
Determines filter_res attribute based on area, height, and OSM tags
"""
from typing import Optional, Dict, Any


class BuildingResidentialFilterCalculator:
    """Calculate filter_res attribute to separate residential from non-residential buildings"""
    
    def __init__(self, pipeline_executor):
        self.pipeline = pipeline_executor
        self.calculator_name = self.__class__.__name__
        
    def calculate_filter_res(self) -> Optional[Dict[str, Any]]:
        """
        Calculate filter_res based on building properties and OSM tags.
        
        Logic:
        - Conservative approach: mark as non-residential only when very sure
        - filter_res = False (non-residential) if:
          * area < 90 sq meters OR
          * height < 4 meters OR  
          * OSM tags clearly indicate non-residential use
        - filter_res = True (residential) for everything else
        
        Returns:
            Dictionary with filter_res results for the pipeline
        """
        
        try:
            # Get building data from pipeline (same pattern as other calculators)
            building_geo = self.pipeline.get_feature_safely('building_geo')
            if not building_geo:
                self.pipeline.log_error(self.calculator_name, "No building_geo data available")
                return None
            
            # Get building heights and areas from previous calculations
            building_heights = self.pipeline.get_feature_safely('building_height')
            building_area_data = self.pipeline.get_feature_safely('building_area')
            
            if not building_heights:
                self.pipeline.log_error(self.calculator_name, "No building_height data available")
                return None
                
            if not building_area_data:
                self.pipeline.log_error(self.calculator_name, "No building_area data available")
                return None
            
            # Extract buildings list
            buildings = building_geo.get('buildings', [])
            if not buildings:
                self.pipeline.log_error(self.calculator_name, "No buildings in building_geo data")
                return None
            
            # Extract areas from building_area_data
            building_areas = building_area_data.get('building_areas', [])
            if not building_areas:
                # Try to extract from building_properties
                building_properties = building_area_data.get('building_properties', [])
                if building_properties:
                    building_areas = [bp.get('area', 0) for bp in building_properties]
            
            if not building_areas:
                self.pipeline.log_error(self.calculator_name, "No building areas available")
                return None
            
            # Ensure we have heights list (should be a list of height values)
            if not isinstance(building_heights, list):
                self.pipeline.log_error(self.calculator_name, f"building_height data is not a list: {type(building_heights)}")
                return None
            
            # Create a simplified buildings list with required data
            buildings_data = []
            for i, building in enumerate(buildings):
                if i < len(building_heights) and i < len(building_areas):
                    # Extract properties from GeoJSON format
                    properties = building.get('properties', {})
                    building_data = {
                        'building_id': properties.get('building_id'),
                        'area': building_areas[i] if i < len(building_areas) else 0,
                        'height': building_heights[i] if i < len(building_heights) else 0,
                        'building': properties.get('building', 'yes'),
                        'amenity': properties.get('amenity', None)
                    }
                    buildings_data.append(building_data)
            
            if not buildings_data:
                self.pipeline.log_error(self.calculator_name, "No valid building data after processing")
                return None
            
            self.pipeline.log_info(self.calculator_name, "Starting residential filter calculation")
            
            # Process buildings and calculate filter_res
            filter_res_values = []
            
            # Track filtering statistics
            total_buildings = len(buildings_data)
            non_residential_count = 0
            area_filtered = 0
            height_filtered = 0
            osm_filtered = 0
            
            # Get OSM tag lists
            osm_non_residential_tags = self._get_non_residential_osm_tags()
            amenity_non_residential_tags = self._get_non_residential_amenity_tags()
            
            # Process each building
            for building_data in buildings_data:
                is_residential = True  # Default to residential
                
                # Criterion 1: Area filter (< 90 sq meters likely non-residential)
                if building_data['area'] < 90.0:
                    is_residential = False
                    area_filtered += 1
                
                # Criterion 2: Height filter (< 4 meters likely non-residential)
                elif building_data['height'] < 4.0:
                    is_residential = False
                    height_filtered += 1
                
                # Criterion 3: OSM building tag filter
                elif building_data['building'] in osm_non_residential_tags:
                    is_residential = False
                    osm_filtered += 1
                
                # Criterion 4: OSM amenity tag filter
                elif building_data['amenity'] and building_data['amenity'] in amenity_non_residential_tags:
                    is_residential = False
                    osm_filtered += 1
                
                filter_res_values.append(is_residential)
                if not is_residential:
                    non_residential_count += 1
            
            # Calculate final statistics
            residential_count = total_buildings - non_residential_count
            residential_percentage = (residential_count / total_buildings) * 100 if total_buildings > 0 else 0
            
            # Log summary
            self.pipeline.log_info(self.calculator_name, f"Residential filter calculation completed:")
            self.pipeline.log_info(self.calculator_name, f"  - Total buildings processed: {total_buildings}")
            self.pipeline.log_info(self.calculator_name, f"  - Residential (filter_res=True): {residential_count} ({residential_percentage:.1f}%)")
            self.pipeline.log_info(self.calculator_name, f"  - Non-residential (filter_res=False): {non_residential_count} ({100-residential_percentage:.1f}%)")
            self.pipeline.log_info(self.calculator_name, f"    * Filtered by area < 90 sq m: {area_filtered}")
            self.pipeline.log_info(self.calculator_name, f"    * Filtered by height < 4 m: {height_filtered}")
            self.pipeline.log_info(self.calculator_name, f"    * Filtered by OSM tags: {osm_filtered}")
            
            # Return results in the format expected by the pipeline
            return {
                'filter_res': filter_res_values,
                'total_buildings': total_buildings,
                'residential_count': residential_count,
                'non_residential_count': non_residential_count,
                'statistics': {
                    'area_filtered': area_filtered,
                    'height_filtered': height_filtered,
                    'osm_filtered': osm_filtered,
                    'residential_percentage': residential_percentage
                }
            }
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to calculate residential filter: {str(e)}")
            return None
    
    def _get_non_residential_osm_tags(self) -> list:
        """
        Return OSM building tags that clearly indicate non-residential use.
        Conservative list - only include tags that are definitely not residential.
        """
        return [
            'school',
            'hospital', 
            'church',
            'mosque',
            'synagogue',
            'temple',
            'chapel',
            'cathedral',
            'commercial',
            'retail',
            'office',
            'industrial',
            'warehouse',
            'factory',
            'civic',
            'public',
            'government',
            'fire_station',
            'police',
            'prison',
            'courthouse',
            'town_hall',
            'library',
            'museum',
            'theatre',
            'cinema',
            'stadium',
            'sports_hall',
            'gym',
            'supermarket',
            'mall',
            'shop',
            'store',
            'hotel',
            'motel',
            'hostel',
            'restaurant',
            'cafe',
            'bar',
            'pub',
            'nightclub',
            'bank',
            'gas_station',
            'parking',
            'garage',
            'hangar',
            'shed',
            'barn',
            'greenhouse',
            'stable',
            'cowshed',
            'farm_auxiliary',
            'kindergarten',
            'university',
            'college',
            'research',
            'laboratory'
        ]
    
    def _get_non_residential_amenity_tags(self) -> list:
        """
        Return OSM amenity tags that clearly indicate non-residential use.
        """
        return [
            'school',
            'hospital',
            'clinic',
            'pharmacy',
            'dentist',
            'veterinary',
            'place_of_worship',
            'bank',
            'atm',
            'post_office',
            'library',
            'museum',
            'theatre',
            'cinema',
            'community_centre',
            'fire_station',
            'police',
            'prison',
            'courthouse',
            'townhall',
            'embassy',
            'restaurant',
            'cafe',
            'bar',
            'pub',
            'fast_food',
            'food_court',
            'biergarten',
            'nightclub',
            'fuel',
            'charging_station',
            'parking',
            'marketplace',
            'waste_disposal',
            'recycling',
            'toilets',
            'shower',
            'kindergarten',
            'childcare',
            'university',
            'college',
            'research_institute',
            'language_school',
            'driving_school',
            'music_school'
        ]
