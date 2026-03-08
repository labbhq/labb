from labb.tests.components.test_base import ComponentTestBase


class TestLoading(ComponentTestBase):
    """Test loading component"""

    def test_basic_loading(self):
        """Test basic loading rendering with default spinner"""
        html = self.render_component("loading")
        assert "loading" in html
        assert "loading-spinner" in html

    def test_loading_types(self):
        """Test all loading animation types"""
        types = ["spinner", "dots", "ring", "ball", "bars", "infinity"]
        for loading_type in types:
            html = self.render_component("loading", type=loading_type)
            assert f"loading-{loading_type}" in html

    def test_loading_sizes(self):
        """Test loading size variants"""
        sizes = ["xs", "sm", "md", "lg", "xl"]
        for size in sizes:
            html = self.render_component("loading", size=size)
            assert f"loading-{size}" in html

    def test_loading_default_size(self):
        """Test that default size is md"""
        html = self.render_component("loading")
        assert "loading-md" in html

    def test_loading_variants(self):
        """Test loading color variants"""
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
            html = self.render_component("loading", variant=variant)
            assert f"text-{variant}" in html

    def test_loading_combination(self):
        """Test loading with type, size, and variant"""
        html = self.render_component(
            "loading",
            type="dots",
            size="lg",
            variant="primary",
        )
        assert "loading-dots" in html
        assert "loading-lg" in html
        assert "text-primary" in html

    def test_loading_custom_class(self):
        """Test loading with custom CSS class"""
        html = self.render_component("loading", **{"class": "my-loader"})
        assert "my-loader" in html

    def test_loading_renders_span(self):
        """Test that loading renders as a span element"""
        html = self.render_component("loading")
        assert "<span" in html
