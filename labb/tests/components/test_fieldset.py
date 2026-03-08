from labb.tests.components.test_base import ComponentTestBase


class TestFieldset(ComponentTestBase):
    """Test fieldset component"""

    def test_basic_fieldset(self):
        """Test basic fieldset rendering"""
        html = self.render_component(
            "fieldset",
            slot_content='<input type="text" class="input" />',
        )
        assert "fieldset" in html
        assert "<fieldset" in html

    def test_fieldset_with_legend_attribute(self):
        """Test fieldset with legend attribute"""
        html = self.render_component(
            "fieldset",
            legend="Page title",
            slot_content='<input type="text" class="input" />',
        )
        assert "fieldset-legend" in html
        assert "Page title" in html

    def test_fieldset_without_legend(self):
        """Test fieldset without legend"""
        html = self.render_component(
            "fieldset",
            slot_content='<input type="text" class="input" />',
        )
        assert "fieldset-legend" not in html

    def test_fieldset_custom_class(self):
        """Test fieldset with custom CSS class"""
        html = self.render_component(
            "fieldset",
            slot_content='<input type="text" />',
            **{"class": "bg-base-200 border-base-300 rounded-box border p-4"},
        )
        assert "bg-base-200" in html
        assert "border-base-300" in html

    def test_fieldset_with_label_component(self):
        """Test fieldset used with label component"""
        html = self.render_template_string(
            """
            {% load lb_tags %}
            <c-lb.fieldset legend="Email">
                <input type="email" class="input" placeholder="you@example.com" />
                <c-lb.label>We will never share your email</c-lb.label>
            </c-lb.fieldset>
            """
        )
        assert "fieldset" in html
        assert "fieldset-legend" in html
        assert "label" in html


class TestFieldsetLegend(ComponentTestBase):
    """Test fieldset.legend sub-component"""

    def test_basic_legend(self):
        """Test basic fieldset legend rendering"""
        html = self.render_component("fieldset.legend", slot_content="Title")
        assert "fieldset-legend" in html
        assert "Title" in html

    def test_legend_custom_class(self):
        """Test fieldset legend with custom class"""
        html = self.render_component(
            "fieldset.legend",
            slot_content="Title",
            **{"class": "text-lg"},
        )
        assert "fieldset-legend" in html
        assert "text-lg" in html
