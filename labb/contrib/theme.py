"""
Theme management functionality for labb Django projects.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from labb.django_settings import get_default_theme

THEME_SESSION_KEY = "LABB_THEME"


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
    return request.session.get(THEME_SESSION_KEY, get_default_theme())


@require_http_methods(["POST"])
def set_theme_view(request):
    """
    AJAX view to set the theme in the session.

    This view can be included in Django projects to provide theme switching functionality.

    Expected POST data:
        theme: Theme name (e.g., 'labb-light', 'labb-dark')

    Returns:
        JsonResponse with success status and theme information
    """
    theme = request.POST.get("theme")

    if not theme:
        return JsonResponse(
            {"success": False, "error": "Theme parameter is required"}, status=400
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
