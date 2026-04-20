FROM mongodb/mongodb-community-server:latest

# Copy init scripts — MongoDB runs these automatically
# on first startup (only when data volume is empty)
COPY init/ /docker-entrypoint-initdb.d/

# Default port
EXPOSE 27017