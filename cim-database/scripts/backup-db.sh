#!/bin/bash
# Dump the local dockerized DB (run ON cloud3 or cloud4, not on the laptop).
#
# Usage: backup-db.sh schema|data|full|all
#
# Files land in ~/cim/cim-database/backups/ (bind-mounted as /backups).
# To copy and restore onto the other server, use the laptop scripts:
#   snapshot-c3-to-c4.sh / snapshot-c4-to-c3.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=db-backup.env
. "$ROOT/db-backup.env"

MODE="${1:-}"

usage() {
  echo "Usage: $0 schema|data|full|all" >&2
  echo "  schema  DDL only  (plain SQL .sql)" >&2
  echo "  data    rows only (custom .dump)" >&2
  echo "  full    schema+data (custom .dump)" >&2
  echo "  all     all three files" >&2
  echo "Copy/restore between C3 and C4 from the laptop, not with --push." >&2
  exit 1
}
[[ "$MODE" =~ ^(schema|data|full|all)$ ]] || usage

docker exec "$CONTAINER" pg_isready -U "$PGUSER" -d "$PGDB" >/dev/null
mkdir -p "$BACKUP_DIR"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)

dump() {
  local kind="$1" fmt="$2" ext="$3"
  shift 3
  local file="cim_${kind}_${STAMP}.${ext}"
  echo "→ ${file}" >&2
  docker exec "$CONTAINER" pg_dump \
    -U "$PGUSER" -d "$PGDB" \
    --no-owner --no-acl \
    -F "$fmt" \
    "$@" \
    -f "/backups/${file}"
  printf '%s\n' "$file"
}

FILES=()
case "$MODE" in
  schema) FILES+=("$(dump schema p sql -s)") ;;
  data)   FILES+=("$(dump data c dump -a --disable-triggers)") ;;
  full)   FILES+=("$(dump full c dump)") ;;
  all)
    FILES+=("$(dump schema p sql -s)")
    FILES+=("$(dump data c dump -a --disable-triggers)")
    FILES+=("$(dump full c dump)")
    ;;
esac

for kind in schema data full; do
  ls -1t "$BACKUP_DIR"/cim_${kind}_*.* 2>/dev/null | tail -n +$((KEEP+1)) | xargs -r rm --
done

echo "OK  ${FILES[*]}"
echo "    dir: ${BACKUP_DIR}"
