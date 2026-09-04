#!/bin/bash
set -euo pipefail

# Configuration
BACKUP_DIR="/var/backups/sanjar_bot"
DATE=$(date +%Y%m%d_%H%M%S)
DB_USER=${POSTGRES_USER:-postgres}
DB_NAME=${POSTGRES_DB:-sanjar_bot}
MINIO_DATA_DIR="/data/minio"
RETENTION_DAYS=30

mkdir -p "$BACKUP_DIR"

echo "🔄 Starting backup process..."

# 1. Database backup
DB_BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql.gz"
pg_dump -U "$DB_USER" -d "$DB_NAME" | gzip > "$DB_BACKUP_FILE"
echo "✅ Database backed up to $DB_BACKUP_FILE"

# 2. MinIO files backup
MINIO_BACKUP_FILE="$BACKUP_DIR/minio_backup_$DATE.tar.gz"
if [ -d "$MINIO_DATA_DIR" ]; then
    tar -czf "$MINIO_BACKUP_FILE" -C "$MINIO_DATA_DIR" .
    echo "✅ MinIO files backed up to $MINIO_BACKUP_FILE"
else
    echo "⚠️ MinIO directory not found at $MINIO_DATA_DIR. Skipping."
fi

# 3. Rotate old backups
echo "🧹 Cleaning up backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -type f -name "*.gz" -mtime +$RETENTION_DAYS -delete
echo "✅ Old backups cleaned."
echo "🎉 Backup completed successfully."
