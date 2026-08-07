"""The search query engine.

`run_search()` is the single entry point shared by every search surface. It
tokenises the raw query for as-you-type prefix matching, scores rows by the
greater of FTS rank and trigram-name similarity (so short/typo'd names still
match), and returns results grouped by type, each group ranked and capped, with
groups ordered by their strongest match.
"""

import re

from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    TrigramWordSimilarity,
)
from django.db.models import F, Q
from django.db.models.functions import Greatest

from .models import SearchDocument

# Human labels for each result group. Insertion order is also the fixed display
# order of the groups (guides, components, blocks, icons).
TYPE_LABELS = {
    SearchDocument.TYPE_GUIDE: "Guides",
    SearchDocument.TYPE_COMPONENT: "Components",
    SearchDocument.TYPE_BLOCK: "Blocks",
    SearchDocument.TYPE_ICON: "Icons",
}
TYPE_ORDER = list(TYPE_LABELS)

# Trigram similarity above this counts as a fuzzy/name match.
SIM_THRESHOLD = 0.3

# Characters that carry meaning in a raw tsquery — strip them from user tokens.
_TSQUERY_OPERATORS = re.compile(r"[&|!():*<>\\'\"]+")


def _tokenise(query: str) -> list[str]:
    """Whitespace tokens with FTS operators stripped; empties dropped."""
    tokens = []
    for raw in query.split():
        cleaned = _TSQUERY_OPERATORS.sub("", raw).strip()
        if cleaned:
            tokens.append(cleaned)
    return tokens


def _raw_tsquery(tokens: list[str]) -> str:
    """`["kbd", "co"]` -> `kbd & co:*` (prefix match on the in-progress token)."""
    parts = list(tokens)
    parts[-1] = parts[-1] + ":*"
    return " & ".join(parts)


def run_search(query: str, cap: int | None = None, type: str | None = None):
    """Search `query`, grouped by type.

    Returns a list of group dicts ordered by each group's top score:
        [{"type", "label", "results": [SearchDocument, ...], "total", "capped"}]
    Empty groups are omitted. `cap` limits results per group (with `total`/
    `capped` reflecting the pre-cap count). `type` restricts to one document type.
    """
    tokens = _tokenise(query or "")
    if not tokens:
        return []

    sq = SearchQuery(_raw_tsquery(tokens), search_type="raw", config="english")

    qs = SearchDocument.objects.all()
    if type:
        qs = qs.filter(type=type)

    qs = (
        qs.annotate(
            rank=SearchRank(F("search_vector"), sq),
            sim=TrigramWordSimilarity(query, "search_name"),
        )
        .annotate(score=Greatest(F("rank"), F("sim")) * (1 + F("weight")))
        .filter(Q(search_vector=sq) | Q(sim__gte=SIM_THRESHOLD))
        .order_by("-score")
    )

    # Bucket rows into groups, preserving the global -score order within each.
    buckets: dict[str, list[SearchDocument]] = {}
    for doc in qs:
        buckets.setdefault(doc.type, []).append(doc)

    groups = []
    for doc_type, rows in buckets.items():
        # Guide rows include per-heading records that the UI nests under their
        # page, so the user-facing count is distinct pages, not rows.
        if doc_type == SearchDocument.TYPE_GUIDE:
            total = len({(r.metadata or {}).get("page_url", r.url) for r in rows})
        else:
            total = len(rows)
        shown = rows[:cap] if cap else rows
        groups.append(
            {
                "type": doc_type,
                "label": TYPE_LABELS.get(doc_type, doc_type.title()),
                "results": shown,
                "total": total,
                "capped": bool(cap) and len(rows) > cap,
                "top_score": rows[0].score if rows else 0,
            }
        )

    # Fixed group order: guides, components, blocks, icons.
    groups.sort(
        key=lambda g: TYPE_ORDER.index(g["type"]) if g["type"] in TYPE_ORDER else 99
    )
    return groups
