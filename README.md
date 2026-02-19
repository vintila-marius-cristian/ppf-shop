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
- Luxury motion system (Cartier-style pacing, black/white/red palette):
  - `TransitionOverlay` route transitions (fade/blur + red accent wipe)
  - `HeroMotion` staggered headline and CTA entrance + pointer parallax
  - `ScrollChapters` editorial chapter reveals with rule/corner micro-effects
  - `WebGLEnhancer` progressive Three.js image warp/parallax + hero 3D moment
  - `ReducedMotionFallback` for `prefers-reduced-motion`
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
  - Dedicated analytics service proxied at `/dashboard/` in production
  - HTTP Basic Auth on dashboard (`OWNER_DASH_USERNAME`/`OWNER_DASH_PASSWORD`)
  - In production, container still binds localhost by default (`DASHBOARD_BIND=127.0.0.1:8050:8050`)
  - Dashboard widgets:
    - page views trend
    - top clicked elements
    - top visited pages
    - average scroll depth
- Social integration:
  - Facebook and Instagram brand cards/icons on Contact page
  - Optional Instagram embeds from `.env`
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
  - `/Users/cristi/eugen-website/static/js/luxury` modular animation system
  - `/Users/cristi/eugen-website/static/css/luxury.css` luxury visual overrides
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
   - Homepage hero prefers:
     - video: `/Users/cristi/eugen-website/media/client/hero-fullres.mp4`
     - fallback video: `/Users/cristi/eugen-website/media/client/video-1.mp4`
     - poster: `/Users/cristi/eugen-website/media/client/image-1.jpeg`
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
5. Open services:
   - Website: `http://localhost`
   - Analytics dashboard (basic auth): `http://localhost:8050`

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
   ./deploy/bootstrap_https.sh ppf.schrodingercat.art premiereaesthetics@gmail.com auto
   ```
   Third argument values:
   - `auto` (default): include `www.<domain>` only if DNS exists
   - `true`: force include `www.<domain>`
   - `false`: issue only for the provided domain
4. Configure renewal (cron example):
   ```cron
   0 3 * * * cd /path/to/repo && ./deploy/renew_certs.sh
   ```
5. Access analytics dashboard via URL path:
   - `https://<your-domain>/dashboard/`
   - Login with `OWNER_DASH_USERNAME`/`OWNER_DASH_PASSWORD`.

## Media Swap Guide
1. Copy optimized assets into `/Users/cristi/eugen-website/media/client`.
2. Keep the hero filenames above, or update references in `/Users/cristi/eugen-website/templates/core/home.html`.
3. For service/blog/gallery cards, upload media through model fields (fixtures or admin shell) so URLs are generated by Django media storage.
4. Use WebP/AVIF for images where possible; keep hero video H.264 `.mp4` for browser compatibility.

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
- `OWNER_DASH_USERNAME` and `OWNER_DASH_PASSWORD`
- `DASH_URL_BASE_PATHNAME` (production default: `/dashboard/`)
- `DASHBOARD_BIND` (production default: `127.0.0.1:8050:8050`)
- `FACEBOOK_PAGE_URL`, `INSTAGRAM_PROFILE_URL`, and optional `INSTAGRAM_EMBEDS`

## Admin Access Policy
- Django admin route is intentionally not exposed.
- Use the dedicated analytics dashboard for private statistics access.

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
