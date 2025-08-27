# CIM Wizard Integrated - API Setup & Postman Examples

## Setup Instructions

### 1. Start Docker Database
```bash
# Start the PostGIS database with your data
docker run -d \
    --name cim_sansalva \
    -p 5433:5432 \
    -e POSTGRES_DB=cim_wizard_integrated \
    -e POSTGRES_USER=cim_wizard_user \
    -e POSTGRES_PASSWORD=cim_wizard_password \
    taherdoust/cim_sansalva:latest

# Verify it's running
docker ps
```

### 2. Install Python Dependencies
```bash
# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Start FastAPI Application
```bash
# Run the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# The API will be available at: http://localhost:8000
# Swagger docs: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

## Main Endpoint: Process Project Boundary

### Endpoint
`POST http://localhost:8000/api/project/process_boundary`

### Headers
```json
{
    "Content-Type": "application/json"
}
```

### Example 1: Small Area in Torino (San Salvario District)
```json
{
    "project_name": "San Salvario Urban Analysis",
    "scenario_name": "Current State 2024",
    "boundary_polygon": [
        [7.6731, 45.0505],
        [7.6831, 45.0505],
        [7.6831, 45.0405],
        [7.6731, 45.0405],
        [7.6731, 45.0505]
    ],
    "fetch_osm": true,
    "run_full_pipeline": true
}
```

### Example 2: Torino City Center
```json
{
    "project_name": "Torino Centro Analysis",
    "scenario_name": "Urban Development 2024",
    "boundary_polygon": [
        [7.6600, 45.0750],
        [7.6900, 45.0750],
        [7.6900, 45.0550],
        [7.6600, 45.0550],
        [7.6600, 45.0750]
    ],
    "fetch_osm": true,
    "run_full_pipeline": true
}
```

### Example 3: Larger Torino Area (Complete Census Coverage)
```json
{
    "project_name": "Greater Torino Metropolitan",
    "scenario_name": "Metropolitan Analysis",
    "boundary_polygon": [
        [7.6000, 45.1000],
        [7.7500, 45.1000],
        [7.7500, 45.0000],
        [7.6000, 45.0000],
        [7.6000, 45.1000]
    ],
    "fetch_osm": true,
    "run_full_pipeline": true
}
```

## Chainable Pipeline Endpoint

### Endpoint
`POST http://localhost:8000/api/pipeline/chainable`

### Headers
```json
{
    "Content-Type": "application/json"
}
```

### Example 1: Basic Chain with Scenario and Building Height
```json
{
    "chain": "scenario_geo.calculate_from_scenario_id|building_height.calculate_default_estimate",
    "inputs": {
        "project_id": "torino_analysis_2024",
        "scenario_id": "current_state",
        "building_id": "building_123"
    }
}
```

### Example 2: Complex Chain with Multiple Features
```json
{
    "chain": "scenario_geo.calculate_from_scenario_id|building_height.calculate_default_estimate|building_area.calculate_from_geometry|building_volume.calculate_from_height_area",
    "inputs": {
        "project_id": "san_salvario_analysis",
        "scenario_id": "development_scenario_1",
        "building_geo": {
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
                                    [7.680074733154416, 45.062201539127464],
                                    [7.687747024566612, 45.059402634535033],
                                    [7.684256625898402, 45.054759745740526],
                                    [7.677391077574613, 45.057081190137779],
                                    [7.677012402247402, 45.057624506911601],
                                    [7.678510639411586, 45.060077664466149],
                                    [7.680074733154416, 45.062201539127464]
                                ]
                            ]
                        ]
                    }
                }
            ]
        }
    }
}
```

### Example 3: Chain with Census Data Integration
```json
{
    "chain": "census_data.load_by_boundary|building_population.estimate_from_census|building_energy.estimate_consumption",
    "inputs": {
        "project_id": "torino_energy_analysis",
        "scenario_id": "baseline_2024",
        "boundary_polygon": [
            [7.6731, 45.0505],
            [7.6831, 45.0505],
            [7.6831, 45.0405],
            [7.6731, 45.0405],
            [7.6731, 45.0505]
        ]
    }
}
```

### Example 4: Raster-Based Height Calculation Chain
```json
{
    "chain": "raster_data.load_dtm_dsm|building_height.calculate_from_raster|building_volume.calculate_from_raster_height",
    "inputs": {
        "project_id": "torino_3d_analysis",
        "scenario_id": "high_precision",
        "building_id": "building_456",
        "raster_bounds": {
            "min_lon": 7.6731,
            "max_lon": 7.6831,
            "min_lat": 45.0405,
            "max_lat": 45.0505
        }
    }
}
```

### Example 4: Quick Test (No OSM, No Pipeline)
```json
{
    "project_name": "Test Project",
    "scenario_name": "Test Scenario",
    "boundary_polygon": [
        [7.6731, 45.0505],
        [7.6741, 45.0505],
        [7.6741, 45.0495],
        [7.6731, 45.0495],
        [7.6731, 45.0505]
    ],
    "fetch_osm": false,
    "run_full_pipeline": false
}
```

## Response Structure

### Successful Response (200 OK)
```json
{
    "success": true,
    "project": {
        "project_id": "proj_abc12345",
        "scenario_id": "scen_def67890",
        "project_name": "Torino Centro Analysis",
        "scenario_name": "Urban Development 2024",
        "boundary": {
            "type": "Polygon",
            "coordinates": [...]
        },
        "center": [7.675, 45.065]
    },
    "statistics": {
        "total_buildings": 250,
        "census_zones": 15,
        "processed_buildings": 10
    },
    "buildings": [
        {
            "building_id": "osm_123456",
            "geometry": {...},
            "properties": {
                "building": "yes",
                "height": "15"
            }
        }
    ],
    "census_data": [
        {
            "census_id": 12720000331,
            "comune": "Torino",
            "regione": "Piemonte",
            "population": 208,
            "geometry": {...}
        }
    ],
    "pipeline_results": [
        {
            "building_id": "osm_123456",
            "features": {
                "building_height": 15.5,
                "building_area": 120.5,
                "building_volume": 1867.75,
                "building_n_floors": 5,
                "building_type": "residential",
                "building_population": 8.5
            }
        }
    ],
    "message": "Project proj_abc12345 created successfully with 250 buildings"
}
```

## Other Useful Endpoints

### Get Project Summary
`GET http://localhost:8000/api/project/projects/{project_id}/summary`

### Get All Projects
`GET http://localhost:8000/api/vector/projects`

### Calculate Building Height (Single)
`POST http://localhost:8000/api/raster/height`
```json
{
    "building_geometry": {
        "type": "Polygon",
        "coordinates": [[[7.673, 45.050], [7.674, 45.050], [7.674, 45.049], [7.673, 45.049], [7.673, 45.050]]]
    },
    "building_id": "test_building_001",
    "use_cache": true
}
```

### Query Census by Polygon
`POST http://localhost:8000/api/census/spatial`
```json
{
    "polygon_array": [[7.673, 45.050], [7.674, 45.050], [7.674, 45.049], [7.673, 45.049], [7.673, 45.050]]
}
```

## Testing Flow

1. **Start Small**: Use Example 1 with a small area to test the complete pipeline
2. **Check Database**: Verify data is saved in PostgreSQL tables
3. **Expand Area**: Use larger boundaries once the system works
4. **Monitor Performance**: Pipeline processing can take time for many buildings

## Database Tables to Check

After running the pipeline, check these tables in pgAdmin:

- `cim_vector.project_scenario` - Project metadata
- `cim_vector.building` - Building geometries
- `cim_vector.building_properties` - Calculated properties
- `cim_census.census_geo` - Census data (already loaded)
- `cim_raster.dtm_raster` - Elevation data (already loaded)
- `cim_raster.dsm_raster` - Surface data (already loaded)
- `cim_raster.building_height_cache` - Cached height calculations

## Troubleshooting

### Database Connection Error
- Ensure Docker container is running: `docker ps`
- Check port 5433 is not blocked
- Verify credentials in `app/db/database.py`

### OSM Data Not Loading
- The Overpass API might be slow or rate-limited
- Try smaller boundaries first
- Set `fetch_osm: false` to skip OSM fetching

### Pipeline Errors
- Check that census and raster data are loaded
- Verify all calculators are properly imported
- Set `run_full_pipeline: false` to skip pipeline processing

## Performance Tips

- Start with small boundaries (< 100 buildings)
- The pipeline processes first 10 buildings by default (modify in code if needed)
- Use `fetch_osm: false` for testing project creation only
- Use `run_full_pipeline: false` to test OSM fetching only


