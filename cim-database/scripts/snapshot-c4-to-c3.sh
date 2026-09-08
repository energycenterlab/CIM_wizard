#!/bin/bash
# Restore cloud4 clone → cloud3 primary. DESTRUCTIVE on cloud3.
#
# Run from the laptop. Copies C4 → this machine → C3 (no nested SSH).
#
# Usage:
#   ./cim-database/scripts/snapshot-c4-to-c3.sh
#
# You must type YES to continue. Stop writers (backends) first if you can.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=cim-hosts.env
. "$ROOT/cim-hosts.env"

FILE="cim_full_$(date -u +%Y%m%dT%H%M%SZ)_from_c4.dump"

echo "This REPLACES the live database on cloud3 (${C3_SSH}) with a snapshot of cloud4."
read -r -p "Type YES to continue: " ok
[[ "$ok" == "YES" ]] || exit 1

mkdir -p "$LOCAL_STAGE"

ssh() { command ssh "${SSH_OPTS[@]}" "$@"; }
rsync() { command rsync -e "ssh ${SSH_OPTS[*]}" "$@"; }

echo "== dump full on cloud4 as ${FILE} =="
ssh "$C4_SSH" "docker exec ${CONTAINER} pg_isready -U ${PGUSER} -d ${PGDB}"
ssh "$C4_SSH" "docker exec ${CONTAINER} pg_dump -U ${PGUSER} -d ${PGDB} --no-owner --no-acl -Fc -f ${REMOTE_BACKUPS}/${FILE}"

echo "== copy ${FILE}: cloud4 → laptop → cloud3 =="
rsync -avz --progress "${C4_SSH}:${C4_HOST_BACKUPS}/${FILE}" "${LOCAL_STAGE}/${FILE}"
ls -lh "${LOCAL_STAGE}/${FILE}"

ssh "$C3_SSH" "mkdir -p ${C3_HOST_BACKUPS}"
rsync -avz --progress "${LOCAL_STAGE}/${FILE}" "${C3_SSH}:${C3_HOST_BACKUPS}/"

echo "== restore full on cloud3 =="
ssh "$C3_SSH" bash -s -- full "$FILE" < "$ROOT/apply-dump.sh"

echo "OK  cloud3 now matches cloud4 snapshot ${FILE}"
