"""
Vector data models for CIM Wizard Integrated
Uses cim_vector schema
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, BigInteger, func
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.db.database import Base


class ProjectScenario(Base):
    """Project scenario model"""
    __tablename__ = 'project_scenario'
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
    
    # Additional fields
    cosimulator_config_mongo_path = Column(String, nullable=True)
    network_mongo_path = Column(JSON, nullable=True)
    results_mongo_path = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    building_properties = relationship("BuildingProperties", back_populates="project_scenario")
    grid_buses = relationship("GridBus", back_populates="project_scenario")
    grid_lines = relationship("GridLine", back_populates="project_scenario")


class Building(Base):
    """Building model"""
    __tablename__ = 'building'
    __table_args__ = {'schema': 'cim_vector'}
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Building identification
    building_id = Column(String(100), nullable=False, index=True)
    lod = Column(Integer, default=0)
    
    # Spatial data
    building_geometry = Column(Geometry('GEOMETRY', srid=4326), index=True)
    building_geometry_source = Column(String(50), default='osm')
    
    # Census link
    census_id = Column(BigInteger, nullable=True, index=True)
    
    # LoD 1.2 data
    building_surfaces_lod12 = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    properties = relationship("BuildingProperties", back_populates="building")


class BuildingProperties(Base):
    """Building properties model"""
    __tablename__ = 'building_properties'
    __table_args__ = {'schema': 'cim_vector'}
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Composite identification
    building_id = Column(String(100), nullable=False, index=True)
    project_id = Column(String(100), ForeignKey('cim_vector.project_scenario.project_id'))
    scenario_id = Column(String(100), ForeignKey('cim_vector.project_scenario.scenario_id'))
    lod = Column(Integer, default=0)
    
    # Foreign key to Building
    building_fk = Column(Integer, ForeignKey('cim_vector.building.id'))
    
    # Physical properties
    height = Column(Float, nullable=True)
    area = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    number_of_floors = Column(Float, nullable=True)
    
    # Building characteristics
    type = Column(String(50), nullable=True)
    const_period_census = Column(String(10), nullable=True)
    const_year = Column(Integer, nullable=True)
    const_TABULA = Column(String(15), nullable=True)
    
    # Demographics
    n_people = Column(Integer, nullable=True)
    n_family = Column(Integer, nullable=True)
    
    # Additional properties
    gross_floor_area = Column(Float, nullable=True)
    net_leased_area = Column(Float, nullable=True)
    neighbours_surfaces = Column(JSON, nullable=True)
    neighbours_ids = Column(JSON, nullable=True)
    
    # Energy properties
    heating = Column(Boolean, nullable=True)
    cooling = Column(Boolean, nullable=True)
    w2w = Column(Float, nullable=True)
    hvac_type = Column(String(50), nullable=True)
    
    # Extra properties
    extra_prop = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    building = relationship("Building", back_populates="properties")
    project_scenario = relationship("ProjectScenario", 
                                  foreign_keys=[project_id, scenario_id],
                                  primaryjoin="and_(BuildingProperties.project_id==ProjectScenario.project_id, "
                                           "BuildingProperties.scenario_id==ProjectScenario.scenario_id)",
                                  back_populates="building_properties")


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
    project_id = Column(String(100), ForeignKey('cim_vector.project_scenario.project_id'))
    scenario_id = Column(String(100), ForeignKey('cim_vector.project_scenario.scenario_id'))
    
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
    project_scenario = relationship("ProjectScenario",
                                  foreign_keys=[project_id, scenario_id],
                                  primaryjoin="and_(GridBus.project_id==ProjectScenario.project_id, "
                                           "GridBus.scenario_id==ProjectScenario.scenario_id)",
                                  back_populates="grid_buses")


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
    project_id = Column(String(100), ForeignKey('cim_vector.project_scenario.project_id'))
    scenario_id = Column(String(100), ForeignKey('cim_vector.project_scenario.scenario_id'))
    
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
    project_scenario = relationship("ProjectScenario",
                                  foreign_keys=[project_id, scenario_id],
                                  primaryjoin="and_(GridLine.project_id==ProjectScenario.project_id, "
                                           "GridLine.scenario_id==ProjectScenario.scenario_id)",
                                  back_populates="grid_lines")