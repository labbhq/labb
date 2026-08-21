"""Remote block sources: monorepo subdirectories, and failing without hanging.

The official collection ships from `extras/blocks` inside the labb monorepo, so
a clone root is not always the source root. And GitHub answers 404 for missing
*and* private repos, so an unreachable source used to leave git waiting on an
interactive credential prompt, hanging the CLI instead of warning and skipping.
"""

import subprocess
from unittest.mock import patch

from labb.cli.handlers.blocks import _clone_source
from labb.config import BlockSource


def _ok(*args, **kwargs):
    return subprocess.CompletedProcess(args=[], returncode=0)


def _fail(*args, **kwargs):
    return subprocess.CompletedProcess(args=[], returncode=128)


class TestSubdir:
    def test_a_subdir_source_resolves_below_the_clone(self):
        source = BlockSource(
            name="labbhq", url="https://x/labb", subdir="extras/blocks"
        )
        with patch("labb.cli.handlers.blocks.subprocess.run", _ok):
            root = _clone_source(source, "/tmp/clone")
        # as_posix so the assertion holds on Windows, where str() uses backslashes.
        assert root.as_posix() == "/tmp/clone/extras/blocks"

    def test_without_a_subdir_the_clone_root_is_the_source_root(self):
        source = BlockSource(name="s", url="https://x/blocks")
        with patch("labb.cli.handlers.blocks.subprocess.run", _ok):
            root = _clone_source(source, "/tmp/clone")
        assert root.as_posix() == "/tmp/clone"

    def test_subdir_survives_a_config_round_trip(self):
        from labb.config import BlocksConfig, LabbConfig

        config = LabbConfig()
        config.blocks = BlocksConfig(
            sources=[
                BlockSource(name="labbhq", url="https://x/labb", subdir="extras/blocks")
            ]
        )
        written = config.to_dict()["blocks"]["sources"][0]
        assert written["subdir"] == "extras/blocks"

        reloaded = LabbConfig.from_dict(config.to_dict())
        assert reloaded.blocks.sources[0].subdir == "extras/blocks"

    def test_a_source_without_a_subdir_omits_the_key(self):
        from labb.config import BlocksConfig, LabbConfig

        config = LabbConfig()
        config.blocks = BlocksConfig(sources=[BlockSource(name="s", path="../blocks")])
        assert "subdir" not in config.to_dict()["blocks"]["sources"][0]


class TestUnreachableSource:
    def test_an_unreachable_source_returns_none_rather_than_raising(self):
        source = BlockSource(name="gone", url="https://x/nope")
        with patch("labb.cli.handlers.blocks.subprocess.run", _fail):
            assert _clone_source(source, "/tmp/clone") is None

    def test_git_is_never_allowed_to_prompt_for_credentials(self):
        """The whole point: a 404 must fail fast, not block on a prompt."""
        seen = {}

        def capture(*args, **kwargs):
            seen.update(kwargs)
            return _ok()

        source = BlockSource(name="s", url="https://x/blocks")
        with patch("labb.cli.handlers.blocks.subprocess.run", capture):
            _clone_source(source, "/tmp/clone")

        assert seen["env"]["GIT_TERMINAL_PROMPT"] == "0"
        assert seen["timeout"] > 0
