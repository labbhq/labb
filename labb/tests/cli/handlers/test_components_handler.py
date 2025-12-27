from unittest.mock import Mock, patch

from labb.cli.handlers.components_handler import (
    _inspect_specific_component,
    _list_all_components,
    inspect_components,
)


@patch("labb.cli.handlers.components_handler.ComponentRegistry")
@patch("labb.cli.handlers.components_handler.console")
def test_inspect_components_list_all(
    mock_console, mock_registry_class, components_yaml_content
):
    mock_registry = Mock()
    mock_registry.get_all_components.return_value = components_yaml_content
    mock_registry_class.return_value = mock_registry

    inspect_components(component=None, list_all=True, verbose=False)

    mock_registry.get_all_components.assert_called_once()
    mock_console.print.assert_called()


@patch("labb.cli.handlers.components_handler.ComponentRegistry")
@patch("labb.cli.handlers.components_handler.console")
def test_inspect_components_specific(
    mock_console, mock_registry_class, components_yaml_content
):
    mock_registry = Mock()
    mock_registry.get_component.return_value = components_yaml_content["button"]
    mock_registry_class.return_value = mock_registry

    inspect_components(component="button", list_all=False, verbose=False)

    mock_registry.get_component.assert_called_once_with("button")
    mock_console.print.assert_called()


@patch("labb.cli.handlers.components_handler.ComponentRegistry")
@patch("labb.cli.handlers.components_handler.console")
def test_inspect_components_default_behavior(
    mock_console, mock_registry_class, components_yaml_content
):
    mock_registry = Mock()
    mock_registry.get_all_components.return_value = components_yaml_content
    mock_registry_class.return_value = mock_registry

    inspect_components()

    mock_registry.get_all_components.assert_called_once()


@patch("labb.cli.handlers.components_handler.console")
def test_list_all_components_empty(mock_console):
    mock_registry = Mock()
    mock_registry.get_all_components.return_value = {}

    _list_all_components(mock_registry, verbose=False)

    mock_console.print.assert_called_with(
        "[yellow]No components found in components.yaml[/yellow]"
    )


@patch("labb.cli.handlers.components_handler.console")
def test_list_all_components_simple(mock_console, components_yaml_content):
    mock_registry = Mock()
    mock_registry.get_all_components.return_value = components_yaml_content

    _list_all_components(mock_registry, verbose=False)

    print_calls = mock_console.print.call_args_list
    assert len(print_calls) > 0

    # Check that component names are printed
    printed_text = str(print_calls)
    assert "button" in printed_text
    assert "drawer" in printed_text
    assert "menu" in printed_text


@patch("labb.cli.handlers.components_handler.Table")
@patch("labb.cli.handlers.components_handler.console")
def test_list_all_components_verbose(
    mock_console, mock_table_class, components_yaml_content
):
    mock_table = Mock()
    mock_table_class.return_value = mock_table
    mock_registry = Mock()
    mock_registry.get_all_components.return_value = components_yaml_content

    _list_all_components(mock_registry, verbose=True)

    mock_table.add_column.assert_called()
    mock_table.add_row.assert_called()
    mock_console.print.assert_called_with(mock_table)


@patch("labb.cli.handlers.components_handler.console")
def test_inspect_specific_component_not_found(mock_console):
    mock_registry = Mock()
    mock_registry.get_component.return_value = None
    mock_registry.get_component_names.return_value = ["button", "drawer"]

    _inspect_specific_component("nonexistent", mock_registry, verbose=False)

    error_calls = [
        call for call in mock_console.print.call_args_list if "not found" in str(call)
    ]
    assert len(error_calls) > 0


@patch("labb.cli.handlers.components_handler.console")
@patch("labb.cli.handlers.components_handler.Table")
def test_inspect_specific_component_found(
    mock_table_class, mock_console, components_yaml_content
):
    mock_table = Mock()
    mock_table_class.return_value = mock_table
    mock_registry = Mock()
    button_spec = components_yaml_content["button"]
    mock_registry.get_component.return_value = button_spec

    _inspect_specific_component("button", mock_registry, verbose=False)

    mock_console.print.assert_called()
    print_calls = mock_console.print.call_args_list
    printed_text = str(print_calls)

    assert "button" in printed_text.lower()


@patch("labb.cli.handlers.components_handler.console")
@patch("labb.cli.handlers.components_handler.Table")
@patch("labb.cli.handlers.components_handler.Syntax")
@patch("labb.cli.handlers.components_handler.Panel")
@patch("labb.cli.handlers.components_handler.yaml")
def test_inspect_specific_component_verbose(
    mock_yaml,
    mock_panel,
    mock_syntax,
    mock_table_class,
    mock_console,
    components_yaml_content,
):
    mock_table = Mock()
    mock_table_class.return_value = mock_table
    mock_registry = Mock()
    button_spec = components_yaml_content["button"]
    mock_registry.get_component.return_value = button_spec

    _inspect_specific_component("button", mock_registry, verbose=True)

    mock_yaml.dump.assert_called_once()
    # Syntax is called multiple times (YAML config + usage example)
    assert mock_syntax.call_count >= 1
    mock_panel.assert_called()


@patch("labb.cli.handlers.components_handler.console")
@patch("labb.cli.handlers.components_handler.Syntax")
@patch("labb.cli.handlers.components_handler.Panel")
def test_inspect_component_with_variables(
    mock_panel, mock_syntax, mock_console, components_yaml_content
):
    mock_registry = Mock()
    button_spec = components_yaml_content["button"]
    mock_registry.get_component.return_value = button_spec

    _inspect_specific_component("button", mock_registry, verbose=False)

    print_calls = mock_console.print.call_args_list
    printed_text = str(print_calls)

    # Should show variables section
    assert "Variables" in printed_text or "variant" in printed_text


@patch("labb.cli.handlers.components_handler.console")
def test_inspect_component_with_events(mock_console):
    mock_registry = Mock()
    component_with_events = {
        "base_classes": ["test"],
        "events": [
            {
                "name": "click",
                "description": "Button clicked",
                "data": ["target", "value"],
            }
        ],
    }
    mock_registry.get_component.return_value = component_with_events

    _inspect_specific_component("test-component", mock_registry, verbose=False)

    print_calls = mock_console.print.call_args_list
    printed_text = str(print_calls)

    # Should show events section
    assert "Events" in printed_text or "click" in printed_text


@patch("labb.cli.handlers.components_handler.console")
def test_inspect_component_usage_example(mock_console, components_yaml_content):
    mock_registry = Mock()
    button_spec = components_yaml_content["button"]
    mock_registry.get_component.return_value = button_spec

    _inspect_specific_component("button", mock_registry, verbose=False)

    print_calls = mock_console.print.call_args_list
    printed_text = str(print_calls)

    # Should show component information (header, description, variables table)
    assert "Component: button" in printed_text
    assert "Variables" in printed_text
