from .test_base import ComponentTestBase


class TestToggle(ComponentTestBase):
    """Test the toggle component"""

    def test_basic_toggle(self):
        """Test basic toggle rendering"""
        html = self.render_component("toggle")
        assert "toggle" in html
        assert 'type="checkbox"' in html

    def test_toggle_with_variants(self):
        """Test toggle with different variants"""
        variants = [
            "primary",
            "secondary",
            "accent",
            "neutral",
            "info",
            "success",
            "warning",
            "error",
        ]
        for variant in variants:
            html = self.render_component("toggle", variant=variant)
            assert f"toggle-{variant}" in html

    def test_toggle_with_sizes(self):
        """Test toggle with different sizes"""
        sizes = ["xs", "sm", "md", "lg", "xl"]
        for size in sizes:
            html = self.render_component("toggle", size=size)
            assert f"toggle-{size}" in html

    def test_toggle_checked(self):
        """Test toggle in checked state"""
        html = self.render_component("toggle", checked="true")
        assert "checked" in html

    def test_toggle_disabled(self):
        """Test toggle in disabled state"""
        html = self.render_component("toggle", disabled="true")
        assert "disabled" in html

    def test_toggle_checked_and_disabled(self):
        """Test toggle in both checked and disabled states"""
        html = self.render_component("toggle", checked="true", disabled="true")
        assert "checked" in html
        assert "disabled" in html

    def test_toggle_with_custom_class(self):
        """Test toggle with custom CSS class"""
        html = self.render_component("toggle", **{"class": "custom-class"})
        assert "custom-class" in html

    def test_toggle_with_all_properties(self):
        """Test toggle with all properties set"""
        html = self.render_component(
            "toggle",
            variant="primary",
            size="lg",
            checked="true",
            disabled="true",
            **{"class": "custom-class"},
        )
        assert "toggle-primary" in html
        assert "toggle-lg" in html
        assert "checked" in html
        assert "disabled" in html
        assert "custom-class" in html

    def test_toggle_base_classes(self):
        """Test that toggle has correct base classes"""
        html = self.render_component("toggle")
        self.assert_classes_present(html, {"toggle"})

    def test_toggle_variant_classes(self):
        """Test that toggle variant classes are applied correctly"""
        html = self.render_component("toggle", variant="primary")
        self.assert_classes_present(html, {"toggle", "toggle-primary"})

    def test_toggle_size_classes(self):
        """Test that toggle size classes are applied correctly"""
        html = self.render_component("toggle", size="lg")
        self.assert_classes_present(html, {"toggle", "toggle-lg"})
