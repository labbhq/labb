"""Generator for Alpine.js component data files from component schemas."""

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional

from labb.components.registry import ComponentRegistry


def _is_valid_js_identifier(name: str) -> bool:
    """Return True if name can be used as an unquoted JS object key."""
    return bool(re.match(r"^[a-zA-Z_$][a-zA-Z0-9_$]*$", name))


def _js_key(name: str) -> str:
    """Return the name quoted if it contains dots or other non-identifier chars."""
    if _is_valid_js_identifier(name):
        return name
    return json.dumps(name)


def _js_filename(name: str) -> str:
    """'accordion.item' → 'accordion_item', 'file-input' → 'file_input'"""
    return re.sub(r"[.\-]", "_", name)


def _to_camel(name: str) -> str:
    """'accordion.item' → 'accordionItem', 'diff.item-1' → 'diffItem1'"""
    parts = re.split(r"[.\-_]", name)
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


# Components with hand-written Alpine logic — excluded from auto-generation.
# The generator will not overwrite these files.
CUSTOM_COMPONENTS = {
    "chart",
    "chart.instance",
    "chart.bar",
    "chart.line",
    "chart.pie",
    "chart.doughnut",
    "chart.radar",
    "chart.polar-area",
    "chart.scatter",
    "chart.bubble",
}


def generate_alpine_components(output_dir: Path, components: Optional[list] = None):
    """
    Generate Alpine.js component files from component schemas.
    Component JS files are written to output_dir/components/.

    Hand-written components (see CUSTOM_COMPONENTS) live in output_dir/custom/
    and are never touched by this generator.

    Args:
        output_dir: Root alpine directory (e.g. .../js/alpine/).
        components: List of component names to generate. If None, generates all
            and clears the components/ directory first for a clean slate.
    """
    registry = ComponentRegistry()
    components_dir = output_dir / "components"
    components_dir.mkdir(parents=True, exist_ok=True)

    # Full regeneration: wipe components/ first so stale files from removed
    # or renamed components don't linger. Partial regens must leave other
    # files alone.
    if components is None:
        for existing in components_dir.glob("*.js"):
            existing.unlink()

    all_components = registry.get_all_components()

    if components is not None:
        all_components = {k: v for k, v in all_components.items() if k in components}

    # Skip components with hand-written Alpine files.
    all_components = {
        k: v for k, v in all_components.items() if k not in CUSTOM_COMPONENTS
    }

    component_variables: Dict[str, Dict[str, str]] = {}

    for component_name, component_spec in all_components.items():
        _generate_component_file(components_dir, component_name, component_spec)
        variables = component_spec.get("variables", {})
        component_variables[component_name] = {
            var_name: var_spec.get("type", "string")
            for var_name, var_spec in variables.items()
            if "css_mapping" in var_spec
        }

    _generate_variables_json(output_dir, component_variables)


def _generate_component_file(
    components_dir: Path, component_name: str, component_spec: Dict[str, Any]
):
    """Generate a per-component Alpine data file inside the components/ subdirectory."""
    base_classes = component_spec.get("base_classes", [])
    variables = component_spec.get("variables", {})

    js_var = _to_camel(component_name)
    pascal = js_var[0].upper() + js_var[1:] if js_var else ""
    data_name = f"lb{pascal}Comp"
    filename = _js_filename(component_name)

    config_lines = [f"const {js_var}Config = {{"]
    config_lines.append(f"  baseClasses: {json.dumps(base_classes)},")
    config_lines.append("  variables: {")

    for var_name, var_spec in variables.items():
        if "css_mapping" not in var_spec:
            continue

        var_config: Dict[str, Any] = {}
        if "default" in var_spec:
            var_config["default"] = var_spec["default"]
        if "css_mapping" in var_spec:
            var_config["css_mapping"] = var_spec["css_mapping"]

        var_json = json.dumps(var_config, indent=4).replace("\n", "\n    ")
        key = _js_key(var_name)
        config_lines.append(f"    {key}: {var_json},")

    config_lines.append("  }")
    config_lines.append("};")

    content = (
        f"// {filename}.js\n\n"
        + "\n".join(config_lines)
        + f"\n\nwindow.lb.createComponent({js_var}Config, '{data_name}', '{component_name}');\n"
    )

    (components_dir / f"{filename}.js").write_text(content, encoding="utf-8")


def _generate_variables_json(
    output_dir: Path, component_variables: Dict[str, Dict[str, str]]
):
    """Write the lightweight component-variables.json lookup file."""
    output_file = output_dir / "component-variables.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(component_variables, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    import sys

    _components = sys.argv[1:] or None
    _output = Path(__file__).parents[2] / "static" / "labb" / "js" / "alpine"
    print(f"Generating Alpine components → {_output / 'components'}")
    generate_alpine_components(_output, _components)
    print("Done.")
