"""
NOTE: Rendering tests must come before unit tests in this file.
Django's template engine initialises lazily; render_component registers the
temp dir before the first render_to_string call. Any test that calls
get_template() first would initialise the engine without that dir, breaking
all subsequent render_component calls.
"""

import logging
from unittest.mock import patch

import pytest
from django.template import TemplateDoesNotExist
from django.test import override_settings

from labb.templatetags.lb_tags import lb_icon_exists

from .test_base import ComponentTestBase


class TestIconRenderingGracefulDegradation(ComponentTestBase):
    @override_settings(DEBUG=False)
    def test_button_with_valid_icon_renders_svg(self):
        html = self.render_component(
            "button", slot_content="Click me", **{"icon": "rmx.heart"}
        )
        assert "<button" in html
        assert "<svg" in html

    @override_settings(DEBUG=False)
    def test_button_with_nonexistent_icon_renders_without_crash(self):
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
        html = self.render_component(
            "button",
            slot_content="X",
            **{"icon": "rmx.this_icon_does_not_exist_xyz"},
        )
        assert "cannot unpack non-iterable NoneType" not in html
        assert "TypeError" not in html

    @override_settings(DEBUG=True)
    def test_button_with_nonexistent_icon_raises_in_debug(self):
        html = self.render_component(
            "button",
            slot_content="Click me",
            **{"icon": "rmx.this_icon_does_not_exist_xyz"},
        )
        assert "Component rendering error" in html
        assert "rmx.this_icon_does_not_exist_xyz" in html
        assert "TypeError" not in html


class TestLbIconExistsFilter:
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
        with patch(
            "labb.templatetags.lb_tags.get_template",
            side_effect=TemplateDoesNotExist("cotton/lbi/rmx/heart.html"),
        ):
            assert lb_icon_exists("rmx.heart") is False

    @override_settings(DEBUG=False)
    def test_missing_template_logs_warning(self, caplog):
        with caplog.at_level(logging.WARNING, logger="labb.icons"):
            with patch(
                "labb.templatetags.lb_tags.get_template",
                side_effect=TemplateDoesNotExist("cotton/lbi/rmx/heart.html"),
            ):
                lb_icon_exists("rmx.heart")
        assert any("rmx.heart" in r.message for r in caplog.records)

    @override_settings(DEBUG=False)
    def test_labbicons_not_installed_logs_different_warning(self, caplog):
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
        with pytest.raises(ValueError, match="rmx.this_icon_does_not_exist_xyz"):
            lb_icon_exists("rmx.this_icon_does_not_exist_xyz")

    @override_settings(DEBUG=True)
    def test_missing_template_raises_value_error_in_debug(self):
        with patch(
            "labb.templatetags.lb_tags.get_template",
            side_effect=TemplateDoesNotExist("cotton/lbi/rmx/heart.html"),
        ):
            with pytest.raises(ValueError, match="rmx.heart"):
                lb_icon_exists("rmx.heart")

    @override_settings(DEBUG=True)
    def test_labbicons_not_installed_raises_with_install_hint_in_debug(self):
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
