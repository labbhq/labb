from .test_base import ComponentTestBase


class TestDiff(ComponentTestBase):
    """Test the diff component"""

    def test_basic_diff(self):
        """Test basic diff rendering"""
        html = self.render_component("diff")
        assert "diff" in html

    def test_diff_with_aspect_ratios(self):
        """Test diff with different aspect ratios"""
        aspect_ratios = {
            "16/9": "aspect-[16/9]",
            "4/3": "aspect-[4/3]",
            "1/1": "aspect-square",
            "3/4": "aspect-[3/4]",
            "9/16": "aspect-[9/16]",
        }
        for ratio, css_class in aspect_ratios.items():
            html = self.render_component("diff", aspectRatio=ratio)
            assert css_class in html

    def test_diff_with_custom_class(self):
        """Test diff with custom CSS class"""
        html = self.render_component("diff", **{"class": "custom-class"})
        assert "custom-class" in html

    def test_diff_item_1(self):
        """Test diff.item-1 sub-component"""
        html = self.render_component("diff.item-1", src="/path/to/image1.jpg")
        assert "diff-item-1" in html
        assert 'role="img"' in html
        assert 'src="/path/to/image1.jpg"' in html

    def test_diff_item_1_with_alt(self):
        """Test diff.item-1 with custom alt text"""
        html = self.render_component(
            "diff.item-1", src="/path/to/image1.jpg", alt="Before image"
        )
        assert 'alt="Before image"' in html

    def test_diff_item_1_with_custom_class(self):
        """Test diff.item-1 with custom CSS class"""
        html = self.render_component(
            "diff.item-1", src="/path/to/image1.jpg", **{"class": "custom-item-1"}
        )
        assert "custom-item-1" in html

    def test_diff_item_2(self):
        """Test diff.item-2 sub-component"""
        html = self.render_component("diff.item-2", src="/path/to/image2.jpg")
        assert "diff-item-2" in html
        assert 'role="img"' in html
        assert 'src="/path/to/image2.jpg"' in html

    def test_diff_item_2_with_alt(self):
        """Test diff.item-2 with custom alt text"""
        html = self.render_component(
            "diff.item-2", src="/path/to/image2.jpg", alt="After image"
        )
        assert 'alt="After image"' in html

    def test_diff_item_2_with_custom_class(self):
        """Test diff.item-2 with custom CSS class"""
        html = self.render_component(
            "diff.item-2", src="/path/to/image2.jpg", **{"class": "custom-item-2"}
        )
        assert "custom-item-2" in html

    def test_diff_resizer(self):
        """Test diff.resizer sub-component"""
        html = self.render_component("diff.resizer")
        assert "diff-resizer" in html

    def test_diff_resizer_with_custom_class(self):
        """Test diff.resizer with custom CSS class"""
        html = self.render_component("diff.resizer", **{"class": "custom-resizer"})
        assert "custom-resizer" in html

    def test_diff_base_classes(self):
        """Test that diff has correct base classes"""
        html = self.render_component("diff")
        self.assert_classes_present(html, {"diff"})

    def test_diff_item_1_base_classes(self):
        """Test that diff.item-1 has correct base classes"""
        html = self.render_component("diff.item-1", src="/path/to/image1.jpg")
        self.assert_classes_present(html, {"diff-item-1"})

    def test_diff_item_2_base_classes(self):
        """Test that diff.item-2 has correct base classes"""
        html = self.render_component("diff.item-2", src="/path/to/image2.jpg")
        self.assert_classes_present(html, {"diff-item-2"})

    def test_diff_resizer_base_classes(self):
        """Test that diff.resizer has correct base classes"""
        html = self.render_component("diff.resizer")
        self.assert_classes_present(html, {"diff-resizer"})

    def test_diff_without_aspect_ratio(self):
        """Test diff without aspect ratio (default)"""
        html = self.render_component("diff")
        # Should not have any aspect ratio classes
        assert "aspect-" not in html

    def test_diff_item_1_without_src(self):
        """Test diff.item-1 without src attribute"""
        html = self.render_component("diff.item-1")
        assert "diff-item-1" in html
        assert "<img" not in html

    def test_diff_item_2_without_src(self):
        """Test diff.item-2 without src attribute"""
        html = self.render_component("diff.item-2")
        assert "diff-item-2" in html
        assert "<img" not in html
