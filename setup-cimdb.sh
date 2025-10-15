#!/bin/bash

# CIM Database Setup Script for Ubuntu
# This script sets up the CIM database with persistent storage
# Ubuntu Machine: eclab@192.168.177.23

set -e

echo "=== CIM Database Setup Script ==="
echo "Setting up CIM database with persistent storage..."
echo "Ubuntu Machine: eclab@192.168.177.23"

# Create necessary directories
echo "Creating directories..."
mkdir -p ./data/postgres
mkdir -p ./backups
mkdir -p ./logs

# Set proper permissions
echo "Setting permissions..."
sudo chown -R 999:999 ./data/postgres  # PostgreSQL user in container
chmod 755 ./data/postgres
chmod 755 ./backups
chmod 755 ./logs

# Pull the latest image
echo "Pulling CIM database image..."
docker pull taherdoust/cim:vector-census-raster-sansalva-purged

# Start the database
echo "Starting CIM database..."
docker-compose -f docker-compose.cimdb.yml up -d

# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 90

# Check if database is running
echo "Checking database status..."
if docker-compose -f docker-compose.cimdb.yml ps | grep -q "Up"; then
    echo "✅ Database is running successfully!"
    
    # Test connection
    echo "Testing database connection..."
    docker exec cim-database pg_isready -U cim_wizard_user -d cim_wizard_integrated
    
    # Show some basic info
    echo "Database connection info:"
    echo "  Host: localhost"
    echo "  Port: 5432"
    echo "  Database: cim_wizard_integrated"
    echo "  Username: cim_wizard_user"
    echo "  Password: cim_wizard_password"
    
    # Show data summary
    echo "Checking data..."
    docker exec cim-database psql -U cim_wizard_user -d cim_wizard_integrated -c "
    SELECT 
        schemaname,
        relname as tablename,
        n_tup_ins as row_count
    FROM pg_stat_user_tables 
    WHERE schemaname LIKE 'cim_%'
    ORDER BY schemaname, relname;
    "
    
    echo ""
    echo "OK! Setup complete! Your CIM database is ready."
    echo "You can now connect from pgAdmin using the connection info above."
    
else
    echo "XXX Database failed to start. Check logs:"
    docker-compose -f docker-compose.cimdb.yml logs
    exit 1
fi
