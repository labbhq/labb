import glob
import re
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Set

from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from labb.cli.handlers.commons import confirm_load_config
from labb.components import ComponentRegistry

console = Console()


def scan_templates(
    watch: bool = False,
    output: Optional[str] = None,
    patterns: Optional[str] = None,
    verbose: bool = False,
):
    """Scan templates for labb components and extract CSS classes"""

    # Load configuration
    config = confirm_load_config(console)
    output_path = output or config.classes_output
    template_patterns = patterns.split(",") if patterns else config.template_patterns
    scan_apps = config.scan_apps

    console.print("[bold blue]🔍 Scanning templates...[/bold blue]")
    if verbose:
        console.print(f"[dim]Template patterns: {template_patterns}[/dim]")
        if scan_apps:
            console.print(f"[dim]Django apps: {scan_apps}[/dim]")
        console.print(f"[dim]Output path: {output_path}[/dim]")

    if watch:
        console.print("[green]👀 Watch mode enabled[/green]")
        console.print("[dim]Press Ctrl+C to stop[/dim]")
        _watch_and_scan_live(
            template_patterns, output_path, verbose, scan_apps=scan_apps
        )
    else:
        _scan_once(
            template_patterns,
            output_path,
            verbose,
            watch=False,
            scan_apps=scan_apps,
        )


def _scan_once(
    template_patterns: List[str],
    output_path: str,
    verbose: bool,
    watch: bool = False,
    scan_apps: Dict[str, List[str]] = None,
):
    """Perform a single scan of templates"""

    # Find all template files
    template_files = _find_template_files(template_patterns, scan_apps)

    if not template_files:
        console.print("[yellow]⚠️  No template files found[/yellow]")
        for pattern in template_patterns:
            console.print(f"[dim]  • {pattern}[/dim]")
        return

    console.print(f"[dim]Found {len(template_files)} files[/dim]")

    # Scan files for components
    all_classes = set()
    component_usage = {}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Scanning templates...", total=len(template_files))

        for template_file in template_files:
            file_classes, file_components = _scan_template_file(template_file, verbose)
            all_classes.update(file_classes)

            # Track component usage
            for comp_name, instances in file_components.items():
                if comp_name not in component_usage:
                    component_usage[comp_name] = []
                component_usage[comp_name].extend(instances)

            progress.advance(task)

    # Write classes to output file
    _write_classes_file(all_classes, output_path, verbose)

    # Show summary
    _create_scan_summary(
        all_classes,
        component_usage,
        template_files,
        output_path,
        verbose,
        watch=watch,
        for_live_display=False,
    )


def _scan_templates_silent(
    template_patterns: List[str],
    output_path: str,
    verbose: bool,
    scan_apps: Dict[str, List[str]] = None,
):
    """Perform a scan without console output, returns scan results"""

    # Find all template files
    template_files = _find_template_files(template_patterns, scan_apps)

    if not template_files:
        return None, None, None

    # Scan files for components
    all_classes = set()
    component_usage = {}

    for template_file in template_files:
        file_classes, file_components = _scan_template_file(template_file, verbose)
        all_classes.update(file_classes)

        # Track component usage
        for comp_name, instances in file_components.items():
            if comp_name not in component_usage:
                component_usage[comp_name] = []
            component_usage[comp_name].extend(instances)

    # Write classes to output file (silent for live display)
    _write_classes_file(all_classes, output_path, verbose, silent=True)

    return all_classes, component_usage, template_files


def _watch_and_scan_live(
    template_patterns: List[str],
    output_path: str,
    verbose: bool,
    scan_apps: Dict[str, List[str]] = None,
):
    """Watch templates and rescan on changes with live updating display"""

    last_scan_time = 0
    scan_interval = 2  # seconds
    last_update = None

    try:
        # Initial scan
        all_classes, component_usage, template_files = _scan_templates_silent(
            template_patterns, output_path, verbose, scan_apps
        )

        if all_classes is None:
            console.print("[yellow]⚠️  No template files found[/yellow]")
            return

        # Create initial display
        with Live(
            _create_scan_summary(
                all_classes,
                component_usage,
                template_files,
                output_path,
                verbose,
                watch=True,
                last_update=last_update,
                for_live_display=True,
            ),
            console=console,
            refresh_per_second=4,
        ) as live:
            while True:
                # Check if any template files have been modified
                template_files = _find_template_files(template_patterns, scan_apps)

                if template_files:
                    latest_mtime = max(Path(f).stat().st_mtime for f in template_files)

                    if latest_mtime > last_scan_time:
                        # Perform silent scan
                        all_classes, component_usage, template_files = (
                            _scan_templates_silent(
                                template_patterns, output_path, verbose, scan_apps
                            )
                        )

                        if all_classes is not None:
                            last_update = time.strftime("%H:%M:%S")
                            live.update(
                                _create_scan_summary(
                                    all_classes,
                                    component_usage,
                                    template_files,
                                    output_path,
                                    verbose,
                                    watch=True,
                                    last_update=last_update,
                                    for_live_display=True,
                                )
                            )

                        last_scan_time = time.time()

                time.sleep(scan_interval)

    except KeyboardInterrupt:
        console.print("\n[yellow]⏹️  Watch stopped[/yellow]")


def _watch_and_scan_with_stop_event_live(
    template_patterns: List[str],
    output_path: str,
    verbose: bool,
    stop_event: threading.Event,
    scan_apps: Dict[str, List[str]] = None,
):
    """Watch templates and rescan on changes with live display, can be stopped by a threading.Event"""

    last_scan_time = 0
    scan_interval = 2  # seconds
    last_update = None

    try:
        # Initial scan
        all_classes, component_usage, template_files = _scan_templates_silent(
            template_patterns, output_path, verbose, scan_apps
        )

        if all_classes is None:
            console.print("[yellow]⚠️  No template files found[/yellow]")
            return

        # Create initial display
        with Live(
            _create_scan_summary(
                all_classes,
                component_usage,
                template_files,
                output_path,
                verbose,
                watch=True,
                last_update=last_update,
                for_live_display=True,
            ),
            console=console,
            refresh_per_second=4,
        ) as live:
            while not stop_event.is_set():
                # Check if any template files have been modified
                template_files = _find_template_files(template_patterns, scan_apps)

                if template_files:
                    latest_mtime = max(Path(f).stat().st_mtime for f in template_files)

                    if latest_mtime > last_scan_time:
                        # Perform silent scan
                        all_classes, component_usage, template_files = (
                            _scan_templates_silent(
                                template_patterns, output_path, verbose, scan_apps
                            )
                        )

                        if all_classes is not None:
                            last_update = time.strftime("%H:%M:%S")
                            live.update(
                                _create_scan_summary(
                                    all_classes,
                                    component_usage,
                                    template_files,
                                    output_path,
                                    verbose,
                                    watch=True,
                                    last_update=last_update,
                                    for_live_display=True,
                                )
                            )

                        last_scan_time = time.time()

                # Wait for the interval or until stop event is set
                stop_event.wait(scan_interval)

    except Exception as e:
        if not stop_event.is_set():
            console.print(f"[red]❌ Scanner error: {e}[/red]")


def _find_template_files(
    patterns: List[str],
    scan_apps: Dict[str, List[str]] = None,
) -> List[str]:
    """Find all template files matching the given patterns and Django apps"""

    files = set()

    # Find files using glob patterns
    for pattern in patterns:
        matched_files = glob.glob(pattern, recursive=True)
        files.update(matched_files)

    # Find files from Django apps if specified, using app-specific or default patterns
    if scan_apps:
        app_files = _discover_django_app_templates(scan_apps, patterns)
        files.update(app_files)

    # Filter to only HTML files and exclude hidden files
    template_files = []
    for file_path in files:
        path = Path(file_path)
        if path.suffix.lower() == ".html" and not any(
            part.startswith(".") for part in path.parts
        ):
            template_files.append(file_path)

    return sorted(template_files)


def _discover_django_app_templates(
    app_config: Dict[str, List[str]],
    default_patterns: List[str],
) -> List[str]:
    """Discover template files from Django apps using app-specific or default patterns"""

    app_files = set()

    for app_name, app_patterns in app_config.items():
        try:
            # Try to import the app
            app_module = __import__(app_name, fromlist=[""])
            app_path = Path(app_module.__file__).parent

            # Use app-specific patterns if defined, otherwise use default patterns
            patterns_to_use = app_patterns if app_patterns else default_patterns

            # Apply the patterns to the app's directory
            for pattern in patterns_to_use:
                # Convert relative patterns to absolute paths within the app
                app_pattern = str(app_path / pattern)
                matched_files = glob.glob(app_pattern, recursive=True)
                app_files.update(matched_files)

        except ImportError as e:
            # Display error message for unimportable apps
            console.print(
                f"[yellow]⚠️  Could not import Django app '{app_name}': {e}[/yellow]"
            )
            console.print(
                f"[dim]  Skipping app '{app_name}' from template scanning[/dim]"
            )
            continue

    return app_files


def _scan_template_file(
    file_path: str, verbose: bool
) -> tuple[Set[str], Dict[str, List[Dict]]]:
    """Scan a single template file for labb components"""

    # if verbose:
    #     console.print(f"[dim]Scanning: {file_path}[/dim]")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        console.print(f"[red]Error reading {file_path}: {e}[/red]")
        return set(), {}

    # Find all labb components using regex
    # Pattern: <c-lb.component-name attributes> (opening tags and self-closing tags)
    # Allow dots in component names for nested components like drawer.toggle
    # Use a simpler pattern that just finds opening tags to handle nested components
    component_pattern = r"<c-lb\.([a-zA-Z0-9_.-]+)([^>]*?)(?:\s*/\s*>|>)"
    matches = re.finditer(component_pattern, content, re.DOTALL | re.IGNORECASE)

    all_classes = set()
    components_found = {}

    registry = ComponentRegistry()

    for match in matches:
        component_name = match.group(1)
        attributes_str = match.group(2)

        # Parse attributes
        attributes = _parse_component_attributes(attributes_str)
        # Track component usage
        if component_name not in components_found:
            components_found[component_name] = []

        components_found[component_name].append(
            {
                "file": file_path,
                "attributes": attributes,
                "match": (
                    match.group(0)[:100] + "..."
                    if len(match.group(0)) > 100
                    else match.group(0)
                ),
            }
        )

        # Map attributes to CSS classes
        component_classes = _map_attributes_to_classes(
            component_name, attributes, registry
        )
        all_classes.update(component_classes)

        # if verbose and component_classes:
        #     console.print(
        #         f"[dim]  Found {component_name}: {', '.join(component_classes)}[/dim]"
        #     )

    return all_classes, components_found


def _split_classes(class_string_or_list) -> Set[str]:
    """Split space-separated classes into individual classes.

    Handles both strings (which may contain multiple space-separated classes)
    and lists/iterables of class strings. Returns empty set for None or empty values.
    """
    classes = set()

    # Handle None explicitly
    if class_string_or_list is None:
        return classes

    if isinstance(class_string_or_list, str):
        # Split by whitespace and filter out empty strings
        classes.update(filter(None, class_string_or_list.split()))
    elif isinstance(class_string_or_list, (list, tuple, set)):
        # Handle iterables
        for item in class_string_or_list:
            # Skip None values
            if item is None:
                continue
            if isinstance(item, str):
                # Only add non-empty strings after splitting
                split_items = filter(None, item.split())
                classes.update(split_items)
    else:
        # Fallback for other types - only add if truthy
        if class_string_or_list:
            classes.add(str(class_string_or_list))

    return classes


def _parse_component_attributes(attributes_str: str) -> Dict[str, str]:
    """Parse component attributes from string"""

    attributes = {}

    # Pattern to match attribute="value" or attribute='value'
    attr_pattern = r'([a-zA-Z0-9_-]+)=(["\'])(.*?)\2'
    matches = re.finditer(attr_pattern, attributes_str)

    for match in matches:
        attr_name = match.group(1)
        attr_value = match.group(3)
        attributes[attr_name] = attr_value

    # Pattern to match boolean attributes without values (e.g., "zebra", "disabled")
    # This matches attribute names that are followed by whitespace, >, or /
    boolean_attr_pattern = r"\b([a-zA-Z0-9_-]+)(?=\s|>|/|$)"
    boolean_matches = re.finditer(boolean_attr_pattern, attributes_str)

    for match in boolean_matches:
        attr_name = match.group(1)
        # Only add if not already found as a key-value attribute
        if attr_name not in attributes:
            attributes[attr_name] = "true"

    return attributes


def _map_attributes_to_classes(
    component_name: str, attributes: Dict[str, str], registry: ComponentRegistry
) -> Set[str]:
    """Map component attributes to CSS classes using components.yaml"""

    component_spec = registry.get_component(component_name)
    if not component_spec:
        return set()

    classes = set()

    # Add base classes
    base_classes = component_spec.get("base_classes", [])
    classes.update(_split_classes(base_classes))

    # Add optional base classes (these are potential classes that might be used)
    optional_base_classes = component_spec.get("optional_base_classes", [])
    classes.update(_split_classes(optional_base_classes))

    # Process variables
    variables = component_spec.get("variables", {})

    for var_name, var_spec in variables.items():
        var_type = var_spec.get("type", "string")

        # Handle map type variables
        if var_type == "map":
            mapped_variable = var_spec.get("variable")
            if mapped_variable:
                # Get the mapped component and variable
                if ":" in mapped_variable:
                    # Variable mapping (e.g., "modal.close:position")
                    component_name, var_name = mapped_variable.split(":", 1)
                    mapped_classes = _get_mapped_component_classes(
                        component_name, var_name, registry
                    )
                    classes.update(mapped_classes)
                else:
                    # Component mapping (e.g., "modal.backdrop")
                    mapped_classes = _get_mapped_component_classes(
                        mapped_variable, None, registry
                    )
                    classes.update(mapped_classes)
            continue

        # Get attribute value (use default if not provided)
        attr_value = attributes.get(var_name, var_spec.get("default", ""))

        # Skip empty values for optional attributes
        if not attr_value and attr_value != 0 and attr_value is not False:
            continue

        # Map value to CSS class
        css_mapping = var_spec.get("css_mapping", {})

        if str(attr_value) in css_mapping:
            css_class = css_mapping[str(attr_value)]
            if css_class:  # Only add non-empty classes
                # Handle nested CSS mappings (e.g., "modal.box:size=xs")
                if ":" in css_class:
                    nested_classes = _resolve_nested_css_mapping(css_class, registry)
                    classes.update(_split_classes(nested_classes))
                else:
                    classes.update(_split_classes(css_class))
        elif var_spec.get("type") == "boolean" and str(attr_value).lower() == "true":
            # For boolean attributes, check if true mapping exists
            # Check for both string "true" and Python boolean True
            if "true" in css_mapping:
                css_class = css_mapping["true"]
                if css_class:  # Only add non-empty classes
                    # Handle nested CSS mappings
                    if ":" in css_class:
                        nested_classes = _resolve_nested_css_mapping(
                            css_class, registry
                        )
                        classes.update(_split_classes(nested_classes))
                    else:
                        classes.update(_split_classes(css_class))
            elif True in css_mapping:
                css_class = css_mapping[True]
                if css_class:  # Only add non-empty classes
                    # Handle nested CSS mappings
                    if ":" in css_class:
                        nested_classes = _resolve_nested_css_mapping(
                            css_class, registry
                        )
                        classes.update(_split_classes(nested_classes))
                    else:
                        classes.update(_split_classes(css_class))

    return classes


def _get_mapped_component_classes(
    component_name: str, var_name: str, registry: ComponentRegistry
) -> Set[str]:
    """Get CSS classes for a mapped component or component variable"""

    classes = set()
    component_spec = registry.get_component(component_name)

    if not component_spec:
        return classes

    # If no specific variable, get all base classes
    if var_name is None:
        base_classes = component_spec.get("base_classes", [])
        classes.update(_split_classes(base_classes))
        optional_base_classes = component_spec.get("optional_base_classes", [])
        classes.update(_split_classes(optional_base_classes))
        return classes

    # Get classes for specific variable
    variables = component_spec.get("variables", {})
    var_spec = variables.get(var_name, {})

    # Get all possible CSS mappings for this variable
    css_mapping = var_spec.get("css_mapping", {})
    for css_class in css_mapping.values():
        if css_class:
            classes.update(_split_classes(css_class))

    return classes


def _resolve_nested_css_mapping(
    css_mapping: str, registry: ComponentRegistry
) -> Set[str]:
    """Resolve nested CSS mappings like 'modal.box:size=xs' or 'modal.close'"""

    classes = set()

    # Handle component references (e.g., "modal.backdrop")
    if "." in css_mapping and ":" not in css_mapping:
        # This is a component reference, get its base classes
        component_spec = registry.get_component(css_mapping)
        if component_spec:
            base_classes = component_spec.get("base_classes", [])
            classes.update(_split_classes(base_classes))
            optional_base_classes = component_spec.get("optional_base_classes", [])
            classes.update(_split_classes(optional_base_classes))

    # Handle variable mappings (e.g., "modal.box:size=xs")
    elif ":" in css_mapping:
        parts = css_mapping.split(":", 1)
        if len(parts) == 2:
            component_name = parts[0]
            var_mapping = parts[1]

            # Parse variable mapping (e.g., "size=xs")
            if "=" in var_mapping:
                var_name, var_value = var_mapping.split("=", 1)

                # Get the component spec
                component_spec = registry.get_component(component_name)
                if component_spec:
                    variables = component_spec.get("variables", {})
                    var_spec = variables.get(var_name, {})
                    css_mapping_dict = var_spec.get("css_mapping", {})

                    # Get the actual CSS class for this value
                    if var_value in css_mapping_dict:
                        css_class = css_mapping_dict[var_value]
                        if css_class:
                            classes.update(_split_classes(css_class))

    return classes


def _write_classes_file(
    classes: Set[str], output_path: str, verbose: bool, silent: bool = False
):
    """Write extracted classes to output file"""

    output_file = Path(output_path)

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Sort classes for consistent output
    sorted_classes = sorted(classes)

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("/* Auto-generated by labb, do not edit */\n")
            f.write(f"/* Total classes: {len(sorted_classes)} */\n\n")

            for css_class in sorted_classes:
                f.write(f"{css_class}\n")

        if not silent:
            console.print(f"[green]✅ Written to {output_path}[/green]")

            if verbose:
                console.print(f"[dim]Classes: {len(sorted_classes)}[/dim]")

    except Exception as e:
        if not silent:
            console.print(f"[red]❌ Error writing classes file: {e}[/red]")


def _create_scan_summary(
    classes: Set[str],
    component_usage: Dict,
    template_files: List[str],
    output_path: str,
    verbose: bool,
    watch: bool = False,
    last_update: str = None,
    for_live_display: bool = False,
):
    """Create scan summary content for display - can be used for both live and static display"""

    # Common content - same for both modes
    summary_text = f"""[bold]Scan Results[/bold]

📁 Files: {len(template_files)}
🧩 Components: {len(component_usage)}
🎨 Classes: {len(classes)}
📄 Output: {output_path}"""

    summary_panel = Panel(summary_text, title="Summary", border_style="green")

    # Component usage table (if verbose) - same for both modes
    usage_table = None
    if verbose and component_usage:
        usage_table = Table(show_header=True, header_style="bold magenta", box=None)
        usage_table.add_column("Component", style="cyan", width=15)
        usage_table.add_column("Instances", style="green", width=10)
        usage_table.add_column("Files", style="blue", width=10)

        for comp_name, instances in component_usage.items():
            files_used = set(inst["file"] for inst in instances)
            usage_table.add_row(comp_name, str(len(instances)), f"{len(files_used)}")

    if for_live_display:
        # Create layout for live display
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=1),
            Layout(name="main"),
            Layout(name="footer", size=1),
        )

        # Header with timestamp
        header_text = Text("🔍 Labb Template Scanner", style="bold blue")
        if last_update:
            header_text.append(f" • Last update: {last_update}", style="dim")
        layout["header"].update(Align.center(header_text))

        # Main content
        if usage_table:
            # Stack summary and table vertically
            layout["main"].split_column(
                Layout(summary_panel, name="summary", size=10),
                Layout(
                    Panel(usage_table, title="Component Usage", border_style="yellow"),
                    name="usage",
                    ratio=1,
                ),
            )
        else:
            layout["main"].update(summary_panel)

        # Footer with status
        if watch:
            footer_text = Text(
                "👀 Watching for changes... Press Ctrl+C to stop", style="dim"
            )
        else:
            footer_text = Text("✅ Scan complete", style="green")
        layout["footer"].update(Align.center(footer_text))

        return layout
    else:
        # Static display for console output
        console.print(summary_panel)

        # Component usage table (if verbose)
        if usage_table:
            console.print("[bold yellow]🧩 Component Usage[/bold yellow]")
            console.print(usage_table)

        # Next steps (only for non-watch mode)
        if not watch:
            console.print("[bold green]💡 Next Steps:[/bold green]")
            console.print("Run: [cyan]labb build[/cyan]")

        return None


def _show_usage_example(component_name: str, spec: dict):
    """Show usage example for the component"""

    variables = spec.get("variables", {})

    # Generate a basic usage example
    example_lines = [f"<c-lb.{component_name}"]

    # Add some example variables with their defaults
    example_vars = []
    for var_name, var_spec in list(variables.items())[:3]:  # Show first 3 variables
        default = var_spec.get("default")
        var_type = var_spec.get("type", "string")

        if var_type == "enum" and "values" in var_spec:
            # Use first non-default value as example
            values = var_spec["values"]
            example_value = (
                values[1] if len(values) > 1 and values[0] == default else values[0]
            )
            example_vars.append(f'{var_name}="{example_value}"')
        elif var_type == "boolean":
            example_value = "true" if not default else "false"
            example_vars.append(f'{var_name}="{example_value}"')
        elif default and str(default):
            example_vars.append(f'{var_name}="{default}"')

    if example_vars:
        example_lines[0] += " " + " ".join(example_vars)

    example_lines.append(">")
    example_lines.append(f"    {component_name.title()} Content")
    example_lines.append(f"</c-lb.{component_name}>")

    example_code = "\n".join(example_lines)
    syntax = Syntax(example_code, "html", theme="monokai")
    console.print(Panel(syntax, title="Template Usage", border_style="green"))
