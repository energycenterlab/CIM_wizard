# CIM Wizard Database - PostgreSQL 15 + PostGIS + TimescaleDB
# Initializes from init-db/ scripts on first startup (mounted via docker-compose)

FROM postgis/postgis:15-3.4

# Environment (can be overridden by docker-compose)
ENV POSTGRES_DB=cim_wizard_integrated
ENV POSTGRES_USER=cim_wizard_user
ENV POSTGRES_PASSWORD=cim_wizard_password
ENV PGDATA=/var/lib/postgresql/data/pgdata

# Install prerequisites, add TimescaleDB repo, then install everything
RUN apt-get update && apt-get install -y curl gnupg apt-transport-https && \
    curl -s https://packagecloud.io/install/repositories/timescale/timescaledb/script.deb.sh | bash && \
    apt-get update && apt-get install -y \
    timescaledb-2-postgresql-15 \
    postgresql-15-postgis-3 \
    postgresql-15-postgis-3-scripts \
    postgresql-15-pgrouting \
    && rm -rf /var/lib/apt/lists/*

RUN ldconfig

# Init scripts are mounted at runtime from ./init-db
# Scripts run in alphabetical order: init_backup.sql, then outputs_schema.sql
# See docker-compose.cimdb.yml volumes

EXPOSE 5432
