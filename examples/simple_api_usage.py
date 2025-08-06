"""
Simple API Usage Examples for CIM Wizard Integrated
Shows how to use the simplified dict-based API (no Pydantic validation)
"""

import requests
import json

# Base URL - adjust as needed
BASE_URL = "http://localhost:8000"

def test_pipeline_execution():
    """Test simple pipeline execution with dict input"""
    
    # Simple pipeline request - just a dictionary
    request_data = {
        "project_id": "test_project_001",
        "scenario_id": "scenario_001", 
        "features": ["building_height", "building_area"],
        "parallel": False
    }
    
    print("Testing pipeline execution...")
    print(f"Request: {json.dumps(request_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/pipeline/execute",
            json=request_data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


def test_explicit_pipeline():
    """Test explicit pipeline with specific method calls"""
    
    request_data = {
        "execution_plan": [
            {"feature_name": "building_height", "method_name": "raster_based_height"},
            {"feature_name": "building_area", "method_name": "geometry_based_area"}
        ],
        "project_id": "test_project_001",
        "scenario_id": "scenario_001"
    }
    
    print("\nTesting explicit pipeline...")
    print(f"Request: {json.dumps(request_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/pipeline/execute_explicit",
            json=request_data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


def test_single_feature():
    """Test calculating a single feature"""
    
    request_data = {
        "feature_name": "building_height",
        "method_name": "raster_based_height",
        "project_id": "test_project_001",
        "scenario_id": "scenario_001",
        "building_id": "building_001"
    }
    
    print("\nTesting single feature calculation...")
    print(f"Request: {json.dumps(request_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/pipeline/calculate_feature",
            json=request_data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


def test_vector_endpoints():
    """Test simplified vector endpoints"""
    
    print("\nTesting vector endpoints...")
    
    # Get all projects
    try:
        response = requests.get(f"{BASE_URL}/api/vector/projects?limit=5")
        print(f"Projects Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Projects: {len(response.json())} found")
        
    except requests.exceptions.RequestException as e:
        print(f"Projects Error: {e}")
    
    # Test dashboard
    try:
        response = requests.get(f"{BASE_URL}/api/vector/dashboard")
        print(f"Dashboard Status: {response.status_code}")
        if response.status_code == 200:
            dashboard = response.json()
            print(f"Dashboard: {dashboard.get('total_projects', 'N/A')} total projects")
        
    except requests.exceptions.RequestException as e:
        print(f"Dashboard Error: {e}")


def test_census_endpoints():
    """Test simplified census endpoints"""
    
    print("\nTesting census endpoints...")
    
    # Test census spatial query with simple polygon
    polygon_coords = [
        [11.2, 43.7],  # Florence area example coordinates
        [11.3, 43.7],
        [11.3, 43.8],
        [11.2, 43.8],
        [11.2, 43.7]
    ]
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/census/census_spatial",
            json=polygon_coords
        )
        
        print(f"Census Spatial Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Census zones found: {len(result.get('features', []))}")
        
    except requests.exceptions.RequestException as e:
        print(f"Census Error: {e}")


def test_raster_endpoints():
    """Test simplified raster endpoints"""
    
    print("\nTesting raster endpoints...")
    
    # Test building height calculation
    building_geometry = {
        "type": "Polygon",
        "coordinates": [[
            [11.25, 43.75],
            [11.26, 43.75], 
            [11.26, 43.76],
            [11.25, 43.76],
            [11.25, 43.75]
        ]]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/raster/height",
            json=building_geometry
        )
        
        print(f"Building Height Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Height calculated: {result.get('height', 'N/A')}m")
        
    except requests.exceptions.RequestException as e:
        print(f"Raster Error: {e}")


def test_configuration():
    """Test configuration endpoints"""
    
    print("\nTesting configuration...")
    
    try:
        # Get available features
        response = requests.get(f"{BASE_URL}/api/pipeline/available_features")
        print(f"Features Status: {response.status_code}")
        if response.status_code == 200:
            features = response.json()
            print(f"Available features: {features.get('features', [])}")
        
        # Get configuration
        response = requests.get(f"{BASE_URL}/api/pipeline/configuration")
        print(f"Config Status: {response.status_code}")
        
    except requests.exceptions.RequestException as e:
        print(f"Configuration Error: {e}")


def test_health_endpoints():
    """Test all health endpoints"""
    
    print("\nTesting health endpoints...")
    
    endpoints = [
        "/health",
        "/api/vector/health", 
        "/api/pipeline/health"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"{endpoint}: {response.status_code} - {response.json().get('status', 'unknown')}")
        except requests.exceptions.RequestException as e:
            print(f"{endpoint}: Error - {e}")


if __name__ == "__main__":
    print("=== CIM Wizard Integrated API Test ===")
    print("Simplified dict-based API (no Pydantic validation)")
    print("=" * 50)
    
    # Test all endpoints
    test_health_endpoints()
    test_configuration()
    test_vector_endpoints()
    test_census_endpoints() 
    test_raster_endpoints()
    test_pipeline_execution()
    test_explicit_pipeline()
    test_single_feature()
    
    print("\n=== Test Complete ===")