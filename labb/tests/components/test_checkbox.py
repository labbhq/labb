from .test_base import ComponentTestBase


class TestCheckbox(ComponentTestBase):
    """Test the checkbox component"""

    def test_basic_checkbox(self):
        """Test basic checkbox rendering"""
        html = self.render_component("checkbox")
        assert "checkbox" in html
        assert 'type="checkbox"' in html

    def test_checkbox_with_variants(self):
        """Test checkbox with different variants"""
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
            html = self.render_component("checkbox", variant=variant)
            assert f"checkbox-{variant}" in html

    def test_checkbox_with_sizes(self):
        """Test checkbox with different sizes"""
        sizes = ["xs", "sm", "md", "lg", "xl"]
        for size in sizes:
            html = self.render_component("checkbox", size=size)
            assert f"checkbox-{size}" in html

    def test_checkbox_with_custom_class(self):
        """Test checkbox with custom CSS class"""
        html = self.render_component("checkbox", **{"class": "custom-class"})
        assert "custom-class" in html

    def test_checkbox_base_classes(self):
        """Test that checkbox has correct base classes"""
        html = self.render_component("checkbox")
        self.assert_classes_present(html, {"checkbox"})

    def test_checkbox_combined_states(self):
        """Test checkbox with multiple states combined"""
        html = self.render_component(
            "checkbox", variant="primary", size="lg", **{"class": "test-class"}
        )
        assert "checkbox-primary" in html
        assert "checkbox-lg" in html
        assert "test-class" in html

    def test_checkbox_accessibility(self):
        """Test checkbox accessibility features"""
        html = self.render_component("checkbox")
        assert 'type="checkbox"' in html
