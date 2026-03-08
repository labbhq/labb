from labb.tests.components.test_base import ComponentTestBase


class TestIndicator(ComponentTestBase):
    """Test indicator component"""

    def test_basic_indicator(self):
        """Test basic indicator rendering"""
        html = self.render_component("indicator", slot_content="<div>Content</div>")
        assert "indicator" in html
        assert "Content" in html

    def test_indicator_custom_class(self):
        """Test indicator with custom CSS class"""
        html = self.render_component(
            "indicator",
            slot_content="<div>Content</div>",
            **{"class": "w-32"},
        )
        assert "w-32" in html


class TestIndicatorItem(ComponentTestBase):
    """Test indicator.item component"""

    def test_basic_indicator_item(self):
        """Test basic indicator item rendering"""
        html = self.render_component("indicator.item", slot_content="New")
        assert "indicator-item" in html
        assert "New" in html

    def test_indicator_item_horizontal(self):
        """Test indicator item horizontal positions"""
        positions = ["start", "center", "end"]
        for pos in positions:
            html = self.render_component(
                "indicator.item", horizontal=pos, slot_content="!"
            )
            assert f"indicator-{pos}" in html

    def test_indicator_item_vertical(self):
        """Test indicator item vertical positions"""
        positions = ["top", "middle", "bottom"]
        for pos in positions:
            html = self.render_component(
                "indicator.item", vertical=pos, slot_content="!"
            )
            assert f"indicator-{pos}" in html

    def test_indicator_item_combined(self):
        """Test indicator item with both positions"""
        html = self.render_component(
            "indicator.item",
            horizontal="center",
            vertical="middle",
            slot_content="!",
        )
        assert "indicator-center" in html
        assert "indicator-middle" in html

    def test_indicator_item_no_position_by_default(self):
        """Test that no position classes are added by default"""
        html = self.render_component("indicator.item", slot_content="!")
        assert "indicator-start" not in html
        assert "indicator-center" not in html
        assert "indicator-end" not in html
        assert "indicator-top" not in html
        assert "indicator-middle" not in html
        assert "indicator-bottom" not in html

    def test_indicator_item_default_shape_is_badge(self):
        """Test default shape is badge"""
        html = self.render_component(
            "indicator.item", variant="primary", slot_content="New"
        )
        assert "badge" in html
        assert "badge-primary" in html

    def test_indicator_item_badge_variants(self):
        """Test indicator item badge shape color variants"""
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
                "indicator.item", shape="badge", variant=variant, slot_content="!"
            )
            assert "badge" in html
            assert f"badge-{variant}" in html

    def test_indicator_item_badge_sizes(self):
        """Test indicator item badge shape sizes"""
        sizes = ["xs", "sm", "md", "lg", "xl"]
        for size in sizes:
            html = self.render_component(
                "indicator.item", shape="badge", size=size, slot_content="!"
            )
            assert f"badge-{size}" in html

    def test_indicator_item_status_shape(self):
        """Test indicator item status shape"""
        html = self.render_component(
            "indicator.item",
            shape="status",
            variant="primary",
            size="md",
            slot_content="",
        )
        assert "status" in html
        assert "status-primary" in html
        assert "status-md" in html

    def test_indicator_item_status_variants(self):
        """Test indicator item status shape color variants"""
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
                "indicator.item", shape="status", variant=variant, slot_content=""
            )
            assert "status" in html
            assert f"status-{variant}" in html

    def test_indicator_item_status_sizes(self):
        """Test indicator item status shape sizes"""
        sizes = ["xs", "sm", "md", "lg", "xl"]
        for size in sizes:
            html = self.render_component(
                "indicator.item", shape="status", size=size, slot_content=""
            )
            assert f"status-{size}" in html

    def test_indicator_item_none_shape(self):
        """Test indicator item none shape for full customisation"""
        html = self.render_component(
            "indicator.item", shape="none", slot_content="Custom"
        )
        assert "indicator-item" in html
        assert "badge" not in html
        assert "status" not in html

    def test_indicator_item_icon(self):
        """Test indicator item with icon"""
        html = self.render_component(
            "indicator.item", icon="rmx.bell", variant="primary", slot_content=""
        )
        assert "indicator-item" in html
        assert "<svg" in html

    def test_indicator_item_custom_class(self):
        """Test indicator item with custom CSS class"""
        html = self.render_component(
            "indicator.item",
            slot_content="!",
            **{"class": "badge badge-primary"},
        )
        assert "badge badge-primary" in html
