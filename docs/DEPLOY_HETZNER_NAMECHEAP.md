# Hetzner + Namecheap Deployment Guide (`schrodingercat.art`)

This guide deploys the Dockerized stack (`web`, `db`, `dashboard`, `nginx`) on a Hetzner Ubuntu server with HTTPS via Let's Encrypt.

## 1) DNS in Namecheap
In Namecheap Advanced DNS for `schrodingercat.art`, create:
- `A` record: Host `@` -> Value `<YOUR_HETZNER_SERVER_IP>`
- `A` record: Host `www` -> Value `<YOUR_HETZNER_SERVER_IP>`

Wait for DNS propagation.

## 2) Server bootstrap on Hetzner (Ubuntu 22.04/24.04)
SSH into server:
```bash
ssh root@<YOUR_HETZNER_SERVER_IP>
```

Install Docker + Compose plugin:
```bash
apt update && apt upgrade -y
apt install -y ca-certificates curl gnupg git ufw
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" \
  > /etc/apt/sources.list.d/docker.list

apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable docker
systemctl start docker
```

Firewall:
```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
```

## 3) Clone repository and configure environment
```bash
mkdir -p /opt/schrodingercat
cd /opt/schrodingercat
# replace with your git remote once pushed
git clone <YOUR_GIT_REMOTE_URL> app
cd app
cp .env.example .env
```

Edit `.env` (must set):
- `DEBUG=False`
- `SECRET_KEY=<strong-random-secret>`
- `POSTGRES_PASSWORD=<strong-random-password>`
- `DATABASE_URL=postgresql://premiere:<POSTGRES_PASSWORD>@db:5432/premiereaesthetics`
- `ALLOWED_HOSTS=schrodingercat.art,www.schrodingercat.art`
- `CSRF_TRUSTED_ORIGINS=https://schrodingercat.art,https://www.schrodingercat.art`
- `SITE_URL=https://schrodingercat.art`
- `DJANGO_SECURE_SSL=True`
- `OWNER_DASH_USERNAME=<your-dashboard-username>`
- `OWNER_DASH_PASSWORD=<strong-dashboard-password>`
- `DASHBOARD_BIND=127.0.0.1:8050:8050` (keeps analytics private on server localhost)

## 4) Start production stack
```bash
cd /opt/schrodingercat/app
./deploy/deploy.sh
```

## 5) Issue SSL certificate and switch nginx to TLS config
```bash
cd /opt/schrodingercat/app
./deploy/bootstrap_https.sh schrodingercat.art premiereaesthetics@gmail.com
```

## 6) Load initial content
```bash
docker compose -f docker-compose.prod.yml exec web python manage.py loaddata core/fixtures/initial_data.json
docker compose -f docker-compose.prod.yml exec web python manage.py bootstrap_site
```

## 7) Verify
- https://schrodingercat.art
- https://www.schrodingercat.art
- Django admin is intentionally not exposed (`/admin/` should return 404).

Access analytics dashboard (private, separate app):
1. From your local machine, open an SSH tunnel:
   ```bash
   ssh -L 8050:127.0.0.1:8050 root@<YOUR_HETZNER_SERVER_IP>
   ```
2. Open:
   - http://127.0.0.1:8050
3. Authenticate with:
   - `OWNER_DASH_USERNAME`
   - `OWNER_DASH_PASSWORD`

## 8) Enable automatic cert renewal
```bash
crontab -e
```
Add:
```cron
0 3 * * * cd /opt/schrodingercat/app && ./deploy/renew_certs.sh >/var/log/cert_renew.log 2>&1
```

## 9) Optional hardening
- Create non-root deployment user and run Docker from that user.
- Keep system packages updated (`apt upgrade -y`).
- Restrict SSH by key-only auth.
- Add daily DB backups via `pg_dump` in cron.
