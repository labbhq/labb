try:
    from django.conf import settings

    DJANGO_SETTINGS_AVAILABLE = True
except ImportError:
    DJANGO_SETTINGS_AVAILABLE = False

# Default settings
DEFAULT_SETTINGS = {
    "DEFAULT_THEME": "__system__",  # system's default theme
    "STACK_HELPERS": {},
    "REACTIVITY": {
        "QUERY_KEY": "lbr",      # query param name for syncQuery URL persistence
        "QUERY_ENCODING": "flat", # "base64" | "flat" | "json"
    },
}


def get_labb_setting(key, default=None):
    """
    Get a Labb setting from Django settings.

    Args:
        key (str): The setting key to retrieve
        default: Default value if setting is not found

    Returns:
        The setting value or default
    """
    if not DJANGO_SETTINGS_AVAILABLE:
        return DEFAULT_SETTINGS.get(key, default)

    # Get the LABB_SETTINGS object from Django settings
    labb_settings = getattr(settings, "LABB_SETTINGS", {})

    # Return the setting value, falling back to defaults
    return labb_settings.get(key, DEFAULT_SETTINGS.get(key, default))


def get_reactivity_setting(key, default=None):
    """Get a reactivity setting from LABB_SETTINGS['REACTIVITY'], falling back to defaults."""
    if not DJANGO_SETTINGS_AVAILABLE:
        return DEFAULT_SETTINGS["REACTIVITY"].get(key, default)

    labb_settings = getattr(settings, "LABB_SETTINGS", {})
    reactivity_settings = labb_settings.get("REACTIVITY", {})
    return reactivity_settings.get(key, DEFAULT_SETTINGS["REACTIVITY"].get(key, default))


def get_default_theme():
    """Get the default theme setting."""
    return get_labb_setting("DEFAULT_THEME")
