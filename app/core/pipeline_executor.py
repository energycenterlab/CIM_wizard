"""
CIM Wizard Pipeline Executor
FastAPI version - maintains object-oriented architecture from datalake8
Handles pipeline orchestration, feature execution, and calculator management
"""

import importlib
from typing import Dict, Any, List, Set, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
from app.core.data_manager import CimWizardDataManager, FeatureMethodSelector


class CimWizardPipelineExecutor:
    """
    CIM Wizard Pipeline Executor
    
    Responsibilities:
    1. Pipeline orchestration and execution
    2. Feature execution with fallback system  
    3. Method selection (explicit vs fallback)
    4. Dependency resolution
    5. Calculator instance management with caching
    """
    
    def __init__(self, data_manager: CimWizardDataManager):
        self.data_manager = data_manager
        self.calculator_cache = {}  # Cache calculator instances
        self.execution_results = {}  # Store execution results
    
    # === LOGGING SERVICES ===
    
    def log_info(self, calculator_name: str, message: str):
        """Log info message"""
        print(f"INFO {calculator_name}: {message}")
    
    def log_error(self, calculator_name: str, message: str):
        """Log error message"""
        print(f"ERROR {calculator_name}: {message}")
    
    def log_warning(self, calculator_name: str, message: str):
        """Log warning message"""
        print(f"WARNING {calculator_name}: {message}")
    
    def log_debug(self, calculator_name: str, message: str):
        """Log debug message"""
        print(f"DEBUG {calculator_name}: {message}")
    
    def log_calculation_failure(self, calculator_name: str, method_name: str, error_message: str):
        """Log calculation failure with method and error details"""
        print(f"ERROR {calculator_name}.{method_name}: {error_message}")
    
    def log_calculation_success(self, calculator_name: str, method_name: str, result: Any, additional_info: str = ""):
        """Log calculation success with method and result details"""
        print(f"SUCCESS {calculator_name}.{method_name}: {additional_info}")
    
    def validate_geometry(self, value: Any, name: str, calculator_name: str = "Validation") -> bool:
        """Validate geometry value"""
        if value is None:
            self.log_error(calculator_name, f"Missing required geometry: {name}")
            return False
        
        # Basic geometry validation - check if it has required fields
        if isinstance(value, dict):
            if 'type' in value and 'coordinates' in value:
                return True
            elif 'geometry' in value and isinstance(value['geometry'], dict):
                if 'type' in value['geometry'] and 'coordinates' in value['geometry']:
                    return True
        
        self.log_error(calculator_name, f"Invalid geometry format for {name}")
        return False
    
    # === VALIDATION SERVICES ===
    
    def validate_input(self, value: Any, name: str, calculator_name: str = "Validation") -> bool:
        """Validate input value exists"""
        if value is None:
            self.log_error(calculator_name, f"Missing required input: {name}")
            return False
        return True
    
    def validate_numeric(self, value: Any, name: str, calculator_name: str = "Validation", 
                        min_val: float = None, max_val: float = None) -> bool:
        """Validate numeric input with optional range checking"""
        if not self.validate_input(value, name, calculator_name):
            return False
        
        try:
            num_val = float(value)
            
            if min_val is not None and num_val < min_val:
                self.log_error(calculator_name, f"{name} value {num_val} is below minimum {min_val}")
                return False
            
            if max_val is not None and num_val > max_val:
                self.log_error(calculator_name, f"{name} value {num_val} is above maximum {max_val}")
                return False
            
            return True
            
        except (ValueError, TypeError):
            self.log_error(calculator_name, f"{name} is not a valid number: {value}")
            return False
    
    def validate_dict(self, value: Any, name: str, calculator_name: str = "Validation", 
                     required_keys: list = None) -> bool:
        """Validate dictionary input with optional required keys"""
        if not self.validate_input(value, name, calculator_name):
            return False
        
        if not isinstance(value, dict):
            self.log_error(calculator_name, f"{name} must be a dictionary, got {type(value)}")
            return False
        
        if required_keys:
            missing_keys = [key for key in required_keys if key not in value]
            if missing_keys:
                self.log_error(calculator_name, f"{name} missing required keys: {missing_keys}")
                return False
        
        return True
    
    # === CALCULATOR MANAGEMENT ===
    
    def get_calculator_instance(self, feature_name: str):
        """Get or create calculator instance for a feature"""
        if feature_name in self.calculator_cache:
            return self.calculator_cache[feature_name]
        
        # Get feature configuration
        feature_config = self.data_manager.get_feature_config(feature_name)
        if not feature_config:
            self.log_error("PipelineExecutor", f"No configuration found for feature: {feature_name}")
            return None
        
        try:
            # Import calculator module and class
            module_path = feature_config.get('class_path')
            class_name = feature_config.get('class_name')
            
            if not module_path or not class_name:
                self.log_error("PipelineExecutor", f"Missing class_path or class_name for feature: {feature_name}")
                return None
            
            # Handle both absolute and relative imports
            if module_path.startswith('app.'):
                module = importlib.import_module(module_path)
            else:
                # Convert datalake8 path to app path
                module_path = module_path.replace('cim_wizard.', 'app.')
                module = importlib.import_module(module_path)
            
            calculator_class = getattr(module, class_name)
            
            # Create instance with executor only (data_manager is accessed through executor)
            calculator_instance = calculator_class(self)
            
            # Cache the instance
            self.calculator_cache[feature_name] = calculator_instance
            
            return calculator_instance
            
        except Exception as e:
            self.log_error("PipelineExecutor", f"Failed to load calculator for {feature_name}: {str(e)}")
            # Additional error details for debugging
            # Could be ImportError, AttributeError, etc.
            return None
    
    # === DEPENDENCY RESOLUTION ===
    
    def check_dependencies(self, dependencies: List[str]) -> bool:
        """Check if all dependencies are satisfied"""
        for dep in dependencies:
            value = self.data_manager.get_context(dep)
            if value is None:
                return False
        return True
    
    def get_feature_safely(self, feature_name: str, calculator_name: str = "PipelineExecutor"):
        """Safely get a feature from the data manager with error handling"""
        try:
            return self.data_manager.get_feature(feature_name)
        except Exception as e:
            self.log_warning(calculator_name, f"Failed to get feature {feature_name}: {str(e)}")
            return None
    
    def enrich_context_from_inputs_or_database(self, required_inputs: List[str], calculator_name: str = "PipelineExecutor") -> Dict[str, Any]:
        """Enrich context with required inputs from data manager or database"""
        enriched_context = {}
        
        for input_name in required_inputs:
            # Try to get from data manager first
            value = self.data_manager.get_feature(input_name)
            if value is not None:
                enriched_context[input_name] = value
                continue
            
            # Try to get from context
            value = getattr(self.data_manager, input_name, None)
            if value is not None:
                enriched_context[input_name] = value
                continue
            
            # Try to get from database if we have a session
            if hasattr(self.data_manager, 'db_session') and self.data_manager.db_session:
                try:
                    # This is a simplified version - you might need to implement specific database queries
                    # based on your models
                    self.log_warning(calculator_name, f"Database lookup for {input_name} not implemented")
                except Exception as e:
                    self.log_warning(calculator_name, f"Database lookup failed for {input_name}: {str(e)}")
            
            # If still not found, log warning
            if input_name not in enriched_context:
                self.log_warning(calculator_name, f"Required input {input_name} not found")
        
        return enriched_context
    
    def get_required_features(self, target_features: List[str]) -> Set[str]:
        """Get all features required (including dependencies) for target features"""
        required = set()
        to_process = set(target_features)
        
        while to_process:
            feature = to_process.pop()
            if feature in required:
                continue
                
            required.add(feature)
            
            # Get feature configuration
            feature_config = self.data_manager.get_feature_config(feature)
            if feature_config and 'methods' in feature_config:
                # Check all methods for dependencies
                for method_config in feature_config['methods']:
                    deps = method_config.get('input_dependencies', [])
                    for dep in deps:
                        # Only add feature dependencies, not service URLs or other context
                        if self.data_manager.get_feature_config(dep):
                            to_process.add(dep)
        
        return required
    
    # === FEATURE EXECUTION ===
    
    def execute_feature(self, feature_name: str, explicit_method: str = None) -> bool:
        """Execute a single feature with optional explicit method"""
        # Check if already calculated
        if self.data_manager.has_feature(feature_name):
            self.log_info("PipelineExecutor", f"Feature {feature_name} already calculated")
            return True
        
        # Get calculator instance
        calculator = self.get_calculator_instance(feature_name)
        if not calculator:
            return False
        
        # Get feature configuration
        feature_config = self.data_manager.get_feature_config(feature_name)
        methods = feature_config.get('methods', [])
        
        if not methods:
            self.log_error("PipelineExecutor", f"No methods configured for feature: {feature_name}")
            return False
        
        # If explicit method specified, try only that method
        if explicit_method:
            method_config = next((m for m in methods if m['method_name'] == explicit_method), None)
            if method_config:
                if self.check_dependencies(method_config.get('input_dependencies', [])):
                    return self._execute_method(calculator, feature_name, method_config)
                else:
                    self.log_error("PipelineExecutor", 
                                 f"Dependencies not satisfied for {feature_name}.{explicit_method}")
                    return False
            else:
                self.log_error("PipelineExecutor", 
                             f"Method {explicit_method} not found for feature {feature_name}")
                return False
        
        # Otherwise, try methods in priority order
        sorted_methods = sorted(methods, key=lambda x: x.get('priority', 999))
        
        for method_config in sorted_methods:
            if self.check_dependencies(method_config.get('input_dependencies', [])):
                if self._execute_method(calculator, feature_name, method_config):
                    return True
        
        self.log_error("PipelineExecutor", f"No suitable method found for feature: {feature_name}")
        return False
    
    def _execute_method(self, calculator: Any, feature_name: str, method_config: Dict) -> bool:
        """Execute a specific method on a calculator"""
        method_name = method_config['method_name']
        
        try:
            # Get the method
            if not hasattr(calculator, method_name):
                self.log_error(calculator.__class__.__name__, 
                             f"Method {method_name} not found")
                return False
            
            method = getattr(calculator, method_name)
            
            # Execute the method
            self.log_info(calculator.__class__.__name__, 
                        f"Executing {method_name}")
            
            result = method()
            
            # Store the result
            if result is not None:
                self.data_manager.set_feature(feature_name, result)
                self.execution_results[feature_name] = {
                    'method': method_name,
                    'success': True,
                    'value': result
                }
                return True
            else:
                self.log_warning(calculator.__class__.__name__, 
                               f"Method {method_name} returned None")
                return False
                
        except Exception as e:
            self.log_error(calculator.__class__.__name__, 
                         f"Error executing {method_name}: {str(e)}")
            # Store error information
            # Could be logged to a file or monitoring system
            self.execution_results[feature_name] = {
                'method': method_name,
                'success': False,
                'error': str(e)
            }
            return False
    
    # === PIPELINE EXECUTION ===
    
    def execute_pipeline(self, features: List[str], parallel: bool = False) -> Dict[str, Any]:
        """Execute a pipeline to calculate multiple features"""
        # Get all required features including dependencies
        all_features = self.get_required_features(features)
        
        # Sort features by dependency order
        sorted_features = self._topological_sort(all_features)
        
        results = {
            'requested_features': features,
            'executed_features': [],
            'failed_features': [],
            'execution_order': sorted_features
        }
        
        if parallel:
            # Execute features in parallel where possible
            self._execute_parallel(sorted_features, results)
        else:
            # Execute features sequentially
            for feature in sorted_features:
                if self.execute_feature(feature):
                    results['executed_features'].append(feature)
                else:
                    results['failed_features'].append(feature)
        
        # Check if all requested features were calculated
        results['success'] = all(
            self.data_manager.has_feature(f) for f in features
        )
        
        return results
    
    def execute_explicit_pipeline(self, execution_plan: List[Dict[str, str]]) -> Dict[str, Any]:
        """Execute pipeline with explicit feature.method specifications"""
        results = {
            'execution_plan': execution_plan,
            'executed_steps': [],
            'failed_steps': [],
            'results': {}
        }
        
        for step in execution_plan:
            feature_name = step['feature_name']
            method_name = step['method_name']
            
            if self.execute_feature(feature_name, method_name):
                results['executed_steps'].append(f"{feature_name}.{method_name}")
                results['results'][feature_name] = self.data_manager.get_feature(feature_name)
            else:
                results['failed_steps'].append(f"{feature_name}.{method_name}")
                # Stop execution on failure
                break
        
        results['success'] = len(results['failed_steps']) == 0
        return results
    
    def execute_predefined_pipeline(self, pipeline_name: str, **additional_context) -> Dict[str, Any]:
        """Execute a predefined pipeline from configuration"""
        pipeline_config = self.data_manager.get_pipeline_config(pipeline_name)
        
        if not pipeline_config:
            return {
                'success': False,
                'error': f"Pipeline {pipeline_name} not found in configuration"
            }
        
        # Set additional context if provided
        if additional_context:
            self.data_manager.set_context(**additional_context)
        
        # Get features to calculate
        features = pipeline_config.get('features', [])
        parallel = pipeline_config.get('async', False)
        
        # Execute pipeline
        result = self.execute_pipeline(features, parallel=parallel)
        result['pipeline_name'] = pipeline_name
        result['pipeline_description'] = pipeline_config.get('description', '')
        
        return result
    
    def _topological_sort(self, features: Set[str]) -> List[str]:
        """Sort features in dependency order using topological sort"""
        # Build dependency graph
        graph = {}
        in_degree = {}
        
        for feature in features:
            graph[feature] = set()
            in_degree[feature] = 0
        
        # Add edges based on dependencies
        for feature in features:
            feature_config = self.data_manager.get_feature_config(feature)
            if feature_config and 'methods' in feature_config:
                for method in feature_config['methods']:
                    for dep in method.get('input_dependencies', []):
                        if dep in features:  # Only consider dependencies within our feature set
                            graph[dep].add(feature)
                            in_degree[feature] += 1
        
        # Topological sort using Kahn's algorithm
        queue = [f for f in features if in_degree[f] == 0]
        sorted_features = []
        
        while queue:
            feature = queue.pop(0)
            sorted_features.append(feature)
            
            for dependent in graph[feature]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        # Check for cycles
        if len(sorted_features) != len(features):
            self.log_error("PipelineExecutor", "Circular dependency detected in features")
            # Return features in original order as fallback
            return list(features)
        
        return sorted_features
    
    def _execute_parallel(self, sorted_features: List[str], results: Dict[str, Any]):
        """Execute features in parallel where possible"""
        # Group features by dependency level
        levels = []
        calculated = set()
        
        remaining = sorted_features.copy()
        while remaining:
            # Find features that can be calculated with current state
            current_level = []
            for feature in remaining:
                feature_config = self.data_manager.get_feature_config(feature)
                can_calculate = True
                
                if feature_config and 'methods' in feature_config:
                    # Check if any method can be executed
                    for method in feature_config['methods']:
                        deps = set(method.get('input_dependencies', []))
                        feature_deps = deps & set(sorted_features)
                        if feature_deps.issubset(calculated):
                            can_calculate = True
                            break
                    else:
                        can_calculate = False
                
                if can_calculate:
                    current_level.append(feature)
            
            if not current_level:
                # No progress possible, break to avoid infinite loop
                self.log_error("PipelineExecutor", "Cannot make progress in parallel execution")
                break
            
            levels.append(current_level)
            calculated.update(current_level)
            remaining = [f for f in remaining if f not in current_level]
        
        # Execute each level in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            for level in levels:
                futures = {
                    executor.submit(self.execute_feature, feature): feature 
                    for feature in level
                }
                
                for future in as_completed(futures):
                    feature = futures[future]
                    try:
                        success = future.result()
                        if success:
                            results['executed_features'].append(feature)
                        else:
                            results['failed_features'].append(feature)
                    except Exception as e:
                        self.log_error("PipelineExecutor", 
                                     f"Error executing {feature}: {str(e)}")
                        results['failed_features'].append(feature)
    
    # === UTILITY METHODS ===
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of execution results"""
        return {
            'total_executions': len(self.execution_results),
            'successful_executions': sum(
                1 for r in self.execution_results.values() if r['success']
            ),
            'failed_executions': sum(
                1 for r in self.execution_results.values() if not r['success']
            ),
            'execution_details': self.execution_results.copy()
        }
    
    def clear_cache(self):
        """Clear calculator cache and execution results"""
        self.calculator_cache.clear()
        self.execution_results.clear()