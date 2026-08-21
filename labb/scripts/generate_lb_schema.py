#!/usr/bin/env python3
"""Generate labb/static/labb/js/lb-schema.js from component YAML schemas.

Reads all *.yaml files under labb/components/schema/, extracts base_classes and
css_mapping entries for each component, and emits a single JS file that sets up
window.lb._schemas and window.lb.classes().

Usage:
    poetry run python labb/scripts/generate_lb_schema.py
    task generate:lb-schema
"""

import json
import pathlib
import sys

import yaml

SCHEMA_DIR = pathlib.Path(__file__).parent.parent / "components" / "schema"
OUTPUT_FILE = (
    pathlib.Path(__file__).parent.parent / "static" / "labb" / "js" / "lb-schema.js"
)

_LB_CLASSES_FN = """\
window.lb.classes = function(name, props, extra) {
  var schema = window.lb._schemas[name];
  if (!schema) return extra || '';
  var classes = (schema.base || []).slice();
  for (var prop in props) {
    var map = schema[prop];
    if (map && map[props[prop]]) classes.push(map[props[prop]]);
  }
  if (extra) classes.push(extra);
  return classes.filter(Boolean).join(' ');
};"""


def _normalize_mapping(mapping: dict) -> dict:
    """Convert Python bool keys (from YAML true/false) to string keys."""
    result = {}
    for k, v in mapping.items():
        if k is True:
            str_key = "true"
        elif k is False:
            str_key = "false"
        else:
            str_key = str(k)
        result[str_key] = str(v) if v is not None else ""
    return result


def build_schemas() -> dict:
    """Read all YAML schema files and return the _schemas dict."""
    schemas = {}
    for yaml_file in sorted(SCHEMA_DIR.glob("*.yaml")):
        with open(yaml_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for comp_name, comp_spec in (data.get("components") or {}).items():
            if not comp_spec:
                continue
            variables = comp_spec.get("variables") or {}
            prop_mappings = {
                prop: _normalize_mapping(spec["css_mapping"])
                for prop, spec in variables.items()
                if spec and "css_mapping" in spec
            }
            if not prop_mappings:
                continue
            schemas[comp_name] = {
                "base": list(comp_spec.get("base_classes") or []),
                **prop_mappings,
            }
    return dict(sorted(schemas.items()))


def generate_js(schemas: dict) -> str:
    schemas_json = json.dumps(schemas, indent=2, ensure_ascii=False)
    return (
        "window.lb = window.lb || {};\n"
        f"window.lb._schemas = {schemas_json};\n"
        f"{_LB_CLASSES_FN}\n"
    )


def main() -> int:
    schemas = build_schemas()
    js = generate_js(schemas)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(js, encoding="utf-8")
    size = OUTPUT_FILE.stat().st_size
    print(f"Generated {OUTPUT_FILE} ({len(schemas)} components, {size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
