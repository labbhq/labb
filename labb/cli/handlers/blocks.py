import os
import re
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich.markup import escape

from labb.cli.handlers.commons import blocks_root, commons_dir, console
from labb.config import (
    BlockCollection,
    BlocksConfig,
    BlockSource,
    find_config_file,
    load_config,
    save_config,
)

# ── Shared helpers ────────────────────────────────────────────────────────────

# Ref segments become path components, so "..", "." and separators must not fit.
_SEGMENT_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def _title_name(name: str) -> str:
    return name.title().replace("_", "").replace("-", "")


def _validate_segment(value: str, kind: str) -> None:
    if not _SEGMENT_RE.match(value):
        console.print(
            f"[red]Invalid {kind} '{value}' — must match "
            f"{escape(_SEGMENT_RE.pattern)}.[/red]"
        )
        raise typer.Exit(1)


def _parse_ref(ref: str) -> tuple[str, str, str]:
    """Split a ref into (vendor, category, slug), rejecting unsafe segments."""
    parts = ref.split("/")
    if len(parts) != 3:
        console.print(
            f"[red]Invalid ref '{ref}' — expected vendor/category/slug (3 parts, got {len(parts)}).[/red]"
        )
        raise typer.Exit(1)

    for value, kind in zip(parts, ("vendor", "category", "slug")):
        _validate_segment(value, kind)

    return parts[0], parts[1], parts[2]


def _clone_source(source: BlockSource, tmp_dir: str) -> Optional[Path]:
    """Clone a remote source and return its root, or None if unreachable."""
    try:
        result = subprocess.run(
            # "--" ensures a URL beginning with "-" is not read as a git option.
            ["git", "clone", "--depth=1", "--quiet", "--", source.url, tmp_dir],
            capture_output=True,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_ASKPASS": "true"},
            timeout=60,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None

    if result.returncode != 0:
        return None

    return Path(tmp_dir) / source.subdir if source.subdir else Path(tmp_dir)


def _fetch_index(source: BlockSource, config_dir: Optional[Path] = None) -> list[dict]:
    if source.is_local:
        raw_path = source.path
        if config_dir is not None:
            resolved = (config_dir / raw_path).resolve()
        else:
            resolved = Path(raw_path).resolve()

        index_path = resolved / "index.yaml"
        if not index_path.exists():
            console.print(
                f"[yellow]Warning: index.yaml not found for source '{source.name}' at {index_path}[/yellow]"
            )
            return []

        try:
            data = yaml.safe_load(index_path.read_text()) or {}
            return data.get("blocks", [])
        except Exception as exc:
            console.print(
                f"[yellow]Warning: failed to parse index.yaml for source '{source.name}': {exc}[/yellow]"
            )
            return []

    elif source.is_remote:
        tmp_dir = tempfile.mkdtemp()
        try:
            src_root = _clone_source(source, tmp_dir)
            if src_root is None:
                console.print(
                    f"[yellow]Warning: could not clone source '{source.name}' "
                    f"from {source.url} — skipping.[/yellow]"
                )
                return []

            index_path = src_root / "index.yaml"
            if not index_path.exists():
                console.print(
                    f"[yellow]Warning: index.yaml not found in cloned repo for source '{source.name}'[/yellow]"
                )
                return []

            try:
                data = yaml.safe_load(index_path.read_text()) or {}
                return data.get("blocks", [])
            except Exception as exc:
                console.print(
                    f"[yellow]Warning: failed to parse index.yaml for source '{source.name}': {exc}[/yellow]"
                )
                return []
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    return []


def _get_sources_and_config_dir():
    config_path = find_config_file()
    config = load_config(config_path)

    if config.blocks is None or not config.blocks.sources:
        console.print("No sources configured.")
        return None, None

    config_dir = config_path.parent if config_path is not None else None
    return config.blocks.sources, config_dir


_TABLE_COLUMNS = (
    ("ref", 30),
    ("name", 20),
    ("type", 10),
    ("tier", 10),
    ("_source", 15),
)


def _print_table(rows: list[dict]) -> None:
    cells = [
        [(row.get(key) or "")[:cap] for key, cap in _TABLE_COLUMNS] for row in rows
    ]
    if not cells:
        return
    # Empty columns are dropped, so an unused tier costs no width.
    used = [i for i in range(len(_TABLE_COLUMNS)) if any(row[i] for row in cells)]
    widths = {i: max(len(row[i]) for row in cells) for i in used}

    for row, source in zip(cells, rows):
        line = escape(" ".join(row[i].ljust(widths[i]) for i in used))
        if source.get("demo"):
            line = f"{line} [yellow]demo[/yellow]"
        console.print(line.rstrip())


@contextmanager
def _resolve_source_for_ref(
    ref_or_vendor: str,
    sources,
    config_dir,
    match_by: str = "ref",
):
    """
    Find which source owns a block ref (match_by="ref") or vendor prefix (match_by="vendor").
    Yields (matched_source, source_root, matched_entry); clones are removed on
    exit, including when nothing matched.
    Prints error and raises typer.Exit(1) if not found.
    """
    matched_source = None
    matched_entry: dict = {}
    source_root_map: dict = {}
    tmp_dirs: list = []

    try:
        for source in sources:
            if source.is_local:
                raw_path = source.path
                src_root = (
                    (config_dir / raw_path).resolve()
                    if not Path(raw_path).is_absolute()
                    else Path(raw_path)
                )
                index_file = src_root / "index.yaml"
                if not index_file.exists():
                    continue
                index_data = yaml.safe_load(index_file.read_text()) or {}
                source_root_map[source.name] = blocks_root(src_root)
            elif source.is_remote:
                tmp_dir = tempfile.mkdtemp()
                tmp_dirs.append(tmp_dir)
                src_root = _clone_source(source, tmp_dir)
                if src_root is None:
                    continue
                index_file = src_root / "index.yaml"
                if not index_file.exists():
                    continue
                index_data = yaml.safe_load(index_file.read_text()) or {}
                source_root_map[source.name] = blocks_root(src_root)
            else:
                continue

            blocks_list = index_data.get("blocks", [])
            for entry in blocks_list:
                if match_by == "ref" and entry.get("ref") == ref_or_vendor:
                    matched_source = source
                    matched_entry = entry
                    break
                elif match_by == "vendor" and entry.get("ref", "").startswith(
                    f"{ref_or_vendor}/"
                ):
                    matched_source = source
                    matched_entry = entry
                    break
            if matched_source is not None:
                break

        if matched_source is None:
            if match_by == "ref":
                console.print(f"[red]No source contains block '{ref_or_vendor}'.[/red]")
            else:
                console.print(
                    f"[red]Error: No source found for vendor '{ref_or_vendor}'. "
                    f"Run `labb block list` to see available vendors.[/red]"
                )
            raise typer.Exit(1)

        yield matched_source, source_root_map[matched_source.name], matched_entry
    finally:
        for tmp_dir in tmp_dirs:
            shutil.rmtree(tmp_dir, ignore_errors=True)


def _copy_cotton_dir(src_dir: Path, dest_dir: Path) -> None:
    """Merge a block's templates/cotton/ into <collection>/templates/cotton/.

    Cotton components resolve only from the single global templates/cotton/ root,
    so a block's cotton/ files are merged there rather than nested per-block.
    """
    for item in src_dir.rglob("*"):
        if "__pycache__" in item.parts or not item.is_file():
            continue
        rel = item.relative_to(src_dir)
        dest_file = dest_dir / rel
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, dest_file)


def _copy_commons(source_root: Path, collection_path: Path) -> bool:
    """Copy the source repo's shared components into the collection.

    Blocks are installed one at a time, so anything several of them depend on has
    to travel with each — commons is copied on every add and sync.
    """
    commons_cotton = commons_dir(source_root) / "templates" / "cotton"
    if not commons_cotton.is_dir():
        return False
    _copy_cotton_dir(commons_cotton, collection_path / "templates" / "cotton")
    return True


def _copy_block_templates(
    source_templates_dir: Path,
    collection_path: Path,
    vendor: str,
    category: str,
    slug: str,
) -> bool:
    """Copy a block's templates into the collection with the correct split.

    - templates/cotton/**  → <collection>/templates/cotton/**   (merged, global)
    - everything else       → <collection>/templates/<vendor>/<category>/<slug>/**

    Returns True if any file was copied.
    """
    if not source_templates_dir.exists():
        return False

    cotton_root = collection_path / "templates" / "cotton"
    block_root = collection_path / "templates" / vendor / category / slug
    copied = False

    for item in sorted(source_templates_dir.iterdir()):
        if item.name == "__pycache__":
            continue
        if item.name == "cotton" and item.is_dir():
            _copy_cotton_dir(item, cotton_root)
            copied = True
        elif item.is_file():
            block_root.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, block_root / item.name)
            copied = True
        elif item.is_dir():
            for sub in item.rglob("*"):
                if "__pycache__" in sub.parts or not sub.is_file():
                    continue
                rel = sub.relative_to(source_templates_dir)
                dest = block_root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(sub, dest)
            copied = True

    return copied


# ── Commands ──────────────────────────────────────────────────────────────────


def block_init(
    name: str = "blocks", path: Optional[str] = None, silent: bool = False
) -> None:
    config_path = find_config_file()
    if config_path is None:
        if not silent:
            console.print(
                "[red]No labb.yaml found. Run `labb init` to create a project first.[/red]"
            )
        raise typer.Exit(1)

    from labb.config import clear_config_cache

    clear_config_cache()
    config = load_config(config_path)

    if config.blocks is not None:
        if config.blocks.get_collection(name) is not None:
            if not silent:
                console.print(f"[red]Collection '{name}' already exists.[/red]")
            raise typer.Exit(1)

    config_dir = config_path.parent
    if path is None:
        collection_path = config_dir / name
    else:
        collection_path = Path(path)

    if collection_path.exists() and any(collection_path.iterdir()):
        if not silent:
            console.print(
                f"[yellow]⚠ Directory '{collection_path}' already exists and is non-empty — skipping folder creation.[/yellow]"
            )
    else:
        collection_path.mkdir(parents=True, exist_ok=True)
        (collection_path / "__init__.py").touch()
        (collection_path / "templates").mkdir(exist_ok=True)
        (collection_path / "fixtures").mkdir(exist_ok=True)

        models_dir = collection_path / "models"
        models_dir.mkdir(exist_ok=True)
        (models_dir / "__init__.py").touch()

        migrations_dir = collection_path / "migrations"
        migrations_dir.mkdir(exist_ok=True)
        (migrations_dir / "__init__.py").touch()

    title = _title_name(name)
    apps_py = collection_path / "apps.py"
    apps_py.write_text(
        f"from django.apps import AppConfig\n"
        f"\n"
        f"\n"
        f"class {title}Config(AppConfig):\n"
        f'    name = "{name}"\n'
        f'    label = "{name}"\n'
    )

    labbhq_source = BlockSource(
        name="labbhq",
        url="https://github.com/labbhq/labb",
        subdir="extras/blocks",
    )

    try:
        rel_path = str(collection_path.resolve().relative_to(config_dir.resolve()))
    except ValueError:
        rel_path = str(collection_path.resolve())

    new_collection = BlockCollection(
        name=name,
        path=str(collection_path.resolve()),
        default=False,
        raw_path=rel_path,
    )

    if config.blocks is None:
        new_collection.default = True
        config.blocks = BlocksConfig(
            collections=[new_collection],
            sources=[labbhq_source],
        )
    else:
        is_first = len(config.blocks.collections) == 0
        new_collection.default = is_first
        config.blocks.collections.append(new_collection)

        existing_source_names = [s.name for s in config.blocks.sources]
        if labbhq_source.name not in existing_source_names:
            config.blocks.sources.append(labbhq_source)

    save_config(config, config_path)

    if not silent:
        console.print(
            f"[green]✓ Created collection '{name}' at {collection_path}/[/green]"
        )
        console.print("[green]✓ Added labbhq as default source[/green]")
        console.print("")
        console.print("Next:")
        console.print(f"  Add '{name}' to INSTALLED_APPS in settings.py")


def block_add(ref: str, collection_name: Optional[str] = None) -> None:
    config_path = find_config_file()
    if config_path is None:
        console.print(
            "[red]No labb.yaml found. Run `labb init` to create a project first.[/red]"
        )
        raise typer.Exit(1)

    from labb.config import clear_config_cache

    clear_config_cache()
    config = load_config(config_path)

    if config.blocks is None:
        block_init(silent=True)
        clear_config_cache()
        config = load_config(config_path)

    vendor, category, slug = _parse_ref(ref)

    if collection_name is not None:
        collection = config.blocks.get_collection(collection_name)
        if collection is None:
            console.print(
                f"[red]Collection '{collection_name}' not found in labb.yaml.[/red]"
            )
            raise typer.Exit(1)
    else:
        collection = config.blocks.get_default_collection()
        if collection is None:
            console.print(
                "[red]No default collection found. Use --collection to specify one.[/red]"
            )
            raise typer.Exit(1)

    config_dir = config_path.parent
    with _resolve_source_for_ref(
        ref, config.blocks.sources, config_dir, match_by="ref"
    ) as (_, source_root, entry):
        collection_path = Path(collection.path)
        source_block_dir = source_root / category / slug
        target_block_dir = collection_path / vendor / category / slug

        if not source_block_dir.exists():
            console.print(
                f"[red]Block directory not found in source: {source_block_dir}[/red]"
            )
            raise typer.Exit(1)

        target_block_dir.mkdir(parents=True, exist_ok=True)

        for item in source_block_dir.rglob("*"):
            if "__pycache__" in item.parts:
                continue
            rel = item.relative_to(source_block_dir)
            if rel.parts and rel.parts[0] == "templates":
                continue
            dest = target_block_dir / rel
            if item.is_dir():
                dest.mkdir(parents=True, exist_ok=True)
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)

        (collection_path / vendor / "__init__.py").touch()
        (collection_path / vendor / category / "__init__.py").touch()
        (collection_path / vendor / category / slug / "__init__.py").touch()

        source_models_dir = source_root / "models"
        target_models_dir = collection_path / vendor / "models"
        new_vendor = False

        if source_models_dir.exists():
            target_models_dir.mkdir(parents=True, exist_ok=True)
            for item in source_models_dir.iterdir():
                if item.is_file():
                    target_file = target_models_dir / item.name
                    if not target_file.exists():
                        shutil.copy2(item, target_file)
                        new_vendor = True

        collection_models_init = collection_path / "models" / "__init__.py"
        # vendor package is a sibling of models/, so import one level up.
        import_line = f"from ..{vendor}.models import *"
        if collection_models_init.exists():
            current_content = collection_models_init.read_text()
            lines = [line.strip() for line in current_content.splitlines()]
            if import_line not in lines:
                new_content = current_content
                if new_content and not new_content.endswith("\n"):
                    new_content += "\n"
                new_content += import_line + "\n"
                collection_models_init.write_text(new_content)
        else:
            collection_models_init.parent.mkdir(parents=True, exist_ok=True)
            collection_models_init.write_text(import_line + "\n")

        source_templates_dir = source_block_dir / "templates"
        _copy_block_templates(
            source_templates_dir, collection_path, vendor, category, slug
        )
        _copy_commons(source_root, collection_path)

        source_fixture = source_root / "fixtures.json"
        collection_app_label = Path(collection.path).name
        target_fixture = collection_path / "fixtures" / f"{vendor}.json"
        new_fixtures = False

        if source_fixture.exists() and not target_fixture.exists():
            content = source_fixture.read_text()
            content = content.replace(f'"{vendor}.', f'"{collection_app_label}.')
            target_fixture.parent.mkdir(parents=True, exist_ok=True)
            target_fixture.write_text(content)
            new_fixtures = True

        if entry.get("demo"):
            console.print("")
            console.print(
                f"[yellow]⚠ {ref} is a UI demo. Its views do not do what they "
                f"appear to do — read them before wiring it into anything real.[/yellow]"
            )

        if new_vendor:
            console.print(f"[green]✓ Added {ref}[/green]")
            console.print("")
            console.print("Next:")
            console.print(
                f"  1. Add '{collection_app_label}' to INSTALLED_APPS (if not already done)"
            )
            console.print(
                f"  2. python manage.py makemigrations {collection_app_label}"
            )
            console.print("  3. python manage.py migrate")
            console.print("  4. Wire URLs in urls.py:")
            console.print("       from labb.contrib.blocks import include_blocks")
            console.print(f"       import {collection_app_label}")
            console.print(f'       path("", include_blocks({collection_app_label}))')
            if new_fixtures:
                console.print(
                    f"  5. Optional seed data: python manage.py loaddata {vendor}"
                )
        else:
            console.print(f"[green]✓ Added {ref}[/green]")
            console.print("")
            console.print(
                f"[dim]{vendor} vendor models already present — skipped.[/dim]"
            )
            if not new_fixtures:
                console.print(
                    f"[dim]{vendor} fixtures already present — skipped.[/dim]"
                )
            console.print("")
            console.print("If new models were introduced, run:")
            console.print(f"  python manage.py makemigrations {collection_app_label}")
            console.print("  python manage.py migrate")


def block_remove(ref: str, collection_name: Optional[str] = None) -> None:
    config_path = find_config_file()
    if config_path is None:
        console.print(
            "[red]No labb.yaml found. Run `labb init` to create a project first.[/red]"
        )
        raise typer.Exit(1)

    from labb.config import clear_config_cache

    clear_config_cache()
    config = load_config(config_path)

    if config.blocks is None:
        console.print(
            "[red]No blocks section in labb.yaml. Run `labb block init` to set up blocks.[/red]"
        )
        raise typer.Exit(1)

    vendor, category, slug = _parse_ref(ref)

    if collection_name is not None:
        collection = config.blocks.get_collection(collection_name)
        if collection is None:
            console.print(
                f"[red]Collection '{collection_name}' not found in labb.yaml.[/red]"
            )
            raise typer.Exit(1)
    else:
        collection = config.blocks.get_default_collection()
        if collection is None:
            console.print(
                "[red]No default collection found. Use --collection to specify one.[/red]"
            )
            raise typer.Exit(1)

    collection_path = Path(collection.path)

    block_dir = collection_path / vendor / category / slug
    if not block_dir.exists():
        console.print(
            f"[red]Error: {ref} is not installed in collection '{collection.name}'.[/red]"
        )
        raise typer.Exit(1)

    shutil.rmtree(block_dir)

    templates_dir = collection_path / "templates" / vendor / category / slug
    if templates_dir.exists():
        shutil.rmtree(templates_dir)

    console.print(f"[green]✓ Removed {ref}[/green]")
    console.print("")
    console.print(
        f"Models and fixtures were not removed — they may be used by other {vendor} blocks."
    )
    console.print(
        f"To clean up, remove unwanted model files from {collection_path}/{vendor}/models/ and run:"
    )
    console.print(f"  python manage.py makemigrations {collection.name}")
    console.print("  python manage.py migrate")


def block_sync(
    vendor: str,
    collection_name: Optional[str] = None,
    models_only: bool = False,
    fixtures_only: bool = False,
    templates_only: bool = False,
) -> None:
    config_path = find_config_file()
    if config_path is None:
        console.print(
            "[red]No labb.yaml found. Run `labb init` to create a project first.[/red]"
        )
        raise typer.Exit(1)

    from labb.config import clear_config_cache

    clear_config_cache()
    config = load_config(config_path)

    if config.blocks is None:
        console.print(
            "[red]Error: No blocks section in labb.yaml. Run `labb block init` first.[/red]"
        )
        raise typer.Exit(1)

    _validate_segment(vendor, "vendor")

    if collection_name is not None:
        collection = config.blocks.get_collection(collection_name)
        if collection is None:
            console.print(
                f"[red]Collection '{collection_name}' not found in labb.yaml.[/red]"
            )
            raise typer.Exit(1)
    else:
        collection = config.blocks.get_default_collection()
        if collection is None:
            console.print(
                "[red]No default collection found. Use --collection to specify one.[/red]"
            )
            raise typer.Exit(1)

    collection_path = Path(collection.path)
    collection_app_label = collection_path.name

    config_dir = config_path.parent
    with _resolve_source_for_ref(
        vendor, config.blocks.sources, config_dir, match_by="vendor"
    ) as (matched_source, source_root, _):
        vendor_dir = collection_path / vendor
        if not vendor_dir.exists():
            console.print(
                f"[red]Error: Vendor '{vendor}' is not installed in collection "
                f"'{collection.name}'. Run `labb block add` first.[/red]"
            )
            raise typer.Exit(1)

        # Templates sync by default; each *_only flag narrows to a single kind.
        any_only = models_only or fixtures_only or templates_only
        do_models = models_only or not any_only
        do_fixtures = fixtures_only or not any_only
        do_templates = templates_only or not any_only
        # A full sync also refreshes block code (views/urls/manifest/tour); the
        # narrow *_only flags never do. Without this, a block's views.py drifts
        # from source silently on every sync.
        do_code = not any_only

        synced_models = False
        if do_models:
            source_models_dir = source_root / "models"
            target_models_dir = collection_path / vendor / "models"
            if source_models_dir.exists():
                target_models_dir.mkdir(parents=True, exist_ok=True)
                for item in source_models_dir.iterdir():
                    if item.is_file():
                        dest = target_models_dir / item.name
                        shutil.copy2(item, dest)
                synced_models = True

        synced_fixtures = False
        if do_fixtures:
            source_fixture = source_root / "fixtures.json"
            target_fixture = collection_path / "fixtures" / f"{vendor}.json"
            if source_fixture.exists():
                content = source_fixture.read_text()
                content = content.replace(f'"{vendor}.', f'"{collection_app_label}.')
                target_fixture.parent.mkdir(parents=True, exist_ok=True)
                target_fixture.write_text(content)
                synced_fixtures = True

        synced_templates = False
        if do_templates:
            synced_templates = _copy_commons(source_root, collection_path)
            for category_dir in sorted(vendor_dir.iterdir()):
                if not category_dir.is_dir() or category_dir.name in (
                    "models",
                    "__pycache__",
                ):
                    continue
                for slug_dir in sorted(category_dir.iterdir()):
                    if not slug_dir.is_dir() or slug_dir.name == "__pycache__":
                        continue
                    source_templates = (
                        source_root / category_dir.name / slug_dir.name / "templates"
                    )
                    if _copy_block_templates(
                        source_templates,
                        collection_path,
                        vendor,
                        category_dir.name,
                        slug_dir.name,
                    ):
                        synced_templates = True

        synced_code = False
        if do_code:
            code_files = ("views.py", "urls.py", "block.yaml", "tour.yaml")
            for category_dir in sorted(vendor_dir.iterdir()):
                if not category_dir.is_dir() or category_dir.name in (
                    "models",
                    "__pycache__",
                ):
                    continue
                for slug_dir in sorted(category_dir.iterdir()):
                    if not slug_dir.is_dir() or slug_dir.name == "__pycache__":
                        continue
                    source_block = source_root / category_dir.name / slug_dir.name
                    for fname in code_files:
                        source_file = source_block / fname
                        if source_file.exists():
                            shutil.copy2(source_file, slug_dir / fname)
                            synced_code = True

        source_name = matched_source.name
        if synced_models:
            console.print(f"[green]✓ Synced {vendor} models from {source_name}[/green]")
        if synced_fixtures:
            console.print(
                f"[green]✓ Synced {vendor} fixtures from {source_name}[/green]"
            )
        if synced_templates:
            console.print(
                f"[green]✓ Synced {vendor} templates from {source_name}[/green]"
            )
        if synced_code:
            console.print(
                f"[green]✓ Synced {vendor} block code from {source_name}[/green]"
            )

        if do_models:
            console.print("")
            console.print("If models changed, run:")
            console.print(f"  python manage.py makemigrations {collection_app_label}")
            console.print("  python manage.py migrate")


def block_list(source_name: Optional[str] = None) -> None:
    sources, config_dir = _get_sources_and_config_dir()
    if sources is None:
        return

    if source_name is not None:
        matched = [s for s in sources if s.name == source_name]
        if not matched:
            console.print(
                f"[red]Source '{source_name}' not found in configuration.[/red]"
            )
            return
        sources = matched

    all_blocks: list[dict] = []
    for source in sources:
        blocks = _fetch_index(source, config_dir=config_dir)
        for block in blocks:
            block["_source"] = source.name
        all_blocks.extend(blocks)

    if not all_blocks:
        console.print("No blocks found.")
        return

    _print_table(all_blocks)


def block_search(query: str) -> None:
    sources, config_dir = _get_sources_and_config_dir()
    if sources is None:
        return

    q = query.lower()
    all_blocks: list[dict] = []
    for source in sources:
        blocks = _fetch_index(source, config_dir=config_dir)
        for block in blocks:
            block["_source"] = source.name
        all_blocks.extend(blocks)

    matched = [
        b
        for b in all_blocks
        if q in (b.get("ref") or "").lower()
        or q in (b.get("name") or "").lower()
        or q in (b.get("description") or "").lower()
    ]

    if not matched:
        console.print(f"No blocks found matching '{query}'.")
        return

    _print_table(matched)


def source_add(
    name: str,
    url: Optional[str],
    path: Optional[str],
    subdir: Optional[str] = None,
) -> None:
    config_path = find_config_file()
    config = load_config(config_path)

    if config.blocks is None:
        console.print(
            "[red]No blocks section found in labb.yaml. Run `labb block init` first.[/red]"
        )
        raise typer.Exit(1)

    existing_names = [s.name for s in config.blocks.sources]
    if name in existing_names:
        console.print(f"[red]A source named '{name}' already exists.[/red]")
        raise typer.Exit(1)

    if url is not None and path is not None:
        console.print("[red]Provide either --url or --path, not both.[/red]")
        raise typer.Exit(1)

    if url is None and path is None:
        console.print("[red]Provide either a URL or --path.[/red]")
        raise typer.Exit(1)

    new_source = BlockSource(name=name, url=url, path=path, subdir=subdir)
    config.blocks.sources.append(new_source)

    save_config(config, config_path)
    console.print(f"[green]✓ Added source '{name}'[/green]")


def source_list() -> None:
    config_path = find_config_file()
    config = load_config(config_path)

    if config.blocks is None or not config.blocks.sources:
        console.print("No sources configured.")
        return

    console.print("Sources:")
    for source in config.blocks.sources:
        if source.url is not None:
            location = source.url
            kind = "remote"
        else:
            location = source.path
            kind = "local"
        console.print(f"  {source.name:<12}{location:<40}({kind})")
