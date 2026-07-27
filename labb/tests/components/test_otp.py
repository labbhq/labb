from labb.tests.components.test_base import ComponentTestBase


class TestOtp(ComponentTestBase):
    """Test otp (one-time-passcode) component"""

    def test_basic(self):
        html = self.render_component("otp")
        assert "otp" in html
        assert "<input" in html

    def test_default_four_cells(self):
        html = self.render_component("otp")
        assert html.count("<span></span>") == 4
        assert 'maxlength="4"' in html

    def test_length(self):
        html = self.render_component("otp", length="6")
        assert html.count("<span></span>") == 6
        assert 'maxlength="6"' in html

    def test_sizes(self):
        for size in ["xs", "sm", "md", "lg", "xl"]:
            html = self.render_component("otp", size=size)
            assert f"otp-{size}" in html

    def test_variants(self):
        for variant in [
            "neutral",
            "primary",
            "secondary",
            "accent",
            "info",
            "success",
            "warning",
            "error",
        ]:
            html = self.render_component("otp", variant=variant)
            assert f"otp-{variant}" in html

    def test_joined(self):
        html = self.render_component("otp", joined=True)
        assert "otp-joined" in html

    def test_not_joined_by_default(self):
        html = self.render_component("otp")
        assert "otp-joined" not in html

    def test_custom_name(self):
        html = self.render_component("otp", name="code")
        assert 'name="code"' in html
