#!/bin/bash

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create superuser if not exists
echo "Creating superuser..."
python manage.py create_admin --discord-id admin --username admin --email admin@example.com --password admin123

# Start server
echo "Starting server..."
exec "$@"