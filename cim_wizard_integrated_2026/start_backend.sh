#!/bin/bash
# Start script for CIM Wizard Integrated Backend

# Activate conda environment (if using conda)
# source ~/miniconda3/etc/profile.d/conda.sh
# conda activate webgis

# Or use the full path to the conda environment's Python
PYTHON_BIN="/home/ali/miniconda3/envs/webgis/bin/python3"
UVICORN_BIN="/home/ali/miniconda3/envs/webgis/bin/uvicorn"

# Set database URL
export DATABASE_URL="postgresql://cim_wizard_user:cim_wizard_password@localhost:15432/cim_wizard_integrated"

# Change to project directory
cd "$(dirname "$0")"

# Start uvicorn server
echo "Starting CIM Wizard Integrated backend..."
echo "Database: $DATABASE_URL"
echo "Server will be available at: http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

$UVICORN_BIN main:app --reload --host 0.0.0.0 --port 8000

#uvicorn main:app --reload --host 0.0.0.0 --port 8000