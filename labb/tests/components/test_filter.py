from labb.tests.components.test_base import ComponentTestBase


class TestFilter(ComponentTestBase):
    """Test filter component"""

    def test_basic_filter(self):
        """Test basic filter rendering"""
        html = self.render_component(
            "filter",
            slot_content='<input class="btn" type="radio" name="f" aria-label="Vue" />',
        )
        assert "filter" in html

    def test_filter_as_form(self):
        """Test filter rendered as form element"""
        html = self.render_component(
            "filter",
            slot_content='<input class="btn" type="radio" name="f" aria-label="Vue" />',
            **{"as": "form"},
        )
        assert "<form" in html

    def test_filter_as_div_default(self):
        """Test filter renders as div by default"""
        html = self.render_component(
            "filter",
            slot_content='<input class="btn" type="radio" name="f" aria-label="Vue" />',
        )
        assert "<div" in html

    def test_filter_custom_class(self):
        """Test filter with custom CSS class"""
        html = self.render_component(
            "filter",
            slot_content='<input class="btn" type="radio" name="f" aria-label="Vue" />',
            **{"class": "my-filter"},
        )
        assert "my-filter" in html

    def test_filter_multi_select(self):
        """Test multiSelect removes filter class"""
        html = self.render_component(
            "filter",
            multiSelect=True,
            slot_content='<input class="btn" type="checkbox" name="f" aria-label="A" />',
        )
        assert "filter" not in html.split("class=")[1].split('"')[1]

    def test_filter_with_items(self):
        """Test filter with filter.item sub-components"""
        html = self.render_template_string(
            """
            {% load lb_tags %}
            <c-lb.filter>
                <c-lb.filter.item name="fw" label="All" reset />
                <c-lb.filter.item name="fw" label="Svelte" />
                <c-lb.filter.item name="fw" label="Vue" />
                <c-lb.filter.item name="fw" label="React" />
            </c-lb.filter>
            """
        )
        assert "filter" in html
        assert "btn" in html
        assert 'aria-label="Svelte"' in html


class TestFilterItem(ComponentTestBase):
    """Test filter.item sub-component"""

    def test_basic_item(self):
        """Test basic filter item rendering"""
        html = self.render_component("filter.item", label="Vue", name="fw")
        assert "btn" in html
        assert 'aria-label="Vue"' in html
        assert 'type="radio"' in html

    def test_item_reset(self):
        """Test filter reset item"""
        html = self.render_component(
            "filter.item", label="All", name="fw", reset="true"
        )
        assert "filter-reset" in html

    def test_item_reset_type(self):
        """Test filter item with type=reset"""
        html = self.render_component("filter.item", label="Clear", type="reset")
        assert 'type="reset"' in html
        assert "btn-square" in html

    def test_item_checkbox_type(self):
        """Test filter item as checkbox"""
        html = self.render_component(
            "filter.item", label="Option", name="opts", type="checkbox"
        )
        assert 'type="checkbox"' in html

    def test_item_custom_class(self):
        """Test filter item with custom class"""
        html = self.render_component(
            "filter.item",
            label="Test",
            name="f",
            **{"class": "btn-primary"},
        )
        assert "btn-primary" in html
