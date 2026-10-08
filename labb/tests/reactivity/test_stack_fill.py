"""
lb_load_stack emits where it sits, so a script pushed by a body component is
dropped when the stack is loaded in <head> — the placement labb documents.

StackFillMiddleware leaves a marker at the tag and fills late pushes into it
after the template renders. Without it, a late push warns rather than failing
silently in the browser.
"""

import pytest
from django.http import HttpResponse
from django.test import RequestFactory

from labb.middleware import StackFillMiddleware
from labb.templatetags.lb_tags import (
    LabbStackWarning,
    _clear_stacks,
    _set_late_fill,
)
from labb.tests.components.test_base import ComponentTestBase

HEAD_THEN_BODY = (
    "{% load lb_tags %}"
    "<html><head><c-lb.m.dependencies datastar /></head>"
    '<body><c-lb.badge variant="$status:neutral">Hi</c-lb.badge></body></html>'
)


class TestLatePushWithoutMiddleware(ComponentTestBase):
    def setup_method(self):
        super().setup_method()
        _clear_stacks()

    def test_late_push_warns_and_is_dropped(self):
        with pytest.warns(LabbStackWarning, match="lb-schema.js"):
            html = self.render_template_string(HEAD_THEN_BODY)
        # lb.classes is emitted but its helper never reached the page.
        assert "lb.classes(" in html
        assert "lb-schema.js" not in html

    def test_no_marker_is_left_behind(self):
        self.render_template_string(HEAD_THEN_BODY)
        assert "labb-stack:" not in self.render_template_string(HEAD_THEN_BODY)


class TestLatePushWithMiddleware(ComponentTestBase):
    def setup_method(self):
        super().setup_method()
        _clear_stacks()

    def _run(self, template):
        """Render inside a request cycle with the middleware installed."""
        holder = {}

        def get_response(request):
            _set_late_fill(True)
            holder["html"] = self.render_template_string(template)
            return HttpResponse(holder["html"], content_type="text/html")

        mw = StackFillMiddleware(get_response)
        return mw(RequestFactory().get("/")).content.decode()

    def test_late_push_is_filled_in(self):
        body = self._run(HEAD_THEN_BODY)
        assert "lb-schema.js" in body
        assert "lb.classes(" in body

    def test_marker_is_consumed(self):
        assert "labb-stack:" not in self._run(HEAD_THEN_BODY)

    def test_does_not_duplicate_what_the_tag_already_emitted(self):
        body = self._run(HEAD_THEN_BODY)
        assert body.count("vendor/datastar.js") == 1
