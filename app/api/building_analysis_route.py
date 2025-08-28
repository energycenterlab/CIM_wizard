"""
Building Analysis Pipeline Route - Executes building-specific calculators
Focuses on physical building properties without demographic calculations
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import json
import uuid
from datetime import datetime

from app.db.database import get_db
from app.core.data_manager import CimWizardDataManager
from app.core.pipeline_executor import CimWizardPipelineExecutor
from app.models.vector import Building, BuildingProperties, ProjectScenario

router = APIRouter()


def get_pipeline_executor(db: Session):
    """Create pipeline executor with database session"""
    data_manager = CimWizardDataManager(db_session=db)
    executor = CimWizardPipelineExecutor(data_manager)
    return executor, data_manager


def save_scenario_to_database(
    db: Session,
    project_id: str,
    scenario_id: str,
    project_name: str,
    scenario_name: str,
    scenario_geo: Dict[str, Any]
) -> bool:
    """
    Save or update project scenario in the database
    
    Args:
        db: Database session
        project_id: Project identifier
        scenario_id: Scenario identifier
        project_name: Project name
        scenario_name: Scenario name
        scenario_geo: Scenario geometry data
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        from shapely.geometry import shape, mapping
        from geoalchemy2.shape import from_shape
        
        # Extract geometry from scenario_geo
        geometry = scenario_geo.get('geometry')
        if not geometry:
            return False
        
        # Convert MultiPolygon to Polygon if needed for project_boundary
        geom_shape = shape(geometry)
        
        # Database expects Polygon, so we need to convert MultiPolygon
        if geometry['type'] == 'MultiPolygon':
            print(f"Converting MultiPolygon to Polygon (coords count: {len(geometry['coordinates'])})")
            if len(geometry['coordinates']) == 1:
                # Create a Polygon from the single MultiPolygon part
                polygon_coords = geometry['coordinates'][0]
                from shapely.geometry import Polygon
                boundary_shape = Polygon(polygon_coords[0], polygon_coords[1:] if len(polygon_coords) > 1 else [])
                print(f"Converted to Polygon: {boundary_shape.geom_type}")
            else:
                # Multiple polygons - use the largest one
                print(f"Multiple polygons detected, using the first one")
                polygon_coords = geometry['coordinates'][0]
                boundary_shape = Polygon(polygon_coords[0], polygon_coords[1:] if len(polygon_coords) > 1 else [])
        else:
            boundary_shape = geom_shape
            print(f"Using original geometry type: {boundary_shape.geom_type}")
        
        # Calculate center point
        center_shape = boundary_shape.centroid
        
        # Check if scenario already exists
        scenario = db.query(ProjectScenario).filter_by(
            project_id=project_id,
            scenario_id=scenario_id
        ).first()
        
        if not scenario:
            # Create new scenario
            scenario = ProjectScenario(
                project_id=project_id,
                scenario_id=scenario_id,
                project_name=project_name,
                scenario_name=scenario_name,
                project_boundary=from_shape(boundary_shape, srid=4326),
                project_center=from_shape(center_shape, srid=4326),
                project_zoom=15,
                project_crs=4326,
                created_at=datetime.utcnow()
            )
            db.add(scenario)
        else:
            # Update existing scenario
            scenario.project_name = project_name
            scenario.scenario_name = scenario_name
            scenario.project_boundary = from_shape(boundary_shape, srid=4326)
            scenario.project_center = from_shape(center_shape, srid=4326)
            scenario.updated_at = datetime.utcnow()
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"ERROR saving scenario to database: {str(e)}")
        print(f"Project ID: {project_id}, Scenario ID: {scenario_id}")
        print(f"Project Name: {project_name}, Scenario Name: {scenario_name}")
        print(f"Scenario Geo Keys: {list(scenario_geo.keys()) if scenario_geo else 'None'}")
        import traceback
        traceback.print_exc()
        return False


def save_building_to_database(
    db: Session,
    building_data: Dict[str, Any],
    project_id: str,
    scenario_id: str,
    lod: int = 0
) -> bool:
    """
    Save or update building geometry and properties in the database
    
    Args:
        db: Database session
        building_data: Building data dictionary with geometry and properties
        project_id: Project identifier
        scenario_id: Scenario identifier
        lod: Level of detail (default 0)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Extract building_id from properties if it's a GeoJSON Feature
        building_id = building_data.get('building_id')
        if not building_id and 'properties' in building_data:
            building_id = building_data['properties'].get('building_id')
        
        if not building_id:
            print(f"No building_id found in building data: {building_data.keys()}")
            return False
        
        # Save or update Building
        building_geo = db.query(Building).filter_by(
            building_id=building_id,
            lod=lod
        ).first()
        
        if not building_geo:
            # Convert geometry to WKT or GeoJSON format for PostGIS
            from shapely.geometry import shape
            from geoalchemy2.shape import from_shape
            
            geom_dict = building_data.get('geometry', {})
            if geom_dict:
                geom_shape = shape(geom_dict)
                building_geo = Building(
                    building_id=building_id,
                    lod=lod,
                    building_geometry=from_shape(geom_shape, srid=4326),
                    building_geometry_source='integrated_database',
                    created_at=datetime.utcnow()
                )
            else:
                building_geo = Building(
                    building_id=building_id,
                    lod=lod,
                    building_geometry_source='integrated_database',
                    created_at=datetime.utcnow()
                )
            db.add(building_geo)
        else:
            # Update existing building
            geom_dict = building_data.get('geometry', {})
            if geom_dict:
                from shapely.geometry import shape
                from geoalchemy2.shape import from_shape
                geom_shape = shape(geom_dict)
                building_geo.building_geometry = from_shape(geom_shape, srid=4326)
            building_geo.updated_at = datetime.utcnow()
        
        # Save or update BuildingProperties
        building_props = db.query(BuildingProperties).filter_by(
            building_id=building_id,
            project_id=project_id,
            scenario_id=scenario_id,
            lod=lod
        ).first()
        
        if not building_props:
            building_props = BuildingProperties(
                building_id=building_id,
                project_id=project_id,
                scenario_id=scenario_id,
                lod=lod,
                building_fk=building_geo.id if building_geo else None,
                created_at=datetime.utcnow()
            )
            db.add(building_props)
        else:
            # Update the building_fk if it's not set
            if not building_props.building_fk and building_geo:
                building_props.building_fk = building_geo.id
        
        # Update properties if they exist in the data
        # For GeoJSON features, properties are in the 'properties' field
        props = building_data.get('properties', {})
        if not props:
            # Fallback: properties might be directly in building_data
            props = building_data
        if 'height' in props:
            building_props.height = float(props['height'])
        if 'area' in props:
            building_props.area = float(props['area'])
        if 'volume' in props:
            building_props.volume = float(props['volume'])
        if 'number_of_floors' in props:
            building_props.number_of_floors = int(props['number_of_floors'])
        
        building_props.updated_at = datetime.utcnow()
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"ERROR saving building to database: {str(e)}")
        print(f"Building ID: {building_data.get('building_id')}")
        print(f"Project ID: {project_id}, Scenario ID: {scenario_id}")
        import traceback
        traceback.print_exc()
        return False


def update_building_properties_in_database(
    db: Session,
    project_id: str,
    scenario_id: str,
    building_results: Dict[str, Any],
    property_name: str,
    property_values: List[Any]
) -> int:
    """
    Update specific building properties in the database
    
    Args:
        db: Database session
        project_id: Project identifier
        scenario_id: Scenario identifier
        building_results: Building geometry results containing building list
        property_name: Name of the property to update (height, area, volume, number_of_floors)
        property_values: List of property values corresponding to buildings
    
    Returns:
        int: Number of buildings updated
    """
    try:
        updated_count = 0
        buildings = building_results.get('buildings', [])
        
        for i, building in enumerate(buildings):
            if i >= len(property_values):
                break
                
            # Extract building_id from properties if it's a GeoJSON Feature
            building_id = building.get('building_id')
            if not building_id and 'properties' in building:
                building_id = building['properties'].get('building_id')
            
            if not building_id:
                print(f"No building_id found in building {i}: {building.keys()}")
                continue
            
            # Get or create BuildingProperties
            building_props = db.query(BuildingProperties).filter_by(
                building_id=building_id,
                project_id=project_id,
                scenario_id=scenario_id,
                lod=0
            ).first()
            
            if not building_props:
                # Need to get the building record for the foreign key
                building_record = db.query(Building).filter_by(
                    building_id=building_id,
                    lod=0
                ).first()
                
                building_props = BuildingProperties(
                    building_id=building_id,
                    project_id=project_id,
                    scenario_id=scenario_id,
                    lod=0,
                    building_fk=building_record.id if building_record else None,
                    created_at=datetime.utcnow()
                )
                db.add(building_props)
            
            # Update the specific property
            if property_name == 'height':
                building_props.height = float(property_values[i])
            elif property_name == 'area':
                building_props.area = float(property_values[i])
            elif property_name == 'volume':
                building_props.volume = float(property_values[i])
            elif property_name == 'number_of_floors':
                building_props.number_of_floors = int(property_values[i])
            
            building_props.updated_at = datetime.utcnow()
            updated_count += 1
        
        db.commit()
        return updated_count
        
    except Exception as e:
        db.rollback()
        print(f"Error updating building properties: {str(e)}")
        return 0


@router.post("/execute_building_analysis")
async def execute_building_analysis(
    request_data: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    Execute building analysis calculator chain.
    
    This endpoint focuses on physical building properties:
    1. scenario_geo - Initialize scenario geometry from project boundary
    2. scenario_census_boundary - Get census boundary (simplified)
    3. building_geo - Extract buildings from the area
    4. building_props - Initialize building properties
    5. building_height - Calculate building heights
    6. building_area - Calculate building footprint areas
    7. building_volume - Calculate building volumes
    8. building_n_floors - Estimate number of floors from height
    
    Input:
    - project_boundary: GeoJSON FeatureCollection or Feature with the project boundary
    - project_name: Optional project name (default: "Building_Analysis")
    - scenario_name: Optional scenario name (default: "Current_State")
    - save_to_db: Whether to save results to database (default: true)
    
    Returns:
    - Analysis results from the calculator chain
    - Database update status for each step
    """
    try:
        # Get executor and data manager with DB session
        executor, data_manager = get_pipeline_executor(db)
        
        # Extract project boundary from request
        project_boundary = request_data.get('project_boundary')
        if not project_boundary:
            raise HTTPException(status_code=400, detail="Missing project_boundary in request")
        
        # Set project and scenario names
        project_name = request_data.get('project_name', 'Building_Analysis')
        scenario_name = request_data.get('scenario_name', None)  # Can be null for baseline
        save_to_db = request_data.get('save_to_db', True)
        
        # Generate proper UUIDs (not truncated)
        project_id = str(uuid.uuid4())
        
        # If scenario_name is null/not provided, use "baseline" with same UUID as project
        if not scenario_name:
            scenario_name = 'baseline'
            scenario_id = project_id  # Same UUID for baseline scenario
        else:
            scenario_id = str(uuid.uuid4())  # Different UUID for named scenarios
        
        # Initialize the data manager context
        data_manager.set_context(
            project_id=project_id,
            scenario_id=scenario_id,
            project_name=project_name,
            scenario_name=scenario_name,
            db_session=db
        )
        
        # Prepare the scenario_geo input
        if project_boundary.get('type') == 'FeatureCollection':
            features = project_boundary.get('features', [])
            if features:
                scenario_geo_input = features[0]
            else:
                raise HTTPException(status_code=400, detail="FeatureCollection has no features")
        else:
            scenario_geo_input = project_boundary
        
        # Set the initial input data
        data_manager.set_feature('scenario_geo', scenario_geo_input)
        data_manager.set_feature('project_boundary', project_boundary)
        
        # Define the calculation chain
        calculation_chain = [
            {
                "feature_name": "scenario_geo",
                "method_name": "calculate_from_scenario_geo",
                "description": "Initialize scenario geometry from project boundary"
            },
            {
                "feature_name": "scenario_census_boundary",
                "method_name": "calculate_from_census_api",
                "description": "Get census boundary (simplified for building analysis)"
            },
            {
                "feature_name": "building_geo",
                "method_name": "calculate_from_scenario_census_geo",
                "description": "Extract buildings from the area"
            },
            {
                "feature_name": "building_props",
                "method_name": "init",
                "description": "Initialize building properties"
            },
            {
                "feature_name": "building_height",
                "method_name": "calculate_from_raster_service",
                "description": "Calculate building heights from integrated DSM/DTM rasters"
            },
            {
                "feature_name": "building_area",
                "method_name": "calculate_from_geometry",
                "description": "Calculate building footprint areas"
            },
            {
                "feature_name": "building_volume",
                "method_name": "calculate_from_height_and_area",
                "description": "Calculate building volumes"
            },
            {
                "feature_name": "building_n_floors",
                "method_name": "estimate_by_height",
                "description": "Estimate number of floors from height"
            }
        ]
        
        # Execute the calculation chain
        results = {}
        successful_calculations = []
        failed_calculations = []
        execution_chain = []
        database_updates = []
        
        print(f"DEBUG: About to execute {len(calculation_chain)} calculators")
        
        for step_num, calc_config in enumerate(calculation_chain, 1):
            feature_name = calc_config["feature_name"]
            method_name = calc_config["method_name"]
            description = calc_config["description"]
            
            print(f"\n=== Step {step_num}/{len(calculation_chain)}: {feature_name} ===")
            print(f"Method: {method_name}")
            print(f"Description: {description}")
            
            # Execute the calculator
            success = executor.execute_feature(feature_name, method_name)
            
            # Get the result
            result = data_manager.get_feature(feature_name)
            
            # Store execution info
            execution_info = {
                "step": step_num,
                "feature": feature_name,
                "method": method_name,
                "description": description,
                "status": "success" if success else "failed"
            }
            
            if not success:
                execution_info["error"] = "Unknown error"
                failed_calculations.append(feature_name)
                print(f"✗ Failed: Unknown error")
            else:
                successful_calculations.append(feature_name)
                results[feature_name] = result
                print(f"✓ Success")
                
                # Save to database if enabled
                if save_to_db and result:
                    db_update_status = {
                        "feature": feature_name,
                        "updated_records": 0,
                        "status": "pending"
                    }
                    
                    try:
                        if feature_name == "scenario_geo":
                            # Save scenario to database
                            if save_scenario_to_database(
                                db, project_id, scenario_id, 
                                project_name, scenario_name, result
                            ):
                                db_update_status["updated_records"] = 1
                                db_update_status["status"] = "success"
                                print(f"Successfully saved scenario to database")
                            else:
                                db_update_status["status"] = "failed"
                                db_update_status["error"] = "Failed to save scenario"
                                print(f"Failed to save scenario to database")
                        
                        elif feature_name == "scenario_census_boundary":
                            # For now, we don't save census boundary separately
                            # It's part of the scenario calculation
                            db_update_status["updated_records"] = 0
                            db_update_status["status"] = "success"
                            db_update_status["note"] = "Census boundary not saved separately"
                        
                        elif feature_name == "building_geo":
                            # Save all buildings to database
                            buildings = result.get('buildings', [])
                            saved_count = 0
                            for building in buildings:
                                if save_building_to_database(db, building, project_id, scenario_id):
                                    saved_count += 1
                            db_update_status["updated_records"] = saved_count
                            db_update_status["status"] = "success"
                        
                        elif feature_name == "building_props":
                            # Building properties are initialized, no separate save needed
                            db_update_status["updated_records"] = 0
                            db_update_status["status"] = "success"
                            db_update_status["note"] = "Properties initialized, will be updated by specific property calculators"
                            
                        elif feature_name == "building_height":
                            # Update building heights in database
                            if isinstance(result, list):
                                building_geo_result = results.get('building_geo', {})
                                updated = update_building_properties_in_database(
                                    db, project_id, scenario_id, 
                                    building_geo_result, 'height', result
                                )
                                db_update_status["updated_records"] = updated
                                db_update_status["status"] = "success"
                        
                        elif feature_name == "building_area":
                            # Update building areas in database
                            building_properties = result.get('building_properties', [])
                            building_areas = result.get('building_areas', [])
                            
                            # Use building_areas if building_properties is empty
                            if building_areas and not building_properties:
                                areas = building_areas
                            elif building_properties:
                                areas = [bp.get('area', 0) for bp in building_properties]
                            else:
                                areas = []
                            
                            if areas:
                                building_geo_result = results.get('building_geo', {})
                                updated = update_building_properties_in_database(
                                    db, project_id, scenario_id,
                                    building_geo_result, 'area', areas
                                )
                                db_update_status["updated_records"] = updated
                                db_update_status["status"] = "success"
                            else:
                                db_update_status["updated_records"] = 0
                                db_update_status["status"] = "success"
                                db_update_status["note"] = "No areas to update"
                        
                        elif feature_name == "building_volume":
                            # Update building volumes in database
                            volumes = result.get('building_volumes', [])
                            if volumes:
                                building_geo_result = results.get('building_geo', {})
                                updated = update_building_properties_in_database(
                                    db, project_id, scenario_id,
                                    building_geo_result, 'volume', volumes
                                )
                                db_update_status["updated_records"] = updated
                                db_update_status["status"] = "success"
                        
                        elif feature_name == "building_n_floors":
                            # Update number of floors in database
                            floors = result.get('building_floors', [])
                            if floors:
                                building_geo_result = results.get('building_geo', {})
                                updated = update_building_properties_in_database(
                                    db, project_id, scenario_id,
                                    building_geo_result, 'number_of_floors', floors
                                )
                                db_update_status["updated_records"] = updated
                                db_update_status["status"] = "success"
                        
                        database_updates.append(db_update_status)
                        
                    except Exception as e:
                        db_update_status["status"] = "failed"
                        db_update_status["error"] = str(e)
                        database_updates.append(db_update_status)
                        print(f"Database update failed for {feature_name}: {str(e)}")
                        import traceback
                        traceback.print_exc()
                else:
                    # If save_to_db is False, still add a status entry
                    if result:
                        database_updates.append({
                            "feature": feature_name,
                            "updated_records": 0,
                            "status": "skipped - save_to_db disabled"
                        })
            
            execution_chain.append(execution_info)
        
        # Get total buildings processed
        building_geo_result = results.get('building_geo', {})
        total_buildings = building_geo_result.get('total_buildings', 0)
        
        # Prepare final response
        response = {
            "project_id": project_id,
            "scenario_id": scenario_id,
            "project_name": project_name,
            "scenario_name": scenario_name,
            "execution_chain": execution_chain,
            "successful_calculations": successful_calculations,
            "failed_calculations": failed_calculations,
            "results": results,
            "database_updates": database_updates if save_to_db else [],
            "summary": {
                "total_buildings": total_buildings,
                "buildings_with_height": len(results.get('building_height', [])) if isinstance(results.get('building_height'), list) else 0,
                "buildings_with_area": len(results.get('building_area', {}).get('building_properties', [])),
                "buildings_with_volume": len(results.get('building_volume', {}).get('building_volumes', [])),
                "buildings_with_floors": len(results.get('building_n_floors', {}).get('building_floors', []))
            },
            "metadata": {
                "total_steps": len(calculation_chain),
                "successful_steps": len(successful_calculations),
                "failed_steps": len(failed_calculations),
                "success_rate": f"{(len(successful_calculations) / len(calculation_chain) * 100):.1f}%",
                "database_updates_enabled": save_to_db,
                "pipeline_version": "1.0.0"
            }
        }
        
        print(f"\n=== Pipeline Execution Complete ===")
        print(f"Success Rate: {response['metadata']['success_rate']}")
        print(f"Total Buildings: {total_buildings}")
        if save_to_db:
            print(f"Database Updates: {len([u for u in database_updates if u.get('status') == 'success'])} successful")
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
