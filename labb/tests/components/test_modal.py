"""
Tests for the modal component.

This module tests the modal component implementation using HTML dialog element,
schema compliance, and all its variants including placement, sizes, and sub-components.
"""

from .test_base import ComponentTestBase, ComponentTestTemplate


class TestModalComponent(ComponentTestTemplate):
    """Test the main modal wrapper component"""

    component_name = "modal"

    def test_modal_default_rendering(self):
        """Test modal component renders with defaults"""
        html = self.render_component("modal", id="test-modal")

        # Should have base modal class and middle placement by default
        self.assert_classes_present(html, {"modal", "modal-middle"})

        # Should be a dialog element
        assert "<dialog" in html
        assert 'id="test-modal"' in html

    def test_modal_id_required(self):
        """Test modal requires an ID"""
        # This should work with ID
        html = self.render_component("modal", id="test-modal")
        assert 'id="test-modal"' in html

        # Test without ID should still work but won't have proper functionality
        html_no_id = self.render_component("modal")
        assert "<dialog" in html_no_id

    def test_modal_placement_variants(self):
        """Test all modal placement variants"""
        placements = {
            "top": "modal-top",
            "middle": "modal-middle",
            "bottom": "modal-bottom",
        }

        for placement, expected_class in placements.items():
            html = self.render_component("modal", id="test-modal", placement=placement)
            self.assert_classes_present(html, {"modal", expected_class})

    def test_modal_horizontal_placement(self):
        """Test modal horizontal placement (start/end)"""
        placements = {
            "start": "modal-start",
            "end": "modal-end",
        }

        for placement, expected_class in placements.items():
            html = self.render_component("modal", id="test-modal", placement=placement)
            self.assert_classes_present(html, {"modal", expected_class})

    def test_modal_open_state(self):
        """Test modal with open state"""
        html = self.render_component("modal", id="test-modal", open="true")

        # Should have modal-open class
        self.assert_classes_present(html, {"modal", "modal-open"})

    def test_modal_combined_states(self):
        """Test modal with combined placement and open states"""
        html = self.render_component(
            "modal",
            id="test-modal",
            placement="bottom",
            open="true",
            class_="custom-modal",
        )

        self.assert_classes_present(
            html, {"modal", "modal-bottom", "modal-open", "custom-modal"}
        )

    def test_modal_custom_attributes(self):
        """Test modal with custom attributes"""
        html = self.render_component(
            "modal",
            id="test-modal",
            **{"data-testid": "modal-dialog", "aria-labelledby": "modal-title"},
        )

        assert 'data-testid="modal-dialog"' in html
        assert 'aria-labelledby="modal-title"' in html

    def test_modal_slot_content(self):
        """Test modal with slot content"""
        slot_content = '<div class="modal-box">Test content</div>'
        html = self.render_component(
            "modal", id="test-modal", slot_content=slot_content
        )

        assert "Test content" in html
        assert "modal-box" in html

    def test_modal_with_backdrop(self):
        """Test modal with backdrop enabled"""
        html = self.render_component("modal", id="test-modal", withBackdrop="true")

        # Should include backdrop element
        assert "modal-backdrop" in html

    def test_modal_with_close_button(self):
        """Test modal with close button enabled"""
        html = self.render_component("modal", id="test-modal", withCloseBtn="true")

        # Should include close button element
        assert "btn-circle" in html
        assert "btn-ghost" in html

    def test_modal_close_button_positions(self):
        """Test modal with different close button positions"""
        positions = ["top-right", "top-left", "bottom-right", "bottom-left"]

        for position in positions:
            html = self.render_component(
                "modal", id="test-modal", withCloseBtn="true", closeBtnPosition=position
            )

            # Should include close button with positioning classes
            if position == "top-right":
                self.assert_classes_present(html, {"right-2", "top-2"})
            elif position == "top-left":
                self.assert_classes_present(html, {"left-2", "top-2"})
            elif position == "bottom-right":
                self.assert_classes_present(html, {"right-2", "bottom-2"})
            elif position == "bottom-left":
                self.assert_classes_present(html, {"left-2", "bottom-2"})

    def test_modal_size_variants(self):
        """Test modal with different sizes"""
        sizes = ["xs", "sm", "md", "lg", "xl", "screen"]

        for size in sizes:
            html = self.render_component("modal", id="test-modal", size=size)

            # Should include size classes based on the size
            if size == "xs":
                self.assert_classes_present(html, {"w-72", "max-w-xs"})
            elif size == "sm":
                self.assert_classes_present(html, {"w-80", "max-w-sm"})
            elif size == "md":
                self.assert_classes_present(html, {"w-96", "max-w-md"})
            elif size == "lg":
                self.assert_classes_present(html, {"w-[32rem]", "max-w-lg"})
            elif size == "xl":
                self.assert_classes_present(html, {"w-[36rem]", "max-w-xl"})
            elif size == "screen":
                self.assert_classes_present(html, {"w-11/12", "max-w-5xl"})

    def test_modal_box_class(self):
        """Test modal with boxClass applied to the modal box"""
        html = self.render_component(
            "modal", id="test-modal", boxClass="custom-box-class"
        )

        # Should pass the boxClass to the modal box component
        assert "modal-box" in html
        assert "custom-box-class" in html

    def test_modal_combined_map_features(self):
        """Test modal with multiple map type features combined"""
        html = self.render_component(
            "modal",
            id="test-modal",
            size="lg",
            withBackdrop="true",
            withCloseBtn="true",
            closeBtnPosition="top-left",
        )

        # Should include all the mapped features
        self.assert_classes_present(html, {"w-[32rem]", "max-w-lg"})  # size
        assert "modal-backdrop" in html  # withBackdrop
        assert "btn-circle" in html  # withCloseBtn
        self.assert_classes_present(html, {"left-2", "top-2"})  # closeBtnPosition


class TestModalBoxComponent(ComponentTestTemplate):
    """Test the modal box sub-component"""

    component_name = "modal.box"

    def test_modal_box_default_rendering(self):
        """Test modal box component renders with defaults"""
        html = self.render_component("modal.box")

        # Should have base modal-box class
        self.assert_classes_present(html, {"modal-box"})

        # Should be a div element
        assert "<div" in html

    def test_modal_box_size_variants(self):
        """Test all modal box size variants"""
        sizes = {
            "xs": ["w-72", "max-w-xs"],
            "sm": ["w-80", "max-w-sm"],
            "md": ["w-96", "max-w-md"],
            "lg": ["w-[32rem]", "max-w-lg"],
            "xl": ["w-[36rem]", "max-w-xl"],
            "screen": ["w-11/12", "max-w-5xl"],
        }

        for size, expected_classes in sizes.items():
            html = self.render_component("modal.box", size=size)
            self.assert_classes_present(html, {"modal-box"} | set(expected_classes))

    def test_modal_box_custom_class(self):
        """Test modal box with custom classes"""
        html = self.render_component("modal.box", class_="custom-box")

        self.assert_classes_present(html, {"modal-box", "custom-box"})

    def test_modal_box_slot_content(self):
        """Test modal box with slot content"""
        slot_content = "<h3>Modal Title</h3><p>Modal content</p>"
        html = self.render_component("modal.box", slot_content=slot_content)

        assert "Modal Title" in html
        assert "Modal content" in html


class TestModalActionComponent(ComponentTestTemplate):
    """Test the modal action sub-component"""

    component_name = "modal.action"

    def test_modal_action_default_rendering(self):
        """Test modal action component renders with defaults"""
        html = self.render_component("modal.action")

        # Should have base modal-action class
        self.assert_classes_present(html, {"modal-action"})

        # Should be a div element
        assert "<div" in html

    def test_modal_action_custom_class(self):
        """Test modal action with custom classes"""
        html = self.render_component("modal.action", class_="custom-actions")

        self.assert_classes_present(html, {"modal-action", "custom-actions"})

    def test_modal_action_slot_content(self):
        """Test modal action with slot content"""
        slot_content = '<button class="btn">Cancel</button><button class="btn btn-primary">Save</button>'
        html = self.render_component("modal.action", slot_content=slot_content)

        assert "Cancel" in html
        assert "Save" in html
        assert "btn" in html


class TestModalBackdropComponent(ComponentTestTemplate):
    """Test the modal backdrop sub-component"""

    component_name = "modal.backdrop"

    def test_modal_backdrop_default_rendering(self):
        """Test modal backdrop component renders with defaults"""
        html = self.render_component("modal.backdrop")

        # Should have base modal-backdrop class
        self.assert_classes_present(html, {"modal-backdrop"})

        # Should be a form element with method dialog
        assert "<form" in html
        assert 'method="dialog"' in html
        assert "<button>" in html

    def test_modal_backdrop_default_button_text(self):
        """Test modal backdrop default button text"""
        html = self.render_component("modal.backdrop")

        # Should have default "close" text
        assert "close" in html

    def test_modal_backdrop_custom_button_text(self):
        """Test modal backdrop with custom button text"""
        html = self.render_component("modal.backdrop", slot_content="dismiss")

        assert "dismiss" in html

    def test_modal_backdrop_custom_class(self):
        """Test modal backdrop with custom classes"""
        html = self.render_component("modal.backdrop", class_="custom-backdrop")

        self.assert_classes_present(html, {"modal-backdrop", "custom-backdrop"})


class TestModalCloseComponent(ComponentTestTemplate):
    """Test the modal close button sub-component"""

    component_name = "modal.close"

    def test_modal_close_default_rendering(self):
        """Test modal close component renders with defaults"""
        html = self.render_component("modal.close")

        # Should have base button classes
        expected_classes = {"btn", "btn-sm", "btn-circle", "btn-ghost", "absolute"}
        self.assert_classes_present(html, expected_classes)

        # Should be wrapped in form with method dialog
        assert "<form" in html
        assert 'method="dialog"' in html
        assert "<button" in html

    def test_modal_close_default_content(self):
        """Test modal close default content"""
        html = self.render_component("modal.close")

        # Should have default close symbol
        assert "✕" in html

    def test_modal_close_custom_content(self):
        """Test modal close with custom content"""
        html = self.render_component("modal.close", slot_content="×")

        assert "×" in html
        # Should not have default ✕ when custom content is provided
        assert "✕" not in html

    def test_modal_close_variants(self):
        """Test all modal close button variants"""
        variants = {
            "neutral": "btn-neutral",
            "primary": "btn-primary",
            "secondary": "btn-secondary",
            "accent": "btn-accent",
            "info": "btn-info",
            "success": "btn-success",
            "warning": "btn-warning",
            "error": "btn-error",
        }

        for variant, expected_class in variants.items():
            html = self.render_component("modal.close", variant=variant)
            expected_classes = {
                "btn",
                "btn-sm",
                "btn-circle",
                "btn-ghost",
                "absolute",
                expected_class,
            }
            self.assert_classes_present(html, expected_classes)

    def test_modal_close_custom_class(self):
        """Test modal close with custom classes"""
        html = self.render_component("modal.close", class_="custom-close")

        expected_classes = {
            "btn",
            "btn-sm",
            "btn-circle",
            "btn-ghost",
            "absolute",
            "custom-close",
        }
        self.assert_classes_present(html, expected_classes)


class TestModalIntegration(ComponentTestBase):
    """Test modal component integration scenarios"""

    def test_modal_complete_structure(self):
        """Test complete modal with all sub-components"""
        template_content = """
        {% load lb_tags %}
        <c-lb.modal id="test-modal" placement="middle">
            <c-lb.modal.box size="md">
                <c-lb.modal.close />
                <h3 class="font-bold text-lg">Modal Title</h3>
                <p class="py-4">Modal content goes here.</p>
                <c-lb.modal.action>
                    <button class="btn">Cancel</button>
                    <button class="btn btn-primary">Save</button>
                </c-lb.modal.action>
            </c-lb.modal.box>
            <c-lb.modal.backdrop />
        </c-lb.modal>
        """

        html = self.render_template_string(template_content)

        # Check main modal structure
        assert "<dialog" in html
        assert 'id="test-modal"' in html
        assert "modal" in html
        assert "modal-middle" in html

        # Check modal box
        assert "modal-box" in html
        assert "w-96" in html  # md size
        assert "max-w-md" in html

        # Check close button
        assert "btn-circle" in html
        assert "✕" in html

        # Check content
        assert "Modal Title" in html
        assert "Modal content goes here." in html

        # Check actions
        assert "modal-action" in html
        assert "Cancel" in html
        assert "Save" in html

        # Check backdrop
        assert "modal-backdrop" in html
        assert 'method="dialog"' in html

    def test_modal_with_backdrop_only(self):
        """Test modal that closes when clicked outside"""
        template_content = """
        {% load lb_tags %}
        <c-lb.modal id="backdrop-modal">
            <c-lb.modal.box>
                <h3>Hello!</h3>
                <p>Press ESC key or click outside to close</p>
            </c-lb.modal.box>
            <c-lb.modal.backdrop />
        </c-lb.modal>
        """

        html = self.render_template_string(template_content)

        assert "Hello!" in html
        assert "click outside to close" in html
        assert "modal-backdrop" in html
        assert 'method="dialog"' in html

    def test_modal_with_close_button_only(self):
        """Test modal with corner close button"""
        template_content = """
        {% load lb_tags %}
        <c-lb.modal id="close-modal">
            <c-lb.modal.box>
                <c-lb.modal.close />
                <h3>Hello!</h3>
                <p>Press ESC key or click on ✕ button to close</p>
            </c-lb.modal.box>
        </c-lb.modal>
        """

        html = self.render_template_string(template_content)

        assert "Hello!" in html
        assert "✕ button to close" in html
        assert "btn-circle" in html
        assert "absolute" in html
        assert "right-2" in html
        assert "top-2" in html

    def test_modal_responsive_placement(self):
        """Test modal with responsive placement"""
        template_content = """
        {% load lb_tags %}
        <c-lb.modal id="responsive-modal" placement="bottom" class="sm:modal-middle">
            <c-lb.modal.box>
                <h3>Responsive Modal</h3>
                <p>Bottom on mobile, middle on desktop</p>
                <c-lb.modal.action>
                    <button class="btn">Close</button>
                </c-lb.modal.action>
            </c-lb.modal.box>
        </c-lb.modal>
        """

        html = self.render_template_string(template_content)

        assert "modal-bottom" in html
        assert "sm:modal-middle" in html
        assert "Responsive Modal" in html

    def test_modal_custom_width(self):
        """Test modal with custom width"""
        template_content = """
        {% load lb_tags %}
        <c-lb.modal id="wide-modal">
            <c-lb.modal.box size="screen">
                <h3>Wide Modal</h3>
                <p>This modal takes up most of the screen width</p>
                <c-lb.modal.action>
                    <button class="btn">Close</button>
                </c-lb.modal.action>
            </c-lb.modal.box>
        </c-lb.modal>
        """

        html = self.render_template_string(template_content)

        assert "w-11/12" in html
        assert "max-w-5xl" in html
        assert "Wide Modal" in html
