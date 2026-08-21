from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from ...metadata import get_available_packs, load_all_packs_metadata, load_pack_metadata

console = Console()


def parse_search_terms(query: str) -> List[str]:
    """Split a search query on commas, keeping order and dropping blanks.

    A query with no comma is one term, so the single-term path is unchanged.
    """
    return [term.strip() for term in query.split(",") if term.strip()]


def _match_icons(
    all_icons: List[dict],
    term: str,
    category: Optional[str],
    variant: Optional[str],
) -> List[dict]:
    """Icons whose name contains `term`, after the category/variant filters."""
    matches = []
    term_lower = term.lower()

    for icon in all_icons:
        icon_name = icon.get("name", "").lower()
        icon_category = icon.get("category", "").lower()
        icon_variants = icon.get("variants", [])

        if term_lower not in icon_name:
            continue
        if category and category.lower() not in icon_category:
            continue
        if variant and variant.lower() not in [v.lower() for v in icon_variants]:
            continue

        matches.append(icon)

    return matches


def _print_no_matches(
    term: str,
    pack: Optional[str],
    category: Optional[str],
    variant: Optional[str],
):
    console.print(f"[yellow]⚠️  No icons found matching '{term}'[/yellow]")
    if pack:
        console.print(f"[dim]Pack filter: {pack}[/dim]")
    if category:
        console.print(f"[dim]Category filter: {category}[/dim]")
    if variant:
        console.print(f"[dim]Variant filter: {variant}[/dim]")


def search_icons(
    query: str,
    pack: Optional[str] = None,
    category: Optional[str] = None,
    variant: Optional[str] = None,
    limit: int = 20,
):
    """Search for icons by name, pack, category, or variant.

    `query` may hold several comma-separated terms. Each is searched and
    reported in its own section, because picking one icon per slot is the
    reason to search for several at once: a merged table loses which term
    matched. `limit` applies per term, so a broad term cannot starve the rest.
    """

    terms = parse_search_terms(query)
    if not terms:
        console.print("[yellow]⚠️  No search terms given[/yellow]")
        return

    console.print(f"[bold blue]🔍 Searching icons for: '{query}'[/bold blue]")

    # Load metadata for specified pack or all packs
    if pack:
        metadata = load_pack_metadata(pack)
        all_icons = metadata.get("icons", [])
        if not all_icons:
            console.print(f"[red]❌ No icons found in pack '{pack}'[/red]")
            return
    else:
        # Load all packs
        all_packs_metadata = load_all_packs_metadata()
        all_icons = []
        for pack_name, pack_metadata in all_packs_metadata.items():
            all_icons.extend(pack_metadata.get("icons", []))

        if not all_icons:
            console.print("[red]❌ No icons found in any pack[/red]")
            return

    multi = len(terms) > 1

    for term in terms:
        if multi:
            console.print(f"\n[bold]{term}[/bold]")

        matches = _match_icons(all_icons, term, category, variant)

        if not matches:
            _print_no_matches(term, pack, category, variant)
            continue

        total = len(matches)
        if total > limit:
            matches = matches[:limit]
            console.print(f"[dim]Showing first {limit} results (total: {total})[/dim]")

        _display_icon_results(matches, term)


def list_packs():
    """List all available icon packs with categories"""

    console.print("[bold blue]📦 Available Icon Packs[/bold blue]")

    packs = get_available_packs()
    if not packs:
        console.print("[red]❌ No icon packs found[/red]")
        return

    # Load metadata for all packs
    all_metadata = load_all_packs_metadata()

    # Create table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Pack", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Icons", style="yellow")
    table.add_column("Categories", style="blue")
    table.add_column("Version", style="magenta")

    for pack in packs:
        metadata = all_metadata.get(pack, {})
        meta_info = metadata.get("metadata", {})
        icons = metadata.get("icons", [])
        categories = metadata.get("categories", [])

        # Use the pack name from metadata, fallback to file name
        pack_display_name = meta_info.get("pack", pack)
        pack_full_name = meta_info.get("name", pack.title())
        icon_count = len(icons)
        version = meta_info.get("version", "Unknown")

        # Create categories string with counts
        category_strings = []
        for category in sorted(categories):
            count = sum(1 for icon in icons if icon.get("category") == category)
            category_strings.append(f"{category}({count})")
        categories_display = ", ".join(category_strings)

        table.add_row(
            pack_display_name,
            pack_full_name,
            str(icon_count),
            categories_display,
            version,
        )

    console.print(table)

    # Show summary
    total_icons = sum(
        len(metadata.get("icons", [])) for metadata in all_metadata.values()
    )
    total_categories = sum(
        len(metadata.get("categories", [])) for metadata in all_metadata.values()
    )

    info_text = Text()
    info_text.append(f"Total Packs: {len(packs)}\n", style="bold")
    info_text.append(f"Total Icons: {total_icons}\n", style="green")
    info_text.append(f"Total Categories: {total_categories}", style="blue")

    console.print(Panel(info_text, title="Summary", border_style="blue"))


def show_icon_info(icon_identifier: str):
    """Show detailed information about a specific icon using pack.icon format"""

    console.print(f"[bold blue]ℹ️  Icon Information: '{icon_identifier}'[/bold blue]")

    # Parse pack.icon format
    if "." in icon_identifier:
        pack_name, icon_name = icon_identifier.split(".", 1)
    else:
        console.print(
            "[red]❌ Icon identifier must be in format 'pack.icon' (e.g., 'rmx.arrow-down')[/red]"
        )
        return

    # Load metadata for the specified pack
    # First try to find the pack by the pack name from metadata
    all_packs_metadata = load_all_packs_metadata()
    metadata = None
    icons = []

    # Look for the pack by checking the pack field in metadata
    for file_pack_name, pack_metadata in all_packs_metadata.items():
        if pack_metadata.get("metadata", {}).get("pack") == pack_name:
            metadata = pack_metadata
            icons = metadata.get("icons", [])
            break

    if not metadata or not icons:
        console.print(f"[red]❌ No icons found in pack '{pack_name}'[/red]")
        return

    matching_icons = [icon for icon in icons if icon.get("name") == icon_name]

    if not matching_icons:
        console.print(
            f"[red]❌ Icon '{icon_name}' not found in pack '{pack_name}'[/red]"
        )
        return

    for icon in matching_icons:
        variants = icon.get("variants", [])
        category = icon.get("category", "Unknown")
        component_name = icon.get("component_name", "Unknown")
        template = icon.get("template", "Unknown")
        icon_pack = icon.get("pack", "Unknown")

        # Create info panel
        info_text = Text()
        info_text.append(f"Name: {icon_name}\n", style="bold")
        info_text.append(f"Pack: {icon_pack}\n", style="magenta")
        info_text.append(f"Category: {category}\n", style="cyan")
        info_text.append(f"Component: {component_name}\n", style="green")
        info_text.append(f"Template: {template}\n", style="blue")
        info_text.append(
            f"Variants: {', '.join(variants) if variants else 'None'}", style="yellow"
        )

        console.print(Panel(info_text, title="Icon Details", border_style="green"))

        # Show usage examples using the actual component_name
        if variants:
            console.print("\n[bold]Usage Examples:[/bold]")

            for variant in variants:
                # Show both usage formats using component_name
                example1 = (
                    f'<c-component is="lbi" n="{icon_name}" variant="{variant}" />'
                )
                example2 = f'<c-lbi.{component_name} w="3" h="3" />'

                console.print(f"[bold]Variant: {variant}[/bold]")
                syntax1 = Syntax(example1, "html", theme="monokai")
                console.print(Panel(syntax1, title="Format 1", border_style="blue"))

                syntax2 = Syntax(example2, "html", theme="monokai")
                console.print(Panel(syntax2, title="Format 2", border_style="green"))
        else:
            # Show usage examples without variants using component_name
            example1 = f'<c-component is="lbi" n="{icon_name}" />'
            example2 = f'<c-lbi.{component_name} w="3" h="3" />'

            console.print("\n[bold]Usage Examples:[/bold]")
            syntax1 = Syntax(example1, "html", theme="monokai")
            console.print(Panel(syntax1, title="Format 1", border_style="blue"))

            syntax2 = Syntax(example2, "html", theme="monokai")
            console.print(Panel(syntax2, title="Format 2", border_style="green"))


def _display_icon_results(icons: List[dict], query: str):
    """Display search results in a formatted table"""

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Icon Name", style="cyan", width=25)
    table.add_column("Pack", style="magenta", width=8)
    table.add_column("Category", style="green", width=15)
    table.add_column("Variants", style="yellow", width=15)
    table.add_column("Component", style="blue", width=20)

    for icon in icons:
        name = icon.get("name", "Unknown")
        pack = icon.get("pack", "Unknown")
        category = icon.get("category", "Unknown")
        variants = ", ".join(icon.get("variants", []))
        component = icon.get("component_name", "Unknown")

        table.add_row(name, pack, category, variants, component)

    console.print(table)

    # Show summary
    console.print(f"\n[green]✅ Found {len(icons)} icon(s) matching '{query}'[/green]")
    console.print(
        "[dim]Use 'labb icons info <pack.icon>' for detailed information[/dim]"
    )
