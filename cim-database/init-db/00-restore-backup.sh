#!/bin/bash
# Restore db_backup.sql on first container startup
# Supports plain SQL (pg_dump -F p) and custom format (pg_dump -F c)
# NOTE: Custom format must match pg_restore version: PG 15 container needs dump from PG 15 or 16.
#       If you see "unsupported version (1.15)" - re-dump as plain SQL: pg_dump -F p -f db_backup.sql ...

set -e

BACKUP_FILE="${BACKUP_FILE:-/db/db_backup.sql}"
DB_NAME="${POSTGRES_DB:-cim_wizard_integrated}"
DB_USER="${POSTGRES_USER:-cim_wizard_user}"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "No backup file found at $BACKUP_FILE, skipping restore."
    exit 0
fi

echo "Restoring database from $BACKUP_FILE..."

# Detect format: custom dump starts with "PGDMP" magic bytes
if head -c 5 "$BACKUP_FILE" | grep -q 'PGDMP'; then
    echo "Detected pg_dump custom format, using pg_restore..."
    if ! pg_restore -U "$DB_USER" -d "$DB_NAME" --no-owner --no-acl -v "$BACKUP_FILE" 2>&1; then
        echo ""
        echo "ERROR: pg_restore failed. If you see 'unsupported version (1.15)':"
        echo "  Your backup was created with a NEWER PostgreSQL (17+) than this container (15)."
        echo "  Solution: Re-create the backup as PLAIN SQL (version-independent):"
        echo "    pg_dump -F p -f db_backup.sql -U user -d database_name"
        echo "  Then replace db/db_backup.sql and run: docker compose down -v && docker compose up -d"
        echo ""
        exit 1
    fi
else
    echo "Detected plain SQL format, using psql..."
    psql -v ON_ERROR_STOP=1 -U "$DB_USER" -d "$DB_NAME" -f "$BACKUP_FILE"
fi

echo "Database restore completed successfully."