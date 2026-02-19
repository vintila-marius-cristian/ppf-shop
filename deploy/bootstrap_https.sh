#!/usr/bin/env bash
set -euo pipefail

DOMAIN="${1:-schrodingercat.art}"
EMAIL="${2:-premiereaesthetics@gmail.com}"

if [[ ! -f .env ]]; then
  echo "Missing .env file. Copy .env.example to .env first."
  exit 1
fi

docker compose -f docker-compose.prod.yml -f docker-compose.prod-bootstrap.yml up -d db web dashboard nginx

docker compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot \
  --webroot-path /var/www/certbot \
  --email "$EMAIL" \
  --agree-tos \
  --no-eff-email \
  -d "$DOMAIN" -d "www.$DOMAIN"

docker compose -f docker-compose.prod.yml up -d nginx
