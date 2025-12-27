"""
Tests for the FAB (Floating Action Button) component.

This module tests the FAB component implementation, schema compliance,
and all its variants including flower mode, variants, and icon integration.
"""

from .test_base import ComponentTestTemplate


class TestFabComponent(ComponentTestTemplate):
    """Test the FAB component"""

    component_name = "fab"

    def test_fab_default_rendering(self):
        """Test FAB component renders with defaults"""
        html = self.render_component("fab", label="F")

        # Should have base fab class and default size
        self.assert_classes_present(html, {"fab", "btn-lg"})

        # Should have main focusable button with proper attributes
        assert 'tabindex="0"' in html
        assert 'role="button"' in html
        assert "btn-circle" in html
        assert "F" in html

    def test_fab_variants(self):
        """Test all FAB color variants"""
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
            html = self.render_component("fab", variant=variant, label="F")
            self.assert_classes_present(html, {"fab", expected_class})

    def test_fab_sizes(self):
        """Test all FAB sizes"""
        sizes = {
            "xs": "btn-xs",
            "sm": "btn-sm",
            "md": "btn-md",
            "lg": "btn-lg",
            "xl": "btn-xl",
        }

        for size, expected_class in sizes.items():
            html = self.render_component("fab", size=size, label="F")
            self.assert_classes_present(html, {"fab", expected_class})

    def test_fab_flower_mode(self):
        """Test FAB flower mode (quarter circle arrangement)"""
        html = self.render_component("fab", flower="true", slot_content="F")

        # Should have fab-flower class
        self.assert_classes_present(html, {"fab", "fab-flower"})

    def test_fab_with_icon(self):
        """Test FAB with icon"""
        html = self.render_component("fab", icon="rmx.add")

        # Should have icon component or SVG content
        assert 'is="lbi"' in html or "<svg" in html
        assert 'n="rmx.add"' in html or "<svg" in html

    def test_fab_with_filled_icon(self):
        """Test FAB with filled icon"""
        html = self.render_component("fab", icon="rmx.add", iconFill="true")

        # Should have icon with fill attribute
        assert 'is="lbi"' in html or "<svg" in html
        assert 'n="rmx.add"' in html or "<svg" in html

    def test_fab_with_icon_class(self):
        """Test FAB with icon class"""
        html = self.render_component("fab", icon="rmx.add", iconClass="text-red-500")

        # Should have icon with class attribute
        assert 'is="lbi"' in html or "<svg" in html
        assert 'n="rmx.add"' in html or "<svg" in html

    def test_fab_combined_features(self):
        """Test FAB with multiple features combined"""
        html = self.render_component(
            "fab",
            variant="primary",
            size="lg",
            flower="true",
            icon="rmx.add",
            iconClass="text-white",
            class_="custom-fab",
        )

        # Should have all expected classes
        self.assert_classes_present(
            html, {"fab", "fab-flower", "btn-primary", "btn-lg", "custom-fab"}
        )

        # Should have all expected elements
        assert 'tabindex="0"' in html
        assert 'role="button"' in html
        assert 'is="lbi"' in html or "<svg" in html

    def test_fab_accessibility(self):
        """Test FAB accessibility features"""
        html = self.render_component("fab", label="F")

        # Should have proper accessibility attributes
        assert 'tabindex="0"' in html
        assert 'role="button"' in html

    def test_fab_slot_content(self):
        """Test FAB with slot content (actions)"""
        html = self.render_component(
            "fab", slot_content="<button>Custom Action</button>"
        )

        # Should render slot content (actions)
        assert "Custom Action" in html
        # Should not have icon component
        assert 'is="lbi"' not in html

    def test_fab_actions_slot(self):
        """Test FAB with actions slot (main slot)"""
        actions_html = '<button class="btn btn-circle">A</button><button class="btn btn-circle">B</button>'
        html = self.render_component("fab", slot_content=actions_html)

        # Should render actions
        assert "A" in html
        assert "B" in html
        assert "btn-circle" in html

    def test_fab_custom_class(self):
        """Test FAB with custom class"""
        html = self.render_component("fab", class_="my-custom-fab", label="F")

        # Should have custom class
        self.assert_classes_present(html, {"fab", "my-custom-fab"})

    def test_fab_flower_with_actions(self):
        """Test FAB flower mode with action buttons"""
        actions_html = '<button class="btn btn-circle">A</button><button class="btn btn-circle">B</button>'
        html = self.render_component("fab", flower="true", slot_content=actions_html)

        # Should have flower class and actions
        self.assert_classes_present(html, {"fab", "fab-flower"})
        assert "A" in html
        assert "B" in html

    def test_fab_with_icon_and_slot(self):
        """Test FAB with both icon and slot content"""
        html = self.render_component(
            "fab", icon="rmx.add", slot_content="<button>A</button>"
        )

        # Should have icon
        assert 'is="lbi"' in html or "<svg" in html
        # Should have slot content (actions) rendered
        assert "A" in html

    def test_fab_single_button_mode(self):
        """Test FAB as single button (no speed dial)"""
        html = self.render_component("fab", label="F")

        # Should only have main button with label
        assert "F" in html
        assert 'tabindex="0"' in html
        assert 'role="button"' in html

    def test_fab_close_with_slot(self):
        """Test FAB close button with custom slot content"""
        html = self.render_component("fab.close", slot_content="×")

        # Should have close button with custom content
        assert "fab-close" in html
        assert "×" in html
        assert "btn-circle" in html

    def test_fab_close_without_slot(self):
        """Test FAB close button without slot content (default)"""
        html = self.render_component("fab.close")

        # Should have close button with default content
        assert "fab-close" in html
        assert "✕" in html
        assert "btn-circle" in html

    def test_fab_main_action_with_slot(self):
        """Test FAB main action with custom slot content"""
        html = self.render_component("fab.main-action", slot_content="M")

        # Should have main action button with custom content
        assert "fab-main-action" in html
        assert "M" in html
        assert "btn-circle" in html

    def test_fab_main_action_without_slot(self):
        """Test FAB main action without slot content"""
        html = self.render_component("fab.main-action")

        # Should have main action button (empty slot)
        assert "fab-main-action" in html
        assert "btn-circle" in html

    def test_fab_custom_button(self):
        """Test FAB with custom button (no icon or label variable)"""
        html = self.render_component("fab", slot_content="<button>Custom</button>")

        # Should render custom button content in main slot (actions)
        assert "Custom" in html
        # Should not have the default button wrapper since no icon or label variable
        assert 'tabindex="0"' not in html
        assert 'role="button"' not in html
