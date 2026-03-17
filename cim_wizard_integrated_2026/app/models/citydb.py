"""
3DCityDB v4 data models for CIM Wizard Integrated
Uses the ``citydb`` schema created by the 3DCityDB init scripts.

These models map to tables that already exist in the database; they are
NOT created by SQLAlchemy's ``Base.metadata.create_all()``.  Only the
columns actively used by CIM Wizard are declared here -- the underlying
tables have many more columns that 3DCityDB manages internally.
"""

from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    Float,
    Numeric,
    String,
    Text,
    DateTime,
    ForeignKey,
    Sequence,
    func,
)
from geoalchemy2 import Geometry
from app.db.database import Base

# ── Sequences (defined by 3DCityDB create-db.sql) ────────────────────

citymodel_seq = Sequence("citymodel_seq", schema="citydb")
cityobject_seq = Sequence("cityobject_seq", schema="citydb")
surface_geometry_seq = Sequence("surface_geometry_seq", schema="citydb")
cityobject_genericattrib_seq = Sequence(
    "cityobject_genericattrib_seq", schema="citydb"
)


# ── CityModel ────────────────────────────────────────────────────────


class CityModel(Base):
    """Root container for a collection of CityObjects (CityGML CityModel)."""

    __tablename__ = "citymodel"
    __table_args__ = {"schema": "citydb"}

    id = Column(BigInteger, citymodel_seq, primary_key=True)
    gmlid = Column(String(256))
    name = Column(String(1000))
    name_codespace = Column(String(4000))
    description = Column(String(4000))
    envelope = Column(Geometry("GEOMETRY", srid=4326), nullable=True)
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    last_modification_date = Column(DateTime(timezone=True))
    lineage = Column(String(256))


# ── CityObject ───────────────────────────────────────────────────────


class CityObject(Base):
    """Abstract root for every feature in 3DCityDB (buildings, surfaces,
    installations, etc.).  ``objectclass_id`` determines the concrete type."""

    __tablename__ = "cityobject"
    __table_args__ = {"schema": "citydb"}

    id = Column(BigInteger, cityobject_seq, primary_key=True)
    objectclass_id = Column(Integer, nullable=False)
    gmlid = Column(String(256))
    gmlid_codespace = Column(String(1000))
    name = Column(String(1000))
    name_codespace = Column(String(4000))
    description = Column(String(4000))
    envelope = Column(Geometry("GEOMETRY", srid=4326), nullable=True)
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    termination_date = Column(DateTime(timezone=True))
    last_modification_date = Column(DateTime(timezone=True))
    lineage = Column(String(256))
    xml_source = Column(Text)


# ── CityObject Member (CityModel <-> CityObject link) ───────────────


class CityObjectMember(Base):
    """Many-to-many link between CityModel and CityObject."""

    __tablename__ = "cityobject_member"
    __table_args__ = {"schema": "citydb"}

    citymodel_id = Column(
        BigInteger,
        ForeignKey("citydb.citymodel.id"),
        primary_key=True,
    )
    cityobject_id = Column(
        BigInteger,
        ForeignKey("citydb.cityobject.id"),
        primary_key=True,
    )


# ── Building ─────────────────────────────────────────────────────────


class CityBuilding(Base):
    """CityGML Building / BuildingPart (objectclass_id 26 / 25).
    Shares the same ``id`` as the parent CityObject row."""

    __tablename__ = "building"
    __table_args__ = {"schema": "citydb"}

    id = Column(
        BigInteger,
        ForeignKey("citydb.cityobject.id"),
        primary_key=True,
    )
    building_parent_id = Column(BigInteger, nullable=True)
    building_root_id = Column(BigInteger, nullable=True)
    objectclass_id = Column(Integer)

    measured_height = Column(Float, nullable=True)
    measured_height_unit = Column(String(4000))
    storeys_above_ground = Column(Numeric, nullable=True)
    storeys_below_ground = Column(Numeric, nullable=True)

    # LOD geometry FK references into surface_geometry
    lod0_footprint_id = Column(BigInteger, nullable=True)
    lod0_roofprint_id = Column(BigInteger, nullable=True)
    lod1_multi_surface_id = Column(BigInteger, nullable=True)
    lod2_multi_surface_id = Column(BigInteger, nullable=True)
    lod3_multi_surface_id = Column(BigInteger, nullable=True)
    lod4_multi_surface_id = Column(BigInteger, nullable=True)
    lod1_solid_id = Column(BigInteger, nullable=True)
    lod2_solid_id = Column(BigInteger, nullable=True)
    lod3_solid_id = Column(BigInteger, nullable=True)
    lod4_solid_id = Column(BigInteger, nullable=True)


# ── Thematic Surface ─────────────────────────────────────────────────


class ThematicSurface(Base):
    """CityGML boundary surface (Wall=34, Roof=33, Ground=35, etc.).
    Shares the same ``id`` as the parent CityObject row."""

    __tablename__ = "thematic_surface"
    __table_args__ = {"schema": "citydb"}

    id = Column(
        BigInteger,
        ForeignKey("citydb.cityobject.id"),
        primary_key=True,
    )
    objectclass_id = Column(Integer, nullable=False)
    building_id = Column(
        BigInteger,
        ForeignKey("citydb.building.id"),
        nullable=True,
    )
    room_id = Column(BigInteger, nullable=True)
    building_installation_id = Column(BigInteger, nullable=True)

    lod2_multi_surface_id = Column(BigInteger, nullable=True)
    lod3_multi_surface_id = Column(BigInteger, nullable=True)
    lod4_multi_surface_id = Column(BigInteger, nullable=True)


# ── Surface Geometry ─────────────────────────────────────────────────


class SurfaceGeometry(Base):
    """Hierarchical geometry storage for all CityGML surfaces and solids."""

    __tablename__ = "surface_geometry"
    __table_args__ = {"schema": "citydb"}

    id = Column(BigInteger, surface_geometry_seq, primary_key=True)
    gmlid = Column(String(256))
    gmlid_codespace = Column(String(1000))
    parent_id = Column(BigInteger, nullable=True)
    root_id = Column(BigInteger, nullable=True)
    is_solid = Column(Numeric, default=0)
    is_composite = Column(Numeric, default=0)
    is_triangulated = Column(Numeric, default=0)
    is_xlink = Column(Numeric, default=0)
    is_reverse = Column(Numeric, default=0)
    solid_geometry = Column(Geometry("GEOMETRY", srid=4326), nullable=True)
    geometry = Column(Geometry("GEOMETRY", srid=4326), nullable=True)
    cityobject_id = Column(
        BigInteger,
        ForeignKey("citydb.cityobject.id"),
        nullable=True,
    )


# ── Generic Attributes ───────────────────────────────────────────────


class CityObjectGenericAttrib(Base):
    """Arbitrary key-value attributes attached to a CityObject.
    ``datatype``: 1=STRING, 2=INTEGER, 3=REAL, 4=URI, 5=DATE, 6=MEASURE."""

    __tablename__ = "cityobject_genericattrib"
    __table_args__ = {"schema": "citydb"}

    id = Column(BigInteger, cityobject_genericattrib_seq, primary_key=True)
    parent_genattrib_id = Column(BigInteger, nullable=True)
    root_genattrib_id = Column(BigInteger, nullable=True)
    attrname = Column(String(256), nullable=False)
    datatype = Column(Numeric, nullable=False)
    strval = Column(String(4000), nullable=True)
    intval = Column(Integer, nullable=True)
    realval = Column(Float, nullable=True)
    urival = Column(String(4000), nullable=True)
    dateval = Column(DateTime(timezone=True), nullable=True)
    unit = Column(String(4000), nullable=True)
    cityobject_id = Column(
        BigInteger,
        ForeignKey("citydb.cityobject.id"),
        nullable=True,
    )
