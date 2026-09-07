#!/bin/bash
# Usage: restore-db.sh schema|data|full FILE
# FILE is a host path under backups/ or an absolute path.
set -euo pipefail
. "$(dirname "$0")/db-backup.env"

MODE="${1:-}"
FILE="${2:-}"
[[ "$MODE" =~ ^(schema|data|full)$ && -n "$FILE" ]] || {
  echo "Usage: $0 schema|data|full FILE"
  echo "  schema  apply DDL (plain .sql or custom .dump --schema-only)"
  echo "  data    load rows (custom .dump --data-only --disable-triggers)"
  echo "  full    drop+recreate objects then load (custom .dump --clean)"
  exit 1
}

[[ -f "$FILE" ]] || FILE="$BACKUP_DIR/$(basename "$FILE")"
[[ -f "$FILE" ]] || { echo "File not found: $FILE"; exit 1; }

NAME=$(basename "$FILE")
# copy into the bind mount if it lives elsewhere (e.g. restored from cloud4)
if [[ "$(realpath "$FILE")" != "$(realpath "$BACKUP_DIR")/"* ]]; then
  cp -v "$FILE" "$BACKUP_DIR/$NAME"
fi

echo "WARNING: restore $MODE of $NAME into $CONTAINER / $PGDB"
read -r -p "Type YES to continue: " ok
[[ "$ok" == "YES" ]] || exit 1

docker exec "$CONTAINER" pg_isready -U "$PGUSER" -d "$PGDB" >/dev/null

case "$MODE" in
  schema)
    if [[ "$NAME" == *.sql ]]; then
      docker exec -i "$CONTAINER" psql -U "$PGUSER" -d "$PGDB" -v ON_ERROR_STOP=1 \
        -f "/backups/$NAME"
    else
      docker exec "$CONTAINER" pg_restore \
        -U "$PGUSER" -d "$PGDB" --no-owner --no-acl \
        --schema-only --if-exists \
        "/backups/$NAME"
    fi
    ;;
  data)
    docker exec "$CONTAINER" pg_restore \
      -U "$PGUSER" -d "$PGDB" --no-owner --no-acl \
      --data-only --disable-triggers \
      "/backups/$NAME"
    ;;
  full)
    docker exec "$CONTAINER" pg_restore \
      -U "$PGUSER" -d "$PGDB" --no-owner --no-acl \
      --clean --if-exists \
      "/backups/$NAME"
    ;;
esac

echo "OK  restored $MODE from $NAME"