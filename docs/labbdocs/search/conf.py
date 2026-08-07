"""Settings access for search, all under ``LABB_DOCS["search"]``.

Every key is optional; the defaults here are what a consumer gets by installing
``labbdocs.search`` and doing nothing else.
"""

from django.conf import settings

DEFAULT_READERS = [
    "labbdocs.search.readers.guides.GuidesReader",
    "labbdocs.search.readers.components.ComponentsReader",
    "labbdocs.search.readers.icons.IconsReader",
]


def labb_docs() -> dict:
    return getattr(settings, "LABB_DOCS", None) or {}


def search_settings() -> dict:
    return labb_docs().get("search") or {}


def doc_types() -> dict:
    return labb_docs().get("types") or {}


def reader_paths() -> list[str]:
    return search_settings().get("readers") or DEFAULT_READERS


def log_queries() -> bool:
    """Off by default: writing visitor free-text to a database is the
    consumer's call, not something installing a package decides for them."""
    return bool(search_settings().get("log_queries", False))


def category_shortcuts() -> list[dict]:
    """Blank-query browse shortcuts, shown before the user types.

    Defaults to one per declared doc type so a plain install has working
    shortcuts with no config. A consumer with surfaces beyond their doc types
    (labbio's /blocks/, say) overrides the list wholesale.
    """
    configured = search_settings().get("shortcuts")
    if configured is not None:
        return configured

    return [
        {
            "label": f"Browse {(spec.get('title') or name).lower()}",
            "href": spec.get("url_prefix") or "/",
            "icon": spec.get("search_icon") or "rmx.book-2",
        }
        for name, spec in doc_types().items()
        if (spec or {}).get("url_prefix")
    ]
