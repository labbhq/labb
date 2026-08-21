"""HTTP seam — the ⌘K palette fragment view (`labbdocs_search:palette`).

Driven the way the live overlay drives it: the query rides in the Datastar
signal bag (`?datastar={"palette": {"q": ...}}`), which the reactivity middleware
decodes into `request.signals`. The palette namespaces its signals so they do not
collide with the `/search` page's own `q`, which shares the same document. Asserts observable facts: grouped/capped results for a query,
each source type reachable, blank-query shortcuts, and — the load-bearing one —
that the response is ONLY the `#search-palette-results` region (never the dialog
shell or a full page), which is what lets the open dialog survive a morph.
"""

import html as _html
import json

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse


def _text(response):
    """Rendered HTML with entities decoded (Cotton escapes attr values)."""
    return _html.unescape(response.content.decode())


class PaletteViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("build_search_index")

    def _get(self, q=None, plain=False):
        """Drive the palette view. Default: as a reactive Datastar GET (signal
        bag). `plain=True` uses a bare ?q= (the no-JS/robustness path)."""
        if q is None:
            return self.client.get(reverse("labbdocs_search:palette"))
        if plain:
            return self.client.get(reverse("labbdocs_search:palette"), {"q": q})
        return self.client.get(
            reverse("labbdocs_search:palette"),
            {"datastar": json.dumps({"palette": {"q": q}})},
        )

    # --- results shape -----------------------------------------------------

    def test_query_finds_component_in_components_group(self):
        response = self._get("button")
        self.assertEqual(response.status_code, 200)
        body = _text(response)
        self.assertIn("Components", body)
        self.assertIn("Button", body)
        self.assertIn("c-lb.button", body)
        self.assertIn("/docs/ui/actions/button/", body)

    def test_plain_q_param_also_works(self):
        # No Datastar header/signal bag — a bare ?q= still resolves (test/no-JS).
        response = self._get("button", plain=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("c-lb.button", _text(response))

    def test_group_caps_at_five_with_see_all(self):
        body = _text(self._get("button"))
        # The literal `c-lb.` tag is emitted only by component cards, so it counts
        # the capped Components group exactly.
        self.assertEqual(body.count("c-lb."), 5)
        self.assertIn("See all", body)

    def test_see_all_links_to_full_search_page(self):
        body = _text(self._get("button"))
        self.assertIn('href="/search/?q=button"', body)

    # --- the morph-target invariant ---------------------------------------

    def test_response_is_only_the_results_region(self):
        """The fragment's sole top-level element is #search-palette-results — no
        dialog shell, no <html>. That scoping is what keeps the dialog open on
        morph (Datastar outer-morphs just the matching id)."""
        body = _text(self._get("button"))
        self.assertIn('id="search-palette-results"', body)
        self.assertNotIn("<html", body.lower())
        # The dialog shell (input, dialog id) must NOT be re-sent by the fragment.
        self.assertNotIn("search-palette-input", body)
        self.assertNotIn('id="search-palette"', body)

    # --- blank / empty states ---------------------------------------------

    def test_blank_query_shows_category_shortcuts(self):
        body = _text(self._get(""))
        self.assertIn("Browse components", body)
        self.assertIn("Browse icons", body)
        self.assertIn("Browse blocks", body)
        self.assertIn("Browse guides", body)
        self.assertNotIn("c-lb.button", body)

    def test_no_query_param_is_blank_state(self):
        body = _text(self._get())
        self.assertIn("Browse components", body)

    def test_no_results_shows_message(self):
        body = _text(self._get("zzzzznotathing"))
        self.assertIn("No results", body)
        self.assertNotIn("c-lb.button", body)

    # --- every source type is reachable through the palette ----------------

    def test_component_reachable(self):
        self.assertIn("c-lb.button", _text(self._get("button")))

    def test_icon_reachable(self):
        body = _text(self._get("arrow-down"))
        self.assertIn("Icons", body)
        self.assertIn("c-lbi.rmx.arrow-down", body)

    def test_block_reachable(self):
        body = _text(self._get("customers"))
        self.assertIn("Blocks", body)
        self.assertIn("Customers table", body)
        self.assertIn("/blocks/data-table/customers/", body)

    def test_guide_reachable(self):
        body = _text(self._get("syncQuery"))
        self.assertIn("Guides", body)
