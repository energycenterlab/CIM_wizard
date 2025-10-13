"""
Application settings and configuration management
Uses Pydantic BaseSettings for environment variable validation and type safety
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # ====================
    # Database Configuration
    # ====================
    DATABASE_URL: str = Field(
        default="postgresql://cim_wizard_user:cim_wizard_password@localhost:5433/cim_wizard_integrated",
        description="Database connection URL"
    )
    
    # Individual database components (for flexibility)
    POSTGRES_HOST: str = Field(default="localhost", description="PostgreSQL host")
    POSTGRES_PORT: int = Field(default=5433, description="PostgreSQL port")
    POSTGRES_DB: str = Field(default="cim_wizard_integrated", description="PostgreSQL database name")
    POSTGRES_USER: str = Field(default="cim_wizard_user", description="PostgreSQL username")
    POSTGRES_PASSWORD: str = Field(default="cim_wizard_password", description="PostgreSQL password")
    
    # ====================
    # Application Settings
    # ====================
    PROJECT_NAME: str = Field(default="CIM Wizard Integrated", description="Project name")
    VERSION: str = Field(default="2.0.0", description="Application version")
    API_V1_STR: str = Field(default="/api", description="API version string")
    
    # Server settings
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    DEBUG: bool = Field(default=True, description="Debug mode")
    
    # ====================
    # Security Settings
    # ====================
    SECRET_KEY: str = Field(
        default="dev-secret-key-only-for-development",
        description="Secret key for JWT tokens"
    )
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["*"],
        description="Allowed CORS origins"
    )
    
    # ====================
    # Database Performance
    # ====================
    POOL_SIZE: int = Field(default=10, description="Database connection pool size")
    MAX_OVERFLOW: int = Field(default=20, description="Database connection pool max overflow")
    POOL_PRE_PING: bool = Field(default=True, description="Database connection pool pre-ping")
    POOL_RECYCLE: int = Field(default=3600, description="Database connection pool recycle time")
    
    # ====================
    # Development Settings
    # ====================
    RELOAD: bool = Field(default=True, description="Auto-reload on code changes")
    SHOW_SQL_QUERIES: bool = Field(default=False, description="Show SQL queries in logs")
    DOCS_ENABLED: bool = Field(default=True, description="Enable API documentation")
    
    # ====================
    # Service Configuration
    # ====================
    CENSUS_SERVICE: str = Field(default="integrated", description="Census service type")
    RASTER_SERVICE: str = Field(default="integrated", description="Raster service type")
    
    # ====================
    # Additional Settings (from .env file)
    # ====================
    LOG_LEVEL: str = Field(default="DEBUG", description="Logging level")
    CONTAINER_PREFIX: str = Field(default="cim_wizard_dev", description="Docker container prefix")
    PGADMIN_EMAIL: str = Field(default="admin@cimwizard.com", description="pgAdmin email")
    PGADMIN_PASSWORD: str = Field(default="admin", description="pgAdmin password")
    PGADMIN_PORT: str = Field(default="5050", description="pgAdmin port")
    WORKERS: str = Field(default="1", description="Number of workers")
    PROFILING_ENABLED: str = Field(default="False", description="Enable profiling")
    EXPLAIN_QUERIES: str = Field(default="False", description="Explain SQL queries")
    LOAD_SAMPLE_DATA: str = Field(default="True", description="Load sample data")
    SAMPLE_DATA_SIZE: str = Field(default="small", description="Sample data size")
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env file
        
        # Allow environment variables to override defaults
        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return (
                init_settings,
                env_settings,
                file_secret_settings,
            )


# Create global settings instance
settings = Settings()


def get_database_url() -> str:
    """Get database URL with proper fallback logic"""
    
    # Check environment variable first
    env_url = os.getenv('DATABASE_URL')
    if env_url:
        return env_url
    
    # Use the dockerized database settings
    return "postgresql://cim_wizard_user:cim_wizard_password@localhost:5433/cim_wizard_integrated"


# Export the constructed database URL
DATABASE_URL = get_database_url()
