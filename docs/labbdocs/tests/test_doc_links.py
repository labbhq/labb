"""Every {% doc_url %} target in the content tree resolves to a real file.

doc_url takes a content-relative path, so a page that moves leaves silently
broken links behind: the tag renders a URL for a file that is gone, and nothing
errors at build time. Four links were already broken this way before the
guide restructure, three of them pointing at a references group that had been
renumbered two versions earlier.

Run with: manage.py test labbdocs
"""

import re
from pathlib import Path

from django.test import SimpleTestCase
from markdown.extensions.toc import slugify

from ..doc_parser import CONTENT_BASE_PATH

DOC_URL = re.compile(r"""doc_url\s+'([^']+)'\s+'([^']+)'""")
# the same tag, followed by an #anchor into the target page
DOC_URL_ANCHOR = re.compile(r"""doc_url\s+'([^']+)'\s+'([^']+)'\s*%\}#([\w-]+)""")
HEADING = re.compile(r"^#{1,6}\s+(.*)$", re.MULTILINE)


def _heading_slugs(markdown_text):
    """Anchor ids the TOC extension will generate for a page's headings."""
    slugs = set()
    for raw in HEADING.findall(markdown_text):
        text = re.sub(r"<[^>]+>", "", raw)  # inline html, e.g. a badge
        text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # links -> text
        text = text.replace("`", "").replace("*", "").strip()
        slugs.add(slugify(text, "-"))
    return slugs


class DocUrlTargetTests(SimpleTestCase):
    def test_every_doc_url_target_exists(self):
        root = Path(CONTENT_BASE_PATH)
        checked = 0
        for source in sorted(root.rglob("*.md")):
            for target, doc_type in DOC_URL.findall(source.read_text()):
                checked += 1
                with self.subTest(source=source.name, target=f"{doc_type}/{target}"):
                    self.assertTrue(
                        (root / doc_type / target).is_file(),
                        f"{source.relative_to(root)} links to {doc_type}/{target}, "
                        f"which does not exist",
                    )
        self.assertGreater(checked, 0, "found no doc_url tags to check")

    def test_every_doc_url_anchor_exists(self):
        """A link to #some-heading must land on a heading that exists.

        The file-level check above passes happily when only the anchor is
        stale, which is how theme-controller.md kept pointing at a numbered
        theming heading long after the numbering was removed.
        """
        root = Path(CONTENT_BASE_PATH)
        for source in sorted(root.rglob("*.md")):
            for target, doc_type, anchor in DOC_URL_ANCHOR.findall(source.read_text()):
                page = root / doc_type / target
                if not page.is_file():
                    continue  # already reported by the file-level test
                with self.subTest(source=source.name, anchor=f"{target}#{anchor}"):
                    self.assertIn(
                        anchor,
                        _heading_slugs(page.read_text()),
                        f"{source.relative_to(root)} links to {target}#{anchor}, "
                        f"but that page has no such heading",
                    )
