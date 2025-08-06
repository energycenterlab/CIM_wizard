"""
CIM Wizard Data Manager - Integrated Version
Handles context management, configuration loading, and feature proxies
Now with direct database access to census and raster services
"""

import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from sqlalchemy.orm import Session

from app.services.census_service import CensusService
from app.services.raster_service import RasterService


class FeatureMethodSelector:
    """Represents a specific feature.method combination for chaining"""
    
    def __init__(self, feature_name: str, method_name: str):
        self.feature_name = feature_name
        self.method_name = method_name
        self.next_selector = None
    
    def __or__(self, other):
        """Enable chaining with | operator"""
        if isinstance(other, FeatureMethodSelector):
            # Find the end of the current chain
            current = self
            while current.next_selector is not None:
                current = current.next_selector
            # Append the other selector at the end
            current.next_selector = other
            return self
        raise TypeError("Can only chain FeatureMethodSelector objects")
    
    def to_execution_plan(self):
        """Convert chained selectors to execution plan"""
        plan = []
        current = self
        while current:
            plan.append({
                'feature_name': current.feature_name,
                'method_name': current.method_name
            })
            current = current.next_selector
        return plan


class FeatureProxy:
    """Proxy object that creates FeatureMethodSelector when accessing methods"""
    
    def __init__(self, feature_name: str):
        self.feature_name = feature_name
    
    def __getattr__(self, method_name: str):
        """Create FeatureMethodSelector when accessing method"""
        return FeatureMethodSelector(self.feature_name, method_name)


class CimWizardDataManager:
    """CIM Wizard Data Manager - handles context, config, feature proxies, and service access"""
    
    def __init__(self, config_path: str = None, db_session: Session = None):
        # Core data storage
        self.calculated_features = {}
        
        # Database session for services
        self.db_session = db_session
        
        # Initialize services
        self.census_service = None
        self.raster_service = None
        
        # Identifiers
        self.scenario_id = None
        self.building_id = None
        self.project_id = None
        
        # Input data (actual data with _data suffix)
        self.scenario_geo_data = None
        self.building_geo_data = None
        self.building_props_data = None
        
        # Calculated features (actual values)
        self.building_height_data = None
        self.building_area_data = None
        self.building_volume_data = None
        self.building_n_floors_data = None
        self.scenario_census_boundary_data = None
        self.census_population_data = None
        self.building_population_data = None
        self.building_n_families_data = None
        self.building_type_data = None
        self.building_construction_year_data = None
        self.building_demographic_data = None
        self.building_geo_lod12_data = None
        
        # Service URLs (kept for compatibility but services are now direct)
        self.raster_service_url = "internal://raster_service"
        self.census_service_url = "internal://census_service"
        
        # Additional context
        self.project_boundary = None
        
        # Configuration
        self.configuration = None
        self.load_configuration(config_path)
        
        # Feature proxies for chaining
        self.scenario_geo = FeatureProxy('scenario_geo')
        self.scenario_census_boundary = FeatureProxy('scenario_census_boundary')
        self.building_geo = FeatureProxy('building_geo')
        self.building_props = FeatureProxy('building_props')
        self.building_height = FeatureProxy('building_height')
        self.building_area = FeatureProxy('building_area')
        self.building_volume = FeatureProxy('building_volume')
        self.building_n_floors = FeatureProxy('building_n_floors')
        self.census_population = FeatureProxy('census_population')
        self.building_population = FeatureProxy('building_population')
        self.building_type = FeatureProxy('building_type')
        self.building_construction_year = FeatureProxy('building_construction_year')
        self.building_n_families = FeatureProxy('building_n_families')
        self.building_demographic = FeatureProxy('building_demographic')
        self.building_geo_lod12 = FeatureProxy('building_geo_lod12')
    
    def load_configuration(self, config_path: str = None):
        """Load configuration from JSON file"""
        if config_path is None:
            # Default configuration path
            config_path = Path(__file__).parent / "configuration.json"
        
        try:
            with open(config_path, 'r') as f:
                self.configuration = json.load(f)
                
            # Update service URLs to indicate internal services
            if 'services' in self.configuration:
                self.configuration['services']['raster_gateway']['url'] = "internal://raster_service"
                self.configuration['services']['census_gateway']['url'] = "internal://census_service"
                
        except FileNotFoundError:
            print(f"Warning: Configuration file not found at {config_path}")
            self.configuration = {}
        except json.JSONDecodeError as e:
            print(f"Error parsing configuration file: {e}")
            self.configuration = {}
    
    def get_census_service(self) -> CensusService:
        """Get or create census service instance"""
        if not self.census_service:
            self.census_service = CensusService(db_session=self.db_session)
        return self.census_service
    
    def get_raster_service(self) -> RasterService:
        """Get or create raster service instance"""
        if not self.raster_service:
            self.raster_service = RasterService(db_session=self.db_session)
        return self.raster_service
    
    # Context Management Methods
    def set_context(self, **kwargs):
        """Set multiple context values at once"""
        for key, value in kwargs.items():
            if key == 'db_session':
                self.db_session = value
                # Reset services to use new session
                self.census_service = None
                self.raster_service = None
            elif hasattr(self, key):
                setattr(self, key, value)
            elif hasattr(self, f"{key}_data"):
                setattr(self, f"{key}_data", value)
            else:
                print(f"Warning: Unknown context key: {key}")
    
    def get_context(self, key: str) -> Any:
        """Get a context value by key"""
        if hasattr(self, key):
            return getattr(self, key)
        elif hasattr(self, f"{key}_data"):
            return getattr(self, f"{key}_data")
        return None
    
    def clear_context(self):
        """Clear all context data"""
        self.calculated_features = {}
        
        # Clear identifiers
        self.scenario_id = None
        self.building_id = None
        self.project_id = None
        
        # Clear all data attributes
        for attr in dir(self):
            if attr.endswith('_data'):
                setattr(self, attr, None)
        
        # Clear services
        self.census_service = None
        self.raster_service = None
    
    # Feature Management Methods
    def set_feature(self, feature_name: str, value: Any):
        """Set a calculated feature value"""
        self.calculated_features[feature_name] = value
        
        # Also set the corresponding _data attribute if it exists
        data_attr = f"{feature_name}_data"
        if hasattr(self, data_attr):
            setattr(self, data_attr, value)
    
    def get_feature(self, feature_name: str) -> Any:
        """Get a calculated feature value"""
        # First check calculated_features
        if feature_name in self.calculated_features:
            return self.calculated_features[feature_name]
        
        # Then check _data attributes
        data_attr = f"{feature_name}_data"
        if hasattr(self, data_attr):
            return getattr(self, data_attr)
        
        return None
    
    def has_feature(self, feature_name: str) -> bool:
        """Check if a feature has been calculated"""
        return (feature_name in self.calculated_features or 
                getattr(self, f"{feature_name}_data", None) is not None)
    
    def get_available_features(self) -> List[str]:
        """Get list of available (calculated) features"""
        features = list(self.calculated_features.keys())
        
        # Add features from _data attributes that have values
        for attr in dir(self):
            if attr.endswith('_data') and getattr(self, attr) is not None:
                feature_name = attr[:-5]  # Remove '_data' suffix
                if feature_name not in features:
                    features.append(feature_name)
        
        return features
    
    # Configuration Access Methods
    def get_feature_config(self, feature_name: str) -> Dict[str, Any]:
        """Get configuration for a specific feature"""
        if self.configuration and 'features' in self.configuration:
            return self.configuration['features'].get(feature_name, {})
        return {}
    
    def get_pipeline_config(self, pipeline_name: str) -> Dict[str, Any]:
        """Get configuration for a predefined pipeline"""
        if self.configuration and 'predefined_pipelines' in self.configuration:
            return self.configuration['predefined_pipelines'].get(pipeline_name, {})
        return {}
    
    def get_global_settings(self) -> Dict[str, Any]:
        """Get global settings from configuration"""
        if self.configuration:
            return self.configuration.get('global_settings', {})
        return {}
    
    # Database Synchronization Methods
    def sync_to_database(self, db_session: Session = None):
        """Sync calculated features to database"""
        # Use provided session or instance session
        session = db_session or self.db_session
        if not session:
            print("Warning: No database session available for sync")
            return
        
        # This would save calculated features to the database
        # Implementation depends on specific requirements
        pass
    
    def load_from_database(self, db_session: Session = None, 
                          project_id: str = None, 
                          scenario_id: str = None, 
                          building_id: str = None):
        """Load data from database into context"""
        # Use provided session or instance session
        session = db_session or self.db_session
        if not session:
            print("Warning: No database session available for loading")
            return
        
        # Set identifiers
        if project_id:
            self.project_id = project_id
        if scenario_id:
            self.scenario_id = scenario_id
        if building_id:
            self.building_id = building_id
        
        # Load data from database
        # Implementation depends on specific requirements
        pass
    
    # Utility Methods
    def to_dict(self) -> Dict[str, Any]:
        """Convert current context to dictionary"""
        result = {
            'project_id': self.project_id,
            'scenario_id': self.scenario_id,
            'building_id': self.building_id,
            'calculated_features': self.calculated_features.copy(),
            'services': {
                'census': 'integrated',
                'raster': 'integrated'
            }
        }
        
        # Add all _data attributes
        for attr in dir(self):
            if attr.endswith('_data'):
                value = getattr(self, attr)
                if value is not None:
                    result[attr[:-5]] = value  # Remove '_data' suffix
        
        return result
    
    def __repr__(self):
        services_status = "integrated" if (self.census_service or self.raster_service) else "not initialized"
        return f"CimWizardDataManager(project={self.project_id}, scenario={self.scenario_id}, features={len(self.calculated_features)}, services={services_status})"