from labb.tests.components.test_base import ComponentTestTemplate


class TestHoverGallery(ComponentTestTemplate):
    """Test suite for the hover-gallery component"""

    component_name = "hover-gallery"

    def test_hover_gallery_renders_with_base_class(self):
        """Test that hover-gallery renders with the hover-gallery base class"""
        html = self.render_component(
            "hover-gallery",
            slot_content='<img src="img1.jpg" /><img src="img2.jpg" />',
        )
        self.assert_classes_present(html, {"hover-gallery"})

    def test_hover_gallery_renders_as_figure_by_default(self):
        """Test that hover-gallery renders as a figure element by default"""
        html = self.render_component(
            "hover-gallery",
            slot_content='<img src="img1.jpg" />',
        )
        assert "<figure" in html
        assert "</figure>" in html

    def test_hover_gallery_renders_as_div(self):
        """Test that hover-gallery can render as a div element"""
        html = self.render_component(
            "hover-gallery",
            slot_content='<img src="img1.jpg" />',
            **{"as": "div"},
        )
        assert "<div" in html

    def test_hover_gallery_renders_slot_content(self):
        """Test that slot content (images) is rendered"""
        html = self.render_component(
            "hover-gallery",
            slot_content='<img src="img1.jpg" /><img src="img2.jpg" /><img src="img3.jpg" />',
        )
        assert 'src="img1.jpg"' in html
        assert 'src="img2.jpg"' in html
        assert 'src="img3.jpg"' in html

    def test_hover_gallery_custom_class(self):
        """Test hover-gallery with custom CSS class"""
        html = self.render_component(
            "hover-gallery",
            slot_content='<img src="img1.jpg" />',
            **{"class": "max-w-60"},
        )
        assert "max-w-60" in html

    def test_hover_gallery_combination(self):
        """Test hover-gallery with custom class and div element"""
        html = self.render_component(
            "hover-gallery",
            slot_content='<img src="img1.jpg" /><img src="img2.jpg" />',
            **{"as": "div", "class": "max-w-80 rounded-lg"},
        )
        assert "<div" in html
        assert "hover-gallery" in html
        assert "max-w-80" in html
        assert "rounded-lg" in html
