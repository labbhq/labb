from labb.tests.components.test_base import ComponentTestBase, ComponentTestTemplate


class TestStatGroup(ComponentTestBase):
    """Test suite for the stat.group container component"""

    def test_stat_group_renders_with_base_class(self):
        """Test that stat.group renders with the stats base class"""
        html = self.render_component("stat.group", slot_content="<div>Stat</div>")
        self.assert_classes_present(html, {"stats"})

    def test_stat_group_default_direction_is_horizontal(self):
        """Test that default direction is horizontal"""
        html = self.render_component("stat.group", slot_content="<div>Stat</div>")
        assert "stats-horizontal" in html

    def test_stat_group_vertical_direction(self):
        """Test stats with vertical direction"""
        html = self.render_component(
            "stat.group", direction="vertical", slot_content="<div>Stat</div>"
        )
        assert "stats-vertical" in html

    def test_stat_group_custom_class(self):
        """Test stats with custom CSS class"""
        html = self.render_component(
            "stat.group",
            slot_content="<div>Stat</div>",
            **{"class": "shadow"},
        )
        assert "shadow" in html
        assert "stats" in html


class TestStat(ComponentTestTemplate):
    """Test suite for the stat component"""

    component_name = "stat"

    def test_stat_renders_with_base_class(self):
        """Test that stat renders with the stat base class"""
        html = self.render_component("stat", slot_content="<div>Content</div>")
        self.assert_classes_present(html, {"stat"})

    def test_stat_custom_class(self):
        """Test stat with custom CSS class"""
        html = self.render_component(
            "stat",
            slot_content="<div>Content</div>",
            **{"class": "place-items-center"},
        )
        assert "place-items-center" in html


class TestStatTitle(ComponentTestBase):
    """Test suite for the stat.title component"""

    def test_stat_title_renders_with_base_class(self):
        """Test that stat.title renders with the stat-title base class"""
        html = self.render_component("stat.title", slot_content="Total Views")
        self.assert_classes_present(html, {"stat-title"})
        assert "Total Views" in html


class TestStatValue(ComponentTestBase):
    """Test suite for the stat.value component"""

    def test_stat_value_renders_with_base_class(self):
        """Test that stat.value renders with the stat-value base class"""
        html = self.render_component("stat.value", slot_content="89,400")
        self.assert_classes_present(html, {"stat-value"})
        assert "89,400" in html

    def test_stat_value_variants(self):
        """Test stat.value color variants"""
        variants = [
            "primary",
            "secondary",
            "accent",
            "neutral",
            "info",
            "success",
            "warning",
            "error",
        ]
        for variant in variants:
            html = self.render_component(
                "stat.value", variant=variant, slot_content="25.6K"
            )
            assert f"text-{variant}" in html

    def test_stat_value_custom_class(self):
        """Test stat.value with custom class"""
        html = self.render_component(
            "stat.value",
            slot_content="100",
            **{"class": "font-bold"},
        )
        assert "font-bold" in html


class TestStatDesc(ComponentTestBase):
    """Test suite for the stat.desc component"""

    def test_stat_desc_renders_with_base_class(self):
        """Test that stat.desc renders with the stat-desc base class"""
        html = self.render_component(
            "stat.desc", slot_content="21% more than last month"
        )
        self.assert_classes_present(html, {"stat-desc"})
        assert "21% more than last month" in html

    def test_stat_desc_variants(self):
        """Test stat.desc color variants"""
        for variant in ["success", "error"]:
            html = self.render_component(
                "stat.desc", variant=variant, slot_content="Up 10%"
            )
            assert f"text-{variant}" in html


class TestStatFigure(ComponentTestBase):
    """Test suite for the stat.figure component"""

    def test_stat_figure_renders_with_base_class(self):
        """Test that stat.figure renders with the stat-figure base class"""
        html = self.render_component("stat.figure")
        self.assert_classes_present(html, {"stat-figure"})

    def test_stat_figure_with_icon(self):
        """Test stat.figure with an icon"""
        html = self.render_component("stat.figure", icon="rmx.heart")
        assert "stat-figure" in html
        assert "<svg" in html

    def test_stat_figure_variant(self):
        """Test stat.figure with color variant"""
        html = self.render_component("stat.figure", variant="primary", icon="rmx.heart")
        assert "text-primary" in html


class TestStatActions(ComponentTestBase):
    """Test suite for the stat.actions component"""

    def test_stat_actions_renders_with_base_class(self):
        """Test that stat.actions renders with the stat-actions base class"""
        html = self.render_component(
            "stat.actions",
            slot_content='<button class="btn btn-xs">View</button>',
        )
        self.assert_classes_present(html, {"stat-actions"})
