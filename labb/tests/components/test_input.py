from labb.tests.components.test_base import ComponentTestBase


class TestInput(ComponentTestBase):
    """Test input component"""

    def test_basic_input(self):
        """Test basic input rendering"""
        html = self.render_component("input")
        assert "input" in html
        assert "<input" in html

    def test_input_variants(self):
        """Test input color variants"""
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
            html = self.render_component("input", variant=variant)
            assert f"input-{variant}" in html

    def test_input_sizes(self):
        """Test input size variants"""
        sizes = ["xs", "sm", "md", "lg", "xl"]
        for size in sizes:
            html = self.render_component("input", size=size)
            assert f"input-{size}" in html

    def test_input_default_size(self):
        """Test that default size is md"""
        html = self.render_component("input")
        assert "input-md" in html

    def test_input_ghost(self):
        """Test ghost style variant"""
        html = self.render_component("input", ghost="true")
        assert "input-ghost" in html

    def test_input_no_ghost_by_default(self):
        """Test ghost not applied by default"""
        html = self.render_component("input")
        assert "input-ghost" not in html

    def test_input_with_type(self):
        """Test input with type attribute"""
        html = self.render_component("input", type="email")
        assert 'type="email"' in html

    def test_input_with_placeholder(self):
        """Test input with placeholder"""
        html = self.render_component("input", placeholder="Type here")
        assert 'placeholder="Type here"' in html

    def test_input_combination(self):
        """Test input with variant, size, and custom class"""
        html = self.render_component(
            "input",
            variant="primary",
            size="lg",
            **{"class": "w-full"},
        )
        assert "input-primary" in html
        assert "input-lg" in html
        assert "w-full" in html

    def test_input_custom_class(self):
        """Test input with custom CSS class"""
        html = self.render_component("input", **{"class": "w-full max-w-xs"})
        assert "w-full" in html
