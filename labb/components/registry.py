from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

SCHEMA_DIR = Path(__file__).parent / "schema"


class ComponentRegistry:
    """Registry for loading and managing component specifications from multiple schema files"""

    _instance = None
    _components = None

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
        for yaml_file in SCHEMA_DIR.glob("*.yaml"):
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                group = data.get("components", {})
                self._components.update(group)

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
            from pathlib import Path

            examples_dir = Path(__file__).parent.parent / "templates" / "lb-examples"
            if not examples_dir.exists():
                return []

            return [d.name for d in examples_dir.iterdir() if d.is_dir()]
        except Exception:
            return []

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
