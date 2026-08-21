import sys
import types
from unittest.mock import MagicMock, patch

import pytest

from labb.contrib.blocks import BlockContextError, include_blocks, lm


def _make_frame_mock(module_name: str):
    """Helper to create a mock frame with the given module __name__."""
    mock_frame = patch("inspect.currentframe")
    return module_name, mock_frame


def _call_lm_as(module_name: str, model_name: str):
    """Call lm() simulating the caller being in the given module."""
    with patch("inspect.currentframe") as mock_cf:
        mock_cf.return_value.f_back.f_globals = {"__name__": module_name}
        return lm(model_name)


class TestLmCollectionContext:
    """Tests for 5+ part module paths (collection context)."""

    def test_lm_collection_context(self):
        """Caller in blocks.lb.crud.todos.views → imports from blocks.lb.models."""

        class FakeLbTodo:
            pass

        fake_models = types.ModuleType("blocks.lb.models")
        fake_models.LbTodo = FakeLbTodo

        with patch.dict(sys.modules, {"blocks.lb.models": fake_models}):
            result = _call_lm_as("blocks.lb.crud.todos.views", "LbTodo")
            assert result is FakeLbTodo

    def test_lm_collection_context_deep_path(self):
        """Caller with 6 parts still resolves from collection + vendor."""

        class FakeModel:
            pass

        fake_models = types.ModuleType("myapp.vendor.models")
        fake_models.VendorItem = FakeModel

        with patch.dict(sys.modules, {"myapp.vendor.models": fake_models}):
            result = _call_lm_as("myapp.vendor.crud.items.views.extra", "VendorItem")
            assert result is FakeModel

    def test_lm_returns_model_class(self):
        """lm() returns the actual class, not the module."""

        class FakeLbTodo:
            pass

        fake_models = types.ModuleType("blocks.lb.models")
        fake_models.LbTodo = FakeLbTodo

        with patch.dict(sys.modules, {"blocks.lb.models": fake_models}):
            result = _call_lm_as("blocks.lb.crud.todos.views", "LbTodo")
            assert result is FakeLbTodo
            assert isinstance(result, type)


class TestLmRendererContext:
    """Tests for exactly 4 part module paths (renderer context)."""

    def test_lm_renderer_context(self):
        """Caller in lb.crud.todos.views → imports from lb.models."""

        class FakeLbTodo:
            pass

        fake_models = types.ModuleType("lb.models")
        fake_models.LbTodo = FakeLbTodo

        with patch.dict(sys.modules, {"lb.models": fake_models}):
            result = _call_lm_as("lb.crud.todos.views", "LbTodo")
            assert result is FakeLbTodo

    def test_lm_renderer_context_different_vendor(self):
        """Renderer context works with different vendor namespaces."""

        class FakeItem:
            pass

        fake_models = types.ModuleType("acme.models")
        fake_models.AcmeItem = FakeItem

        with patch.dict(sys.modules, {"acme.models": fake_models}):
            result = _call_lm_as("acme.catalog.products.views", "AcmeItem")
            assert result is FakeItem


class TestLmOutsideContext:
    """Tests for fewer than 4 part module paths — must raise BlockContextError."""

    def test_lm_outside_context_raises(self):
        """Caller in myapp.views (2 parts) raises BlockContextError."""
        with pytest.raises(BlockContextError):
            _call_lm_as("myapp.views", "LbTodo")

    def test_lm_top_level_module_raises(self):
        """Caller in a single-part module name raises BlockContextError."""
        with pytest.raises(BlockContextError):
            _call_lm_as("views", "LbTodo")

    def test_lm_three_part_path_raises(self):
        """Caller in a 3-part path (myapp.some.views) raises BlockContextError."""
        with pytest.raises(BlockContextError):
            _call_lm_as("myapp.some.views", "LbTodo")

    def test_lm_error_message_contains_replacement(self):
        """Error message includes a replacement import statement."""
        with pytest.raises(BlockContextError) as exc_info:
            _call_lm_as("myapp.views", "LbTodo")

        assert "from myapp.models import LbTodo" in str(exc_info.value)

    def test_lm_error_message_contains_detected_module(self):
        """Error message includes the detected module path."""
        with pytest.raises(BlockContextError) as exc_info:
            _call_lm_as("myapp.views", "LbTodo")

        assert "myapp.views" in str(exc_info.value)

    def test_lm_error_message_format(self):
        """Error message contains all three expected parts."""
        with pytest.raises(BlockContextError) as exc_info:
            _call_lm_as("myapp.views", "LbTodo")

        message = str(exc_info.value)
        assert "lm('LbTodo') cannot resolve outside a blocks collection" in message
        assert "from myapp.models import LbTodo" in message
        assert "(Detected module: myapp.views)" in message


# ---------------------------------------------------------------------------
# Helpers for include_blocks tests
# ---------------------------------------------------------------------------


def make_fake_collection(tmp_path, name="blocks"):
    """Create a fake collection directory and module."""
    (tmp_path / "lb" / "crud" / "todos").mkdir(parents=True)
    (tmp_path / "lb" / "crud" / "todos" / "urls.py").write_text("# urls")
    (tmp_path / "lb" / "crud" / "contacts").mkdir(parents=True)
    (tmp_path / "lb" / "crud" / "contacts" / "urls.py").write_text("# urls")
    (tmp_path / "lb" / "models").mkdir(
        parents=True
    )  # should be skipped (category skip)
    (tmp_path / "templates").mkdir()  # should be skipped (vendor skip)
    (tmp_path / "migrations").mkdir()  # should be skipped (vendor skip)

    mod = types.ModuleType(name)
    mod.__path__ = [str(tmp_path)]
    mod.__name__ = name
    return mod


class TestIncludeBlocksAutoDiscovery:
    """Tests for include_blocks(collection) — auto-discovery mode."""

    def test_include_blocks_auto_discovers_all_blocks(self, tmp_path):
        """Finds todos and contacts; skips models, templates, migrations."""
        collection = make_fake_collection(tmp_path)

        mock_include = MagicMock(side_effect=lambda m: f"included:{m}")
        mock_path = MagicMock(side_effect=lambda prefix, inc: (prefix, inc))

        with (
            patch("django.urls.include", mock_include),
            patch("django.urls.path", mock_path),
        ):
            result = include_blocks(collection)

        assert len(result) == 2
        prefixes = {r[0] for r in result}
        assert "lb/crud/contacts/" in prefixes
        assert "lb/crud/todos/" in prefixes

    def test_include_blocks_returns_correct_prefixes(self, tmp_path):
        """Each discovered block is mounted at vendor/category/slug/."""
        collection = make_fake_collection(tmp_path)

        mock_include = MagicMock(side_effect=lambda m: f"included:{m}")
        mock_path = MagicMock(side_effect=lambda prefix, inc: (prefix, inc))

        with (
            patch("django.urls.include", mock_include),
            patch("django.urls.path", mock_path),
        ):
            result = include_blocks(collection)

        by_prefix = {r[0]: r[1] for r in result}
        assert by_prefix["lb/crud/todos/"] == "included:blocks.lb.crud.todos.urls"
        assert by_prefix["lb/crud/contacts/"] == "included:blocks.lb.crud.contacts.urls"

    def test_include_blocks_skips_dirs_without_urls_py(self, tmp_path):
        """A block directory that has no urls.py is silently skipped."""
        collection = make_fake_collection(tmp_path)
        # Add a slug dir with no urls.py
        (tmp_path / "lb" / "crud" / "nourls").mkdir(parents=True)

        mock_include = MagicMock(side_effect=lambda m: f"included:{m}")
        mock_path = MagicMock(side_effect=lambda prefix, inc: (prefix, inc))

        with (
            patch("django.urls.include", mock_include),
            patch("django.urls.path", mock_path),
        ):
            result = include_blocks(collection)

        prefixes = {r[0] for r in result}
        assert "lb/crud/nourls/" not in prefixes
        assert len(result) == 2

    def test_include_blocks_fe_only_skipped(self, tmp_path):
        """FE-only block dirs (no urls.py) are not mounted."""
        collection = make_fake_collection(tmp_path)
        # Add a FE-only block directory (no urls.py inside)
        (tmp_path / "lb" / "ui" / "button").mkdir(parents=True)
        # No urls.py — should be skipped

        mock_include = MagicMock(side_effect=lambda m: f"included:{m}")
        mock_path = MagicMock(side_effect=lambda prefix, inc: (prefix, inc))

        with (
            patch("django.urls.include", mock_include),
            patch("django.urls.path", mock_path),
        ):
            result = include_blocks(collection)

        prefixes = {r[0] for r in result}
        assert "lb/ui/button/" not in prefixes


class TestIncludeBlocksSingleRef:
    """Tests for include_blocks(collection, ref) — single-block mode."""

    def test_include_blocks_single_ref(self, tmp_path):
        """include_blocks(collection, "lb/crud/todos") calls include on the right module."""
        collection = make_fake_collection(tmp_path)

        mock_include = MagicMock(return_value="sentinel")

        with patch("django.urls.include", mock_include):
            result = include_blocks(collection, "lb/crud/todos")

        mock_include.assert_called_once_with("blocks.lb.crud.todos.urls")
        assert result == "sentinel"

    def test_include_blocks_single_ref_invalid_format(self, tmp_path):
        """A malformed ref (not vendor/category/slug) raises ValueError."""
        collection = make_fake_collection(tmp_path)

        with pytest.raises(ValueError, match="vendor/category/slug"):
            include_blocks(collection, "lb/todos")

    def test_include_blocks_single_ref_too_many_parts(self, tmp_path):
        """A ref with four parts raises ValueError."""
        collection = make_fake_collection(tmp_path)

        with pytest.raises(ValueError, match="vendor/category/slug"):
            include_blocks(collection, "lb/crud/todos/extra")
