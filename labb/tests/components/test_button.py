"""
Tests for the button component.

This module tests the button component implementation, schema compliance,
and all its variants including styles, sizes, and behaviors.
"""

import pytest

from .test_base import ComponentTestBase, ComponentTestTemplate


class TestButtonComponent(ComponentTestTemplate):
    """Test the button component"""

    component_name = "button"

    def test_button_default_rendering(self):
        """Test button component renders with defaults"""
        html = self.render_component("button", slot_content="Click me")

        # Should have base btn class and default size
        self.assert_classes_present(html, {"btn", "btn-md"})

        # Should be a button element by default
        assert "<button" in html
        assert "Click me" in html

    def test_button_as_attribute(self):
        """Test button can render as different elements"""
        elements = ["button", "a", "input", "div"]

        for element in elements:
            html = self.render_component(
                "button", **{"as": element}, slot_content="Test"
            )
            assert f"<{element}" in html

    def test_button_variants(self):
        """Test all button color variants"""
        variants = {
            "neutral": "btn-neutral",
            "primary": "btn-primary",
            "secondary": "btn-secondary",
            "accent": "btn-accent",
            "info": "btn-info",
            "success": "btn-success",
            "warning": "btn-warning",
            "error": "btn-error",
        }

        for variant, expected_class in variants.items():
            html = self.render_component("button", variant=variant, slot_content="Test")
            self.assert_classes_present(html, {"btn", expected_class})

    def test_button_styles(self):
        """Test all button style variants"""
        styles = {
            "outline": "btn-outline",
            "dash": "btn-dash",
            "soft": "btn-soft",
            "ghost": "btn-ghost",
            "link": "btn-link",
        }

        for style, expected_class in styles.items():
            html = self.render_component("button", btnStyle=style, slot_content="Test")
            self.assert_classes_present(html, {"btn", expected_class})

    def test_button_bare_style(self):
        """Test bare style strips all btn classes"""
        html = self.render_component("button", btnStyle="bare", slot_content="Bare")
        assert "<button" in html
        assert "Bare" in html
        assert "btn " not in html
        assert "btn-md" not in html

    def test_button_sizes(self):
        """Test all button sizes"""
        sizes = ["xs", "sm", "md", "lg", "xl"]

        for size in sizes:
            html = self.render_component("button", size=size, slot_content="Test")
            self.assert_classes_present(html, {"btn", f"btn-{size}"})

    def test_button_behaviors(self):
        """Test button behavior states"""
        behaviors = {"active": "btn-active", "disabled": "btn-disabled"}

        for behavior, expected_class in behaviors.items():
            html = self.render_component(
                "button", behavior=behavior, slot_content="Test"
            )
            self.assert_classes_present(html, {"btn", expected_class})

    def test_button_modifiers(self):
        """Test button layout modifiers"""
        modifiers = {
            "wide": "btn-wide",
            "block": "btn-block",
            "square": "btn-square",
            "circle": "btn-circle",
        }

        for modifier, expected_class in modifiers.items():
            html = self.render_component(
                "button", modifier=modifier, slot_content="Test"
            )
            self.assert_classes_present(html, {"btn", expected_class})

    def test_button_combined_attributes(self):
        """Test combining multiple button attributes"""
        html = self.render_component(
            "button",
            variant="primary",
            btnStyle="outline",
            size="lg",
            modifier="wide",
            class_="custom-btn",
            slot_content="Combined Button",
        )

        self.assert_classes_present(
            html,
            {"btn", "btn-primary", "btn-outline", "btn-lg", "btn-wide", "custom-btn"},
        )

    def test_button_empty_attributes(self):
        """Test that empty attributes don't add classes"""
        html = self.render_component(
            "button",
            variant="",  # Empty variant
            btnStyle="",  # Empty style
            slot_content="Test",
        )

        # Should only have base classes, no variant/style classes
        classes = self.extract_classes_from_html(html)
        assert "btn" in classes
        assert "btn-md" in classes  # Default size

        # Should not have incomplete classes (classes ending with dash but no value)
        for cls in classes:
            assert not (cls.endswith("-") or "--" in cls), (
                f"Found incomplete class: {cls}"
            )

    def test_button_attributes_passed_through(self):
        """Test that HTML attributes are passed through correctly"""
        html = self.render_component(
            "button",
            id="test-btn",
            type="submit",
            title="Test button",
            slot_content="Submit",
        )

        self.assert_attributes_present(
            html, {"id": "test-btn", "type": "submit", "title": "Test button"}
        )

    def test_button_link_variant(self):
        """Test button as link with href"""
        html = self.render_component(
            "button",
            **{"as": "a"},
            href="/contact",
            variant="primary",
            slot_content="Contact",
        )

        assert "<a" in html
        assert 'href="/contact"' in html
        self.assert_classes_present(html, {"btn", "btn-primary"})

    # --- Icon dot-notation tests ---

    def test_button_with_icon(self):
        """Test button renders with icon using icon='name' syntax"""
        html = self.render_component("button", icon="rmx.home", slot_content="Home")

        assert "<svg" in html
        assert "Home" in html

    def test_button_with_icon_fill(self):
        """Test button renders with filled icon using icon.fill='name'"""
        html = self.render_template_string(
            '{% load lb_tags %}<c-lb.button icon.fill="rmx.home">Home</c-lb.button>'
        )

        assert "<svg" in html
        assert "Home" in html

    def test_button_with_icon_end(self):
        """Test button renders with icon at end using icon.end='name'"""
        html = self.render_template_string(
            '{% load lb_tags %}<c-lb.button icon.end="rmx.home">Home</c-lb.button>'
        )

        assert "<svg" in html
        assert "Home" in html
        # Icon should appear after the text content
        svg_pos = html.find("<svg")
        text_pos = html.find("Home")
        assert text_pos < svg_pos, "Icon should appear after text when using icon.end"

    def test_button_with_icon_fill_end(self):
        """Test button with icon.fill.end='name'"""
        html = self.render_template_string(
            '{% load lb_tags %}<c-lb.button icon.fill.end="rmx.home">Home</c-lb.button>'
        )

        assert "<svg" in html
        assert "Home" in html
        svg_pos = html.find("<svg")
        text_pos = html.find("Home")
        assert text_pos < svg_pos, (
            "Icon should appear after text when using icon.fill.end"
        )

    def test_button_with_icon_end_fill(self):
        """Test button with icon.end.fill='name' (reversed order)"""
        html = self.render_template_string(
            '{% load lb_tags %}<c-lb.button icon.end.fill="rmx.home">Home</c-lb.button>'
        )

        assert "<svg" in html
        assert "Home" in html
        svg_pos = html.find("<svg")
        text_pos = html.find("Home")
        assert text_pos < svg_pos, (
            "Icon should appear after text when using icon.end.fill"
        )

    def test_button_with_icon_class(self):
        """Test button with icon and icon.class"""
        html = self.render_template_string(
            '{% load lb_tags %}<c-lb.button icon="rmx.home" icon.class="text-warning">Test</c-lb.button>'
        )

        assert "<svg" in html
        assert "text-warning" in html

    def test_button_icon_only(self):
        """Test button with only icon (no text)"""
        html = self.render_component("button", icon="rmx.home", modifier="circle")

        assert "<svg" in html
        assert "btn-circle" in html

    def test_button_icon_attrs_stripped_from_element(self):
        """Test that icon.* attrs don't leak onto the button element"""
        html = self.render_template_string(
            '{% load lb_tags %}<c-lb.button icon.fill="rmx.home" icon.class="text-red" id="my-btn">Test</c-lb.button>'
        )

        assert 'id="my-btn"' in html
        # icon.fill and icon.class should NOT appear on the button element itself
        assert "icon.fill=" not in html
        assert "icon.class=" not in html


class TestButtonSchemaCompliance(ComponentTestBase):
    """Test button component against its schema definition"""

    def test_button_schema_variables(self):
        """Test button schema has all expected variables"""
        schema = self.get_component_schema("button")

        expected_variables = {
            "class",
            "as",
            "variant",
            "btnStyle",
            "behavior",
            "size",
            "modifier",
            "icon",
            "icon.class",
        }

        assert "variables" in schema
        for var_name in expected_variables:
            assert var_name in schema["variables"], (
                f"Variable '{var_name}' missing from button schema"
            )

    def test_button_variant_mappings(self):
        """Test that schema variant mappings work correctly"""
        schema = self.get_component_schema("button")

        if "variables" in schema and "variant" in schema["variables"]:
            variant_var = schema["variables"]["variant"]
            if "css_mapping" in variant_var:
                for variant, css_class in variant_var["css_mapping"].items():
                    html = self.render_component(
                        "button", variant=variant, slot_content="Test"
                    )
                    self.assert_classes_present(html, {"btn", css_class})

    def test_button_size_defaults(self):
        """Test button default size from schema"""
        schema = self.get_component_schema("button")

        if "variables" in schema and "size" in schema["variables"]:
            size_var = schema["variables"]["size"]
            default_size = size_var.get("default", "md")

            html = self.render_component("button", slot_content="Test")
            self.assert_classes_present(html, {"btn", f"btn-{default_size}"})

    def test_button_as_default(self):
        """Test button default element type from schema"""
        schema = self.get_component_schema("button")

        if "variables" in schema and "as" in schema["variables"]:
            as_var = schema["variables"]["as"]
            default_as = as_var.get("default", "button")

            html = self.render_component("button", slot_content="Test")
            assert f"<{default_as}" in html


# --- Tests for parse_icon and strip_icon_attrs ---


class TestParseIconTag(ComponentTestBase):
    """Test the parse_icon template tag logic directly"""

    def test_parse_icon_basic(self):
        """Test parsing icon='name' from attrs string"""
        from labb.templatetags.lb_tags import parse_icon

        result = parse_icon('icon="rmx.home" id="btn"')
        assert result["name"] == "rmx.home"
        assert result["fill"] is False
        assert result["end"] is False

    def test_parse_icon_fill(self):
        """Test parsing icon.fill='name'"""
        from labb.templatetags.lb_tags import parse_icon

        result = parse_icon('icon.fill="rmx.home"')
        assert result["name"] == "rmx.home"
        assert result["fill"] is True
        assert result["end"] is False

    def test_parse_icon_end(self):
        """Test parsing icon.end='name'"""
        from labb.templatetags.lb_tags import parse_icon

        result = parse_icon('icon.end="rmx.home"')
        assert result["name"] == "rmx.home"
        assert result["fill"] is False
        assert result["end"] is True

    def test_parse_icon_fill_end(self):
        """Test parsing icon.fill.end='name'"""
        from labb.templatetags.lb_tags import parse_icon

        result = parse_icon('icon.fill.end="rmx.home"')
        assert result["name"] == "rmx.home"
        assert result["fill"] is True
        assert result["end"] is True

    def test_parse_icon_end_fill(self):
        """Test parsing icon.end.fill='name' (reversed order)"""
        from labb.templatetags.lb_tags import parse_icon

        result = parse_icon('icon.end.fill="rmx.home"')
        assert result["name"] == "rmx.home"
        assert result["fill"] is True
        assert result["end"] is True

    def test_parse_icon_class(self):
        """Test parsing icon.class='classes'"""
        from labb.templatetags.lb_tags import parse_icon

        result = parse_icon('icon="rmx.home" icon.class="text-red-500"')
        assert result["name"] == "rmx.home"
        assert result["css_class"] == "text-red-500"

    def test_parse_icon_empty(self):
        """Test parsing with no icon attrs"""
        from labb.templatetags.lb_tags import parse_icon

        result = parse_icon('id="btn" class="foo"')
        assert result["name"] == ""
        assert result["fill"] is False
        assert result["end"] is False
        assert result["css_class"] == ""

    def test_parse_icon_none(self):
        """Test parsing with None/empty attrs"""
        from labb.templatetags.lb_tags import parse_icon

        result = parse_icon("")
        assert result["name"] == ""

        result = parse_icon()
        assert result["name"] == ""

    def test_strip_icon_attrs(self):
        """Test stripping icon attrs from attrs string"""
        from labb.templatetags.lb_tags import strip_icon_attrs

        result = strip_icon_attrs('icon.fill="rmx.home" icon.class="text-red" id="btn"')
        assert "icon" not in result
        assert 'id="btn"' in result

    def test_strip_icon_attrs_preserves_non_icon(self):
        """Test that non-icon attributes are preserved"""
        from labb.templatetags.lb_tags import strip_icon_attrs

        result = strip_icon_attrs('icon="rmx.home" id="btn" data-x="y"')
        assert 'id="btn"' in result
        assert 'data-x="y"' in result
        assert "icon" not in result


# Test fixtures
@pytest.fixture
def button_variants():
    """Fixture providing various button configurations"""
    return {
        "primary_large": {"variant": "primary", "size": "lg"},
        "outline_secondary": {"variant": "secondary", "btnStyle": "outline"},
        "ghost_small": {"btnStyle": "ghost", "size": "sm"},
        "wide_success": {"variant": "success", "modifier": "wide"},
        "circle_icon": {"modifier": "circle", "size": "lg"},
    }


@pytest.fixture
def button_test_content():
    """Fixture providing different button content types"""
    return {
        "text": "Click me",
        "html": '<span class="icon">📱</span> Mobile',
        "long_text": "This is a very long button text to test wrapping",
        "empty": "",
    }
