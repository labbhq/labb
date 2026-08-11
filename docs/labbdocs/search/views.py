from urllib.parse import urlencode

from django.shortcuts import render
from django.urls import reverse

from labb.signals import Signals, Str

from .conf import category_shortcuts, log_queries
from .models import SearchDocument, SearchQueryLog
from .services import TYPE_LABELS, run_search, search_counts

# A type facet is the uncapped surface a group's See-all points at.
PALETTE_GROUP_CAP = 5
PAGE_GROUP_CAP = 50

# Facet rail order (after the leading "All" facet).
FACET_TYPES = [
    SearchDocument.TYPE_GUIDE,
    SearchDocument.TYPE_COMPONENT,
    SearchDocument.TYPE_BLOCK,
    SearchDocument.TYPE_ICON,
]
VALID_TYPES = set(FACET_TYPES)


class SearchPageSignals(Signals):
    """Shareable /search state. Clean query keys `?q=` and `?type=` map onto the
    `search.*` signal namespace (kept separate from the global palette's `q`
    signal, which is also on this page). A Datastar request carries the whole
    bag; a cold/shared link carries only these keys, read back via `from_query`.
    """

    q = Str(path="search.q", query="q", default="")
    doc_type = Str(path="search.type", query="type", default="")


def _facet_href(q, doc_type):
    """Reversed, never assumed: the consumer chooses where search is mounted."""
    params = {"q": q}
    if doc_type:
        params["type"] = doc_type
    return f"{reverse('labbdocs_search:page')}?{urlencode(params)}"


def search_page(request):
    """Server-rendered /search page: grouped results, a type-facet rail, and a
    shareable `?q=&type=` URL. Renders identically for a cold/shared GET (no
    Datastar header — rehydrated via `from_query`) and a reactive morph.

    Each group shows `PAGE_GROUP_CAP` and links to its own type facet, which
    shows the rest up to the engine's hard ceiling.
    """
    signals = (
        SearchPageSignals(request)
        if request.signals
        else SearchPageSignals.from_query(request)
    )
    q = (signals.q or "").strip()
    active_type = signals.doc_type if signals.doc_type in VALID_TYPES else ""

    # Untyped, so the rail shows every total even while filtered to one type.
    counts = search_counts(q) if q else {}
    total_count = sum(counts.values())
    groups = []
    if q:
        cap = None if active_type else PAGE_GROUP_CAP
        groups = run_search(q, cap=cap, type=active_type or None)

    if log_queries() and q and not request.is_datastar:
        SearchQueryLog.objects.create(
            query=q[:255],
            result_count=total_count,
            has_results=total_count > 0,
        )

    facets = [
        {
            "type": "",
            "label": "All",
            "count": total_count,
            "href": _facet_href(q, ""),
            "behavior": "" if active_type else "active",
        }
    ]
    for doc_type in FACET_TYPES:
        facets.append(
            {
                "type": doc_type,
                "label": TYPE_LABELS[doc_type],
                "count": counts.get(doc_type, 0),
                "href": _facet_href(q, doc_type),
                "behavior": "active" if doc_type == active_type else "",
            }
        )

    active_label = TYPE_LABELS[active_type] if active_type else "All"

    return render(
        request,
        "labbdocs/search/page.html",
        {
            "signals": signals,
            "q": q,
            "groups": groups,
            "facets": facets,
            "active_type": active_type,
            "active_label": active_label,
            "shortcuts": category_shortcuts(),
            "has_query": bool(q),
            "has_results": total_count > 0,
            "canonical_url": (
                _facet_href(q, active_type) if q else reverse("labbdocs_search:page")
            ),
        },
    )


def palette(request):
    """⌘K palette results fragment.

    Driven by the debounced reactive GET from the global palette overlay: the
    query lives in ``request.signals`` (``?datastar={"q": ...}``); a plain ``?q=``
    is also accepted for the no-JS/test path. Returns a minimal document whose
    ONLY top-level element is ``#search-palette-results`` — Datastar's default
    outer-morph then updates just that region and leaves the open dialog shell
    (never re-sent) untouched, so the palette can't flicker shut mid-search.

    Deliberately does NOT log to ``SearchQueryLog``: an as-you-type surface would
    record every prefix ("b", "bu", "but", ...) and drown the zero-result signal.
    The submitted ``/search`` query is the meaningful analytics event.
    """
    q = (request.signals.get("q") or request.GET.get("q") or "").strip()
    groups = run_search(q, cap=PALETTE_GROUP_CAP) if q else []
    return render(
        request,
        "labbdocs/search/palette_results.html",
        {
            "q": q,
            "groups": groups,
            "shortcuts": category_shortcuts(),
            "has_query": bool(q),
            "no_results": bool(q) and not groups,
        },
    )
