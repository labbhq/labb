from labb.tests.components.test_base import ComponentTestBase


class TestTextarea(ComponentTestBase):
    """Test textarea component"""

    def test_basic_textarea(self):
        """Test basic textarea rendering"""
        html = self.render_component("textarea")
        assert "textarea" in html
        assert "<textarea" in html

    def test_textarea_variants(self):
        """Test textarea color variants"""
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
            html = self.render_component("textarea", variant=variant)
            assert f"textarea-{variant}" in html

    def test_textarea_sizes(self):
        """Test textarea size variants"""
        sizes = ["xs", "sm", "md", "lg", "xl"]
        for size in sizes:
            html = self.render_component("textarea", size=size)
            assert f"textarea-{size}" in html

    def test_textarea_default_size(self):
        """Test that default size is md"""
        html = self.render_component("textarea")
        assert "textarea-md" in html

    def test_textarea_ghost(self):
        """Test ghost style variant"""
        html = self.render_component("textarea", ghost="true")
        assert "textarea-ghost" in html

    def test_textarea_no_ghost_by_default(self):
        """Test ghost not applied by default"""
        html = self.render_component("textarea")
        assert "textarea-ghost" not in html

    def test_textarea_with_placeholder(self):
        """Test textarea with placeholder"""
        html = self.render_component("textarea", placeholder="Your bio")
        assert 'placeholder="Your bio"' in html

    def test_textarea_combination(self):
        """Test textarea with variant, size, and custom class"""
        html = self.render_component(
            "textarea",
            variant="primary",
            size="lg",
            **{"class": "h-24"},
        )
        assert "textarea-primary" in html
        assert "textarea-lg" in html
        assert "h-24" in html

    def test_textarea_custom_class(self):
        """Test textarea with custom CSS class"""
        html = self.render_component("textarea", **{"class": "h-24 w-full"})
        assert "h-24" in html
