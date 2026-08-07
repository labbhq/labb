"""Rendering helpers available to a block's views.py."""

from django.http import HttpRequest
from django.shortcuts import render as _django_render


def render_page(
    request: HttpRequest, template: str, context: dict | None = None, title: str = ""
):
    """Render a pages/ block template wrapped in c-lbb.page."""
    ctx = dict(context or {})
    ctx.setdefault("title", title)
    ctx["lbb_page_tpl"] = template
    return _django_render(request, "cotton/lbb/block_page.html", ctx)
