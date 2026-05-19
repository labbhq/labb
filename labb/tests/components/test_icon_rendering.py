"""
Tests for icon rendering error handling.

Covers two failure modes:
  1. Icon name that doesn't exist in labbicons
  2. labbicons not installed (simulated by mocking get_template)

NOTE: Rendering-based tests must be defined BEFORE pure unit tests in this file.
Django's template engine is initialized lazily on first use; render_component adds
the temp dir to settings before the first render_to_string call, which is how the
engine picks it up.  Any test that calls Template() or get_template() before a
render_component call would initialize the engine without that temp dir, breaking
all subsequent render_component calls.
"""

import logging
from unittest.mock import patch

import pytest
from django.template import TemplateDoesNotExist
from django.test import override_settings

from labb.templatetags.lb_tags import lb_icon_exists

from .test_base import ComponentTestBase

# ---------------------------------------------------------------------------
# Rendering integration tests (must come first — see module docstring)
# ---------------------------------------------------------------------------


class TestIconRenderingGracefulDegradation(ComponentTestBase):
    """Production (DEBUG=False) rendering: bad icon names must not crash the component."""

    @override_settings(DEBUG=False)
    def test_button_with_valid_icon_renders_svg(self):
        """A button with a valid icon name renders the SVG."""
        html = self.render_component(
            "button",
            slot_content="Click me",
            **{"icon": "rmx.heart"},
        )
        assert "<button" in html
        assert "<svg" in html

    @override_settings(DEBUG=False)
    def test_button_with_nonexistent_icon_renders_without_crash(self):
        """Production: bad icon name renders the button; the icon is silently skipped."""
        html = self.render_component(
            "button",
            slot_content="Click me",
            **{"icon": "rmx.this_icon_does_not_exist_xyz"},
        )
        assert "<button" in html
        assert "Click me" in html
        assert "<svg" not in html

    @override_settings(DEBUG=False)
    def test_alert_with_nonexistent_icon_renders_without_crash(self):
        html = self.render_component(
            "alert",
            slot_content="Something happened",
            **{"icon": "rmx.this_icon_does_not_exist_xyz"},
        )
        assert "alert" in html
        assert "Something happened" in html
        assert "<svg" not in html

    @override_settings(DEBUG=False)
    def test_kbd_with_nonexistent_icon_renders_without_crash(self):
        html = self.render_component(
            "kbd",
            slot_content="Ctrl",
            **{"icon": "rmx.this_icon_does_not_exist_xyz"},
        )
        assert "<kbd" in html
        assert "<svg" not in html

    @override_settings(DEBUG=False)
    def test_nonexistent_icon_does_not_raise_type_error(self):
        """The cryptic 'cannot unpack non-iterable NoneType object' must not surface."""
        html = self.render_component(
            "button",
            slot_content="X",
            **{"icon": "rmx.this_icon_does_not_exist_xyz"},
        )
        assert "cannot unpack non-iterable NoneType" not in html
        assert "TypeError" not in html

    @override_settings(DEBUG=True)
    def test_button_with_nonexistent_icon_raises_in_debug(self):
        """DEBUG=True: rendering a button with a bad icon surfaces a clear ValueError."""
        html = self.render_component(
            "button",
            slot_content="Click me",
            **{"icon": "rmx.this_icon_does_not_exist_xyz"},
        )
        # render_component catches all exceptions and returns an HTML comment
        assert "Component rendering error" in html
        assert "rmx.this_icon_does_not_exist_xyz" in html
        assert "TypeError" not in html


# ---------------------------------------------------------------------------
# lb_icon_exists filter unit tests
# ---------------------------------------------------------------------------


class TestLbIconExistsFilter:
    """Unit tests for the lb_icon_exists filter (called as a plain Python function)."""

    def test_valid_icon_returns_true(self):
        assert lb_icon_exists("rmx.heart") is True

    @override_settings(DEBUG=False)
    def test_nonexistent_icon_returns_false(self):
        assert lb_icon_exists("rmx.this_icon_does_not_exist_xyz") is False

    def test_empty_string_returns_false(self):
        assert lb_icon_exists("") is False

    def test_none_returns_false(self):
        assert lb_icon_exists(None) is False

    @override_settings(DEBUG=False)
    def test_missing_template_returns_false(self):
        """When get_template raises TemplateDoesNotExist, filter returns False."""
        with patch(
            "labb.templatetags.lb_tags.get_template",
            side_effect=TemplateDoesNotExist("cotton/lbi/rmx/heart.html"),
        ):
            assert lb_icon_exists("rmx.heart") is False

    @override_settings(DEBUG=False)
    def test_missing_template_logs_warning(self, caplog):
        """A missing icon logs a labb.icons warning instead of crashing."""
        with caplog.at_level(logging.WARNING, logger="labb.icons"):
            with patch(
                "labb.templatetags.lb_tags.get_template",
                side_effect=TemplateDoesNotExist("cotton/lbi/rmx/heart.html"),
            ):
                lb_icon_exists("rmx.heart")
        assert any("rmx.heart" in r.message for r in caplog.records)

    @override_settings(DEBUG=False)
    def test_labbicons_not_installed_logs_different_warning(self, caplog):
        """When labbicons is not installed, the warning mentions the package."""
        with caplog.at_level(logging.WARNING, logger="labb.icons"):
            with patch(
                "labb.templatetags.lb_tags.get_template",
                side_effect=TemplateDoesNotExist("cotton/lbi/rmx/heart.html"),
            ):
                with patch(
                    "labb.templatetags.lb_tags.apps.is_installed",
                    return_value=False,
                ):
                    lb_icon_exists("rmx.heart")
        assert any("labbicons" in r.message for r in caplog.records)

    @override_settings(DEBUG=True)
    def test_nonexistent_icon_raises_value_error_in_debug(self):
        """DEBUG=True: a bad icon name raises ValueError with a clear message."""
        with pytest.raises(ValueError, match="rmx.this_icon_does_not_exist_xyz"):
            lb_icon_exists("rmx.this_icon_does_not_exist_xyz")

    @override_settings(DEBUG=True)
    def test_missing_template_raises_value_error_in_debug(self):
        """DEBUG=True: when get_template raises TemplateDoesNotExist, ValueError is raised."""
        with patch(
            "labb.templatetags.lb_tags.get_template",
            side_effect=TemplateDoesNotExist("cotton/lbi/rmx/heart.html"),
        ):
            with pytest.raises(ValueError, match="rmx.heart"):
                lb_icon_exists("rmx.heart")

    @override_settings(DEBUG=True)
    def test_labbicons_not_installed_raises_with_install_hint_in_debug(self):
        """DEBUG=True + labbicons missing: ValueError message mentions INSTALLED_APPS."""
        with patch(
            "labb.templatetags.lb_tags.get_template",
            side_effect=TemplateDoesNotExist("cotton/lbi/rmx/heart.html"),
        ):
            with patch(
                "labb.templatetags.lb_tags.apps.is_installed",
                return_value=False,
            ):
                with pytest.raises(ValueError, match="labbicons"):
                    lb_icon_exists("rmx.heart")
