"""Engine bounds — search is a public, unauthenticated endpoint over an index
that holds every icon, so a one-letter prefix must not be able to make the
server fetch the table or hand Postgres an arbitrarily large tsquery.

Asserts the two limits at the seam that matters: rows are cut by SQL LIMIT (not
by slicing a materialised list), and the query text is bounded before it is
tokenised. Built over the REAL corpus so the numbers are the live ones.
"""

from unittest.mock import patch

from django.core.management import call_command
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from .. import services
from ..models import SearchDocument
from ..services import (
    MAX_GROUP_RESULTS,
    MAX_QUERY_CHARS,
    MAX_QUERY_TOKENS,
    _tokenise,
    run_search,
    search_counts,
)

# A single letter is the worst realistic case: it prefix-matches most of the
# icon pack. "s" beats every other letter in this corpus.
BROAD = "s"


def _row_selects(captured):
    """The SELECTs that pull SearchDocument rows, ignoring aggregates."""
    return [
        q["sql"]
        for q in captured.captured_queries
        if "search_searchdocument" in q["sql"] and "COUNT(" not in q["sql"].upper()
    ]


class ResultLimitTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("build_search_index")

    def test_rows_are_cut_by_sql_limit_not_in_python(self):
        with CaptureQueriesContext(connection) as captured:
            run_search(BROAD, cap=5)
        selects = _row_selects(captured)
        self.assertTrue(selects)
        for sql in selects:
            self.assertIn("LIMIT 5", sql)

    def test_uncapped_call_still_carries_the_hard_ceiling(self):
        # cap=None is "show everything" — everything up to MAX_GROUP_RESULTS.
        with CaptureQueriesContext(connection) as captured:
            run_search(BROAD)
        for sql in _row_selects(captured):
            self.assertIn(f"LIMIT {MAX_GROUP_RESULTS}", sql)

    def test_cap_never_exceeds_the_hard_ceiling(self):
        with CaptureQueriesContext(connection) as captured:
            run_search(BROAD, cap=MAX_GROUP_RESULTS * 10)
        for sql in _row_selects(captured):
            self.assertIn(f"LIMIT {MAX_GROUP_RESULTS}", sql)

    def test_ceiling_bounds_results_while_total_stays_honest(self):
        # Lowered so the real corpus trips it: the group reports the full match
        # count and flags itself capped, but hands back only the ceiling's worth.
        with patch.object(services, "MAX_GROUP_RESULTS", 3):
            groups = services.run_search(BROAD)
        icons = next(g for g in groups if g["type"] == SearchDocument.TYPE_ICON)
        self.assertEqual(len(icons["results"]), 3)
        self.assertGreater(icons["total"], 3)
        self.assertTrue(icons["capped"])

    def test_query_count_does_not_grow_with_corpus_size(self):
        # One aggregate + one limited SELECT per matched group (+ the distinct
        # guide-page count). A fixed handful, whatever the query matches.
        with CaptureQueriesContext(connection) as captured:
            run_search(BROAD)
        self.assertLessEqual(len(captured.captured_queries), 6)


class FacetCountCostTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("build_search_index")

    def test_counts_are_aggregates_and_fetch_no_rows(self):
        with CaptureQueriesContext(connection) as captured:
            counts = search_counts(BROAD)
        self.assertTrue(counts)
        self.assertEqual(_row_selects(captured), [])

    def test_counts_match_run_search_totals(self):
        expected = {g["type"]: g["total"] for g in run_search(BROAD)}
        self.assertEqual(search_counts(BROAD), expected)

    def test_grouped_count_agrees_with_a_plain_per_type_count(self):
        # Independent of the GROUP BY: the annotations on the queryset must not
        # leak into the grouping and split a type across rows.
        counts = search_counts(BROAD)
        for doc_type in (
            SearchDocument.TYPE_COMPONENT,
            SearchDocument.TYPE_BLOCK,
            SearchDocument.TYPE_ICON,
        ):
            expected = services._matches(BROAD, type=doc_type).count()
            self.assertEqual(counts[doc_type], expected, doc_type)

    def test_guide_count_is_distinct_pages_not_rows(self):
        # Guide rows include per-heading records nested under their page, so the
        # user-facing count is pages. The SQL distinct-count must agree exactly
        # with the page_url-or-url set the UI actually renders.
        rows = list(services._matches("signals", type=SearchDocument.TYPE_GUIDE))
        pages = {(r.metadata or {}).get("page_url", r.url) for r in rows}
        self.assertGreater(len(rows), len(pages))  # headings really are present
        self.assertEqual(
            search_counts("signals")[SearchDocument.TYPE_GUIDE], len(pages)
        )

    def test_page_view_runs_the_row_query_once(self):
        # The facet rail used to cost a second full search. It is an aggregate
        # now, so only the displayed groups fetch rows.
        with CaptureQueriesContext(connection) as captured:
            self.client.get(reverse("labbdocs_search:page"), {"q": BROAD})
        selects = _row_selects(captured)
        self.assertLessEqual(len(selects), len(SearchDocument.TYPE_CHOICES))


class QueryLengthTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("build_search_index")

    def test_tokens_are_capped(self):
        tokens = _tokenise(" ".join(f"tok{i}" for i in range(MAX_QUERY_TOKENS * 10)))
        self.assertEqual(len(tokens), MAX_QUERY_TOKENS)

    def test_text_past_the_char_limit_is_ignored(self):
        # "button" sits beyond the cut, so it never reaches the tsquery.
        long_query = ("x" * MAX_QUERY_CHARS) + " button"
        self.assertEqual(run_search(long_query), [])

    def test_oversized_query_is_answered_not_rejected(self):
        # Truncation keeps the leading terms, so a padded query still searches.
        groups = run_search("button " * 5000)
        self.assertTrue(any(g["type"] == SearchDocument.TYPE_COMPONENT for g in groups))

    def test_oversized_query_through_the_page_view(self):
        response = self.client.get(
            reverse("labbdocs_search:page"), {"q": "button " * 5000}
        )
        self.assertEqual(response.status_code, 200)

    def test_oversized_query_through_the_palette_view(self):
        response = self.client.get(
            reverse("labbdocs_search:palette"), {"q": "b " * 5000}
        )
        self.assertEqual(response.status_code, 200)
