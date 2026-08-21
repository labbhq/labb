"""
Django settings for the block renderer test suite.
Mirrors the inline settings.configure() in blocks_dev.py serve().
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Build the synthetic vendor package and add .labb/ to sys.path before
# Django loads INSTALLED_APPS — pytest-django calls django.setup() before
# conftest.py runs, so this must happen here.
from labb.cli.handlers.blocks_dev import _build_vendor_package  # noqa: E402

_build_vendor_package(BASE_DIR, vendor="lb")
_labb_pkg_root = str(BASE_DIR / ".labb")
if _labb_pkg_root not in sys.path:
    sys.path.insert(0, _labb_pkg_root)

SECRET_KEY = "labb-test-not-for-production"
DEBUG = True

USE_TZ = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.staticfiles",
    "django_cotton",
    "labb",
    "labbicons",
    "lb",
]

MIDDLEWARE = [
    "labb.middleware.ReactivityMiddleware",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(BASE_DIR / ".labb" / "templates")],
        "APP_DIRS": False,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
            "loaders": [
                (
                    "django_cotton.cotton_loader.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                ),
            ],
        },
    }
]

STATIC_URL = "/static/"
STATICFILES_DIRS = [str(BASE_DIR / "static")]
ROOT_URLCONF = "labb.contrib.blocks.renderer.urls"
