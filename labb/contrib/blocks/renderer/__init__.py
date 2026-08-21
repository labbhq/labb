"""The block dev-server renderer: gallery, detail pages and source viewer."""

from .registry import Registry, configure, registry
from .tree import file_tree

__all__ = ["Registry", "configure", "file_tree", "registry"]
