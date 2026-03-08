from labb.tests.components.test_base import ComponentTestTemplate


class TestKbd(ComponentTestTemplate):
    """Test suite for the kbd component"""

    component_name = "kbd"

    def test_kbd_renders_with_base_class(self):
        """Test that kbd renders with the kbd base class"""
        html = self.render_component("kbd", slot_content="K")
        self.assert_classes_present(html, {"kbd"})

    def test_kbd_renders_as_kbd_element(self):
        """Test that kbd renders as a kbd HTML element"""
        html = self.render_component("kbd", slot_content="K")
        assert "<kbd" in html
        assert "</kbd>" in html

    def test_kbd_renders_slot_content(self):
        """Test that slot content is rendered"""
        html = self.render_component("kbd", slot_content="Ctrl")
        assert "Ctrl" in html

    def test_kbd_sizes(self):
        """Test kbd size variants"""
        sizes = ["xs", "sm", "md", "lg", "xl"]
        for size in sizes:
            html = self.render_component("kbd", size=size, slot_content="A")
            assert f"kbd-{size}" in html

    def test_kbd_default_size(self):
        """Test that default size is md"""
        html = self.render_component("kbd", slot_content="A")
        assert "kbd-md" in html

    def test_kbd_custom_class(self):
        """Test kbd with custom CSS class"""
        html = self.render_component("kbd", slot_content="A", **{"class": "my-custom"})
        assert "my-custom" in html

    def test_kbd_with_unicode_content(self):
        """Test kbd with unicode arrow symbols"""
        html = self.render_component("kbd", slot_content="▲")
        assert "▲" in html

    def test_kbd_variants(self):
        """Test kbd color variants"""
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
            html = self.render_component("kbd", variant=variant, slot_content="A")
            assert f"bg-{variant}/15" in html
            assert f"text-{variant}" in html
            assert f"border-{variant}/25" in html

    def test_kbd_no_variant_by_default(self):
        """Test that no variant classes are applied by default"""
        html = self.render_component("kbd", slot_content="A")
        assert "bg-primary" not in html
        assert "text-primary" not in html

    def test_kbd_with_icon(self):
        """Test kbd with icon prop renders an SVG"""
        html = self.render_component("kbd", icon="rmx.arrow-up")
        assert "<kbd" in html
        assert "<svg" in html

    def test_kbd_icon_with_slot_content(self):
        """Test kbd with both icon and text"""
        html = self.render_component("kbd", icon="rmx.command", slot_content="K")
        assert "<svg" in html
        assert "K" in html

    def test_kbd_no_icon_by_default(self):
        """Test that no icon renders by default"""
        html = self.render_component("kbd", slot_content="A")
        assert "<svg" not in html

    def test_kbd_combination(self):
        """Test kbd with size, variant, and custom class"""
        html = self.render_component(
            "kbd",
            size="lg",
            variant="primary",
            slot_content="Enter",
            **{"class": "font-bold"},
        )
        assert "kbd-lg" in html
        assert "bg-primary/15" in html
        assert "text-primary" in html
        assert "font-bold" in html
        assert "Enter" in html
