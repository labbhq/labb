from labb.tests.components.test_base import ComponentTestBase


class TestRating(ComponentTestBase):
    """Test rating component"""

    def test_basic_rating(self):
        """Test basic rating generates 5 inputs by default"""
        html = self.render_component("rating")
        assert "rating" in html
        assert html.count('type="radio"') == 5
        assert "mask-star-2" in html

    def test_rating_max(self):
        """Test rating with custom max"""
        html = self.render_component("rating", max="3")
        assert html.count('type="radio"') == 3

    def test_rating_name(self):
        """Test rating with custom name"""
        html = self.render_component("rating", name="my-rating")
        assert 'name="my-rating"' in html

    def test_rating_shape(self):
        """Test rating with custom shape"""
        html = self.render_component("rating", shape="heart")
        assert "mask-heart" in html

    def test_rating_variant(self):
        """Test rating color variants"""
        html = self.render_component("rating", variant="warning")
        assert "bg-warning" in html

    def test_rating_variants(self):
        """Test rating standard color variants"""
        variants = [
            "primary",
            "secondary",
            "accent",
            "info",
            "success",
            "warning",
            "error",
        ]
        for variant in variants:
            html = self.render_component("rating", variant=variant)
            assert f"bg-{variant}" in html

    def test_rating_rate(self):
        """Test rating with checked item"""
        html = self.render_component("rating", rate="3")
        assert 'checked="checked"' in html

    def test_rating_sizes(self):
        """Test rating size variants"""
        sizes = ["xs", "sm", "md", "lg", "xl"]
        for size in sizes:
            html = self.render_component("rating", size=size)
            assert f"rating-{size}" in html

    def test_rating_default_size(self):
        """Test that default size is md"""
        html = self.render_component("rating")
        assert "rating-md" in html

    def test_rating_half(self):
        """Test half-star ratings"""
        html = self.render_component("rating", half="true", max="3")
        assert "rating-half" in html
        assert "rating-hidden" in html
        assert "mask-half-1" in html
        assert "mask-half-2" in html
        # half mode: 1 hidden + 3*2 half inputs = 7
        assert html.count('type="radio"') == 7

    def test_rating_no_half_by_default(self):
        """Test half not applied by default"""
        html = self.render_component("rating")
        assert "rating-half" not in html
        assert "mask-half-1" not in html

    def test_rating_custom_class(self):
        """Test rating with custom CSS class"""
        html = self.render_component(
            "rating",
            **{"class": "my-rating"},
        )
        assert "my-rating" in html

    def test_rating_half_rate_decimal(self):
        """Test half-star rating with .5 rate value"""
        html = self.render_component("rating", half="true", rate="3.5", max="5")
        assert 'checked="checked"' in html
        # half-1 of star 4 (i=4, 4-0.5=3.5) should be checked
        assert 'aria-label="3.5 star" checked="checked"' in html

    def test_rating_half_rate_whole(self):
        """Test half-star rating with whole rate value"""
        html = self.render_component("rating", half="true", rate="3", max="5")
        assert 'checked="checked"' in html
        # half-2 of star 3 should be checked
        assert 'aria-label="3 star" checked="checked"' in html

    def test_rating_heart_with_variant(self):
        """Test rating with heart shape and error variant"""
        html = self.render_component("rating", shape="heart", variant="error")
        assert "mask-heart" in html
        assert "bg-error" in html
