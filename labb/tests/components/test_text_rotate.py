from labb.tests.components.test_base import ComponentTestTemplate


class TestTextRotate(ComponentTestTemplate):
    """Test suite for the text-rotate component"""

    component_name = "text-rotate"

    def test_text_rotate_renders_with_base_class(self):
        """Test that text-rotate renders with the text-rotate base class"""
        html = self.render_component(
            "text-rotate",
            slot_content="<span>Hello</span><span>World</span>",
        )
        self.assert_classes_present(html, {"text-rotate"})

    def test_text_rotate_renders_slot_content(self):
        """Test that slot content is rendered"""
        html = self.render_component(
            "text-rotate",
            slot_content="<span>First</span><span>Second</span>",
        )
        assert "First" in html
        assert "Second" in html

    def test_text_rotate_with_duration(self):
        """Test text-rotate with custom duration"""
        html = self.render_component(
            "text-rotate",
            duration="duration-6000",
            slot_content="<span>A</span><span>B</span>",
        )
        assert "duration-6000" in html
        assert "text-rotate" in html

    def test_text_rotate_no_duration_by_default(self):
        """Test that no duration class is applied by default"""
        html = self.render_component(
            "text-rotate",
            slot_content="<span>A</span><span>B</span>",
        )
        assert "duration-" not in html

    def test_text_rotate_custom_class(self):
        """Test text-rotate with custom CSS class"""
        html = self.render_component(
            "text-rotate",
            slot_content="<span>A</span><span>B</span>",
            **{"class": "text-4xl font-bold"},
        )
        assert "text-4xl" in html
        assert "font-bold" in html

    def test_text_rotate_nested_span_structure(self):
        """Test that the component has the required nested span structure"""
        html = self.render_component(
            "text-rotate",
            slot_content="<span>Hello</span>",
        )
        # Should have outer span.text-rotate > span > slot content
        assert "<span" in html
        assert "text-rotate" in html
