"""Runtime support for installed labb blocks.

The public surface a block's own views.py imports lives here; the
implementations are in sibling modules.
"""

from .resolution import BlockContextError, lm
from .shortcuts import render_page
from .urls import include_blocks

__all__ = ["BlockContextError", "include_blocks", "lm", "render_page"]
