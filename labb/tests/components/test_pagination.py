from labb.tests.components.test_base import ComponentTestBase


class TestPagination(ComponentTestBase):
    """Test pagination component"""

    def test_basic_pagination(self):
        """Test basic pagination rendering"""
        html = self.render_template_string(
            """
            {% load lb_tags %}
            <c-lb.pagination>
                <c-lb.pagination.item>1</c-lb.pagination.item>
                <c-lb.pagination.item active>2</c-lb.pagination.item>
                <c-lb.pagination.item>3</c-lb.pagination.item>
            </c-lb.pagination>
            """
        )
        assert "join" in html
        assert "join-item" in html
        assert "btn" in html

    def test_pagination_container_class(self):
        """Test pagination container has join class"""
        html = self.render_component(
            "pagination",
            slot_content="<button>1</button>",
        )
        assert "join" in html

    def test_pagination_custom_class(self):
        """Test pagination with custom CSS class"""
        html = self.render_component(
            "pagination",
            slot_content="<button>1</button>",
            **{"class": "my-custom"},
        )
        assert "my-custom" in html


class TestPaginationItem(ComponentTestBase):
    """Test pagination.item sub-component"""

    def test_basic_item(self):
        """Test basic pagination item rendering"""
        html = self.render_component("pagination.item", slot_content="1")
        assert "join-item" in html
        assert "btn" in html
        assert "1" in html

    def test_item_active(self):
        """Test active pagination item"""
        html = self.render_component("pagination.item", active="true", slot_content="2")
        assert "btn-active" in html

    def test_item_disabled(self):
        """Test disabled pagination item"""
        html = self.render_component(
            "pagination.item", disabled="true", slot_content="..."
        )
        assert "btn-disabled" in html

    def test_item_sizes(self):
        """Test pagination item sizes"""
        sizes = ["xs", "sm", "md", "lg", "xl"]
        for size in sizes:
            html = self.render_component("pagination.item", size=size, slot_content="1")
            assert f"btn-{size}" in html

    def test_item_custom_class(self):
        """Test pagination item with custom class"""
        html = self.render_component(
            "pagination.item",
            slot_content="1",
            **{"class": "btn-square"},
        )
        assert "btn-square" in html

    def test_item_icon_start(self):
        """Test pagination item with icon at the start (default)"""
        html = self.render_component(
            "pagination.item",
            icon="rmx.arrow-left",
            slot_content="Previous",
        )
        assert 'is="lbi"' in html or "<svg" in html
        assert "Previous" in html

    def test_item_icon_end(self):
        """Test pagination item with icon at the end"""
        html = self.render_template_string(
            '{% load cotton %}<c-lb.pagination.item icon.end="rmx.arrow-right">Next</c-lb.pagination.item>'
        )
        assert "<svg" in html
        assert "Next" in html

    def test_item_icon_class(self):
        """Test pagination item with custom icon class"""
        html = self.render_template_string(
            '{% load cotton %}<c-lb.pagination.item icon="rmx.arrow-left" icon.class="my-icon-class">Prev</c-lb.pagination.item>'
        )
        assert "<svg" in html
        assert "my-icon-class" in html
