from unittest.mock import MagicMock

import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory

from labb.contrib.theme import THEME_SESSION_KEY, get_labb_theme, set_labb_theme
from labb.django_settings import get_default_theme


@pytest.fixture
def factory():
    return RequestFactory()


@pytest.fixture
def request_with_session(factory):
    request = factory.get("/")
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()
    return request


@pytest.fixture
def request_without_session(factory):
    return factory.get("/")


class TestGetLabbTheme:
    def test_returns_default_when_no_session_key(self, request_with_session):
        theme = get_labb_theme(request_with_session)
        assert theme == get_default_theme()

    def test_returns_stored_theme(self, request_with_session):
        request_with_session.session[THEME_SESSION_KEY] = "labb-dark"
        assert get_labb_theme(request_with_session) == "labb-dark"

    def test_returns_default_when_session_missing(self, request_without_session):
        theme = get_labb_theme(request_without_session)
        assert theme == get_default_theme()

    def test_returns_default_when_session_attr_is_none(self, request_without_session):
        request_without_session.session = None
        theme = get_labb_theme(request_without_session)
        assert theme == get_default_theme()


class TestSetLabbTheme:
    def test_sets_theme_in_session(self, request_with_session):
        result = set_labb_theme(request_with_session, "labb-dark")
        assert result is True
        assert request_with_session.session[THEME_SESSION_KEY] == "labb-dark"

    def test_returns_false_when_session_missing(self, request_without_session):
        result = set_labb_theme(request_without_session, "labb-dark")
        assert result is False

    def test_returns_false_on_exception(self, request_with_session):
        request_with_session.session = MagicMock()
        request_with_session.session.__setitem__.side_effect = Exception("fail")
        result = set_labb_theme(request_with_session, "labb-dark")
        assert result is False


class TestLabbThemeTagRendering:
    """`{% labb_theme %}` must emit a *usable* data-theme attribute.

    Regression: it returned a plain str, which Django autoescaped into
    data-theme=&quot;x&quot;. The attribute value then carried literal quote
    characters and [data-theme="x"] never matched, so a persisted theme silently
    failed to apply on page load, sitewide.
    """

    def _render(self, request):
        from django.template import Context, Template

        return Template("{% load lb_tags %}<html {% labb_theme %}>").render(
            Context({"request": request})
        )

    def test_theme_attribute_is_not_escaped(self, request_with_session):
        set_labb_theme(request_with_session, "labb-dark")
        html = self._render(request_with_session)
        assert 'data-theme="labb-dark"' in html
        assert "&quot;" not in html

    def test_system_theme_emits_no_attribute(self, request_with_session):
        set_labb_theme(request_with_session, "__system__")
        assert "data-theme" not in self._render(request_with_session)

    def test_theme_value_is_still_escaped(self, request_with_session):
        # The theme is unvalidated session input; the quotes are markup but the
        # value must not be able to break out of the attribute.
        set_labb_theme(request_with_session, 'x" onload="alert(1)')
        html = self._render(request_with_session)
        assert 'onload="alert(1)' not in html
