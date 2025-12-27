from labb.contrib.theme import (
    THEME_SESSION_KEY,
    get_labb_theme,
    set_labb_theme,
    set_theme_view,
)
from labb.django_settings import get_default_theme

DEFAULT_THEME = get_default_theme()


__all__ = [
    "DEFAULT_THEME",
    "get_labb_theme",
    "set_labb_theme",
    "set_theme_view",
    "THEME_SESSION_KEY",
]
