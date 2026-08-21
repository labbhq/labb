from labb.tests.components.test_base import ComponentTestBase


class TestCountdown(ComponentTestBase):
    """Test countdown component"""

    def test_basic(self):
        html = self.render_component("countdown", value="59")
        assert "countdown" in html
        assert "--value:59" in html

    def test_default_value_zero(self):
        html = self.render_component("countdown")
        assert "--value:0" in html

    def test_aria_label_defaults_to_value(self):
        html = self.render_component("countdown", value="42")
        assert 'aria-label="42"' in html

    def test_custom_aria_label(self):
        html = self.render_component("countdown", value="42", ariaLabel="42 seconds")
        assert 'aria-label="42 seconds"' in html

    def test_digits(self):
        html = self.render_component("countdown", value="5", digits="3")
        assert "--digits:3" in html

    def test_no_digits_by_default(self):
        html = self.render_component("countdown", value="5")
        assert "--digits" not in html

    def test_custom_class(self):
        html = self.render_component("countdown", value="1", **{"class": "text-4xl"})
        assert "text-4xl" in html


class TestCountdownReactive(ComponentTestBase):
    """A signal-bound value drives --value, so the digits actually roll."""

    def test_signal_value_renders_fallback_server_side(self):
        html = self.render_component("countdown", value="$seconds:30")
        assert "--value:30" in html
        assert ">30<" in html

    def test_signal_value_tracks_the_signal(self):
        html = self.render_component("countdown", value="$seconds:30")
        assert "data-attr:style=" in html
        assert "--value:${$seconds};" in html
        assert 'data-text="$seconds"' in html

    def test_static_value_stays_inert(self):
        html = self.render_component("countdown", value="30")
        assert "data-attr:style" not in html
        assert "data-text" not in html

    def test_nested_signal_path(self):
        html = self.render_component("countdown", value="$timer.left:5")
        assert "--value:5" in html
        assert "--value:${$timer.left};" in html
