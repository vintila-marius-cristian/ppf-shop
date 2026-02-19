# Premiere Aesthetics Website Rebuild

Production-ready Django 4.x website for **schrodingercat.art** with a glassmorphism UI, SEO best practices, social embeds, custom event tracking, and Dockerized deployment.

## Stack
- Python 3.11
- Django 4.2 + Django REST Framework
- PostgreSQL (production), SQLite (development fallback)
- WhiteNoise + Gunicorn
- Nginx reverse proxy
- Dash analytics container (Plotly)

## Implemented Features
- Full page structure:
  - Home
  - Services index + dedicated service detail pages
  - Gallery with service filter
  - About Us
  - Blog list/detail with categories/tags
  - Contact page with server-side validation and social embeds
  - Testimonials page
- Glassmorphism design system (`.glass-card`, translucent navigation, frosted panels)
- SEO:
  - Unique metadata per page
  - OpenGraph + Twitter Card tags
  - `LocalBusiness` JSON-LD
  - `Article` JSON-LD for blog posts
  - XML sitemap (`/sitemap.xml`)
  - robots.txt (`/robots.txt`)
- Analytics:
  - Plausible or Matomo hooks (configured via `.env`)
  - Custom tracking endpoint (`/api/track/`)
  - Client-side click/page/scroll tracking (`static/js/analytics.js`)
  - Dedicated owner analytics panel:
    - login: `/owner/login/`
    - dashboard: `/owner/analytics/`
  - Dashboard widgets:
    - page views trend
    - top clicked elements
    - top visited pages
    - average scroll depth
- Social integration:
  - Facebook Page plugin embed
  - Instagram embeds from `.env`
  - Cookie notice regarding third-party embeds
- Content bootstrap:
  - Fixture data (`core/fixtures/initial_data.json`)
  - Management command to copy media and seed baseline records (`bootstrap_site`)
- Test coverage:
  - Models, forms, views, and API endpoints in `core/tests/`

## Project Structure
- `/Users/cristi/eugen-website/premiereaesthetics` Django project config
- `/Users/cristi/eugen-website/core` main app (models, views, APIs, tests)
- `/Users/cristi/eugen-website/templates` all page templates + reusable partials
- `/Users/cristi/eugen-website/static` CSS/JS assets
- `/Users/cristi/eugen-website/dashboard` Dash app for analytics visualization
- `/Users/cristi/eugen-website/nginx` local and production Nginx configs
- `/Users/cristi/eugen-website/deploy` deployment and HTTPS scripts

## Local Setup (without Docker)
1. Create environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Configure environment:
   ```bash
   cp .env.example .env
   ```
3. Place media assets:
   - Default location: `/Users/cristi/eugen-website/media/client`
   - Or set a custom source path using `CLIENT_MEDIA_DIR` in `.env`.
4. Run migrations, load fixture, and seed:
   ```bash
   python manage.py migrate
   python manage.py loaddata core/fixtures/initial_data.json
   python manage.py bootstrap_site
   ```
5. Start server:
   ```bash
   python manage.py runserver
   ```

## Docker (Development)
1. Configure `.env`:
   ```bash
   cp .env.example .env
   ```
2. Use PostgreSQL in `.env`, for example:
   ```env
   DATABASE_URL=postgresql://premiere:premierepass@db:5432/premiereaesthetics
   ```
3. Launch stack:
   ```bash
   docker compose up --build
   ```
4. Load initial content:
   ```bash
   docker compose exec web python manage.py loaddata core/fixtures/initial_data.json
   docker compose exec web python manage.py bootstrap_site
   ```

Containers provided:
- `web` (Django + Gunicorn)
- `db` (PostgreSQL)
- `dashboard` (Dash analytics app)
- `nginx` (reverse proxy + static/media)

## Production Deployment
1. Update `.env` with production values and secure secrets.
2. Build and deploy:
   ```bash
   ./deploy/deploy.sh
   ```
3. Bootstrap HTTPS certificates (Let's Encrypt):
   ```bash
   ./deploy/bootstrap_https.sh schrodingercat.art premiereaesthetics@gmail.com
   ```
4. Configure renewal (cron example):
   ```cron
   0 3 * * * cd /path/to/repo && ./deploy/renew_certs.sh
   ```

## Environment Variables
See `/Users/cristi/eugen-website/.env.example`.
Critical values:
- `SECRET_KEY`
- `DEBUG=False`
- `POSTGRES_PASSWORD`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `DATABASE_URL`
- `DJANGO_SECURE_SSL=True`
- `CONTACT_EMAIL`
- `PLAUSIBLE_DOMAIN` or `MATOMO_URL` + `MATOMO_SITE_ID`
- `FACEBOOK_PAGE_URL`, `INSTAGRAM_PROFILE_URL`, and optional `INSTAGRAM_EMBEDS`

## API Documentation
Detailed endpoint docs: `/Users/cristi/eugen-website/docs/API.md`

Deployment runbook for Hetzner + Namecheap:
- `/Users/cristi/eugen-website/docs/DEPLOY_HETZNER_NAMECHEAP.md`

## QA and Testing
Run tests:
```bash
python manage.py test
```

Recommended audits:
- Accessibility: axe/WAVE on key pages
- Performance: Lighthouse (mobile + desktop)
- Cross-browser: Chrome, Safari, Firefox, Edge

## SEO/Marketing Notes
Suggested keyword clusters integrated in content templates and seed posts:
- ppf pitesti
- folie protectie vopsea
- ceramic coating pitesti
- detailing auto premium pitesti
- folie geamuri auto omologata

Ensure NAP consistency with Google Business Profile:
- Business name
- Address
- Phone number
- Working hours

## Future Enhancements
- User portal with order history
- Appointment booking with deposits
- E-commerce catalog for detailing products
- SMS/email reminders for appointments
