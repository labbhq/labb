from labb.tests.components.test_base import ComponentTestBase


class TestSelect(ComponentTestBase):
    """Test select component"""

    def test_basic_select(self):
        """Test basic select rendering"""
        html = self.render_component(
            "select",
            slot_content="<option>Option 1</option><option>Option 2</option>",
        )
        assert "select" in html
        assert "<select" in html
        assert "Option 1" in html

    def test_select_variants(self):
        """Test select color variants"""
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
            html = self.render_component(
                "select",
                variant=variant,
                slot_content="<option>A</option>",
            )
            assert f"select-{variant}" in html

    def test_select_sizes(self):
        """Test select size variants"""
        sizes = ["xs", "sm", "md", "lg", "xl"]
        for size in sizes:
            html = self.render_component(
                "select",
                size=size,
                slot_content="<option>A</option>",
            )
            assert f"select-{size}" in html

    def test_select_default_size(self):
        """Test that default size is md"""
        html = self.render_component(
            "select",
            slot_content="<option>A</option>",
        )
        assert "select-md" in html

    def test_select_ghost(self):
        """Test ghost style variant"""
        html = self.render_component(
            "select",
            ghost="true",
            slot_content="<option>A</option>",
        )
        assert "select-ghost" in html

    def test_select_no_ghost_by_default(self):
        """Test ghost not applied by default"""
        html = self.render_component(
            "select",
            slot_content="<option>A</option>",
        )
        assert "select-ghost" not in html

    def test_select_combination(self):
        """Test select with variant, size, and custom class"""
        html = self.render_component(
            "select",
            variant="primary",
            size="lg",
            slot_content="<option>A</option>",
            **{"class": "w-full"},
        )
        assert "select-primary" in html
        assert "select-lg" in html
        assert "w-full" in html

    def test_select_custom_class(self):
        """Test select with custom CSS class"""
        html = self.render_component(
            "select",
            slot_content="<option>A</option>",
            **{"class": "w-full"},
        )
        assert "w-full" in html
