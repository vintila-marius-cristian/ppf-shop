from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, False), DJANGO_SECURE_SSL=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="dev-only-change-in-production")
DEBUG = env.bool("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "rest_framework",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "premiereaesthetics.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.media",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.global_settings",
            ]
        },
    }
]

WSGI_APPLICATION = "premiereaesthetics.wsgi.application"
ASGI_APPLICATION = "premiereaesthetics.asgi.application"

if env("DATABASE_URL", default=""):
    DATABASES = {"default": env.db("DATABASE_URL")}
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ro-ro"
TIME_ZONE = "Europe/Bucharest"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_MAX_AGE = 31536000

MEDIA_URL = "/media/"
MEDIA_ROOT = Path(env("MEDIA_ROOT", default=str(BASE_DIR / "media")))
CLIENT_MEDIA_DIR = Path(env("CLIENT_MEDIA_DIR", default=str(BASE_DIR / "media/client")))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend" if not DEBUG else "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="premiereaesthetics@gmail.com")
CONTACT_EMAIL = env("CONTACT_EMAIL", default="premiereaesthetics@gmail.com")

SITE_URL = env("SITE_URL", default="https://schrodingercat.art")

SOCIAL_LINKS = {
    "facebook_page_url": env(
        "FACEBOOK_PAGE_URL",
        default="https://www.facebook.com/profile.php?id=100091611583430",
    ),
    "instagram_profile_url": env("INSTAGRAM_PROFILE_URL", default="https://www.instagram.com/premiere.aesthetics"),
    "instagram_embeds": [item.strip() for item in env("INSTAGRAM_EMBEDS", default="").split(",") if item.strip()],
}

ANALYTICS = {
    "plausible_domain": env("PLAUSIBLE_DOMAIN", default=""),
    "matomo_url": env("MATOMO_URL", default=""),
    "matomo_site_id": env("MATOMO_SITE_ID", default=""),
}

BUSINESS = {
    "name": env("BUSINESS_NAME", default="Programare Folie PPF Pitesti"),
    "phone": env("BUSINESS_PHONE", default="0748 113 202"),
    "email": env("BUSINESS_EMAIL", default="premiereaesthetics@gmail.com"),
    "street": env("BUSINESS_STREET", default="Sat Albota, DN65B, Nr. 465E"),
    "city": env("BUSINESS_CITY", default="Albota, Arges"),
    "postal_code": env("BUSINESS_POSTAL_CODE", default="117030"),
    "country": env("BUSINESS_COUNTRY", default="RO"),
    "hours": env("BUSINESS_HOURS", default="Mo-Sa 07:30-19:00"),
    "maps_embed": env("GOOGLE_MAPS_EMBED", default="https://www.google.com/maps?q=Sat+Albota+DN65B+Nr.+465E+117030+Arges&output=embed"),
}

SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL", default=False)
SESSION_COOKIE_SECURE = env.bool("DJANGO_SECURE_SSL", default=False)
CSRF_COOKIE_SECURE = env.bool("DJANGO_SECURE_SSL", default=False)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
X_FRAME_OPTIONS = "SAMEORIGIN"
SECURE_HSTS_SECONDS = 31536000 if env.bool("DJANGO_SECURE_SSL", default=False) else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("DJANGO_SECURE_SSL", default=False)
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_SSL", default=False)

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
}
