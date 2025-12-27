from typing import Optional

import typer

from .handlers.icons_handler import list_packs, search_icons, show_icon_info

app = typer.Typer(
    help="labbicons CLI - Search and manage icon packs",
    no_args_is_help=True,
)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search term for icon names"),
    pack: Optional[str] = typer.Option(
        None, "--pack", "-p", help="Filter by icon pack (e.g., rmx)"
    ),
    category: Optional[str] = typer.Option(
        None, "--category", "-c", help="Filter by category"
    ),
    variant: Optional[str] = typer.Option(
        None, "--variant", "-v", help="Filter by variant (fill, line)"
    ),
    limit: int = typer.Option(
        20, "--limit", "-l", help="Maximum number of results to show"
    ),
):
    """Search for icons by name, pack, category, or variant"""
    search_icons(query, pack, category, variant, limit)


@app.command()
def packs():
    """List all available icon packs"""
    list_packs()


@app.command()
def info(
    icon_identifier: str = typer.Argument(
        ..., help="Icon identifier in format 'pack.icon' (e.g., 'rmx.arrow-down')"
    ),
):
    """Show detailed information about a specific icon"""
    show_icon_info(icon_identifier)


if __name__ == "__main__":
    app()
