from labb.tests.components.test_base import ComponentTestBase


class TestMockupWindow(ComponentTestBase):
    """Test mockup-window component"""

    def test_basic_mockup_window(self):
        """Test basic window mockup rendering"""
        html = self.render_component("mockup-window", slot_content="<div>Hello!</div>")
        assert "mockup-window" in html
        assert "Hello!" in html

    def test_mockup_window_custom_class(self):
        """Test window mockup with custom CSS class"""
        html = self.render_component(
            "mockup-window",
            slot_content="<div>Hello!</div>",
            **{"class": "border border-base-300 w-full"},
        )
        assert "border" in html
        assert "w-full" in html
