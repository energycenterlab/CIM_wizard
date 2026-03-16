#!/bin/bash
# 3DCityDB schema + Energy ADE + Utility Network ADE initialization
# Runs BEFORE init_backup.sql (alphabetical: 00_ < init_)
# Requires: SRID env var (default 4326), POSTGRES_DB, POSTGRES_USER
set -e

echo "============================================="
echo "  3DCityDB Schema Setup"
echo "============================================="

psql=(psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB")

SRID="${SRID:-4326}"
SRS_NAME="${SRS_NAME:-urn:ogc:def:crs:EPSG::$SRID}"
CHANGELOG="${CHANGELOG:-no}"

# ── 1. Create 3DCityDB base schema ──────────────────────────────────
echo "Creating 3DCityDB schema (SRID=$SRID) ..."
if [ -f /3dcitydb/create-db.sql ]; then
    "${psql[@]}" -f /3dcitydb/create-db.sql \
        -v srid="$SRID" -v srs_name="$SRS_NAME" -v changelog="$CHANGELOG" > /dev/null
    echo "3DCityDB base schema created."
else
    echo "WARNING: /3dcitydb/create-db.sql not found. Skipping 3DCityDB base schema."
fi

# ── 2. Energy ADE ───────────────────────────────────────────────────
echo "Installing Energy ADE ..."
ENERGY_SQL="/ade/energy_ade/postgresql/CREATE_ADE_DB.sql"
if [ -f "$ENERGY_SQL" ]; then
    "${psql[@]}" -f "$ENERGY_SQL" > /dev/null 2>&1 || \
        echo "WARNING: Energy ADE SQL had errors (may be expected if already exists)"
    echo "Energy ADE installed."
else
    echo "WARNING: $ENERGY_SQL not found. Skipping Energy ADE."
fi

# ── 3. Utility Network ADE ─────────────────────────────────────────
echo "Installing Utility Network ADE ..."
UTIL_SQL="/ade/utility_network_ade/03_utility_network_ade/postgresql/CREATE_ADE_DB.sql"
if [ -f "$UTIL_SQL" ]; then
    "${psql[@]}" -f "$UTIL_SQL" > /dev/null 2>&1 || \
        echo "WARNING: Utility Network ADE SQL had errors (may be expected if already exists)"
    echo "Utility Network ADE installed."
else
    echo "WARNING: $UTIL_SQL not found. Skipping Utility Network ADE."
fi

echo "============================================="
echo "  3DCityDB setup complete"
echo "============================================="
