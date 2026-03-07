from labb.tests.components.test_base import ComponentTestBase


class TestDivider(ComponentTestBase):
    """Test divider component"""

    def test_basic_divider(self):
        """Test basic divider rendering"""
        html = self.render_component("divider")
        assert "divider" in html

    def test_divider_with_text(self):
        """Test divider with text content"""
        html = self.render_component("divider", slot_content="OR")
        assert "divider" in html
        assert "OR" in html

    def test_divider_variants(self):
        """Test divider color variants"""
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
            html = self.render_component("divider", variant=variant)
            assert f"divider-{variant}" in html

    def test_divider_no_variant_by_default(self):
        """Test that no variant class is added by default"""
        html = self.render_component("divider")
        assert "divider-primary" not in html
        assert "divider-neutral" not in html

    def test_divider_directions(self):
        """Test divider direction variants"""
        for direction in ["horizontal", "vertical"]:
            html = self.render_component("divider", direction=direction)
            assert f"divider-{direction}" in html

    def test_divider_positions(self):
        """Test divider text position"""
        for position in ["start", "end"]:
            html = self.render_component(
                "divider", position=position, slot_content="OR"
            )
            assert f"divider-{position}" in html

    def test_divider_combination(self):
        """Test divider with multiple options"""
        html = self.render_component(
            "divider",
            variant="primary",
            direction="horizontal",
            position="start",
            slot_content="OR",
        )
        assert "divider-primary" in html
        assert "divider-horizontal" in html
        assert "divider-start" in html

    def test_divider_custom_class(self):
        """Test divider with custom CSS class"""
        html = self.render_component("divider", **{"class": "my-4"})
        assert "my-4" in html
