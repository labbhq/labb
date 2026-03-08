from labb.tests.components.test_base import ComponentTestBase


class TestLabel(ComponentTestBase):
    """Test label component"""

    def test_basic_label(self):
        """Test basic label rendering"""
        html = self.render_component("label", slot_content="Help text")
        assert "label" in html
        assert "Help text" in html

    def test_label_as_p_default(self):
        """Test label renders as p by default"""
        html = self.render_component("label", slot_content="Text")
        assert "<p" in html

    def test_label_as_span(self):
        """Test label rendered as span"""
        html = self.render_component("label", slot_content="Text", **{"as": "span"})
        assert "<span" in html

    def test_label_as_label(self):
        """Test label rendered as label element"""
        html = self.render_component("label", slot_content="Text", **{"as": "label"})
        assert "<label" in html

    def test_label_custom_class(self):
        """Test label with custom CSS class"""
        html = self.render_component(
            "label",
            slot_content="Max 2MB",
            **{"class": "text-error"},
        )
        assert "text-error" in html
        assert "Max 2MB" in html

    def test_label_floating(self):
        """Test label with floating flag"""
        html = self.render_component(
            "label",
            floating=True,
            slot_content='<span>Email</span><input type="text" class="input" />',
        )
        assert "floating-label" in html
        assert "<label" in html

    def test_label_floating_custom_class(self):
        """Test floating label with custom class"""
        html = self.render_component(
            "label",
            floating=True,
            slot_content='<span>Email</span><input type="text" class="input" />',
            **{"class": "w-full"},
        )
        assert "floating-label" in html
        assert "w-full" in html

    def test_label_not_floating_by_default(self):
        """Test label does not have floating-label class by default"""
        html = self.render_component("label", slot_content="Text")
        assert "floating-label" not in html
