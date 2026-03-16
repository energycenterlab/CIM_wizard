# CIM Wizard Database - PostgreSQL 15 + PostGIS + TimescaleDB + 3DCityDB
# Initializes from init-db/ scripts on first startup (mounted via docker-compose)
# 3DCityDB schema (with Energy ADE + Utility Network ADE) created via init script

# ---------------------------------------------------------------------------
# Stage 1: Extract pre-built 3DCityDB SQL scripts from the official image
# ---------------------------------------------------------------------------
FROM 3dcitydb/3dcitydb-pg:edge AS citydb-source

# ---------------------------------------------------------------------------
# Stage 2: Clone Energy ADE and Utility Network ADE repos for their SQL
# ---------------------------------------------------------------------------
FROM alpine/git:latest AS ade-source
WORKDIR /ade
RUN git clone --depth 1 https://github.com/gioagu/3dcitydb_energy_ade.git && \
    git clone --depth 1 https://github.com/gioagu/3dcitydb_ade.git

# ---------------------------------------------------------------------------
# Stage 3: Runtime image
# ---------------------------------------------------------------------------
FROM postgis/postgis:15-3.4

# Environment (can be overridden by docker-compose)
ENV POSTGRES_DB=cim_wizard_integrated
ENV POSTGRES_USER=cim_wizard_user
ENV POSTGRES_PASSWORD=cim_wizard_password
ENV PGDATA=/var/lib/postgresql/data/pgdata

# 3DCityDB configuration (SRID=4326 for WGS84 to match CIM Wizard)
ENV SRID=4326
ENV SRS_NAME=urn:ogc:def:crs:EPSG::4326

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

# Copy 3DCityDB SQL scripts from the official image
COPY --from=citydb-source /3dcitydb /3dcitydb

# Copy ADE SQL sources
COPY --from=ade-source /ade/3dcitydb_energy_ade /ade/energy_ade
COPY --from=ade-source /ade/3dcitydb_ade /ade/utility_network_ade

# Copy the 3DCityDB init script (runs alphabetically BEFORE init_backup.sql)
# Named 00_3dcitydb_init.sh so it runs first among mounted init-db/ scripts
COPY --from=citydb-source /docker-entrypoint-initdb.d/3dcitydb-initdb.sh /3dcitydb/3dcitydb-initdb.sh
RUN chmod +x /3dcitydb/3dcitydb-initdb.sh

# Init scripts are mounted at runtime from ./init-db
# Scripts run in alphabetical order via docker-entrypoint-initdb.d
# See docker-compose.cimdb.yml volumes

EXPOSE 5432
