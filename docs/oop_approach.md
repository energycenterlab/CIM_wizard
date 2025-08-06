# Object-Oriented Architecture in CIM Wizard

## Overview

CIM Wizard uses a sophisticated object-oriented architecture that separates concerns and provides flexibility in feature calculation. The system is built around four main components:

1. **Configuration System**
2. **Data Manager**
3. **Pipeline Executor**
4. **Calculator Classes**

## Core Components

### 1. Configuration System (`configuration.json`)

The configuration file defines:
- Available features and their constraints
- Calculator class paths and methods
- Method priorities and dependencies
- Predefined pipelines
- Global settings

```json
{
  "features": {
    "building_height": {
      "constraints": {
        "datatype": "float",
        "value_range": [0, 500],
        "required": false
      },
      "class_path": "app.calculators.building_height_calculator",
      "class_name": "BuildingHeightCalculator",
      "methods": [
        {
          "priority": 1,
          "input_dependencies": ["building_geo", "raster_service"],
          "method_name": "calculate_from_raster_service"
        },
        {
          "priority": 2,
          "input_dependencies": ["building_geo"],
          "method_name": "calculate_from_osm_height"
        }
      ]
    }
  }
}
```

### 2. Data Manager (`CimWizardDataManager`)

**Purpose**: Centralized context and state management

**Key Features**:
- **Context Management**: Stores all calculation inputs and outputs
- **Service Integration**: Provides access to census and raster services
- **Feature Proxies**: Enables intuitive method chaining
- **Configuration Access**: Loads and provides configuration data

**Design Pattern**: Singleton-like context manager

```python
class CimWizardDataManager:
    def __init__(self, config_path=None, db_session=None):
        # Core data storage
        self.calculated_features = {}
        
        # Service instances
        self.census_service = None
        self.raster_service = None
        
        # Feature proxies for chaining
        self.building_height = FeatureProxy('building_height')
```

**Key Methods**:
- `set_context()`: Set multiple context values
- `get_feature()`: Retrieve calculated features
- `get_census_service()`: Get integrated census service
- `get_raster_service()`: Get integrated raster service

### 3. Pipeline Executor (`CimWizardPipelineExecutor`)

**Purpose**: Orchestrates feature calculation and manages execution flow

**Key Features**:
- **Dependency Resolution**: Automatically determines calculation order
- **Method Selection**: Chooses appropriate calculation methods
- **Parallel Execution**: Supports concurrent feature calculation
- **Calculator Management**: Caches calculator instances
- **Error Handling**: Graceful fallback to alternative methods

**Design Pattern**: Strategy pattern with dependency injection

```python
class CimWizardPipelineExecutor:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.calculator_cache = {}
        self.execution_results = {}
```

**Execution Flow**:
1. Receive feature request
2. Resolve dependencies
3. Topological sort for execution order
4. Load calculator instances
5. Execute methods by priority
6. Store results in data manager

### 4. Calculator Classes

**Purpose**: Encapsulate feature-specific calculation logic

**Design Pattern**: Strategy pattern with multiple calculation methods

**Structure**:
```python
class FeatureCalculator:
    def __init__(self, executor, data_manager):
        self.executor = executor
        self.data_manager = data_manager
        
    def primary_method(self):
        # Preferred calculation method
        pass
        
    def fallback_method(self):
        # Alternative if primary fails
        pass
```

**Key Characteristics**:
- Each feature has its own calculator class
- Multiple methods with priority ordering
- Access to data manager for context
- Access to executor for validation and logging

## Design Patterns

### 1. Dependency Injection
- Calculators receive executor and data_manager
- Services injected into data_manager
- Database sessions injected via FastAPI

### 2. Strategy Pattern
- Multiple calculation strategies per feature
- Runtime method selection based on available data

### 3. Chain of Responsibility
- Methods tried in priority order
- Automatic fallback on failure

### 4. Factory Pattern
- Dynamic calculator instantiation
- Class loading from configuration

### 5. Proxy Pattern
- Feature proxies for method chaining
- Lazy evaluation of calculations

## Method Chaining

The system supports intuitive method chaining:

```python
# Define execution plan
plan = (
    data_manager.building_height.calculate_from_raster_service() |
    data_manager.building_area.calculate_from_geometry() |
    data_manager.building_volume.calculate_from_height_and_area()
)

# Execute plan
result = executor.execute_explicit_pipeline(plan.to_execution_plan())
```

## Execution Strategies

### 1. Automatic Execution
```python
executor.execute_pipeline(['building_height', 'building_area'])
```
- Automatically resolves dependencies
- Selects methods by priority
- Handles failures gracefully

### 2. Explicit Execution
```python
execution_plan = [
    {'feature_name': 'building_height', 'method_name': 'calculate_from_raster_service'},
    {'feature_name': 'building_area', 'method_name': 'calculate_from_geometry'}
]
executor.execute_explicit_pipeline(execution_plan)
```
- Full control over method selection
- No automatic fallback
- Useful for testing specific methods

### 3. Predefined Pipelines
```python
executor.execute_predefined_pipeline('milestone1_scenario')
```
- Configured workflows
- Reusable calculation patterns
- Consistent results

## Benefits of OOP Approach

### 1. Modularity
- Each calculator is independent
- Easy to add new features
- Simple to modify existing logic

### 2. Flexibility
- Multiple calculation methods
- Runtime method selection
- Graceful degradation

### 3. Testability
- Isolated calculator testing
- Mock dependencies easily
- Unit test individual methods

### 4. Maintainability
- Clear separation of concerns
- Configuration-driven behavior
- Consistent patterns

### 5. Extensibility
- Add new calculators without modifying core
- Plugin-like architecture
- Override methods in subclasses

## Integration with Database Services

The integrated version enhances the OOP approach:

```python
class BuildingHeightCalculator:
    def calculate_from_raster_service(self):
        # Direct database access
        raster_service = self.data_manager.get_raster_service()
        result = raster_service.calculate_building_height(
            building_geometry=building_geo,
            use_cache=True
        )
        return result['building_height']
```

**Advantages**:
- No network latency
- Transaction support
- Shared database connections
- Better error handling

## Best Practices

1. **Single Responsibility**: Each calculator handles one feature
2. **Dependency Injection**: Always inject dependencies
3. **Configuration Over Code**: Define behavior in configuration
4. **Fail Gracefully**: Provide fallback methods
5. **Log Extensively**: Use executor's logging services
6. **Validate Inputs**: Use executor's validation methods
7. **Cache Results**: Store in data_manager for reuse

## Example Calculator Implementation

```python
class BuildingVolumeCalculator:
    def __init__(self, executor, data_manager):
        self.executor = executor
        self.data_manager = data_manager
        self.calculator_name = "BuildingVolumeCalculator"
    
    def calculate_from_height_and_area(self):
        # Get dependencies
        height = self.data_manager.get_feature('building_height')
        area = self.data_manager.get_feature('building_area')
        
        # Validate
        if not self.executor.validate_numeric(height, 'height', self.calculator_name):
            return None
        if not self.executor.validate_numeric(area, 'area', self.calculator_name):
            return None
        
        # Calculate
        volume = height * area
        
        # Log
        self.executor.log_info(self.calculator_name, f"Volume calculated: {volume}")
        
        return volume
```

This OOP architecture provides a robust, flexible, and maintainable system for complex feature calculations with multiple data sources and calculation strategies.