#!/bin/bash
set -e

echo "🔄 Waiting for database..."
until python manage.py shell -c "from django.db import connection; connection.ensure_connection()" > /dev/null 2>&1; do
  echo "⏳ Database is unavailable - sleeping"
  sleep 1
done
echo "✅ Database is up!"

echo "🔄 Running database migrations..."
python manage.py migrate --noinput

echo "🔄 Collecting static files..."
python manage.py collectstatic --noinput

echo "🔄 Creating superuser if needed..."
SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-admin@example.com}
SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD:-admin123}

python manage.py shell <<EOF
from django.contrib.auth import get_user_model, models
User = get_user_model()
email = "${SUPERUSER_EMAIL}"
if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email,
        password="${SUPERUSER_PASSWORD}",
        first_name='Admin',
        last_name='User'
    )
    print(f"✅ Superuser created: {email} / admin123")
else:
    print(f"ℹ️ Superuser '{email}' already exists; skipping creation.")
EOF

echo "🚀 Starting application..."
exec "$@"
