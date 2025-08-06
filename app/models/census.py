"""
Census data models for CIM Wizard Integrated
Uses cim_census schema
"""

from sqlalchemy import Column, String, Integer, Float, BigInteger, func
from geoalchemy2 import Geometry
from app.db.database import Base


class CensusGeo(Base):
    """Census geographical data model"""
    __tablename__ = 'census_geo'
    __table_args__ = {'schema': 'cim_census'}
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    SEZ2011 = Column(BigInteger, unique=True, index=True)  # Census ID
    
    # Geometry
    geometry = Column(Geometry('MULTIPOLYGON', srid=4326), index=True)
    crs = Column(String(100), default="urn:ogc:def:crs:OGC:1.3:CRS84")
    
    # Census administrative attributes
    Shape_Area = Column(Float, nullable=True)
    CODREG = Column(String(10), nullable=True)
    REGIONE = Column(String(50), nullable=True)
    CODPRO = Column(String(10), nullable=True)
    PROVINCIA = Column(String(50), nullable=True)
    CODCOM = Column(String(10), nullable=True)
    COMUNE = Column(String(50), nullable=True)
    PROCOM = Column(String(10), nullable=True)
    NSEZ = Column(String(10), nullable=True)
    ACE = Column(String(10), nullable=True)
    CODLOC = Column(String(10), nullable=True)
    CODASC = Column(String(10), nullable=True)
    
    # Population attributes (P1-P66)
    P1 = Column(Integer, nullable=True)  # Total population
    P2 = Column(Integer, nullable=True)
    P3 = Column(Integer, nullable=True)
    P4 = Column(Integer, nullable=True)
    P5 = Column(Integer, nullable=True)
    P6 = Column(Integer, nullable=True)
    P7 = Column(Integer, nullable=True)
    P8 = Column(Integer, nullable=True)
    P9 = Column(Integer, nullable=True)
    P10 = Column(Integer, nullable=True)
    P11 = Column(Integer, nullable=True)
    P12 = Column(Integer, nullable=True)
    P13 = Column(Integer, nullable=True)
    P14 = Column(Integer, nullable=True)
    P15 = Column(Integer, nullable=True)
    P16 = Column(Integer, nullable=True)
    P17 = Column(Integer, nullable=True)
    P18 = Column(Integer, nullable=True)
    P19 = Column(Integer, nullable=True)
    P20 = Column(Integer, nullable=True)
    P21 = Column(Integer, nullable=True)
    P22 = Column(Integer, nullable=True)
    P23 = Column(Integer, nullable=True)
    P24 = Column(Integer, nullable=True)
    P25 = Column(Integer, nullable=True)
    P26 = Column(Integer, nullable=True)
    P27 = Column(Integer, nullable=True)
    P28 = Column(Integer, nullable=True)
    P29 = Column(Integer, nullable=True)
    P30 = Column(Integer, nullable=True)
    P31 = Column(Integer, nullable=True)
    P32 = Column(Integer, nullable=True)
    P33 = Column(Integer, nullable=True)
    P34 = Column(Integer, nullable=True)
    P35 = Column(Integer, nullable=True)
    P36 = Column(Integer, nullable=True)
    P37 = Column(Integer, nullable=True)
    P38 = Column(Integer, nullable=True)
    P39 = Column(Integer, nullable=True)
    P40 = Column(Integer, nullable=True)
    P41 = Column(Integer, nullable=True)
    P42 = Column(Integer, nullable=True)
    P43 = Column(Integer, nullable=True)
    P44 = Column(Integer, nullable=True)
    P45 = Column(Integer, nullable=True)
    P46 = Column(Integer, nullable=True)
    P47 = Column(Integer, nullable=True)
    P48 = Column(Integer, nullable=True)
    P49 = Column(Integer, nullable=True)
    P50 = Column(Integer, nullable=True)
    P51 = Column(Integer, nullable=True)
    P52 = Column(Integer, nullable=True)
    P53 = Column(Integer, nullable=True)
    P54 = Column(Integer, nullable=True)
    P55 = Column(Integer, nullable=True)
    P56 = Column(Integer, nullable=True)
    P57 = Column(Integer, nullable=True)
    P58 = Column(Integer, nullable=True)
    P59 = Column(Integer, nullable=True)
    P60 = Column(Integer, nullable=True)
    P61 = Column(Integer, nullable=True)
    P62 = Column(Integer, nullable=True)
    P64 = Column(Integer, nullable=True)
    P65 = Column(Integer, nullable=True)
    P66 = Column(Integer, nullable=True)
    P128 = Column(Integer, nullable=True)
    P129 = Column(Integer, nullable=True)
    P130 = Column(Integer, nullable=True)
    P131 = Column(Integer, nullable=True)
    P132 = Column(Integer, nullable=True)
    P135 = Column(Integer, nullable=True)
    P136 = Column(Integer, nullable=True)
    P137 = Column(Integer, nullable=True)
    P138 = Column(Integer, nullable=True)
    P139 = Column(Integer, nullable=True)
    P140 = Column(Integer, nullable=True)
    
    # Housing statistics (ST1-ST15)
    ST1 = Column(Integer, nullable=True)
    ST2 = Column(Integer, nullable=True)
    ST3 = Column(Integer, nullable=True)
    ST4 = Column(Integer, nullable=True)
    ST5 = Column(Integer, nullable=True)
    ST6 = Column(Integer, nullable=True)
    ST7 = Column(Integer, nullable=True)
    ST8 = Column(Integer, nullable=True)
    ST9 = Column(Integer, nullable=True)
    ST10 = Column(Integer, nullable=True)
    ST11 = Column(Integer, nullable=True)
    ST12 = Column(Integer, nullable=True)
    ST13 = Column(Integer, nullable=True)
    ST14 = Column(Integer, nullable=True)
    ST15 = Column(Integer, nullable=True)
    
    # Building age attributes (A2-A48)
    A2 = Column(Integer, nullable=True)
    A3 = Column(Integer, nullable=True)
    A5 = Column(Integer, nullable=True)
    A6 = Column(Integer, nullable=True)
    A7 = Column(Integer, nullable=True)
    A44 = Column(Integer, nullable=True)
    A46 = Column(Integer, nullable=True)
    A47 = Column(Integer, nullable=True)
    A48 = Column(Integer, nullable=True)
    
    # Family attributes (PF1-PF9)
    PF1 = Column(Integer, nullable=True)
    PF2 = Column(Integer, nullable=True)
    PF3 = Column(Integer, nullable=True)
    PF4 = Column(Integer, nullable=True)
    PF5 = Column(Integer, nullable=True)
    PF6 = Column(Integer, nullable=True)
    PF7 = Column(Integer, nullable=True)
    PF8 = Column(Integer, nullable=True)
    PF9 = Column(Integer, nullable=True)
    
    # Building period attributes (E1-E31)
    E1 = Column(Integer, nullable=True)
    E2 = Column(Integer, nullable=True)
    E3 = Column(Integer, nullable=True)
    E4 = Column(Integer, nullable=True)
    E5 = Column(Integer, nullable=True)
    E6 = Column(Integer, nullable=True)
    E7 = Column(Integer, nullable=True)
    E8 = Column(Integer, nullable=True)   # Buildings before 1918
    E9 = Column(Integer, nullable=True)   # Buildings 1919-1945
    E10 = Column(Integer, nullable=True)  # Buildings 1946-1960
    E11 = Column(Integer, nullable=True)  # Buildings 1961-1970
    E12 = Column(Integer, nullable=True)  # Buildings 1971-1980
    E13 = Column(Integer, nullable=True)  # Buildings 1981-1990
    E14 = Column(Integer, nullable=True)  # Buildings 1991-2000
    E15 = Column(Integer, nullable=True)  # Buildings 2001-2005
    E16 = Column(Integer, nullable=True)  # Buildings after 2005
    E17 = Column(Integer, nullable=True)
    E18 = Column(Integer, nullable=True)
    E19 = Column(Integer, nullable=True)
    E20 = Column(Integer, nullable=True)
    E21 = Column(Integer, nullable=True)
    E22 = Column(Integer, nullable=True)
    E23 = Column(Integer, nullable=True)
    E24 = Column(Integer, nullable=True)
    E25 = Column(Integer, nullable=True)
    E26 = Column(Integer, nullable=True)
    E27 = Column(Integer, nullable=True)
    E28 = Column(Integer, nullable=True)
    E29 = Column(Integer, nullable=True)
    E30 = Column(Integer, nullable=True)
    E31 = Column(Integer, nullable=True)

    def __str__(self):
        return f"Census {self.SEZ2011}"