from labb.tests.components.test_base import ComponentTestBase


class TestTooltip(ComponentTestBase):
    """Test tooltip component"""

    def test_basic_tooltip(self):
        """Test basic tooltip rendering with text tip"""
        html = self.render_component(
            "tooltip", tip="Hello", slot_content="<button>Hover me</button>"
        )
        assert "tooltip" in html
        assert 'data-tip="Hello"' in html

    def test_tooltip_placements(self):
        """Test tooltip placement variants"""
        placements = ["top", "bottom", "left", "right"]
        for placement in placements:
            html = self.render_component(
                "tooltip",
                tip="Tip",
                placement=placement,
                slot_content="<button>Btn</button>",
            )
            assert f"tooltip-{placement}" in html

    def test_tooltip_default_placement(self):
        """Test that default placement is top"""
        html = self.render_component(
            "tooltip", tip="Tip", slot_content="<button>Btn</button>"
        )
        assert "tooltip-top" in html

    def test_tooltip_alignment(self):
        """Test tooltip alignment modifiers"""
        for align in ["start", "center", "end"]:
            html = self.render_component(
                "tooltip", tip="Tip", align=align, slot_content="<button>Btn</button>"
            )
            assert f"tooltip-{align}" in html

    def test_tooltip_no_alignment_by_default(self):
        """Test that no alignment class is applied by default (centered)"""
        html = self.render_component(
            "tooltip", tip="Tip", slot_content="<button>Btn</button>"
        )
        assert "tooltip-start" not in html
        assert "tooltip-end" not in html

    def test_tooltip_variants(self):
        """Test tooltip color variants"""
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
                "tooltip",
                tip="Tip",
                variant=variant,
                slot_content="<button>Btn</button>",
            )
            assert f"tooltip-{variant}" in html

    def test_tooltip_open(self):
        """Test tooltip forced open"""
        html = self.render_component(
            "tooltip",
            tip="Always visible",
            open="true",
            slot_content="<button>Btn</button>",
        )
        assert "tooltip-open" in html

    def test_tooltip_not_open_by_default(self):
        """Test tooltip is not forced open by default"""
        html = self.render_component(
            "tooltip", tip="Tip", slot_content="<button>Btn</button>"
        )
        assert "tooltip-open" not in html

    def test_tooltip_without_tip(self):
        """Test tooltip without data-tip (for use with tooltip.content)"""
        html = self.render_component("tooltip", slot_content="<button>Btn</button>")
        assert "tooltip" in html
        assert "data-tip" not in html

    def test_tooltip_custom_class(self):
        """Test tooltip with custom CSS class"""
        html = self.render_component(
            "tooltip",
            tip="Tip",
            slot_content="<button>Btn</button>",
            **{"class": "my-tooltip"},
        )
        assert "my-tooltip" in html

    def test_tooltip_combination(self):
        """Test tooltip with variant, placement, and open"""
        html = self.render_component(
            "tooltip",
            tip="Info tip",
            variant="primary",
            placement="bottom",
            open="true",
            slot_content="<button>Btn</button>",
        )
        assert "tooltip-primary" in html
        assert "tooltip-bottom" in html
        assert "tooltip-open" in html
        assert 'data-tip="Info tip"' in html


class TestTooltipContent(ComponentTestBase):
    """Test tooltip.content sub-component"""

    def test_basic_content(self):
        """Test basic tooltip content rendering"""
        html = self.render_component(
            "tooltip.content", slot_content="<p>Rich content</p>"
        )
        assert "tooltip-content" in html
        assert "Rich content" in html

    def test_content_custom_class(self):
        """Test tooltip content with custom class"""
        html = self.render_component(
            "tooltip.content",
            slot_content="<p>Content</p>",
            **{"class": "bg-base-200"},
        )
        assert "tooltip-content" in html
        assert "bg-base-200" in html
