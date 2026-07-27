"""Drift guard for the committed labb/static/labb/js/lb-schema.js artifact.

lb-schema.js is generated from the component YAML schemas by
labb/scripts/generate_lb_schema.py and sits in the runtime path (reactive
data-attr:class bindings resolve classes through window.lb.classes() from it).
It is regenerated only by the lb-schema-generate pre-commit hook, so a commit
made with --no-verify can ship a stale file. This test fails when the committed
file no longer matches the schemas.
"""

import importlib.util
from pathlib import Path

import labb

# Anchored on the labb package, not this file's depth in labb/tests/.
_SCRIPT = Path(labb.__file__).resolve().parent / "scripts" / "generate_lb_schema.py"


def _load_generator():
    spec = importlib.util.spec_from_file_location("generate_lb_schema", _SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_lb_schema_js_matches_component_schemas():
    gen = _load_generator()
    expected = gen.generate_js(gen.build_schemas())
    actual = gen.OUTPUT_FILE.read_text(encoding="utf-8")
    assert actual == expected, (
        "labb/static/labb/js/lb-schema.js is out of sync with the component YAML "
        "schemas. Regenerate it with:  task lb-schema:generate"
    )
