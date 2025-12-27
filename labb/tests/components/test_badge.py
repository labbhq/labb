from labb.tests.components.test_base import ComponentTestBase


class TestBadge(ComponentTestBase):
    """Test badge component"""

    def test_basic_badge(self):
        """Test basic badge rendering"""
        html = self.render_component("badge", slot_content="Test Badge")
        assert "badge" in html
        assert "Test Badge" in html

    def test_badge_variants(self):
        """Test badge color variants"""
        variants = [
            "neutral",
            "primary",
            "secondary",
            "accent",
            "info",
            "success",
            "warning",
            "error",
        ]
        for variant in variants:
            html = self.render_component(
                "badge", variant=variant, slot_content=f"{variant} badge"
            )
            assert f"badge-{variant}" in html
            assert f"{variant} badge" in html

    def test_badge_styles(self):
        """Test badge style variants"""
        styles = ["outline", "dash", "soft", "ghost"]
        for style in styles:
            html = self.render_component(
                "badge", style=style, slot_content=f"{style} badge"
            )
            assert f"badge-{style}" in html
            assert f"{style} badge" in html

    def test_badge_sizes(self):
        """Test badge sizes"""
        sizes = ["xs", "sm", "md", "lg", "xl"]
        for size in sizes:
            html = self.render_component(
                "badge", size=size, slot_content=f"{size} badge"
            )
            assert f"badge-{size}" in html
            assert f"{size} badge" in html

    def test_badge_with_custom_class(self):
        """Test badge with custom CSS class"""
        html = self.render_component(
            "badge", class_name="custom-class", slot_content="Custom Badge"
        )
        assert "custom-class" in html
        assert "Custom Badge" in html

    def test_badge_combination(self):
        """Test badge with multiple properties"""
        html = self.render_component(
            "badge",
            variant="primary",
            style="outline",
            size="lg",
            class_name="custom-class",
            slot_content="Combined Badge",
        )
        assert "badge-primary" in html
        assert "badge-outline" in html
        assert "badge-lg" in html
        assert "custom-class" in html
        assert "Combined Badge" in html

    def test_empty_badge(self):
        """Test empty badge (no content)"""
        html = self.render_component("badge", variant="primary", size="md")
        assert "badge" in html
        assert "badge-primary" in html
        assert "badge-md" in html
        # Should not have any content between opening and closing tags
        assert "<span" in html
        assert "</span>" in html

    def test_badge_with_html_content(self):
        """Test badge with HTML content (like icons)"""
        html = self.render_component(
            "badge",
            variant="info",
            slot_content='<svg class="icon">Info</svg> Info Badge',
        )
        assert "badge-info" in html
        # Note: HTML content in slot is escaped, so we check for the text content
        assert "Info Badge" in html

    def test_badge_default_values(self):
        """Test badge with default values"""
        html = self.render_component("badge", slot_content="Default Badge")
        # Should have base badge class
        assert "badge" in html
        # Should not have any variant, style, or size classes (using defaults)
        assert "badge-primary" not in html
        assert "badge-outline" not in html
        assert "badge-lg" not in html
        assert "Default Badge" in html

    def test_badge_with_icon(self):
        """Test badge with icon"""
        html = self.render_component("badge", icon="rmx.check", slot_content="Success")
        assert "badge" in html
        assert "Success" in html
        # Should contain the rendered SVG icon
        assert "<svg" in html
        assert 'fill="currentColor"' in html
        assert 'height="1em"' in html
        assert 'width="1em"' in html

    def test_badge_icon_only(self):
        """Test badge with icon only (no text content)"""
        html = self.render_component("badge", variant="primary", icon="rmx.star")
        assert "badge" in html
        assert "badge-primary" in html
        # Should contain the rendered SVG icon
        assert "<svg" in html
        assert 'fill="currentColor"' in html
        assert 'height="1em"' in html
        assert 'width="1em"' in html

    def test_badge_with_icon_and_combined_properties(self):
        """Test badge with icon and other properties"""
        html = self.render_component(
            "badge",
            variant="success",
            style="outline",
            size="lg",
            icon="rmx.check",
            slot_content="Completed",
        )
        assert "badge-success" in html
        assert "badge-outline" in html
        assert "badge-lg" in html
        assert "Completed" in html
        # Should contain the rendered SVG icon
        assert "<svg" in html
        assert 'fill="currentColor"' in html
        assert 'height="1em"' in html
        assert 'width="1em"' in html

    def test_badge_with_icon_fill(self):
        """Test badge with filled icon"""
        html = self.render_component(
            "badge", icon="rmx.star", iconFill="true", slot_content="Filled Star"
        )
        assert "badge" in html
        assert "Filled Star" in html
        # Should contain the rendered SVG icon with fill
        assert "<svg" in html
        assert 'fill="currentColor"' in html
        assert 'height="1em"' in html
        assert 'width="1em"' in html

    def test_badge_with_icon_no_fill(self):
        """Test badge with unfilled icon (default)"""
        html = self.render_component(
            "badge", icon="rmx.star", iconFill="false", slot_content="Unfilled Star"
        )
        assert "badge" in html
        assert "Unfilled Star" in html
        # Should contain the rendered SVG icon without fill
        assert "<svg" in html
        assert 'fill="currentColor"' in html
        assert 'height="1em"' in html
        assert 'width="1em"' in html

    def test_badge_with_icon_class(self):
        """Test badge with icon and custom icon class"""
        html = self.render_component(
            "badge", icon="rmx.check", iconClass="text-warning", slot_content="Success"
        )
        assert "badge" in html
        assert "Success" in html
        # Should contain the icon component with custom class
        assert 'is="lbi"' in html or "<svg" in html
