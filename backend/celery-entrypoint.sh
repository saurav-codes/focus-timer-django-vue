#!/bin/bash
set -e

echo "🔄 Waiting for database..."
until python manage.py shell -c "from django.db import connection; connection.ensure_connection()" > /dev/null 2>&1; do
  echo "⏳ Database is unavailable - sleeping"
  sleep 1
done
echo "✅ Database is up!"

echo "🔄 Waiting for backend to be ready..."
until curl -f http://backend:8000/control-room1/ > /dev/null 2>&1; do
  echo "⏳ Backend is not ready - sleeping"
  sleep 2
done
echo "✅ Backend is ready!"

echo "🚀 Starting Celery application..."
exec "$@"
