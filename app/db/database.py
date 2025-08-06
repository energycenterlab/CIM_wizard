"""
Database configuration for CIM Wizard Integrated
Uses PostgreSQL with PostGIS extension
Manages three schemas: cim_vector, cim_census, cim_raster
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration with Docker and local fallback
def get_database_url():
    """Get database URL with Docker PostGIS as primary and local as fallback"""
    
    # Priority 1: Environment variable (can override everything)
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")
    
    # Priority 2: Docker PostGIS (recommended for development/production)
    docker_url = "postgresql://cim_wizard_user:cim_wizard_password@localhost:5432/cim_wizard_integrated"
    
    # Priority 3: Local PostgreSQL fallback (commented but available)
    # local_url = "postgresql://postgres:postgres@localhost:5432/cim_wizard_integrated"
    
    return docker_url

DATABASE_URL = get_database_url()

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for debugging
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


# Dependency to get database session
def get_db():
    """Get database session for dependency injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all_schemas():
    """Create all required database schemas and extensions"""
    with engine.connect() as connection:
        # Create extensions
        # Possible errors: Extension already exists, insufficient privileges
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis_topology"))
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis_raster"))
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
        
        # Create schemas for different services
        schemas = ['cim_vector', 'cim_census', 'cim_raster']
        for schema in schemas:
            # Possible errors: Schema already exists, insufficient privileges
            connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
        
        connection.commit()
        print(f"Created schemas: {', '.join(schemas)}")


def get_census_db():
    """Get database session specifically for census operations"""
    # This could be configured to use a different connection if needed
    return get_db()


def get_raster_db():
    """Get database session specifically for raster operations"""
    # This could be configured to use a different connection if needed
    return get_db()


def get_vector_db():
    """Get database session specifically for vector operations"""
    # This could be configured to use a different connection if needed
    return get_db()