from .test_base import ComponentTestBase, ComponentTestTemplate


class TestDrawerComponent(ComponentTestTemplate):
    """Test the main drawer wrapper component"""

    component_name = "drawer"

    def test_drawer_default_rendering(self):
        """Test drawer component renders with defaults"""
        html = self.render_component("drawer", drawerId="test-drawer")

        # Should have base drawer classes
        self.assert_classes_present(html, {"drawer", "drawer-toggle", "drawer-content"})

        # Should contain drawer structure elements
        assert "drawer" in html

    def test_drawer_end_placement(self):
        """Test drawer with end placement"""
        html = self.render_component("drawer", drawerId="end-drawer", end="true")

        # Should have drawer-end class
        self.assert_classes_present(html, {"drawer", "drawer-end"})

    def test_drawer_open_state(self):
        """Test drawer with open state"""
        html = self.render_component("drawer", drawerId="open-drawer", open="true")

        # Should have drawer-open class
        self.assert_classes_present(html, {"drawer", "drawer-open"})

    def test_drawer_combined_states(self):
        """Test drawer with combined end and open states"""
        html = self.render_component(
            "drawer",
            drawerId="combined-drawer",
            end="true",
            open="true",
            class_="custom-drawer",
        )

        self.assert_classes_present(
            html, {"drawer", "drawer-end", "drawer-open", "custom-drawer"}
        )

    def test_drawer_with_side_content_optional_classes(self):
        """Test that optional base classes are present when drawer has side content"""
        # Render drawer with side content to trigger optional base classes
        template_str = """
{% load lb_tags %}
<c-lb.drawer drawerId="side-drawer">
    <c-slot name="sideContent">
        <div>Sidebar content</div>
    </c-slot>
    <div>Main content</div>
</c-lb.drawer>
        """

        html = self.render_template_string(template_str)

        # Should have all base classes including optional ones
        self.assert_classes_present(
            html,
            {
                "drawer",
                "drawer-toggle",
                "drawer-content",
                "drawer-side",
                "drawer-overlay",
            },
        )

    def test_drawer_sideClass_variable(self):
        """Test drawer with sideClass variable"""
        template_str = """
{% load lb_tags %}
<c-lb.drawer drawerId="sideclass-drawer" sideClass="custom-side-class">
    <c-slot name="sideContent">
        <div>Sidebar content</div>
    </c-slot>
    <div>Main content</div>
</c-lb.drawer>
        """

        html = self.render_template_string(template_str)

        # Should have custom side class applied to drawer-side
        assert 'class="drawer-side custom-side-class"' in html

    def test_drawer_overlayClass_variable(self):
        """Test drawer with overlayClass variable"""
        template_str = """
{% load lb_tags %}
<c-lb.drawer drawerId="overlayclass-drawer" overlayClass="custom-overlay-class">
    <c-slot name="sideContent">
        <div>Sidebar content</div>
    </c-slot>
    <div>Main content</div>
</c-lb.drawer>
        """

        html = self.render_template_string(template_str)

        # Should have custom overlay class applied to drawer-overlay
        assert 'class="drawer-overlay custom-overlay-class"' in html

    def test_drawer_custom_checkbox_slot(self):
        """Test drawer with custom checkbox slot"""
        template_str = """
{% load lb_tags %}
<c-lb.drawer drawerId="custom-checkbox-drawer">
    <c-slot name="checkbox">
        <input type="checkbox" id="custom-checkbox" class="drawer-toggle" />
    </c-slot>
    <div>Main content</div>
</c-lb.drawer>
        """

        html = self.render_template_string(template_str)

        # Should use custom checkbox instead of default
        assert 'id="custom-checkbox"' in html
        assert 'class="drawer-toggle"' in html

    def test_drawer_custom_content_slot(self):
        """Test drawer with custom content slot"""
        template_str = """
{% load lb_tags %}
<c-lb.drawer drawerId="custom-content-drawer">
    <c-slot name="content">
        <main class="drawer-content custom-content">
            <h1>Custom Content</h1>
        </main>
    </c-slot>
</c-lb.drawer>
        """

        html = self.render_template_string(template_str)

        # Should use custom content instead of default
        assert '<main class="drawer-content custom-content">' in html
        assert "<h1>Custom Content</h1>" in html

    def test_drawer_custom_side_slot(self):
        """Test drawer with custom side slot"""
        template_str = """
{% load lb_tags %}
<c-lb.drawer drawerId="custom-side-drawer">
    <c-slot name="side">
        <aside class="drawer-side custom-side">
            <label class="drawer-overlay" for="custom-side-drawer"></label>
            <div>Custom Sidebar</div>
        </aside>
    </c-slot>
    <div>Main content</div>
</c-lb.drawer>
        """

        html = self.render_template_string(template_str)

        # Should use custom side instead of default
        assert '<aside class="drawer-side custom-side">' in html
        assert "Custom Sidebar" in html

    def test_drawer_default_slot_only(self):
        """Test drawer with only default slot (no side content)"""
        template_str = """
{% load lb_tags %}
<c-lb.drawer drawerId="default-only-drawer">
    <div>Only default content</div>
</c-lb.drawer>
        """

        html = self.render_template_string(template_str)

        # Should have drawer structure but no side/overlay
        assert "drawer" in html
        assert "drawer-content" in html
        assert "Only default content" in html
        # Should not have side content classes
        assert "drawer-side" not in html
        assert "drawer-overlay" not in html

    def test_drawer_sideContent_vs_side_slots(self):
        """Test that sideContent and side slots are mutually exclusive"""
        template_str = """
{% load lb_tags %}
<c-lb.drawer drawerId="both-slots-drawer">
    <c-slot name="sideContent">
        <div>SideContent slot</div>
    </c-slot>
    <c-slot name="side">
        <aside>Side slot</aside>
    </c-slot>
    <div>Main content</div>
</c-lb.drawer>
        """

        html = self.render_template_string(template_str)

        # sideContent should take precedence over side
        assert "SideContent slot" in html
        assert "Side slot" not in html


class TestDrawerContentComponent(ComponentTestTemplate):
    """Test the drawer content component"""

    component_name = "drawer.content"

    def test_drawer_content_default_rendering(self):
        """Test drawer content renders with defaults"""
        html = self.render_component("drawer.content", slot_content="Main content")

        # Should have drawer-content class
        self.assert_classes_present(html, {"drawer-content"})

        # Should be div by default
        assert "<div" in html
        assert "Main content" in html

    def test_drawer_content_as_attribute(self):
        """Test drawer content with different element types"""
        elements = ["div", "main", "section", "article"]

        for element in elements:
            html = self.render_component(
                "drawer.content", **{"as": element}, slot_content="Test"
            )
            assert f"<{element}" in html
            self.assert_classes_present(html, {"drawer-content"})

    def test_drawer_content_custom_class(self):
        """Test drawer content with custom class"""
        html = self.render_component(
            "drawer.content", class_="custom-content", slot_content="Content"
        )

        self.assert_classes_present(html, {"drawer-content", "custom-content"})


class TestDrawerSideComponent(ComponentTestTemplate):
    """Test the drawer side component"""

    component_name = "drawer.side"

    def test_drawer_side_default_rendering(self):
        """Test drawer side renders with defaults"""
        html = self.render_component("drawer.side", slot_content="Side content")

        # Should have drawer-side class
        self.assert_classes_present(html, {"drawer-side"})

        # Should be div element
        assert "<div" in html
        assert "Side content" in html

    def test_drawer_side_custom_class(self):
        """Test drawer side with custom class"""
        html = self.render_component(
            "drawer.side", class_="bg-base-200", slot_content="Sidebar"
        )

        self.assert_classes_present(html, {"drawer-side", "bg-base-200"})


class TestDrawerOverlayComponent(ComponentTestTemplate):
    """Test the drawer overlay component"""

    component_name = "drawer.overlay"

    def test_drawer_overlay_default_rendering(self):
        """Test drawer overlay renders correctly"""
        html = self.render_component("drawer.overlay")

        # Should have drawer-overlay class
        self.assert_classes_present(html, {"drawer-overlay"})

        # Should be label element with aria-label
        assert "<label" in html
        assert 'aria-label="close sidebar"' in html

    def test_drawer_overlay_custom_class(self):
        """Test drawer overlay with custom class"""
        html = self.render_component("drawer.overlay", class_="backdrop-blur")

        self.assert_classes_present(html, {"drawer-overlay", "backdrop-blur"})

    def test_drawer_overlay_with_content(self):
        """Test drawer overlay with slot content"""
        html = self.render_component("drawer.overlay", slot_content="Close")

        assert "Close" in html

    def test_drawer_overlay_with_for_attribute(self):
        """Test drawer overlay with for attribute"""
        html = self.render_component("drawer.overlay", **{"for": "test-drawer"})

        assert 'for="test-drawer"' in html


class TestDrawerToggleComponent(ComponentTestTemplate):
    """Test the drawer toggle component"""

    component_name = "drawer.toggle"

    def test_drawer_toggle_default_rendering(self):
        """Test drawer toggle renders correctly"""
        html = self.render_component("drawer.toggle", **{"for": "drawer-id"})

        # Should be label element with for attribute
        assert "<label" in html
        assert 'for="drawer-id"' in html

    def test_drawer_toggle_with_title(self):
        """Test drawer toggle with title text"""
        html = self.render_component(
            "drawer.toggle", title="Open Menu", **{"for": "menu-drawer"}
        )

        assert "Open Menu" in html
        assert 'for="menu-drawer"' in html

    def test_drawer_toggle_with_slot_content(self):
        """Test drawer toggle with slot content (overrides title)"""
        html = self.render_component(
            "drawer.toggle",
            title="Default Title",
            slot_content="<span>Custom Toggle</span>",
            **{"for": "test-drawer"},
        )

        assert "<span>Custom Toggle</span>" in html
        # Title should not appear when slot content is provided
        assert "Default Title" not in html

    def test_drawer_toggle_custom_class(self):
        """Test drawer toggle with custom class"""
        html = self.render_component(
            "drawer.toggle",
            class_="btn btn-square btn-ghost",
            **{"for": "styled-drawer"},
        )

        classes = self.extract_classes_from_html(html)
        assert "btn" in classes
        assert "btn-square" in classes
        assert "btn-ghost" in classes

    def test_drawer_toggle_without_for_attribute(self):
        """Test drawer toggle without for attribute (should still render)"""
        html = self.render_component("drawer.toggle")

        assert "<label" in html
        assert "for=" not in html


class TestDrawerCheckboxComponent(ComponentTestTemplate):
    """Test the drawer checkbox component"""

    component_name = "drawer.checkbox"

    def test_drawer_checkbox_default_rendering(self):
        """Test drawer checkbox renders correctly"""
        html = self.render_component("drawer.checkbox", id="drawer-toggle")

        # Should have drawer-toggle class
        self.assert_classes_present(html, {"drawer-toggle"})

        # Should be input checkbox with id
        assert "<input" in html
        assert 'type="checkbox"' in html
        assert 'id="drawer-toggle"' in html

    def test_drawer_checkbox_custom_class(self):
        """Test drawer checkbox with custom class"""
        html = self.render_component(
            "drawer.checkbox", class_="sr-only", id="hidden-toggle"
        )

        self.assert_classes_present(html, {"drawer-toggle", "sr-only"})

    def test_drawer_checkbox_without_id(self):
        """Test drawer checkbox without id attribute"""
        html = self.render_component("drawer.checkbox")

        # Should still render as checkbox
        assert "<input" in html
        assert 'type="checkbox"' in html
        # Should not have id attribute
        assert "id=" not in html


class TestDrawerComponentIntegration(ComponentTestBase):
    """Integration tests for the complete drawer system"""

    def test_complete_drawer_structure(self):
        """Test a complete drawer with all components"""
        template_str = """
{% load lb_tags %}
<c-lb.drawer id="integration-drawer" end="true">
    <c-lb.drawer.checkbox id="drawer-checkbox" />
    <c-lb.drawer.content>
        <div class="navbar">
            <c-lb.drawer.toggle for="drawer-checkbox" title="Open Menu" />
        </div>
        <main class="p-4">
            <h1>Main Content</h1>
        </main>
    </c-lb.drawer.content>
    <c-lb.drawer.side class="bg-base-200">
        <c-lb.drawer.overlay for="drawer-checkbox" />
        <nav class="p-4">
            <h2>Navigation</h2>
        </nav>
    </c-lb.drawer.side>
</c-lb.drawer>
        """

        html = self.render_template_string(template_str)

        # Should have all drawer-related classes
        self.assert_classes_present(
            html,
            {
                "drawer",
                "drawer-end",
                "drawer-toggle",
                "drawer-content",
                "drawer-side",
                "drawer-overlay",
            },
        )

        # Should have proper structure
        assert 'type="checkbox"' in html
        assert 'id="drawer-checkbox"' in html
        assert 'for="drawer-checkbox"' in html
        assert "Main Content" in html
        assert "Navigation" in html

    def test_drawer_accessibility(self):
        """Test drawer accessibility features"""
        # Test overlay has proper aria-label
        html = self.render_component("drawer.overlay")
        assert 'aria-label="close sidebar"' in html

        # Test toggle with proper for attribute
        html = self.render_component("drawer.toggle", **{"for": "accessible-drawer"})
        assert 'for="accessible-drawer"' in html

    def test_drawer_id_linking(self):
        """Test that drawer IDs are properly linked between components"""
        template_str = """
{% load lb_tags %}
<c-lb.drawer drawerId="linked-drawer">
    <c-lb.drawer.checkbox id="linked-checkbox" />
    <c-lb.drawer.content>
        <c-lb.drawer.toggle for="linked-checkbox" title="Toggle" />
    </c-lb.drawer.content>
    <c-lb.drawer.side>
        <c-lb.drawer.overlay for="linked-checkbox" />
        <div>Sidebar</div>
    </c-lb.drawer.side>
</c-lb.drawer>
        """

        html = self.render_template_string(template_str)

        # All components should reference the same ID
        assert 'id="linked-checkbox"' in html
        assert 'for="linked-checkbox"' in html
        # Should appear twice (toggle and overlay)
        assert html.count('for="linked-checkbox"') == 2


class TestDrawerSchemaCompliance(ComponentTestBase):
    """Test drawer components against schema definitions"""

    def test_drawer_schema_variables(self):
        """Test main drawer schema has expected variables"""
        schema = self.get_component_schema("drawer")

        expected_variables = {
            "drawerId",
            "class",
            "end",
            "open",
            "sideClass",
            "overlayClass",
        }

        assert "variables" in schema
        for var_name in expected_variables:
            assert var_name in schema["variables"], (
                f"Variable '{var_name}' missing from drawer schema"
            )

    def test_drawer_sub_component_schemas(self):
        """Test that all drawer sub-components have schemas"""
        sub_components = [
            "drawer.content",
            "drawer.side",
            "drawer.overlay",
            "drawer.toggle",
            "drawer.checkbox",
        ]

        for component_name in sub_components:
            schema = self.get_component_schema(component_name)
            assert schema is not None, f"Schema missing for {component_name}"
            assert "base_classes" in schema, (
                f"Base classes missing for {component_name}"
            )

    def test_drawer_schema_slots(self):
        """Test that drawer schema has all expected slots"""
        schema = self.get_component_schema("drawer")

        expected_slots = {"default", "checkbox", "content", "sideContent", "side"}

        assert "slots" in schema
        for slot_name in expected_slots:
            assert slot_name in schema["slots"], (
                f"Slot '{slot_name}' missing from drawer schema"
            )

    def test_drawer_content_schema_as_variable(self):
        """Test drawer.content schema has 'as' variable with correct values"""
        schema = self.get_component_schema("drawer.content")

        assert "variables" in schema
        assert "as" in schema["variables"]

        as_var = schema["variables"]["as"]
        assert as_var["type"] == "enum"
        assert set(as_var["values"]) == {"div", "main", "section", "article"}
        assert as_var["default"] == "div"
