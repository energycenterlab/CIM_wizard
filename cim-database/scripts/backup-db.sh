#!/bin/bash
# Usage: backup-db.sh schema|data|full|all [--push]
set -euo pipefail
. "$(dirname "$0")/db-backup.env"

MODE="${1:-}"
PUSH=0
[[ "${2:-}" == "--push" ]] && PUSH=1

usage() {
  echo "Usage: $0 schema|data|full|all [--push]"
  echo "  schema  DDL only  (plain SQL .sql)"
  echo "  data    rows only (custom .dump)"
  echo "  full    schema+data (custom .dump)"
  echo "  all     all three files"
  echo "  --push  rsync new file(s) to cloud4"
  exit 1
}
[[ "$MODE" =~ ^(schema|data|full|all)$ ]] || usage

docker exec "$CONTAINER" pg_isready -U "$PGUSER" -d "$PGDB" >/dev/null
mkdir -p "$BACKUP_DIR"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)

dump() {
  local kind="$1" fmt="$2" extra="$3" ext="$4"
  local file="cim_${kind}_${STAMP}.${ext}"
  echo "→ ${file}"
  docker exec "$CONTAINER" pg_dump \
    -U "$PGUSER" -d "$PGDB" \
    --no-owner --no-acl \
    -F "$fmt" $extra \
    -f "/backups/${file}"
  echo "$file"
}

FILES=()
case "$MODE" in
  schema) FILES+=("$(dump schema p '-s' sql)") ;;
  data)   FILES+=("$(dump data   c '-a --disable-triggers' dump)") ;;
  full)   FILES+=("$(dump full   c '' dump)") ;;
  all)
    FILES+=("$(dump schema p '-s' sql)")
    FILES+=("$(dump data   c '-a --disable-triggers' dump)")
    FILES+=("$(dump full   c '' dump)")
    ;;
esac

# prune old files of each kind
for kind in schema data full; do
  ls -1t "$BACKUP_DIR"/cim_${kind}_*.* 2>/dev/null | tail -n +$((KEEP+1)) | xargs -r rm --
done

if [[ "$PUSH" -eq 1 ]]; then
  ssh -o StrictHostKeyChecking=accept-new "${REMOTE%%:*}" "mkdir -p ~/cim-db-backups/cloud3"
  for f in "${FILES[@]}"; do
    rsync -avz "$BACKUP_DIR/$f" "$REMOTE"
  done
fi

echo "OK  ${FILES[*]}"