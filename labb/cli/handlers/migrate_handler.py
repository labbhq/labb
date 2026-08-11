"""Aided migration: css.scan.apps → css.packages.

Rewrites a labb.yaml still on the legacy `css.scan.apps` schema to the new
`css.packages` shape, and patches input.css to import the generated seam. The
old schema keeps working during the deprecation window; this just makes the
move a guided one instead of hand-editing.
"""

import sys
from pathlib import Path

import yaml

from labb.cli.handlers.commons import console

LABB_IMPORT_LINE = '@import "../.labb/labb.css";'
LABB_IMPORT_BLOCK = f"/* labb css - don't remove this line */\n{LABB_IMPORT_LINE}\n"


def _backup(path: Path) -> Path:
    """Copy `path` to `path.bak` before it gets overwritten.

    An existing backup is never clobbered: the next free `.bak.1`, `.bak.2`, …
    is used instead, so re-running the migration keeps every earlier version.
    """
    target = path.with_suffix(path.suffix + ".bak")
    n = 1
    while target.exists():
        target = path.with_suffix(f"{path.suffix}.bak.{n}")
        n += 1
    target.write_bytes(path.read_bytes())
    return target


def _plan_packages(apps: dict) -> dict:
    """Map legacy scan.apps → css.packages (components only; literals left to the user)."""
    packages = {}
    for app, patterns in apps.items():
        pats = list(patterns) if patterns else []
        packages[app] = {"components": pats} if pats else {"components": []}
    return packages


def _patch_input_css(input_path: Path) -> list:
    """Add the labb.css import if missing; return a list of manual-cleanup notes."""
    notes = []
    if not input_path.exists():
        notes.append(
            f"input.css not found at {input_path} — add {LABB_IMPORT_LINE} yourself."
        )
        return notes
    text = input_path.read_text(encoding="utf-8")

    if "labb.css" not in text:
        # Insert after the daisyui plugin block, else after @import "tailwindcss".
        anchor = '@plugin "daisyui" {\n  themes: light, dark;\n}\n'
        if anchor in text:
            text = text.replace(anchor, anchor + "\n" + LABB_IMPORT_BLOCK, 1)
        elif '@import "tailwindcss";\n' in text:
            text = text.replace(
                '@import "tailwindcss";\n',
                '@import "tailwindcss";\n\n' + LABB_IMPORT_BLOCK,
                1,
            )
        else:
            text = LABB_IMPORT_BLOCK + text
        backup = _backup(input_path)
        input_path.write_text(text, encoding="utf-8")
        console.print(f"[dim]Backed up {input_path.name} → {backup.name}[/dim]")

    # Flag things that must be removed by hand (auto-deleting CSS is unsafe).
    if "@source" in text and any(
        m in text
        for m in ("labb-fullstack-reactivity", "/labb/templates", "labbdocs/templates")
    ):
        notes.append(
            'Remove the old hardcoded `@source "...labb/templates"` lines — labb.css supplies them now.'
        )
    if '@plugin "daisyui/theme"' in text:
        notes.append(
            'Remove the inline `@plugin "daisyui/theme"` blocks — themes now come from the `themes` group.'
        )
    return notes


def migrate_config(path: str = ".", assume_yes: bool = False) -> None:
    root = Path(path).resolve()
    labb_yaml = root / "labb.yaml"
    if not labb_yaml.exists():
        console.print(f"[red]No labb.yaml at {labb_yaml}[/red]")
        raise SystemExit(1)

    data = yaml.safe_load(labb_yaml.read_text(encoding="utf-8")) or {}
    css = data.get("css") or {}
    scan = css.get("scan") or {}
    apps = scan.get("apps")

    if not apps:
        console.print("[green]Nothing to migrate — no css.scan.apps found.[/green]")
        return

    packages = dict(css.get("packages") or {})
    packages.update(_plan_packages(apps))

    console.print("[bold]Migrating css.scan.apps → css.packages[/bold]\n")
    console.print("[red]- css.scan.apps:[/red]")
    console.print(yaml.dump({"apps": apps}, sort_keys=False, indent=2))
    console.print("[green]+ css.packages:[/green]")
    console.print(yaml.dump(packages, sort_keys=False, indent=2))
    console.print(
        "[yellow]Note:[/yellow] only `components` is filled in. If this package's "
        "templates carry raw utilities (e.g. labb's cotton/lb), add a `literals` "
        "list or use a published group like `labb: all`.\n"
    )
    console.print(
        "[yellow]Note:[/yellow] labb.yaml is rewritten from parsed YAML, so comments "
        "and key order are lost. A .bak copy is written next to every file this "
        "command overwrites.\n"
    )

    if not assume_yes:
        if not sys.stdin.isatty():
            console.print(
                "[yellow]Non-interactive shell: skipping. Re-run with --yes to apply.[/yellow]"
            )
            return
        import questionary

        if not questionary.confirm("Apply this migration?", default=True).ask():
            console.print("[yellow]Migration cancelled.[/yellow]")
            return

    # 1. rewrite labb.yaml
    css["packages"] = packages
    scan.pop("apps", None)
    scan.pop("output", None)  # obsolete: safelist now lives in .labb/
    if scan:
        css["scan"] = scan
    else:
        css.pop("scan", None)
    data["css"] = css
    yaml_backup = _backup(labb_yaml)
    labb_yaml.write_text(yaml.dump(data, sort_keys=False, indent=2), encoding="utf-8")
    console.print(
        f"[green]✅ Rewrote {labb_yaml.name}[/green] "
        f"[dim](backup: {yaml_backup.name})[/dim]"
    )

    # 2. patch input.css
    input_file = (css.get("build") or {}).get("input", "static_src/input.css")
    notes = _patch_input_css(root / input_file)
    console.print(f"[green]✅ Ensured {input_file} imports labb.css[/green]")

    # 3. drop stale committed safelist + gitignore .labb/
    stale = root / "static_src" / "labb-classes.txt"
    if stale.exists():
        stale.unlink()
        console.print("[green]✅ Removed stale static_src/labb-classes.txt[/green]")
    gitignore = root / ".gitignore"
    if gitignore.exists() and ".labb/" not in gitignore.read_text(encoding="utf-8"):
        with gitignore.open("a", encoding="utf-8") as f:
            f.write(".labb/\n")
        console.print("[green]✅ Added .labb/ to .gitignore[/green]")

    if notes:
        console.print(
            "\n[bold yellow]Manual cleanup needed in input.css:[/bold yellow]"
        )
        for note in notes:
            console.print(f"  • {note}")
    console.print("\n[bold green]Done. Run `labb build` to verify.[/bold green]")
