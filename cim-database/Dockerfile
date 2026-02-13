FROM taherdoust/cim:vector-census-raster-sansalva-purged

# Copy the database backup to initialization directory
# PostgreSQL will automatically run .sql files in this directory on first startup
COPY backups/init_with_raster.sql /docker-entrypoint-initdb.d/

# Set proper permissions
USER root
RUN chmod 644 /docker-entrypoint-initdb.d/init_with_raster.sql

# Switch back to postgres user
USER postgres