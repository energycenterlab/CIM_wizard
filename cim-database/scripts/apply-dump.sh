#!/bin/bash
# Apply a dump that already sits in the container bind-mount /backups.
# Invoked on cloud3 or cloud4, not on the laptop:
#   ssh eclabuser@host bash -s -- full cim_full_....dump < apply-dump.sh
set -euo pipefail

MODE="${1:?mode: schema|data|full}"
FILE="${2:?dump filename inside /backups}"
USER="${PGUSER:-cim_wizard_user}"
DB="${PGDB:-cim_wizard_integrated}"
CONTAINER="${CONTAINER:-cim-integrateddb}"

docker exec "$CONTAINER" pg_isready -U "$USER" -d postgres >/dev/null

recreate() {
  docker exec "$CONTAINER" psql -U "$USER" -d postgres -v ON_ERROR_STOP=1 -c \
    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${DB}' AND pid <> pg_backend_pid();" \
    >/dev/null
  docker exec "$CONTAINER" psql -U "$USER" -d postgres -c "DROP DATABASE IF EXISTS ${DB};"
  docker exec "$CONTAINER" psql -U "$USER" -d postgres -c "CREATE DATABASE ${DB} OWNER ${USER};"
}

case "$MODE" in
  full)
    recreate
    docker exec "$CONTAINER" pg_restore -U "$USER" -d "$DB" \
      --no-owner --no-acl --exit-on-error "/backups/${FILE}"
    ;;
  schema)
    recreate
    docker exec "$CONTAINER" psql -U "$USER" -d "$DB" -v ON_ERROR_STOP=1 \
      -f "/backups/${FILE}"
    ;;
  data)
    docker exec "$CONTAINER" pg_restore -U "$USER" -d "$DB" \
      --no-owner --no-acl --data-only --disable-triggers --exit-on-error \
      "/backups/${FILE}"
    ;;
  *)
    echo "Unknown mode: $MODE" >&2
    exit 1
    ;;
esac

echo "OK  restored ${MODE} from ${FILE}"
