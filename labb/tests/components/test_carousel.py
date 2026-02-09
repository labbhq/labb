"""
Tests for the carousel component and its sub-components.

This module tests the carousel component implementation, schema compliance,
and rendering behavior including all variants and states.
"""

from .test_base import ComponentTestBase, ComponentTestTemplate


class TestCarouselComponent(ComponentTestTemplate):
    """Test the main carousel wrapper component"""

    component_name = "carousel"

    def test_carousel_default_rendering(self):
        """Test carousel component renders with default attributes"""
        html = self.render_component("carousel")

        # Should have base carousel class
        self.assert_classes_present(html, {"carousel"})

        # Should have default snap position (start)
        self.assert_classes_present(html, {"carousel-start"})

        # Should not have vertical direction class by default
        assert "carousel-vertical" not in html

    def test_carousel_snap_positions(self):
        """Test all carousel snap position variants"""
        snaps = {
            "start": "carousel-start",
            "center": "carousel-center",
            "end": "carousel-end",
        }

        for snap, expected_class in snaps.items():
            html = self.render_component("carousel", snap=snap)
            self.assert_classes_present(html, {"carousel", expected_class})

    def test_carousel_direction_horizontal(self):
        """Test horizontal direction (default, no extra class)"""
        html = self.render_component("carousel", direction="horizontal")
        self.assert_classes_present(html, {"carousel"})
        assert "carousel-vertical" not in html

    def test_carousel_direction_vertical(self):
        """Test vertical direction variant"""
        html = self.render_component("carousel", direction="vertical")
        self.assert_classes_present(html, {"carousel", "carousel-vertical"})

    def test_carousel_custom_class(self):
        """Test custom CSS class addition"""
        html = self.render_component("carousel", class_="custom-carousel")
        self.assert_classes_present(html, {"carousel", "custom-carousel"})

    def test_carousel_combined_attributes(self):
        """Test combination of multiple attributes"""
        html = self.render_component(
            "carousel",
            snap="center",
            direction="vertical",
            class_="w-full",
        )
        self.assert_classes_present(
            html, {"carousel", "carousel-center", "carousel-vertical", "w-full"}
        )

    def test_carousel_attributes_passthrough(self):
        """Test that HTML attributes are passed through correctly"""
        html = self.render_component(
            "carousel", id="main-carousel", **{"data-carousel": "main"}
        )

        self.assert_attributes_present(
            html, {"id": "main-carousel", "data-carousel": "main"}
        )

    def test_carousel_with_slot_content(self):
        """Test carousel with slot content"""
        slot_content = '<div class="carousel-item">Item 1</div>'
        html = self.render_component(
            "carousel",
            slot_content=slot_content,
        )

        assert slot_content in html
        assert "Item 1" in html


class TestCarouselItemComponent(ComponentTestTemplate):
    """Test the carousel item component"""

    component_name = "carousel.item"

    def test_carousel_item_default_rendering(self):
        """Test carousel item component renders with defaults"""
        html = self.render_component("carousel.item")

        # Should have carousel-item class
        self.assert_classes_present(html, {"carousel-item"})

    def test_carousel_item_with_id(self):
        """Test carousel item with ID for anchor navigation"""
        html = self.render_component("carousel.item", id="item1")

        self.assert_classes_present(html, {"carousel-item"})
        assert 'id="item1"' in html

    def test_carousel_item_without_id(self):
        """Test carousel item without ID"""
        html = self.render_component("carousel.item")

        self.assert_classes_present(html, {"carousel-item"})
        # Should not have id attribute
        assert 'id=""' not in html

    def test_carousel_item_custom_class(self):
        """Test custom class addition"""
        html = self.render_component(
            "carousel.item",
            class_="w-full",
        )

        self.assert_classes_present(html, {"carousel-item", "w-full"})

    def test_carousel_item_with_content(self):
        """Test carousel item with slot content"""
        slot_content = '<img src="/image.jpg" alt="Test" />'
        html = self.render_component(
            "carousel.item",
            slot_content=slot_content,
        )

        assert slot_content in html
        assert "Test" in html

    def test_carousel_item_attributes_passthrough(self):
        """Test that HTML attributes are passed through correctly"""
        html = self.render_component(
            "carousel.item", **{"data-index": "1", "aria-label": "First item"}
        )

        self.assert_attributes_present(
            html, {"data-index": "1", "aria-label": "First item"}
        )


class TestCarouselComponentIntegration(ComponentTestBase):
    """Integration tests for carousel component system"""

    def test_complete_carousel_structure(self):
        """Test a complete carousel structure with multiple items"""
        template_str = """
{% load lb_tags %}
<c-lb.carousel snap="center" class="w-full">
    <c-lb.carousel.item id="item1" class="w-full">
        <img src="/img1.jpg" alt="Image 1" class="w-full" />
    </c-lb.carousel.item>
    <c-lb.carousel.item id="item2" class="w-full">
        <img src="/img2.jpg" alt="Image 2" class="w-full" />
    </c-lb.carousel.item>
    <c-lb.carousel.item id="item3" class="w-full">
        <img src="/img3.jpg" alt="Image 3" class="w-full" />
    </c-lb.carousel.item>
</c-lb.carousel>
        """

        html = self.render_template_string(template_str)

        # Should have all expected classes and structure
        self.assert_classes_present(
            html, {"carousel", "carousel-center", "carousel-item", "w-full"}
        )

        # Should have all item IDs
        assert 'id="item1"' in html
        assert 'id="item2"' in html
        assert 'id="item3"' in html

        # Should have all images
        assert "Image 1" in html
        assert "Image 2" in html
        assert "Image 3" in html

    def test_vertical_carousel_with_items(self):
        """Test a vertical carousel with items"""
        template_str = """
{% load lb_tags %}
<c-lb.carousel direction="vertical" snap="start" class="h-96">
    <c-lb.carousel.item id="slide1">
        <div class="h-full w-full bg-primary">Slide 1</div>
    </c-lb.carousel.item>
    <c-lb.carousel.item id="slide2">
        <div class="h-full w-full bg-secondary">Slide 2</div>
    </c-lb.carousel.item>
    <c-lb.carousel.item id="slide3">
        <div class="h-full w-full bg-accent">Slide 3</div>
    </c-lb.carousel.item>
</c-lb.carousel>
        """

        html = self.render_template_string(template_str)

        # Should have all expected classes
        self.assert_classes_present(
            html, {"carousel", "carousel-vertical", "carousel-start", "carousel-item"}
        )

        # Should have all slide content
        assert "Slide 1" in html
        assert "Slide 2" in html
        assert "Slide 3" in html

    def test_carousel_with_half_width_items(self):
        """Test carousel with half-width items for multiple visible"""
        template_str = """
{% load lb_tags %}
<c-lb.carousel snap="start" class="w-full">
    <c-lb.carousel.item class="w-1/2">
        <div class="bg-neutral text-neutral-content p-4">Item 1</div>
    </c-lb.carousel.item>
    <c-lb.carousel.item class="w-1/2">
        <div class="bg-primary text-primary-content p-4">Item 2</div>
    </c-lb.carousel.item>
    <c-lb.carousel.item class="w-1/2">
        <div class="bg-secondary text-secondary-content p-4">Item 3</div>
    </c-lb.carousel.item>
</c-lb.carousel>
        """

        html = self.render_template_string(template_str)

        # Should have carousel and items
        self.assert_classes_present(
            html, {"carousel", "carousel-start", "carousel-item", "w-1/2"}
        )

        # Should have all item content
        assert "Item 1" in html
        assert "Item 2" in html
        assert "Item 3" in html


class TestCarouselSchemaCompliance(ComponentTestBase):
    """Test carousel components against their schema definitions"""

    def test_carousel_schema_variables(self):
        """Test carousel schema has all expected variables"""
        schema = self.get_component_schema("carousel")

        expected_variables = {"class", "snap", "direction"}

        assert "variables" in schema
        for var_name in expected_variables:
            assert var_name in schema["variables"], (
                f"Variable '{var_name}' missing from carousel schema"
            )

    def test_carousel_item_schema_variables(self):
        """Test carousel.item schema has all expected variables"""
        schema = self.get_component_schema("carousel.item")

        expected_variables = {"class", "id"}

        assert "variables" in schema
        for var_name in expected_variables:
            assert var_name in schema["variables"], (
                f"Variable '{var_name}' missing from carousel.item schema"
            )

    def test_carousel_snap_css_mappings(self):
        """Test that schema snap mappings match component behavior"""
        schema = self.get_component_schema("carousel")

        # Test snap mappings
        if "variables" in schema and "snap" in schema["variables"]:
            snap_var = schema["variables"]["snap"]
            if "css_mapping" in snap_var:
                for snap, css_class in snap_var["css_mapping"].items():
                    html = self.render_component("carousel", snap=snap)
                    self.assert_classes_present(html, {"carousel", css_class})

    def test_carousel_direction_css_mappings(self):
        """Test that schema direction mappings match component behavior"""
        schema = self.get_component_schema("carousel")

        # Test direction mappings
        if "variables" in schema and "direction" in schema["variables"]:
            direction_var = schema["variables"]["direction"]
            if "css_mapping" in direction_var:
                for direction, css_class in direction_var["css_mapping"].items():
                    html = self.render_component("carousel", direction=direction)
                    self.assert_classes_present(html, {"carousel"})
                    if css_class:  # Only check if class is not empty string
                        self.assert_classes_present(html, {css_class})

    def test_carousel_default_snap(self):
        """Test carousel default snap from schema"""
        schema = self.get_component_schema("carousel")

        if "variables" in schema and "snap" in schema["variables"]:
            snap_var = schema["variables"]["snap"]
            default_snap = snap_var.get("default", "start")

            html = self.render_component("carousel")
            # Should have default snap class
            expected_class = snap_var.get("css_mapping", {}).get(default_snap, "")
            if expected_class:
                self.assert_classes_present(html, {"carousel", expected_class})

    def test_carousel_default_direction(self):
        """Test carousel default direction from schema"""
        schema = self.get_component_schema("carousel")

        if "variables" in schema and "direction" in schema["variables"]:
            direction_var = schema["variables"]["direction"]
            default_direction = direction_var.get("default", "horizontal")

            html = self.render_component("carousel")
            # Horizontal should not add extra class
            if default_direction == "horizontal":
                assert "carousel-vertical" not in html
