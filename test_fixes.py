#!/usr/bin/env python3
"""
Test script to verify calculator fixes
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_calculator_imports():
    """Test that all calculators can be imported"""
    calculators = [
        'scenario_geo_calculator',
        'scenario_census_boundary_calculator', 
        'building_geo_calculator',
        'building_props_calculator',
        'building_height_calculator_integrated',
        'building_area_calculator',
        'building_volume_calculator',
        'building_n_floors_calculator',
        'census_population_calculator',
        'building_type_calculator',
        'building_population_calculator',
        'building_n_families_calculator',
        'building_construction_year_calculator',
        'building_demographic_calculator',
        'building_geo_lod12_calculator'
    ]
    
    print("Testing calculator imports...")
    
    for calc in calculators:
        try:
            module = __import__(f'calculators.{calc}', fromlist=['*'])
            print(f"✓ {calc}")
        except Exception as e:
            print(f"✗ {calc}: {str(e)}")
            return False
    
    return True

def test_calculator_constructors():
    """Test that calculators can be instantiated"""
    print("\nTesting calculator constructors...")
    
    # Mock pipeline executor and data manager
    class MockPipelineExecutor:
        def __init__(self):
            self.data_manager = MockDataManager()
        
        def log_info(self, name, msg):
            pass
        
        def log_error(self, name, msg):
            pass
        
        def log_warning(self, name, msg):
            pass
        
        def get_feature_safely(self, feature_name, calculator_name=None):
            return None
        
        def enrich_context_from_inputs_or_database(self, inputs, calculator_name=None):
            return {}
    
    class MockDataManager:
        def __init__(self):
            pass
        
        def get_feature(self, name):
            return None
        
        def set_feature(self, name, value):
            pass
    
    mock_executor = MockPipelineExecutor()
    
    # Test a few key calculators
    test_calculators = [
        ('scenario_geo_calculator', 'ScenarioGeoCalculator'),
        ('scenario_census_boundary_calculator', 'ScenarioCensusBoundaryCalculator'),
        ('building_props_calculator', 'BuildingPropsCalculator'),
        ('census_population_calculator', 'CensusPopulationCalculator')
    ]
    
    for module_name, class_name in test_calculators:
        try:
            module = __import__(f'calculators.{module_name}', fromlist=[class_name])
            calculator_class = getattr(module, class_name)
            instance = calculator_class(mock_executor)
            print(f"✓ {class_name}")
        except Exception as e:
            print(f"✗ {class_name}: {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    print("Testing CIM Wizard Calculator Fixes")
    print("=" * 40)
    
    if test_calculator_imports() and test_calculator_constructors():
        print("\n✓ All tests passed! The fixes should work.")
    else:
        print("\n✗ Some tests failed. There may still be issues.")
        sys.exit(1)
