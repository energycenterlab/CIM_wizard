"""
Vector data models for CIM Wizard Integrated
Uses cim_vector schema
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, BigInteger, func, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.db.database import Base


class ProjectScenario(Base):
    """Project scenario model"""
    __tablename__ = 'cim_wizard_project_scenario'
    __table_args__ = {'schema': 'cim_vector'}
    
    # Primary keys
    project_id = Column(String(100), primary_key=True)
    scenario_id = Column(String(100), primary_key=True)
    
    # Project information
    project_name = Column(String(255))
    scenario_name = Column(String(255))
    
    # Spatial data
    project_boundary = Column(Geometry('POLYGON', srid=4326), nullable=True)
    project_center = Column(Geometry('POINT', srid=4326), nullable=True)
    project_zoom = Column(Integer, default=15)
    project_crs = Column(Integer, default=4326)
    census_boundary = Column(Geometry('MULTIPOLYGON', srid=4326), nullable=True)
    
    # Additional fields (these columns may not exist in all database versions)
    # cosimulator_config_mongo_path = Column(String, nullable=True)
    # network_mongo_path = Column(JSON, nullable=True)
    # results_mongo_path = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    # Note: All relationships removed due to missing foreign key constraints in database schema


class Building(Base):
    """Building model - uses cim_wizard_building table with UUID primary key"""
    __tablename__ = 'cim_wizard_building'
    __table_args__ = {'schema': 'cim_vector'}
    
    # Primary key (UUID)
    building_id = Column(String(100), primary_key=True)  # UUID stored as string
    lod = Column(Integer, default=0, nullable=False)
    
    # Spatial data
    building_geometry = Column(Geometry('GEOMETRY', srid=4326), nullable=False, index=True)
    building_geometry_source = Column(String(50), nullable=False)
    
    # Census link
    census_id = Column(BigInteger, nullable=True, index=True)
    
    # LoD 1.2 data
    building_surfaces_lod12 = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class BuildingProperties(Base):
    """Building properties model - uses cim_wizard_building_properties table"""
    __tablename__ = 'cim_wizard_building_properties'
    __table_args__ = {'schema': 'cim_vector'}
    
    # Composite primary key
    scenario_id = Column(String(100), primary_key=True)  # UUID stored as string
    building_id = Column(String(100), primary_key=True)  # UUID stored as string
    lod = Column(Integer, default=0, primary_key=True)
    
    # Project reference
    project_id = Column(String(100), nullable=False)
    
    # Physical properties
    height = Column(Float, nullable=True)
    area = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    number_of_floors = Column(Float, nullable=True)
    
    # Building characteristics
    type = Column(String(50), nullable=True)  # Building type (residential, commercial, etc.)
    envelope_efficiency = Column(String(20), nullable=True)  # "low" | "medium" | "high"
    fmu_file = Column(String(255), nullable=True)  # FMU file path or identifier
    const_period_census = Column(String(10), nullable=True)
    const_year = Column(Integer, nullable=True)
    const_tabula = Column(String(15), nullable=True)  # Note: lowercase in actual table
    
    # Demographics
    n_people = Column(Integer, nullable=True)
    n_family = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class GridBus(Base):
    """Grid bus model"""
    __tablename__ = 'grid_bus'
    __table_args__ = {'schema': 'cim_vector'}
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Identification
    network_id = Column(String(100))
    bus_id = Column(Integer)
    
    # Foreign keys
    project_id = Column(String(100), nullable=True)
    scenario_id = Column(String(100), nullable=True)
    
    # Spatial and properties
    geometry = Column(Geometry('POINT', srid=4326), nullable=True, index=True)
    name = Column(String(255), nullable=True)
    voltage_kv = Column(Float, nullable=True)
    zone = Column(String(50), nullable=True)
    in_service = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    # Note: project_scenario relationship removed due to missing foreign key constraints


class GridLine(Base):
    """Grid line model"""
    __tablename__ = 'grid_line'
    __table_args__ = {'schema': 'cim_vector'}
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Identification
    network_id = Column(String(100))
    line_id = Column(Integer)
    
    # Foreign keys
    project_id = Column(String(100), nullable=True)
    scenario_id = Column(String(100), nullable=True)
    
    # Spatial and properties
    geometry = Column(Geometry('LINESTRING', srid=4326), nullable=True, index=True)
    name = Column(String(255), nullable=True)
    from_bus = Column(Integer)
    to_bus = Column(Integer)
    length_km = Column(Float, nullable=True)
    max_loading_percent = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    # Note: project_scenario relationship removed due to missing foreign key constraints