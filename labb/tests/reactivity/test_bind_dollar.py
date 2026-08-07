"""`bind` accepts a `$`-prefixed signal path.

Signals are named with `$` everywhere else: declarations (`$count="0"`),
data- expressions (`data-text="$count"`), reactive props (`variant="$status:x"`).
`bind` was the one place you dropped it. It now takes either, so the guide can
teach one rule, and the bare form keeps working so existing templates and the
35 installed blocks are unaffected.
"""

import re

import pytest

from labb.templatetags.lbr_tags import lbr_bind_path
from labb.tests.components.test_base import ComponentTestBase

# every component declaring a `bind` prop
BIND_COMPONENTS = ["input", "checkbox", "textarea", "toggle", "select", "range"]


def _bound_path(html):
    m = re.search(r"data-bind:([^\s=>\"']+)", html)
    return m.group(1) if m else None


class TestBindPathFilter:
    @pytest.mark.parametrize(
        "value,expected",
        [
            ("$filters.q", "filters.q"),
            ("filters.q", "filters.q"),
            ("$q", "q"),
            ("q", "q"),
            ("", ""),
        ],
    )
    def test_strips_one_leading_dollar(self, value, expected):
        assert lbr_bind_path(value) == expected

    def test_only_the_first_dollar_is_the_sigil(self):
        # a signal literally named "$q" is addressed as "$$q"
        assert lbr_bind_path("$$q") == "$q"

    def test_a_schema_field_is_read_through_its_path(self):
        class Field:
            path = "filters.q"

        assert lbr_bind_path(Field()) == "filters.q"

    def test_a_schema_field_path_may_also_carry_a_dollar(self):
        class Field:
            path = "$filters.q"

        assert lbr_bind_path(Field()) == "filters.q"


class TestBindOnComponents(ComponentTestBase):
    @pytest.mark.parametrize("component", BIND_COMPONENTS)
    def test_dollar_form_binds_the_same_signal_as_the_bare_form(self, component):
        dollar = self.render_component(component, bind="$filters.q")
        bare = self.render_component(component, bind="filters.q")

        assert _bound_path(dollar) == "filters.q"
        assert _bound_path(bare) == "filters.q"

    @pytest.mark.parametrize("component", BIND_COMPONENTS)
    def test_no_bind_emits_no_data_bind(self, component):
        assert "data-bind" not in self.render_component(component)

    @pytest.mark.parametrize("component", BIND_COMPONENTS)
    def test_the_dollar_does_not_survive_into_the_attribute(self, component):
        html = self.render_component(component, bind="$filters.q")
        assert "data-bind:$" not in html
