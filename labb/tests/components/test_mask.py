from labb.tests.components.test_base import ComponentTestBase


class TestMask(ComponentTestBase):
    """Test mask component"""

    def test_basic_mask(self):
        """Test basic mask rendering with default shape"""
        html = self.render_component("mask", src="test.jpg")
        assert "mask" in html
        assert "mask-squircle" in html
        assert "<img" in html

    def test_mask_shapes(self):
        """Test all mask shapes"""
        shapes = [
            "squircle",
            "heart",
            "hexagon",
            "hexagon-2",
            "decagon",
            "pentagon",
            "diamond",
            "square",
            "circle",
            "star",
            "star-2",
            "triangle",
            "triangle-2",
            "triangle-3",
            "triangle-4",
        ]
        for shape in shapes:
            html = self.render_component("mask", shape=shape, src="test.jpg")
            assert f"mask-{shape}" in html

    def test_mask_half(self):
        """Test mask half variants"""
        for half in ["1", "2"]:
            html = self.render_component("mask", half=half, src="test.jpg")
            assert f"mask-half-{half}" in html

    def test_mask_no_half_by_default(self):
        """Test that no half class is added by default"""
        html = self.render_component("mask", src="test.jpg")
        assert "mask-half-1" not in html
        assert "mask-half-2" not in html

    def test_mask_custom_class(self):
        """Test mask with custom CSS class"""
        html = self.render_component("mask", src="test.jpg", **{"class": "w-20"})
        assert "w-20" in html

    def test_mask_combination(self):
        """Test mask with shape and half combined"""
        html = self.render_component("mask", shape="star", half="1", src="test.jpg")
        assert "mask-star" in html
        assert "mask-half-1" in html
