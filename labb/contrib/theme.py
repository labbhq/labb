"""
Theme management functionality for labb Django projects.
"""

import re

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from labb.django_settings import get_default_theme

THEME_SESSION_KEY = "LABB_THEME"

# No registry to check against: themes are declared per project.
THEME_NAME_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def is_valid_theme_name(theme):
    """True if `theme` is shaped like a theme name (or the `__system__` sentinel)."""
    return bool(theme) and bool(THEME_NAME_RE.match(theme))


def set_labb_theme(request, theme):
    """
    Set the theme value in the request session.

    Args:
        request: Django request object
        theme (str): Theme name to set (e.g., 'labb-light', 'labb-dark')

    Returns:
        bool: True if theme was set successfully, False otherwise
    """
    try:
        request.session[THEME_SESSION_KEY] = theme
        return True
    except Exception:
        return False


def get_labb_theme(request):
    """
    Get the theme value from the request session.

    Args:
        request: Django request object

    Returns:
        str: Current theme name, or DEFAULT_THEME if none is set
    """
    session = getattr(request, "session", None)
    if session is None:
        return get_default_theme()
    return session.get(THEME_SESSION_KEY, get_default_theme())


@require_http_methods(["POST"])
def set_theme_view(request):
    """
    AJAX view to set the theme in the session.

    This view can be included in Django projects to provide theme switching functionality.

    Expected POST data:
        theme: Theme name (e.g., 'labb-light', 'labb-dark'). Must match
            THEME_NAME_RE; anything else is rejected with 400.

    Returns:
        JsonResponse with success status and theme information
    """
    theme = request.POST.get("theme")

    if not theme:
        return JsonResponse(
            {"success": False, "error": "Theme parameter is required"}, status=400
        )

    if not is_valid_theme_name(theme):
        return JsonResponse(
            {"success": False, "error": "Invalid theme name"}, status=400
        )

    # Set the theme in session
    success = set_labb_theme(request, theme)

    if success:
        return JsonResponse(
            {"success": True, "theme": theme, "current_theme": get_labb_theme(request)}
        )
    else:
        return JsonResponse(
            {"success": False, "error": "Failed to set theme"}, status=500
        )
