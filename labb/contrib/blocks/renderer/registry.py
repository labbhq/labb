"""Renderer state, set once before Django starts.

`block dev serve` and the block test harness both configure the renderer before
the urlconf is imported. Holding the state on one object means views read the
current values — module-level names would be snapshotted by `from . import X`
at import time, so a later reassignment would be invisible.
"""


class Registry:
    __slots__ = ("blocks", "repo_path", "vendor")

    def __init__(self):
        self.blocks = {}
        self.repo_path = "."
        self.vendor = ""


registry = Registry()


def configure(blocks, repo_path, vendor):
    """Point the renderer at a source repo. Call before the urlconf is imported."""
    registry.blocks = blocks
    registry.repo_path = str(repo_path)
    registry.vendor = vendor
