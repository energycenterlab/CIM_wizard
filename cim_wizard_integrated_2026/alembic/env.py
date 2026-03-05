"""
Alembic env.py - reads DATABASE_URL from environment and imports all
SQLAlchemy models so autogenerate can diff them against the live DB.
"""
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Ensure the project root is on sys.path so "app.*" imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.database import Base  # noqa: E402
import app.models  # noqa: E402,F401  -- registers all models with Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cim_wizard_user:cim_wizard_password@localhost:5433/cim_wizard_integrated",
)
config.set_main_option("sqlalchemy.url", DATABASE_URL)

target_metadata = Base.metadata

INCLUDE_SCHEMAS = ["cim_vector", "cim_census", "cim_raster", "cim_network"]


def include_name(name, type_, parent_names):
    if type_ == "schema":
        return name in INCLUDE_SCHEMAS
    return True


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_name=include_name,
        version_table_schema="cim_vector",
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_name=include_name,
            version_table_schema="cim_vector",
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
