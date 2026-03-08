from labb.tests.components.test_base import ComponentTestTemplate


class TestStatus(ComponentTestTemplate):
    """Test suite for the status component"""

    component_name = "status"

    def test_status_renders_with_base_class(self):
        """Test that status renders with the status base class"""
        html = self.render_component("status")
        self.assert_classes_present(html, {"status"})

    def test_status_variants(self):
        """Test status color variants"""
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
            html = self.render_component("status", variant=variant)
            assert f"status-{variant}" in html

    def test_status_sizes(self):
        """Test status size variants"""
        sizes = ["xs", "sm", "md", "lg", "xl"]
        for size in sizes:
            html = self.render_component("status", size=size)
            assert f"status-{size}" in html

    def test_status_default_size(self):
        """Test that default size is md"""
        html = self.render_component("status")
        assert "status-md" in html

    def test_status_animate_ping(self):
        """Test status with ping animation"""
        html = self.render_component("status", variant="error", animate="ping")
        assert "animate-ping" in html
        assert "status-error" in html
        # Ping uses inline-grid wrapper with two elements
        assert "inline-grid" in html

    def test_status_animate_bounce(self):
        """Test status with bounce animation"""
        html = self.render_component("status", variant="info", animate="bounce")
        assert "animate-bounce" in html
        assert "status-info" in html

    def test_status_no_animation_by_default(self):
        """Test that no animation is applied by default"""
        html = self.render_component("status")
        assert "animate-ping" not in html
        assert "animate-bounce" not in html
        assert "inline-grid" not in html

    def test_status_custom_class(self):
        """Test status with custom CSS class"""
        html = self.render_component("status", **{"class": "my-custom"})
        assert "my-custom" in html

    def test_status_combination(self):
        """Test status with variant, size, and custom class"""
        html = self.render_component(
            "status",
            variant="success",
            size="lg",
            **{"class": "ml-2"},
        )
        assert "status-success" in html
        assert "status-lg" in html
        assert "ml-2" in html
