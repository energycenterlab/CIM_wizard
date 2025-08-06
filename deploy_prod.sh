#!/bin/bash

# Production Deployment Script for CIM Wizard Integrated (Unix/Linux/macOS)
# This script deploys the application and database using Docker

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "==================================================="
echo "   CIM Wizard Integrated - Production Deployment"
echo "==================================================="
echo ""

# Check if Docker is running
echo -e "${YELLOW}[1/7] Checking Docker...${NC}"
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
echo -e "${YELLOW}[2/7] Checking Docker Compose...${NC}"
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
echo -e "${YELLOW}[3/7] Setting up environment...${NC}"
if [ ! -f ".env" ]; then
    if [ -f ".env.production" ]; then
        cp .env.production .env
        echo -e "${GREEN}[SUCCESS] Production environment file created${NC}"
    else
        echo -e "${RED}[ERROR] .env.production file not found${NC}"
        echo "Please create .env.production with your production settings"
        exit 1
    fi
else
    echo -e "${YELLOW}[WARNING] Environment file already exists${NC}"
    read -p "Overwrite with production settings? (y/N): " overwrite
    if [[ "$overwrite" =~ ^[Yy]$ ]]; then
        cp .env.production .env
        echo -e "${GREEN}[SUCCESS] Production environment applied${NC}"
    else
        echo -e "${YELLOW}[INFO] Using existing environment${NC}"
    fi
fi

# Stop existing containers
echo -e "${YELLOW}[4/7] Stopping existing containers...${NC}"
$COMPOSE_CMD -f docker-compose.prod.yml down > /dev/null 2>&1 || true

# Build containers
echo -e "${YELLOW}[5/7] Building containers...${NC}"
if $COMPOSE_CMD -f docker-compose.prod.yml build; then
    echo -e "${GREEN}[SUCCESS] Containers built${NC}"
else
    echo -e "${RED}[ERROR] Failed to build containers${NC}"
    exit 1
fi

# Start services
echo -e "${YELLOW}[6/7] Starting services...${NC}"
if $COMPOSE_CMD -f docker-compose.prod.yml up -d; then
    echo -e "${GREEN}[SUCCESS] Services started${NC}"
else
    echo -e "${RED}[ERROR] Failed to start services${NC}"
    exit 1
fi

# Wait for services to be healthy
echo -e "${YELLOW}[7/7] Waiting for services to be ready...${NC}"
attempts=0
max_attempts=30

while [ $attempts -lt $max_attempts ]; do
    if $COMPOSE_CMD -f docker-compose.prod.yml ps | grep -q "healthy"; then
        echo ""
        echo -e "${GREEN}[SUCCESS] All services are healthy${NC}"
        break
    fi
    
    attempts=$((attempts + 1))
    if [ $attempts -eq $max_attempts ]; then
        echo -e "${RED}[ERROR] Services did not become healthy in time${NC}"
        $COMPOSE_CMD -f docker-compose.prod.yml logs
        exit 1
    fi
    
    echo -n "."
    sleep 2
done

# Test application endpoint
echo ""
echo -e "${YELLOW}Testing application endpoint...${NC}"
sleep 5
if curl -f http://localhost:8000/docs &> /dev/null; then
    echo -e "${GREEN}[SUCCESS] Application is responding${NC}"
else
    echo -e "${YELLOW}[WARNING] Application may still be starting up${NC}"
    echo "Please check http://localhost:8000/docs manually"
fi

echo ""
echo "==================================================="
echo -e "${GREEN}   Production Deployment Complete!${NC}"
echo "==================================================="
echo ""
echo "Services Running:"
echo "  - Application:       http://localhost:8000"
echo "  - API Documentation: http://localhost:8000/docs"
echo "  - PostGIS Database:  localhost:5432"
echo ""
echo "To enable optional services:"
echo "  - pgAdmin:  $COMPOSE_CMD -f docker-compose.prod.yml --profile tools up pgadmin -d"
echo "  - Nginx:    $COMPOSE_CMD -f docker-compose.prod.yml --profile proxy up nginx -d"
echo ""
echo "Management Commands:"
echo "  View logs:    $COMPOSE_CMD -f docker-compose.prod.yml logs -f"
echo "  Stop all:     $COMPOSE_CMD -f docker-compose.prod.yml down"
echo "  Restart all:  $COMPOSE_CMD -f docker-compose.prod.yml restart"
echo "  View status:  $COMPOSE_CMD -f docker-compose.prod.yml ps"
echo ""
echo "Database Backup:"
echo "  docker exec cim_wizard_postgis_prod pg_dump -U cim_wizard_user cim_wizard_integrated > backup.sql"
echo ""
echo "Database Restore:"
echo "  docker exec -i cim_wizard_postgis_prod psql -U cim_wizard_user cim_wizard_integrated < backup.sql"
echo ""