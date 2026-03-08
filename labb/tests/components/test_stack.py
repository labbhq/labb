from labb.tests.components.test_base import ComponentTestBase


class TestStack(ComponentTestBase):
    """Test stack component"""

    def test_basic_stack(self):
        """Test basic stack rendering"""
        html = self.render_component("stack", slot_content="<div>1</div><div>2</div>")
        assert "stack" in html

    def test_stack_directions(self):
        """Test stack direction variants"""
        directions = ["top", "bottom", "start", "end"]
        for direction in directions:
            html = self.render_component(
                "stack",
                direction=direction,
                slot_content="<div>1</div>",
            )
            assert f"stack-{direction}" in html

    def test_stack_no_direction_by_default(self):
        """Test that no direction class is added by default"""
        html = self.render_component("stack", slot_content="<div>1</div>")
        assert "stack-top" not in html
        assert "stack-bottom" not in html
        assert "stack-start" not in html
        assert "stack-end" not in html

    def test_stack_custom_class(self):
        """Test stack with custom CSS class"""
        html = self.render_component(
            "stack",
            slot_content="<div>1</div>",
            **{"class": "h-20 w-32"},
        )
        assert "h-20" in html
        assert "w-32" in html
