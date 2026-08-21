"""
Tests for c-lbr.signals and lbr_build_signals.

- $key=val              → data-signals JSON blob (add ifmissing to seed only)
- $path.key__mod=val    → individual data-signals:path.key__mod attr
- dots before __        → path separators
- dots after __         → modifier options (e.g. __case.kebab)

A schema adds a second, plain data-signals blob carrying only the fields the
view changed. See TestDeclarationAndChanges.
"""

import html as _html
import json
import re

from labb.tests.components.test_base import ComponentTestBase


def _parse(html, attr):
    m = re.search(rf"{re.escape(attr)}='([^']*)'", html)
    return None if m is None else json.loads(_html.unescape(m.group(1)))


def _blob(html):
    """The declared signals. A schema declares with the non-clobbering
    `__ifmissing`; `$` props are applied as written unless asked otherwise.
    """
    blob = _parse(html, "data-signals__ifmissing")
    if blob is None:
        blob = _parse(html, "data-signals")
    assert blob is not None, f"no signal declaration found in: {html}"
    return blob


def _blob_count(html):
    """How many signal-blob attributes the element carries, any modifier."""
    return len(re.findall(r"data-signals(?:__[\w.]+)?='", html))


def _changed(html):
    """The signals the view changed, or None when it changed nothing."""
    return _parse(html, "data-signals")


def _signal_attrs(html):
    """Return list of data-signals:* attribute names (with modifiers)."""
    return re.findall(r"data-signals:([\w.__-]+)=", html)


def _signal_attr_value(html, attr):
    """Return the parsed value of a specific data-signals:attr."""
    m = re.search(rf"data-signals:{re.escape(attr)}='([^']*)'", html)
    assert m, f"data-signals:{attr} not found in: {html}"
    return json.loads(_html.unescape(m.group(1)))


class TestCottonAttrPreservation(ComponentTestBase):
    def test_dollar_prefix_preserved(self):
        html = self.render_template_string(
            '{% load lbr_tags %}<c-lbr.signals $signalA="hello" />'
        )
        assert '"signalA": "hello"' in html

    def test_dotted_path_preserved(self):
        html = self.render_template_string(
            '{% load lbr_tags %}<c-lbr.signals $filters.q="foo" />'
        )
        assert _blob(html) == {"filters": {"q": "foo"}}

    def test_deep_nesting(self):
        html = self.render_template_string(
            '{% load lbr_tags %}<c-lbr.signals $a.b.c="deep" />'
        )
        assert _blob(html) == {"a": {"b": {"c": "deep"}}}


class TestBlobSignals(ComponentTestBase):
    def _render(self, attrs_str, context=None):
        return self.render_template_string(
            f"{{% load lbr_tags %}}<c-lbr.signals {attrs_str} />",
            context=context or {},
        )

    def test_flat_signal(self):
        assert _blob(self._render('$count="0"')) == {"count": "0"}

    def test_nested_signal(self):
        assert _blob(self._render('$filters.q="bar"')) == {"filters": {"q": "bar"}}

    def test_multiple_signals(self):
        assert _blob(self._render('$filters.q="x" $page="1"')) == {
            "filters": {"q": "x"},
            "page": "1",
        }

    def test_sibling_nested_signals_merge(self):
        assert _blob(self._render('$filters.q="x" $filters.sort="asc"')) == {
            "filters": {"q": "x", "sort": "asc"}
        }

    def test_html_attrs_excluded_from_signals(self):
        data = _blob(self._render('id="my-signals" $count="0"'))
        assert "id" not in data

    def test_id_passes_through_to_html(self):
        assert 'id="my-signals"' in self._render('id="my-signals" $count="0"')

    def test_hidden_div_output(self):
        html = self._render('$count="0"')
        assert "<div" in html
        assert "hidden" in html

    def test_variable_resolution(self):
        html = self._render("$filters.q=q", context={"q": 'fo"o'})
        assert _blob(html) == {"filters": {"q": 'fo"o'}}

    def test_single_quote_in_value_does_not_break_attribute(self):
        # Regression: _safe_json was a no-op — ' in values closed the attribute early.
        html = self._render("$filters.q=q", context={"q": "it's"})
        assert "&#x27;" in html  # single quote is HTML-escaped
        assert _blob(html) == {"filters": {"q": "it's"}}

    def test_angle_brackets_stay_literal_inside_the_attribute(self):
        # Left literal on purpose: the attribute quoting is what makes it safe.
        html = self._render("$filters.q=q", context={"q": "<script>a&b</script>"})
        assert _blob(html) == {"filters": {"q": "<script>a&b</script>"}}

    def test_deep_dot_path(self):
        assert _blob(self._render('$a.b.c.d="deep"')) == {
            "a": {"b": {"c": {"d": "deep"}}}
        }

    def test_dict_value_expands_to_nested(self):
        state = {"user": {"name": "Alice", "age": 30}}
        html = self._render("$state=state", context={"state": state})
        assert _blob(html) == {"state": {"user": {"name": "Alice", "age": 30}}}


class TestSignalInjection(ComponentTestBase):
    """Verify that user-controlled signal values cannot break out of data-signals='...'."""

    def _render(self, attrs_str, context=None):
        return self.render_template_string(
            f"{{% load lbr_tags %}}<c-lbr.signals {attrs_str} />",
            context=context or {},
        )

    def _assert_no_injection(self, html, injected_attr):
        """Assert the injected attribute name does not appear as a real HTML attribute
        (i.e. not followed by = with a literal single-quote delimiter)."""
        assert f"{injected_attr}='" not in html, (
            f"Injection succeeded — '{injected_attr}' appeared as an attribute:\n{html}"
        )

    def test_single_quote_closes_attribute_blocked(self):
        # Classic: ' closes data-signals='...' early, injecting a new attribute.
        payload = "foo' data-on-load='alert(1)"
        html = self._render("$q=q", context={"q": payload})
        self._assert_no_injection(html, "data-on-load")
        assert _blob(html) == {"q": payload}

    def test_datastar_event_handler_injection_blocked(self):
        # Attacker injects a Datastar event handler via a signal value.
        payload = "x' data-on:click='$secret=document.cookie"
        html = self._render("$q=q", context={"q": payload})
        self._assert_no_injection(html, "data-on:click")
        assert _blob(html) == {"q": payload}

    def test_signals_injection_blocked(self):
        # Attacker tries to add a second data-signals attribute to override state.
        payload = "x' data-signals='{\"admin\":true}"
        html = self._render("$q=q", context={"q": payload})
        # Only one data-signals blob should exist — the injected one won't parse cleanly.

        assert _blob_count(html) == 1, f"Extra data-signals attribute injected:\n{html}"
        assert _blob(html) == {"q": payload}

    def test_multiple_single_quotes_all_escaped(self):
        payload = "it's O'Brien's fault"
        html = self._render("$q=q", context={"q": payload})
        assert html.count("&#x27;") == 3
        assert _blob(html) == {"q": payload}

    def test_single_quote_in_nested_signal_value(self):
        payload = "don't"
        html = self._render("$filters.q=q", context={"q": payload})
        self._assert_no_injection(html, "data-on-load")
        assert _blob(html) == {"filters": {"q": payload}}

    def test_single_quote_in_dict_signal(self):
        # Dict values (e.g. from $state=state) with ' in string leaves must be safe.
        state = {"label": "it's here", "count": 1}
        html = self._render("$state=state", context={"state": state})
        assert "&#x27;" in html
        assert _blob(html) == {"state": state}

    def test_double_quote_in_value_is_safe(self):
        # json.dumps encodes " as \" — must not be double-escaped or broken.
        payload = 'say "hello"'
        html = self._render("$q=q", context={"q": payload})
        assert _blob(html) == {"q": payload}

    def test_combined_quote_types(self):
        payload = """it's a "test" value"""
        html = self._render("$q=q", context={"q": payload})
        self._assert_no_injection(html, "data-on-load")
        assert _blob(html) == {"q": payload}

    def test_backslash_in_value_is_safe(self):
        # Backslash is encoded by json.dumps as \\, must survive the round-trip.
        payload = "path\\to\\file"
        html = self._render("$q=q", context={"q": payload})
        assert _blob(html) == {"q": payload}

    def test_modifier_signal_injection_blocked(self):
        # Individual data-signals:key__mod='...' attrs go through _safe_json too.
        payload = "foo' data-on-load='alert(1)"
        html = self._render("$q__ifmissing=q", context={"q": payload})
        self._assert_no_injection(html, "data-on-load")

    def test_null_byte_in_value_is_safe(self):
        payload = "hello\x00world"
        html = self._render("$q=q", context={"q": payload})
        assert _blob(html) == {"q": payload}


class TestStripSignalAttrs(ComponentTestBase):
    """strip_signal_attrs — HTML-attribute injection via non-signal (passthrough) attrs."""

    def _render(self, attrs_str, context=None):
        return self.render_template_string(
            f"{{% load lbr_tags %}}<c-lbr.signals {attrs_str} />",
            context=context or {},
        )

    def _assert_no_injection(self, html, injected_attr):
        assert f" {injected_attr}=" not in html, (
            f"Injection succeeded — '{injected_attr}' appeared as an attribute:\n{html}"
        )

    # ── correct output ───────────────────────────────────────────────────────

    def test_plain_attr_passes_through(self):
        html = self._render('id="my-signals" $count="0"')
        assert 'id="my-signals"' in html

    def test_boolean_attr_has_no_value(self):
        # boolean True attrs are emitted as bare keys (e.g. hidden, disabled)
        html = self._render('$count="0"')
        assert "hidden" in html
        assert 'hidden="' not in html

    def test_dollar_attrs_excluded(self):
        html = self._render('$count="0" id="x"')
        assert "$count" not in html
        assert "count=" not in html

    # ── escaping correctness ─────────────────────────────────────────────────

    def test_double_quote_in_attr_value_is_escaped(self):
        # " in a passthrough attr value must become &quot; so it can't close
        # the surrounding double-quoted HTML attribute.
        html = self._render('id=x $count="0"', context={"x": 'fo"o'})
        assert 'id="fo&quot;o"' in html

    def test_less_than_in_attr_value_is_escaped(self):
        html = self._render('id=x $count="0"', context={"x": "a<b"})
        assert 'id="a&lt;b"' in html

    def test_ampersand_in_attr_value_is_escaped(self):
        html = self._render('id=x $count="0"', context={"x": "a&b"})
        assert 'id="a&amp;b"' in html

    # ── injection tests ──────────────────────────────────────────────────────

    def test_double_quote_breakout_injection_blocked(self):
        # " closes the attribute, the rest becomes new attributes on the element.
        payload = 'x" data-on-load="alert(1)'
        html = self._render('id=x $count="0"', context={"x": payload})
        assert "&quot;" in html  # " was HTML-escaped, kept inside the attribute value
        # A real breakout would produce data-on-load="alert — with a literal ".
        assert 'data-on-load="alert' not in html

    def test_signal_override_injection_blocked(self):
        # Attempt to inject a second data-signals attr to override state.
        payload = 'x" data-signals=\'{"admin":true}\' y="z'
        html = self._render('id=x $count="0"', context={"x": payload})
        assert _blob_count(html) == 1, f"Extra data-signals injected:\n{html}"

    def test_script_tag_injection_blocked(self):
        payload = '"><script>alert(1)</script><span x="'
        html = self._render('id=x $count="0"', context={"x": payload})
        assert "<script>" not in html


class TestSignalModifiers(ComponentTestBase):
    def _render(self, attrs_str, context=None):
        return self.render_template_string(
            f"{{% load lbr_tags %}}<c-lbr.signals {attrs_str} />",
            context=context or {},
        )

    def test_ifmissing_renders_as_individual_attr(self):
        html = self._render('$count__ifmissing="0"')
        assert "count__ifmissing" in _signal_attrs(html)
        assert _signal_attr_value(html, "count__ifmissing") == "0"

    def test_case_modifier_with_option(self):
        html = self._render('$mySignal__case.kebab="val"')
        assert "mySignal__case.kebab" in _signal_attrs(html)

    def test_nested_path_with_modifier(self):
        html = self._render('$filters.q__ifmissing="default"')
        assert "filters.q__ifmissing" in _signal_attrs(html)
        assert _signal_attr_value(html, "filters.q__ifmissing") == "default"

    def test_modifier_not_in_blob(self):
        html = self._render('$count="0" $foo__ifmissing="bar"')
        assert _blob(html) == {"count": "0"}
        assert "foo__ifmissing" in _signal_attrs(html)

    def test_mixed_blob_and_individual(self):
        html = self._render('$count="1" $filters.q="x" $page__ifmissing="1"')
        assert _blob(html) == {"count": "1", "filters": {"q": "x"}}
        assert "page__ifmissing" in _signal_attrs(html)

    def test_dots_after_double_underscore_are_modifier_options(self):
        """$a.b__case.kebab → path=a.b, modifier=case.kebab (not a.b.case)"""
        html = self._render('$a.b__case.kebab="v"')
        assert "a.b__case.kebab" in _signal_attrs(html)
        assert _blob_count(html) == 0  # modifier signals never go in a blob


class TestSyncQuery(ComponentTestBase):
    def _render(self, attrs_str, context=None):
        return self.render_template_string(
            f"{{% load lbr_tags %}}<c-lbr.signals {attrs_str} />",
            context=context or {},
        )

    def _patch_js(self, html):
        m = re.search(r"data-on-signal-patch='([^']*)'", html)
        assert m, f"data-on-signal-patch not found in: {html}"
        return m.group(1)

    def test_no_sync_query_no_patch_attr(self):
        html = self._render('$filters.q="foo"')
        assert "data-on-signal-patch" not in html

    def test_no_sync_query_no_init_attr(self):
        html = self._render('$filters.q="foo"')
        assert "data-init" not in html

    def test_sync_query_adds_patch_attr(self):
        html = self._render('$filters.q="foo" syncQuery')
        assert "data-on-signal-patch=" in html

    def test_sync_query_adds_init_attr(self):
        # data-init fires on morph so URL is written even when signals haven't changed
        html = self._render('$filters.q="foo" syncQuery')
        assert "data-init=" in html

    def test_sync_query_init_and_patch_same_js(self):
        html = self._render('$filters.q="foo" syncQuery')
        m_init = re.search(r"data-init='([^']*)'", html)
        m_patch = re.search(r"data-on-signal-patch='([^']*)'", html)
        assert m_init and m_patch
        assert m_init.group(1) == m_patch.group(1)

    def test_sync_js_uses_configured_key(self):
        js = self._patch_js(self._render('$filters.q="foo" syncQuery'))
        assert 'p.set("lbr.' in js  # default key, flat format
        assert "URLSearchParams" in js

    def test_sync_js_nested_object(self):
        js = self._patch_js(self._render('$filters.q="foo" syncQuery'))
        assert 'p.set("lbr.filters.q",$filters.q)' in js

    def test_sync_js_flat_signal(self):
        js = self._patch_js(self._render('$page="1" syncQuery'))
        assert 'p.set("lbr.page",$page)' in js

    def test_sync_query_multiple_signals(self):
        js = self._patch_js(self._render('$filters.q="foo" $page="1" syncQuery'))
        assert 'p.set("lbr.filters.q",$filters.q)' in js
        assert 'p.set("lbr.page",$page)' in js

    def test_modifier_signals_excluded_from_sync(self):
        js = self._patch_js(
            self._render('$filters.q="foo" $page__ifmissing="1" syncQuery')
        )
        assert 'p.set("lbr.filters.q",$filters.q)' in js
        assert '"lbr.page"' not in js

    def test_sync_query_false_by_default(self):
        html = self._render('$filters.q="foo"')
        assert "replaceState" not in html


class TestSyncQueryPathGuard(ComponentTestBase):
    """Paths outside [\\w.] are dropped instead of being interpolated raw into JS."""

    def _js(self, attrs):
        from labb.templatetags.lbr_tags import lbr_query_sync_js

        return lbr_query_sync_js(attrs)

    def test_odd_path_produces_no_js(self):
        assert self._js({'$q");alert(1);//': "x"}) == ""

    def test_good_path_kept_alongside_odd_one(self):
        js = self._js({"$page": "1", '$a"b': "x"})
        assert 'p.set("lbr.page",$page)' in js
        assert 'a"b' not in js

    def test_odd_path_dropped_from_js_object(self):
        from labb.templatetags.lbr_tags import _build_datastar_js_obj

        assert _build_datastar_js_obj(['a"b', "page"]) == '{"page":$page}'


class TestDeclarationAndChanges(ComponentTestBase):
    """The schema declares with `__ifmissing` and sends changes as a plain blob."""

    def _render(self, attrs_str, context=None):
        return self.render_template_string(
            f"{{% load lbr_tags %}}<c-lbr.signals {attrs_str} />",
            context=context or {},
        )

    def _schema(self, values):
        from labb.signals import Int, Signals, Str

        class QuerySignals(Signals):
            q = Str(path="filters.q", default="")
            page = Int(default=1)

        return QuerySignals(values)

    def test_dollar_attrs_are_applied_as_written(self):
        html = self._render('$ui.editingPk="0"')
        assert "data-signals__ifmissing=" not in html
        assert _changed(html) == {"ui": {"editingPk": "0"}}

    def test_ifmissing_opts_a_dollar_declaration_out_of_clobbering(self):
        html = self._render('$open="false" ifmissing')
        assert _blob(html) == {"open": False}
        assert _changed(html) is None

    def test_schema_declares_every_field(self):
        schema = self._schema({"filters": {"q": "acme"}, "page": 3})
        html = self._render(":schema=schema", {"schema": schema})
        assert _blob(html) == {"filters": {"q": "acme"}, "page": 3}

    def test_untouched_schema_changes_nothing(self):
        schema = self._schema({"filters": {"q": "acme"}})
        html = self._render(":schema=schema", {"schema": schema})
        assert _changed(html) is None

    def test_assigned_field_is_sent_as_a_change(self):
        schema = self._schema({"filters": {"q": "acme"}, "page": 9})
        schema.page = 1
        html = self._render(":schema=schema", {"schema": schema})
        assert _changed(html) == {"page": 1}
        # ...and the declaration still carries the whole schema.
        assert _blob(html) == {"filters": {"q": "acme"}, "page": 1}

    def test_assigning_the_same_value_is_not_a_change(self):
        # `s.page = min(s.page, total_pages)` on a page needing no clamp.
        schema = self._schema({"page": 3})
        schema.page = 3
        html = self._render(":schema=schema", {"schema": schema})
        assert _changed(html) is None

    def test_mark_changed_is_how_a_schema_forces_a_value(self):
        schema = self._schema({"filters": {"q": "acme"}})
        schema.mark_changed()
        html = self._render(":schema=schema", {"schema": schema})
        assert _changed(html) == {"filters": {"q": "acme"}, "page": 1}


class TestChangeTracking(ComponentTestBase):
    def _schema(self, values=None):
        from labb.signals import Int, Signals, Str

        class S(Signals):
            q = Str(path="filters.q", default="")
            page = Int(default=1)

        return S(values or {})

    def test_parsing_the_request_is_not_a_change(self):
        assert self._schema({"filters": {"q": "acme"}, "page": 4}).changed == set()

    def test_assignment_records_the_field(self):
        s = self._schema()
        s.page = 7
        assert s.changed == {"page"}

    def test_changed_dict_uses_the_field_path(self):
        s = self._schema()
        s.q = "acme"
        assert s.changed_signals_dict() == {"filters": {"q": "acme"}}

    def test_changed_dict_follows_field_declaration_order(self):
        from labb.signals import Int, Signals

        class Ordered(Signals):
            first = Int(default=1)
            second = Int(default=2)
            third = Int(default=3)

        s = Ordered()
        s.third = 30
        s.first = 10
        s.second = 20

        assert list(s.changed_signals_dict()) == ["first", "second", "third"]

    def test_mark_changed_forces_a_matching_value(self):
        s = self._schema({"page": 4})
        s.page = 4
        assert s.changed == set()
        s.mark_changed("page")
        assert s.changed_signals_dict() == {"page": 4}

    def test_mark_changed_with_no_args_marks_everything(self):
        s = self._schema({"filters": {"q": "acme"}, "page": 4})
        s.mark_changed()
        assert s.changed_signals_dict() == {"filters": {"q": "acme"}, "page": 4}

    def test_mark_changed_rejects_an_unknown_field(self):
        import pytest

        with pytest.raises(KeyError, match="nope"):
            self._schema().mark_changed("nope")

    def test_changed_is_a_copy(self):
        s = self._schema()
        s.changed.add("page")
        assert s.changed == set()


class TestSignalPatches:
    def test_patch_delegates_named_fields(self, monkeypatch):
        from datastar_py import ServerSentEventGenerator

        from labb.signals import Int, Signals

        class S(Signals):
            page = Int(default=1)
            size = Int(default=20)  # a second field, so "named" can fail

        calls = []

        def patch_signals(signals, only_if_missing=False):
            calls.append((signals, only_if_missing))
            return "signal-patch"

        monkeypatch.setattr(ServerSentEventGenerator, "patch_signals", patch_signals)
        s = S()

        assert s.patch("page") == "signal-patch"
        assert calls == [({"page": 1}, False)]
