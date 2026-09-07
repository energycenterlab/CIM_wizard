#!/bin/bash
# laptop: snapshot cloud3 → files on cloud4 → optional clone DB on cloud4
set -euo pipefail
C3=eclabuser@130.192.238.11
C4=eclabuser@130.192.238.12
MODE="${1:-full}"          # schema|data|full
RESTORE_C4="${2:-}"        # pass --restore-cloud4 to rebuild cloud4 DB

STAMP=$(date -u +%Y%m%dT%H%M%SZ)
FILE="cim_${MODE}_${STAMP}.dump"
# schema uses .sql and pg_dump -Fp -s; full/data use -Fc as now

ssh "$C3" bash -s -- "$MODE" "$FILE" <<'EOS'
  set -euo pipefail
  MODE="$1"; FILE="$2"
  docker exec cim-integrateddb pg_isready -U cim_wizard_user -d cim_wizard_integrated
  docker exec cim-integrateddb pg_dump -U cim_wizard_user -d cim_wizard_integrated \
    --no-owner --no-acl -Fc -f "/backups/${FILE}"
EOS

ssh "$C4" 'mkdir -p ~/cim-db-backups/cloud3 ~/cim/cim-database/backups'
ssh "$C3" rsync -avz "~/cim/cim-database/backups/${FILE}" \
  "$C4:~/cim-db-backups/cloud3/"

if [[ "$RESTORE_C4" == "--restore-cloud4" ]]; then
  ssh "$C4" bash -s -- "$FILE" <<'EOS'
    set -euo pipefail
    FILE="$1"
    cp ~/cim-db-backups/cloud3/"$FILE" ~/cim/cim-database/backups/
    cd ~/cim
    ./run-docker.sh db-down
    cd ~/cim/cim-database
    docker compose -f docker-compose.cimdb.yml -p cim-database down
    docker volume rm cim-database_cim_postgres_data || true
    docker compose -f docker-compose.cimdb.yml -p cim-database up -d --build
    # wait until pg_isready
    docker exec cim-integrateddb pg_restore -U cim_wizard_user \
      -d cim_wizard_integrated --no-owner --no-acl --clean --if-exists \
      "/backups/${FILE}"
EOS
fi