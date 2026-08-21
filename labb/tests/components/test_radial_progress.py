from labb.tests.components.test_base import ComponentTestBase


class TestRadialProgress(ComponentTestBase):
    """Test radial-progress component"""

    def test_basic_radial_progress(self):
        """Test basic radial progress rendering"""
        html = self.render_component("radial-progress", value="70", slot_content="70%")
        assert "radial-progress" in html
        assert "70%" in html

    def test_radial_progress_value(self):
        """Test radial progress with value CSS variable"""
        html = self.render_component("radial-progress", value="45", slot_content="45%")
        assert "--value:45" in html

    def test_radial_progress_accessibility(self):
        """Test radial progress has proper ARIA attributes"""
        html = self.render_component("radial-progress", value="60", slot_content="60%")
        assert 'role="progressbar"' in html
        assert 'aria-valuenow="60"' in html

    def test_radial_progress_custom_size(self):
        """Test radial progress with custom size"""
        html = self.render_component(
            "radial-progress",
            value="50",
            progressSize="8rem",
            slot_content="50%",
        )
        assert "--size:8rem" in html

    def test_radial_progress_custom_thickness(self):
        """Test radial progress with custom thickness"""
        html = self.render_component(
            "radial-progress",
            value="50",
            thickness="4px",
            slot_content="50%",
        )
        assert "--thickness:4px" in html

    def test_radial_progress_all_custom(self):
        """Test radial progress with all custom values"""
        html = self.render_component(
            "radial-progress",
            value="75",
            progressSize="10rem",
            thickness="2px",
            slot_content="75%",
        )
        assert "--value:75" in html
        assert "--size:10rem" in html
        assert "--thickness:2px" in html

    def test_radial_progress_variants(self):
        """Test radial progress color variants"""
        variants = [
            "neutral",
            "primary",
            "secondary",
            "accent",
            "info",
            "success",
            "warning",
            "error",
        ]
        for variant in variants:
            html = self.render_component(
                "radial-progress", value="50", variant=variant, slot_content="50%"
            )
            assert f"text-{variant}" in html

    def test_radial_progress_bg_variants(self):
        """Test radial progress background color variants"""
        variants = [
            "neutral",
            "primary",
            "secondary",
            "accent",
            "info",
            "success",
            "warning",
            "error",
        ]
        for variant in variants:
            html = self.render_component(
                "radial-progress", value="50", bgVariant=variant, slot_content="50%"
            )
            assert f"bg-{variant}" in html
            assert f"text-{variant}-content" in html
            assert f"border-{variant}" in html

    def test_radial_progress_custom_class(self):
        """Test radial progress with custom CSS class"""
        html = self.render_component(
            "radial-progress",
            value="50",
            slot_content="50%",
            **{"class": "text-primary"},
        )
        assert "text-primary" in html

    def test_radial_progress_default_value(self):
        """Test radial progress with default value of 0"""
        html = self.render_component("radial-progress")
        assert "--value:0" in html


class TestRadialProgressReactive(ComponentTestBase):
    """A signal-bound value drives --value and aria-valuenow together."""

    def test_signal_value_renders_fallback(self):
        html = self.render_component("radial-progress", value="$upload.pct:35")
        assert "--value:35" in html
        assert 'aria-valuenow="35"' in html

    def test_signal_value_tracks_the_signal(self):
        html = self.render_component("radial-progress", value="$upload.pct:35")
        assert "--value:${$upload.pct};" in html
        assert 'data-attr:aria-valuenow="$upload.pct"' in html

    def test_static_value_stays_inert(self):
        html = self.render_component("radial-progress", value="35")
        assert "data-attr:style" not in html
        assert "data-attr:aria-valuenow" not in html

    def test_variant_is_reactive(self):
        html = self.render_component("radial-progress", variant="$ui.tone:primary")
        assert "text-primary" in html
        assert "data-attr:class" in html
