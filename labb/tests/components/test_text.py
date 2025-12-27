from labb.tests.components.test_base import ComponentTestBase


class TestText(ComponentTestBase):
    """Test text component"""

    def test_basic_text(self):
        """Test basic text rendering"""
        html = self.render_component("text", slot_content="Test Text")
        assert "<span" in html
        assert "Test Text" in html

    def test_text_variants(self):
        """Test text color variants"""
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
                "text", variant=variant, slot_content=f"{variant} text"
            )
            assert f"text-{variant}" in html
            assert f"{variant} text" in html

    def test_text_sizes(self):
        """Test text sizes"""
        sizes = ["xs", "sm", "md", "lg", "xl", "2xl", "3xl", "4xl"]
        size_classes = {
            "xs": "text-xs",
            "sm": "text-sm",
            "md": "text-base",
            "lg": "text-lg",
            "xl": "text-xl",
            "2xl": "text-2xl",
            "3xl": "text-3xl",
            "4xl": "text-4xl",
        }
        for size in sizes:
            html = self.render_component("text", size=size, slot_content=f"{size} text")
            assert size_classes[size] in html
            assert f"{size} text" in html

    def test_text_underline(self):
        """Test text underline"""
        html = self.render_component(
            "text", underline=True, slot_content="Underlined text"
        )
        assert "underline" in html
        assert "Underlined text" in html

    def test_text_no_underline(self):
        """Test text without underline (default)"""
        html = self.render_component("text", slot_content="Normal text")
        assert "underline" not in html
        assert "Normal text" in html

    def test_text_with_custom_class(self):
        """Test text with custom CSS class"""
        html = self.render_component(
            "text", class_="custom-class", slot_content="Custom Text"
        )
        assert "custom-class" in html
        assert "Custom Text" in html

    def test_text_elements(self):
        """Test text with different HTML elements"""
        elements = ["span", "p", "div", "h1", "h2", "h3", "h4", "h5", "h6"]
        for element in elements:
            html = self.render_component(
                "text", **{"as": element}, slot_content=f"{element} text"
            )
            assert f"<{element}" in html
            assert f"{element} text" in html

    def test_text_with_icon(self):
        """Test text with icon"""
        html = self.render_component("text", icon="rmx.check", slot_content="Success")
        assert "Success" in html
        # Should contain the rendered SVG icon
        assert "<svg" in html
        assert 'height="1em"' in html
        assert 'width="1em"' in html

    def test_text_icon_at_start(self):
        """Test text with icon at start (default)"""
        html = self.render_component(
            "text", icon="rmx.information", iconEnd=False, slot_content="Info text"
        )
        assert "Info text" in html
        assert "<svg" in html
        # Icon should appear before text content
        # We can't easily test order, but we can verify both are present
        assert 'height="1em"' in html

    def test_text_icon_at_end(self):
        """Test text with icon at end"""
        html = self.render_component(
            "text", icon="rmx.arrow-right", iconEnd=True, slot_content="Next"
        )
        assert "Next" in html
        assert "<svg" in html
        assert 'height="1em"' in html
        assert 'width="1em"' in html

    def test_text_with_icon_fill(self):
        """Test text with filled icon"""
        html = self.render_component(
            "text", icon="rmx.star", iconFill=True, slot_content="Filled Star"
        )
        assert "Filled Star" in html
        # Should contain the rendered SVG icon
        assert "<svg" in html
        assert 'height="1em"' in html
        assert 'width="1em"' in html

    def test_text_with_icon_no_fill(self):
        """Test text with unfilled icon (default)"""
        html = self.render_component(
            "text", icon="rmx.star", iconFill=False, slot_content="Unfilled Star"
        )
        assert "Unfilled Star" in html
        # Should contain the rendered SVG icon
        assert "<svg" in html
        assert 'height="1em"' in html
        assert 'width="1em"' in html

    def test_text_with_icon_class(self):
        """Test text with icon and custom icon class"""
        html = self.render_component(
            "text", icon="rmx.check", iconClass="text-warning", slot_content="Success"
        )
        assert "Success" in html
        # Should contain the icon component
        assert 'is="lbi"' in html or "<svg" in html

    def test_text_combination(self):
        """Test text with multiple properties"""
        html = self.render_component(
            "text",
            variant="primary",
            size="lg",
            underline=True,
            icon="rmx.check",
            slot_content="Combined Text",
        )
        assert "text-primary" in html
        assert "text-lg" in html
        assert "underline" in html
        assert "Combined Text" in html
        assert "<svg" in html

    def test_text_combination_with_icon_end(self):
        """Test text with icon at end and other properties"""
        html = self.render_component(
            "text",
            variant="success",
            size="xl",
            underline=True,
            icon="rmx.arrow-right",
            iconEnd=True,
            iconFill=True,
            slot_content="Complete",
        )
        assert "text-success" in html
        assert "text-xl" in html
        assert "underline" in html
        assert "Complete" in html
        assert "<svg" in html

    def test_text_default_values(self):
        """Test text with default values"""
        html = self.render_component("text", slot_content="Default Text")
        # Should render as span (default)
        assert "<span" in html
        # Should have default size (text-base)
        assert "text-base" in html
        # Should not have variant, underline, or icon
        assert "text-primary" not in html
        assert "underline" not in html
        assert "<svg" not in html
        assert "Default Text" in html

    def test_text_empty_content(self):
        """Test text with no content (icon only)"""
        html = self.render_component("text", icon="rmx.star", variant="primary")
        assert "<span" in html
        assert "text-primary" in html
        assert "<svg" in html

    def test_text_as_heading_with_variant(self):
        """Test text as heading with variant"""
        html = self.render_component(
            "text",
            **{"as": "h1"},
            size="3xl",
            variant="primary",
            slot_content="Heading",
        )
        assert "<h1" in html
        assert "text-3xl" in html
        assert "text-primary" in html
        assert "Heading" in html
