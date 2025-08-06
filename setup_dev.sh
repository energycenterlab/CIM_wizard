#!/bin/bash

# Development Environment Setup Script for CIM Wizard Integrated (Unix/Linux/macOS)
# This script sets up the local development environment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "==================================================="
echo "   CIM Wizard Integrated - Development Setup"
echo "==================================================="
echo ""

# Check Python installation
echo -e "${YELLOW}[1/7] Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python is not installed or not in PATH${NC}"
    echo "Please install Python 3.10 or higher"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
echo -e "${GREEN}[SUCCESS] Python ${PYTHON_VERSION} is installed${NC}"

# Check Docker
echo -e "${YELLOW}[2/7] Checking Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[ERROR] Docker is not installed${NC}"
    echo "Please install Docker and Docker Compose"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}[ERROR] Docker is not running${NC}"
    echo "Please start Docker daemon"
    exit 1
fi
echo -e "${GREEN}[SUCCESS] Docker is available${NC}"

# Create virtual environment
echo -e "${YELLOW}[3/7] Creating Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}[SUCCESS] Virtual environment created${NC}"
else
    echo -e "${YELLOW}[INFO] Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}[4/7] Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}[5/7] Upgrading pip...${NC}"
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo -e "${YELLOW}[6/7] Installing Python dependencies...${NC}"
if pip install -r requirements.txt; then
    echo -e "${GREEN}[SUCCESS] Dependencies installed${NC}"
else
    echo -e "${RED}[ERROR] Failed to install dependencies${NC}"
    exit 1
fi

# Create environment file
echo -e "${YELLOW}[7/7] Setting up environment configuration...${NC}"
if [ ! -f ".env" ]; then
    cp .env.development .env
    echo -e "${GREEN}[SUCCESS] Development environment file created${NC}"
else
    echo -e "${YELLOW}[INFO] Environment file already exists${NC}"
    echo -e "${YELLOW}[INFO] To reset, delete .env and run this script again${NC}"
fi

echo ""
echo "==================================================="
echo "   Development Setup Complete!"
echo "==================================================="
echo ""
echo "Next steps:"
echo "1. Start PostGIS database:"
echo "   docker-compose up -d"
echo ""
echo "2. Initialize database (first time only):"
echo "   python scripts/populate_sample_data.py"
echo ""
echo "3. Run the application:"
echo "   python run.py"
echo ""
echo "4. Access the application:"
echo "   - API: http://localhost:8000"
echo "   - Docs: http://localhost:8000/docs"
echo "   - pgAdmin: http://localhost:5050 (if enabled)"
echo ""
echo "To activate the virtual environment manually:"
echo "   source venv/bin/activate"
echo ""