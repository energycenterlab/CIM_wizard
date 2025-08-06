# PostgreSQL/PostGIS Docker Image for CIM Wizard Integrated
FROM postgis/postgis:15-3.4

# Set environment variables
ENV POSTGRES_DB=cim_wizard_integrated
ENV POSTGRES_USER=cim_wizard_user
ENV POSTGRES_PASSWORD=cim_wizard_password
ENV PGDATA=/var/lib/postgresql/data/pgdata

# Install additional tools
RUN apt-get update && apt-get install -y \
    postgresql-15-pgrouting \
    postgresql-15-postgis-3-scripts \
    && rm -rf /var/lib/apt/lists/*

# Create directories for initialization scripts
RUN mkdir -p /docker-entrypoint-initdb.d/

# Copy initialization scripts
COPY ./init-scripts/ /docker-entrypoint-initdb.d/

# Set proper permissions
RUN chmod -R 755 /docker-entrypoint-initdb.d/

# Expose PostgreSQL port
EXPOSE 5432

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD pg_isready -U $POSTGRES_USER -d $POSTGRES_DB