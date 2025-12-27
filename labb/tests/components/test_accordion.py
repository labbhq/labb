from labb.tests.components.test_base import ComponentTestBase


class TestAccordion(ComponentTestBase):
    """Test accordion component"""

    def test_accordion_basic(self):
        """Test basic accordion rendering"""
        html = self.render_component("accordion")
        assert '<div class="' in html
        assert "collapse" not in html  # Basic accordion shouldn't have collapse class

    def test_accordion_with_join(self):
        """Test accordion with join layout"""
        html = self.render_component("accordion", join="true")
        assert "join join-vertical" in html

    def test_accordion_with_class(self):
        """Test accordion with custom class"""
        html = self.render_component("accordion", **{"class": "custom-class"})
        assert "custom-class" in html

    def test_accordion_item_basic(self):
        """Test basic accordion item rendering"""
        html = self.render_component(
            "accordion.item", name="test-accordion", title="Test Title"
        )
        assert 'name="test-accordion"' in html
        assert "collapse" in html
        assert "Test Title" in html
        assert "collapse-title" in html
        assert "collapse-content" in html

    def test_accordion_item_checked(self):
        """Test accordion item with checked state"""
        html = self.render_component(
            "accordion.item", name="test-accordion", title="Test Title", checked="true"
        )
        assert "checked" in html

    def test_accordion_item_with_style(self):
        """Test accordion item with different styles"""
        styles = ["arrow", "plus"]
        for style in styles:
            html = self.render_component(
                "accordion.item", name="test-accordion", title="Test Title", style=style
            )
            if style == "arrow":
                assert "collapse-arrow" in html
            elif style == "plus":
                assert "collapse-plus" in html

    def test_accordion_item_with_join(self):
        """Test accordion item with join layout"""
        html = self.render_component(
            "accordion.item", name="test-accordion", title="Test Title", join="true"
        )
        assert "join-item" in html

    def test_accordion_item_with_border(self):
        """Test accordion item with border"""
        html = self.render_component(
            "accordion.item", name="test-accordion", title="Test Title", border="true"
        )
        assert "border border-base-300" in html

    def test_accordion_item_with_class(self):
        """Test accordion item with custom class"""
        html = self.render_component(
            "accordion.item",
            name="test-accordion",
            title="Test Title",
            **{"class": "custom-class"},
        )
        assert "custom-class" in html

    def test_accordion_item_without_title(self):
        """Test accordion item without title attribute"""
        html = self.render_component("accordion.item", name="test-accordion")
        assert "collapse-title" not in html

    def test_accordion_item_radio_input(self):
        """Test accordion item has radio input"""
        html = self.render_component(
            "accordion.item", name="test-accordion", title="Test Title"
        )
        assert 'type="radio"' in html
        assert 'name="test-accordion"' in html

    def test_accordion_item_content_slot(self):
        """Test accordion item content slot"""
        html = self.render_component(
            "accordion.item", name="test-accordion", title="Test Title"
        )
        assert "collapse-content" in html

    def test_accordion_combined_features(self):
        """Test accordion with multiple features combined"""
        html = self.render_component(
            "accordion", join="true", **{"class": "custom-accordion"}
        )
        assert "join join-vertical" in html
        assert "custom-accordion" in html

    def test_accordion_item_combined_features(self):
        """Test accordion item with multiple features combined"""
        html = self.render_component(
            "accordion.item",
            name="test-accordion",
            title="Test Title",
            style="arrow",
            join="true",
            border="true",
            checked="true",
            **{"class": "custom-item"},
        )
        assert "collapse-arrow" in html
        assert "join-item" in html
        assert "border border-base-300" in html
        assert "checked" in html
        assert "custom-item" in html
        assert "Test Title" in html
