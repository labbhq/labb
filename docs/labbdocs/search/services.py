"""The search query engine.

`run_search()` is the single entry point shared by every search surface. It
tokenises the raw query for as-you-type prefix matching, scores rows by the
greater of FTS rank and trigram-name similarity (so short/typo'd names still
match), and returns results grouped by type in a fixed group order, each group
counted by aggregate and limited in the database.
"""

import re

from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    TrigramWordSimilarity,
)
from django.db.models import Count, F, Q, TextField
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Coalesce, Greatest

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

MAX_QUERY_CHARS = 200
MAX_QUERY_TOKENS = 12

# A backstop against a one-letter prefix, not a display cap.
MAX_GROUP_RESULTS = 500

# Characters that carry meaning in a raw tsquery — strip them from user tokens.
_TSQUERY_OPERATORS = re.compile(r"[&|!():*<>\\'\"]+")


def _tokenise(query: str) -> list[str]:
    """Whitespace tokens with FTS operators stripped; empties dropped."""
    tokens = []
    for raw in query.split():
        cleaned = _TSQUERY_OPERATORS.sub("", raw).strip()
        if cleaned:
            tokens.append(cleaned)
        if len(tokens) == MAX_QUERY_TOKENS:
            break
    return tokens


def _raw_tsquery(tokens: list[str]) -> str:
    """`["kbd", "co"]` -> `kbd & co:*` (prefix match on the in-progress token)."""
    parts = list(tokens)
    parts[-1] = parts[-1] + ":*"
    return " & ".join(parts)


def _matches(query: str, type: str | None = None):
    """Scored, filtered queryset for `query`, or None when there is nothing to
    search for. Unordered and unsliced — callers add their own."""
    query = (query or "")[:MAX_QUERY_CHARS]
    tokens = _tokenise(query)
    if not tokens:
        return None

    sq = SearchQuery(_raw_tsquery(tokens), search_type="raw", config="english")

    qs = SearchDocument.objects.all()
    if type:
        qs = qs.filter(type=type)

    return (
        qs.annotate(
            rank=SearchRank(F("search_vector"), sq),
            sim=TrigramWordSimilarity(query, "search_name"),
        )
        .annotate(score=Greatest(F("rank"), F("sim")) * (1 + F("weight")))
        .filter(Q(search_vector=sq) | Q(sim__gte=SIM_THRESHOLD))
    )


def _row_counts(qs) -> dict[str, int]:
    """`{type: matching row count}` as a single GROUP BY, no rows fetched."""
    return {r["type"]: r["n"] for r in qs.values("type").annotate(n=Count("id"))}


def _guide_page_count(qs) -> int:
    """Distinct guide pages, not rows. Guide rows include per-heading records
    that the UI nests under their page, so a row count overcounts what is shown.
    """
    return (
        qs.filter(type=SearchDocument.TYPE_GUIDE)
        .annotate(
            page=Coalesce(
                KeyTextTransform("page_url", "metadata"),
                F("url"),
                output_field=TextField(),
            )
        )
        .values("page")
        .distinct()
        .count()
    )


def _totals(qs, row_counts: dict[str, int]) -> dict[str, int]:
    """Row counts, with guides swapped for their distinct-page count."""
    totals = dict(row_counts)
    if totals.get(SearchDocument.TYPE_GUIDE):
        totals[SearchDocument.TYPE_GUIDE] = _guide_page_count(qs)
    return totals


def search_counts(query: str, type: str | None = None) -> dict[str, int]:
    """`{type: total}` for `query`, computed entirely by aggregate.

    Same numbers as `run_search`'s `total` (distinct pages for guides), for
    callers that need the counts but not the rows — the facet rail, say.
    """
    qs = _matches(query, type)
    if qs is None:
        return {}
    return _totals(qs, _row_counts(qs))


def run_search(query: str, cap: int | None = None, type: str | None = None):
    """Search `query`, grouped by type.

    Returns a list of group dicts in the fixed `TYPE_ORDER` (guides, components,
    blocks, icons):
        [{"type", "label", "results": [SearchDocument, ...], "total", "capped"}]
    Empty groups are omitted. `results` is limited in the database to `cap` rows
    per group, and never more than `MAX_GROUP_RESULTS`. `total` is the full
    pre-limit count (distinct pages for guides) and `capped` says rows were
    withheld. `type` restricts to one document type.
    """
    qs = _matches(query, type)
    if qs is None:
        return []

    row_counts = _row_counts(qs)
    if not row_counts:
        return []

    limit = min(cap, MAX_GROUP_RESULTS) if cap else MAX_GROUP_RESULTS
    totals = _totals(qs, row_counts)
    ordered = sorted(
        row_counts,
        key=lambda t: TYPE_ORDER.index(t) if t in TYPE_ORDER else 99,
    )

    groups = []
    for doc_type in ordered:
        groups.append(
            {
                "type": doc_type,
                "label": TYPE_LABELS.get(doc_type, doc_type.title()),
                "results": list(qs.filter(type=doc_type).order_by("-score")[:limit]),
                "total": totals[doc_type],
                "capped": row_counts[doc_type] > limit,
            }
        )
    return groups
