#!/bin/bash
# Run CIM Wizard DB and Backend via Docker Compose
# Usage: ./run-docker.sh [up|down]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

DB_COMPOSE="cim-database/docker-compose.cimdb.yml"
BACKEND_COMPOSE="cim_wizard_integrated_2026/docker-compose.backend-only.yml"

case "${1:-up}" in
  up)
    echo "Starting CIM Wizard Database..."
    docker compose -f "$DB_COMPOSE" -p cim-database up -d --build

    echo "Waiting for database to be ready..."
    for i in {1..60}; do
      if docker exec cim-integrateddb pg_isready -U cim_wizard_user -d cim_wizard_integrated 2>/dev/null; then
        echo "Database is ready."
        break
      fi
      if [ $i -eq 60 ]; then
        echo "Timeout waiting for database."
        exit 1
      fi
      sleep 5
    done

    echo "Starting CIM Wizard Backend..."
    docker compose -f "$BACKEND_COMPOSE" -p cim-backend up -d --build

    echo ""
    echo "CIM Wizard is running:"
    echo "  Database: localhost:15432"
    echo "  API docs: http://localhost:8001/docs"
    ;;
  down)
    echo "Stopping CIM Wizard Backend..."
    docker compose -f "$BACKEND_COMPOSE" -p cim-backend down 2>/dev/null || true

    echo "Stopping CIM Wizard Database..."
    docker compose -f "$DB_COMPOSE" -p cim-database down

    echo "Stopped."
    ;;
  *)
    echo "Usage: $0 [up|down]"
    echo "  up   - Start database and backend (default)"
    echo "  down - Stop database and backend"
    exit 1
    ;;
esac
