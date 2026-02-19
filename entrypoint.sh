#!/bin/sh
set -e

if [ "${RUN_STARTUP_TASKS:-1}" = "1" ]; then
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput
fi

gunicorn premiereaesthetics.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 90
