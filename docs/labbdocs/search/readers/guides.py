"""Guides/docs reader — hybrid page + heading granularity.

Consumes the generated config of every declared doc type (the same configs the
docs build produces), skipping the types another reader owns. For each page it
emits a **page record** (title + frontmatter description + keywords) plus **one
record per heading** in the page's `toc` (recursively flattening children), so a
search can deep-link straight to the exact section anchor rather than the page
top. Blog posts come through the same path with `category="blog"`.

Sources come from `LABB_DOCS["types"]` rather than a hardcoded list, so a
consumer who declares an `api` or `changelog` doc type gets it indexed with no
code and no extra reader.

Heading anchors come from the config's `toc` list (`{id, name, level,
children}`) — the DocParser already emits them, so nothing here parses markdown.
"""

import re
from pathlib import Path
from typing import Iterable

import yaml

import labbdocs

from ..conf import doc_types
from ..models import SearchDocument

# Source markdown lives beside the labbdocs package: content/<doc_name>/<file_path>.
_CONTENT_DIR = Path(labbdocs.__file__).resolve().parent / "content"

_FRONTMATTER = re.compile(r"^---\n.*?\n---\n", re.DOTALL)
_FENCED_CODE = re.compile(r"```.*?```", re.DOTALL)
_HTML_TAG = re.compile(r"<[^>]+>")
_MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")


def _page_body(category: str, file_path: str) -> str:
    """Stripped prose from a page's source markdown for full-text (weight D).

    Removes frontmatter, fenced code, cotton/HTML tags and markdown noise so the
    body carries readable words, not syntax. Missing files degrade to "".
    """
    if not file_path:
        return ""
    path = _CONTENT_DIR / category / file_path
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="ignore")
    text = _FRONTMATTER.sub("", text, count=1)
    text = _FENCED_CODE.sub(" ", text)
    text = _HTML_TAG.sub(" ", text)
    text = _MD_LINK.sub(r"\1", text)
    text = re.sub(r"[#>*_`~|]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _as_text(value) -> str:
    """Frontmatter keywords may be a comma-string or a list — normalise to text."""
    if isinstance(value, (list, tuple)):
        return " ".join(str(v) for v in value if v)
    return str(value or "").strip()


def _flatten_headings(toc):
    """Depth-first flatten of a `toc` tree into `(id, name)` heading pairs."""
    for entry in toc or []:
        if not isinstance(entry, dict):
            continue
        hid = entry.get("id")
        name = entry.get("name")
        if hid and name:
            yield str(hid), str(name)
        yield from _flatten_headings(entry.get("children"))


class GuidesReader:
    type = SearchDocument.TYPE_GUIDE

    # Doc types another reader owns. `ui` is the components reader's.
    EXCLUDE = {"ui"}

    def read(self) -> Iterable[dict]:
        for name, spec in doc_types().items():
            if name in self.EXCLUDE:
                continue
            config = Path((spec or {}).get("config") or "")
            if not config.name or not config.exists():
                continue
            data = yaml.safe_load(config.read_text()) or {}
            yield from self._read_config(data, name)

    def _read_config(self, data: dict, category: str) -> Iterable[dict]:
        pages = data.get("pages") or {}
        for url, page in pages.items():
            page = page or {}
            frontmatter = page.get("frontmatter") or {}

            # Component-layout pages belong to the components reader — guard even
            # though guide/blog configs shouldn't carry any.
            if frontmatter.get("doc_layout") == "component":
                continue

            page_url = url
            page_title = _as_text(frontmatter.get("title"))

            # Page record — title + frontmatter + stripped prose body (weight D).
            yield {
                "type": self.type,
                "title": page_title,
                "url": page_url,
                "category": category,
                "summary": _as_text(frontmatter.get("description")),
                "keywords": _as_text(frontmatter.get("keywords")),
                "body": _page_body(category, page.get("file_path")),
                "metadata": {
                    "page_url": page_url,
                    "page_title": page_title,
                    "is_heading": False,
                },
            }

            # One heading record per toc entry (children flattened), deep-linking
            # to `#anchor` so a match lands on the exact section.
            for hid, name in _flatten_headings(page.get("toc")):
                yield {
                    "type": self.type,
                    "title": f"{page_title} › {name}",
                    "url": f"{page_url}#{hid}",
                    "category": category,
                    "summary": "",
                    "keywords": name,
                    "metadata": {
                        "page_url": page_url,
                        "page_title": page_title,
                        "heading": name,
                        "is_heading": True,
                    },
                }
