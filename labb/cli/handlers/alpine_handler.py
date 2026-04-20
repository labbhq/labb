from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


def generate_alpine(
    components: Optional[list[str]] = None,
    output_dir: Optional[str] = None,
):
    """Generate Alpine.js component files from component schemas."""
    from labb.components.generators.alpine_components import generate_alpine_components

    if output_dir:
        output_path = Path(output_dir)
    else:
        # Default: labb package static directory
        output_path = Path(__file__).parents[3] / "static" / "labb" / "js" / "alpine"

    label = ", ".join(components) if components else "all components"
    console.print(
        f"Generating Alpine JS for [cyan]{label}[/cyan] → [dim]{output_path}[/dim]"
    )

    try:
        generate_alpine_components(output_path, components)
        console.print("[green]✓ Done[/green]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise
