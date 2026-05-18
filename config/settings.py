import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _
import dj_database_url
import os


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


BASE_DIR = Path(__file__).resolve().parent.parent


# =========================
# ADMIN SECURITY SETTINGS
# =========================

ADMIN_PROTECTED_PATH = os.environ.get(
    "ADMIN_PROTECTED_PATH",
    "/rotaya-control-panel-92x7/"
)

ADMIN_MAX_FAILED_LOGIN_ATTEMPTS = int(
    os.environ.get("ADMIN_MAX_FAILED_LOGIN_ATTEMPTS", 5)
)

ADMIN_LOGIN_BLOCK_MINUTES = int(
    os.environ.get("ADMIN_LOGIN_BLOCK_MINUTES", 30)
)


# =========================
# CORE SETTINGS
# =========================

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-local-dev-key-change-this"
)

DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1,.onrender.com,rotaya.co,www.rotaya.co"
).split(",")

CSRF_TRUSTED_ORIGINS = os.environ.get(
    "CSRF_TRUSTED_ORIGINS",
    "https://*.onrender.com,https://rotaya.co,https://www.rotaya.co"
).split(",")

# =========================
# APPLICATIONS
# =========================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core.apps.CoreConfig",
]


# =========================
# MIDDLEWARE
# =========================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # Static files for production
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "core.middleware.BlockedIPMiddleware",
    "core.middleware.AdminBlockedIPMiddleware",
]


ROOT_URLCONF = "config.urls"


# =========================
# TEMPLATES
# =========================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",

                "core.context_processors.navbar_categories",
                "core.context_processors.payment_settings",

                "django.template.context_processors.media",
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"


# =========================
# DATABASE
# Render PostgreSQL uses DATABASE_URL
# Local fallback: sqlite3
# =========================

if os.environ.get("DATABASE_URL"):

    DATABASES = {
        "default": dj_database_url.config(
            conn_max_age=600,
            ssl_require=True,
        )
    }

else:

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# =========================
# PASSWORD VALIDATION
# =========================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# =========================
# LANGUAGE / TIMEZONE
# =========================

LANGUAGE_CODE = "tr"

LANGUAGES = [
    ("tr", _("Turkish")),
]

TIME_ZONE = "Europe/Istanbul"

USE_I18N = True
USE_TZ = True


# =========================
# STATIC FILES
# =========================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "core/static",
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"


# =========================
# MEDIA FILES
# Render Disk path
# =========================
# =========================
# MEDIA FILES
# =========================

MEDIA_URL = "/media/"

if os.environ.get("RENDER"):
    MEDIA_ROOT = "/var/data/media"
else:
    MEDIA_ROOT = BASE_DIR / "media"

# =========================
# SECURITY - PRODUCTION
# =========================

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    X_FRAME_OPTIONS = "DENY"
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"


# =========================
# DEFAULT PK
# =========================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
