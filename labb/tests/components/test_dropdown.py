from .test_base import ComponentTestBase


class TestDropdown(ComponentTestBase):
    """Test the dropdown component"""

    def test_basic_dropdown(self):
        """Test basic dropdown rendering"""
        html = self.render_component("dropdown")
        assert "dropdown" in html

    def test_dropdown_with_placement(self):
        """Test dropdown with different placements"""
        placements = ["top", "left", "right"]
        for placement in placements:
            html = self.render_component("dropdown", placement=placement)
            assert f"dropdown-{placement}" in html

    def test_dropdown_with_alignment(self):
        """Test dropdown with different alignments"""
        alignments = ["start", "center", "end"]
        for alignment in alignments:
            html = self.render_component("dropdown", alignment=alignment)
            assert f"dropdown-{alignment}" in html

    def test_dropdown_hover(self):
        """Test dropdown with hover activation"""
        html = self.render_component("dropdown", hover="true")
        assert "dropdown-hover" in html

    def test_dropdown_open(self):
        """Test dropdown with forced open state"""
        html = self.render_component("dropdown", open="true")
        assert "dropdown-open" in html

    def test_dropdown_with_custom_class(self):
        """Test dropdown with custom CSS class"""
        html = self.render_component("dropdown", **{"class": "custom-class"})
        assert "custom-class" in html

    def test_dropdown_trigger(self):
        """Test dropdown.trigger sub-component"""
        html = self.render_component("dropdown.trigger", **{"class": "test-trigger"})
        assert 'tabindex="0"' in html
        assert 'role="button"' in html
        assert "test-trigger" in html

    def test_dropdown_trigger_with_different_elements(self):
        """Test dropdown.trigger with different HTML elements"""
        elements = ["button", "label"]
        for element in elements:
            html = self.render_component("dropdown.trigger", **{"as": element})
            assert html.strip().startswith(f"<{element}")
            assert html.strip().endswith(f"</{element}>")

    def test_dropdown_content(self):
        """Test dropdown.content sub-component"""
        html = self.render_component("dropdown.content", **{"class": "test-content"})
        assert "dropdown-content" in html
        assert 'tabindex="0"' in html
        assert "test-content" in html

    def test_dropdown_content_renders_div(self):
        """Test dropdown.content renders as div element"""
        html = self.render_component("dropdown.content")
        assert html.strip().startswith("<div")
        assert html.strip().endswith("</div>")

    def test_dropdown_base_classes(self):
        """Test that dropdown has correct base classes"""
        html = self.render_component("dropdown")
        self.assert_classes_present(html, {"dropdown"})

    def test_dropdown_subcomponent_base_classes(self):
        """Test that dropdown sub-components have correct base classes"""
        # Test dropdown.content
        html = self.render_component("dropdown.content")
        self.assert_classes_present(html, {"dropdown-content"})

    def test_dropdown_combined_states(self):
        """Test dropdown with multiple states combined"""
        html = self.render_component(
            "dropdown",
            placement="top",
            alignment="end",
            hover="true",
            **{"class": "test-class"},
        )
        assert "dropdown-top" in html
        assert "dropdown-end" in html
        assert "dropdown-hover" in html
        assert "test-class" in html

    def test_dropdown_accessibility(self):
        """Test dropdown accessibility features"""
        # Test trigger accessibility
        html = self.render_component("dropdown.trigger")
        assert 'tabindex="0"' in html
        assert 'role="button"' in html

        # Test content accessibility
        html = self.render_component("dropdown.content")
        assert 'tabindex="0"' in html
