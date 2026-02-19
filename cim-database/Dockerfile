# CIM Wizard Database - PostgreSQL 15 + PostGIS
# Initializes from init_backup.sql on first startup (mounted via docker-compose)

FROM postgis/postgis:15-3.4

# Environment (can be overridden by docker-compose)
ENV POSTGRES_DB=cim_wizard_integrated
ENV POSTGRES_USER=cim_wizard_user
ENV POSTGRES_PASSWORD=cim_wizard_password
ENV PGDATA=/var/lib/postgresql/data/pgdata

# Install PostGIS extensions, GDAL, and tools for data loading
RUN apt-get update && apt-get install -y \
    postgresql-15-postgis-3 \
    postgresql-15-postgis-3-scripts \
    postgresql-15-pgrouting \
    # gdal-bin \
    # libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

RUN ldconfig

# Init scripts are mounted at runtime from ./init-db (contains init_backup.sql)
# See docker-compose.cimdb.yml volumes

EXPOSE 5432
