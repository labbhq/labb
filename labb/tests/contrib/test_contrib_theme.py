from unittest.mock import MagicMock

import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory

from labb.contrib.theme import (
    THEME_SESSION_KEY,
    get_labb_theme,
    is_valid_theme_name,
    set_labb_theme,
    set_theme_view,
)
from labb.django_settings import get_default_theme
from labb.tests.components.test_base import ComponentTestBase


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


class TestSetThemeView:
    """The view is the only path that writes attacker-reachable input into the
    session, and that value ends up in data-theme and in a CSS selector."""

    def _post(self, factory, data):
        request = factory.post("/set-theme/", data)
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        return request

    @pytest.mark.parametrize(
        "theme", ["labb-dark", "light", "__system__", "my_theme_2"]
    )
    def test_accepts_theme_names(self, factory, theme):
        request = self._post(factory, {"theme": theme})
        response = set_theme_view(request)
        assert response.status_code == 200
        assert request.session[THEME_SESSION_KEY] == theme

    @pytest.mark.parametrize(
        "theme",
        [
            'x" onload="alert(1)',
            "dark]:hover",
            "a b",
            "../../etc/passwd",
            "x" * 65,
        ],
    )
    def test_rejects_anything_else(self, factory, theme):
        request = self._post(factory, {"theme": theme})
        response = set_theme_view(request)
        assert response.status_code == 400
        assert THEME_SESSION_KEY not in request.session

    def test_missing_theme_still_400s(self, factory):
        request = self._post(factory, {})
        assert set_theme_view(request).status_code == 400


class TestIsValidThemeName:
    def test_empty_is_invalid(self):
        assert is_valid_theme_name("") is False
        assert is_valid_theme_name(None) is False


class TestThemeEndpointScript(ComponentTestBase):
    """`<c-lb.m.dependencies setThemeEndpoint="...">` writes the endpoint into a
    <script>. A script is a raw-text element, so an interpolated `{{ }}` there is
    escaped into entities the browser never decodes: it corrupts the value and
    guards nothing. The endpoint has to arrive as JSON instead."""

    def _render(self):
        return self.render_component(
            "m.dependencies",
            noGlobalCSS=True,
            setThemeEndpoint="/set-theme/",
        )

    def test_endpoint_travels_as_json(self):
        html = self._render()
        assert 'id="labb-set-theme-endpoint"' in html
        assert '"/set-theme/"' in html
        assert "fetch(LABB_THEME_ENDPOINT" in html
        assert "fetch('/set-theme/'" not in html

    def test_theme_value_is_escaped_into_the_radio_selector(self):
        assert "CSS.escape(currentTheme)" in self._render()


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
