"""Components reader — one search row per component doc page.

Source is the generated `doc_configs/ui.yaml` (its top-level `pages` dict), the
same config the docs build consumes. A page is a component page when its
frontmatter has `doc_layout: component` (or a `component` key). Keywords are
enriched from the live component registry (`labb.components`) with prop names
and enum variant values, so components are findable by capability, not just
name. `c-lbr.*` reactivity component pages come through the same path (their
folder gives `category=reactivity`); nothing special-cases them.
"""

import re
from pathlib import Path
from typing import Iterable

import yaml
from django.conf import settings

from ..models import SearchDocument


def _ui_config_path() -> Path:
    """The ui.yaml the docs build uses (from LABB_DOCS), with a BASE_DIR fallback."""
    try:
        return Path(settings.LABB_DOCS["types"]["ui"]["config"])
    except (AttributeError, KeyError, TypeError):
        return Path(settings.BASE_DIR) / "doc_configs" / "ui.yaml"


def _category_from_file_path(file_path: str) -> str:
    """`1_actions/button.md` -> `actions`; strips a leading `N_` from the folder."""
    if not file_path:
        return ""
    folder = Path(file_path).parent.name or ""
    return re.sub(r"^\d+_", "", folder)


def _daisy_name(frontmatter: dict) -> str:
    """The registry key for a page — its daisyUI component name."""
    name = frontmatter.get("daisy_ui_component_name")
    if name:
        return str(name)
    # Fall back to the bare tag name: `c-lb.button` / `c-lbr.get` -> `button`/`get`.
    component = frontmatter.get("component") or ""
    return component.split(".")[-1]


def _enrich_keywords(frontmatter: dict) -> list[str]:
    """Prop names + enum variant values from the live component registry."""
    try:
        from labb.components import get_all_components
    except Exception:
        return []

    registry = get_all_components() or {}
    spec = registry.get(_daisy_name(frontmatter))
    if not isinstance(spec, dict):
        return []

    extra: list[str] = []
    for prop_name, prop in (spec.get("variables") or {}).items():
        extra.append(str(prop_name))
        if isinstance(prop, dict):
            for value in prop.get("values", []) or []:
                if value:
                    extra.append(str(value))
    return extra


class ComponentsReader:
    type = SearchDocument.TYPE_COMPONENT

    def read(self) -> Iterable[dict]:
        config = _ui_config_path()
        if not config.exists():
            return

        data = yaml.safe_load(config.read_text()) or {}
        pages = data.get("pages") or {}

        for url, page in pages.items():
            frontmatter = (page or {}).get("frontmatter") or {}
            is_component = (
                frontmatter.get("doc_layout") == "component"
                or "component" in frontmatter
            )
            if not is_component:
                continue

            tag = frontmatter.get("component") or ""
            keyword_parts = [
                (frontmatter.get("keywords") or "").strip(),
                tag,
                *_enrich_keywords(frontmatter),
            ]
            keywords = " ".join(part for part in keyword_parts if part)

            yield {
                "type": self.type,
                "title": frontmatter.get("title") or "",
                "url": url,
                "category": _category_from_file_path(
                    (page or {}).get("file_path", "")
                ).replace("_", " "),
                "summary": frontmatter.get("description") or "",
                "keywords": keywords,
                "metadata": {
                    "component": tag,
                    "daisy": frontmatter.get("daisy_ui_component_name") or "",
                    "icon": frontmatter.get("icon") or "",
                },
            }
