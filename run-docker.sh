#!/bin/bash
# Run CIM Wizard DB and Backend via Docker Compose
# Usage: ./run-docker.sh [command]
#
# Commands:
#   up        - Start database and backend (default)
#   down      - Stop database and backend
#   db-up     - Start database only
#   db-down   - Stop database only
#   backend-up   - Start backend only (requires DB running)
#   backend-down - Stop backend only

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

DB_COMPOSE="cim-database/docker-compose.cimdb.yml"
BACKEND_COMPOSE="cim_wizard_integrated_2026/docker-compose.backend-only.yml"

wait_for_db() {
  echo "Waiting for database to be ready..."
  for i in {1..60}; do
    if docker exec cim-integrateddb pg_isready -U cim_wizard_user -d cim_wizard_integrated 2>/dev/null; then
      echo "Database is ready."
      return 0
    fi
    if [ $i -eq 60 ]; then
      echo "Timeout waiting for database."
      return 1
    fi
    sleep 5
  done
}

cmd_db_up() {
  echo "Starting CIM Wizard Database..."
  docker compose -f "$DB_COMPOSE" -p cim-database up -d --build
  wait_for_db
  echo ""
  echo "Database running at localhost:15432"
}

cmd_db_down() {
  echo "Stopping CIM Wizard Database..."
  docker compose -f "$DB_COMPOSE" -p cim-database down
  echo "Database stopped."
}

cmd_backend_up() {
  echo "Starting CIM Wizard Backend..."
  docker compose -f "$BACKEND_COMPOSE" -p cim-backend up -d --build
  echo ""
  echo "Backend running:"
  echo "  API docs: http://localhost:8001/docs"
}

cmd_backend_down() {
  echo "Stopping CIM Wizard Backend..."
  docker compose -f "$BACKEND_COMPOSE" -p cim-backend down 2>/dev/null || true
  echo "Backend stopped."
}

case "${1:-up}" in
  up)
    cmd_db_up
    echo ""
    cmd_backend_up
    echo ""
    echo "CIM Wizard is running:"
    echo "  Database: localhost:15432"
    echo "  API docs: http://localhost:8001/docs"
    ;;
  down)
    cmd_backend_down
    echo ""
    cmd_db_down
    echo ""
    echo "CIM Wizard stopped."
    ;;
  db-up)
    cmd_db_up
    ;;
  db-down)
    cmd_db_down
    ;;
  backend-up)
    if ! docker exec cim-integrateddb pg_isready -U cim_wizard_user -d cim_wizard_integrated 2>/dev/null; then
      echo "Error: Database is not running. Start it first with: ./run-docker.sh db-up"
      exit 1
    fi
    cmd_backend_up
    ;;
  backend-down)
    cmd_backend_down
    ;;
  *)
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  up           - Start database and backend (default)"
    echo "  down         - Stop database and backend"
    echo "  db-up        - Start database only"
    echo "  db-down      - Stop database only"
    echo "  backend-up   - Start backend only (requires DB running)"
    echo "  backend-down - Stop backend only"
    exit 1
    ;;
esac
