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


class TestMorphGuard(ComponentTestBase):
    """data-preserve-attr guards a bound field whose value the server renders.

    The other half, the schema sending back only what changed, is in
    test_lbr_signals.py.
    """

    @pytest.mark.parametrize(
        "component,attr",
        [
            ("input", "value"),
            ("range", "value"),
            ("checkbox", "checked"),
            ("toggle", "checked"),
        ],
    )
    def test_bound_field_preserves_its_value_attribute(self, component, attr):
        html = self.render_component(component, bind="$filters.q")
        assert f'data-preserve-attr="{attr}"' in html

    @pytest.mark.parametrize("component", BIND_COMPONENTS)
    def test_unbound_field_has_no_guard(self, component):
        assert "data-preserve-attr" not in self.render_component(component)

    @pytest.mark.parametrize("component", ["select", "textarea"])
    def test_unguardable_components_do_not_claim_a_guard(self, component):
        html = self.render_component(component, bind="$filters.q")
        assert "data-bind:filters.q" in html
        assert "data-preserve-attr" not in html

    def test_every_bindable_component_declares_its_guard(self):
        """A new bindable component cannot ship without a BIND_PRESERVE entry."""
        from pathlib import Path

        from labb.templatetags.lbr_tags import BIND_PRESERVE

        root = Path(__file__).resolve().parents[2] / "templates" / "cotton" / "lb"
        calling = {
            path.parent.name
            for path in root.glob("*/index.html")
            if "{% lbr_bind " in path.read_text()
        }
        assert calling == set(BIND_PRESERVE), (
            f"templates calling lbr_bind: {sorted(calling)}, "
            f"BIND_PRESERVE: {sorted(BIND_PRESERVE)}"
        )


class TestBindPathIsValidated:
    """Attribute-NAME position: a space alone breaks out, so only a path gets through."""

    @pytest.mark.parametrize(
        "payload",
        [
            'filters.q" autofocus onfocus="alert(1)',  # quote break-out
            "filters.q onfocus=alert(1) autofocus",  # spaces alone, no quote
            "filters.q><script>alert(1)</script>",  # close the tag
            "filters.q'",
            "$",  # a bare sigil, no name
        ],
    )
    def test_a_path_that_is_not_a_signal_name_is_refused(self, payload):
        from labb.templatetags.lbr_tags import lbr_bind

        with pytest.raises(ValueError, match="not a signal path"):
            lbr_bind("input", payload)

    @pytest.mark.parametrize(
        "path", ["q", "filters.q", "edit.contact_name", "selected.7", "$filters.q"]
    )
    def test_real_paths_still_render(self, path):
        from labb.templatetags.lbr_tags import lbr_bind

        assert lbr_bind("input", path).startswith("data-bind:")


class TestBindInjectionThroughContext(ComponentTestBase):
    """The real vector: an interpolated path, as in bind="$selected.{{ pk }}".

    The helper swallows render errors, so these assert no element is produced.
    """

    PAYLOAD = "q onfocus=alert(1) autofocus"

    @pytest.mark.parametrize("component", BIND_COMPONENTS)
    def test_a_path_from_context_cannot_inject_an_attribute(self, component):
        html = self.render_template_string(
            f"<c-lb.{component} :bind=payload />", context={"payload": self.PAYLOAD}
        )
        assert "data-bind" not in html
        assert "<input" not in html and "<select" not in html
        assert "<textarea" not in html

    def test_an_interpolated_path_cannot_inject_an_attribute(self):
        html = self.render_template_string(
            '<c-lb.input bind="$selected.{{ pk }}" />',
            context={"pk": "x onfocus=alert(1) autofocus"},
        )
        assert "data-bind" not in html
        assert "<input" not in html

    def test_an_ordinary_interpolated_path_still_renders(self):
        html = self.render_template_string(
            '<c-lb.input bind="$selected.{{ pk }}" />', context={"pk": 7}
        )
        assert "data-bind:selected.7" in html
