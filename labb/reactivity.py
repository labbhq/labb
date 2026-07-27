from datastar_py import ServerSentEventGenerator as _DS
from datastar_py.django import DatastarResponse as SSEResponse
from datastar_py.consts import ElementPatchMode

__all__ = [
    "SSEResponse",
    "patch_component",
    "patch_template",
    "patch_signal",
    "remove_element",
    "execute_script",
    "redirect",
]

execute_script = _DS.execute_script
redirect = _DS.redirect


def _css_selector(selector: str) -> str:
    """Convert @name shorthand to [data-lbr-target='name'] CSS selector."""
    if selector.startswith("@"):
        return f"[data-lbr-target='{selector[1:]}']"
    return selector


def patch_component(request, selector, component_name, mode=ElementPatchMode.OUTER, **kwargs):
    from django_cotton import render_component
    html = render_component(request, component_name, **kwargs)
    return _DS.patch_elements(html, selector=_css_selector(selector), mode=mode)


def patch_template(request, selector, template_name, context=None, mode=ElementPatchMode.OUTER):
    from django.template.loader import render_to_string
    html = render_to_string(template_name, context or {}, request)
    return _DS.patch_elements(html, selector=_css_selector(selector), mode=mode)


def patch_signal(signals: dict, only_if_missing: bool = False):
    return _DS.patch_signals(signals, only_if_missing=only_if_missing)


def remove_element(selector: str):
    return _DS.remove_elements(_css_selector(selector))
