"""Render test for the docs api_table reactive-prop marker.

The marker keeps the flashlight icon, but its tooltip must read
"Supports reactive $signals" (the dead `.x` wording is gone).

The labb test suite does not install `labbdocs`, so this builds a self-contained
Django engine that registers the two template libraries the api_table template
loads (`lb_tags`, `docs_tags`) and renders it against a real component spec
(`button`) that has css-mapped, reactive props.
"""

import os
from pathlib import Path

import labb
import labbdocs
from django.template import Context, Engine


def _render_api_table(component_name: str) -> str:
    labb_templates = Path(os.path.dirname(labb.__file__)) / "templates"
    labbdocs_templates = Path(os.path.dirname(labbdocs.__file__)) / "templates"
    engine = Engine(
        dirs=[str(labbdocs_templates), str(labb_templates)],
        libraries={
            "lb_tags": "labb.templatetags.lb_tags",
            "docs_tags": "labbdocs.templatetags.docs_tags",
        },
    )
    template = engine.get_template("cotton/lbdocs/api_table.html")
    return template.render(Context({"component_name": component_name}))


def test_api_table_reactive_marker_tooltip():
    html = _render_api_table("button")

    # New tooltip wording is present on the reactive marker.
    assert 'data-tip="Supports reactive $signals"' in html

    # The dead `.x` wording is gone.
    assert "Reactive via" not in html
    assert ".x\"" not in html

    # The flashlight icon marker is still emitted.
    assert "rmx.flashlight" in html
