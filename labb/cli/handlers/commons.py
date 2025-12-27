from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Confirm

from labb.config import LabbConfig, LabbConfigNotFound, load_config


def is_django_project(path: Path) -> bool:
    return (path / "manage.py").exists()


def confirm_working_in_django_project(path: Path, console: Console):
    if not is_django_project(path):
        console.print(
            "[yellow]⚠️  Appears not to be a Django project directory (manage.py not found).[/yellow]"
        )
        continue_anyway = Confirm.ask("Continue anyway?", default=True)
        if not continue_anyway:
            console.print("[yellow]Initialization cancelled[/yellow]")
            raise typer.Exit(0)


def confirm_load_config(console: Console) -> LabbConfig:
    try:
        config = load_config()
        console.print("[dim]Using configuration from labb.yaml[/dim]")
        return config
    except LabbConfigNotFound as e:
        console.print(
            f"[yellow]Warning: Could not resolve labb.yaml config file: {e}[/yellow]"
        )

    except Exception as e:
        console.print(f"[yellow]Warning: Could not load configuration: {e}[/yellow]")

    use_defaults = Confirm.ask("Use default labb.yaml config values?", default=True)
    if use_defaults:
        return LabbConfig()
    raise typer.Exit(0)
