"""
Rendered-HTML tests for opt-in Datastar loading (ticket 0007).

Static labb pages ship zero JS: ``<c-lb.m.dependencies>`` loads no runtime by
default. A truthy ``datastar`` prop force-loads it, and every reactive surface
(signals, ``c-lbr.*`` actions, reactive ``$``-props, reactive charts)
self-declares its own runtime through the push/load stack.

Assertions check external behaviour only — which ``<script>`` tags reach the
rendered ``<head>`` — never internal stack state. Reactive surfaces live in the
page body; Cotton's children-first render means their pushes reach the
``lb_load_stack`` in the ``<head>`` before it drains.
"""

from labb.templatetags.lb_tags import _clear_stacks
from labb.tests.components.test_base import ComponentTestBase


def _has_datastar(html):
    return "datastar.js" in html


def _has_schema(html):
    return "lb-schema.js" in html


class TestDatastarOptInLoading(ComponentTestBase):
    def setup_method(self):
        # The push/load stack is process-global and normally cleared on the
        # request_finished signal, which does not fire under render_to_string.
        # Clear it so the negative "no runtime" assertions don't see scripts
        # leaked by reactive renders in other tests sharing this worker.
        super().setup_method()
        _clear_stacks()

    def test_default_page_ships_no_runtime(self):
        html = self.render_template_string("{% load lb_tags %}<c-lb.m.dependencies />")
        assert not _has_datastar(html)
        assert not _has_schema(html)

    def test_datastar_flag_force_loads_runtime(self):
        html = self.render_template_string(
            "{% load lb_tags %}<c-lb.m.dependencies datastar />"
        )
        assert _has_datastar(html)
        assert _has_schema(html)

    def test_signals_self_declare_runtime(self):
        html = self.render_template_string(
            '{% load lb_tags %}<c-lb.m.page><c-lbr.signals $count="1" /></c-lb.m.page>'
        )
        assert _has_datastar(html)
        assert _has_schema(html)

    def test_reactive_prop_auto_loads_runtime(self):
        # A lone reactive $-prop on a plain component, no signals, no flag.
        html = self.render_template_string(
            "{% load lb_tags %}<c-lb.m.page>"
            '<c-lb.badge variant="$status:neutral">Hi</c-lb.badge>'
            "</c-lb.m.page>"
        )
        assert _has_datastar(html)
        assert _has_schema(html)

    def test_static_prop_ships_no_runtime(self):
        html = self.render_template_string(
            "{% load lb_tags %}<c-lb.m.page>"
            '<c-lb.badge variant="neutral">Hi</c-lb.badge>'
            "</c-lb.m.page>"
        )
        assert not _has_datastar(html)
        assert not _has_schema(html)

    def test_action_loads_datastar(self):
        html = self.render_template_string(
            "{% load lb_tags %}<c-lb.m.page>"
            '<c-lbr.get to="/x/"><c-lb.button>Go</c-lb.button></c-lbr.get>'
            "</c-lb.m.page>"
        )
        assert _has_datastar(html)

    def test_reactive_chart_loads_runtime(self):
        html = self.render_template_string(
            "{% load lb_tags %}<c-lb.m.page>"
            '<c-lb.chart.instance type="bar" data="$sales:{}" />'
            "</c-lb.m.page>"
        )
        assert _has_datastar(html)

    def test_reactive_countdown_loads_runtime(self):
        # A signal-bound --value is reactive without being a class prop.
        html = self.render_template_string(
            "{% load lb_tags %}<c-lb.m.page>"
            '<c-lb.countdown value="$seconds:30" />'
            "</c-lb.m.page>"
        )
        assert _has_datastar(html)

    def test_static_countdown_ships_no_runtime(self):
        html = self.render_template_string(
            '{% load lb_tags %}<c-lb.m.page><c-lb.countdown value="30" /></c-lb.m.page>'
        )
        assert not _has_datastar(html)
