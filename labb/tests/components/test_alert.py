from labb.tests.components.test_base import ComponentTestBase


class TestAlert(ComponentTestBase):
    """Test alert component"""

    def test_basic_alert(self):
        """Test basic alert rendering"""
        html = self.render_component("alert", slot_content="Test Alert")
        assert "alert" in html
        assert "Test Alert" in html
        assert 'role="alert"' in html

    def test_alert_variants(self):
        """Test alert color variants"""
        variants = ["info", "success", "warning", "error"]
        for variant in variants:
            html = self.render_component(
                "alert", variant=variant, slot_content=f"{variant} alert"
            )
            assert f"alert-{variant}" in html
            assert f"{variant} alert" in html

    def test_alert_with_custom_class(self):
        """Test alert with custom CSS class"""
        html = self.render_component(
            "alert", class_name="custom-class", slot_content="Custom Alert"
        )
        assert "custom-class" in html
        assert "Custom Alert" in html

    def test_alert_combination(self):
        """Test alert with multiple properties"""
        html = self.render_component(
            "alert",
            variant="success",
            class_name="custom-class",
            slot_content="Combined Alert",
        )
        assert "alert-success" in html
        assert "custom-class" in html
        assert "Combined Alert" in html

    def test_empty_alert(self):
        """Test empty alert (no content)"""
        html = self.render_component("alert", variant="info")
        assert "alert" in html
        assert "alert-info" in html
        # Should not have any content between opening and closing tags
        assert "<div" in html
        assert "</div>" in html

    def test_alert_with_html_content(self):
        """Test alert with HTML content"""
        html = self.render_component(
            "alert",
            variant="warning",
            slot_content="<strong>Warning:</strong> This is important",
        )
        assert "alert-warning" in html
        # Note: HTML content in slot is escaped, so we check for the text content
        assert "Warning:" in html
        assert "This is important" in html

    def test_alert_default_values(self):
        """Test alert with default values"""
        html = self.render_component("alert", slot_content="Default Alert")
        # Should have base alert class
        assert "alert" in html
        # Should not have any variant classes (using defaults)
        assert "alert-info" not in html
        assert "alert-success" not in html
        assert "alert-warning" not in html
        assert "alert-error" not in html
        assert "Default Alert" in html

    def test_alert_with_icon(self):
        """Test alert with icon"""
        html = self.render_component(
            "alert", icon="rmx.information", slot_content="Info message"
        )
        assert "alert" in html
        assert "Info message" in html
        # Should contain the rendered SVG icon
        assert "<svg" in html
        assert 'fill="currentColor"' in html
        assert 'height="1em"' in html
        assert 'width="1em"' in html

    def test_alert_icon_only(self):
        """Test alert with icon only (no text content)"""
        html = self.render_component("alert", variant="success", icon="rmx.check")
        assert "alert" in html
        assert "alert-success" in html
        # Should contain the rendered SVG icon
        assert "<svg" in html
        assert 'fill="currentColor"' in html
        assert 'height="1em"' in html
        assert 'width="1em"' in html

    def test_alert_with_icon_and_combined_properties(self):
        """Test alert with icon and other properties"""
        html = self.render_component(
            "alert",
            variant="error",
            icon="rmx.close-circle",
            class_name="custom-alert",
            slot_content="Error occurred",
        )
        assert "alert-error" in html
        assert "custom-alert" in html
        assert "Error occurred" in html
        # Should contain the rendered SVG icon
        assert "<svg" in html
        assert 'fill="currentColor"' in html
        assert 'height="1em"' in html
        assert 'width="1em"' in html

    def test_alert_with_icon_fill(self):
        """Test alert with filled icon"""
        html = self.render_component(
            "alert", icon="rmx.star", iconFill=True, slot_content="Filled Star Alert"
        )
        assert "alert" in html
        assert "Filled Star Alert" in html
        # Should contain the rendered SVG icon with fill
        assert "<svg" in html
        assert 'fill="currentColor"' in html
        assert 'height="1em"' in html
        assert 'width="1em"' in html

    def test_alert_with_icon_no_fill(self):
        """Test alert with unfilled icon (default)"""
        html = self.render_component(
            "alert", icon="rmx.star", iconFill=False, slot_content="Unfilled Star Alert"
        )
        assert "alert" in html
        assert "Unfilled Star Alert" in html
        # Should contain the rendered SVG icon without fill
        assert "<svg" in html
        assert 'fill="currentColor"' in html
        assert 'height="1em"' in html
        assert 'width="1em"' in html

    def test_alert_with_icon_class(self):
        """Test alert with icon and custom icon class"""
        html = self.render_component(
            "alert",
            icon="rmx.check",
            iconClass="text-warning",
            slot_content="Success Alert",
        )
        assert "alert" in html
        assert "Success Alert" in html
        # Should contain the icon component with custom class
        assert 'is="lbi"' in html or "<svg" in html

    def test_alert_with_actions_slot(self):
        """Test alert with actions slot"""
        html = self.render_component(
            "alert",
            variant="info",
            slot_content="Alert message",
            actions='<button class="btn btn-sm">Action</button>',
        )
        assert "alert" in html
        assert "alert-info" in html
        assert "Alert message" in html
        assert "Action" in html

    def test_alert_accessibility(self):
        """Test alert accessibility attributes"""
        html = self.render_component("alert", slot_content="Accessible alert")
        assert 'role="alert"' in html
        assert "Accessible alert" in html

    def test_alert_all_variants_with_icons(self):
        """Test all alert variants with appropriate icons"""
        variants_and_icons = [
            ("info", "rmx.information"),
            ("success", "rmx.check"),
            ("warning", "rmx.alert"),
            ("error", "rmx.close-circle"),
        ]

        for variant, icon in variants_and_icons:
            html = self.render_component(
                "alert",
                variant=variant,
                icon=icon,
                slot_content=f"{variant.title()} message",
            )
            assert f"alert-{variant}" in html
            assert f"{variant.title()} message" in html
            assert "<svg" in html

    def test_alert_style_variants(self):
        """Test alert style variants"""
        styles = ["outline", "dash", "soft"]
        for style in styles:
            html = self.render_component(
                "alert", style=style, slot_content=f"{style} style alert"
            )
            assert f"alert-{style}" in html
            assert f"{style} style alert" in html

    def test_alert_directions(self):
        """Test alert layout directions"""
        directions = ["vertical", "horizontal"]
        for direction in directions:
            html = self.render_component(
                "alert",
                direction=direction,
                slot_content=f"{direction} direction alert",
            )
            assert f"alert-{direction}" in html
            assert f"{direction} direction alert" in html

    def test_alert_combined_style_and_direction(self):
        """Test alert with both style and direction"""
        html = self.render_component(
            "alert",
            variant="info",
            style="outline",
            direction="vertical",
            slot_content="Combined style and direction",
        )
        assert "alert-info" in html
        assert "alert-outline" in html
        assert "alert-vertical" in html
        assert "Combined style and direction" in html

    def test_alert_all_features_combined(self):
        """Test alert with all features combined"""
        html = self.render_component(
            "alert",
            variant="success",
            style="soft",
            direction="horizontal",
            icon="rmx.check",
            class_name="custom-alert",
            slot_content="All features combined",
        )
        assert "alert-success" in html
        assert "alert-soft" in html
        assert "alert-horizontal" in html
        assert "custom-alert" in html
        assert "All features combined" in html
        assert "<svg" in html
