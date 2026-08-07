"""Icons reader — one search row per icon, across every installed pack.

Source is the labbicons package metadata dir: one JSON file per pack, each with
a `metadata` block (pack id + name) and a `categories` map whose entries carry
the icons. An icon record makes the glyph findable by name, category, variants,
component name, and pack; `metadata` carries what the icon card needs to render
the glyph and offer its copy-the-tag affordance. All packs are globbed, so a new
pack file is picked up with no code change.
"""

import glob
import json
import os
import sys
from typing import Iterable

from ..models import SearchDocument

# labbicons is an optional dependency of labbdocs — a docs site without it
# simply has no icons to index, which is a missing source, not a broken install.
try:
    import labbicons
except ImportError:  # pragma: no cover - exercised by installs without labbicons
    labbicons = None


def _metadata_dir() -> str:
    return os.path.join(os.path.dirname(labbicons.__file__), "metadata")


class IconsReader:
    type = SearchDocument.TYPE_ICON

    def read(self) -> Iterable[dict]:
        if labbicons is None:
            print(
                "search: IconsReader skipped — labbicons is not installed",
                file=sys.stderr,
            )
            return

        for path in glob.glob(os.path.join(_metadata_dir(), "*.json")):
            with open(path) as fh:
                data = json.load(fh)

            meta = data.get("metadata") or {}
            pack = meta.get("pack") or meta.get("name") or ""

            for cat_name, cat in (data.get("categories") or {}).items():
                for icon in cat.get("icons") or []:
                    name = icon.get("name") or ""
                    component_name = icon.get("component_name") or ""
                    variants = icon.get("variants") or []

                    keywords = " ".join(
                        part
                        for part in [name, cat_name, component_name, *variants, pack]
                        if part
                    )

                    yield {
                        "type": self.type,
                        "title": name,
                        "category": cat_name,
                        "summary": "",
                        "keywords": keywords,
                        "url": "/docs/icons/",
                        "metadata": {
                            "component_name": component_name,
                            "pack": pack,
                            "variants": variants,
                        },
                    }
