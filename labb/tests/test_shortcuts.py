import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory

from labb.shortcuts import (
    DEFAULT_THEME,
    THEME_SESSION_KEY,
    get_labb_theme,
    set_labb_theme,
)


@pytest.mark.django_db
class TestThemeShortcuts:
    """Test theme management shortcuts."""

    def setup_method(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()

    def _get_request_with_session(self):
        """Helper to create a request with session middleware."""
        request = self.factory.get("/")
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        return request

    def test_set_labb_theme_success(self):
        """Test setting theme successfully."""
        request = self._get_request_with_session()
        theme = "labb-dark"

        result = set_labb_theme(request, theme)

        assert result is True
        assert request.session[THEME_SESSION_KEY] == theme

    def test_set_labb_theme_multiple_times(self):
        """Test setting theme multiple times."""
        request = self._get_request_with_session()

        # Set initial theme
        set_labb_theme(request, "labb-light")
        assert get_labb_theme(request) == "labb-light"

        # Change theme
        set_labb_theme(request, "labb-dark")
        assert get_labb_theme(request) == "labb-dark"

    def test_get_labb_theme_default(self):
        """Test getting default theme when none is set."""
        request = self._get_request_with_session()

        theme = get_labb_theme(request)

        assert theme == DEFAULT_THEME

    def test_get_labb_theme_from_session(self):
        """Test getting theme from session."""
        request = self._get_request_with_session()
        expected_theme = "labb-dark"

        # Set theme in session
        request.session[THEME_SESSION_KEY] = expected_theme

        theme = get_labb_theme(request)

        assert theme == expected_theme

    def test_set_labb_theme_invalid_request(self):
        """Test setting theme with invalid request (no session)."""
        request = self.factory.get("/")
        # Don't add session middleware

        result = set_labb_theme(request, "labb-dark")

        assert result is False

    def test_theme_session_key_consistency(self):
        """Test that the session key is consistent."""
        request = self._get_request_with_session()
        theme = "labb-dark"

        set_labb_theme(request, theme)

        # Verify the theme is stored with the correct session key
        assert THEME_SESSION_KEY in request.session
        assert request.session[THEME_SESSION_KEY] == theme
