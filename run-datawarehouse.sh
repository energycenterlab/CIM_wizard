#!/bin/bash
# Run Data Warehouse PostGIS + FastAPI via Docker Compose
# Usage: ./run-datawarehouse.sh [command]
#
# Commands:
#   up        - Start database and API (default)
#   down      - Stop database and API
#   db-up     - Start PostGIS only
#   db-down   - Stop PostGIS only
#   api-up    - Start API only (requires PostGIS running)
#   api-down  - Stop API only

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

DW_COMPOSE="datalake/api/docker-compose.yml"
DW_PROJECT="datawarehouse"

wait_for_db() {
  echo "Waiting for data warehouse database..."
  for i in {1..60}; do
    if docker exec dw_postgis pg_isready -U datalake -d datalake 2>/dev/null; then
      echo "PostGIS is ready."
      return 0
    fi
    if [ "$i" -eq 60 ]; then
      echo "Timeout waiting for PostGIS."
      return 1
    fi
    sleep 5
  done
}

cmd_db_up() {
  echo "Starting Data Warehouse PostGIS..."
  docker compose -f "$DW_COMPOSE" -p "$DW_PROJECT" up -d --build postgis
  wait_for_db
  echo ""
  echo "PostGIS running at localhost:35432 (db/user/pass: datalake)"
}

cmd_db_down() {
  echo "Stopping Data Warehouse PostGIS..."
  docker compose -f "$DW_COMPOSE" -p "$DW_PROJECT" stop postgis
  docker compose -f "$DW_COMPOSE" -p "$DW_PROJECT" rm -f postgis 2>/dev/null || true
  echo "PostGIS stopped."
}

cmd_api_up() {
  echo "Starting Data Warehouse API..."
  docker compose -f "$DW_COMPOSE" -p "$DW_PROJECT" up -d --build api
  echo ""
  echo "API running at http://localhost:8008/docs"
}

cmd_api_down() {
  echo "Stopping Data Warehouse API..."
  docker compose -f "$DW_COMPOSE" -p "$DW_PROJECT" stop api
  docker compose -f "$DW_COMPOSE" -p "$DW_PROJECT" rm -f api 2>/dev/null || true
  echo "API stopped."
}

case "${1:-up}" in
  up)
    cmd_db_up
    echo ""
    cmd_api_up
    echo ""
    echo "Data Warehouse is running:"
    echo "  PostGIS: localhost:35432"
    echo "  API docs: http://localhost:8008/docs"
    ;;
  down)
    cmd_api_down
    echo ""
    cmd_db_down
    echo ""
    echo "Data Warehouse stopped."
    ;;
  db-up)
    cmd_db_up
    ;;
  db-down)
    cmd_db_down
    ;;
  api-up)
    if ! docker exec dw_postgis pg_isready -U datalake -d datalake 2>/dev/null; then
      echo "Error: PostGIS is not running. Start it first with: ./run-datawarehouse.sh db-up"
      exit 1
    fi
    cmd_api_up
    ;;
  api-down)
    cmd_api_down
    ;;
  *)
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  up        - Start PostGIS and API (default)"
    echo "  down      - Stop PostGIS and API"
    echo "  db-up     - Start PostGIS only"
    echo "  db-down   - Stop PostGIS only"
    echo "  api-up    - Start API only (requires PostGIS)"
    echo "  api-down  - Stop API only"
    exit 1
    ;;
esac
