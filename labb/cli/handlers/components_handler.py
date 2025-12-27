from typing import Optional

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree

from ...components import ComponentRegistry

console = Console()


def inspect_components(
    component: Optional[str] = None, list_all: bool = False, verbose: bool = False
):
    """Inspect components from components.yaml configuration"""

    registry = ComponentRegistry()

    if list_all or component is None:
        _list_all_components(registry, verbose)
    else:
        _inspect_specific_component(component, registry, verbose)


def examples_command(
    component: Optional[str] = None,
    examples: Optional[list[str]] = None,
    list_all: bool = False,
    tree: bool = False,
):
    """Handle examples subcommand - list or show component examples"""

    registry = ComponentRegistry()

    if tree:
        _show_examples_tree(registry)
    elif list_all or (component is None and examples is None):
        _list_all_examples(registry)
    elif component and examples:
        _show_multiple_examples(registry, component, examples)
    elif component:
        _list_component_examples(registry, component)
    else:
        _list_all_examples(registry)


def _list_all_components(registry: ComponentRegistry, verbose: bool):
    """List all available components"""

    components = registry.get_all_components()

    if not components:
        console.print("[yellow]No components found in components.yaml[/yellow]")
        return

    console.print(
        f"\n[bold blue]📦 Available Components ({len(components)})[/bold blue]"
    )

    if verbose:
        # Detailed view with table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Component", style="cyan")
        table.add_column("Description", style="dim")
        table.add_column("Template", style="green")
        table.add_column("Variables", style="yellow")
        table.add_column("Events", style="blue")

        for name, spec in components.items():
            description = spec.get("description", "No description")
            template = spec.get("template", "No template")
            var_count = len(spec.get("variables", {}))
            event_count = len(spec.get("events", []))

            table.add_row(
                name,
                description,
                template,
                f"{var_count} vars",
                f"{event_count} events",
            )

        console.print(table)
    else:
        # Simple list view
        for name, spec in components.items():
            description = spec.get("description", "No description")
            console.print(f"  [cyan]{name}[/cyan] - {description}")


def _inspect_specific_component(
    component: str, registry: ComponentRegistry, verbose: bool
):
    """Inspect a specific component"""

    spec = registry.get_component(component)

    if not spec:
        console.print(f"[red]❌ Component '{component}' not found[/red]")

        # Suggest available components
        available = registry.get_component_names()
        if available:
            console.print("\n[yellow]Available components:[/yellow]")
            for name in available:
                console.print(f"  • {name}")
        return

    # Component header
    console.print(f"\n[bold blue]📦 Component: {component}[/bold blue]")

    description = spec.get("description", "No description provided")
    console.print(f"[dim]{description}[/dim]")

    # Basic info
    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column("Property", style="bold")
    info_table.add_column("Value", style="cyan")

    info_table.add_row("Template", spec.get("template", "Not specified"))

    base_classes = spec.get("base_classes", [])
    if base_classes:
        info_table.add_row("Base Classes", ", ".join(base_classes))

    console.print(info_table)

    # Variables section
    variables = spec.get("variables", {})
    if variables:
        console.print(f"\n[bold yellow]⚙️  Variables ({len(variables)})[/bold yellow]")

        var_table = Table(show_header=True, header_style="bold magenta")
        var_table.add_column("Name", style="cyan")
        var_table.add_column("Type", style="green")
        var_table.add_column("Default", style="yellow")
        var_table.add_column("Description", style="dim")

        for var_name, var_spec in variables.items():
            var_type = var_spec.get("type", "string")
            default = var_spec.get("default", "")
            desc = var_spec.get("description", "No description")

            # Show enum values if available
            if var_type == "enum" and "values" in var_spec:
                values = var_spec["values"]
                # Filter out empty strings from enum values
                filtered_values = [str(v) for v in values if str(v).strip()]
                var_type = f"enum: {', '.join(filtered_values)}"

            # Show dash for empty defaults
            default_display = str(default) if default else "-"

            var_table.add_row(var_name, var_type, default_display, desc)

        console.print(var_table)

    # Events section
    events = spec.get("events", [])
    if events:
        console.print(f"\n[bold blue]🔔 Events ({len(events)})[/bold blue]")

        event_table = Table(show_header=True, header_style="bold magenta")
        event_table.add_column("Event Name", style="cyan")
        event_table.add_column("Description", style="dim")
        event_table.add_column("Data", style="yellow")

        for event in events:
            name = event.get("name", "Unknown")
            desc = event.get("description", "No description")
            data = ", ".join(event.get("data", []))

            event_table.add_row(name, desc, data)

        console.print(event_table)

    # Raw YAML if verbose
    if verbose:
        console.print("\n[bold green]📄 Raw Configuration[/bold green]")
        yaml_content = yaml.dump({component: spec}, default_flow_style=False, indent=2)
        syntax = Syntax(yaml_content, "yaml", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="components.yaml", border_style="green"))


def _list_all_examples(registry: ComponentRegistry):
    """List all components that have examples"""

    components_with_examples = registry.get_available_components_with_examples()

    if not components_with_examples:
        console.print("[yellow]No components with examples found[/yellow]")
        return

    console.print(
        f"\n[bold blue]📚 Components with Examples ({len(components_with_examples)})[/bold blue]"
    )

    for component in sorted(components_with_examples):
        example_names = registry.get_component_example_names(component)
        example_count = len(example_names)
        console.print(
            f"  [cyan]{component}[/cyan] - {example_count} example{'s' if example_count != 1 else ''}"
        )

    console.print(
        "\n[dim]Use 'labb components ex <component>' to see examples for a specific component[/dim]"
    )


def _list_component_examples(registry: ComponentRegistry, component: str):
    """List examples for a specific component"""

    example_names = registry.get_component_example_names(component)

    if not example_names:
        console.print(f"[yellow]No examples found for component '{component}'[/yellow]")

        # Suggest available components
        available = registry.get_available_components_with_examples()
        if available:
            console.print("\n[dim]Components with examples:[/dim]")
            for name in sorted(available):
                console.print(f"  • {name}")
        return

    console.print(
        f"\n[bold blue]📚 Examples for '{component}' ({len(example_names)})[/bold blue]"
    )

    for example_name in sorted(example_names):
        title = registry.get_example_title_from_name(example_name)
        console.print(f"  [cyan]{example_name}[/cyan] - {title}")

    console.print(
        f"\n[dim]Use 'labb components ex {component} <example>' to view a specific example[/dim]"
    )


def _show_examples_tree(registry: ComponentRegistry):
    """Show all components and examples in a tree format"""

    components_with_examples = registry.get_available_components_with_examples()

    if not components_with_examples:
        console.print("[yellow]No components with examples found[/yellow]")
        return

    # Create the root tree
    tree = Tree(
        f"[bold blue]📚 Component Examples ({len(components_with_examples)} components)[/bold blue]",
        guide_style="dim",
    )

    total_examples = 0

    for component in sorted(components_with_examples):
        example_names = registry.get_component_example_names(component)
        example_count = len(example_names)
        total_examples += example_count

        # Add component branch
        component_branch = tree.add(
            f"[cyan]{component}[/cyan] [dim]({example_count} example{'s' if example_count != 1 else ''})[/dim]"
        )

        # Add examples as leaves
        for example_name in sorted(example_names):
            title = registry.get_example_title_from_name(example_name)
            component_branch.add(f"[green]{example_name}[/green] - {title}")

    console.print("\n")
    console.print(tree)
    console.print(
        f"\n[dim]Total: {total_examples} examples across {len(components_with_examples)} components[/dim]"
    )
    console.print(
        "[dim]Use 'labb components ex <component> <example>' to view specific examples[/dim]"
    )


def _show_multiple_examples(
    registry: ComponentRegistry, component: str, examples: list[str]
):
    """Show multiple examples for a component"""

    # Check if component has examples
    available_components = registry.get_available_components_with_examples()
    if component not in available_components:
        console.print(f"[red]❌ Component '{component}' has no examples[/red]")

        if available_components:
            console.print("\n[dim]Components with examples:[/dim]")
            for name in sorted(available_components):
                console.print(f"  • {name}")
        return

    # Get available examples for the component
    available_examples = registry.get_component_example_names(component)

    # Check which examples exist and which don't
    valid_examples = []
    invalid_examples = []

    for example in examples:
        if example in available_examples:
            valid_examples.append(example)
        else:
            invalid_examples.append(example)

    # Show errors for invalid examples
    if invalid_examples:
        console.print(
            f"[red]❌ Examples not found for component '{component}': {', '.join(invalid_examples)}[/red]"
        )

        if available_examples:
            console.print(f"\n[dim]Available examples for '{component}':[/dim]")
            for name in sorted(available_examples):
                title = registry.get_example_title_from_name(name)
                console.print(f"  • [cyan]{name}[/cyan] - {title}")

        if not valid_examples:
            return

        console.print("\n[yellow]Showing valid examples only...[/yellow]")

    # Show valid examples
    for i, example in enumerate(valid_examples):
        if i > 0:
            console.print("\n" + "─" * 80 + "\n")  # Separator between examples

        example_path = f"{component}/{example}"
        content = registry.get_example_raw_content(example_path)

        if not content:
            console.print(
                f"[red]❌ Could not read example content for '{example_path}'[/red]"
            )
            continue

        title = registry.get_example_title_from_name(example)
        console.print(f"[bold blue]📄 {component}/{example} - {title}[/bold blue]")

        # Display the content with syntax highlighting
        syntax = Syntax(content, "html", theme="monokai", line_numbers=True)
        console.print(
            Panel(syntax, title=f"{component}/{example}.html", border_style="blue")
        )

    if len(valid_examples) > 1:
        console.print(
            f"\n[dim]Showed {len(valid_examples)} examples for '{component}'[/dim]"
        )
