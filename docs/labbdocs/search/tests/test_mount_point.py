"""The consumer chooses where search is mounted, so no link may assume /search/.

Mounting it at /find/docs/ and asserting every generated URL follows is the only
check that actually catches a reintroduced hardcoded path — a reversal and a
hardcoded string are indistinguishable while both sit at the default mount.
"""

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from ..conf import DEFAULT_READERS
from ..views import _facet_href


def _shipped_readers_only():
    """The alt urlconf has no `blocks_detail`, and labbio's BlocksReader reverses
    it at index-build time. Scope to the three labbdocs ships."""
    docs = {**(getattr(settings, "LABB_DOCS", None) or {})}
    docs["search"] = {**(docs.get("search") or {}), "readers": DEFAULT_READERS}
    return docs


@override_settings(
    ROOT_URLCONF="labbdocs.search.tests.urls_alt",
    LABB_DOCS=_shipped_readers_only(),
)
class MountPointTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("build_search_index")

    def test_page_reverses_to_the_configured_mount(self):
        self.assertEqual(reverse("labbdocs_search:page"), "/find/docs/")

    def test_facet_href_follows_the_mount(self):
        href = _facet_href("button", "icon")
        self.assertTrue(href.startswith("/find/docs/?"), href)
        self.assertIn("type=icon", href)

    def test_palette_result_links_follow_the_mount(self):
        # The palette fragment renders without the base layout, so it can be
        # exercised under a urlconf that carries search and nothing else. The
        # full /search page cannot: `c-lbdocs.layout.base` reverses `set_theme`
        # and `index`, which are the *consumer's* URL names — a labbdocs->host
        # coupling wider than search (see the map's Not-yet-specified).
        response = self.client.get(reverse("labbdocs_search:palette"), {"q": "button"})
        body = response.content.decode()
        self.assertIn('href="/find/docs/?q=button"', body)
        self.assertNotIn('href="/search/', body)
