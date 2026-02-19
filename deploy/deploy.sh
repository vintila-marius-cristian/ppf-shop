#!/usr/bin/env bash
set -euo pipefail

export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

if [[ ! -f .env ]]; then
  echo "Missing .env file. Copy .env.example to .env and update values first."
  exit 1
fi

docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
