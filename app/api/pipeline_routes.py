"""
Pipeline Routes - All services from datalake8 with integrated database access
FastAPI implementation for CIM Wizard Integrated
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import json

from app.db.database import get_db
from app.models.vector import ProjectScenario, Building, BuildingProperties
from app.core.data_manager import CimWizardDataManager
from app.core.pipeline_executor import CimWizardPipelineExecutor
# Removed Pydantic schemas for simplicity - using dict instead


router = APIRouter()


# Initialize data manager and pipeline executor
# These will be created per request with database session
def get_pipeline_executor(db: Session):
    """Create pipeline executor with database session"""
    data_manager = CimWizardDataManager(db_session=db)
    executor = CimWizardPipelineExecutor(data_manager)
    return executor, data_manager


@router.post("/execute")
async def execute_pipeline(
    request_data: dict,
    db: Session = Depends(get_db)
):
    """Execute a pipeline to calculate multiple features"""
    try:
        # Get executor and data manager with DB session
        executor, data_manager = get_pipeline_executor(db)
        
        # Possible errors to handle later:
        # - Missing project_id, scenario_id, features
        # - Invalid feature names
        # - Database connection issues
        # - Calculator execution failures
        
        project_id = request_data.get('project_id')
        scenario_id = request_data.get('scenario_id')
        building_id = request_data.get('building_id')
        features = request_data.get('features', [])
        parallel = request_data.get('parallel', False)
        input_data = request_data.get('input_data')
        
        if not project_id:
            return {"error": "Missing project_id"}
        if not scenario_id:
            return {"error": "Missing scenario_id"}
        if not features:
            return {"error": "Missing features list"}
        
        # Set context from request
        data_manager.set_context(
            project_id=project_id,
            scenario_id=scenario_id,
            building_id=building_id,
            db_session=db  # Pass DB session to context
        )
        
        # Set any additional input data
        if input_data:
            data_manager.set_context(**input_data)
        
        # Execute pipeline
        result = executor.execute_pipeline(
            features,
            parallel=parallel
        )
        
        # Add calculated feature values to result
        result['results'] = {}
        for feature in result['executed_features']:
            result['results'][feature] = data_manager.get_feature(feature)
        
        # Save results to database if successful
        if result['success']:
            # This would update BuildingProperties or other tables
            # Implementation depends on specific requirements
            pass
        
        return result
        
    except Exception as e:
        # Possible errors: Invalid features, calculation errors
        raise HTTPException(status_code=500, detail=f"Pipeline execution error: {str(e)}")


@router.post("/execute_explicit")
async def execute_explicit_pipeline(
    request_data: dict,
    db: Session = Depends(get_db)
):
    """Execute pipeline with explicit feature.method specifications"""
    try:
        # Get executor and data manager with DB session
        executor, data_manager = get_pipeline_executor(db)
        
        # Possible errors to handle later:
        # - Missing execution_plan
        # - Invalid execution plan format
        # - Method not found
        
        execution_plan = request_data.get('execution_plan', [])
        project_id = request_data.get('project_id')
        scenario_id = request_data.get('scenario_id')
        building_id = request_data.get('building_id')
        input_data = request_data.get('input_data')
        
        if not execution_plan:
            return {"error": "Missing execution_plan"}
        
        # Set context from request
        data_manager.set_context(
            project_id=project_id,
            scenario_id=scenario_id,
            building_id=building_id,
            db_session=db
        )
        
        # Set any additional input data
        if input_data:
            data_manager.set_context(**input_data)
        
        # Execute explicit pipeline
        result = executor.execute_explicit_pipeline(
            execution_plan
        )
        
        return result
        
    except Exception as e:
        # Possible errors: Invalid execution plan, method not found
        raise HTTPException(status_code=500, detail=f"Pipeline execution error: {str(e)}")


@router.post("/execute_predefined")
async def execute_predefined_pipeline(
    request_data: dict,
    db: Session = Depends(get_db)
):
    """Execute a predefined pipeline from configuration"""
    try:
        # Get executor and data manager with DB session
        executor, data_manager = get_pipeline_executor(db)
        
        # Possible errors to handle later:
        # - Missing pipeline_name
        # - Pipeline not found in configuration
        # - Execution errors
        
        pipeline_name = request_data.get('pipeline_name')
        project_id = request_data.get('project_id')
        scenario_id = request_data.get('scenario_id')
        building_id = request_data.get('building_id')
        input_data = request_data.get('input_data', {})
        
        if not pipeline_name:
            return {"error": "Missing pipeline_name"}
        
        # Set context from request
        data_manager.set_context(
            project_id=project_id,
            scenario_id=scenario_id,
            building_id=building_id,
            db_session=db
        )
        
        # Execute predefined pipeline
        result = executor.execute_predefined_pipeline(
            pipeline_name,
            **input_data
        )
        
        return result
        
    except Exception as e:
        # Possible errors: Pipeline not found, execution errors
        raise HTTPException(status_code=500, detail=f"Pipeline execution error: {str(e)}")


@router.post("/calculate_feature")
async def calculate_feature(
    request_data: dict,
    db: Session = Depends(get_db)
):
    """Calculate a single feature"""
    try:
        # Get executor and data manager with DB session
        executor, data_manager = get_pipeline_executor(db)
        
        # Possible errors to handle later:
        # - Missing feature_name
        # - Feature not found in configuration
        # - Method not found
        # - Calculation errors
        
        feature_name = request_data.get('feature_name')
        method_name = request_data.get('method_name')
        project_id = request_data.get('project_id')
        scenario_id = request_data.get('scenario_id')
        building_id = request_data.get('building_id')
        input_data = request_data.get('input_data')
        
        if not feature_name:
            return {"error": "Missing feature_name"}
        
        # Set context from request
        data_manager.set_context(
            project_id=project_id,
            scenario_id=scenario_id,
            building_id=building_id,
            db_session=db
        )
        
        # Set any additional input data
        if input_data:
            data_manager.set_context(**input_data)
        
        # Execute single feature
        success = executor.execute_feature(
            feature_name,
            method_name
        )
        
        if success:
            value = data_manager.get_feature(feature_name)
            execution_info = executor.execution_results.get(feature_name, {})
            method_used = execution_info.get('method', None)
            
            return {
                "success": True,
                "feature_name": feature_name,
                "value": value,
                "method_used": method_used
            }
        else:
            execution_info = executor.execution_results.get(feature_name, {})
            error = execution_info.get('error', 'Unknown error')
            
            return {
                "success": False,
                "feature_name": feature_name,
                "value": None,
                "method_used": None,
                "error": error
            }
            
    except Exception as e:
        # Possible errors: Feature not found, calculation errors
        raise HTTPException(status_code=500, detail=f"Feature calculation error: {str(e)}")


@router.get("/configuration")
async def get_configuration(db: Session = Depends(get_db)):
    """Get the current pipeline configuration"""
    try:
        data_manager = CimWizardDataManager(db_session=db)
        return data_manager.configuration
    except Exception as e:
        # Possible errors: Configuration file not found
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")


@router.get("/available_features")
async def get_available_features(db: Session = Depends(get_db)):
    """Get list of available features from configuration"""
    try:
        data_manager = CimWizardDataManager(db_session=db)
        if data_manager.configuration and 'features' in data_manager.configuration:
            return {
                "features": list(data_manager.configuration['features'].keys()),
                "services": {
                    "census": "integrated",
                    "raster": "integrated"
                }
            }
        return {"features": [], "services": {}}
    except Exception as e:
        # Possible errors: Configuration file issues
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")


@router.get("/predefined_pipelines")
async def get_predefined_pipelines(db: Session = Depends(get_db)):
    """Get list of predefined pipelines"""
    try:
        data_manager = CimWizardDataManager(db_session=db)
        if data_manager.configuration and 'predefined_pipelines' in data_manager.configuration:
            pipelines = data_manager.configuration['predefined_pipelines']
            return {
                "pipelines": [
                    {
                        "name": name,
                        "description": config.get('description', ''),
                        "features": config.get('features', []),
                        "required_inputs": config.get('required_inputs', [])
                    }
                    for name, config in pipelines.items()
                ]
            }
        return {"pipelines": []}
    except Exception as e:
        # Possible errors: Configuration file issues
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")


@router.get("/feature_methods/{feature_name}")
async def get_feature_methods(
    feature_name: str,
    db: Session = Depends(get_db)
):
    """Get available methods for a specific feature"""
    try:
        data_manager = CimWizardDataManager(db_session=db)
        feature_config = data_manager.get_feature_config(feature_name)
        if not feature_config:
            raise HTTPException(status_code=404, detail=f"Feature {feature_name} not found")
        
        methods = feature_config.get('methods', [])
        return {
            "feature": feature_name,
            "methods": [
                {
                    "name": m['method_name'],
                    "priority": m.get('priority', 999),
                    "dependencies": m.get('input_dependencies', [])
                }
                for m in methods
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        # Possible errors: Configuration issues
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")


@router.post("/load_scenario_geo")
async def load_scenario_geo(
    project_id: str = Body(...),
    scenario_id: str = Body(...),
    scenario_geo: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """Load scenario geometry data"""
    try:
        # Get executor and data manager with DB session
        executor, data_manager = get_pipeline_executor(db)
        
        # Set context
        data_manager.set_context(
            project_id=project_id,
            scenario_id=scenario_id,
            scenario_geo_data=scenario_geo,
            db_session=db
        )
        
        # Execute milestone1_scenario pipeline to initialize data
        result = executor.execute_predefined_pipeline(
            "milestone1_scenario",
            scenario_geo=scenario_geo
        )
        
        return result
        
    except Exception as e:
        # Possible errors: Invalid geometry, pipeline execution errors
        raise HTTPException(status_code=500, detail=f"Data loading error: {str(e)}")


@router.post("/load_building_geo")
async def load_building_geo(
    project_id: str = Body(...),
    scenario_id: str = Body(...),
    building_geo: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """Load building geometry data"""
    try:
        # Get executor and data manager with DB session
        executor, data_manager = get_pipeline_executor(db)
        
        # Set context
        data_manager.set_context(
            project_id=project_id,
            scenario_id=scenario_id,
            building_geo_data=building_geo,
            db_session=db
        )
        
        # Execute milestone1_building pipeline to initialize data
        result = executor.execute_predefined_pipeline(
            "milestone1_building",
            building_geo=building_geo
        )
        
        return result
        
    except Exception as e:
        # Possible errors: Invalid geometry, pipeline execution errors
        raise HTTPException(status_code=500, detail=f"Data loading error: {str(e)}")


@router.get("/execution_summary")
async def get_execution_summary(db: Session = Depends(get_db)):
    """Get summary of pipeline executions in current session"""
    try:
        # Note: This would need session management to track executions
        return {
            "message": "Execution summary requires session management",
            "tip": "Each request creates a new executor instance"
        }
    except Exception as e:
        # Possible errors: Session management issues
        raise HTTPException(status_code=500, detail=f"Summary error: {str(e)}")


@router.get("/health")
async def pipeline_health():
    """Health check for pipeline execution routes"""
    return {
        "status": "healthy",
        "service": "pipeline_executor",
        "database_integration": "active"
    }


def _parse_chain_spec(chain_spec: str) -> List[Dict[str, str]]:
    """
    Parse chain specification string into execution plan
    
    Args:
        chain_spec: String like "scenario_geo.calculate_from_scenario_id|building_height.calculate_default_estimate"
    
    Returns:
        List of execution steps with feature_name and method_name
    """
    execution_plan = []
    
    # Split by pipe separator
    steps = chain_spec.split('|')
    
    for step in steps:
        step = step.strip()
        if '.' in step:
            feature_name, method_name = step.split('.', 1)
            execution_plan.append({
                'feature_name': feature_name.strip(),
                'method_name': method_name.strip()
            })
        else:
            # If no method specified, use default
            execution_plan.append({
                'feature_name': step.strip(),
                'method_name': 'calculate'
            })
    
    return execution_plan


@router.post("/chainable")
async def chainable_pipeline(
    request_data: dict,
    db: Session = Depends(get_db)
):
    """
    Chainable Pipeline Endpoint
    
    POST /api/pipeline/chainable
    Body: {
        "chain": "scenario_geo.calculate_from_scenario_id|building_height.calculate_default_estimate",
        "inputs": {
            "scenario_id": "123",
            "building_geo": {...}
        }
    }
    """
    try:
        chain_spec = request_data.get('chain')
        chain_inputs = request_data.get('inputs', {})
        
        if not chain_spec:
            raise HTTPException(
                status_code=400,
                detail={
                    'success': False,
                    'error': 'Missing required parameter: chain',
                    'usage': 'Specify chain of feature.method calls separated by |'
                }
            )
        
        # Get executor and data manager with DB session
        executor, data_manager = get_pipeline_executor(db)
        
        # Set context from inputs
        project_id = chain_inputs.get('project_id')
        scenario_id = chain_inputs.get('scenario_id')
        building_id = chain_inputs.get('building_id')
        
        data_manager.set_context(
            project_id=project_id,
            scenario_id=scenario_id,
            building_id=building_id,
            db_session=db
        )
        
        # Set any additional input data
        for key, value in chain_inputs.items():
            if key not in ['project_id', 'scenario_id', 'building_id']:
                data_manager.set_context(**{key: value})
        
        # Parse and execute chain
        execution_plan = _parse_chain_spec(chain_spec)
        result = executor.execute_explicit_pipeline(execution_plan)
        
        # Add chain information to result
        result['chain'] = chain_spec
        result['success'] = result.get('success', True)
        
        # Get available context data
        context_data = {
            'project_id': data_manager.project_id,
            'scenario_id': data_manager.scenario_id,
            'building_id': data_manager.building_id,
            'available_features': data_manager.get_available_features()
        }
        
        return {
            'success': True,
            'chain': chain_spec,
            'result': result,
            'context': context_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                'success': False,
                'error': f'Failed to execute chain: {str(e)}'
            }
        )


@router.post("/execute_complete_chain")
async def execute_sansa_complete_chain(
    request_data: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    Execute complete calculator chain for Sansa project boundary.
    
    CRITICAL ORDER:
    1. scenario_geo → Initialize from boundary
    2. scenario_census_boundary → Get census zones FIRST (for population calculation)
    3. building_geo → Extract ALL buildings from census zones (not just project boundary)
    4. Then all other calculators in sequence
    
    IMPORTANT: Population calculation needs ALL buildings in census zones,
    but we only save buildings inside project boundary.
    
    Input:
    - project_boundary: GeoJSON FeatureCollection or Feature with the project boundary
    - project_name: Optional project name (default: "Sansa_Project")
    - scenario_name: Optional scenario name (default: "Current_State")
    
    Returns:
    - Complete analysis results from all calculators in sequence
    """
    try:
        # Import all calculators dynamically
        import importlib
        import os
        from pathlib import Path
        import uuid
        
        # Get executor and data manager with DB session
        executor, data_manager = get_pipeline_executor(db)
        
        # Dynamically import all calculators from calculators folder
        calculators_dir = Path(__file__).parent.parent / 'calculators'
        calculator_modules = {}
        
        for file in calculators_dir.glob('*_calculator.py'):
            if file.name != '__init__.py':
                module_name = file.stem
                try:
                    module = importlib.import_module(f'app.calculators.{module_name}')
                    # Get the calculator class (assumes class name follows convention)
                    class_name = ''.join(word.capitalize() for word in module_name.split('_'))
                    if hasattr(module, class_name):
                        calculator_modules[module_name] = getattr(module, class_name)
                        print(f"Imported calculator: {class_name}")
                except Exception as e:
                    print(f"Failed to import {module_name}: {str(e)}")
        
        # Extract project boundary from request
        project_boundary = request_data.get('project_boundary')
        if not project_boundary:
            raise HTTPException(status_code=400, detail="Missing project_boundary in request")
        
        # Set project and scenario names
        project_name = request_data.get('project_name', 'Sansa_Project')
        scenario_name = request_data.get('scenario_name', 'Current_State')
        
        # Generate unique IDs
        import uuid
        project_id = f"project_{uuid.uuid4().hex[:8]}"
        scenario_id = f"scenario_{uuid.uuid4().hex[:8]}"
        
        # Initialize the data manager context with all required data
        data_manager.set_context(
            project_id=project_id,
            scenario_id=scenario_id,
            project_name=project_name,
            scenario_name=scenario_name,
            db_session=db,
            # Service URLs for integrated system
            raster_service_url="http://localhost:8000/api/raster",
            census_service_url="http://localhost:8000/api/census"
        )
        
        # Prepare the scenario_geo input (expected by ScenarioGeoCalculator)
        if project_boundary.get('type') == 'FeatureCollection':
            # Use the first feature if it's a FeatureCollection
            features = project_boundary.get('features', [])
            if features:
                scenario_geo_input = features[0]
            else:
                raise HTTPException(status_code=400, detail="FeatureCollection has no features")
        else:
            # Assume it's already a Feature
            scenario_geo_input = project_boundary
        
        # Set the scenario_geo as input data
        data_manager.set_feature('scenario_geo', scenario_geo_input)
        data_manager.set_feature('project_boundary', project_boundary)
        
        # Define the complete calculation chain in order
        # Each calculator depends on the results of previous ones
        calculation_chain = [
            # === MILESTONE 1: Initialize basic data ===
            {
                "feature_name": "scenario_geo",
                "method_name": "calculate_from_scenario_geo",
                "description": "Initialize scenario geometry from project boundary"
            },
            {
                "feature_name": "building_geo",
                "method_name": "calculate_from_scenario_census_geo",
                "description": "Extract building geometries from OSM"
            },
            {
                "feature_name": "building_props",
                "method_name": "init",
                "description": "Initialize building properties"
            },
            
            # === MILESTONE 2: Calculate physical attributes ===
            {
                "feature_name": "building_height",
                "method_name": "calculate_from_raster_service",
                "description": "Calculate building heights from DSM/DTM rasters"
            },
            {
                "feature_name": "building_area",
                "method_name": "calculate_from_geometry",
                "description": "Calculate building footprint areas"
            },
            {
                "feature_name": "scenario_census_boundary",
                "method_name": "calculate_from_census_api",
                "description": "Get census boundary for the scenario"
            },
            
            # === MILESTONE 3: Calculate derived attributes ===
            {
                "feature_name": "building_volume",
                "method_name": "calculate_from_height_and_area",
                "description": "Calculate building volumes"
            },
            {
                "feature_name": "building_n_floors",
                "method_name": "estimate_by_height",
                "description": "Estimate number of floors from height"
            },
            
            # === MILESTONE 4: Calculate demographics ===
            {
                "feature_name": "census_population",
                "method_name": "calculate_from_census_boundary",
                "description": "Get total population from census"
            },
            {
                "feature_name": "building_type",
                "method_name": "by_census_osm",
                "description": "Determine building types"
            },
            {
                "feature_name": "building_population",
                "method_name": "calculate_from_volume_distribution",
                "description": "Distribute population to buildings"
            },
            {
                "feature_name": "building_n_families",
                "method_name": "calculate_from_population",
                "description": "Calculate number of families per building"
            },
            
            # === MILESTONE 5: Additional attributes ===
            {
                "feature_name": "building_construction_year",
                "method_name": "by_census_osm",
                "description": "Estimate construction years"
            },
            {
                "feature_name": "building_demographic",
                "method_name": "by_census_osm",
                "description": "Calculate demographic details"
            },
            {
                "feature_name": "building_geo_lod12",
                "method_name": "by_footprint_height",
                "description": "Generate LOD1/LOD2 3D geometries"
            }
        ]
        
        # Track execution results
        execution_results = {
            "project_id": project_id,
            "scenario_id": scenario_id,
            "project_name": project_name,
            "scenario_name": scenario_name,
            "execution_chain": [],
            "successful_calculations": [],
            "failed_calculations": [],
            "results": {},
            "summary": {}
        }
        
        # Execute each step in the chain
        for step in calculation_chain:
            feature_name = step["feature_name"]
            method_name = step["method_name"]
            description = step["description"]
            
            print(f"\n=== Executing: {feature_name} - {description} ===")
            
            try:
                # Execute the feature calculation
                success = executor.execute_feature(feature_name, method_name)
                
                if success:
                    # Get the calculated value
                    value = data_manager.get_feature(feature_name)
                    
                    execution_results["successful_calculations"].append(feature_name)
                    execution_results["results"][feature_name] = value
                    execution_results["execution_chain"].append({
                        "feature": feature_name,
                        "method": method_name,
                        "description": description,
                        "status": "success",
                        "value_type": type(value).__name__ if value is not None else "None"
                    })
                    
                    print(f"✓ Successfully calculated {feature_name}")
                else:
                    execution_results["failed_calculations"].append(feature_name)
                    execution_results["execution_chain"].append({
                        "feature": feature_name,
                        "method": method_name,
                        "description": description,
                        "status": "failed",
                        "error": executor.execution_results.get(feature_name, {}).get('error', 'Unknown error')
                    })
                    
                    print(f"✗ Failed to calculate {feature_name}")
                    
            except Exception as e:
                execution_results["failed_calculations"].append(feature_name)
                execution_results["execution_chain"].append({
                    "feature": feature_name,
                    "method": method_name,
                    "description": description,
                    "status": "error",
                    "error": str(e)
                })
                print(f"✗ Error calculating {feature_name}: {str(e)}")
        
        # Generate summary statistics
        building_geo = data_manager.get_feature('building_geo')
        building_heights = data_manager.get_feature('building_height')
        building_areas = data_manager.get_feature('building_area')
        building_volumes = data_manager.get_feature('building_volume')
        building_populations = data_manager.get_feature('building_population')
        census_population = data_manager.get_feature('census_population')
        
        # Calculate summary based on available data
        summary = {
            "total_features_requested": len(calculation_chain),
            "successful_calculations": len(execution_results["successful_calculations"]),
            "failed_calculations": len(execution_results["failed_calculations"]),
            "success_rate": f"{(len(execution_results['successful_calculations']) / len(calculation_chain) * 100):.1f}%"
        }
        
        # Add building statistics if available
        if building_geo and isinstance(building_geo, dict):
            features = building_geo.get('features', [])
            summary["total_buildings"] = len(features)
        
        if building_heights and isinstance(building_heights, (list, dict)):
            if isinstance(building_heights, list):
                summary["average_height_m"] = sum(building_heights) / len(building_heights) if building_heights else 0
                summary["max_height_m"] = max(building_heights) if building_heights else 0
                summary["min_height_m"] = min(building_heights) if building_heights else 0
        
        if building_areas and isinstance(building_areas, (list, dict)):
            if isinstance(building_areas, list):
                summary["total_area_m2"] = sum(building_areas)
                summary["average_area_m2"] = sum(building_areas) / len(building_areas) if building_areas else 0
        
        if building_volumes and isinstance(building_volumes, (list, dict)):
            if isinstance(building_volumes, list):
                summary["total_volume_m3"] = sum(building_volumes)
                summary["average_volume_m3"] = sum(building_volumes) / len(building_volumes) if building_volumes else 0
        
        if census_population:
            summary["total_census_population"] = census_population
        
        if building_populations and isinstance(building_populations, (list, dict)):
            if isinstance(building_populations, list):
                summary["total_distributed_population"] = sum(building_populations)
                summary["average_population_per_building"] = sum(building_populations) / len(building_populations) if building_populations else 0
        
        execution_results["summary"] = summary
        
        # Add execution metadata
        execution_results["metadata"] = {
            "execution_time": "async",
            "pipeline_version": "2.0.0",
            "data_sources": ["OSM", "Census", "Raster Services"],
            "coordinate_system": project_boundary.get('crs', {}).get('properties', {}).get('name', 'Unknown')
        }
        
        return execution_results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Complete chain execution error: {str(e)}")