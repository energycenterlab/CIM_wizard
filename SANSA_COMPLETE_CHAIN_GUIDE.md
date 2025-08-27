# Complete Chain Endpoint Guide for Sansa Boundary

## 🚀 New Endpoint: `/api/pipeline/execute_complete_chain`

This endpoint automatically executes ALL calculators in the correct order, chaining results from one to the next.

## 📋 Postman Setup

### Endpoint
```
POST http://localhost:8000/api/pipeline/execute_complete_chain
```

### Headers
```
Content-Type: application/json
```

### Request Body
```json
{
  "project_name": "Sansa_Project",
  "scenario_name": "Current_State",
  "project_boundary": {
    "type": "FeatureCollection",
    "name": "Sansa_boundary",
    "crs": { 
      "type": "name", 
      "properties": { 
        "name": "urn:ogc:def:crs:OGC:1.3:CRS84" 
      } 
    },
    "features": [
      { 
        "type": "Feature", 
        "properties": { "id": 1 }, 
        "geometry": { 
          "type": "MultiPolygon", 
          "coordinates": [
            [
              [
                [ 7.680074733154416, 45.062201539127464 ],
                [ 7.687747024566612, 45.059402634535033 ],
                [ 7.684256625898402, 45.054759745740526 ],
                [ 7.677391077574613, 45.057081190137779 ],
                [ 7.677012402247402, 45.057624506911601 ],
                [ 7.678510639411586, 45.060077664466149 ],
                [ 7.680074733154416, 45.062201539127464 ]
              ]
            ]
          ]
        }
      }
    ]
  }
}
```

## 🔄 What This Endpoint Does

The endpoint automatically executes the following calculators in sequence:

### Milestone 1: Initialize Basic Data
1. **scenario_geo** - Initialize scenario geometry from project boundary
2. **building_geo** - Extract building geometries from OSM
3. **building_props** - Initialize building properties

### Milestone 2: Calculate Physical Attributes
4. **building_height** - Calculate building heights from DSM/DTM rasters
5. **building_area** - Calculate building footprint areas
6. **scenario_census_boundary** - Get census boundary for the scenario

### Milestone 3: Calculate Derived Attributes
7. **building_volume** - Calculate building volumes
8. **building_n_floors** - Estimate number of floors from height

### Milestone 4: Calculate Demographics
9. **census_population** - Get total population from census
10. **building_type** - Determine building types
11. **building_population** - Distribute population to buildings
12. **building_n_families** - Calculate number of families per building

### Milestone 5: Additional Attributes
13. **building_construction_year** - Estimate construction years
14. **building_demographic** - Calculate demographic details
15. **building_geo_lod12** - Generate LOD1/LOD2 3D geometries

## 📊 Expected Response

```json
{
  "project_id": "project_a1b2c3d4",
  "scenario_id": "scenario_e5f6g7h8",
  "project_name": "Sansa_Project",
  "scenario_name": "Current_State",
  "execution_chain": [
    {
      "feature": "scenario_geo",
      "method": "calculate_from_scenario_geo",
      "description": "Initialize scenario geometry from project boundary",
      "status": "success",
      "value_type": "dict"
    },
    {
      "feature": "building_geo",
      "method": "calculate_from_scenario_census_geo",
      "description": "Extract building geometries from OSM",
      "status": "success",
      "value_type": "dict"
    },
    // ... all other calculations ...
  ],
  "successful_calculations": [
    "scenario_geo",
    "building_geo",
    "building_props",
    // ... etc
  ],
  "failed_calculations": [],
  "results": {
    "scenario_geo": { /* GeoJSON data */ },
    "building_geo": { /* Building geometries */ },
    "building_height": [12.5, 15.2, 10.8, ...],
    "building_area": [150.0, 200.5, 175.3, ...],
    "building_volume": [1875.0, 3050.0, 1893.2, ...],
    "census_population": 1250,
    "building_population": [45, 62, 38, ...],
    // ... all other results ...
  },
  "summary": {
    "total_features_requested": 15,
    "successful_calculations": 15,
    "failed_calculations": 0,
    "success_rate": "100.0%",
    "total_buildings": 25,
    "average_height_m": 12.5,
    "max_height_m": 18.5,
    "min_height_m": 8.2,
    "total_area_m2": 3750.0,
    "average_area_m2": 150.0,
    "total_volume_m3": 46875.0,
    "average_volume_m3": 1875.0,
    "total_census_population": 1250,
    "total_distributed_population": 1250,
    "average_population_per_building": 50
  },
  "metadata": {
    "execution_time": "async",
    "pipeline_version": "2.0.0",
    "data_sources": ["OSM", "Census", "Raster Services"],
    "coordinate_system": "urn:ogc:def:crs:OGC:1.3:CRS84"
  }
}
```

## ⚡ Key Features

1. **Automatic Chaining**: Each calculator automatically uses results from previous calculators
2. **Error Handling**: If a calculation fails, it continues with the rest and reports failures
3. **Progress Tracking**: Shows which calculations succeeded and which failed
4. **Summary Statistics**: Provides aggregate statistics for all calculated values
5. **No Manual Setup**: No need to create projects or scenarios manually - everything is automatic

## 🎯 How It Works

1. **Input**: You provide just the project boundary GeoJSON
2. **Processing**: The endpoint:
   - Generates unique project and scenario IDs
   - Sets up the data context
   - Executes each calculator in the correct order
   - Passes results from one calculator to the next
3. **Output**: Complete analysis results with summary statistics

## 🔧 Testing in Postman

1. Create a new POST request
2. Set URL: `http://localhost:8000/api/pipeline/execute_complete_chain`
3. Set Headers: `Content-Type: application/json`
4. Copy the request body from above
5. Send the request
6. View the complete analysis results

## 📝 Notes

- The endpoint uses hardcoded service URLs for raster and census services
- It assumes these services are running on the same host (localhost:8000)
- The calculation chain is predefined but comprehensive
- Each calculator has fallback methods if the primary method fails
- Results are not saved to database (can be added if needed)

## 🚨 Prerequisites

Make sure you have:
1. Database running: `sudo docker-compose -f docker-compose.db.yml up -d`
2. Application running: `./start_app.sh dev`
3. Raster data loaded in the database
4. Census data available

## 💡 Alternative: Custom Chain

If you want to execute only specific calculators, you can still use the other endpoints:
- `/api/pipeline/execute` - For automatic dependency resolution
- `/api/pipeline/execute_explicit` - For manual method specification
- `/api/pipeline/calculate_feature` - For single feature calculation

But this new `/execute_complete_chain` endpoint is the simplest way to get a complete analysis!



