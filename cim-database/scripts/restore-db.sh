#!/bin/bash
# Restore a dump into the local dockerized DB (run ON cloud3 or cloud4).
#
# Usage: restore-db.sh schema|data|full FILE
# FILE is a host path under backups/ or any readable path (copied into backups/).
#
# full  drops and recreates the database, then pg_restore
# schema same, then loads DDL
# data  loads rows only (schema must already exist)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=db-backup.env
. "$ROOT/db-backup.env"

MODE="${1:-}"
FILE="${2:-}"
[[ "$MODE" =~ ^(schema|data|full)$ && -n "$FILE" ]] || {
  echo "Usage: $0 schema|data|full FILE" >&2
  exit 1
}

[[ -f "$FILE" ]] || FILE="$BACKUP_DIR/$(basename "$FILE")"
[[ -f "$FILE" ]] || { echo "File not found: $FILE" >&2; exit 1; }

NAME=$(basename "$FILE")
mkdir -p "$BACKUP_DIR"
if [[ "$(realpath "$FILE")" != "$(realpath "$BACKUP_DIR")/${NAME}" ]]; then
  cp -v "$FILE" "$BACKUP_DIR/$NAME"
fi

echo "WARNING: restore ${MODE} of ${NAME} into ${CONTAINER} / ${PGDB} on $(hostname)"
read -r -p "Type YES to continue: " ok
[[ "$ok" == "YES" ]] || exit 1

"$ROOT/apply-dump.sh" "$MODE" "$NAME"
