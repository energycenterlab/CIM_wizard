"""
BaseCalculator - Abstract base class for all CIM Wizard pipeline calculators.

Every calculator inherits from this class to get:
- pipeline executor and data manager references
- convenience wrappers for logging, validation, feature access
- project_id / scenario_id properties
- save_to_db helper that delegates to DataManager

Subclasses only need to call  super().__init__(pipeline_executor)  and then
implement their domain-specific calculation methods.  Direct database access
(db.query, db.commit, ...) should NOT appear in calculators; all persistence
goes through DataManager.
"""

from typing import Any, Dict, List, Optional


class BaseCalculator:
    """Base class that all pipeline calculators inherit from."""

    def __init__(self, pipeline_executor):
        self.pipeline = pipeline_executor
        self.data_manager = pipeline_executor.data_manager
        self.calculator_name: str = self.__class__.__name__

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def log_info(self, message: str):
        self.pipeline.log_info(self.calculator_name, message)

    def log_error(self, message: str):
        self.pipeline.log_error(self.calculator_name, message)

    def log_warning(self, message: str):
        self.pipeline.log_warning(self.calculator_name, message)

    def log_debug(self, message: str):
        self.pipeline.log_debug(self.calculator_name, message)

    def log_success(self, method_name: str, result: Any, info: str = ""):
        self.pipeline.log_calculation_success(
            self.calculator_name, method_name, result, info
        )

    def log_failure(self, method_name: str, error: str):
        self.pipeline.log_calculation_failure(
            self.calculator_name, method_name, error
        )

    # ------------------------------------------------------------------
    # Feature access
    # ------------------------------------------------------------------

    def get_feature(self, feature_name: str) -> Any:
        """Safely retrieve a calculated feature from the data manager."""
        return self.pipeline.get_feature_safely(
            feature_name, calculator_name=self.calculator_name
        )

    def set_feature(self, feature_name: str, value: Any):
        """Store a calculated feature in the data manager."""
        self.data_manager.set_feature(feature_name, value)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_input(self, value: Any, name: str) -> bool:
        return self.pipeline.validate_input(value, name, self.calculator_name)

    def validate_dict(
        self, value: Any, name: str, required_keys: List[str] = None
    ) -> bool:
        return self.pipeline.validate_dict(
            value, name, self.calculator_name, required_keys
        )

    def validate_geometry(self, value: Any, name: str) -> bool:
        return self.pipeline.validate_geometry(value, name, self.calculator_name)

    def validate_numeric(
        self,
        value: Any,
        name: str,
        min_val: float = None,
        max_val: float = None,
    ) -> bool:
        return self.pipeline.validate_numeric(
            value, name, self.calculator_name, min_val=min_val, max_val=max_val
        )

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def project_id(self) -> Optional[str]:
        return getattr(self.data_manager, "project_id", None)

    @property
    def scenario_id(self) -> Optional[str]:
        return getattr(self.data_manager, "scenario_id", None)

    # ------------------------------------------------------------------
    # Database persistence (via DataManager)
    # ------------------------------------------------------------------

    def save_property_batch(
        self,
        buildings: List[Dict[str, Any]],
        property_name: str,
        values: List[Any],
        project_id: str = None,
        scenario_id: str = None,
    ) -> int:
        """
        Convenience wrapper around DataManager.upsert_building_properties_batch.

        Calculators should call this instead of touching the DB session
        directly.
        """
        pid = project_id or self.project_id
        sid = scenario_id or self.scenario_id
        if not pid or not sid:
            self.log_warning("Cannot save to DB: missing project_id or scenario_id")
            return 0
        return self.data_manager.upsert_building_properties_batch(
            buildings, pid, sid, property_name, values,
        )
