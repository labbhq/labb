from typing import Optional

import typer

from .handlers.new_handler import create_new_project

app = typer.Typer(
    help="labbstart - Kickstart Django projects with labb",
    no_args_is_help=True,
)


@app.command()
def new(
    name: Optional[str] = typer.Argument(
        None, help="Project name (will prompt if not provided)"
    ),
    django_version: Optional[int] = typer.Option(
        None, "--django-version", "-d", help="Django version (4, 5, or 6)"
    ),
    package_manager: Optional[str] = typer.Option(
        None, "--package-manager", "-p", help="Package manager (poetry, pip, or uv)"
    ),
    kit: Optional[str] = typer.Option(
        None, "--kit", "-k", help="Starter kit to use (default: welcome)"
    ),
    app_name: Optional[str] = typer.Option(
        None, "--app-name", "-a", help="Name for the kit app (default: starter)"
    ),
):
    """Create a new Django project with labb pre-configured"""
    create_new_project(
        name=name,
        django_version=django_version,
        package_manager=package_manager,
        kit=kit,
        app_name=app_name,
    )


if __name__ == "__main__":
    app()
