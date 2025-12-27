"""
Tests for the tabs component and its sub-components.

This module tests the tabs component implementation, schema compliance,
and rendering behavior including all variants and states.
"""

from .test_base import ComponentTestBase, ComponentTestTemplate


class TestTabsComponent(ComponentTestTemplate):
    """Test the main tabs wrapper component"""

    component_name = "tabs"

    def test_tabs_default_rendering(self):
        """Test tabs component renders with default attributes"""
        html = self.render_component("tabs", name="test_tabs")

        # Should have base tabs class
        self.assert_classes_present(html, {"tabs"})

        # Should not have style classes by default
        assert "tabs-border" not in html
        assert "tabs-lift" not in html
        assert "tabs-box" not in html

    def test_tabs_style_variants(self):
        """Test all tabs style variants"""
        styles = {"border": "tabs-border", "lift": "tabs-lift", "box": "tabs-box"}

        for style, expected_class in styles.items():
            html = self.render_component("tabs", name="test", style=style)
            self.assert_classes_present(html, {"tabs", expected_class})

    def test_tabs_size_variants(self):
        """Test all tabs size variants"""
        sizes = ["xs", "sm", "md", "lg", "xl"]

        for size in sizes:
            html = self.render_component("tabs", name="test", size=size)
            self.assert_classes_present(html, {"tabs", f"tabs-{size}"})

    def test_tabs_placement_bottom(self):
        """Test bottom placement variant"""
        html = self.render_component("tabs", name="test", placement="bottom")
        self.assert_classes_present(html, {"tabs", "tabs-bottom"})

    def test_tabs_placement_top_default(self):
        """Test that top placement is default (no extra class)"""
        html = self.render_component("tabs", name="test", placement="top")
        self.assert_classes_present(html, {"tabs"})
        assert "tabs-bottom" not in html

    def test_tabs_custom_class(self):
        """Test custom CSS class addition"""
        html = self.render_component("tabs", name="test", class_="custom-tabs")
        self.assert_classes_present(html, {"tabs", "custom-tabs"})

    def test_tabs_combined_attributes(self):
        """Test combination of multiple attributes"""
        html = self.render_component(
            "tabs",
            name="combined_test",
            style="border",
            size="lg",
            placement="bottom",
            class_="custom-class",
        )
        self.assert_classes_present(
            html, {"tabs", "tabs-border", "tabs-lg", "tabs-bottom", "custom-class"}
        )


class TestTabsContentComponent(ComponentTestTemplate):
    """Test the tabs content/item component"""

    component_name = "tabs.content"

    def test_tabs_content_default_rendering(self):
        """Test tabs content component renders with defaults"""
        html = self.render_component("tabs.content", name="test_tabs", title="Test Tab")

        # Should have tab-content class
        self.assert_classes_present(html, {"tab-content"})

        # Should have radio input with correct name
        assert 'type="radio"' in html
        assert 'name="test_tabs"' in html
        assert "Test Tab" in html

    def test_tabs_content_checked_state(self):
        """Test checked/active state"""
        html = self.render_component(
            "tabs.content", name="test_tabs", title="Active Tab", checked="true"
        )

        # Should have active class and checked attribute
        self.assert_classes_present(html, {"tab-content", "tab-active"})
        assert 'checked="checked"' in html

    def test_tabs_content_disabled_state(self):
        """Test disabled state"""
        html = self.render_component(
            "tabs.content", name="test_tabs", title="Disabled Tab", disabled="true"
        )

        # Should have disabled class and attribute
        self.assert_classes_present(html, {"tab-content", "tab-disabled"})
        assert "disabled" in html

    def test_tabs_content_with_slot_content(self):
        """Test tabs content with slot content"""
        slot_content = '<div class="p-4">Tab content here</div>'
        html = self.render_component(
            "tabs.content",
            name="test_tabs",
            title="Content Tab",
            slot_content=slot_content,
        )

        assert slot_content in html
        assert "Tab content here" in html

    def test_tabs_content_custom_class(self):
        """Test custom class addition"""
        html = self.render_component(
            "tabs.content",
            name="test_tabs",
            title="Custom Tab",
            class_="custom-tab-content",
        )

        self.assert_classes_present(html, {"tab-content", "custom-tab-content"})

    def test_tabs_content_with_icon(self):
        """Test tabs content renders with icon"""
        html = self.render_component(
            "tabs.content", name="test_tabs", title="Home", icon="rmx.home"
        )

        # Should contain the icon component or SVG content
        assert 'is="lbi"' in html or "<svg" in html
        assert "Home" in html
        # Icon should be rendered (either as component or SVG)
        assert "me-2 size-4" in html

    def test_tabs_content_with_filled_icon(self):
        """Test tabs content renders with filled icon"""
        html = self.render_component(
            "tabs.content",
            name="test_tabs",
            title="Messages",
            icon="rmx.message",
            iconFill="true",
        )

        # Should contain the icon component with fill attribute
        assert 'is="lbi"' in html or "<svg" in html
        assert "Messages" in html
        # Icon should be rendered with fill
        assert "me-2 size-4" in html

    def test_tabs_content_with_icon_class(self):
        """Test tabs content renders with custom icon class"""
        html = self.render_component(
            "tabs.content",
            name="test_tabs",
            title="Settings",
            icon="rmx.settings",
            iconClass="text-primary",
        )

        # Should contain the icon component with custom class
        assert 'is="lbi"' in html or "<svg" in html
        assert "Settings" in html
        # Icon should have custom class overriding default classes
        assert 'class="text-primary"' in html

    def test_tabs_content_icon_only(self):
        """Test tabs content with only icon (no title)"""
        html = self.render_component("tabs.content", name="test_tabs", icon="rmx.menu")

        # Should contain the icon component
        assert 'is="lbi"' in html or "<svg" in html
        # Icon should be rendered with default classes
        assert "me-2 size-4" in html


class TestTabsComponentIntegration(ComponentTestBase):
    """Integration tests for tabs component system"""

    def test_complete_tabs_structure(self):
        """Test a complete tabs structure with multiple content items"""
        # This would test the full tabs system as it would be used
        template_str = """
{% load lb_tags %}
<c-lb.tabs name="integration_test" style="lift">
    <c-lb.tabs.content name="integration_test" title="Tab 1" checked="true">
        <div class="p-6">Content 1</div>
    </c-lb.tabs.content>
    <c-lb.tabs.content name="integration_test" title="Tab 2">
        <div class="p-6">Content 2</div>
    </c-lb.tabs.content>
    <c-lb.tabs.content name="integration_test" title="Tab 3" disabled="true">
        <div class="p-6">Content 3</div>
    </c-lb.tabs.content>
</c-lb.tabs>
        """

        html = self.render_template_string(template_str)

        # Should have all expected classes and structure
        self.assert_classes_present(
            html, {"tabs", "tabs-lift", "tab-content", "tab-active", "tab-disabled"}
        )

        # Should have correct radio inputs
        assert 'name="integration_test"' in html
        assert 'checked="checked"' in html
        assert "disabled" in html

        # Should have all tab titles and content
        assert "Tab 1" in html
        assert "Tab 2" in html
        assert "Tab 3" in html
        assert "Content 1" in html
        assert "Content 2" in html
        assert "Content 3" in html

    def test_complete_tabs_structure_with_icons(self):
        """Test a complete tabs structure with icons"""
        template_str = """
{% load lb_tags %}
<c-lb.tabs name="icon_integration_test" style="lift">
    <c-lb.tabs.content name="icon_integration_test" title="Home" checked="true" icon="rmx.home">
        <div class="p-6">Home Content</div>
    </c-lb.tabs.content>
    <c-lb.tabs.content name="icon_integration_test" title="Settings" icon="rmx.settings">
        <div class="p-6">Settings Content</div>
    </c-lb.tabs.content>
    <c-lb.tabs.content name="icon_integration_test" title="Messages" icon="rmx.message" iconFill="true">
        <div class="p-6">Messages Content</div>
    </c-lb.tabs.content>
</c-lb.tabs>
        """

        html = self.render_template_string(template_str)

        # Should have all expected classes and structure
        self.assert_classes_present(
            html, {"tabs", "tabs-lift", "tab-content", "tab-active"}
        )

        # Should have correct radio inputs
        assert 'name="icon_integration_test"' in html
        assert 'checked="checked"' in html

        # Should have all tab titles and content
        assert "Home" in html
        assert "Settings" in html
        assert "Messages" in html
        assert "Home Content" in html
        assert "Settings Content" in html
        assert "Messages Content" in html

        # Should have icons with proper classes
        assert "me-2 size-4" in html
        assert 'is="lbi"' in html or "<svg" in html

    def test_tabs_accessibility(self):
        """Test tabs accessibility features"""
        html = self.render_component(
            "tabs.content", name="accessible_tabs", title="Accessible Tab"
        )

        # Should have proper radio input structure
        assert 'type="radio"' in html
        assert 'name="accessible_tabs"' in html
        assert "Accessible Tab" in html


class TestTabsSchemaCompliance(ComponentTestBase):
    """Test tabs components against their schema definitions"""

    def test_tabs_schema_variables(self):
        """Test tabs schema has all expected variables"""
        schema = self.get_component_schema("tabs")

        expected_variables = {"class", "style", "placement", "size", "name"}

        assert "variables" in schema
        for var_name in expected_variables:
            assert var_name in schema["variables"], (
                f"Variable '{var_name}' missing from tabs schema"
            )

    def test_tabs_content_schema_variables(self):
        """Test tabs.content schema has all expected variables"""
        schema = self.get_component_schema("tabs.content")

        expected_variables = {
            "class",
            "name",
            "checked",
            "disabled",
            "title",
            "icon",
            "iconFill",
            "iconClass",
        }

        assert "variables" in schema
        for var_name in expected_variables:
            assert var_name in schema["variables"], (
                f"Variable '{var_name}' missing from tabs.content schema"
            )

    def test_tabs_css_mappings(self):
        """Test that schema CSS mappings match component behavior"""
        schema = self.get_component_schema("tabs")

        # Test style mappings
        if "variables" in schema and "style" in schema["variables"]:
            style_var = schema["variables"]["style"]
            if "css_mapping" in style_var:
                for style, css_class in style_var["css_mapping"].items():
                    html = self.render_component("tabs", name="test", style=style)
                    self.assert_classes_present(html, {"tabs", css_class})

    def test_tabs_content_css_mappings(self):
        """Test tabs.content CSS mappings"""
        schema = self.get_component_schema("tabs.content")

        # Test checked mapping
        if "variables" in schema and "checked" in schema["variables"]:
            checked_var = schema["variables"]["checked"]
            if "css_mapping" in checked_var:
                for value, css_class in checked_var["css_mapping"].items():
                    if value == "true":
                        html = self.render_component(
                            "tabs.content", name="test", title="Test", checked="true"
                        )
                        self.assert_classes_present(html, {"tab-content", css_class})
