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

    def test_button_with_icon(self):
        """Test button renders with icon"""
        html = self.render_component("button", icon="rmx.home", slot_content="Home")

        # Should contain the icon component or SVG content
        assert 'is="lbi"' in html or "<svg" in html
        assert "Home" in html

    def test_button_with_filled_icon(self):
        """Test button renders with filled icon"""
        html = self.render_component(
            "button", icon="rmx.star", iconFill=True, slot_content="Favorite"
        )

        # Should contain the icon component or SVG content
        assert 'is="lbi"' in html or "<svg" in html
        assert "Favorite" in html

    def test_button_icon_only(self):
        """Test button with only icon (no text)"""
        html = self.render_component("button", icon="rmx.home", modifier="circle")

        # Should contain the icon component or SVG content
        assert 'is="lbi"' in html or "<svg" in html
        assert "btn-circle" in html

    def test_button_with_icon_class(self):
        """Test button with icon and custom icon class"""
        html = self.render_component(
            "button", icon="rmx.add", iconClass="text-warning", slot_content="Test"
        )
        self.assert_classes_present(html, {"btn"})
        # Should contain the icon component with custom class
        assert 'is="lbi"' in html or "<svg" in html


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
            "iconFill",
            "iconClass",
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
