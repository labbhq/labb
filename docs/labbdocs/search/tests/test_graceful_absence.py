"""A docs site that never wires search up must still render.

Before the gate, `lbdocs/layout/base.html` rendered the palette unconditionally
on every page — and the palette loads `search_tags` and reverses
`labbdocs_search:*`, so a consumer without the app got an error on every single
docs page. These tests pin the gate.

Rendered through the test client rather than an inline `Template()`, because
cotton's `<c-...>` tags are expanded by its template *loader* — a template
string built in Python never goes through it.
"""

from django.test import TestCase, modify_settings

# Any docs page carries the base layout; the guide index is the stable one.
DOCS_URL = "/docs/guide/"


class SearchInstalledTests(TestCase):
    def test_palette_renders_when_the_app_is_installed(self):
        html = self.client.get(DOCS_URL).content.decode()
        self.assertIn("search-palette", html)


@modify_settings(INSTALLED_APPS={"remove": ["labbdocs.search"]})
class SearchNotInstalledTests(TestCase):
    def test_docs_page_still_renders(self):
        response = self.client.get(DOCS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertIn("</html>", response.content.decode())

    def test_no_palette_shell_is_emitted(self):
        html = self.client.get(DOCS_URL).content.decode()
        self.assertNotIn("search-palette", html)

    def test_no_dead_keyboard_shortcut(self):
        # The ⌘K handler lives inside the palette's <script>; not rendering the
        # component is what makes the shortcut absent rather than broken.
        self.assertNotIn("palOpen", self.client.get(DOCS_URL).content.decode())

    def test_no_datastar_loader(self):
        # A search-less docs site stays zero-JS; the palette is what pulls
        # Datastar in on demand.
        self.assertNotIn(
            "palEnsureDatastar", self.client.get(DOCS_URL).content.decode()
        )
