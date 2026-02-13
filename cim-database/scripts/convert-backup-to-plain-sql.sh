#!/bin/bash
# Convert db_backup.sql from custom format (-Fc) to plain SQL (-Fp)
# pg_restore -f outputs a script with \restrict markers - NOT valid for psql!
# This script: restore into temp PG17 -> pg_dump -F p -> true plain SQL for PG 15

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DB_DIR="$PROJECT_ROOT/db"
BACKUP="$DB_DIR/db_backup.sql"
OUTPUT="$DB_DIR/db_backup_plain.sql"
CONTAINER_NAME="pg17_convert_$$"

if [ ! -f "$BACKUP" ]; then
    echo "Error: $BACKUP not found"
    exit 1
fi

# Check if it's custom format
if ! head -c 5 "$BACKUP" | grep -q 'PGDMP'; then
    echo "File appears to be plain SQL. If you see \\restrict errors, restore original custom format first:"
    echo "  mv db/db_backup.sql db/db_backup.sql.bad && mv db/db_backup.sql.custom db/db_backup.sql"
    exit 1
fi

echo "Converting custom format to plain SQL (restore -> pg_dump)..."
echo "Input:  $BACKUP"
echo "Output: $OUTPUT"

# Cleanup on exit
cleanup() {
    docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
}
trap cleanup EXIT

# 1. Start temp PostGIS 17 (dump has PostGIS extensions)
echo "Starting temporary PostGIS 17..."
docker run -d --name "$CONTAINER_NAME" \
    -v "$DB_DIR:/db" \
    -e POSTGRES_HOST_AUTH_METHOD=trust \
    postgis/postgis:17-3.5
sleep 8

# 2. Create database and restore
echo "Restoring into temporary database..."
docker exec "$CONTAINER_NAME" psql -U postgres -c "CREATE DATABASE cim_wizard_integrated;" 2>/dev/null || true
docker exec "$CONTAINER_NAME" pg_restore -U postgres -d cim_wizard_integrated --no-owner --no-acl /db/db_backup.sql

# 3. pg_dump as plain SQL (PG 15 compatible)
echo "Creating plain SQL dump..."
docker exec "$CONTAINER_NAME" pg_dump -F p -U postgres -d cim_wizard_integrated -f /db/db_backup_plain.sql --no-owner

# 4. Remove PG 17-specific SET that PG 15 doesn't support
if grep -q "transaction_timeout" "$OUTPUT" 2>/dev/null; then
    echo "Removing PG 17-specific SET for PG 15 compatibility..."
    sed -i '/^SET transaction_timeout/d' "$OUTPUT"
fi

echo ""
echo "Conversion complete. Next steps:"
echo "  1. Backup: mv db/db_backup.sql db/db_backup.sql.custom"
echo "  2. Use:    mv db/db_backup_plain.sql db/db_backup.sql"
echo "  3. Restart: cd cim-database/cim-database && docker compose -f docker-compose.cimdb.yml down -v && docker compose -f docker-compose.cimdb.yml up -d"
