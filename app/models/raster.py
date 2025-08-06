"""
Raster data models for CIM Wizard Integrated
Uses cim_raster schema
"""

from sqlalchemy import Column, String, Integer, DateTime, func, LargeBinary
from sqlalchemy.dialects.postgresql import BYTEA
from app.db.database import Base


class RasterModel(Base):
    """Raster data model for DTM and DSM"""
    __tablename__ = 'raster_model'
    __table_args__ = {'schema': 'cim_raster'}
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Raster data
    # Note: In production, you might want to use PostGIS raster type
    # For now using BYTEA to store raster data
    rast = Column(BYTEA, nullable=False)
    
    # Metadata
    filename = Column(String(255), nullable=False)
    raster_type = Column(String(50), nullable=False)  # 'DTM' or 'DSM'
    srid = Column(Integer, default=4326)
    
    # Raster properties
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    scale_x = Column(Float, nullable=True)
    scale_y = Column(Float, nullable=True)
    upperleft_x = Column(Float, nullable=True)
    upperleft_y = Column(Float, nullable=True)
    
    # Timestamps
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __str__(self):
        return f"{self.raster_type}: {self.filename}"


class DTMRaster(Base):
    """Digital Terrain Model raster data"""
    __tablename__ = 'dtm_raster'
    __table_args__ = {'schema': 'cim_raster'}
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # PostGIS raster field
    # In actual implementation, this would be: Column(Raster)
    # For now, storing as binary
    rast = Column(BYTEA, nullable=False)
    
    # Metadata
    filename = Column(String(255))
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Spatial reference
    srid = Column(Integer, default=4326)
    
    # Bounds
    min_elevation = Column(Float, nullable=True)
    max_elevation = Column(Float, nullable=True)
    
    def __str__(self):
        return f"DTM: {self.filename}"


class DSMRaster(Base):
    """Digital Surface Model raster data"""
    __tablename__ = 'dsm_raster'
    __table_args__ = {'schema': 'cim_raster'}
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # PostGIS raster field
    # In actual implementation, this would be: Column(Raster)
    # For now, storing as binary
    rast = Column(BYTEA, nullable=False)
    
    # Metadata
    filename = Column(String(255))
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Spatial reference
    srid = Column(Integer, default=4326)
    
    # Bounds
    min_elevation = Column(Float, nullable=True)
    max_elevation = Column(Float, nullable=True)
    
    def __str__(self):
        return f"DSM: {self.filename}"


from sqlalchemy import Float

class BuildingHeightCache(Base):
    """Cache for calculated building heights from raster data"""
    __tablename__ = 'building_height_cache'
    __table_args__ = {'schema': 'cim_raster'}
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Building identification
    building_id = Column(String(100), nullable=False, index=True)
    project_id = Column(String(100), nullable=False, index=True)
    scenario_id = Column(String(100), nullable=False, index=True)
    
    # Height values
    dtm_avg_height = Column(Float, nullable=True)
    dsm_avg_height = Column(Float, nullable=True)
    building_height = Column(Float, nullable=True)  # DSM - DTM
    
    # Calculation metadata
    calculation_date = Column(DateTime(timezone=True), server_default=func.now())
    calculation_method = Column(String(50), default='raster_intersection')
    
    # Quality indicators
    coverage_percentage = Column(Float, nullable=True)  # How much of building is covered by raster
    confidence_score = Column(Float, nullable=True)  # Confidence in the calculation
    
    def __str__(self):
        return f"Height cache for building {self.building_id}: {self.building_height}m"