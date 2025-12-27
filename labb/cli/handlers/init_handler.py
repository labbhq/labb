import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt

import labb.cli
from labb.cli.handlers.commons import confirm_working_in_django_project
from labb.config import LabbConfig, save_config

console = Console()


def init_project(use_defaults: bool = False, force: bool = False):
    """Initialize a new labb project with configuration and project structure"""

    console.print(
        Panel.fit(
            "[bold blue]Welcome to labb! Let's initialize your project.[/bold blue]",
            border_style="blue",
        )
    )
    confirm_working_in_django_project(Path.cwd(), console)

    # Check if config file already exists
    existing_config_names = ["labb.yaml", "labb.yml"]
    existing_config = None

    for config_name in existing_config_names:
        config_path = Path.cwd() / config_name
        if config_path.exists():
            existing_config = config_path
            break

    if existing_config:
        console.print(
            f"[yellow]⚠️  Configuration file exists: {existing_config}[/yellow]"
        )
        overwrite = Confirm.ask("Overwrite existing configuration?", default=False)
        if not overwrite:
            console.print("[yellow]Initialization cancelled[/yellow]")
            raise typer.Exit(0)

    # Create configuration with defaults or prompts
    if use_defaults:
        config = LabbConfig()
        console.print("[green]Using default configuration values[/green]")
    else:
        config = _prompt_for_config()

    config_path = Path.cwd() / "labb.yaml"
    save_config(config, config_path)

    # Create project structure
    _create_project_structure(config, force)

    _show_init_success_message()


def _prompt_for_config() -> LabbConfig:
    config = LabbConfig()

    console.print("\n[bold]CSS Configuration[/bold]")
    console.print(
        "[dim]All tailwind and daisyui configuration is done in your CSS file.[/dim]"
    )
    input_file = Prompt.ask("CSS input file", default=config.input_file)
    config.input_file = input_file

    output_file = Prompt.ask("CSS output file", default=config.output_file)
    config.output_file = output_file

    return config


def _create_project_structure(config: LabbConfig, force: bool):
    """Create the project structure (directories, CSS file, package.json)"""

    current_dir = Path.cwd()
    static_src_path = Path(config.input_file).parent
    css_file_path = Path(config.input_file)

    console.print("\n[bold]Creating project structure...[/bold]")

    _create_static_dir(static_src_path, force)
    _create_css_file(css_file_path, force)
    _init_package_json(current_dir)


def _create_static_dir(static_src_path: Path, force: bool):
    """Create the static source directory"""
    if static_src_path.exists():
        if not force:
            console.print(
                f"[yellow]📁 Directory {static_src_path} already exists[/yellow]"
            )
        else:
            console.print(
                f"[green]✅ Directory {static_src_path} already exists[/green]"
            )
    else:
        static_src_path.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]✅ Created directory: {static_src_path}[/green]")


def _create_css_file(css_file_path: Path, force: bool):
    """Create the input CSS file from template"""
    if css_file_path.exists() and not force:
        console.print(f"[yellow]📄 File {css_file_path} already exists[/yellow]")

        # Prompt user for confirmation (default: no)
        overwrite = Confirm.ask(f"Overwrite {css_file_path.name}?", default=False)

        if not overwrite:
            console.print(
                "[yellow]💡 To manually update your existing CSS file, add these lines:[/yellow]"
            )
            console.print('[dim]   @import "tailwindcss";[/dim]')
            console.print('[dim]   @plugin "daisyui";[/dim]')
            return  # Skip creation

    try:
        current_dir = Path(labb.cli.__file__).parent
        template_path = current_dir / "templates" / "input.template.css"
        template_content = template_path.read_text()

        with open(css_file_path, "w") as f:
            f.write(template_content)

        console.print(f"[green]✅ Created CSS file: {css_file_path}[/green]")

    except Exception as e:
        console.print(f"[red]❌ Error creating CSS file: {e}[/red]")
        raise typer.Exit(1)


def _init_package_json(current_dir: Path):
    """Initialize package.json if it doesn't exist"""
    package_json_path = current_dir / "package.json"

    if not package_json_path.exists():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Initializing package.json...", total=None)

            try:
                subprocess.run(
                    ["npm", "init", "-y"],
                    cwd=current_dir,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                console.print("[green]✅ Initialized package.json[/green]")
            except subprocess.CalledProcessError as e:
                console.print(f"[red]❌ Error initializing package.json: {e}[/red]")
                raise typer.Exit(1)
            except FileNotFoundError:
                console.print(
                    "[red]❌ Error: npm not found. Please install Node.js and npm[/red]"
                )
                console.print("Visit: https://nodejs.org/")
                raise typer.Exit(1)
    else:
        console.print("[green]✅ package.json already exists[/green]")


def _show_init_success_message():
    console.print(
        "\n[bold green]🎉 Project initialized! Run 'labb setup' to install dependencies.[/bold green]"
    )
