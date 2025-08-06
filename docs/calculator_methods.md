# Calculator Methods Logic

## Overview

This document describes the logic and implementation of all calculator methods in CIM Wizard. Each calculator is responsible for calculating a specific feature using multiple methods with fallback mechanisms.

## Calculator Classes

### 1. BuildingHeightCalculator

**Purpose**: Calculate building height

**Methods**:
1. `calculate_from_raster_service()` (Priority 1)
   - Uses integrated raster service
   - Calculates DSM - DTM
   - Caches results for performance
   
2. `calculate_from_osm_height()` (Priority 2)
   - Extracts height from OSM tags
   - Checks: height, building:height, building_height
   - Falls back to levels * 3.5m
   
3. `calculate_default_estimate()` (Priority 3)
   - Uses building type defaults
   - Residential: 10.5m, Commercial: 14m
   - Generic default: 10.5m

### 2. BuildingAreaCalculator

**Purpose**: Calculate building footprint area

**Methods**:
1. `calculate_from_geometry()` (Priority 1)
   - Uses Shapely for area calculation
   - Projects to appropriate CRS if needed
   - Returns area in square meters

### 3. BuildingVolumeCalculator

**Purpose**: Calculate building volume

**Methods**:
1. `calculate_from_height_and_area()` (Priority 1)
   - Simple multiplication: height × area
   - Requires pre-calculated height and area
   - Validates input ranges

### 4. BuildingNFloorsCalculator

**Purpose**: Estimate number of floors

**Methods**:
1. `estimate_by_height()` (Priority 1)
   - Divides height by floor height
   - Uses building type for floor height:
     - Residential: 3.0m per floor
     - Commercial: 3.5m per floor
     - Industrial: 4.0m per floor
   - Default: 3.3m per floor

### 5. BuildingTypeCalculator

**Purpose**: Determine building type

**Methods**:
1. `by_census_osm()` (Priority 1)
   - Combines census and OSM data
   - Priority order:
     1. OSM building tag
     2. Census zone characteristics
     3. Building size heuristics
   - Categories: residential, commercial, industrial, office, retail

### 6. BuildingPopulationCalculator

**Purpose**: Estimate building population

**Methods**:
1. `calculate_from_volume_distribution()` (Priority 1)
   - Distributes census population by volume
   - Formula: `building_pop = (building_vol / total_vol) × census_pop`
   - Adjusts for building type
   
2. `by_census_osm()` (Priority 2)
   - Uses census demographic data
   - Considers building type
   - Applies occupancy factors

### 7. BuildingNFamiliesCalculator

**Purpose**: Estimate number of families

**Methods**:
1. `calculate_from_population()` (Priority 1)
   - Divides population by average family size
   - Default family size: 2.3 persons
   
2. `by_census_osm()` (Priority 2)
   - Uses census family statistics
   - Adjusts for building type
   - Residential only

### 8. BuildingConstructionYearCalculator

**Purpose**: Estimate construction year

**Methods**:
1. `by_census_osm()` (Priority 1)
   - Maps census periods to years:
     - E8: Before 1918 → random(1850, 1918)
     - E9: 1919-1945 → random(1919, 1945)
     - E10: 1946-1960 → random(1946, 1960)
     - E11: 1961-1970 → random(1961, 1970)
     - E12: 1971-1980 → random(1971, 1980)
     - E13: 1981-1990 → random(1981, 1990)
     - E14: 1991-2000 → random(1991, 2000)
     - E15: 2001-2005 → random(2001, 2005)
     - E16: After 2005 → random(2006, current_year)

### 9. ScenarioGeoCalculator

**Purpose**: Process scenario geometry

**Methods**:
1. `calculate_from_scenario_geo()` (Priority 1)
   - Validates GeoJSON format
   - Extracts boundary polygon
   - Calculates centroid
   
2. `calculate_from_buildings_geo()` (Priority 2)
   - Aggregates building geometries
   - Creates convex hull
   - Calculates bounding box

### 10. BuildingGeoCalculator

**Purpose**: Process building geometry

**Methods**:
1. `calculate_from_building_geo()` (Priority 1)
   - Validates geometry
   - Ensures polygon closure
   - Fixes invalid geometries
   
2. `calculate_from_scenario_census_geo()` (Priority 2)
   - Queries buildings from database
   - Filters by census boundary
   - Returns building collection

### 11. ScenarioCensusBoundaryCalculator

**Purpose**: Get census boundaries for scenario

**Methods**:
1. `calculate_from_census_api()` (Priority 1)
   - Now uses integrated census service
   - Queries census zones intersecting scenario
   - Returns MultiPolygon of census boundaries

### 12. CensusPopulationCalculator

**Purpose**: Calculate total census population

**Methods**:
1. `calculate_from_census_boundary()` (Priority 1)
   - Sums P1 field from census zones
   - Handles overlapping zones
   - Returns total population

### 13. BuildingDemographicCalculator

**Purpose**: Calculate demographic attributes

**Methods**:
1. `by_census_osm()` (Priority 1)
   - Complex calculation combining:
     - Age distribution from census
     - Family composition
     - Education levels
     - Employment statistics
   - Returns demographic profile dict

### 14. BuildingGeoLod12Calculator

**Purpose**: Generate LoD 1.2 geometry

**Methods**:
1. `by_footprint_height()` (Priority 1)
   - Extrudes 2D footprint by height
   - Creates semantic surfaces:
     - Floor: bottom polygon
     - Roof: top polygon
     - Walls: vertical surfaces
   - Compatible with 3DCityDB

### 15. BuildingPropsCalculator

**Purpose**: Initialize building properties

**Methods**:
1. `init()` (Priority 1)
   - Creates property container
   - Sets default values
   - Links to building geometry

## Calculation Dependencies

### Dependency Graph

```
scenario_geo
    ├── building_geo
    │   ├── building_area
    │   ├── building_props
    │   └── scenario_census_boundary
    │       └── census_population
    │           └── building_population
    │               └── building_n_families
    │
    └── building_height (requires raster_service)
        ├── building_n_floors
        ├── building_volume
        │   └── building_population
        └── building_geo_lod12

building_type (requires census_boundary)
    └── building_construction_year
        └── building_demographic
```

## Method Selection Logic

### Priority System

Each method has a priority (1 = highest):
1. Try methods in priority order
2. Check if dependencies are satisfied
3. Execute first viable method
4. Fall back to next priority on failure

### Dependency Checking

```python
def check_dependencies(self, dependencies):
    for dep in dependencies:
        if dep.endswith('_service'):
            # Check service availability
            if dep == 'raster_service':
                return self.data_manager.get_raster_service() is not None
        else:
            # Check data availability
            if not self.data_manager.has_feature(dep):
                return False
    return True
```

## Integration with Services

### Census Service Integration

```python
def get_census_data(self):
    census_service = self.data_manager.get_census_service()
    census_zones = census_service.get_census_by_polygon(polygon_coords)
    return census_zones
```

### Raster Service Integration

```python
def get_building_height(self):
    raster_service = self.data_manager.get_raster_service()
    result = raster_service.calculate_building_height(
        building_geometry=geometry,
        use_cache=True
    )
    return result['building_height']
```

## Error Handling

Each calculator method handles errors gracefully:

1. **Input Validation**: Check required inputs exist
2. **Type Validation**: Ensure correct data types
3. **Range Validation**: Check values are within bounds
4. **Service Errors**: Handle database/service failures
5. **Fallback**: Return None to trigger next method

## Performance Optimization

### Caching Strategy

1. **Result Caching**: Store in data_manager
2. **Service Caching**: Database-level caching
3. **Calculator Caching**: Reuse calculator instances

### Parallel Execution

Features without dependencies can run in parallel:
```python
executor.execute_pipeline(
    features=['building_height', 'building_area', 'building_type'],
    parallel=True
)
```

## Adding New Calculators

### Step 1: Create Calculator Class

```python
class NewFeatureCalculator:
    def __init__(self, executor, data_manager):
        self.executor = executor
        self.data_manager = data_manager
        self.calculator_name = "NewFeatureCalculator"
    
    def primary_method(self):
        # Implementation
        pass
```

### Step 2: Update Configuration

```json
{
  "features": {
    "new_feature": {
      "class_path": "app.calculators.new_feature_calculator",
      "class_name": "NewFeatureCalculator",
      "methods": [
        {
          "priority": 1,
          "input_dependencies": ["required_feature"],
          "method_name": "primary_method"
        }
      ]
    }
  }
}
```

### Step 3: Add to Data Manager

```python
# In CimWizardDataManager.__init__
self.new_feature = FeatureProxy('new_feature')
self.new_feature_data = None
```

## Testing Calculators

### Unit Testing

```python
def test_building_height_calculator():
    # Setup
    data_manager = CimWizardDataManager()
    executor = CimWizardPipelineExecutor(data_manager)
    
    # Set context
    data_manager.set_context(
        building_geo_data=test_geometry,
        db_session=test_db
    )
    
    # Execute
    calculator = BuildingHeightCalculator(executor, data_manager)
    height = calculator.calculate_from_raster_service()
    
    # Assert
    assert height is not None
    assert 0 < height < 500
```

This architecture ensures reliable, maintainable, and extensible feature calculation with multiple fallback strategies and integrated service access.