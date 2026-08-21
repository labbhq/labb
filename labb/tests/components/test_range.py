from labb.tests.components.test_base import ComponentTestBase


class TestRange(ComponentTestBase):
    """Test range component"""

    def test_basic_range(self):
        """Test basic range rendering"""
        html = self.render_component("range")
        assert "range" in html
        assert 'type="range"' in html

    def test_range_variants(self):
        """Test range color variants"""
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
            html = self.render_component("range", variant=variant)
            assert f"range-{variant}" in html

    def test_range_vertical(self):
        """Test vertical orientation applies range-vertical"""
        html = self.render_component("range", orientation="vertical")
        assert "range-vertical" in html

    def test_range_horizontal_default(self):
        """Test horizontal orientation has no range-vertical class"""
        html = self.render_component("range")
        assert "range-vertical" not in html

    def test_range_sizes(self):
        """Test range size variants"""
        sizes = ["xs", "sm", "md", "lg", "xl"]
        for size in sizes:
            html = self.render_component("range", size=size)
            assert f"range-{size}" in html

    def test_range_default_size(self):
        """Test that default size is md"""
        html = self.render_component("range")
        assert "range-md" in html

    def test_range_with_attributes(self):
        """Test range with min/max/value"""
        html = self.render_component("range", min="0", max="100", value="40")
        assert 'min="0"' in html
        assert 'max="100"' in html
        assert 'value="40"' in html

    def test_range_combination(self):
        """Test range with variant, size, and custom class"""
        html = self.render_component(
            "range",
            variant="primary",
            size="lg",
            **{"class": "w-full"},
        )
        assert "range-primary" in html
        assert "range-lg" in html
        assert "w-full" in html

    def test_range_custom_class(self):
        """Test range with custom CSS class"""
        html = self.render_component("range", **{"class": "w-full"})
        assert "w-full" in html
