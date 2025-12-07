#!/bin/bash

echo "Starting update process..."

# 1. Pull latest code
echo "Pulling latest code..."
git pull origin main

# 2. Rebuild and restart containers
echo "Rebuilding containers..."
docker-compose -f docker-compose.prod.yml up -d --build

# 3. Run migrations
echo "Running database migrations..."
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# 4. Collect static files
echo "Collecting static files..."
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

echo "✅ Update complete! System is running."
