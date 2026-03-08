from labb.tests.components.test_base import ComponentTestBase


class TestSteps(ComponentTestBase):
    """Test steps component"""

    def test_basic_steps(self):
        """Test basic steps rendering"""
        html = self.render_template_string(
            """
            {% load lb_tags %}
            <c-lb.steps>
                <c-lb.steps.item variant="primary">Register</c-lb.steps.item>
                <c-lb.steps.item variant="primary">Choose plan</c-lb.steps.item>
                <c-lb.steps.item>Purchase</c-lb.steps.item>
            </c-lb.steps>
            """
        )
        assert "steps" in html
        assert "step" in html
        assert "Register" in html

    def test_steps_horizontal(self):
        """Test horizontal steps (default)"""
        html = self.render_component(
            "steps",
            slot_content="<li class='step'>Step 1</li>",
        )
        assert "steps-horizontal" in html

    def test_steps_vertical(self):
        """Test vertical steps"""
        html = self.render_component(
            "steps",
            direction="vertical",
            slot_content="<li class='step'>Step 1</li>",
        )
        assert "steps-vertical" in html

    def test_steps_custom_class(self):
        """Test steps with custom CSS class"""
        html = self.render_component(
            "steps",
            slot_content="<li class='step'>Step 1</li>",
            **{"class": "w-full"},
        )
        assert "w-full" in html


class TestStepsItem(ComponentTestBase):
    """Test steps.item sub-component"""

    def test_basic_item(self):
        """Test basic step item rendering"""
        html = self.render_component("steps.item", slot_content="Register")
        assert "step" in html
        assert "Register" in html

    def test_item_variants(self):
        """Test step color variants"""
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
                "steps.item", variant=variant, slot_content=f"{variant} step"
            )
            assert f"step-{variant}" in html

    def test_item_with_data_content(self):
        """Test step item with custom data-content"""
        html = self.render_component(
            "steps.item",
            variant="neutral",
            content="✓",
            slot_content="Done",
        )
        assert 'data-content="✓"' in html

    def test_item_without_data_content(self):
        """Test step item without data-content"""
        html = self.render_component("steps.item", slot_content="Step 1")
        assert "data-content" not in html

    def test_item_custom_class(self):
        """Test step item with custom class"""
        html = self.render_component(
            "steps.item",
            slot_content="Custom",
            **{"class": "my-step"},
        )
        assert "my-step" in html
