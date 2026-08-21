"""Template access to the browse shortcuts (so the global palette component,
which has no search view behind it, reuses one source of truth)."""

from django import template

from ..conf import category_shortcuts as _category_shortcuts

register = template.Library()


@register.simple_tag
def category_shortcuts():
    return _category_shortcuts()
