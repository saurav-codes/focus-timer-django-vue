#!/usr/bin/env bash

# Script to restart all Focus Timer services

set -euo pipefail

# Parse options
SKIP_FRONTEND=false
for arg in "$@"; do
  case $arg in
    --skip-frontend)
      SKIP_FRONTEND=true
      ;;
  esac
done
echo "Installing backend requirements..."
.venv/bin/uv pip install -r backend/requirements.txt

echo "Applying database migrations..."
.venv/bin/python backend/manage.py migrate --noinput

echo "Collecting static files..."
.venv/bin/python backend/manage.py collectstatic --noinput
if [ "$SKIP_FRONTEND" = false ]; then
  echo "Building frontend..."
  ( cd frontend-vue && npm ci && npm run build )
else
  echo "Skipping frontend build due to --skip-frontend option"
fi

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

services=(
  gunicorn
  celery
  celery-beat
  nginx
  redis-server
  postgresql
)

for service in "${services[@]}"; do
  echo "Restarting $service..."
  sudo systemctl restart "$service"
done

echo "Waiting for services to settle..."
sleep 2

echo "Services status:"
for service in "${services[@]}"; do
  echo "===== $service ====="
  sudo systemctl status "$service" --no-pager
done

echo "All services restarted."
