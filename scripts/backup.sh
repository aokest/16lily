#!/bin/bash

# Define backup directory
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR

# Generate timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="db_backup_$TIMESTAMP.sql"

echo "Starting database backup..."

# Dump database
docker-compose -f docker-compose.prod.yml exec -t db pg_dump -U postgres opportunity_db > "$BACKUP_DIR/$FILENAME"

if [ $? -eq 0 ]; then
  echo "✅ Backup created successfully: $BACKUP_DIR/$FILENAME"
else
  echo "❌ Backup failed!"
  exit 1
fi
