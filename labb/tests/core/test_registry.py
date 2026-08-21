from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest
import yaml

from labb.components.registry import (
    ComponentRegistry,
    get_all_components,
    get_component_names,
    load_component_spec,
)


class TestComponentRegistry:
    """Test the ComponentRegistry class"""

    def test_singleton_pattern(self):
        """Test that ComponentRegistry is a singleton"""
        registry1 = ComponentRegistry()
        registry2 = ComponentRegistry()

        assert registry1 is registry2
        assert id(registry1) == id(registry2)

    @patch("labb.components.registry.SCHEMA_DIR")
    def test_load_components_success(self, mock_schema_dir, temp_dir):
        """Test successful loading of components from YAML files"""
        # Create mock schema directory
        mock_schema_dir.glob.return_value = ["test.yaml"]

        # Mock YAML content
        yaml_content = """
        components:
          button:
            template: "lb/button.html"
            description: "Button component"
            variables:
              variant:
                type: enum
                values: [primary, secondary]
          drawer:
            template: "lb/drawer.html"
            description: "Drawer component"
        """

        # Mock file operations
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("yaml.safe_load", return_value=yaml.safe_load(yaml_content)):
                registry = ComponentRegistry()

                # Force reload by clearing the components
                registry._components = None
                registry._load_components()

                components = registry.get_all_components()
                assert "button" in components
                assert "drawer" in components
                assert components["button"]["template"] == "lb/button.html"
                assert components["drawer"]["description"] == "Drawer component"

    @patch("labb.components.registry.SCHEMA_DIR")
    def test_load_components_empty_yaml(self, mock_schema_dir):
        """Test loading components from empty YAML file"""
        mock_schema_dir.glob.return_value = []

        with patch("builtins.open", mock_open(read_data="")):
            with patch("yaml.safe_load", return_value=None):
                registry = ComponentRegistry()
                registry._components = None
                registry._load_components()

                components = registry.get_all_components()
                assert components == {}

    @patch("labb.components.registry.SCHEMA_DIR")
    def test_load_components_file_error(self, mock_schema_dir):
        """Test that file reading errors are raised"""
        mock_schema_dir.glob.return_value = ["test.yaml"]
        with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
            registry = ComponentRegistry()
            registry._components = None
            with pytest.raises(FileNotFoundError):
                registry._load_components()

    @patch("labb.components.registry.SCHEMA_DIR")
    def test_load_components_yaml_error(self, mock_schema_dir):
        """Test that YAML parsing errors are raised"""
        mock_schema_dir.glob.return_value = ["test.yaml"]
        with patch("builtins.open", mock_open(read_data="invalid yaml")):
            with patch("yaml.safe_load", side_effect=yaml.YAMLError("Invalid YAML")):
                registry = ComponentRegistry()
                registry._components = None
                with pytest.raises(yaml.YAMLError):
                    registry._load_components()

    def test_get_component_existing(self):
        """Test getting an existing component"""
        registry = ComponentRegistry()
        registry._components = {
            "button": {"template": "lb/button.html", "description": "Button"}
        }

        component = registry.get_component("button")
        assert component == {"template": "lb/button.html", "description": "Button"}

    def test_get_component_nonexistent(self):
        """Test getting a non-existent component"""
        registry = ComponentRegistry()
        registry._components = {"button": {"template": "lb/button.html"}}

        component = registry.get_component("nonexistent")
        assert component is None

    def test_get_all_components(self):
        """Test getting all components"""
        registry = ComponentRegistry()
        test_components = {
            "button": {"template": "lb/button.html"},
            "drawer": {"template": "lb/drawer.html"},
        }
        registry._components = test_components

        components = registry.get_all_components()
        assert components == test_components
        # Ensure it returns a copy, not the original
        assert components is not test_components

    def test_get_component_names(self):
        """Test getting component names"""
        registry = ComponentRegistry()
        registry._components = {
            "button": {"template": "lb/button.html"},
            "drawer": {"template": "lb/drawer.html"},
        }

        names = registry.get_component_names()
        assert set(names) == {"button", "drawer"}

    def test_get_component_variables_existing(self):
        """Test getting variables for existing component"""
        registry = ComponentRegistry()
        registry._components = {
            "button": {
                "variables": {
                    "variant": {"type": "enum", "values": ["primary", "secondary"]}
                }
            }
        }

        variables = registry.get_component_variables("button")
        assert variables == {
            "variant": {"type": "enum", "values": ["primary", "secondary"]}
        }

    def test_get_component_variables_nonexistent(self):
        """Test getting variables for non-existent component"""
        registry = ComponentRegistry()
        registry._components = {}

        variables = registry.get_component_variables("nonexistent")
        assert variables == {}

    def test_get_component_variables_no_variables(self):
        """Test getting variables for component without variables"""
        registry = ComponentRegistry()
        registry._components = {"button": {"template": "lb/button.html"}}

        variables = registry.get_component_variables("button")
        assert variables == {}

    def test_get_component_events_existing(self):
        """Test getting events for existing component"""
        registry = ComponentRegistry()
        registry._components = {
            "button": {
                "events": [
                    {"name": "click", "description": "Button clicked"},
                    {"name": "hover", "description": "Button hovered"},
                ]
            }
        }

        events = registry.get_component_events("button")
        assert events == [
            {"name": "click", "description": "Button clicked"},
            {"name": "hover", "description": "Button hovered"},
        ]

    def test_get_component_events_nonexistent(self):
        """Test getting events for non-existent component"""
        registry = ComponentRegistry()
        registry._components = {}

        events = registry.get_component_events("nonexistent")
        assert events == []

    def test_get_component_events_no_events(self):
        """Test getting events for component without events"""
        registry = ComponentRegistry()
        registry._components = {"button": {"template": "lb/button.html"}}

        events = registry.get_component_events("button")
        assert events == []

    def test_get_component_base_classes_existing(self):
        """Test getting base classes for existing component"""
        registry = ComponentRegistry()
        registry._components = {"button": {"base_classes": ["btn", "btn-primary"]}}

        base_classes = registry.get_component_base_classes("button")
        assert base_classes == ["btn", "btn-primary"]

    def test_get_component_base_classes_nonexistent(self):
        """Test getting base classes for non-existent component"""
        registry = ComponentRegistry()
        registry._components = {}

        base_classes = registry.get_component_base_classes("nonexistent")
        assert base_classes == []

    def test_get_component_base_classes_no_base_classes(self):
        """Test getting base classes for component without base classes"""
        registry = ComponentRegistry()
        registry._components = {"button": {"template": "lb/button.html"}}

        base_classes = registry.get_component_base_classes("button")
        assert base_classes == []


class TestConvenienceFunctions:
    """Test the convenience functions"""

    @patch("labb.components.registry.ComponentRegistry")
    def test_load_component_spec(self, mock_registry_class):
        """Test load_component_spec function"""
        mock_registry = Mock()
        mock_registry.get_component.return_value = {"template": "lb/button.html"}
        mock_registry_class.return_value = mock_registry

        result = load_component_spec("button")

        assert result == {"template": "lb/button.html"}
        mock_registry.get_component.assert_called_once_with("button")

    @patch("labb.components.registry.ComponentRegistry")
    def test_get_all_components(self, mock_registry_class):
        """Test get_all_components function"""
        mock_registry = Mock()
        test_components = {"button": {"template": "lb/button.html"}}
        mock_registry.get_all_components.return_value = test_components
        mock_registry_class.return_value = mock_registry

        result = get_all_components()

        assert result == test_components
        mock_registry.get_all_components.assert_called_once()

    @patch("labb.components.registry.ComponentRegistry")
    def test_get_component_names(self, mock_registry_class):
        """Test get_component_names function"""
        mock_registry = Mock()
        mock_registry.get_component_names.return_value = ["button", "drawer"]
        mock_registry_class.return_value = mock_registry

        result = get_component_names()

        assert result == ["button", "drawer"]
        mock_registry.get_component_names.assert_called_once()


class TestIconPropGroup:
    """The icon prop group is declared once in schema/_shared.yaml and merged
    into every component that declares `icon`."""

    TEMPLATE_ROOT = Path(__file__).parent.parent.parent / "templates" / "cotton"

    @staticmethod
    def icon_components():
        registry = ComponentRegistry()
        return {
            name: registry.get_component(name)
            for name in registry.get_component_names()
            if "icon" in (registry.get_component_variables(name) or {})
        }

    def template_source(self, spec):
        return (self.TEMPLATE_ROOT / spec["template"]).read_text(encoding="utf-8")

    def test_full_attribute_set_is_reported(self):
        """A component supporting both modifiers reports every accepted form"""
        variables = ComponentRegistry().get_component_variables("button")

        assert {
            "icon",
            "icon.class",
            "icon.fill",
            "icon.end",
            "icon.fill.end",
            "icon.end.fill",
        } <= set(variables)

    def test_modifiers_are_marked_as_such(self):
        """Modifier entries name the prop they modify"""
        variables = ComponentRegistry().get_component_variables("button")

        assert variables["icon.fill"]["modifier_of"] == "icon"
        assert variables["icon.fill"]["type"] == "modifier"
        assert "modifier_of" not in variables["icon"]

    def test_unsupported_modifiers_are_not_reported(self):
        """`end` is only declared where the template places the icon at the end"""
        variables = ComponentRegistry().get_component_variables("alert")

        assert "icon.fill" in variables
        assert "icon.end" not in variables
        assert "icon.fill.end" not in variables

    def test_component_overrides_win_over_the_group(self):
        """A component may describe its own icon prop"""
        variables = ComponentRegistry().get_component_variables("avatar")

        assert variables["icon"]["description"] == (
            "Icon name for placeholder avatars (alternative to initials)"
        )
        assert variables["icon"]["type"] == "string"

    def test_every_parse_icon_template_opts_in(self):
        """Any template calling parse_icon belongs to a component declaring `icon`"""
        declared = {spec["template"] for spec in self.icon_components().values()}

        using_parse_icon = {
            path.relative_to(self.TEMPLATE_ROOT).as_posix()
            for path in self.TEMPLATE_ROOT.rglob("*.html")
            if "{% parse_icon" in path.read_text(encoding="utf-8")
        }

        assert using_parse_icon == declared

    def test_declared_modifiers_match_the_templates(self):
        """`icon.end` is declared exactly where the template reads `i.end`"""
        for name, spec in self.icon_components().items():
            variables = ComponentRegistry().get_component_variables(name)
            source = self.template_source(spec)

            assert ("icon.end" in variables) == ("i.end" in source), (
                f"{name}: icon.end declaration does not match its template"
            )
            assert ("icon.fill" in variables) == ("i.fill" in source), (
                f"{name}: icon.fill declaration does not match its template"
            )

    def test_parse_icon_accepts_every_declared_form(self):
        """Every declared attribute form is one parse_icon actually parses"""
        from labb.templatetags.lb_tags import parse_icon

        for name in self.icon_components():
            for attr in ComponentRegistry().get_component_variables(name):
                if not attr.startswith("icon") or attr == "icon.class":
                    continue
                parsed = parse_icon({attr: "rmx.heart"})

                assert parsed["name"] == "rmx.heart", f"{name}: {attr} not parsed"
                assert parsed["fill"] is ("fill" in attr)
                assert parsed["end"] is ("end" in attr)
