"""Guides/blog hybrid source — HTTP seam + command seam.

Built over the REAL guide.yaml / blog.yaml corpus in setUp. Asserts observable
facts: a heading match deep-links to its `#anchor` under the Guides group, a
multi-heading page shows once at top level (dedup/nesting), a blog post is
searchable, and the reader emits one page record plus per-heading records.
"""

import html as _html

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .. import services
from ..models import SearchDocument
from ..services import run_search, search_counts

SIGNALS_URL = "/docs/guide/reactivity/signals/"
# a heading that lives on the Signals page, not its title. The syncQuery
# section used to serve this role; it moved to Patterns in the 0.5 guide rework.
SIGNALS_ANCHOR = "#declaration-forms"
BLOG_URL = "/blog/posts/labb-featured-on-youtube/"


def _text(response):
    """Rendered HTML with entities decoded (Cotton escapes attr values)."""
    return _html.unescape(response.content.decode())


class GuidesSearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("build_search_index")

    def _get(self, q):
        return self.client.get(reverse("labbdocs_search:page"), {"q": q})

    def test_heading_match_deeplinks_under_guides_group(self):
        # A term that lives in a heading (not the page title) returns that
        # heading, deep-linked to its anchor, inside the Guides group.
        response = self._get("declaration forms")
        self.assertEqual(response.status_code, 200)
        body = _text(response)
        self.assertIn("Guides", body)  # the group heading
        self.assertIn(SIGNALS_URL + SIGNALS_ANCHOR, body)

    def test_multi_section_page_appears_once_at_top_level(self):
        # "signals" matches the Signals page AND several of its headings; the
        # page must appear once as a top-level card (its bare url, no anchor),
        # with headings nested beneath rather than as separate top hits.
        response = self._get("signals")
        body = _text(response)
        top_level_href = 'href="{}"'.format(SIGNALS_URL)
        self.assertEqual(body.count(top_level_href), 1)

    def test_blog_post_is_searchable(self):
        # The blog is indexed alongside guides (category=blog).
        response = self._get("BugBytes")
        self.assertEqual(response.status_code, 200)
        body = _text(response)
        self.assertIn("Guides", body)
        self.assertIn("Blog", body)  # the Blog badge
        self.assertIn(BLOG_URL, body)

    def _guide_group(self, q, cap):
        groups = run_search(q, cap=cap)
        return next(g for g in groups if g["type"] == SearchDocument.TYPE_GUIDE)

    def _by_page(self, rows):
        pages = {}
        for row in rows:
            page = (row.metadata or {}).get("page_url", row.url)
            pages.setdefault(page, []).append(row)
        return pages

    def test_cap_cuts_guides_by_page_and_keeps_each_page_whole(self):
        matching = self._by_page(services._matches("s", type=SearchDocument.TYPE_GUIDE))
        rows = sum(len(page_rows) for page_rows in matching.values())
        self.assertGreater(rows, len(matching))  # headings really are present

        shown = self._by_page(self._guide_group("s", cap=3)["results"])
        self.assertEqual(len(shown), 3)
        for page, page_rows in shown.items():
            self.assertEqual(len(page_rows), len(matching[page]))

    def test_capped_and_total_and_the_facet_count_are_the_same_unit(self):
        pages = search_counts("s")[SearchDocument.TYPE_GUIDE]

        capped = self._guide_group("s", cap=3)
        self.assertEqual(capped["total"], pages)
        self.assertTrue(capped["capped"])

        whole = self._guide_group("s", cap=pages)
        self.assertGreater(len(whole["results"]), pages)  # rows outnumber pages
        self.assertFalse(whole["capped"])

    # --- command seam: hybrid emission ---------------------------------------

    def test_signals_page_emits_page_plus_heading_records(self):
        rows = SearchDocument.objects.filter(
            type=SearchDocument.TYPE_GUIDE, url__startswith=SIGNALS_URL
        )

        page_records = [r for r in rows if not r.metadata.get("is_heading")]
        heading_records = [r for r in rows if r.metadata.get("is_heading")]

        # Exactly one page record, at the bare page url.
        self.assertEqual(len(page_records), 1)
        self.assertEqual(page_records[0].url, SIGNALS_URL)
        self.assertEqual(page_records[0].title, "Signals")

        # Multiple heading records, each deep-linking under the page.
        self.assertGreaterEqual(len(heading_records), 6)
        anchors = {r.url for r in heading_records}
        self.assertIn(SIGNALS_URL + SIGNALS_ANCHOR, anchors)
        for r in heading_records:
            self.assertTrue(r.url.startswith(SIGNALS_URL + "#"))
            self.assertEqual(r.metadata.get("page_url"), SIGNALS_URL)
            self.assertTrue(r.title.startswith("Signals › "))

    def test_blog_page_record_has_blog_category(self):
        post = SearchDocument.objects.filter(
            type=SearchDocument.TYPE_GUIDE, url=BLOG_URL
        ).first()
        self.assertIsNotNone(post)
        self.assertEqual(post.category, "blog")
        self.assertFalse(post.metadata.get("is_heading"))
