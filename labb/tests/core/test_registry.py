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
