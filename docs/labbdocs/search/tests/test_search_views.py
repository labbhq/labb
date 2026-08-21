"""HTTP seam — external behaviour of the /search page, over the REAL ui.yaml
corpus built in setUp. Asserts observable facts a user could confirm: a known
component is found, prefix + fuzzy matches work, the group caps with a See-all
affordance, and the blank / no-results states render.
"""

import html as _html
import re

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from ..models import SearchDocument
from ..services import search_counts
from ..views import PAGE_GROUP_CAP


def _text(response):
    """Rendered HTML with entities decoded (Cotton escapes attr values)."""
    return _html.unescape(response.content.decode())


def _component_cards(body):
    """How many component cards were rendered. No other card template opens its
    link with these classes, so this counts them exactly."""
    return body.count('class="flex items-start gap-3 rounded-lg px-3 py-2')


class SearchPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("build_search_index")

    def _get(self, q=None):
        params = {"q": q} if q is not None else {}
        return self.client.get(reverse("labbdocs_search:page"), params)

    def test_query_finds_component_in_components_group(self):
        response = self._get("button")
        self.assertEqual(response.status_code, 200)
        body = _text(response)
        self.assertIn("Components", body)  # the group heading
        self.assertIn("Button", body)
        # The component card renders the mono c-lb.* tag and links to the doc page.
        self.assertIn("c-lb.button", body)
        self.assertIn("/docs/ui/actions/button/", body)

    def test_prefix_match_finds_button(self):
        # A partial token still matches while typing (raw tsquery `:*`).
        response = self._get("butt")
        self.assertContains(response, "Button")
        self.assertIn("c-lb.button", _text(response))

    def test_fuzzy_match_finds_button(self):
        # One-char typo is rescued by trigram similarity on search_name.
        response = self._get("buton")
        self.assertContains(response, "Button")
        self.assertIn("c-lb.button", _text(response))

    def test_broad_query_caps_the_group_with_see_all(self):
        matches = search_counts("button")[SearchDocument.TYPE_COMPONENT]
        self.assertGreater(matches, PAGE_GROUP_CAP)  # the group does cap

        body = _text(self._get("button"))
        self.assertEqual(_component_cards(body), PAGE_GROUP_CAP)
        self.assertIn(f"See all {matches}", body)

    def test_see_all_lands_on_the_uncapped_type_facet(self):
        matches = search_counts("button")[SearchDocument.TYPE_COMPONENT]
        response = self.client.get(
            reverse("labbdocs_search:page"), {"q": "button", "type": "component"}
        )
        body = _text(response)
        self.assertEqual(_component_cards(body), matches)
        self.assertNotIn("See all", body)

    def test_facet_count_matches_the_see_all_number(self):
        matches = search_counts("button")[SearchDocument.TYPE_COMPONENT]
        body = _text(self._get("button"))
        rail = re.search(r"Components</span>\s*<span[^>]*>(\d+)</span>", body)
        self.assertIsNotNone(rail)
        self.assertEqual(int(rail.group(1)), matches)

    def test_blank_query_shows_category_shortcuts(self):
        response = self._get("")
        self.assertEqual(response.status_code, 200)
        body = _text(response)
        self.assertIn("Browse components", body)
        self.assertIn("Browse icons", body)
        # No result cards on the blank state.
        self.assertNotIn("c-lb.button", body)

    def test_no_query_param_is_blank_state(self):
        response = self._get()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Browse components", _text(response))

    def test_no_results_shows_message(self):
        response = self._get("zzzzznotathing")
        self.assertEqual(response.status_code, 200)
        body = _text(response)
        self.assertIn("No results", body)
        self.assertNotIn("c-lb.button", body)
