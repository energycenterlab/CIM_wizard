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
def get_pipeline_executor(db: Session = Depends(get_db)):
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