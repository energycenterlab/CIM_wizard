"""
Network data models for CIM Wizard Integrated
Uses cim_network schema

Structure:
- network_scenarios: scenario_id for each network
- scenario_buses: links bus_id to scenario_id
- scenario_lines: links line_id to scenario_id
- network_buses: bus geometries and attributes
- network_lines: line geometries and attributes
"""

from sqlalchemy import Column, Integer, String
from geoalchemy2 import Geometry
from app.db.database import Base


class NetworkScenario(Base):
    """Network scenario model - references a network by scenario_id"""
    __tablename__ = 'network_scenarios'
    __table_args__ = {'schema': 'cim_network'}

    scenario_id = Column(String(100), primary_key=True)


class ScenarioBus(Base):
    """Links bus_id to network scenario"""
    __tablename__ = 'scenario_buses'
    __table_args__ = {'schema': 'cim_network'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    scenario_id = Column(String(100), nullable=False, index=True)
    bus_id = Column(Integer, nullable=False, index=True)


class ScenarioLine(Base):
    """Links line_id to network scenario"""
    __tablename__ = 'scenario_lines'
    __table_args__ = {'schema': 'cim_network'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    scenario_id = Column(String(100), nullable=False, index=True)
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
