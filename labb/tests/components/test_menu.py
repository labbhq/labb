from labb.tests.components.test_base import ComponentTestBase


class TestMenu(ComponentTestBase):
    """c-lb.menu — base, direction and size."""

    def test_base_class(self):
        assert "menu" in self.render_component("menu")

    def test_renders_a_ul(self):
        assert "<ul" in self.render_component("menu")

    def test_slot(self):
        html = self.render_component("menu", slot_content="<li>Item</li>")
        assert "<li>Item</li>" in html

    def test_custom_class(self):
        assert "w-56" in self.render_component("menu", class_="w-56")

    def test_direction_defaults_to_vertical(self):
        # daisyUI's .menu-vertical is not a no-op: it switches the element to
        # inline-flex, so the default has to emit it.
        assert "menu-vertical" in self.render_component("menu")

    def test_direction_vertical(self):
        assert "menu-vertical" in self.render_component("menu", direction="vertical")

    def test_direction_horizontal(self):
        html = self.render_component("menu", direction="horizontal")
        assert "menu-horizontal" in html
        assert "menu-vertical" not in html

    def test_sizes(self):
        for size in ("xs", "sm", "md", "lg", "xl"):
            assert f"menu-{size}" in self.render_component("menu", size=size)

    def test_size_defaults_to_md(self):
        assert "menu-md" in self.render_component("menu")

    def test_direction_is_reactive(self):
        html = self.render_component("menu", direction="$nav.dir:horizontal")
        assert "menu-horizontal" in html
        assert "data-attr:class" in html
