"""
Tests for the footer component.

This module tests the footer component implementation, schema compliance,
and all its variants including centered layout and different elements.
"""

import pytest

from .test_base import ComponentTestBase, ComponentTestTemplate


class TestFooterComponent(ComponentTestTemplate):
    """Test the footer component"""

    component_name = "footer"

    def test_footer_default_rendering(self):
        """Test footer component renders with defaults"""
        html = self.render_component(
            "footer",
            slot_content='<div><span class="footer-title">Services</span></div>',
        )

        # Should have base footer class
        self.assert_classes_present(html, {"footer"})

        # Should be a footer element by default
        assert "<footer" in html
        assert "Services" in html

    def test_footer_as_attribute(self):
        """Test footer can render as different elements"""
        elements = ["footer", "div", "section"]

        for element in elements:
            html = self.render_component(
                "footer",
                **{"as": element},
                slot_content="<p>Footer content</p>",
            )
            assert f"<{element}" in html

    def test_footer_center(self):
        """Test footer with centered layout"""
        html = self.render_component(
            "footer",
            center=True,
            slot_content="<p>Centered footer</p>",
        )

        self.assert_classes_present(html, {"footer", "footer-center"})

    def test_footer_custom_classes(self):
        """Test footer with custom CSS classes"""
        html = self.render_component(
            "footer",
            class_="bg-neutral text-neutral-content p-10",
            slot_content="<p>Footer</p>",
        )

        self.assert_classes_present(
            html, {"footer", "bg-neutral", "text-neutral-content", "p-10"}
        )

    def test_footer_combined_attributes(self):
        """Test combining multiple footer attributes"""
        html = self.render_component(
            "footer",
            center=True,
            class_="custom-footer",
            slot_content="<p>Combined Footer</p>",
        )

        self.assert_classes_present(html, {"footer", "footer-center", "custom-footer"})

    def test_footer_not_centered_by_default(self):
        """Test that footer is not centered by default"""
        html = self.render_component(
            "footer",
            slot_content="<p>Footer</p>",
        )

        classes = self.extract_classes_from_html(html)
        assert "footer" in classes
        assert "footer-center" not in classes

    def test_footer_direction_horizontal(self):
        """Test footer with horizontal direction"""
        html = self.render_component(
            "footer",
            direction="horizontal",
            slot_content="<p>Footer</p>",
        )

        self.assert_classes_present(html, {"footer", "footer-horizontal"})

    def test_footer_direction_vertical(self):
        """Test footer with vertical direction"""
        html = self.render_component(
            "footer",
            direction="vertical",
            slot_content="<p>Footer</p>",
        )

        self.assert_classes_present(html, {"footer", "footer-vertical"})

    def test_footer_direction_default(self):
        """Test that footer has horizontal direction by default"""
        html = self.render_component(
            "footer",
            slot_content="<p>Footer</p>",
        )

        self.assert_classes_present(html, {"footer", "footer-horizontal"})

    def test_footer_direction_and_center_combined(self):
        """Test footer with both direction and center attributes"""
        html = self.render_component(
            "footer",
            center=True,
            direction="vertical",
            slot_content="<p>Footer</p>",
        )

        self.assert_classes_present(
            html, {"footer", "footer-center", "footer-vertical"}
        )

    def test_footer_complex_content(self):
        """Test footer with complex multi-column content"""
        content = """
        <div>
            <c-lb.footer.title>Services</c-lb.footer.title>
            <a class="link link-hover">Branding</a>
            <a class="link link-hover">Design</a>
        </div>
        <div>
            <c-lb.footer.title>Company</c-lb.footer.title>
            <a class="link link-hover">About us</a>
            <a class="link link-hover">Contact</a>
        </div>
        """

        html = self.render_component("footer", slot_content=content)

        assert "Services" in html
        assert "Company" in html
        assert "Branding" in html
        assert "About us" in html
        assert "footer-title" in html

    def test_footer_attributes_passed_through(self):
        """Test that HTML attributes are passed through correctly"""
        html = self.render_component(
            "footer",
            id="main-footer",
            **{"data-theme": "dark"},
            slot_content="<p>Footer</p>",
        )

        self.assert_attributes_present(html, {"id": "main-footer"})
        assert 'data-theme="dark"' in html

    def test_footer_as_div(self):
        """Test footer rendered as div element"""
        html = self.render_component(
            "footer",
            **{"as": "div"},
            slot_content="<p>Footer as div</p>",
        )

        assert "<div" in html
        self.assert_classes_present(html, {"footer"})

    def test_footer_empty_content(self):
        """Test footer with empty content"""
        html = self.render_component("footer", slot_content="")

        assert "<footer" in html
        assert "footer" in html


class TestFooterSchemaCompliance(ComponentTestBase):
    """Test footer component against its schema definition"""

    def test_footer_schema_variables(self):
        """Test footer schema has all expected variables"""
        schema = self.get_component_schema("footer")

        expected_variables = {"class", "as", "center", "direction"}

        assert "variables" in schema
        for var_name in expected_variables:
            assert var_name in schema["variables"], (
                f"Variable '{var_name}' missing from footer schema"
            )

    def test_footer_as_default(self):
        """Test footer default element type from schema"""
        schema = self.get_component_schema("footer")

        if "variables" in schema and "as" in schema["variables"]:
            as_var = schema["variables"]["as"]
            default_as = as_var.get("default", "footer")

            html = self.render_component("footer", slot_content="<p>Test</p>")
            assert f"<{default_as}" in html

    def test_footer_center_default(self):
        """Test footer center default from schema"""
        schema = self.get_component_schema("footer")

        if "variables" in schema and "center" in schema["variables"]:
            center_var = schema["variables"]["center"]
            default_center = center_var.get("default", False)

            html = self.render_component("footer", slot_content="<p>Test</p>")
            classes = self.extract_classes_from_html(html)

            if default_center:
                assert "footer-center" in classes
            else:
                assert "footer-center" not in classes

    def test_footer_direction_mappings(self):
        """Test that schema direction mappings work correctly"""
        schema = self.get_component_schema("footer")

        if "variables" in schema and "direction" in schema["variables"]:
            direction_var = schema["variables"]["direction"]
            if "css_mapping" in direction_var:
                for direction, css_class in direction_var["css_mapping"].items():
                    html = self.render_component(
                        "footer", direction=direction, slot_content="<p>Test</p>"
                    )
                    self.assert_classes_present(html, {"footer", css_class})

    def test_footer_base_classes(self):
        """Test footer has correct base classes from schema"""
        schema = self.get_component_schema("footer")

        if "base_classes" in schema:
            html = self.render_component("footer", slot_content="<p>Test</p>")
            self.assert_classes_present(html, set(schema["base_classes"]))


# Test fixtures
@pytest.fixture
def footer_variants():
    """Fixture providing various footer configurations"""
    return {
        "basic": {"class_": "bg-neutral text-neutral-content p-10"},
        "centered": {"center": True, "class_": "bg-base-200 p-4"},
        "as_div": {"as": "div", "class_": "footer-custom"},
        "centered_section": {
            "center": True,
            "as": "section",
            "class_": "bg-base-300",
        },
    }


@pytest.fixture
def footer_test_content():
    """Fixture providing different footer content types"""
    return {
        "simple": "<p>Copyright © 2024</p>",
        "multi_column": """
            <div><c-lb.footer.title>Services</c-lb.footer.title></div>
            <div><c-lb.footer.title>Company</c-lb.footer.title></div>
        """,
        "with_links": """
            <div>
                <c-lb.footer.title>Quick Links</c-lb.footer.title>
                <a class="link link-hover">Home</a>
                <a class="link link-hover">About</a>
            </div>
        """,
        "empty": "",
    }


class TestFooterTitleComponent(ComponentTestTemplate):
    """Test the footer.title sub-component"""

    component_name = "footer.title"

    def test_footer_title_default_rendering(self):
        """Test footer.title component renders with defaults"""
        html = self.render_component("footer.title", slot_content="Services")

        # Should have base footer-title class
        self.assert_classes_present(html, {"footer-title"})

        # Should be a span element by default
        assert "<span" in html
        assert "Services" in html

    def test_footer_title_as_attribute(self):
        """Test footer.title can render as different elements"""
        elements = ["span", "h2", "h3", "h4", "h5", "h6", "div", "p"]

        for element in elements:
            html = self.render_component(
                "footer.title",
                **{"as": element},
                slot_content="Title",
            )
            assert f"<{element}" in html
            self.assert_classes_present(html, {"footer-title"})

    def test_footer_title_custom_classes(self):
        """Test footer.title with custom CSS classes"""
        html = self.render_component(
            "footer.title",
            class_="text-primary font-bold",
            slot_content="Custom Title",
        )

        self.assert_classes_present(html, {"footer-title", "text-primary", "font-bold"})

    def test_footer_title_attributes_passed_through(self):
        """Test that HTML attributes are passed through correctly"""
        html = self.render_component(
            "footer.title",
            id="services-title",
            **{"data-section": "services"},
            slot_content="Services",
        )

        self.assert_attributes_present(html, {"id": "services-title"})
        assert 'data-section="services"' in html

    def test_footer_title_as_heading(self):
        """Test footer.title rendered as heading element"""
        html = self.render_component(
            "footer.title",
            **{"as": "h3"},
            slot_content="Section Title",
        )

        assert "<h3" in html
        self.assert_classes_present(html, {"footer-title"})
        assert "Section Title" in html


class TestFooterTitleSchemaCompliance(ComponentTestBase):
    """Test footer.title component against its schema definition"""

    def test_footer_title_schema_variables(self):
        """Test footer.title schema has all expected variables"""
        schema = self.get_component_schema("footer.title")

        expected_variables = {"class", "as"}

        assert "variables" in schema
        for var_name in expected_variables:
            assert var_name in schema["variables"], (
                f"Variable '{var_name}' missing from footer.title schema"
            )

    def test_footer_title_as_default(self):
        """Test footer.title default element type from schema"""
        schema = self.get_component_schema("footer.title")

        if "variables" in schema and "as" in schema["variables"]:
            as_var = schema["variables"]["as"]
            default_as = as_var.get("default", "span")

            html = self.render_component("footer.title", slot_content="Test")
            assert f"<{default_as}" in html

    def test_footer_title_base_classes(self):
        """Test footer.title has correct base classes from schema"""
        schema = self.get_component_schema("footer.title")

        if "base_classes" in schema:
            html = self.render_component("footer.title", slot_content="Test")
            self.assert_classes_present(html, set(schema["base_classes"]))
