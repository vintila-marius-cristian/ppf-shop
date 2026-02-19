#!/usr/bin/env bash
set -euo pipefail

DOMAIN="${1:-schrodingercat.art}"
EMAIL="${2:-premiereaesthetics@gmail.com}"
INCLUDE_WWW="${3:-auto}"

if [[ ! -f .env ]]; then
  echo "Missing .env file. Copy .env.example to .env first."
  exit 1
fi

if [[ ! -f nginx/nginx.prod.conf.template || ! -f nginx/nginx.bootstrap.conf.template ]]; then
  echo "Missing nginx templates. Expected:"
  echo "  nginx/nginx.prod.conf.template"
  echo "  nginx/nginx.bootstrap.conf.template"
  exit 1
fi

resolve_host() {
  local host="$1"
  if command -v getent >/dev/null 2>&1; then
    getent ahostsv4 "$host" >/dev/null 2>&1 || getent ahostsv6 "$host" >/dev/null 2>&1
    return $?
  fi
  if command -v dig >/dev/null 2>&1; then
    [[ -n "$(dig +short "$host" A 2>/dev/null)" || -n "$(dig +short "$host" AAAA 2>/dev/null)" ]]
    return $?
  fi
  if command -v host >/dev/null 2>&1; then
    host "$host" >/dev/null 2>&1
    return $?
  fi
  return 1
}

if ! resolve_host "$DOMAIN"; then
  echo "Domain $DOMAIN does not resolve yet. Create DNS A/AAAA records first."
  exit 1
fi

WANT_WWW=0
if [[ "$INCLUDE_WWW" == "1" || "$INCLUDE_WWW" == "true" ]]; then
  WANT_WWW=1
elif [[ "$INCLUDE_WWW" == "auto" ]]; then
  if resolve_host "www.$DOMAIN"; then
    WANT_WWW=1
  else
    echo "www.$DOMAIN does not resolve in DNS; issuing certificate only for $DOMAIN"
  fi
elif [[ "$INCLUDE_WWW" != "0" && "$INCLUDE_WWW" != "false" ]]; then
  echo "Invalid INCLUDE_WWW value: $INCLUDE_WWW (expected auto|true|false)"
  exit 1
fi

if [[ "$WANT_WWW" == "1" ]] && ! resolve_host "www.$DOMAIN"; then
  echo "www.$DOMAIN does not resolve, but INCLUDE_WWW=true was requested."
  echo "Create DNS for www.$DOMAIN or rerun with INCLUDE_WWW=false."
  exit 1
fi

SERVER_NAMES="$DOMAIN"
CERT_DOMAINS=(-d "$DOMAIN")
if [[ "$WANT_WWW" == "1" ]]; then
  SERVER_NAMES="$DOMAIN www.$DOMAIN"
  CERT_DOMAINS+=(-d "www.$DOMAIN")
fi

sed \
  -e "s|__SERVER_NAMES__|$SERVER_NAMES|g" \
  -e "s|__CERT_DOMAIN__|$DOMAIN|g" \
  nginx/nginx.prod.conf.template > nginx/nginx.prod.conf

sed \
  -e "s|__SERVER_NAMES__|$SERVER_NAMES|g" \
  nginx/nginx.bootstrap.conf.template > nginx/nginx.bootstrap.conf

docker compose -f docker-compose.prod.yml -f docker-compose.prod-bootstrap.yml up -d db web dashboard nginx

docker compose -f docker-compose.prod.yml run --rm --entrypoint /bin/sh certbot -c \
  "mkdir -p /var/www/certbot/.well-known/acme-challenge && echo ok > /var/www/certbot/.well-known/acme-challenge/healthcheck.txt"

if ! curl -fsS --max-time 15 "http://$DOMAIN/.well-known/acme-challenge/healthcheck.txt" >/dev/null; then
  echo "HTTP challenge preflight failed for $DOMAIN."
  echo "Check DNS, firewall (port 80), and reverse proxy before retrying."
  exit 1
fi

docker compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot \
  --webroot-path /var/www/certbot \
  --email "$EMAIL" \
  --agree-tos \
  --no-eff-email \
  "${CERT_DOMAINS[@]}"

docker compose -f docker-compose.prod.yml up -d nginx
