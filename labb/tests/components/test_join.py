from labb.tests.components.test_base import ComponentTestBase


class TestJoin(ComponentTestBase):
    """Test join component"""

    def test_basic_join(self):
        """Test basic join rendering"""
        html = self.render_component(
            "join", slot_content="<button class='btn join-item'>A</button>"
        )
        assert "join" in html

    def test_join_horizontal(self):
        """Test join horizontal direction"""
        html = self.render_component(
            "join",
            direction="horizontal",
            slot_content="<button>A</button>",
        )
        assert "join-horizontal" in html

    def test_join_vertical(self):
        """Test join vertical direction"""
        html = self.render_component(
            "join",
            direction="vertical",
            slot_content="<button>A</button>",
        )
        assert "join-vertical" in html

    def test_join_no_direction_by_default(self):
        """Test that no direction class is added by default"""
        html = self.render_component("join", slot_content="<button>A</button>")
        assert "join-horizontal" not in html
        assert "join-vertical" not in html

    def test_join_custom_class(self):
        """Test join with custom CSS class"""
        html = self.render_component(
            "join",
            slot_content="<button>A</button>",
            **{"class": "w-full"},
        )
        assert "w-full" in html
