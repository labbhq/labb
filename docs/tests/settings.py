"""Django settings for the labbdocs test suite.

Stands in for a consumer site: labbdocs, its optional search app, and the Cotton
template stack, with nothing site-specific. Run it with `task test:docs`.

The docs build output goes to a throwaway directory outside the repo, so a test
run never overwrites a real site's templates or doc configs.

Search stores its index in PostgreSQL and has no SQLite fallback. Point the
POSTGRES_* env vars at a server to run it. When none is reachable, conftest.py
skips the search tests instead of letting them error.
"""

import getpass
import os
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Outside the repo on purpose: DocParser wipes its build path before writing.
BUILD_DIR = Path(tempfile.gettempdir()) / "labbdocs-test-build"
CONFIG_DIR = BUILD_DIR / "doc_configs"
TEMPLATE_DIR = BUILD_DIR / "templates"

SECRET_KEY = "labbdocs-test-not-for-production"
DEBUG = True
ALLOWED_HOSTS = ["*"]

POSTGRES = {
    "NAME": os.environ.get("POSTGRES_DB", "labbdocs"),
    "USER": os.environ.get("POSTGRES_USER", ""),
    "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres"),
    "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
    "PORT": os.environ.get("POSTGRES_PORT", "5432"),
}

# With POSTGRES_USER unset, try both conventions: a container image ships the
# `postgres` superuser, a Homebrew install names the role after the OS user.
# Without this the suite skips itself on a perfectly good local server.
_USER_CANDIDATES = (
    [POSTGRES["USER"]] if POSTGRES["USER"] else ["postgres", getpass.getuser()]
)


def _search_skip_reason():
    """Empty when the search suite can run, else a one-line reason why not.

    Probed here rather than in conftest.py because `django.contrib.postgres`
    imports the driver at app-registry time: without a working Postgres there is
    nothing to install the app onto, so the whole suite would error on setup
    instead of skipping the part that needs it.
    """
    if os.environ.get("LABBDOCS_SKIP_SEARCH_TESTS"):
        return "search tests disabled by LABBDOCS_SKIP_SEARCH_TESTS"
    try:
        import psycopg
    except ImportError:
        try:
            import psycopg2 as psycopg
        except ImportError:
            return "search needs PostgreSQL and no psycopg driver is installed"
    last = ""
    for user in _USER_CANDIDATES:
        try:
            # The maintenance database, not NAME: only the server and the
            # credentials have to work, the test database is created later.
            psycopg.connect(
                host=POSTGRES["HOST"],
                port=POSTGRES["PORT"],
                user=user,
                password=POSTGRES["PASSWORD"],
                dbname="postgres",
                connect_timeout=5,
            ).close()
        except Exception as exc:
            detail = str(exc).strip().splitlines()[0] if str(exc).strip() else exc
            last = f"{user}: {detail}"
            continue
        POSTGRES["USER"] = user
        return ""
    return (
        "search needs PostgreSQL; no usable server at "
        f"{POSTGRES['HOST']}:{POSTGRES['PORT']} ({last})"
    )


SEARCH_SKIP_REASON = _search_skip_reason()

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_cotton",
    "labb",
    "labbicons",
    "labbdocs",
]

if not SEARCH_SKIP_REASON:
    INSTALLED_APPS += ["django.contrib.postgres", "labbdocs.search"]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # Decodes the Datastar signal bag; the palette view reads request.signals.
    "labb.middleware.ReactivityMiddleware",
]

ROOT_URLCONF = "tests.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATE_DIR],
        "APP_DIRS": False,  # must be False alongside custom loaders
        "OPTIONS": {
            "loaders": [
                "django_cotton.cotton_loader.Loader",
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "builtins": [
                "django_cotton.templatetags.cotton",
                "labbdocs.templatetags.docs_tags",
            ],
        },
    },
]


def _doc_type(name, title, url_prefix, **extra):
    return {
        "config": str(CONFIG_DIR / f"{name}.yaml"),
        "title": title,
        "name": name,
        "url_prefix": url_prefix,
        "template_dir": f"labbdocs/docs/{name}/",
        "build_path": str(TEMPLATE_DIR / "labbdocs" / "docs" / name),
        **extra,
    }


# The block catalogue in this repo, standing in for a consumer's installed
# blocks. tests/blocks_reader.py indexes it.
BLOCKS_ROOT = BASE_DIR.parent / "extras" / "blocks" / "blocks"

LABB_DOCS = {
    "types": {
        "ui": _doc_type("ui", "UI", "/docs/ui"),
        "guide": _doc_type("guide", "Guide", "/docs/guide"),
        "icons": _doc_type("icons", "Icons", "/docs/icons"),
        "blog": _doc_type("blog", "Blog", "/blog", menu_order="desc"),
    },
    "search": {
        # The three labbdocs ships, plus a blocks reader: blocks are a consumer
        # surface, and the search tests cover the block card and facet.
        "readers": [
            "labbdocs.search.readers.guides.GuidesReader",
            "labbdocs.search.readers.components.ComponentsReader",
            "labbdocs.search.readers.icons.IconsReader",
            "tests.blocks_reader.BlocksReader",
        ],
        # Off for a plain install; on here so the analytics and report tests
        # exercise the logging path.
        "log_queries": True,
        # Overridden because /blocks/ is a consumer surface, not a doc type.
        "shortcuts": [
            {"label": "Browse components", "href": "/docs/ui/"},
            {"label": "Browse icons", "href": "/docs/icons/"},
            {"label": "Browse blocks", "href": "/blocks/"},
            {"label": "Browse guides", "href": "/docs/guide/"},
        ],
    },
}

if SEARCH_SKIP_REASON:
    # Nothing left in the suite touches a database, but Django wants one named.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.postgresql", **POSTGRES}}

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
