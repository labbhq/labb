from labb.tests.components.test_base import ComponentTestBase, ComponentTestTemplate


class TestList(ComponentTestTemplate):
    """Test suite for the list component"""

    component_name = "list"

    def test_list_renders_with_base_class(self):
        """Test that list renders with the list base class"""
        html = self.render_component("list", slot_content="<li>Item</li>")
        self.assert_classes_present(html, {"list"})

    def test_list_default_tag_is_ul(self):
        """Test that the default HTML tag is ul"""
        html = self.render_component("list", slot_content="<li>Item</li>")
        assert "<ul" in html
        assert "</ul>" in html

    def test_list_as_div(self):
        """Test list renders as a div when as=div"""
        html = self.render_component(
            "list", slot_content="<div>Item</div>", **{"as": "div"}
        )
        assert "<div" in html

    def test_list_as_ol(self):
        """Test list renders as an ol when as=ol"""
        html = self.render_component(
            "list", slot_content="<li>Item</li>", **{"as": "ol"}
        )
        assert "<ol" in html
        assert "</ol>" in html

    def test_list_custom_class(self):
        """Test list with custom CSS class"""
        html = self.render_component(
            "list",
            slot_content="<li>Item</li>",
            **{"class": "bg-base-100 rounded-box"},
        )
        assert "bg-base-100" in html
        assert "rounded-box" in html


class TestListRow(ComponentTestBase):
    """Test suite for the list.row component"""

    def test_list_row_renders_with_base_class(self):
        """Test that list.row renders with the list-row base class"""
        html = self.render_component("list.row", slot_content="<div>Content</div>")
        self.assert_classes_present(html, {"list-row"})

    def test_list_row_default_tag_is_li(self):
        """Test that the default HTML tag is li"""
        html = self.render_component("list.row", slot_content="<div>Content</div>")
        assert "<li" in html
        assert "</li>" in html

    def test_list_row_as_div(self):
        """Test list.row renders as a div when as=div"""
        html = self.render_component(
            "list.row", slot_content="<div>Content</div>", **{"as": "div"}
        )
        # Should have at least one div with list-row class
        assert "list-row" in html

    def test_list_row_custom_class(self):
        """Test list.row with custom CSS class"""
        html = self.render_component(
            "list.row",
            slot_content="<div>Content</div>",
            **{"class": "hover:bg-base-200"},
        )
        assert "hover:bg-base-200" in html

    def test_list_row_renders_slot_content(self):
        """Test that slot content is rendered"""
        html = self.render_component(
            "list.row",
            slot_content="<div>Column 1</div><div>Column 2</div>",
        )
        assert "Column 1" in html
        assert "Column 2" in html
