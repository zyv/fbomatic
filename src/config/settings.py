import os
from pathlib import Path

import dj_database_url
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if bool(os.getenv("DJANGO_DEBUG")) else False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = (
    os.environ["SECRET_KEY"] if not DEBUG else "django-insecure-)v&$w#rnu3u&t$s6q%e+oxuak&ea@bxeiz455-v321_@e2*an5"
)

if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = "DENY"

ALLOWED_HOSTS = ["*" if DEBUG else os.environ["ALLOWED_HOSTS"]]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_bootstrap5",
    "cuser",
    "reversion",
    "fbomatic",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "fbomatic.context_processors.global_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
        **({"default": "sqlite:///" + str(BASE_DIR.parent / "db.sqlite3")} if DEBUG else {}),
    )
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

TIME_ZONE = "UTC"

USE_I18N = True

LANGUAGE_CODE = "de"

LANGUAGES = [
    ("de", _("German")),
    ("en", _("English")),
]

LOCALE_PATHS = (BASE_DIR / "locale",)

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = os.getenv("STATIC_URL", "assets/")
STATIC_ROOT = os.getenv("STATIC_ROOT", BASE_DIR / "staticfiles")

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STORAGES = {
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
            if not DEBUG
            else "django.contrib.staticfiles.storage.StaticFilesStorage"
        ),
    },
}

BOOTSTRAP5 = {
    "css_url": f"{STATIC_URL}css/bootstrap.min.css",
    "javascript_url": f"{STATIC_URL}js/bootstrap.bundle.min.js",
    "horizontal_label_class": "col-sm-3",
    "horizontal_field_class": "col-sm-9",
}

if DEBUG:
    INTERNAL_IPS = ["127.0.0.1"]
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

AUTH_USER_MODEL = "cuser.CUser"
AUTHENTICATION_BACKENDS = ["fbomatic.backends.VereinsfliegerBackend"]

LOGIN_URL = reverse_lazy("fbomatic:login")
LOGIN_REDIRECT_URL = reverse_lazy("fbomatic:index")
LOGOUT_REDIRECT_URL = reverse_lazy("fbomatic:index")

VEREINSFLIEGER_APP_KEY = (
    os.environ["VEREINSFLIEGER_APP_KEY"] if not DEBUG else os.getenv("VEREINSFLIEGER_APP_KEY", "dummy")
)

REFUELING_THRESHOLD_LITERS = 50

ADMINS = [("", email) for email in os.getenv("DJANGO_ADMINS", "").split(",")]

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")

EMAIL_HOST = os.getenv("EMAIL_HOST", "localhost")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_PORT = os.getenv("EMAIL_PORT", 25)
EMAIL_USE_SSL = bool(os.getenv("EMAIL_USE_SSL", False))
EMAIL_USE_TLS = bool(os.getenv("EMAIL_USE_TLS", False))

EMAIL_SUBJECT_PREFIX = "[fbomatic] "
EMAIL_CONTENTS = "Greetings from fbomatic!"

NOTIFICATIONS_EMAIL_FROM = os.getenv("NOTIFICATIONS_EMAIL_FROM", "no-reply@localhost")
NOTIFICATIONS_EMAIL_REPLY_TO = os.getenv("NOTIFICATIONS_EMAIL_REPLY_TO")
NOTIFICATIONS_EMAIL_TO = os.getenv("NOTIFICATIONS_EMAIL_TO", "fbo@localhost")

SERVER_EMAIL = DEFAULT_FROM_EMAIL = NOTIFICATIONS_EMAIL_FROM

PROJECT_VERSION = os.getenv("PROJECT_VERSION", "unknown")

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
