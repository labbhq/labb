"""
Tests for lbr action tags and components: get, post, delete, replace-url.

Tag-level tests cover output shape, options, before, and escaping.
Component-level tests cover prop wiring, on="init" → data-init, and passthrough attrs.
"""

import re

from labb.tests.components.test_base import ComponentTestBase


def _load_js(html):
    m = re.search(r'data-init="([^"]*)"', html)
    assert m, f"data-init not found in: {html}"
    return m.group(1)


class TestReplaceUrlJs(ComponentTestBase):
    def _render(self, attrs_str):
        return self.render_template_string(
            f"{{% load lbr_tags %}}<c-lbr.replace-url {attrs_str} />"
        )

    def test_uses_replace_state_by_default(self):
        js = _load_js(self._render('to="/todos/"'))
        assert "replaceState" in js
        assert "pushState" not in js

    def test_push_uses_push_state(self):
        js = _load_js(self._render('to="/todos/" push'))
        assert "pushState" in js

    def test_push_falls_back_to_replace_when_same_path(self):
        # Guards against duplicate history entries on direct page loads
        js = _load_js(self._render('to="/todos/" push'))
        assert "location.pathname===_u" in js
        assert "replaceState" in js  # the same-path branch

    def test_static_url_quoted(self):
        js = _load_js(self._render('to="/todos/1/"'))
        assert "'/todos/1/'" in js

    def test_signal_url_becomes_template_literal(self):
        js = _load_js(self._render('to="/todos/$todoId/"'))
        assert "`/todos/${$todoId}/`" in js

    def test_signal_url_dotted_path(self):
        js = _load_js(self._render('to="/todos/$todo.pk/detail/"'))
        assert "`/todos/${$todo.pk}/detail/`" in js

    def test_signal_url_multiple_refs(self):
        js = _load_js(self._render('to="/$section/$itemId/"'))
        assert "`/${$section}/${$itemId}/`" in js

    def test_direct_url_passthrough(self):
        html = self._render('to="/todos/42/"')
        assert "/todos/42/" in html

    def test_hidden_div_with_data_init(self):
        html = self._render('to="/todos/"')
        assert "<div" in html
        assert "data-init=" in html
        assert "hidden" in html

    def test_no_signal_url_no_template_literal(self):
        js = _load_js(self._render('to="/todos/plain/"'))
        assert "`" not in js


class TestReplaceUrlJsInjection(ComponentTestBase):
    """lbr_replace_url_js — template-literal injection via backtick / ${ in href."""

    def _js(self, url):
        from labb.templatetags.lbr_tags import lbr_replace_url_js

        return lbr_replace_url_js(url)

    # ── signal refs still work after the fix ─────────────────────────────────

    def test_signal_ref_still_becomes_template_expression(self):
        js = self._js("/todos/$todoId/")
        assert "${$todoId}" in js

    def test_dotted_signal_ref_still_works(self):
        js = self._js("/todos/$todo.pk/")
        assert "${$todo.pk}" in js

    # ── backtick escaping ─────────────────────────────────────────────────────

    def test_backtick_in_url_is_escaped(self):
        # A bare ` in the url would close the template literal early.
        js = self._js("/path/`xss`/$id/")
        assert "\\`xss\\`" in js
        assert "${$id}" in js  # signal ref still resolved

    def test_backtick_only_url_does_not_close_literal(self):
        # URL must contain $ to enter the template-literal branch.
        js = self._js("/path/`/$id/")
        assert "\\`" in js  # backtick is escaped so it cannot close the literal

    # ── ${ injection escaping ─────────────────────────────────────────────────

    def test_existing_brace_expression_is_escaped(self):
        # ${expr} in the url must not be evaluated as a JS template expression.
        js = self._js("/path/${location.href}/$id/")
        assert "\\${location.href}" in js
        assert "${$id}" in js  # signal ref still resolved

    def test_combined_backtick_and_brace_injection(self):
        js = self._js("/x/`${alert(1)}`/$signal/")
        assert "\\`" in js
        assert "\\${alert(1)}" in js
        assert "${$signal}" in js


class TestResolveUrlKwargs(ComponentTestBase):
    """Tests for to= URL detection, pk shorthand, and kwargs."""

    def _get(self, attrs_str):
        return self.render_template_string(
            f"{{% load lbr_tags %}}<c-lbr.get {attrs_str} />"
        )

    def _replace_url(self, attrs_str):
        return self.render_template_string(
            f"{{% load lbr_tags %}}<c-lbr.replace-url {attrs_str} />"
        )

    # ── direct URL (leading /) ────────────────────────────────────────────────

    def test_direct_url_passes_through(self):
        html = self._get('to="/todos/42/"')
        assert "@get('/todos/42/')" in html

    def test_direct_url_on_replace_url(self):
        html = self._replace_url('to="/todos/42/"')
        assert "/todos/42/" in html

    def test_pk_ignored_for_direct_url(self):
        # pk is irrelevant when to= is a direct URL
        html = self._get('to="/todos/42/" pk="42"')
        assert "@get('/todos/42/')" in html

    def test_pk_empty_does_not_break_direct_url(self):
        html = self._get('to="/todos/" pk=""')
        assert "@get('/todos/')" in html

    # ── kwargs ────────────────────────────────────────────────────────────────

    def test_kwargs_and_pk_both_empty_is_fine(self):
        html = self._get('to="/safe/"')
        assert "@get('/safe/')" in html

    # ── tag-level lbr_resolve_url ─────────────────────────────────────────────

    def test_direct_url_returned_as_is(self):
        from labb.templatetags.lbr_tags import lbr_resolve_url

        assert lbr_resolve_url("/direct/") == "/direct/"

    def test_empty_to_returns_empty(self):
        from labb.templatetags.lbr_tags import lbr_resolve_url

        assert lbr_resolve_url("") == ""

    def test_graceful_empty_on_bad_viewname(self):
        from labb.templatetags.lbr_tags import lbr_resolve_url

        assert lbr_resolve_url("no:such:view") == ""

    def test_graceful_empty_on_bad_json(self):
        from labb.templatetags.lbr_tags import lbr_resolve_url

        assert lbr_resolve_url("no:view", "not-json") == ""

    def test_dict_kwargs_does_not_raise(self):
        from labb.templatetags.lbr_tags import lbr_resolve_url

        assert lbr_resolve_url("no:view", {"pk": 1}) == ""

    def test_http_url_passes_through(self):
        from labb.templatetags.lbr_tags import lbr_resolve_url

        assert lbr_resolve_url("https://example.com/api/") == "https://example.com/api/"


class TestDeleteActionConfirm(ComponentTestBase):
    """lbr_delete_action — confirm= escaping and injection hardening."""

    def _action(self, confirm_text):
        """Call lbr_delete_action directly with a pre-HTML-escaped confirm string,
        matching what the template engine delivers after auto-escaping {{ emp.name }}."""
        from django.utils.html import conditional_escape

        from labb.templatetags.lbr_tags import lbr_delete_action

        escaped = conditional_escape(confirm_text)
        return lbr_delete_action("/items/1/", "", escaped)

    # ── correct output shape ─────────────────────────────────────────────────

    def test_no_confirm_omits_confirm_call(self):
        from labb.templatetags.lbr_tags import lbr_delete_action

        assert "confirm(" not in lbr_delete_action("/items/1/", "", "")

    def test_plain_message_passes_through(self):
        result = self._action("Delete this item?")
        assert "confirm('Delete this item?')" in result

    def test_delete_action_always_present(self):
        result = self._action("Sure?")
        assert "@delete('/items/1/'" in result

    # ── character escaping correctness ───────────────────────────────────────

    def test_single_quote_is_backslash_escaped(self):
        # ' → \' so the JS single-quoted string is not broken
        result = self._action("Delete O'Brien?")
        assert r"confirm('Delete O\'Brien?')" in result

    def test_backslash_is_doubled(self):
        # \ → \\ before the quote escape, to avoid mangling the \' sequence
        result = self._action("path\\file")
        assert r"confirm('path\\file')" in result

    def test_newline_is_escaped(self):
        result = self._action("Line1\nLine2")
        assert r"confirm('Line1\nLine2')" in result

    def test_carriage_return_is_escaped(self):
        result = self._action("Line1\rLine2")
        assert r"confirm('Line1\rLine2')" in result

    def test_double_quote_does_not_break_html_attribute(self):
        # " must NOT appear literally in the JS string — it would close the
        # surrounding data-on:click="..." HTML attribute.
        result = self._action('Delete "special" item?')
        # json.dumps-style \" is fine; a bare " in the action would not be.
        assert (
            '"special"' not in result or result.count('"') <= 2
        )  # only the outer attr quotes

    # ── injection tests ──────────────────────────────────────────────────────

    def test_single_quote_injection_blocked(self):
        # Classic JS string breakout: close the confirm string, run arbitrary JS.
        # Without escaping, "x')" closes the confirm string and " && alert(...)" runs.
        payload = "x') && alert(document.cookie) && confirm('"
        result = self._action(payload)
        # Both ' chars in the payload must be backslash-escaped in the output.
        # The payload has exactly 2 single quotes; both must appear as \'.
        assert result.count("\\'") >= 2, (
            f"Payload quotes not escaped — injection may be possible:\n{result}"
        )
        # The confirm call must open and the @delete must follow, not arbitrary JS.
        assert result.startswith("confirm('")
        assert ") && @delete(" in result

    def test_backslash_then_quote_injection_blocked(self):
        # Without escaping \ first, \' in the output could be read as an escaped \
        # followed by a bare ', closing the string.
        payload = "foo\\'bar"  # intended to produce foo\' after naive escaping
        result = self._action(payload)
        # Both the backslash and the quote must be independently escaped.
        assert r"foo\\\'" in result  # \\ for the \ and \' for the '

    def test_html_entities_in_input_are_unescaped_before_js_escaping(self):
        # The template engine turns ' into &#x27;. The function must unescape
        # that before JS-escaping, otherwise &#x27; reaches the browser as-is
        # and HTML-decodes back to ' at the JS layer — broken string.
        from labb.templatetags.lbr_tags import lbr_delete_action

        html_escaped_input = "Delete O&#x27;Brien?"  # as delivered by template engine
        result = lbr_delete_action("/items/1/", "", html_escaped_input)
        assert r"O\'Brien" in result  # properly JS-escaped
        assert "&#x27;" not in result  # entity must not survive into JS


# ---------------------------------------------------------------------------
# lbr_get_action tag
# ---------------------------------------------------------------------------


class TestGetAction(ComponentTestBase):
    def _action(self, **kwargs):
        from labb.templatetags.lbr_tags import lbr_get_action

        return lbr_get_action("/url/", **kwargs)

    def test_basic(self):
        assert self._action() == "@get('/url/')"

    def test_options_appended(self):
        result = self._action(options="{selector: '#main'}")
        assert result == "@get('/url/', {selector: '#main'})"

    def test_before_prepended(self):
        result = self._action(before="evt.preventDefault()")
        assert result == "evt.preventDefault(); @get('/url/')"

    def test_replace_url_appended(self):
        result = self._action(replace_url="1")
        assert "replaceState" in result
        assert "@get('/url/')" in result

    def test_push_url_appended(self):
        result = self._action(push_url="1")
        assert "pushState" in result
        assert "@get('/url/')" in result

    def test_preserve_query_adds_location_search(self):
        result = self._action(replace_url="1", preserve_query="1")
        assert "location.search" in result

    def test_before_and_options_together(self):
        result = self._action(before="log()", options="{x: 1}")
        assert result.startswith("log()")
        assert "@get('/url/', {x: 1})" in result


# ---------------------------------------------------------------------------
# lbr_post_action tag
# ---------------------------------------------------------------------------


class TestPostAction(ComponentTestBase):
    def _action(self, **kwargs):
        from labb.templatetags.lbr_tags import lbr_post_action

        return lbr_post_action("/url/", **kwargs)

    # CSRF is on by default — assertions below pass csrf=False to test the pure
    # options shaping; the dedicated CSRF cases live in TestPostActionCSRF.

    def test_form_default_posts_json(self):
        # Form mode posts the signal store as JSON — the only body the middleware
        # reads back into request.signals — so no contentType is emitted.
        assert self._action(csrf=False) == "@post('/url/')"
        assert self._action(tag="form", csrf=False) == "@post('/url/')"

    def test_non_form_tag_omits_content_type(self):
        assert self._action(tag="div", csrf=False) == "@post('/url/')"

    def test_explicit_form_content_type_still_available(self):
        # A caller who genuinely wants a classic form POST opts in explicitly.
        result = self._action(options="{contentType: 'form'}", csrf=False)
        assert result == "@post('/url/', {contentType: 'form'})"

    def test_options_override_content_type(self):
        result = self._action(options="{contentType: 'json'}", csrf=False)
        assert result == "@post('/url/', {contentType: 'json'})"

    def test_options_on_non_form_tag(self):
        result = self._action(tag="div", options="{retryCount: 3}", csrf=False)
        assert result == "@post('/url/', {retryCount: 3})"

    def test_before_prepended(self):
        result = self._action(before="validate()", csrf=False)
        assert result == "validate(); @post('/url/')"


class TestPostActionCSRF(ComponentTestBase):
    """lbr_post_action — CSRF header is injected by default, opt-out via csrf=False."""

    def _action(self, **kwargs):
        from labb.templatetags.lbr_tags import lbr_post_action

        return lbr_post_action("/url/", **kwargs)

    def test_form_includes_csrf_header_by_default(self):
        result = self._action()
        assert result == (
            "@post('/url/', {headers: {'X-CSRFToken': labbGetCSRFToken()}})"
        )

    def test_non_form_includes_csrf_header_by_default(self):
        assert self._action(tag="div") == (
            "@post('/url/', {headers: {'X-CSRFToken': labbGetCSRFToken()}})"
        )

    def test_token_value_is_js_call_not_static_string(self):
        # The header value must be evaluated client-side at request time.
        assert "labbGetCSRFToken()" in self._action()

    def test_csrf_false_omits_header_on_form(self):
        result = self._action(csrf=False)
        assert result == "@post('/url/')"
        assert "X-CSRFToken" not in result

    def test_csrf_false_omits_header_on_non_form(self):
        assert self._action(tag="div", csrf=False) == "@post('/url/')"

    def test_explicit_options_still_get_csrf(self):
        result = self._action(options="{contentType: 'json'}")
        assert result == (
            "@post('/url/', {contentType: 'json', "
            "headers: {'X-CSRFToken': labbGetCSRFToken()}})"
        )

    def test_csrf_false_string_from_template_omits_header(self):
        # Templates may deliver csrf as the string "False".
        assert "X-CSRFToken" not in self._action(csrf="False")


class TestDeleteActionCSRF(ComponentTestBase):
    """lbr_delete_action — CSRF header is injected by default, opt-out via csrf=False."""

    def _action(self, **kwargs):
        from labb.templatetags.lbr_tags import lbr_delete_action

        return lbr_delete_action("/url/", **kwargs)

    def test_includes_csrf_header_by_default(self):
        assert self._action() == (
            "@delete('/url/', {headers: {'X-CSRFToken': labbGetCSRFToken()}})"
        )

    def test_csrf_false_omits_header(self):
        assert self._action(csrf=False) == "@delete('/url/')"

    def test_confirm_and_csrf_coexist(self):
        result = self._action(confirm="Sure?")
        assert result.startswith("confirm('Sure?') && @delete('/url/'")
        assert "X-CSRFToken" in result

    def test_explicit_options_merged_with_csrf(self):
        result = self._action(options="{selector: '#x'}")
        assert result == (
            "@delete('/url/', {selector: '#x', "
            "headers: {'X-CSRFToken': labbGetCSRFToken()}})"
        )


class TestGetActionNoCSRF(ComponentTestBase):
    """GET is a safe method — it must never carry a CSRF header."""

    def test_basic_get_has_no_csrf(self):
        from labb.templatetags.lbr_tags import lbr_get_action

        assert "X-CSRFToken" not in lbr_get_action("/url/")

    def test_get_with_options_has_no_csrf(self):
        from labb.templatetags.lbr_tags import lbr_get_action

        assert "X-CSRFToken" not in lbr_get_action("/url/", options="{selector: '#x'}")


# ---------------------------------------------------------------------------
# lbr_delete_action tag — basic and options (confirm covered by TestDeleteActionConfirm)
# ---------------------------------------------------------------------------


class TestDeleteAction(ComponentTestBase):
    def _action(self, **kwargs):
        from labb.templatetags.lbr_tags import lbr_delete_action

        return lbr_delete_action("/url/", **kwargs)

    # CSRF is on by default — pass csrf=False here to test pure options shaping;
    # dedicated CSRF cases live in TestDeleteActionCSRF.

    def test_basic(self):
        assert self._action(csrf=False) == "@delete('/url/')"

    def test_options_appended(self):
        result = self._action(options="{selector: '#x'}", csrf=False)
        assert result == "@delete('/url/', {selector: '#x'})"

    def test_before_without_confirm(self):
        result = self._action(before="log()", csrf=False)
        assert result == "log(); @delete('/url/')"

    def test_before_with_confirm(self):
        result = self._action(before="log()", confirm="Sure?", csrf=False)
        assert result.startswith("log()")
        assert "confirm('Sure?')" in result
        assert "@delete('/url/')" in result


# ---------------------------------------------------------------------------
# href escaping — a `to` derived from model/user data must not break out of
# the single-quoted JS string in @get/@post/@delete (or the pushState loc).
# ---------------------------------------------------------------------------


class TestActionHrefEscaping(ComponentTestBase):
    # A URL with an apostrophe: legitimately possible, and the injection vector.
    PAYLOAD = "/search/?q=a' + alert(document.cookie) + '"

    def test_get_action_escapes_quote(self):
        from labb.templatetags.lbr_tags import lbr_get_action

        result = lbr_get_action(self.PAYLOAD)
        assert "a\\' + alert" in result  # quote escaped, does not break out
        # No raw (unescaped) single quote from the payload survives to break the string.
        assert "a' + alert" not in result

    def test_get_action_escapes_quote_in_pushstate_loc(self):
        from labb.templatetags.lbr_tags import lbr_get_action

        result = lbr_get_action(self.PAYLOAD, push_url="1")
        # Both @get and the pushState loc carry the href, so both quotes are escaped.
        assert "a' + alert" not in result
        assert result.count("\\'") >= 2

    def test_post_action_escapes_quote(self):
        from labb.templatetags.lbr_tags import lbr_post_action

        result = lbr_post_action(self.PAYLOAD, tag="div")
        assert "a\\' + alert" in result
        assert "a' + alert" not in result

    def test_delete_action_escapes_quote(self):
        from labb.templatetags.lbr_tags import lbr_delete_action

        result = lbr_delete_action(self.PAYLOAD)
        assert "a\\' + alert" in result
        assert "a' + alert" not in result

    def test_backslash_in_href_is_doubled(self):
        from labb.templatetags.lbr_tags import lbr_get_action

        result = lbr_get_action("/a\\'b")
        assert r"/a\\\'b" in result  # \\ for the backslash, \' for the quote

    def test_plain_url_unchanged(self):
        from labb.templatetags.lbr_tags import lbr_get_action

        assert lbr_get_action("/todos/1/") == "@get('/todos/1/')"


# ---------------------------------------------------------------------------
# c-lbr.get component
# ---------------------------------------------------------------------------


class TestGetComponent(ComponentTestBase):
    def _render(self, attrs_str, slot=""):
        return self.render_template_string(
            f"{{% load lbr_tags %}}<c-lbr.get {attrs_str}>{slot}</c-lbr.get>"
        )

    def test_default_tag_is_div(self):
        assert "<div" in self._render('to="/url/"')

    def test_default_event_is_click(self):
        assert "data-on:click=" in self._render('to="/url/"')

    def test_action_in_data_on(self):
        html = self._render('to="/url/"')
        assert "@get('/url/')" in html

    def test_custom_tag(self):
        assert "<button" in self._render('to="/url/" tag="button"')

    def test_custom_on_event(self):
        assert "data-on:change=" in self._render('to="/url/" on="change"')

    def test_on_init_renders_data_init_not_data_on(self):
        html = self._render('to="/url/" on="init"')
        assert "data-init=" in html
        assert "data-on:init" not in html

    def test_on_init_action_value(self):
        html = self._render('to="/url/" on="init"')
        assert "@get('/url/')" in html

    def test_options_passed_to_action(self):
        html = self._render('to="/url/" options="{selector: \'#main\'}"')
        assert "{selector: '#main'}" in html

    def test_before_passed_to_action(self):
        html = self._render('to="/url/" before="log()"')
        assert "log()" in html

    def test_slot_rendered(self):
        html = self._render('to="/url/"', slot="Click me")
        assert "Click me" in html

    def test_passthrough_attrs(self):
        html = self._render('to="/url/" id="my-btn"')
        assert 'id="my-btn"' in html


# ---------------------------------------------------------------------------
# c-lbr.post component
# ---------------------------------------------------------------------------


class TestPostComponent(ComponentTestBase):
    def _render(self, attrs_str, slot=""):
        return self.render_template_string(
            f"{{% load lbr_tags %}}<c-lbr.post {attrs_str}>{slot}</c-lbr.post>"
        )

    def test_default_tag_is_form(self):
        assert "<form" in self._render('to="/url/"')

    def test_default_event_is_submit_and_prevents_native(self):
        # A real <form> must not let the browser's native submit race the @post.
        html = self._render('to="/url/"')
        assert "data-on:submit__prevent=" in html

    def test_form_default_posts_json(self):
        # Form mode posts signals as JSON (no contentType) so request.signals is populated.
        html = self._render('to="/url/"')
        assert "contentType" not in html
        assert "@post('/url/'" in html

    def test_non_form_tag_omits_content_type(self):
        html = self._render('to="/url/" tag="div"')
        assert "contentType" not in html
        assert "@post('/url/'" in html

    def test_on_init_renders_data_init(self):
        html = self._render('to="/url/" on="init"')
        assert "data-init=" in html
        assert "data-on:init" not in html

    def test_options_overrides_content_type(self):
        html = self._render('to="/url/" options="{contentType: \'json\'}"')
        assert "contentType: 'json'" in html

    def test_csrf_header_present_by_default(self):
        html = self._render('to="/url/"')
        assert "X-CSRFToken" in html
        assert "labbGetCSRFToken()" in html

    def test_no_csrf_opts_out(self):
        html = self._render('to="/url/" noCSRF')
        assert "X-CSRFToken" not in html

    def test_slot_rendered(self):
        html = self._render('to="/url/"', slot="<input>")
        assert "<input>" in html


# ---------------------------------------------------------------------------
# c-lbr.delete component
# ---------------------------------------------------------------------------


class TestDeleteComponent(ComponentTestBase):
    def _render(self, attrs_str, slot=""):
        return self.render_template_string(
            f"{{% load lbr_tags %}}<c-lbr.delete {attrs_str}>{slot}</c-lbr.delete>"
        )

    def test_default_tag_is_span(self):
        assert "<span" in self._render('to="/url/"')

    def test_default_event_is_click(self):
        assert "data-on:click=" in self._render('to="/url/"')

    def test_action_in_data_on(self):
        html = self._render('to="/url/"')
        assert "@delete('/url/'" in html

    def test_on_init_renders_data_init(self):
        html = self._render('to="/url/" on="init"')
        assert "data-init=" in html
        assert "data-on:init" not in html

    def test_confirm_wraps_action(self):
        html = self._render('to="/url/" confirm="Sure?"')
        assert "confirm('Sure?')" in html
        assert "@delete('/url/'" in html

    def test_options_in_action(self):
        html = self._render('to="/url/" options="{x: 1}"')
        assert "x: 1" in html

    def test_custom_tag(self):
        assert "<button" in self._render('to="/url/" tag="button"')

    def test_csrf_header_present_by_default(self):
        html = self._render('to="/url/"')
        assert "X-CSRFToken" in html
        assert "labbGetCSRFToken()" in html

    def test_no_csrf_opts_out(self):
        html = self._render('to="/url/" noCSRF')
        assert "X-CSRFToken" not in html

    def test_slot_rendered(self):
        html = self._render('to="/url/"', slot="Delete")
        assert "Delete" in html


class TestCSRFHelperAvailability(ComponentTestBase):
    """labbGetCSRFToken() must be defined whenever the reactive bundle loads.

    Mirrors the login-block page: c-lb.m.dependencies gets datastar=False, but a
    body c-lbr.post pushes datastar.js onto the stack. The helper must still emit
    (once) so the POST action's X-CSRFToken header can be evaluated.
    """

    def _render(self, slot):
        # Stacks are thread-local and cleared per real request (request_finished);
        # render_to_string skips that cycle, so clear manually for isolation.
        from labb.templatetags.lb_tags import _clear_stacks

        _clear_stacks()
        return self.render_template_string(
            "{% load lb_tags %}<c-lb.m.dependencies>" + slot + "</c-lb.m.dependencies>"
        )

    def test_helper_defined_when_body_pushes_datastar(self):
        html = self._render(
            '<c-lbr.post to="/submit/" tag="div" on="click"><button>Go</button></c-lbr.post>'
        )
        assert "function labbGetCSRFToken()" in html
        assert "X-CSRFToken" in html  # the action header
        # defined exactly once (no duplicate with any other block)
        assert html.count("function labbGetCSRFToken()") == 1

    def test_helper_absent_on_static_page(self):
        html = self._render("<p>static</p>")
        assert "function labbGetCSRFToken()" not in html


class TestTargetComponent(ComponentTestBase):
    def _render(self, attrs_str, slot=""):
        return self.render_template_string(
            f"{{% load lbr_tags %}}<c-lbr.target {attrs_str}>{slot}</c-lbr.target>"
        )

    def test_default_tag_is_div(self):
        assert "<div" in self._render('name="results"')

    def test_custom_tag(self):
        assert "<section" in self._render('name="results" tag="section"')

    def test_data_lbr_target_attr_set(self):
        html = self._render('name="todo-list"')
        assert 'data-lbr-target="todo-list"' in html

    def test_slot_rendered(self):
        html = self._render('name="results"', slot="<p>Content</p>")
        assert "<p>Content</p>" in html

    def test_passthrough_attrs(self):
        html = self._render('name="results" id="my-target" class="mt-4"')
        assert 'id="my-target"' in html
        assert 'class="mt-4"' in html

    def test_name_not_leaked_as_html_attr(self):
        html = self._render('name="results"')
        # name= should only appear as the value of data-lbr-target, not as a bare attr
        assert 'name="results"' not in html
