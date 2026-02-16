from .test_base import ComponentTestBase, ComponentTestTemplate


class TestHover3D(ComponentTestTemplate):
    """Test suite for the hover3d component using the standard template checks"""

    component_name = "hover3d"


class TestHover3DRendering(ComponentTestBase):
    """Detailed rendering tests for the hover3d component"""

    # ---------------------------------------------------------------------------
    # Basic rendering
    # ---------------------------------------------------------------------------

    def test_basic_rendering(self):
        """Test that hover3d renders with the base class"""
        html = self.render_component("hover3d", slot_content="<p>content</p>")
        assert "hover-3d" in html

    def test_base_class_present(self):
        """Test that the hover-3d base class is applied"""
        html = self.render_component("hover3d", slot_content="<p>content</p>")
        self.assert_classes_present(html, {"hover-3d"})

    # ---------------------------------------------------------------------------
    # 8 hover-zone divs
    # ---------------------------------------------------------------------------

    def test_eight_empty_divs_rendered(self):
        """Test that exactly 8 empty hover-zone divs are present after the slot content"""
        html = self.render_component("hover3d", slot_content="<p>content</p>")
        # Count consecutive empty divs: <div></div> with no content between tags
        # The rendered output should contain at least 8 empty divs
        import re

        empty_divs = re.findall(r"<div\s*></div>", html)
        assert len(empty_divs) == 8, (
            f"Expected 8 empty hover-zone divs, found {len(empty_divs)}. HTML: {html}"
        )

    def test_hover_zones_present_without_slot_content(self):
        """Test that the 8 hover-zone divs render even when slot content is empty"""
        html = self.render_component("hover3d")
        import re

        empty_divs = re.findall(r"<div\s*></div>", html)
        assert len(empty_divs) == 8, (
            f"Expected 8 empty hover-zone divs with no slot content, found {len(empty_divs)}"
        )

    # ---------------------------------------------------------------------------
    # Slot content passthrough
    # ---------------------------------------------------------------------------

    def test_slot_content_rendered(self):
        """Test that arbitrary slot content is rendered inside the wrapper"""
        html = self.render_component(
            "hover3d", slot_content='<figure><img src="/img.jpg" alt="test" /></figure>'
        )
        assert '<img src="/img.jpg"' in html
        assert 'alt="test"' in html

    def test_slot_content_with_text(self):
        """Test that plain text slot content appears in the output"""
        html = self.render_component("hover3d", slot_content="<p>Hello 3D</p>")
        assert "Hello 3D" in html

    # ---------------------------------------------------------------------------
    # Custom classes
    # ---------------------------------------------------------------------------

    def test_custom_class_applied(self):
        """Test that a custom class passed via the class attribute is rendered"""
        html = self.render_component(
            "hover3d", slot_content="<p>x</p>", **{"class": "my-custom-class"}
        )
        assert "my-custom-class" in html

    def test_multiple_custom_classes(self):
        """Test that multiple custom classes are all present"""
        html = self.render_component(
            "hover3d",
            slot_content="<p>x</p>",
            **{"class": "w-96 shadow-lg rounded-xl"},
        )
        self.assert_classes_present(html, {"w-96", "shadow-lg", "rounded-xl"})

    def test_custom_class_does_not_remove_base_class(self):
        """Test that adding a custom class does not displace the hover-3d base class"""
        html = self.render_component(
            "hover3d", slot_content="<p>x</p>", **{"class": "extra"}
        )
        self.assert_classes_present(html, {"hover-3d", "extra"})

    # ---------------------------------------------------------------------------
    # HTML attribute passthrough
    # ---------------------------------------------------------------------------

    def test_data_attribute_passthrough(self):
        """Test that arbitrary data-* attributes are passed through to the wrapper"""
        html = self.render_component(
            "hover3d", slot_content="<p>x</p>", **{"data-testid": "hover-box"}
        )
        assert 'data-testid="hover-box"' in html

    def test_id_attribute_passthrough(self):
        """Test that an id attribute is passed through to the wrapper"""
        html = self.render_component("hover3d", slot_content="<p>x</p>", id="my-hover")
        assert 'id="my-hover"' in html

    # ---------------------------------------------------------------------------
    # Structure integrity
    # ---------------------------------------------------------------------------

    def test_wrapper_is_single_root_div(self):
        """Test that the component renders a single root div with hover-3d class"""
        html = self.render_component("hover3d", slot_content="<p>x</p>")
        # The outermost element should be a div with hover-3d
        stripped = html.strip()
        assert stripped.startswith("<div") and "hover-3d" in stripped.split(">")[0]

    def test_content_appears_before_hover_zones(self):
        """Test that slot content is placed before the 8 empty hover-zone divs"""
        html = self.render_component("hover3d", slot_content="<p>MARKER</p>")
        marker_pos = html.index("MARKER")
        # Find the first empty div after the marker
        import re

        first_empty_div_match = re.search(r"<div\s*></div>", html[marker_pos:])
        assert first_empty_div_match is not None, (
            "No empty hover-zone divs found after slot content"
        )
        # Confirm the marker comes first
        assert marker_pos < (marker_pos + first_empty_div_match.start())
