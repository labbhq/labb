from labb.tests.components.test_base import ComponentTestBase


class TestToast(ComponentTestBase):
    """Test toast component"""

    def test_basic_toast(self):
        """Test basic toast rendering"""
        html = self.render_component(
            "toast", slot_content="<div class='alert'>Message</div>"
        )
        assert "toast" in html
        assert "Message" in html

    def test_toast_horizontal_positions(self):
        """Test toast horizontal positioning"""
        positions = ["start", "center", "end"]
        for pos in positions:
            html = self.render_component(
                "toast",
                horizontal=pos,
                slot_content="<div>Msg</div>",
            )
            assert f"toast-{pos}" in html

    def test_toast_vertical_positions(self):
        """Test toast vertical positioning"""
        positions = ["top", "middle", "bottom"]
        for pos in positions:
            html = self.render_component(
                "toast",
                vertical=pos,
                slot_content="<div>Msg</div>",
            )
            assert f"toast-{pos}" in html

    def test_toast_combined_position(self):
        """Test toast with both horizontal and vertical positioning"""
        html = self.render_component(
            "toast",
            horizontal="end",
            vertical="top",
            slot_content="<div>Msg</div>",
        )
        assert "toast-end" in html
        assert "toast-top" in html

    def test_toast_no_position_by_default(self):
        """Test that no position classes are added by default"""
        html = self.render_component("toast", slot_content="<div>Msg</div>")
        assert "toast-start" not in html
        assert "toast-center" not in html
        assert "toast-end" not in html
        assert "toast-top" not in html
        assert "toast-middle" not in html
        assert "toast-bottom" not in html

    def test_toast_custom_class(self):
        """Test toast with custom CSS class"""
        html = self.render_component(
            "toast",
            slot_content="<div>Msg</div>",
            **{"class": "z-50"},
        )
        assert "z-50" in html
