"""Stand-in for a consumer's blocks reader.

labbdocs ships readers for guides, components and icons only; blocks belong to
whoever installs them, so the site that mounts search registers its own (labb.io
does). The search tests still cover the block card and the Blocks facet, so the
suite needs one. This reads the catalogue in extras/blocks and links through the
`blocks_detail` route in tests/urls.py, mirroring labb.io's reader.
"""

from pathlib import Path
from typing import Iterable

import yaml
from django.conf import settings
from django.urls import reverse

from labbdocs.search.models import SearchDocument


class BlocksReader:
    type = SearchDocument.TYPE_BLOCK

    def read(self) -> Iterable[dict]:
        root = Path(settings.BLOCKS_ROOT)
        if not root.exists():
            return

        for block_yaml in sorted(root.glob("*/*/block.yaml")):
            category = block_yaml.parent.parent.name
            slug = block_yaml.parent.name

            try:
                data = yaml.safe_load(block_yaml.read_text()) or {}
            except yaml.YAMLError:
                continue

            name = data.get("name", "")
            ref = data.get("ref", "")
            tags = data.get("tags") or []

            yield {
                "type": self.type,
                "title": name,
                "url": reverse(
                    "blocks_detail", kwargs={"category": category, "slug": slug}
                ),
                "category": category,
                "summary": data.get("description", ""),
                "keywords": " ".join(
                    part for part in [name, category, slug, ref, *tags] if part
                ),
                "metadata": {
                    "ref": ref,
                    "tags": tags,
                    "status": data.get("status"),
                    "block_type": data.get("type"),
                },
            }
