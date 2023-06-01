#!/bin/bash

# wait for PSQL server to start
sleep 10

# Generate new migration files
echo "Generating new migration files..."
python manage.py makemigrations

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# collect static files
python manage.py collectstatic --no-input

# Start the Django development server
# echo "Starting Django development server..."
# python manage.py runserver 0.0.0.0:8000

# Start the Gunicorn development server
echo "Starting Gunicorn development server..."
gunicorn griot_backend.wsgi:application
