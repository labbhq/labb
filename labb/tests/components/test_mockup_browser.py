from labb.tests.components.test_base import ComponentTestBase


class TestMockupBrowser(ComponentTestBase):
    """Test mockup-browser component"""

    def test_basic_mockup_browser(self):
        """Test basic browser mockup rendering"""
        html = self.render_component("mockup-browser", slot_content="<div>Hello!</div>")
        assert "mockup-browser" in html
        assert "Hello!" in html

    def test_mockup_browser_with_url(self):
        """Test browser mockup with URL in toolbar"""
        html = self.render_component(
            "mockup-browser",
            url="https://daisyui.com",
            slot_content="<div>Content</div>",
        )
        assert "mockup-browser-toolbar" in html
        assert "https://daisyui.com" in html

    def test_mockup_browser_no_toolbar_without_url(self):
        """Test that toolbar is not rendered without URL"""
        html = self.render_component(
            "mockup-browser", slot_content="<div>Content</div>"
        )
        assert "mockup-browser-toolbar" not in html

    def test_mockup_browser_custom_class(self):
        """Test browser mockup with custom CSS class"""
        html = self.render_component(
            "mockup-browser",
            slot_content="<div>Content</div>",
            **{"class": "border border-base-300 w-full"},
        )
        assert "border" in html
        assert "w-full" in html
