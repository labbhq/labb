from labb.tests.components.test_base import ComponentTestBase


class TestMockupPhone(ComponentTestBase):
    """Test mockup-phone component"""

    def test_basic_mockup_phone(self):
        """Test basic phone mockup rendering"""
        html = self.render_component("mockup-phone", slot_content="<div>Screen</div>")
        assert "mockup-phone" in html
        assert "Screen" in html

    def test_mockup_phone_custom_class(self):
        """Test phone mockup with custom CSS class"""
        html = self.render_component(
            "mockup-phone",
            slot_content="<div>Screen</div>",
            **{"class": "border-primary"},
        )
        assert "border-primary" in html


class TestMockupPhoneCamera(ComponentTestBase):
    """Test mockup-phone.camera component"""

    def test_basic_camera(self):
        """Test basic phone camera rendering"""
        html = self.render_component("mockup-phone.camera")
        assert "mockup-phone-camera" in html

    def test_camera_custom_class(self):
        """Test phone camera with custom class"""
        html = self.render_component("mockup-phone.camera", **{"class": "custom"})
        assert "custom" in html


class TestMockupPhoneDisplay(ComponentTestBase):
    """Test mockup-phone.display component"""

    def test_basic_display(self):
        """Test basic phone display rendering"""
        html = self.render_component("mockup-phone.display", slot_content="Hello")
        assert "mockup-phone-display" in html
        assert "Hello" in html

    def test_display_custom_class(self):
        """Test phone display with custom class"""
        html = self.render_component(
            "mockup-phone.display",
            slot_content="Hello",
            **{"class": "bg-neutral-900"},
        )
        assert "bg-neutral-900" in html

    def test_display_with_img(self):
        """Test phone display with img prop"""
        html = self.render_component(
            "mockup-phone.display",
            img="https://example.com/photo.webp",
            alt="wallpaper",
        )
        assert '<img src="https://example.com/photo.webp"' in html
        assert 'alt="wallpaper"' in html

    def test_display_img_no_slot(self):
        """Test phone display with img prop ignores slot content"""
        html = self.render_component(
            "mockup-phone.display",
            img="https://example.com/photo.webp",
            slot_content="Should not appear",
        )
        assert "<img" in html
        assert "Should not appear" not in html
