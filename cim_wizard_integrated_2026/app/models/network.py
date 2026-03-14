"""
Network data models for CIM Wizard Integrated
Uses cim_network schema

Structure:
- network_scenarios: grid_id (PK) for each network
- scenario_buses: links bus_id to grid_id
- scenario_lines: links line_id to grid_id
- network_buses: bus geometries and attributes
- network_lines: line geometries and attributes
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.db.database import Base


class NetworkScenario(Base):
    """Network scenario model - references a network by grid_id"""
    __tablename__ = 'network_scenarios'
    __table_args__ = {'schema': 'cim_network'}

    grid_id = Column(UUID(as_uuid=True), primary_key=True)


class ScenarioBus(Base):
    """Links bus_id to network scenario"""
    __tablename__ = 'scenario_buses'
    __table_args__ = {'schema': 'cim_network'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    grid_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    bus_id = Column(Integer, nullable=False, index=True)


class ScenarioLine(Base):
    """Links line_id to network scenario"""
    __tablename__ = 'scenario_lines'
    __table_args__ = {'schema': 'cim_network'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    grid_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    line_id = Column(Integer, nullable=False, index=True)


class NetworkBus(Base):
    """Network bus model - stores bus geometries and attributes"""
    __tablename__ = 'network_buses'
    __table_args__ = {'schema': 'cim_network'}

    bus_id = Column(Integer, primary_key=True)
    geometry = Column(Geometry('POINT', srid=4326), nullable=True, index=True)


class NetworkLine(Base):
    """Network line model - stores line geometries and attributes"""
    __tablename__ = 'network_lines'
    __table_args__ = {'schema': 'cim_network'}

    line_id = Column(Integer, primary_key=True)
    geometry = Column(Geometry('LINESTRING', srid=4326), nullable=True, index=True)
