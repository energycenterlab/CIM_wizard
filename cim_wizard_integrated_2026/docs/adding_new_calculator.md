# How to Add a New Calculator

This guide walks you through the process of adding a new calculator to the CIM Wizard Integrated system.

## Table of Contents
1. [Overview](#overview)
2. [Calculator Architecture](#calculator-architecture)
3. [Step-by-Step Guide](#step-by-step-guide)
4. [Calculator Template](#calculator-template)
5. [Database Integration](#database-integration)
6. [API Endpoint Setup](#api-endpoint-setup)
7. [Testing Your Calculator](#testing-your-calculator)
8. [Best Practices](#best-practices)
9. [Examples](#examples)

---

## Overview

Calculators in CIM Wizard Integrated are modular components that perform specific calculations on geospatial and demographic data. Each calculator:
- Inherits from a base calculator class
- Has its own database model
- Exposes an API endpoint
- Can depend on other calculators

---

## Calculator Architecture

```
┌─────────────────────────────────────────┐
│           API Endpoint                   │
│    /api/calculate/your_calculator        │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         Calculator Service               │
│   app/services/your_calculator.py        │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         Calculator Class                 │
│  app/calculators/your_calculator.py      │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│          Database Model                  │
│     app/models/your_model.py            │
└─────────────────────────────────────────┘
```

---

## Step-by-Step Guide

### Step 1: Create the Calculator Class

Create a new file in `app/calculators/your_calculator_name.py`:

```python
"""
Your Calculator Name
Description: What this calculator does
Author: Your Name
Date: YYYY-MM-DD
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.calculators.base import BaseCalculator
from app.models import YourModel
from app.core.logging import get_logger

logger = get_logger(__name__)


class YourCalculator(BaseCalculator):
    """
    Calculator for computing [what it computes].
    
    This calculator:
    - Does X
    - Computes Y
    - Returns Z
    """
    
    def __init__(self, db: Session):
        """Initialize the calculator with database session."""
        super().__init__(db)
        self.name = "your_calculator"
        self.description = "Brief description of what this calculator does"
        self.version = "1.0.0"
        
    def calculate(self, scenario_id: int, **kwargs) -> Dict[str, Any]:
        """
        Main calculation method.
        
        Args:
            scenario_id: The scenario to calculate for
            **kwargs: Additional parameters
            
        Returns:
            Dict containing calculation results
        """
        try:
            # Log the start
            logger.info(f"Starting {self.name} calculation for scenario {scenario_id}")
            
            # Validate inputs
            self._validate_inputs(scenario_id, **kwargs)
            
            # Perform calculation
            results = self._perform_calculation(scenario_id, **kwargs)
            
            # Store results if needed
            self._store_results(results, scenario_id)
            
            # Log completion
            logger.info(f"Completed {self.name} calculation")
            
            return {
                "status": "success",
                "calculator": self.name,
                "scenario_id": scenario_id,
                "results": results,
                "metadata": self._get_metadata()
            }
            
        except Exception as e:
            logger.error(f"Error in {self.name} calculation: {str(e)}")
            raise
            
    def _validate_inputs(self, scenario_id: int, **kwargs):
        """Validate input parameters."""
        if not scenario_id:
            raise ValueError("scenario_id is required")
            
        # Add your validation logic here
        
    def _perform_calculation(self, scenario_id: int, **kwargs) -> Any:
        """
        Perform the actual calculation logic.
        
        This is where your main calculation happens.
        """
        # Example calculation
        query = self.db.query(YourModel).filter(
            YourModel.scenario_id == scenario_id
        )
        
        results = []
        for item in query:
            # Perform calculations
            calculated_value = self._calculate_value(item)
            results.append({
                "id": item.id,
                "value": calculated_value
            })
            
        return results
        
    def _calculate_value(self, item) -> float:
        """Helper method for individual calculations."""
        # Your calculation logic here
        return item.some_field * 2  # Example
        
    def _store_results(self, results: Any, scenario_id: int):
        """Store calculation results in database if needed."""
        # Optional: Store results
        pass
        
    def _get_metadata(self) -> Dict[str, Any]:
        """Return calculator metadata."""
        return {
            "version": self.version,
            "description": self.description,
            "timestamp": datetime.utcnow().isoformat()
        }
```

### Step 2: Create the Database Model (if needed)

Create or update `app/models/your_model.py`:

```python
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class YourCalculationResult(Base):
    """Model for storing calculation results."""
    
    __tablename__ = "your_calculation_results"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"))
    
    # Your calculated fields
    calculated_value = Column(Float)
    calculation_method = Column(String(50))
    confidence_score = Column(Float)
    
    # Timestamps
    calculated_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    scenario = relationship("Scenario", back_populates="your_results")
    building = relationship("Building", back_populates="your_results")
```

### Step 3: Create the Pydantic Schema

Create `app/schemas/your_calculator.py`:

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class YourCalculatorRequest(BaseModel):
    """Request model for your calculator."""
    
    scenario_id: int = Field(..., description="Scenario ID to calculate for")
    param1: Optional[float] = Field(None, description="Optional parameter 1")
    param2: Optional[str] = Field(None, description="Optional parameter 2")
    
    class Config:
        schema_extra = {
            "example": {
                "scenario_id": 1,
                "param1": 100.0,
                "param2": "example"
            }
        }


class YourCalculatorResponse(BaseModel):
    """Response model for your calculator."""
    
    status: str
    calculator: str
    scenario_id: int
    results: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "calculator": "your_calculator",
                "scenario_id": 1,
                "results": [
                    {"id": 1, "value": 123.45}
                ],
                "metadata": {
                    "version": "1.0.0",
                    "timestamp": "2024-01-01T00:00:00"
                }
            }
        }
```

### Step 4: Create the Service Layer

Create `app/services/your_calculator_service.py`:

```python
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.calculators.your_calculator import YourCalculator
from app.core.logging import get_logger

logger = get_logger(__name__)


class YourCalculatorService:
    """Service layer for your calculator."""
    
    def __init__(self, db: Session):
        self.db = db
        self.calculator = YourCalculator(db)
        
    def calculate(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process calculation request.
        
        Args:
            request_data: Dictionary containing request parameters
            
        Returns:
            Calculation results
        """
        try:
            # Extract parameters
            scenario_id = request_data.get("scenario_id")
            params = {k: v for k, v in request_data.items() if k != "scenario_id"}
            
            # Run calculation
            results = self.calculator.calculate(scenario_id, **params)
            
            return results
            
        except Exception as e:
            logger.error(f"Service error: {str(e)}")
            raise
```

### Step 5: Create the API Endpoint

Add to `app/api/endpoints/calculators.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.your_calculator import (
    YourCalculatorRequest,
    YourCalculatorResponse
)
from app.services.your_calculator_service import YourCalculatorService

router = APIRouter()


@router.post(
    "/calculate/your_calculator",
    response_model=YourCalculatorResponse,
    summary="Run Your Calculator",
    description="Detailed description of what this calculator does"
)
async def calculate_your_thing(
    request: YourCalculatorRequest,
    db: Session = Depends(get_db)
):
    """
    Run your calculator on the specified scenario.
    
    This endpoint:
    - Validates input parameters
    - Runs the calculation
    - Returns results
    """
    try:
        service = YourCalculatorService(db)
        result = service.calculate(request.dict())
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 6: Register the Calculator

Update `app/calculators/__init__.py`:

```python
from app.calculators.your_calculator import YourCalculator

# Add to the calculator registry
CALCULATORS = {
    # ... existing calculators ...
    "your_calculator": YourCalculator,
}
```

---

## Database Integration

### Creating Tables

Add migration script in `migrations/`:

```sql
-- Create table for your calculator results
CREATE TABLE IF NOT EXISTS your_calculation_results (
    id SERIAL PRIMARY KEY,
    scenario_id INTEGER NOT NULL REFERENCES scenarios(id),
    building_id INTEGER REFERENCES buildings(id),
    calculated_value FLOAT,
    calculation_method VARCHAR(50),
    confidence_score FLOAT,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_your_results_scenario ON your_calculation_results(scenario_id);
CREATE INDEX idx_your_results_building ON your_calculation_results(building_id);
```

### Using PostGIS Functions

If your calculator needs spatial operations:

```python
from geoalchemy2 import func

# Example: Calculate area
area = self.db.query(
    func.ST_Area(Building.geometry)
).filter(Building.scenario_id == scenario_id).scalar()

# Example: Find nearby features
nearby = self.db.query(Building).filter(
    func.ST_DWithin(
        Building.geometry,
        target_geometry,
        distance
    )
).all()
```

---

## Testing Your Calculator

### Unit Tests

Create `tests/calculators/test_your_calculator.py`:

```python
import pytest
from sqlalchemy.orm import Session
from app.calculators.your_calculator import YourCalculator


class TestYourCalculator:
    """Test suite for YourCalculator."""
    
    def test_initialization(self, db_session: Session):
        """Test calculator initialization."""
        calculator = YourCalculator(db_session)
        assert calculator.name == "your_calculator"
        assert calculator.version == "1.0.0"
        
    def test_calculate(self, db_session: Session, sample_scenario):
        """Test calculation method."""
        calculator = YourCalculator(db_session)
        result = calculator.calculate(sample_scenario.id)
        
        assert result["status"] == "success"
        assert result["calculator"] == "your_calculator"
        assert "results" in result
        
    def test_invalid_scenario(self, db_session: Session):
        """Test with invalid scenario."""
        calculator = YourCalculator(db_session)
        
        with pytest.raises(ValueError):
            calculator.calculate(scenario_id=None)
```

### Integration Tests

Test the API endpoint:

```python
def test_api_endpoint(client, sample_scenario):
    """Test the calculator API endpoint."""
    response = client.post(
        "/api/calculate/your_calculator",
        json={
            "scenario_id": sample_scenario.id,
            "param1": 100.0
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
```

### Manual Testing

Test using curl or the API documentation:

```bash
# Using curl
curl -X POST "http://localhost:8000/api/calculate/your_calculator" \
     -H "Content-Type: application/json" \
     -d '{"scenario_id": 1, "param1": 100.0}'

# Or use the Swagger UI at http://localhost:8000/docs
```

---

## Best Practices

### 1. Error Handling

Always implement proper error handling:

```python
try:
    # Your calculation
    pass
except ValueError as e:
    logger.warning(f"Invalid input: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

### 2. Logging

Use structured logging:

```python
logger.info(
    "Calculation started",
    extra={
        "calculator": self.name,
        "scenario_id": scenario_id,
        "parameters": kwargs
    }
)
```

### 3. Performance Optimization

- Use database indexes
- Implement batch processing for large datasets
- Use query optimization
- Consider caching results

```python
# Batch processing example
def process_in_batches(self, items, batch_size=1000):
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        self._process_batch(batch)
        self.db.commit()
```

### 4. Dependency Management

If your calculator depends on others:

```python
class YourCalculator(BaseCalculator):
    def __init__(self, db: Session):
        super().__init__(db)
        self.dependencies = ["building_area", "building_height"]
        
    def check_dependencies(self, scenario_id):
        """Ensure required calculations are complete."""
        for dep in self.dependencies:
            if not self._is_calculated(dep, scenario_id):
                raise ValueError(f"Dependency {dep} not calculated")
```

### 5. Documentation

Always document your calculator:

```python
class YourCalculator(BaseCalculator):
    """
    Calculator for [specific purpose].
    
    Algorithm:
        1. Step one description
        2. Step two description
        3. Step three description
    
    Dependencies:
        - building_area: Required for X
        - census_data: Required for Y
    
    Output:
        - calculated_value: Description of what this represents
        - confidence_score: How reliable the calculation is (0-1)
    
    References:
        - Paper/Standard/Method used
        - URL to documentation
    """
```

---

## Examples

### Example 1: Simple Property Calculator

```python
class BuildingAgeCalculator(BaseCalculator):
    """Calculate building age from construction year."""
    
    def calculate(self, scenario_id: int, reference_year: int = 2024):
        buildings = self.db.query(Building).filter(
            Building.scenario_id == scenario_id
        ).all()
        
        results = []
        for building in buildings:
            if building.construction_year:
                age = reference_year - building.construction_year
                building.age = age
                results.append({
                    "building_id": building.id,
                    "age": age
                })
        
        self.db.commit()
        return results
```

### Example 2: Spatial Calculator

```python
class ProximityCalculator(BaseCalculator):
    """Calculate proximity to amenities."""
    
    def calculate(self, scenario_id: int, amenity_type: str):
        from geoalchemy2 import func
        
        buildings = self.db.query(Building).filter(
            Building.scenario_id == scenario_id
        ).all()
        
        amenities = self.db.query(Amenity).filter(
            Amenity.type == amenity_type
        ).all()
        
        results = []
        for building in buildings:
            # Find nearest amenity
            nearest_distance = self.db.query(
                func.ST_Distance(building.geometry, Amenity.geometry)
            ).filter(
                Amenity.type == amenity_type
            ).order_by(
                func.ST_Distance(building.geometry, Amenity.geometry)
            ).first()[0]
            
            results.append({
                "building_id": building.id,
                "nearest_distance": nearest_distance,
                "amenity_type": amenity_type
            })
        
        return results
```

### Example 3: Dependent Calculator

```python
class EnergyEfficiencyCalculator(BaseCalculator):
    """Calculate energy efficiency based on multiple factors."""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.dependencies = ["building_area", "building_height", "building_age"]
    
    def calculate(self, scenario_id: int):
        # Check dependencies
        self.check_dependencies(scenario_id)
        
        # Get calculated values from dependencies
        buildings = self.db.query(
            Building.id,
            Building.area,
            Building.height,
            Building.age
        ).filter(
            Building.scenario_id == scenario_id
        ).all()
        
        results = []
        for building in buildings:
            # Complex calculation using multiple inputs
            efficiency_score = self._calculate_efficiency(
                area=building.area,
                height=building.height,
                age=building.age
            )
            
            results.append({
                "building_id": building.id,
                "efficiency_score": efficiency_score,
                "efficiency_class": self._get_efficiency_class(efficiency_score)
            })
        
        return results
    
    def _calculate_efficiency(self, area, height, age):
        # Your efficiency algorithm
        base_score = 100
        
        # Penalties and bonuses
        if age > 50:
            base_score -= 20
        if area > 1000:
            base_score -= 10
        if height < 10:
            base_score += 5
            
        return max(0, min(100, base_score))
    
    def _get_efficiency_class(self, score):
        if score >= 80:
            return "A"
        elif score >= 60:
            return "B"
        elif score >= 40:
            return "C"
        elif score >= 20:
            return "D"
        else:
            return "E"
```

---

## Checklist

Before considering your calculator complete:

- [ ] Calculator class created in `app/calculators/`
- [ ] Database model created/updated if needed
- [ ] Pydantic schemas defined
- [ ] Service layer implemented
- [ ] API endpoint added
- [ ] Calculator registered in `__init__.py`
- [ ] Unit tests written
- [ ] Integration tests written
- [ ] Documentation updated
- [ ] Error handling implemented
- [ ] Logging added
- [ ] Performance optimized
- [ ] Code reviewed

---

## Getting Help

If you need help:

1. Check existing calculators for examples
2. Review the base calculator class
3. Check the API documentation
4. Review test files for patterns
5. Ask the team

---

## Summary

Adding a new calculator involves:
1. Creating the calculator class
2. Setting up database models if needed
3. Defining API schemas
4. Implementing the service layer
5. Adding API endpoints
6. Writing tests
7. Documenting your work

Follow the patterns established in existing calculators and maintain consistency with the codebase.