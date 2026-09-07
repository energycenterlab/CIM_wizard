#!/bin/bash
# Copy init_backup.sql and pv/ to server (for populating the dockerized DB)
# Requires: sshpass (sudo apt install sshpass)
# WARNING: init_backup.sql is ~2.1 GB - transfer may take several minutes

set -e

# SERVER_USER="eclabuser"
# SERVER_HOST="130.192.238.11"
# SERVER_PASS="Cl0udThr332021!"
SERVER_USER="eclabuser"
SERVER_HOST="130.192.238.12"
SERVER_PASS="Cl0udF0ur2021!"
REMOTE_DIR="~/cim"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v sshpass &>/dev/null; then
  echo "Error: sshpass is required. Install it with:"
  echo "  sudo apt install sshpass"
  exit 1
fi

echo "Copying init_backup.sql and pv/ to ${SERVER_USER}@${SERVER_HOST}..."
echo "(init_backup.sql is ~2.1 GB - this may take several minutes)"
echo ""

# Copy init_backup.sql
if [ -f "cim-database/init-db/init_backup.sql" ]; then
  echo "Copying init_backup.sql..."
  sshpass -p "$SERVER_PASS" rsync -avz --progress \
    -e "ssh -o StrictHostKeyChecking=no" \
    cim-database/init-db/init_backup.sql \
    "${SERVER_USER}@${SERVER_HOST}:${REMOTE_DIR}/cim-database/init-db/"
  echo "init_backup.sql copied."
else
  echo "Warning: cim-database/init-db/init_backup.sql not found. Skipping."
fi

# Copy pv folder (scripts + geojson)
if [ -d "pv" ]; then
  echo ""
  echo "Copying pv/..."
  sshpass -p "$SERVER_PASS" rsync -avz --progress \
    -e "ssh -o StrictHostKeyChecking=no" \
    pv/ "${SERVER_USER}@${SERVER_HOST}:${REMOTE_DIR}/pv/"
  echo "pv/ copied."
else
  echo "Warning: pv/ folder not found. Skipping."
fi

echo ""
echo "Done. To populate the server DB:"
echo "  1. SSH: ssh ${SERVER_USER}@${SERVER_HOST}"
echo "  2. cd ~/cim && ./run-docker.sh down"
echo "  3. cd cim-database && docker compose -f docker-compose.cimdb.yml down -v"
echo "  4. docker compose -f docker-compose.cimdb.yml up -d"
echo "  5. cd ~/cim && ./run-docker.sh backend-up"
echo ""
echo "To load PV data (after DB is up):"
echo "  cd ~/cim/pv/scripts"
echo "  DATABASE_URL='postgresql://cim_wizard_user:cim_wizard_password@localhost:15432/cim_wizard_integrated' python load_pv_geojson.py"
echo ""
