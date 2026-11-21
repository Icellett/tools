"""Validated environment-based Django settings for TutBerry."""
import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

def required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ImproperlyConfigured(f"Missing required environment variable: {name}")
    return value

SECRET_KEY = required("DJANGO_SECRET_KEY")
DATABASE_URL = required("DATABASE_URL")
DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}
if DATABASES["default"]["ENGINE"] != "django.db.backends.postgresql":
    raise ImproperlyConfigured("DATABASE_URL must be PostgreSQL")
DEBUG_VALUE = os.getenv("DJANGO_DEBUG", "false").lower()
if DEBUG_VALUE not in {"true", "false"}:
    raise ImproperlyConfigured("DJANGO_DEBUG must be true or false")
DEBUG = DEBUG_VALUE == "true"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()
if LOG_LEVEL not in {"debug", "info", "warning", "error"}:
    raise ImproperlyConfigured("Invalid LOG_LEVEL")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
ROOT_URLCONF = "tutberry.urls"
INSTALLED_APPS = ["django.contrib.auth", "django.contrib.contenttypes", "rest_framework", "tutberry"]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "tutberry.middleware.NoStoreMiddleware",
    "tutberry.middleware.RequestLoggingMiddleware",
]
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
        ]},
    }
]
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "tutberry.api_errors.api_exception_handler",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
    ],
}
