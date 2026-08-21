"""HTTP seam — the /search page facet rail, shareable ?q=&type= URLs, and the
reactive (Datastar) vs cold (no-header) branches. Uses the real ui.yaml corpus
built in setUp. "menu" is chosen because it matches every type (components,
icons, blocks, guides), so filtering to one type is observable.
"""

import html as _html
import json

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from ..models import SearchQueryLog
from ..services import run_search


def _text(response):
    """Rendered HTML with entities decoded (Cotton escapes attr values)."""
    return _html.unescape(response.content.decode())


# Literal `c-lb.<name>` text is emitted only by component cards; icon cards emit
# `c-lbi.<name>` (no trailing-dot match), block/guide cards emit neither. The
# facet rail's own <c-lb.button>/<c-lb.badge> render to <a>/<span>, not literal
# text — so these strings count *result cards*, not template tags.
COMPONENT_CARD = "c-lb."
ICON_CARD = "c-lbi."


class FacetFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("build_search_index")

    def _get(self, **params):
        return self.client.get(reverse("labbdocs_search:page"), params)

    def test_type_facet_filters_to_one_type(self):
        # Untyped "menu" surfaces components.
        self.assertIn(COMPONENT_CARD, _text(self._get(q="menu")))
        # Narrowed to icons: component cards are gone, icon cards remain.
        body = _text(self._get(q="menu", type="icon"))
        self.assertIn(ICON_CARD, body)
        self.assertNotIn(COMPONENT_CARD, body)

    def test_component_facet_excludes_icons(self):
        body = _text(self._get(q="menu", type="component"))
        self.assertIn(COMPONENT_CARD, body)
        self.assertNotIn(ICON_CARD, body)

    def test_unknown_type_falls_back_to_all(self):
        # A bogus ?type= is ignored (treated as All), not an error.
        body = _text(self._get(q="menu", type="bogus"))
        self.assertEqual(self._get(q="menu", type="bogus").status_code, 200)
        self.assertIn(COMPONENT_CARD, body)
        self.assertIn(ICON_CARD, body)


class ShareableUrlTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("build_search_index")

    def test_cold_shared_load_renders_server_side(self):
        # A shared /search?q=&type= link arrives with NO Datastar header and an
        # empty signal bag; from_query rehydrates it and the page renders the
        # filtered results server-side (the no-JS fallback).
        response = self.client.get(
            reverse("labbdocs_search:page"), {"q": "menu", "type": "icon"}
        )
        self.assertEqual(response.status_code, 200)
        body = _text(response)
        self.assertIn(ICON_CARD, body)  # icons rendered
        self.assertNotIn(COMPONENT_CARD, body)  # type filter respected, no JS

    def test_cold_load_without_type_shows_all(self):
        response = self.client.get(reverse("labbdocs_search:page"), {"q": "menu"})
        body = _text(response)
        self.assertIn(COMPONENT_CARD, body)
        self.assertIn(ICON_CARD, body)

    def test_reactive_request_filters_via_signals(self):
        # The Datastar path: header present, signals carry the clean state under
        # the `search.*` namespace. Same filtering, driven by request.signals.
        response = self.client.get(
            reverse("labbdocs_search:page"),
            {"datastar": json.dumps({"search": {"q": "menu", "type": "icon"}})},
            headers={"datastar-request": "true"},
        )
        self.assertEqual(response.status_code, 200)
        body = _text(response)
        self.assertIn(ICON_CARD, body)
        self.assertNotIn(COMPONENT_CARD, body)

    def test_reactive_request_does_not_log(self):
        # As-you-type morphs must not pollute analytics; only cold/submitted
        # queries are logged.
        self.client.get(
            reverse("labbdocs_search:page"),
            {"datastar": json.dumps({"search": {"q": "menu"}})},
            headers={"datastar-request": "true"},
        )
        self.assertEqual(SearchQueryLog.objects.count(), 0)


class FacetCountTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("build_search_index")

    def test_counts_match_untyped_search(self):
        expected = {g["type"]: g["total"] for g in run_search("menu")}
        response = self.client.get(reverse("labbdocs_search:page"), {"q": "menu"})
        facets = {f["type"]: f["count"] for f in response.context["facets"]}
        for doc_type, total in expected.items():
            self.assertEqual(facets[doc_type], total)

    def test_all_facet_shows_grand_total(self):
        expected_total = sum(g["total"] for g in run_search("menu"))
        response = self.client.get(reverse("labbdocs_search:page"), {"q": "menu"})
        facets = {f["type"]: f["count"] for f in response.context["facets"]}
        self.assertEqual(facets[""], expected_total)

    def test_counts_stable_when_filtered(self):
        # Filtering to one type must not shrink the rail's counts — they come
        # from the untyped search, so All still shows the grand total.
        untyped = sum(g["total"] for g in run_search("menu"))
        response = self.client.get(
            reverse("labbdocs_search:page"), {"q": "menu", "type": "icon"}
        )
        facets = {f["type"]: f["count"] for f in response.context["facets"]}
        self.assertEqual(facets[""], untyped)

    def test_active_facet_marked(self):
        response = self.client.get(
            reverse("labbdocs_search:page"), {"q": "menu", "type": "icon"}
        )
        active = {
            f["type"] for f in response.context["facets"] if f["behavior"] == "active"
        }
        self.assertEqual(active, {"icon"})

    def test_all_active_by_default(self):
        response = self.client.get(reverse("labbdocs_search:page"), {"q": "menu"})
        active = {
            f["type"] for f in response.context["facets"] if f["behavior"] == "active"
        }
        self.assertEqual(active, {""})
