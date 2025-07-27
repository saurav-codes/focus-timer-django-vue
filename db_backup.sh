#!/bin/bash
# Database backup script for focus_timer_django_vue_db

# Source environment variables from the project directory
source /home/focususer/focus-timer-django-vue/.env

# Set the backup directory
BACKUP_DIR="/home/focususer/backups"
mkdir -p "$BACKUP_DIR"

# Run the backup using environment variables
PGPASSWORD="$DATABASE_PASSWORD" pg_dump -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" -f "$BACKUP_DIR/focus_timer_django_vue_db_backup_$(date +%Y%m%d_%H%M%S).sql"

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "$(date): Database backup completed successfully" >> "$BACKUP_DIR/backup.log"
else
    echo "$(date): Database backup FAILED" >> "$BACKUP_DIR/backup.log"
fi
