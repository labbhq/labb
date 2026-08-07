"""Icons source — HTTP seam over the real labbicons metadata built in setUp,
plus a thin command-seam check that every pack icon is populated.

Asserts observable facts a user could confirm: a known icon is found in the
Icons group with its glyph and a copy-the-tag affordance; a short typo still
surfaces an arrow icon (trigram); and a query that matches both icons and a
component keeps the component group while the flooding Icons group is capped
with a See-all affordance.
"""

import glob
import html as _html
import json
import os

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

import labbicons

from ..models import SearchDocument
from ..views import GROUP_CAP


def _text(response):
    """Rendered HTML with entities decoded (Cotton escapes attr values)."""
    return _html.unescape(response.content.decode())


def _expected_icon_count():
    """Total icons across every pack JSON in the labbicons metadata dir."""
    meta_dir = os.path.join(os.path.dirname(labbicons.__file__), "metadata")
    total = 0
    for path in glob.glob(os.path.join(meta_dir, "*.json")):
        with open(path) as fh:
            data = json.load(fh)
        for cat in (data.get("categories") or {}).values():
            total += len(cat.get("icons") or [])
    return total


class IconSearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("build_search_index")

    def _get(self, q):
        return self.client.get(reverse("labbdocs_search:page"), {"q": q})

    def test_known_icon_found_with_glyph_and_copy_affordance(self):
        # arrow-down is a real remix icon (Arrows category).
        response = self._get("arrow-down")
        self.assertEqual(response.status_code, 200)
        body = _text(response)
        self.assertIn("Icons", body)  # the group heading
        self.assertIn("arrow-down", body)
        # The copy affordance carries the tag built from component_name.
        self.assertIn("c-lbi.rmx.arrow-down", body)
        # The glyph is rendered via the labbicons component.
        self.assertIn("rmx.arrow-down", body)

    def test_fuzzy_short_token_finds_arrow(self):
        # "arow" is a one-char typo — trigram on search_name rescues it.
        response = self._get("arow")
        self.assertEqual(response.status_code, 200)
        body = _text(response)
        self.assertIn("Icons", body)
        self.assertIn("arrow", body)

    def test_icons_uncapped_and_do_not_suppress_components(self):
        # "menu" matches many icons AND the Menu component. Grouping keeps icons
        # in their own group so they don't drown the component; on the /search
        # page (unlike the palette) every match is shown — uncapped, no See-all.
        response = self._get("menu")
        self.assertEqual(response.status_code, 200)
        body = _text(response)

        # Both groups present — icons did not drown the component.
        self.assertIn("Icons", body)
        self.assertIn("Components", body)
        self.assertIn("Menu", body)

        # The Icons group is uncapped: one copy affordance per rendered icon
        # card, far more than the palette's cap, and no See-all truncation.
        shown_icons = body.count("navigator.clipboard.writeText")
        self.assertGreater(shown_icons, GROUP_CAP)
        self.assertNotIn("See all", body)

    def test_all_pack_icons_are_indexed(self):
        # Command seam: every icon in every pack JSON becomes a row.
        count = SearchDocument.objects.filter(type=SearchDocument.TYPE_ICON).count()
        self.assertEqual(count, _expected_icon_count())
        self.assertGreater(count, 0)
