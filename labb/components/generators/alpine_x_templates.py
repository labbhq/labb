"""Generator for Alpine.js x.html component templates."""

from pathlib import Path
from typing import Optional

from labb.components.generators.alpine_components import _js_filename, _to_camel
from labb.components.registry import ComponentRegistry

# Components excluded from auto-generation — require custom Alpine logic
# beyond standard class management.
DEFAULT_EXCLUDE = {}


def _template_path_parts(name: str) -> list[str]:
    """
    Return underscore-normalised path parts for template lookup.
    'diff.item-1' → ['diff', 'item_1']
    'file-input'  → ['file_input']
    """
    return [seg.replace("-", "_") for seg in name.split(".")]


def _find_single_file(templates_dir: Path, parts: list[str]) -> Optional[Path]:
    """
    Return the existing single-file template path, or None if not found.
    Checks underscore variant (e.g. item_1.html).
    """
    if len(parts) == 1:
        candidate = templates_dir / f"{parts[0]}.html"
    else:
        candidate = templates_dir.joinpath(*parts[:-1]) / f"{parts[-1]}.html"
    return candidate if candidate.exists() else None


def _x_template(component_name: str) -> str:
    """Return the standard x.html content for a component."""
    js_var = _to_camel(component_name)
    pascal = js_var[0].upper() + js_var[1:] if js_var else ""
    data_name = f"lb{pascal}Comp"
    filename = _js_filename(component_name)
    dot_name = component_name  # cotton tag uses original name with dots/hyphens

    return (
        f"{{% load lb_tags %}}\n"
        f'<c-vars x-data="{data_name}" />\n'
        f"\n"
        f'{{% lb_push_stack name="components" path="labb/js/alpine/components/{filename}.js" %}}\n'
        f"\n"
        f"\n"
        f"<c-lb.{dot_name}\n"
        f'    x-data="{{{{ x_data }}}}"\n'
        f'    data-lb-defaults="{{% lb_alpine_defaults attrs "{component_name}" %}}"\n'
        f'    x-modelable="lbProps"\n'
        f'    ::class="compClasses"\n'
        f"    :attrs=attrs\n"
        f">\n"
        f"    {{{{ slot }}}}\n"
        f"</c-lb.{dot_name}>\n"
    )


def generate_alpine_x_templates(
    templates_dir: Path,
    components: Optional[list] = None,
    exclude: Optional[set] = None,
    restructure: bool = False,
):
    """
    Generate x.html Alpine templates for reactive components.

    Args:
        templates_dir: Path to templates/cotton/lb/
        components: Component names to process. If None, processes all reactive ones.
        exclude: Component names to skip. Defaults to DEFAULT_EXCLUDE.
        restructure: If True, convert single-file sub-components
                     (parent/name.html → parent/name/index.html).
    """
    registry = ComponentRegistry()
    all_components = registry.get_all_components()
    excluded = exclude if exclude is not None else DEFAULT_EXCLUDE

    if components is not None:
        all_components = {k: v for k, v in all_components.items() if k in components}

    reactive = {
        name: spec
        for name, spec in all_components.items()
        if any("css_mapping" in var for var in spec.get("variables", {}).values())
        and name not in excluded
    }

    generated, skipped, restructured = [], [], []

    for component_name in reactive:
        parts = _template_path_parts(component_name)
        comp_dir = templates_dir.joinpath(*parts)
        single_file = _find_single_file(templates_dir, parts)

        if not comp_dir.exists():
            if single_file and restructure:
                comp_dir.mkdir(parents=True, exist_ok=True)
                single_file.rename(comp_dir / "index.html")
                restructured.append(component_name)
            elif single_file:
                skipped.append(component_name)
                continue
            else:
                skipped.append(component_name)
                continue

        (comp_dir / "x.html").write_text(_x_template(component_name), encoding="utf-8")
        generated.append(component_name)

    return {"generated": generated, "skipped": skipped, "restructured": restructured}


if __name__ == "__main__":
    import sys

    _restructure = "--restructure" in sys.argv
    _components = [a for a in sys.argv[1:] if not a.startswith("--")] or None
    _templates = Path(__file__).parents[2] / "templates" / "cotton" / "lb"

    print(f"Generating x.html templates → {_templates}")
    if _restructure:
        print(
            "  --restructure: single-file sub-components will be converted to folders"
        )

    result = generate_alpine_x_templates(
        _templates, _components, restructure=_restructure
    )

    if result["restructured"]:
        print(f"\nRestructured ({len(result['restructured'])}):")
        for name in sorted(result["restructured"]):
            parts = _template_path_parts(name)
            print(f"  {'/'.join(parts)}.html → {'/'.join(parts)}/index.html")

    if result["generated"]:
        print(f"\nGenerated x.html ({len(result['generated'])}):")
        for name in sorted(result["generated"]):
            parts = _template_path_parts(name)
            print(f"  {'/'.join(parts)}/x.html")

    if result["skipped"]:
        print(f"\nSkipped ({len(result['skipped'])}):")
        for name in sorted(result["skipped"]):
            print(f"  {name}")

    print("\nDone.")
