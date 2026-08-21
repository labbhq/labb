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
    invoke_without_command=True,  # Run callback when no subcommand → show help and exit 0
)


@app.callback()
def main(ctx: typer.Context):
    """When no command is given, show help and exit successfully (0)."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


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


@app.command()
def migrate(
    path: str = typer.Argument(".", help="Project directory (contains labb.yaml)"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Apply without prompting"),
):
    """Migrate a legacy css.scan.apps config to the new css.packages schema."""
    from .handlers.migrate_handler import migrate_config

    migrate_config(path=path, assume_yes=yes)


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


# Block subcommand group
block_app = typer.Typer(
    help="Block management commands",
    no_args_is_help=True,
)
app.add_typer(block_app, name="block")


@block_app.command("init")
def block_init_cmd(
    name: str = typer.Option("blocks", "--name", "-n", help="Collection name"),
    path: str = typer.Option(
        None, "--path", "-p", help="Path to create collection (default: ./{name})"
    ),
):
    """Initialise a block collection as a Django app"""
    from .handlers.blocks import block_init

    block_init(name=name, path=path)


@block_app.command("add")
def block_add_cmd(
    ref: str = typer.Argument(..., help="Block ref (vendor/category/slug)"),
    collection: Optional[str] = typer.Option(
        None, "--collection", "-c", help="Target collection name"
    ),
):
    """Add a block from a configured source into a collection"""
    from .handlers.blocks import block_add

    block_add(ref=ref, collection_name=collection)


@block_app.command("remove")
def block_remove_cmd(
    ref: str = typer.Argument(..., help="Block ref (vendor/category/slug)"),
    collection: Optional[str] = typer.Option(
        None, "--collection", "-c", help="Target collection name"
    ),
):
    """Remove a block from a collection"""
    from .handlers.blocks import block_remove

    block_remove(ref=ref, collection_name=collection)


@block_app.command("sync")
def block_sync_cmd(
    vendor: str = typer.Argument(..., help="Vendor key to sync (e.g. lb)"),
    collection: Optional[str] = typer.Option(
        None, "--collection", "-c", help="Target collection name"
    ),
    models_only: bool = typer.Option(
        False, "--models-only", help="Sync only model files"
    ),
    fixtures_only: bool = typer.Option(
        False, "--fixtures-only", help="Sync only fixtures"
    ),
    templates_only: bool = typer.Option(
        False, "--templates-only", help="Sync only templates"
    ),
):
    """Re-fetch and overwrite vendor models, fixtures, templates and block code from source"""
    from .handlers.blocks import block_sync

    block_sync(
        vendor=vendor,
        collection_name=collection,
        models_only=models_only,
        fixtures_only=fixtures_only,
        templates_only=templates_only,
    )


@block_app.command("list")
def block_list_cmd(
    source: Optional[str] = typer.Option(
        None, "--source", "-s", help="Filter to a specific source"
    ),
):
    """List all available blocks from configured sources"""
    from .handlers.blocks import block_list

    block_list(source_name=source)


@block_app.command("search")
def block_search_cmd(
    query: str = typer.Argument(
        ..., help="Search query (matches ref, name, description)"
    ),
):
    """Search for blocks by name or description"""
    from .handlers.blocks import block_search

    block_search(query=query)


# Block dev subcommand group
block_dev_app = typer.Typer(
    help="Block authoring and development tools",
    no_args_is_help=True,
)
block_app.add_typer(block_dev_app, name="dev")


@block_dev_app.command("start")
def block_dev_start_cmd(
    name: Optional[str] = typer.Option(
        None, "--name", "-n", help="Directory name for the source repo"
    ),
    vendor: Optional[str] = typer.Option(
        None, "--vendor", "-v", help="Vendor key (e.g. lb)"
    ),
    package_manager: Optional[str] = typer.Option(
        None, "--package-manager", "-p", help="Package manager (poetry, pip, uv)"
    ),
):
    """Bootstrap a new block source repo with package manager setup"""
    from .handlers.blocks_dev import start

    start(name=name, vendor=vendor, package_manager=package_manager)


@block_dev_app.command("new")
def block_dev_new_cmd(
    ref: str = typer.Argument(..., help="Block ref as category/slug (e.g. crud/todos)"),
    block_type: str = typer.Option(
        "fullstack", "--type", "-t", help="Block type: fe or fullstack"
    ),
):
    """Scaffold a new block skeleton in the current source repo"""
    from .handlers.blocks_dev import new_block

    new_block(ref=ref, block_type=block_type)


@block_dev_app.command("build")
def block_dev_build_index(
    path: str = typer.Option(
        ".",
        "--path",
        "-p",
        help="Path to block source repo (default: current directory)",
    ),
):
    """Regenerate index.yaml from all block.yaml files in a source repo"""
    from .handlers.blocks_dev import build_index

    build_index(path=path)


@block_dev_app.command("validate")
def block_dev_validate_cmd(
    path: str = typer.Option(
        ".",
        "--path",
        "-p",
        help="Path to block source repo (default: current directory)",
    ),
):
    """Check all blocks in a source repo conform to the spec"""
    from .handlers.blocks_dev import validate

    validate(path=path)


@block_dev_app.command("serve")
def block_dev_serve_cmd(
    path: str = typer.Option(".", "--path", "-p", help="Path to block source repo"),
    port: int = typer.Option(8765, "--port", help="Port to serve on"),
):
    """Boot a live block renderer for the source repo"""
    from .handlers.blocks_dev import serve

    serve(path=path, port=port)


# Source subcommand group
source_app = typer.Typer(
    help="Manage block sources",
    no_args_is_help=True,
)
block_app.add_typer(source_app, name="source")


@source_app.command("add")
def source_add_cmd(
    name: str = typer.Argument(..., help="Source name"),
    url: Optional[str] = typer.Argument(None, help="Remote git URL"),
    path: Optional[str] = typer.Option(
        None, "--path", "-p", help="Local filesystem path"
    ),
    subdir: Optional[str] = typer.Option(
        None, "--subdir", help="Blocks directory inside the repo, for a monorepo source"
    ),
):
    """Add a block source (remote git repo or local path) to labb.yaml"""
    from .handlers.blocks import source_add

    source_add(name=name, url=url, path=path, subdir=subdir)


@source_app.command("list")
def source_list_cmd():
    """List all configured block sources"""
    from .handlers.blocks import source_list

    source_list()


if __name__ == "__main__":
    app()
