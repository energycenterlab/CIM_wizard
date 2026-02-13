#!/bin/bash
# Quick backup script for CIM Wizard Database
# Usage: ./create_backup.sh [full|schema|census]

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CONTAINER="cim-integrateddb"
USER="cim_wizard_user"
DB="cim_wizard_integrated"

# Create backups directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "=========================================="
echo "CIM Wizard Database Backup Utility"
echo "=========================================="

# Determine backup type
BACKUP_TYPE=${1:-full}

case $BACKUP_TYPE in
  full)
    echo "Creating FULL database backup..."
    FILENAME="cim_wizard_full_backup_${TIMESTAMP}.dump"
    
    # Create backup inside container
    sudo docker exec -t $CONTAINER pg_dump -U $USER -d $DB -F c -f /tmp/$FILENAME
    
    # Copy to host
    sudo docker cp $CONTAINER:/tmp/$FILENAME $BACKUP_DIR/
    
    # Clean up inside container
    sudo docker exec -t $CONTAINER rm /tmp/$FILENAME
    
    echo "✓ Full backup saved: $BACKUP_DIR/$FILENAME"
    ;;
    
  schema)
    echo "Creating SCHEMA-ONLY backup..."
    FILENAME="cim_wizard_schema_${TIMESTAMP}.sql"
    
    # Create schema backup
    sudo docker exec -t $CONTAINER pg_dump -U $USER -d $DB --schema-only -f /tmp/$FILENAME
    
    # Copy to host
    sudo docker cp $CONTAINER:/tmp/$FILENAME $BACKUP_DIR/
    
    # Clean up
    sudo docker exec -t $CONTAINER rm /tmp/$FILENAME
    
    echo "✓ Schema backup saved: $BACKUP_DIR/$FILENAME"
    ;;
    
  census)
    echo "Creating CENSUS table backup..."
    FILENAME="censusgeo_backup_${TIMESTAMP}.sql"
    
    # Backup just census table
    sudo docker exec -t $CONTAINER pg_dump -U $USER -d $DB -t cim_census.censusgeo -f /tmp/$FILENAME
    
    # Copy to host
    sudo docker cp $CONTAINER:/tmp/$FILENAME $BACKUP_DIR/
    
    # Clean up
    sudo docker exec -t $CONTAINER rm /tmp/$FILENAME
    
    echo "✓ Census table backup saved: $BACKUP_DIR/$FILENAME"
    ;;
    
  *)
    echo "Error: Unknown backup type '$BACKUP_TYPE'"
    echo "Usage: $0 [full|schema|census]"
    echo ""
    echo "Options:"
    echo "  full   - Complete database backup (data + schema)"
    echo "  schema - Schema only (no data)"
    echo "  census - Just the cim_census.censusgeo table"
    exit 1
    ;;
esac

# Show file size
if [ -f "$BACKUP_DIR/$FILENAME" ]; then
    SIZE=$(du -h "$BACKUP_DIR/$FILENAME" | cut -f1)
    echo "✓ Backup size: $SIZE"
    echo "✓ Location: $(readlink -f $BACKUP_DIR/$FILENAME)"
else
    echo "✗ Backup file not found!"
    exit 1
fi

echo ""
echo "Backup completed successfully!"
echo "=========================================="

