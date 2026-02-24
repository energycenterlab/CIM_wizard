"""
CIM Wizard Views - Two-Class Approach
=====================================

Using:
- CimWizardDataManager: Context + Configuration + Database sync
- CimWizardPipelineExecutor: Pipeline orchestration + Feature execution

Endpoints accept chain of calculators separated by | (e.g. feature1.method1|feature2.method2)
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, Body

from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.data_manager import CimWizardDataManager
from app.core.pipeline_executor import CimWizardPipelineExecutor


router = APIRouter()


def create_executor(
    db: Session = None,
    inputs: Dict[str, Any] = None
) -> tuple:
    """Factory function to create data manager and executor"""
    data_manager = CimWizardDataManager(db_session=db)
    executor = CimWizardPipelineExecutor(data_manager)

    if inputs:
        data_manager.set_inputs_from_request(inputs)
        data_manager.load_from_database()

    return data_manager, executor


def _parse_chain_spec(chain_spec: str) -> List[Dict[str, str]]:
    """
    Parse chain specification string into execution plan.

    Args:
        chain_spec: String like "scenario_geo.calculate_from_scenario_id|building_height.calculate_default_estimate"

    Returns:
        List of execution steps with feature_name and method_name
    """
    execution_plan = []
    steps = chain_spec.split("|")

    for step in steps:
        step = step.strip()
        if "." in step:
            feature_name, method_name = step.split(".", 1)
            execution_plan.append({
                "feature_name": feature_name.strip(),
                "method_name": method_name.strip()
            })
        else:
            execution_plan.append({
                "feature_name": step.strip(),
                "method_name": "calculate"
            })

    return execution_plan


# ---------------------------------------------------------------------------
# Single Feature Calculator
# ---------------------------------------------------------------------------

@router.post("/calculate")
async def single_feature_calculator_post(
    request_data: Dict[str, Any] = Body(default={}),
    db: Session = Depends(get_db)
):
    """
    Single Feature Calculator (POST)

    Body: {
        "feature_name": "building_geo",
        "building_geo": { "type": "FeatureCollection", "features": [...] }
    }
    """
    return await _single_feature_calculator_impl(
        feature_name=request_data.get("feature_name"),
        inputs=request_data,
        db=db
    )


@router.get("/calculate")
async def single_feature_calculator_get(
    feature_name: str = Query(..., alias="feature_name"),
    db: Session = Depends(get_db)
):
    """
    Single Feature Calculator (GET)

    GET /cim-wizard/calculate/?feature_name=<name>
    Uses context from database if project_id/scenario_id are in session.
    """
    return await _single_feature_calculator_impl(
        feature_name=feature_name,
        inputs={},
        db=db
    )


async def _single_feature_calculator_impl(
    feature_name: str,
    inputs: Dict[str, Any],
    db: Session
):
    """Shared implementation for single feature calculation"""
    try:
        fn = feature_name

        if not fn:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "Missing feature_name parameter",
                    "required_inputs": ["feature_name"]
                }
            )

        data_manager, executor = create_executor(db=db, inputs=inputs)
        success = executor.execute_feature(fn)

        if success:
            value = data_manager.get_feature(fn)
            execution_info = executor.execution_results.get(fn, {})
            method_used = execution_info.get("method")

            return {
                "success": True,
                "feature_name": fn,
                "value": value,
                "method_used": method_used
            }
        else:
            execution_info = executor.execution_results.get(fn, {})
            error = execution_info.get("error", "Unknown error")
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "error": f"Failed to calculate feature {fn}: {error}"
                }
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": f"Failed to calculate feature: {str(e)}"
            }
        )


# ---------------------------------------------------------------------------
# Chainable Pipeline (chain of calculators separated by |)
# ---------------------------------------------------------------------------

@router.post("/chainable")
async def chainable_pipeline(
    request_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Chainable Pipeline Endpoint

    POST /cim-wizard/chainable
    Body: {
        "chain": "scenario_geo.calculate_from_scenario_id|building_height.calculate_default_estimate",
        "inputs": {
            "scenario_id": "123",
            "building_geo": {...}
        }
    }
    """
    chain_spec = request_data.get("chain")
    chain_inputs = request_data.get("inputs", {})

    if not chain_spec:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "Missing required parameter: chain",
                "usage": "Specify chain of feature.method calls separated by |"
            }
        )

    try:
        data_manager, executor = create_executor(db=db, inputs=chain_inputs)
        chain = _parse_chain_spec(chain_spec)
        result = executor.execute_explicit_pipeline(chain)

        return {
            "success": True,
            "chain": chain_spec,
            "result": result,
            "context": data_manager.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": f"Failed to execute chain: {str(e)}"
            }
        )


# ---------------------------------------------------------------------------
# Runtime Priority Override
# ---------------------------------------------------------------------------

@router.post("/priority-override")
async def priority_override(
    request_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Runtime Priority Override Endpoint

    POST /cim-wizard/priority-override
    Body: {
        "scenario_id": "123",
        "feature": "building_height",
        "priorities": {
            "calculate_default_estimate": 1,
            "calculate_from_osm_height": 2,
            "calculate_from_raster_service": 3
        },
        "execute": true
    }
    """
    feature = request_data.get("feature")
    priorities = request_data.get("priorities")
    execute = request_data.get("execute", False)

    if not feature or not priorities:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "Missing required parameters",
                "required": ["feature", "priorities"],
                "usage": "Set priority override for a feature and optionally execute it"
            }
        )

    try:
        inputs = {k: v for k, v in request_data.items() if k not in ("feature", "priorities", "execute")}
        data_manager, executor = create_executor(db=db, inputs=inputs)
        data_manager.set_method_priority(feature, priorities)

        response = {
            "success": True,
            "feature": feature,
            "priority_override_set": priorities
        }

        if execute:
            success = executor.execute_feature(feature)
            if success:
                response["execution_result"] = {
                    "success": True,
                    "value": data_manager.get_feature(feature),
                    "method_used": executor.execution_results.get(feature, {}).get("method")
                }
            else:
                response["execution_result"] = {
                    "success": False,
                    "error": executor.execution_results.get(feature, {}).get("error", "Unknown error")
                }

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": f"Failed to set priority override: {str(e)}"
            }
        )


# ---------------------------------------------------------------------------
# List Features and Pipelines
# ---------------------------------------------------------------------------

@router.get("/list")
async def list_features(db: Session = Depends(get_db)):
    """List all available features and pipelines"""
    try:
        data_manager = CimWizardDataManager(db_session=db)

        return {
            "success": True,
            "available_features": data_manager.get_configured_features(),
            "available_pipelines": data_manager.get_available_pipelines(),
            "endpoints": {
                "single_feature": "/cim-wizard/calculate/?feature_name=<n>",
                "milestone1_scenario": "/cim-wizard/milestone1/scenario/",
                "milestone1_building": "/cim-wizard/milestone1/building/",
                "milestone2": "/cim-wizard/milestone2/",
                "milestone3": "/cim-wizard/milestone3/",
                "milestone4_demographic": "/cim-wizard/milestone4/demographic/",
                "chainable_pipeline": "/cim-wizard/chainable/",
                "priority_override": "/cim-wizard/priority-override/",
                "buildings_geojson": "/cim-wizard/buildings/?project_id=<project>&scenario_id=<scenario>&lod=<lod>"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": f"Failed to list features: {str(e)}"
            }
        )
