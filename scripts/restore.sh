#!/bin/bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <db_backup_file.sql.gz> <minio_backup_file.tar.gz>"
    exit 1
fi

DB_BACKUP=$1
MINIO_BACKUP=$2

DB_USER=${POSTGRES_USER:-postgres}
DB_NAME=${POSTGRES_DB:-sanjar_bot}
MINIO_DATA_DIR="/data/minio"

echo "🔄 Starting restoration process..."

# 1. Restore DB
if [ -f "$DB_BACKUP" ]; then
    echo "Restoring database from $DB_BACKUP..."
    # Drop and recreate DB (requires proper permissions)
    dropdb -U "$DB_USER" "$DB_NAME" --if-exists
    createdb -U "$DB_USER" "$DB_NAME"
    gunzip -c "$DB_BACKUP" | psql -U "$DB_USER" -d "$DB_NAME"
    echo "✅ Database restored."
else
    echo "❌ Database backup file not found!"
    exit 1
fi

# 2. Restore MinIO
if [ -f "$MINIO_BACKUP" ]; then
    echo "Restoring MinIO data from $MINIO_BACKUP..."
    mkdir -p "$MINIO_DATA_DIR"
    tar -xzf "$MINIO_BACKUP" -C "$MINIO_DATA_DIR"
    echo "✅ MinIO data restored."
else
    echo "⚠️ MinIO backup file not found. Skipping."
fi

echo "🎉 Restoration completed successfully."
