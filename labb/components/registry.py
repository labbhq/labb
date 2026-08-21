from itertools import permutations
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

SCHEMA_DIR = Path(__file__).parent / "schema"

SHARED_SCHEMA = SCHEMA_DIR / "_shared.yaml"

# Guide-only examples live under lb-examples/guide/<topic>/. They are not
# components, so the component listings skip this directory.
GUIDE_EXAMPLES_DIR = "guide"


def _load_prop_groups() -> Dict[str, Any]:
    """Load the shared prop group definitions from schema/_shared.yaml."""
    if not SHARED_SCHEMA.exists():
        return {}
    with open(SHARED_SCHEMA, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("prop_groups", {}) or {}


def _modifier_variables(
    trigger: str,
    modifiers: List[str],
    group_modifiers: Dict[str, str],
    combine: bool,
) -> Dict[str, Any]:
    """Variable entries for one component's dot-notation modifiers.

    A combining group accepts every ordering, so fill and end also give
    `icon.fill.end` and `icon.end.fill` - what parse_icon parses.
    """
    variables: Dict[str, Any] = {}

    def add(parts: List[str], description: str):
        variables[trigger + "." + ".".join(parts)] = {
            "type": "modifier",
            "default": "",
            "description": description,
            "required": False,
            "modifier_of": trigger,
        }

    for modifier in modifiers:
        add([modifier], group_modifiers.get(modifier, ""))

    if combine and len(modifiers) > 1:
        for size in range(2, len(modifiers) + 1):
            for combo in permutations(modifiers, size):
                combined = " and ".join(f"{trigger}.{m}" for m in combo)
                add(list(combo), f"Combines {combined}")

    return variables


def apply_prop_groups(
    spec: Dict[str, Any], prop_groups: Dict[str, Any]
) -> Dict[str, Any]:
    """Merge shared prop groups into a component spec.

    A component opts in by declaring the group's trigger variable (`icon`); the
    group supplies the rest of the attribute names it accepts, so readers of
    `variables` see the full set. Component declarations win over inherited ones.
    """
    for group_name, group in (prop_groups or {}).items():
        trigger = group.get("trigger", group_name)
        declared = spec.get("variables") or {}
        if trigger not in declared:
            continue

        own = declared[trigger] or {}
        modifiers = own.get("dot_modifiers") or []
        if isinstance(modifiers, dict):  # {name: description} form
            modifiers = list(modifiers)

        group_variables = dict(group.get("variables") or {})
        # Modifiers first so `inspect` lists them directly under the trigger.
        inherited = _modifier_variables(
            trigger,
            modifiers,
            group.get("modifiers") or {},
            bool(group.get("combine")),
        )
        inherited[trigger] = group_variables.pop(trigger, {})
        inherited.update(group_variables)

        variables: Dict[str, Any] = {}
        for name, var_spec in declared.items():
            if name == trigger:
                merged = {**inherited.pop(trigger, {}), **(own or {})}
                merged.pop("dot_modifiers", None)
                variables[trigger] = merged
                for extra_name, extra_spec in inherited.items():
                    variables.setdefault(extra_name, extra_spec)
            else:
                variables[name] = var_spec

        # Re-apply: a declaration after the trigger beats the inherited entry.
        for name, var_spec in declared.items():
            if name != trigger:
                variables[name] = var_spec

        spec = {**spec, "variables": variables}

    return spec


class ComponentRegistry:
    """Registry for loading and managing component specifications from multiple schema files"""

    _instance = None
    _components = None
    _prop_groups = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._components is None:
            self._load_components()

    def _load_components(self):
        """Load and merge components from all YAML files in the schema directory"""
        self._components = {}
        self._prop_groups = _load_prop_groups()
        for yaml_file in SCHEMA_DIR.glob("*.yaml"):
            if yaml_file == SHARED_SCHEMA:
                continue
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                group = data.get("components", {})
                self._components.update(group)
        for name, spec in self._components.items():
            self._components[name] = apply_prop_groups(spec, self._prop_groups)

    def get_prop_groups(self) -> Dict[str, Any]:
        """Get the shared prop group definitions"""
        return dict(self._prop_groups)

    def get_component(self, name: str) -> Optional[Dict[str, Any]]:
        """Get component specification by name"""
        return self._components.get(name)

    def get_all_components(self) -> Dict[str, Any]:
        """Get all component specifications"""
        return self._components.copy()

    def get_component_names(self) -> List[str]:
        """Get list of all component names"""
        return list(self._components.keys())

    def get_component_variables(self, name: str) -> Dict[str, Any]:
        """Get variables specification for a component"""
        component = self.get_component(name)
        return component.get("variables", {}) if component else {}

    def get_component_events(self, name: str) -> List[Dict[str, Any]]:
        """Get events specification for a component"""
        component = self.get_component(name)
        return component.get("events", []) if component else []

    def get_component_base_classes(self, name: str) -> List[str]:
        """Get base CSS classes for a component"""
        component = self.get_component(name)
        return component.get("base_classes", []) if component else []

    def get_example_raw_content(self, path: str) -> Optional[str]:
        """Get raw template content for an example by path (e.g., 'badge/basic')"""
        try:
            from pathlib import Path

            # Get path relative to this file (go up to labb/ then to templates/)
            template_path = (
                Path(__file__).parent.parent
                / "templates"
                / "lb-examples"
                / f"{path}.html"
            )

            if template_path.exists():
                with open(template_path, "r", encoding="utf-8") as f:
                    return f.read()

            return None
        except Exception:
            return None

    def get_available_components_with_examples(self) -> List[str]:
        """Get list of components that have examples by scanning the file system"""
        try:
            examples_dir = self._examples_dir()
            if not examples_dir.exists():
                return []

            return [
                d.name
                for d in examples_dir.iterdir()
                if d.is_dir() and d.name != GUIDE_EXAMPLES_DIR
            ]
        except Exception:
            return []

    def get_guide_example_topics(self) -> Dict[str, List[str]]:
        """Guide-only examples, keyed by topic.

        These are not components, so they stay out of the component listings.
        Reference them as `guide/<topic>/<name>`.
        """
        try:
            guide_dir = self._examples_dir() / GUIDE_EXAMPLES_DIR
            if not guide_dir.exists():
                return {}

            return {
                topic.name: sorted(f.stem for f in topic.glob("*.html"))
                for topic in sorted(guide_dir.iterdir())
                if topic.is_dir()
            }
        except Exception:
            return {}

    @staticmethod
    def _examples_dir() -> Path:
        return Path(__file__).parent.parent / "templates" / "lb-examples"

    def get_component_example_names(self, component_name: str) -> List[str]:
        """Get list of example names for a component by scanning the file system"""
        try:
            from pathlib import Path

            component_dir = (
                Path(__file__).parent.parent
                / "templates"
                / "lb-examples"
                / component_name
            )

            if not component_dir.exists():
                return []

            # Get all .html files and return their names without extension
            return [f.stem for f in component_dir.glob("*.html")]
        except Exception:
            return []

    def get_example_title_from_name(self, example_name: str) -> str:
        """Convert example filename to a readable title"""
        # Convert "with-icons" to "With Icons", "basic" to "Basic", etc.
        return example_name.replace("-", " ").replace("_", " ").title()


# Convenience functions for easy access
def load_component_spec(name: str) -> Optional[Dict[str, Any]]:
    """Load component specification by name"""
    registry = ComponentRegistry()
    return registry.get_component(name)


def get_all_components() -> Dict[str, Any]:
    """Get all component specifications"""
    registry = ComponentRegistry()
    return registry.get_all_components()


def get_component_names() -> List[str]:
    """Get list of all component names"""
    registry = ComponentRegistry()
    return registry.get_component_names()
