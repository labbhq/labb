from labb.tests.components.test_base import ComponentTestBase


class TestRadio(ComponentTestBase):
    """Test radio component"""

    def test_basic_radio(self):
        """Test basic radio rendering"""
        html = self.render_component("radio")
        assert "radio" in html
        assert 'type="radio"' in html

    def test_radio_variants(self):
        """Test radio color variants"""
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
            html = self.render_component("radio", variant=variant)
            assert f"radio-{variant}" in html

    def test_radio_sizes(self):
        """Test radio size variants"""
        sizes = ["xs", "sm", "md", "lg", "xl"]
        for size in sizes:
            html = self.render_component("radio", size=size)
            assert f"radio-{size}" in html

    def test_radio_default_size(self):
        """Test that default size is md"""
        html = self.render_component("radio")
        assert "radio-md" in html

    def test_radio_custom_class(self):
        """Test radio with custom CSS class"""
        html = self.render_component("radio", **{"class": "my-radio"})
        assert "my-radio" in html

    def test_radio_combination(self):
        """Test radio with variant, size, and custom class"""
        html = self.render_component(
            "radio",
            variant="primary",
            size="lg",
            **{"class": "my-radio"},
        )
        assert "radio-primary" in html
        assert "radio-lg" in html
        assert "my-radio" in html

    def test_radio_with_name(self):
        """Test radio with name attribute passed through"""
        html = self.render_component("radio", name="radio-group-1")
        assert 'name="radio-group-1"' in html

    def test_radio_group(self):
        """Test multiple radios in a group"""
        html = self.render_template_string(
            """
            {% load lb_tags %}
            <c-lb.radio name="radio-1" variant="primary" checked="checked" />
            <c-lb.radio name="radio-1" variant="primary" />
            """
        )
        assert html.count("radio-primary") == 2
        assert 'name="radio-1"' in html
