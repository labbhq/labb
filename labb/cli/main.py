from typing import Optional

import typer

# Import all handler functions at module level for better testability
from .handlers.build_handler import build_css
from .handlers.components_handler import examples_command, inspect_components
from .handlers.config_handler import edit_config, show_config, validate_config
from .handlers.init_handler import init_project
from .handlers.llms_handler import display_llms_txt
from .handlers.scan_handler import scan_templates
from .handlers.setup_handler import setup_project_with_config

try:
    from labbicons.cli.main import app as icons_app

    LABBICONS_AVAILABLE = True
except ImportError:
    LABBICONS_AVAILABLE = False
    icons_app = None

app = typer.Typer(
    help="labb Django UI Components CLI",
    no_args_is_help=True,  # Show help when no command is provided
)


@app.command()
def init(
    defaults: bool = typer.Option(
        False, "--defaults", help="Use default values without prompts"
    ),
    force: bool = typer.Option(
        False, "--force", help="Overwrite existing files and directories"
    ),
):
    """Initialize labb project with configuration and project structure"""
    init_project(use_defaults=defaults, force=force)


@app.command()
def setup(
    install_deps: Optional[bool] = typer.Option(
        None, help="Install Node.js dependencies"
    ),
):
    """Install labb dependencies (Tailwind CSS CLI and DaisyUI)"""
    setup_project_with_config(install_deps)


@app.command()
def config(
    show_metadata: bool = typer.Option(
        False, "--metadata", "-m", help="Show configuration metadata"
    ),
    validate: bool = typer.Option(
        False, "--validate", "-v", help="Validate configuration and check files"
    ),
    edit: bool = typer.Option(
        False, "--edit", "-e", help="Open configuration file in editor"
    ),
    config_path: Optional[str] = typer.Option(
        None, "--config", "-c", help="Path to specific configuration file"
    ),
):
    """Display, validate, or edit labb configuration in YAML format"""
    if edit:
        edit_config(config_path)
    elif validate:
        validate_config(config_path)
    else:
        show_config(show_metadata, config_path)


@app.command()
def build(
    watch: bool = typer.Option(
        False, "--watch", "-w", help="Watch for changes and rebuild"
    ),
    scan: bool = typer.Option(
        False, "--scan", "-s", help="Also watch templates and scan for CSS classes"
    ),
    minify: Optional[bool] = typer.Option(
        None, "--minify/--no-minify", help="Minify CSS output (default: from config)"
    ),
    input_file: Optional[str] = typer.Option(
        None, "--input", "-i", help="Override input CSS file path"
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", help="Override output CSS file path"
    ),
):
    """Build CSS using Tailwind CSS 4 with labb configuration"""
    build_css(
        watch=watch,
        scan=scan,
        minify=minify,
        input_file=input_file,
        output_file=output_file,
    )


@app.command()
def dev(
    minify: Optional[bool] = typer.Option(
        False, "--minify/--no-minify", help="Minify CSS output (default: false for dev)"
    ),
    input_file: Optional[str] = typer.Option(
        None, "--input", "-i", help="Override input CSS file path"
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", help="Override output CSS file path"
    ),
):
    """Development mode: watch and build CSS + scan templates concurrently"""
    build_css(
        watch=True,
        scan=True,
        minify=minify,
        input_file=input_file,
        output_file=output_file,
    )


@app.command()
def llms():
    """Display llms.txt content for AI/LLM consumption"""
    display_llms_txt()


# Create icons subcommand group
if LABBICONS_AVAILABLE:
    app.add_typer(icons_app, name="icons")
else:
    # Create a placeholder command that shows the error
    @app.command()
    def icons():
        """Access labb icons packs (requires labbicons package)"""
        from rich.console import Console

        console = Console()
        console.print("[red]❌ labbicons package not found[/red]")
        console.print(
            "[yellow]To use icon commands, install the labbicons package:[/yellow]"
        )
        console.print("[cyan]  pip install labbicons[/cyan]")
        console.print("[dim]or[/dim]")
        console.print("[cyan]  poetry add labbicons[/cyan]")
        raise typer.Exit(1)


# Create a subcommand group for components
components_app = typer.Typer(
    help="Component inspection and examples",
    no_args_is_help=True,  # Show help when no subcommand is provided
)
app.add_typer(components_app, name="components")


@components_app.command("inspect")
def components_inspect(
    component: Optional[str] = typer.Argument(
        None, help="Specific component to inspect"
    ),
    list_all: bool = typer.Option(False, "--list", "-l", help="List all components"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed information"
    ),
):
    """Inspect available components and their specifications"""
    inspect_components(component, list_all, verbose)


@components_app.command("ex")
def components_examples(
    component: Optional[str] = typer.Argument(
        None, help="Component name to show examples for"
    ),
    examples: Optional[list[str]] = typer.Argument(
        None, help="Specific example(s) to display (can specify multiple)"
    ),
    list_all: bool = typer.Option(
        False, "--list", "-l", help="List all components with examples"
    ),
    tree: bool = typer.Option(
        False, "--tree", "-t", help="Show examples in tree format"
    ),
):
    """View component examples"""
    examples_command(component, examples, list_all, tree)


@app.command()
def scan(
    watch: bool = typer.Option(
        False, "--watch", "-w", help="Watch for changes and rescan"
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Override output file path"
    ),
    patterns: Optional[str] = typer.Option(
        None, "--patterns", help="Override template patterns (comma-separated)"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed scanning information"
    ),
):
    """Scan templates for labb components and extract CSS classes"""
    scan_templates(watch, output, patterns, verbose)


if __name__ == "__main__":
    app()
