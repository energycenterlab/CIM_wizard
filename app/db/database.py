"""
Database configuration for CIM Wizard Integrated
Uses PostgreSQL with PostGIS extension
Manages three schemas: cim_vector, cim_census, cim_raster
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.settings import settings, DATABASE_URL

# Debug: Print the database URL being used
print(f"Using database URL: {DATABASE_URL}")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=settings.SHOW_SQL_QUERIES,  # Use settings for SQL query logging
    pool_pre_ping=settings.POOL_PRE_PING,
    pool_size=settings.POOL_SIZE,
    max_overflow=settings.MAX_OVERFLOW,
    pool_recycle=settings.POOL_RECYCLE
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