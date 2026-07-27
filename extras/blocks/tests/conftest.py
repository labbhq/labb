import os
import sys
from pathlib import Path

import pytest

# Allow async db access — required for pytest-playwright under asyncio.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

# Ensure the blocks package root (extras/blocks/) is on sys.path so that
# settings_test.py is importable and the synthetic vendor package resolves.
BLOCKS_ROOT = Path(__file__).resolve().parent.parent
if str(BLOCKS_ROOT) not in sys.path:
    sys.path.insert(0, str(BLOCKS_ROOT))

# Build .labb/templates/, synthetic vendor package, and populate BLOCK_REGISTRY
# before Django loads the ROOT_URLCONF (which reads BLOCK_REGISTRY at import time).
from labb.cli.handlers.commons import blocks_root  # noqa: E402
from labb.cli.handlers.blocks_dev import (  # noqa: E402  (import after sys.path setup — intentional)
    _build_template_tree,
    _build_vendor_package,
    _create_renderer_base_template,
    _discover_blocks,
)

_build_template_tree(BLOCKS_ROOT, vendor="lb")
_build_vendor_package(BLOCKS_ROOT, vendor="lb")
_create_renderer_base_template(BLOCKS_ROOT)

# Add .labb/ to sys.path so the synthetic 'lb' package is importable.
labb_pkg_root = str(BLOCKS_ROOT / ".labb")
if labb_pkg_root not in sys.path:
    sys.path.insert(0, labb_pkg_root)

discovered = _discover_blocks(BLOCKS_ROOT)

from labb.contrib.blocks import renderer as _renderer  # noqa: E402  (import after sys.path setup — intentional)

_block_registry = {
    f"lb/{category}/{slug}": {
        "type": meta["type"],
        "vendor": "lb",
        "category": category,
        "slug": slug,
        "preview_context": meta.get("preview_context", {}),
    }
    for (category, slug), meta in discovered.items()
}
_renderer.configure(_block_registry, blocks_root(BLOCKS_ROOT), "lb")
