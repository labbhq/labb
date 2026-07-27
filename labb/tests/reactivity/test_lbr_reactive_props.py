"""Tests for the reactive-prop parser and its safe fallback.

`$signal.path:fallback` props drive client-side reactive classes via a
`data-attr:class="lb.classes(...)"` expression. The signal path is interpolated
raw into that JS, so a value whose path carries characters outside ``[\\w.]`` must
be treated as static rather than reactive — otherwise a malformed prop could inject
arbitrary JS into the emitted expression.
"""

from labb.templatetags.lbr_tags import (
    _parse_reactive,
    lbr_chart_signal,
)
from labb.tests.components.test_base import ComponentTestBase


class TestParseReactive:

    def test_reactive_with_fallback(self):
        assert _parse_reactive("$badge.variant:neutral") == (True, "badge.variant", "neutral")

    def test_reactive_without_fallback(self):
        assert _parse_reactive("$open") == (True, "open", "")

    def test_static_value(self):
        assert _parse_reactive("primary") == (False, None, "primary")

    def test_empty_value(self):
        assert _parse_reactive("") == (False, None, "")

    def test_none_value(self):
        assert _parse_reactive(None) == (False, None, "")

    def test_malformed_path_is_treated_as_static(self):
        # A quote/paren in the path would break out of the JS expression — must not
        # be reported as reactive.
        val = "$x';alert(1)//"
        is_rx, path, _ = _parse_reactive(val)
        assert is_rx is False
        assert path is None

    def test_empty_signal_path_is_static(self):
        # "$:foo" has no path — not reactive.
        assert _parse_reactive("$:foo") == (False, None, "$:foo")

    def test_path_with_spaces_is_static(self):
        is_rx, path, _ = _parse_reactive("$foo bar")
        assert is_rx is False


class TestChartSignal:

    def test_valid_signal_returned(self):
        assert str(lbr_chart_signal("$chartData")) == "$chartData"

    def test_dotted_signal_returned(self):
        assert str(lbr_chart_signal("$charts.sales")) == "$charts.sales"

    def test_static_data_returns_empty(self):
        assert str(lbr_chart_signal('{"labels": []}')) == ""

    def test_malformed_signal_falls_back_to_static(self):
        # Must not echo the injection payload back as a JS signal ref.
        assert str(lbr_chart_signal("$x');evil()//")) == ""


class TestReactivePropRendering(ComponentTestBase):
    """Integration: a malformed reactive prop must not emit raw JS on the element."""

    def _render(self, attrs_str):
        return self.render_template_string(
            f"{{% load lb_tags %}}<c-lb.badge {attrs_str}>x</c-lb.badge>"
        )

    def test_valid_reactive_prop_emits_data_attr_class(self):
        html = self._render('variant="$badge.variant:neutral"')
        assert "data-attr:class" in html
        assert "$badge.variant" in html

    def test_malformed_reactive_prop_does_not_emit_injection(self):
        html = self._render("variant=\"$x');alert(1)//\"")
        assert "alert(1)" not in html
        # Degrades to a plain (non-reactive) badge — no reactive class binding.
        assert "data-attr:class" not in html


class TestPassthroughEscaping(ComponentTestBase):
    """Attr values reach the DOM escaped exactly once.

    Values parsed out of an attrs string arrive already HTML-escaped, so
    re-escaping them turned an authored `&amp;` into a literal "&amp;".
    """

    def test_ampersand_entity_is_not_double_escaped(self):
        html = self.render_component("input", placeholder="Kite &amp; Bell")
        assert 'placeholder="Kite &amp; Bell"' in html
        assert "&amp;amp;" not in html

    def test_raw_ampersand_is_escaped_once(self):
        html = self.render_component("input", placeholder="Kite & Bell")
        assert 'placeholder="Kite &amp; Bell"' in html
        assert "&amp;amp;" not in html

    def test_angle_bracket_is_escaped(self):
        html = self.render_component("input", placeholder="a < b")
        assert "&lt;" in html
        assert "placeholder=\"a < b\"" not in html
