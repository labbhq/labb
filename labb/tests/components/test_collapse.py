from labb.tests.components.test_base import ComponentTestTemplate


class TestCollapse(ComponentTestTemplate):
    """Test suite for the collapse component"""

    component_name = "collapse"

    # --- Basic rendering ---

    def test_collapse_renders_with_base_class(self):
        """Test that collapse renders with the collapse base class"""
        html = self.render_component("collapse", title="Test Title")
        self.assert_classes_present(html, {"collapse"})

    def test_collapse_renders_checkbox_input(self):
        """Test that collapse renders a checkbox input for toggle behavior"""
        html = self.render_component("collapse", title="Test Title")
        assert 'type="checkbox"' in html

    def test_collapse_renders_title_from_attribute(self):
        """Test that the title attribute renders inside collapse-title"""
        html = self.render_component("collapse", title="My Section")
        assert "My Section" in html
        assert "collapse-title" in html

    def test_collapse_renders_content_area(self):
        """Test that the collapse-content div is present"""
        html = self.render_component("collapse", title="Test Title")
        assert "collapse-content" in html

    def test_collapse_renders_slot_content(self):
        """Test that default slot content renders inside collapse-content"""
        html = self.render_component(
            "collapse", title="Test Title", slot_content="<p>Body text here</p>"
        )
        assert "Body text here" in html

    # --- Style variants ---

    def test_collapse_default_style_has_no_icon_class(self):
        """Test that default style (empty) does not add arrow or plus classes"""
        html = self.render_component("collapse", title="Test Title")
        assert "collapse-arrow" not in html
        assert "collapse-plus" not in html

    def test_collapse_arrow_style(self):
        """Test that style=arrow adds collapse-arrow class"""
        html = self.render_component("collapse", title="Test Title", style="arrow")
        self.assert_classes_present(html, {"collapse", "collapse-arrow"})

    def test_collapse_plus_style(self):
        """Test that style=plus adds collapse-plus class"""
        html = self.render_component("collapse", title="Test Title", style="plus")
        self.assert_classes_present(html, {"collapse", "collapse-plus"})

    # --- Open state ---

    def test_collapse_closed_by_default(self):
        """Test that collapse does not have collapse-open or checked when open is not set"""
        html = self.render_component("collapse", title="Test Title")
        assert "collapse-open" not in html
        # The checkbox should not be checked
        assert "checked" not in html

    def test_collapse_open_adds_class_and_checked(self):
        """Test that open=true adds collapse-open class and checked attribute to input"""
        html = self.render_component("collapse", title="Test Title", open="true")
        assert "collapse-open" in html
        assert "checked" in html

    # --- Custom classes ---

    def test_collapse_custom_class(self):
        """Test that custom classes are applied to the outer div"""
        html = self.render_component(
            "collapse", title="Test Title", **{"class": "bg-base-100 border"}
        )
        assert "bg-base-100" in html
        assert "border" in html

    # --- Named title slot ---

    def test_collapse_title_slot_renders_custom_title(self):
        """Test that titleSlot renders when title attribute is not provided"""
        html = self.render_component(
            "collapse",
            slot_content='<c-slot name="titleSlot"><div class="collapse-title font-semibold">Custom Title</div></c-slot><p>Content</p>',
        )
        assert "Custom Title" in html
        assert "Content" in html

    def test_collapse_title_attribute_takes_priority_over_slot(self):
        """Test that title attribute is rendered when both title and titleSlot are provided"""
        html = self.render_component(
            "collapse",
            title="Attribute Title",
            slot_content='<c-slot name="titleSlot"><div class="collapse-title">Slot Title</div></c-slot><p>Content</p>',
        )
        assert "Attribute Title" in html
        # The slot title should not appear because title attribute takes priority
        assert "Slot Title" not in html

    # --- Combined features ---

    def test_collapse_all_features_combined(self):
        """Test collapse with style, open, custom class, and title all set"""
        html = self.render_component(
            "collapse",
            title="Full Featured",
            style="plus",
            open="true",
            **{"class": "my-custom-class"},
        )
        assert "collapse" in html
        assert "collapse-plus" in html
        assert "collapse-open" in html
        assert "checked" in html
        assert "my-custom-class" in html
        assert "Full Featured" in html
        assert "collapse-title" in html
        assert "collapse-content" in html
