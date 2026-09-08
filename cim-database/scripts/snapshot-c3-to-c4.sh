#!/bin/bash
# Snapshot cloud3 primary → restore onto cloud4 clone.
#
# Run from the laptop (not from cloud3). Copies C3 → this machine → C4
# because cloud3 cannot SSH to cloud4.
#
# Usage:
#   ./cim-database/scripts/snapshot-c3-to-c4.sh           # full dump (default)
#   ./cim-database/scripts/snapshot-c3-to-c4.sh full
#   ./cim-database/scripts/snapshot-c3-to-c4.sh schema
#   ./cim-database/scripts/snapshot-c3-to-c4.sh data
#
# Do not use sudo. Type the eclabuser password when SSH asks (once per host).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=cim-hosts.env
. "$ROOT/cim-hosts.env"

MODE="${1:-full}"
case "$MODE" in
  schema) FILE="cim_schema_$(date -u +%Y%m%dT%H%M%SZ).sql" ;;
  data)   FILE="cim_data_$(date -u +%Y%m%dT%H%M%SZ).dump" ;;
  full)   FILE="cim_full_$(date -u +%Y%m%dT%H%M%SZ).dump" ;;
  *)
    echo "Usage: $0 [full|schema|data]" >&2
    exit 1
    ;;
esac

mkdir -p "$LOCAL_STAGE"

ssh() { command ssh "${SSH_OPTS[@]}" "$@"; }
rsync() { command rsync -e "ssh ${SSH_OPTS[*]}" "$@"; }

echo "== dump ${MODE} on cloud3 as ${FILE} =="
ssh "$C3_SSH" "docker exec ${CONTAINER} pg_isready -U ${PGUSER} -d ${PGDB}"

case "$MODE" in
  schema)
    ssh "$C3_SSH" "docker exec ${CONTAINER} pg_dump -U ${PGUSER} -d ${PGDB} --no-owner --no-acl -Fp -s -f ${REMOTE_BACKUPS}/${FILE}"
    ;;
  data)
    ssh "$C3_SSH" "docker exec ${CONTAINER} pg_dump -U ${PGUSER} -d ${PGDB} --no-owner --no-acl -Fc -a --disable-triggers -f ${REMOTE_BACKUPS}/${FILE}"
    ;;
  full)
    ssh "$C3_SSH" "docker exec ${CONTAINER} pg_dump -U ${PGUSER} -d ${PGDB} --no-owner --no-acl -Fc -f ${REMOTE_BACKUPS}/${FILE}"
    ;;
esac

echo "== copy ${FILE}: cloud3 → laptop → cloud4 =="
rsync -avz --progress "${C3_SSH}:${C3_HOST_BACKUPS}/${FILE}" "${LOCAL_STAGE}/${FILE}"
ls -lh "${LOCAL_STAGE}/${FILE}"

ssh "$C4_SSH" "mkdir -p ${C4_HOST_BACKUPS} ${C4_ARCHIVE}"
rsync -avz --progress "${LOCAL_STAGE}/${FILE}" "${C4_SSH}:${C4_ARCHIVE}/"
ssh "$C4_SSH" "cp ${C4_ARCHIVE}/${FILE} ${C4_HOST_BACKUPS}/${FILE} && ls -lh ${C4_HOST_BACKUPS}/${FILE}"

echo "== restore ${MODE} on cloud4 =="
ssh "$C4_SSH" bash -s -- "$MODE" "$FILE" < "$ROOT/apply-dump.sh"

echo "OK  ${FILE} applied on cloud4"
echo "    archive: ${C4_SSH}:${C4_ARCHIVE}/${FILE}"
echo "    staged:  ${LOCAL_STAGE}/${FILE}"
