from .test_base import ComponentTestBase


class TestSwap(ComponentTestBase):
    """Test the swap component"""

    def test_basic_swap(self):
        """Test basic swap rendering"""
        html = self.render_component("swap")
        assert "swap" in html
        assert 'type="checkbox"' in html

    def test_swap_with_effects(self):
        """Test swap with different effects"""
        effects = ["rotate", "flip"]
        for effect in effects:
            html = self.render_component("swap", effect=effect)
            assert f"swap-{effect}" in html

    def test_swap_checked(self):
        """Test swap in checked state"""
        html = self.render_component("swap", checked="true")
        assert "checked" in html

    def test_swap_disabled(self):
        """Test swap in disabled state"""
        html = self.render_component("swap", disabled="true")
        assert "disabled" in html

    def test_swap_with_name_and_value(self):
        """Test swap with name and value attributes"""
        html = self.render_component("swap", name="test-swap", value="test-value")
        assert 'name="test-swap"' in html
        assert 'value="test-value"' in html

    def test_swap_with_custom_class(self):
        """Test swap with custom CSS class"""
        html = self.render_component("swap", **{"class": "custom-class"})
        assert "custom-class" in html

    def test_swap_with_input_class(self):
        """Test swap with custom input CSS class"""
        html = self.render_component("swap", inputClass="theme-controller")
        assert 'class="theme-controller"' in html

    def test_swap_on_subcomponent(self):
        """Test swap.on sub-component"""
        html = self.render_component("swap.on", **{"class": "test-on"})
        assert "swap-on" in html
        assert "test-on" in html

    def test_swap_off_subcomponent(self):
        """Test swap.off sub-component"""
        html = self.render_component("swap.off", **{"class": "test-off"})
        assert "swap-off" in html
        assert "test-off" in html

    def test_swap_indeterminate_subcomponent(self):
        """Test swap.indeterminate sub-component"""
        html = self.render_component(
            "swap.indeterminate", **{"class": "test-indeterminate"}
        )
        assert "swap-indeterminate" in html
        assert "test-indeterminate" in html

    def test_swap_base_classes(self):
        """Test that swap has correct base classes"""
        html = self.render_component("swap")
        self.assert_classes_present(html, {"swap"})

    def test_swap_subcomponent_base_classes(self):
        """Test that swap sub-components have correct base classes"""
        # Test swap.on
        html = self.render_component("swap.on")
        self.assert_classes_present(html, {"swap-on"})

        # Test swap.off
        html = self.render_component("swap.off")
        self.assert_classes_present(html, {"swap-off"})

        # Test swap.indeterminate
        html = self.render_component("swap.indeterminate")
        self.assert_classes_present(html, {"swap-indeterminate"})
