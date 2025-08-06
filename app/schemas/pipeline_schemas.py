"""
Pydantic schemas for Pipeline execution
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class PipelineRequest(BaseModel):
    project_id: str
    scenario_id: str
    building_id: Optional[str] = None
    features: List[str]
    parallel: bool = False
    input_data: Optional[Dict[str, Any]] = None


class ExplicitPipelineRequest(BaseModel):
    project_id: str
    scenario_id: str
    building_id: Optional[str] = None
    execution_plan: List[Dict[str, str]]  # [{'feature_name': 'xxx', 'method_name': 'yyy'}]
    input_data: Optional[Dict[str, Any]] = None


class PredefinedPipelineRequest(BaseModel):
    project_id: str
    scenario_id: str
    building_id: Optional[str] = None
    pipeline_name: str
    input_data: Optional[Dict[str, Any]] = None


class PipelineResponse(BaseModel):
    success: bool
    requested_features: Optional[List[str]] = None
    executed_features: List[str]
    failed_features: List[str]
    execution_order: Optional[List[str]] = None
    results: Dict[str, Any]
    error: Optional[str] = None
    pipeline_name: Optional[str] = None
    pipeline_description: Optional[str] = None


class FeatureCalculationRequest(BaseModel):
    project_id: str
    scenario_id: str
    building_id: Optional[str] = None
    feature_name: str
    method_name: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None


class FeatureCalculationResponse(BaseModel):
    success: bool
    feature_name: str
    value: Optional[Any] = None
    method_used: Optional[str] = None
    error: Optional[str] = None