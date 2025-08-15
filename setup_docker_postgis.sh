#!/bin/bash

# Docker PostGIS Setup Script for CIM Wizard Integrated (Unix/Linux/macOS)
# This script sets up and starts the PostGIS database container

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "==================================================="
echo "   CIM Wizard Integrated - PostGIS Docker Setup"
echo "==================================================="
echo ""

# Check if Docker is running
echo -e "${YELLOW}[1/6] Checking Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[ERROR] Docker is not installed${NC}"
    echo "Please install Docker first"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}[ERROR] Docker is not running${NC}"
    echo "Please start Docker daemon"
        exit 1
    fi
echo -e "${GREEN}[SUCCESS] Docker is running${NC}"

# Check if docker-compose is available
echo -e "${YELLOW}[2/6] Checking Docker Compose...${NC}"
    if ! command -v docker-compose &> /dev/null; then
    # Try docker compose (newer Docker versions)
    if docker compose version &> /dev/null; then
        echo -e "${GREEN}[SUCCESS] Docker Compose is available (docker compose)${NC}"
        COMPOSE_CMD="docker compose"
    else
        echo -e "${RED}[ERROR] Docker Compose not found${NC}"
        echo "Please install Docker Compose"
        exit 1
    fi
else
    echo -e "${GREEN}[SUCCESS] Docker Compose is available${NC}"
    COMPOSE_CMD="docker-compose"
fi

# Create .env file if it doesn't exist
echo -e "${YELLOW}[3/6] Setting up environment...${NC}"
if [ ! -f ".env" ]; then
    if [ -f ".env.development" ]; then
        cp .env.development .env
        echo -e "${GREEN}[SUCCESS] Development environment file created${NC}"
    elif [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}[SUCCESS] Environment file created from example${NC}"
    else
        echo -e "${YELLOW}[WARNING] No environment template found${NC}"
        echo -e "${YELLOW}[INFO] Please create .env file manually${NC}"
    fi
else
    echo -e "${YELLOW}[INFO] Environment file already exists${NC}"
fi

# Stop existing containers
echo -e "${YELLOW}[4/6] Cleaning up existing containers...${NC}"
$COMPOSE_CMD down > /dev/null 2>&1 || true

# Build PostGIS container
echo -e "${YELLOW}[5/6] Building PostGIS container...${NC}"
if $COMPOSE_CMD build postgis; then
    echo -e "${GREEN}[SUCCESS] PostGIS container built${NC}"
else
    echo -e "${RED}[ERROR] Failed to build PostGIS container${NC}"
    exit 1
fi

# Start PostGIS container
echo -e "${YELLOW}[6/6] Starting PostGIS container...${NC}"
if $COMPOSE_CMD up postgis -d; then
    echo -e "${GREEN}[SUCCESS] PostGIS container started${NC}"
else
    echo -e "${RED}[ERROR] Failed to start PostGIS container${NC}"
    exit 1
fi

# Wait for database to be ready
echo ""
echo -e "${YELLOW}Waiting for database to be ready...${NC}"
attempts=0
max_attempts=30

while [ $attempts -lt $max_attempts ]; do
    if $COMPOSE_CMD ps | grep -q "healthy"; then
        echo -e "${GREEN}[SUCCESS] PostGIS is healthy${NC}"
        break
    fi
    
    attempts=$((attempts + 1))
    if [ $attempts -eq $max_attempts ]; then
        echo -e "${RED}[ERROR] PostGIS container did not become healthy in time${NC}"
        $COMPOSE_CMD logs postgis
        exit 1
        fi
        
        echo -n "."
        sleep 2
    done

# Test database connection
echo ""
echo -e "${YELLOW}Testing database connection...${NC}"
if docker exec cim_wizard_postgis_dev pg_isready -U cim_wizard_user -d cim_wizard_integrated &> /dev/null; then
    echo -e "${GREEN}[SUCCESS] Database connection successful${NC}"
else
    echo -e "${YELLOW}[WARNING] Database not ready, waiting...${NC}"
    sleep 5
    if docker exec cim_wizard_postgis_dev pg_isready -U cim_wizard_user -d cim_wizard_integrated &> /dev/null; then
        echo -e "${GREEN}[SUCCESS] Database connection successful${NC}"
    else
        echo -e "${RED}[ERROR] Database connection failed${NC}"
        echo "Please check Docker logs: $COMPOSE_CMD logs postgis"
        exit 1
    fi
fi

echo ""
echo "==================================================="
echo -e "${GREEN}   PostGIS Setup Complete!${NC}"
echo "==================================================="
echo ""
echo "Database Connection Details:"
echo "  Host:     localhost"
echo "  Port:     5432"
echo "  Database: cim_wizard_integrated"
echo "  Username: cim_wizard_user"
echo "  Password: cim_wizard_password"
echo ""
echo "Connection String:"
echo "  postgresql://cim_wizard_user:cim_wizard_password@localhost:5432/cim_wizard_integrated"
echo ""
echo "Available Services:"
echo "  - PostgreSQL/PostGIS: localhost:5432"
echo "  - pgAdmin (optional): http://localhost:5050"
echo "    To enable: $COMPOSE_CMD --profile tools up pgadmin -d"
echo ""
echo "Useful Commands:"
echo "  View logs:         $COMPOSE_CMD logs -f postgis"
echo "  Stop database:     $COMPOSE_CMD down"
echo "  Start database:    $COMPOSE_CMD up postgis -d"
echo "  Restart database:  $COMPOSE_CMD restart postgis"
echo "  Access psql:       docker exec -it cim_wizard_postgis_dev psql -U cim_wizard_user -d cim_wizard_integrated"
echo ""
echo "Next Steps:"
echo "  1. Test connection:     python scripts/test_docker_connection.py"
echo "  2. Populate sample data: python scripts/populate_sample_data.py"
echo "  3. Run application:     python run.py"
echo ""