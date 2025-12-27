import subprocess
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from labb.cli.handlers.commons import confirm_load_config

console = Console()


def setup_project_with_config(install_deps: Optional[bool] = None):
    """Setup labb dependencies in current Django project"""

    confirm_load_config(console)
    setup_project(install_deps)


def setup_project(install_deps: Optional[bool]):
    """Install labb dependencies (Tailwind CSS CLI and DaisyUI)"""

    console.print(
        Panel.fit(
            "[bold blue]Installing labb dependencies[/bold blue]",
            border_style="blue",
        )
    )

    current_dir = Path.cwd()

    # Check if package.json exists
    package_json_path = current_dir / "package.json"
    if not package_json_path.exists():
        console.print(
            "[red]❌ Error: package.json not found. Run 'labb init' first to initialize the project.[/red]"
        )
        raise typer.Exit(1)

    if install_deps is None:
        install_node_deps = Confirm.ask(
            "Install Tailwind CSS CLI and DaisyUI?", default=True
        )
    else:
        # Use the explicitly set value
        install_node_deps = install_deps

    if install_node_deps:
        _install_tailwind_cli(current_dir)
        _install_daisyui(current_dir)
    else:
        console.print("[yellow]Skipped Node.js dependencies installation.[/yellow]")
        console.print(
            "[dim]To install manually: npm install -D tailwindcss @tailwindcss/cli daisyui@latest[/dim]"
        )

    _show_success_message()


def _install_tailwind_cli(current_dir: Path):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Installing tailwindcss & @tailwindcss/cli...", total=None)

        try:
            subprocess.run(
                ["npm", "install", "-D", "tailwindcss", "@tailwindcss/cli"],
                cwd=current_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            console.print("[green]✅ Installed tailwindcss & @tailwindcss/cli[/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]❌ Error installing Tailwind CSS CLI: {e}[/red]")
            raise typer.Exit(1)


def _install_daisyui(current_dir: Path):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Installing daisyui@latest...", total=None)

        try:
            subprocess.run(
                ["npm", "install", "-D", "daisyui@latest"],
                cwd=current_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            console.print("[green]✅ Installed daisyui@latest[/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]❌ Error installing DaisyUI: {e}[/red]")
            raise typer.Exit(1)


def _show_success_message():
    console.print(
        "\n[bold green]Dependencies installed! Run 'labb dev' to start the development mode.[/bold green]"
    )
