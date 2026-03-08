from labb.tests.components.test_base import ComponentTestBase


class TestProgress(ComponentTestBase):
    """Test progress component"""

    def test_basic_progress(self):
        """Test basic progress rendering"""
        html = self.render_component("progress", value="40")
        assert "progress" in html
        assert "<progress" in html

    def test_progress_with_value(self):
        """Test progress with value attribute"""
        html = self.render_component("progress", value="70", max="100")
        assert 'value="70"' in html
        assert 'max="100"' in html

    def test_progress_indeterminate(self):
        """Test indeterminate progress (no value)"""
        html = self.render_component("progress")
        assert "progress" in html
        # Should not have a value attribute
        assert 'value="' not in html

    def test_progress_variants(self):
        """Test progress color variants"""
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
            html = self.render_component("progress", variant=variant, value="50")
            assert f"progress-{variant}" in html

    def test_progress_default_max(self):
        """Test that default max is 100"""
        html = self.render_component("progress", value="50")
        assert 'max="100"' in html

    def test_progress_custom_max(self):
        """Test progress with custom max value"""
        html = self.render_component("progress", value="5", max="10")
        assert 'max="10"' in html

    def test_progress_custom_class(self):
        """Test progress with custom CSS class"""
        html = self.render_component("progress", value="50", **{"class": "w-56"})
        assert "w-56" in html

    def test_progress_combination(self):
        """Test progress with variant, value, and custom class"""
        html = self.render_component(
            "progress",
            variant="success",
            value="80",
            **{"class": "w-full"},
        )
        assert "progress-success" in html
        assert 'value="80"' in html
        assert "w-full" in html
