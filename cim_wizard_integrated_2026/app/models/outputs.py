"""
Output data models for CIM Wizard Integrated
Uses outputs schema — TimescaleDB hypertables linked to building_properties

NOTE: scenario_id and building_id are UUID in the actual database even though
the vector.py models declare them as String(100). We use the pg UUID type here
to match the real column types and keep FK constraints valid.
"""

from sqlalchemy import Column, String, Integer, BigInteger, Float, DateTime, ForeignKeyConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base


class SimulationRun(Base):
    __tablename__ = 'simulation_run'
    __table_args__ = {'schema': 'outputs'}

    project_id = Column(String(100), primary_key=True)
    scenario_id = Column(UUID(as_uuid=True), primary_key=True)
    step_size_ms = Column(Integer, nullable=False)
    simulation_start = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BuildingFrassinetto3(Base):
    """Building thermal simulation output — hypertable on time_step"""
    __tablename__ = 'building_frassinetto3'
    __table_args__ = (
        ForeignKeyConstraint(
            ['scenario_id', 'building_id', 'lod'],
            ['cim_vector.cim_wizard_building_properties.scenario_id',
             'cim_vector.cim_wizard_building_properties.building_id',
             'cim_vector.cim_wizard_building_properties.lod'],
        ),
        {'schema': 'outputs'},
    )

    project_id = Column(String(100), primary_key=True)
    scenario_id = Column(UUID(as_uuid=True), primary_key=True)
    building_id = Column(UUID(as_uuid=True), primary_key=True)
    lod = Column(Integer, primary_key=True, default=0)
    time_step = Column(BigInteger, primary_key=True)
    t_building = Column(Float, nullable=True)
    heating_load_target = Column(Float, nullable=True)


class Battery(Base):
    """Battery simulation output — hypertable on time_step"""
    __tablename__ = 'battery'
    __table_args__ = (
        ForeignKeyConstraint(
            ['scenario_id', 'building_id', 'lod'],
            ['cim_vector.cim_wizard_building_properties.scenario_id',
             'cim_vector.cim_wizard_building_properties.building_id',
             'cim_vector.cim_wizard_building_properties.lod'],
        ),
        {'schema': 'outputs'},
    )

    project_id = Column(String(100), primary_key=True)
    scenario_id = Column(UUID(as_uuid=True), primary_key=True)
    building_id = Column(UUID(as_uuid=True), primary_key=True)
    lod = Column(Integer, primary_key=True, default=0)
    time_step = Column(BigInteger, primary_key=True)
    i = Column(Float, default=0)
    v = Column(Float, default=0)
    soc = Column(Float, default=0)
    p_net_batt = Column(Float, default=0)


class HeatingFrassinettoHp2(Base):
    """Heating / heat-pump simulation output — hypertable on time_step"""
    __tablename__ = 'heating_frassinetto_hp2'
    __table_args__ = (
        ForeignKeyConstraint(
            ['scenario_id', 'building_id', 'lod'],
            ['cim_vector.cim_wizard_building_properties.scenario_id',
             'cim_vector.cim_wizard_building_properties.building_id',
             'cim_vector.cim_wizard_building_properties.lod'],
        ),
        {'schema': 'outputs'},
    )

    project_id = Column(String(100), primary_key=True)
    scenario_id = Column(UUID(as_uuid=True), primary_key=True)
    building_id = Column(UUID(as_uuid=True), primary_key=True)
    lod = Column(Integer, primary_key=True, default=0)
    time_step = Column(BigInteger, primary_key=True)
    en_el = Column(Float, default=0)
    en_auxel = Column(Float, default=0)
    qt_return = Column(Float, default=0)
    cop = Column(Float, default=0)
    cr = Column(Float, default=0)
