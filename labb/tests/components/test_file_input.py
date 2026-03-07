from labb.tests.components.test_base import ComponentTestBase


class TestFileInput(ComponentTestBase):
    """Test file-input component"""

    def test_basic_file_input(self):
        """Test basic file input rendering"""
        html = self.render_component("file-input")
        assert "file-input" in html
        assert 'type="file"' in html

    def test_file_input_variants(self):
        """Test file input color variants"""
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
            html = self.render_component("file-input", variant=variant)
            assert f"file-input-{variant}" in html

    def test_file_input_sizes(self):
        """Test file input size variants"""
        sizes = ["xs", "sm", "md", "lg", "xl"]
        for size in sizes:
            html = self.render_component("file-input", size=size)
            assert f"file-input-{size}" in html

    def test_file_input_default_size(self):
        """Test that default size is md"""
        html = self.render_component("file-input")
        assert "file-input-md" in html

    def test_file_input_ghost(self):
        """Test ghost style variant"""
        html = self.render_component("file-input", ghost="true")
        assert "file-input-ghost" in html

    def test_file_input_no_ghost_by_default(self):
        """Test ghost is not applied by default"""
        html = self.render_component("file-input")
        assert "file-input-ghost" not in html

    def test_file_input_combination(self):
        """Test file input with variant, size, and custom class"""
        html = self.render_component(
            "file-input",
            variant="primary",
            size="lg",
            **{"class": "w-full"},
        )
        assert "file-input-primary" in html
        assert "file-input-lg" in html
        assert "w-full" in html

    def test_file_input_custom_class(self):
        """Test file input with custom CSS class"""
        html = self.render_component("file-input", **{"class": "w-full max-w-xs"})
        assert "w-full" in html
