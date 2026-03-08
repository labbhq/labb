from labb.tests.components.test_base import ComponentTestBase


class TestSkeleton(ComponentTestBase):
    """Test skeleton component"""

    def test_basic_skeleton(self):
        """Test basic skeleton rendering"""
        html = self.render_component("skeleton")
        assert "skeleton" in html
        assert "<div" in html

    def test_skeleton_with_custom_class(self):
        """Test skeleton with dimensions"""
        html = self.render_component("skeleton", **{"class": "h-32 w-32"})
        assert "skeleton" in html
        assert "h-32" in html
        assert "w-32" in html

    def test_skeleton_text(self):
        """Test skeleton with text animation"""
        html = self.render_component("skeleton", text="true", slot_content="Loading...")
        assert "skeleton-text" in html
        assert "Loading..." in html

    def test_skeleton_no_text_by_default(self):
        """Test that skeleton-text is not applied by default"""
        html = self.render_component("skeleton")
        assert "skeleton-text" not in html

    def test_skeleton_as_span(self):
        """Test skeleton rendered as span element"""
        html = self.render_component(
            "skeleton",
            slot_content="Loading text...",
            **{"as": "span"},
        )
        assert "<span" in html
        assert "</span>" in html

    def test_skeleton_as_div_default(self):
        """Test skeleton renders as div by default"""
        html = self.render_component("skeleton")
        assert "<div" in html

    def test_skeleton_combination(self):
        """Test skeleton with text and custom class"""
        html = self.render_component(
            "skeleton",
            text="true",
            slot_content="Thinking...",
            **{"class": "w-full"},
        )
        assert "skeleton" in html
        assert "skeleton-text" in html
        assert "w-full" in html
        assert "Thinking..." in html
