from labb.tests.components.test_base import ComponentTestBase


class TestDock(ComponentTestBase):
    """Test dock component"""

    def test_basic_dock(self):
        """Test basic dock rendering"""
        html = self.render_component(
            "dock",
            slot_content="<button>Home</button>",
        )
        assert "dock" in html
        assert "Home" in html

    def test_dock_sizes(self):
        """Test dock size variants"""
        sizes = ["xs", "sm", "md", "lg", "xl"]
        for size in sizes:
            html = self.render_component(
                "dock",
                size=size,
                slot_content="<button>Item</button>",
            )
            assert f"dock-{size}" in html

    def test_dock_default_size(self):
        """Test that default size is md"""
        html = self.render_component(
            "dock",
            slot_content="<button>Item</button>",
        )
        assert "dock-md" in html

    def test_dock_variants(self):
        """Test dock color variants"""
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
                "dock",
                variant=variant,
                slot_content="<button>Item</button>",
            )
            assert f"bg-{variant}" in html
            assert f"text-{variant}-content" in html

    def test_dock_custom_class(self):
        """Test dock with custom CSS class"""
        html = self.render_component(
            "dock",
            slot_content="<button>Item</button>",
            **{"class": "bg-base-200"},
        )
        assert "bg-base-200" in html

    def test_dock_with_active_item(self):
        """Test dock with an active navigation item"""
        html = self.render_template_string(
            """
            {% load lb_tags %}
            <c-lb.dock>
                <button>Home</button>
                <button class="dock-active">Search</button>
                <button>Settings</button>
            </c-lb.dock>
            """
        )
        assert "dock" in html
        assert "dock-active" in html


class TestDockLabel(ComponentTestBase):
    """Test dock.label sub-component"""

    def test_basic_label(self):
        """Test basic dock label rendering"""
        html = self.render_component("dock.label", slot_content="Home")
        assert "dock-label" in html
        assert "Home" in html

    def test_label_custom_class(self):
        """Test dock label with custom class"""
        html = self.render_component(
            "dock.label",
            slot_content="Search",
            **{"class": "text-xs"},
        )
        assert "dock-label" in html
        assert "text-xs" in html
