import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

import questionary
import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from labb.cli.handlers.commons import DEFAULT_BLOCKS_DIR, blocks_root, commons_dir
from labb.versions import DAISYUI_VERSION, TAILWIND_VERSION

console = Console()

PACKAGE_MANAGERS = ["poetry", "pip", "uv"]

VALID_CATEGORIES = {
    # legacy surfaces — removed once the catalogue rework contracts (ticket 0028)
    "forms",
    "marketing",
    # catalogue surfaces
    "auth",
    "dashboard",
    "data-table",
    "wizard",
    "settings",
    "hero",
    "pricing",
}
VALID_STATUSES = {"launch", "backlog"}
DEFAULT_STATUS = "backlog"

# Capability vocabulary for a tour step's `teaches:`. Closed, so a typo fails
# rather than passing silently — the catalogue's coverage matrix is generated
# from these claims, so an unchecked claim would let the matrix drift.
#
# Each value is the set of code signatures that prove the claim; a claim is
# satisfied if ANY appears in the block. An empty tuple means the capability is
# real but not mechanically detectable (it is a pattern, not a tag), so the slug
# is accepted without a code check.
CAPABILITY_SIGNATURES: dict[str, tuple[str, ...]] = {
    "signals": ("c-lbr.signals",),
    # `bind=` covers both idioms a block author actually writes: `:bind=signals.fields.x`
    # (fullstack, schema-backed) and `bind="x"` (fe, no schema). The component emits
    # data-bind itself, so block source rarely carries it.
    "binding": ("bind=", "data-bind"),
    "reactive-props": ('="$',),
    "server-actions": ("c-lbr.get", "c-lbr.post", "c-lbr.delete"),
    "morphing": ("c-lbr.get", "c-lbr.post", "c-lbr.delete"),
    # SSE has no dedicated component — a stream is opened with `c-lbr.get on="init"`
    # and served by `SSEResponse` in views.py. Key the claim on the server half.
    "sse": ("SSEResponse",),
    "replace-url": ("c-lbr.replace-url",),
    "scoped-morph": ("c-lbr.target",),
    "charts": ("c-lb.chart",),
    "live-validation": (),
    "multi-step": (),
    "theming": (),
    "zero-js": (),
}

# Fixed colours bypass the daisyUI theme, so a block carrying one cannot look
# deliberate in every theme. Semantic tokens (primary, base-100, …) are the only
# way to colour a block — which keeps theme-token gradients legal.
_TAILWIND_FIXED_PALETTE = (
    "slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|"
    "teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose"
)
_FIXED_COLOUR_PATTERNS = (
    # (?<!&) so HTML entities like &#123; are not read as colour literals
    re.compile(r"(?<!&)#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b"),
    re.compile(r"\brgba?\([^)]*\)"),
    re.compile(r"\bhsla?\([^)]*\)"),
    re.compile(
        r"\b(?:bg|text|border|from|via|to|ring|fill|stroke|outline|decoration|"
        r"accent|caret|divide|placeholder|shadow)-(?:"
        + _TAILWIND_FIXED_PALETTE
        + r")-\d{2,3}\b"
    ),
)


def _block_status(block_data: dict) -> str:
    """Effective status for a manifest; defaults to backlog (hidden) when unset."""
    return block_data.get("status") or DEFAULT_STATUS


def prompt_package_manager() -> str:
    return questionary.select(
        "Select package manager:",
        choices=[
            questionary.Choice("poetry (Recommended)", value="poetry"),
            questionary.Choice("pip (Standard)", value="pip"),
            questionary.Choice("uv (Fast)", value="uv"),
        ],
        default="poetry",
    ).ask()


def run_command(
    cmd: list,
    cwd: Optional[Path] = None,
    env: Optional[dict] = None,
    clean_env: bool = False,
) -> bool:
    try:
        if clean_env:
            command_env = os.environ.copy()
            for var in ["VIRTUAL_ENV", "POETRY_ACTIVE", "PYTHONHOME"]:
                command_env.pop(var, None)
        else:
            command_env = env or os.environ.copy()

        result = subprocess.run(
            cmd,
            cwd=cwd,
            env=command_env,
            capture_output=True,
            text=True,
            check=False,
            shell=sys.platform == "win32",
        )
        if result.returncode != 0:
            details = (result.stderr or "").strip()
            stdout = (result.stdout or "").strip()
            if stdout:
                details = f"{details}\n{stdout}" if details else stdout
            console.print(f"[red]Error: {details}[/red]")
            return False
        return True
    except Exception as e:
        console.print(f"[red]Error running command: {e}[/red]")
        return False


def setup_poetry_project(project_path: Path) -> bool:
    readme = project_path / "README.md"
    if not readme.exists():
        readme.write_text(f"# {project_path.name}\n")

    if not run_command(
        ["poetry", "init", "--no-interaction"], cwd=project_path, clean_env=True
    ):
        return False

    pyproject = project_path / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text()
        if "[tool.poetry]" in content and "package-mode" not in content:
            content = content.replace(
                "[tool.poetry]", "[tool.poetry]\npackage-mode = false"
            )
        pyproject.write_text(content)

    run_command(
        ["poetry", "config", "virtualenvs.in-project", "true", "--local"],
        cwd=project_path,
        clean_env=True,
    )
    return True


def setup_pip_project(project_path: Path) -> bool:
    if not run_command([sys.executable, "-m", "venv", "venv"], cwd=project_path):
        return False
    (project_path / "requirements.txt").write_text("# Python >=3.10\n")
    return True


def setup_uv_project(project_path: Path) -> bool:
    # --no-package keeps uv's application layout; from uv 0.12 the default became
    # a packaged src/ project, whose module name collides with startproject's.
    return run_command(["uv", "init", "--no-readme", "--no-package"], cwd=project_path)


def install_labb(project_path: Path, package_manager: str) -> bool:
    if package_manager == "poetry":
        return run_command(
            ["poetry", "add", "labbui"], cwd=project_path, clean_env=True
        )
    elif package_manager == "pip":
        pip = _pip_path(project_path)
        success = run_command([str(pip), "install", "labbui"], cwd=project_path)
        if success:
            req = project_path / "requirements.txt"
            with open(req, "a") as f:
                f.write("labbui\n")
        return success
    elif package_manager == "uv":
        return run_command(["uv", "add", "labbui"], cwd=project_path)
    return False


def get_labb_command(project_path: Path, package_manager: str) -> list:
    if package_manager == "poetry":
        return ["poetry", "run", "labb"]
    elif package_manager == "pip":
        labb_bin = _bin_dir(project_path, "venv") / (
            "labb.exe" if sys.platform == "win32" else "labb"
        )
        return [str(labb_bin)]
    elif package_manager == "uv":
        return ["uv", "run", "labb"]
    return ["labb"]


def _pip_path(project_path: Path) -> Path:
    return _bin_dir(project_path, "venv") / (
        "pip.exe" if sys.platform == "win32" else "pip"
    )


def _bin_dir(project_path: Path, venv_name: str) -> Path:
    if sys.platform == "win32":
        return project_path / venv_name / "Scripts"
    return project_path / venv_name / "bin"


# Directories to skip when discovering blocks or building template trees.
# These names are reserved and must never be treated as category/slug dirs.
_SKIP_DIRS = {
    "commons",
    "models",
    "migrations",
    "fixtures",
    "templates",
    "__pycache__",
    ".labb",
    ".git",
    "dist",
    "venv",
    ".venv",
    "node_modules",
}


# ── Shared helpers ────────────────────────────────────────────────────────────


def _print_block_result(ref: str, errors: list[str], warnings: list[str]) -> None:
    if errors:
        print(f"✗ {ref}")
        for msg in errors:
            print(f"    - {msg}")
    elif warnings:
        print(f"⚠  {ref}")
        for msg in warnings:
            print(f"    - {msg}")
    else:
        print(f"✓ {ref}")


def _ensure_gitignore(repo_path: Path) -> None:
    gitignore = repo_path / ".gitignore"
    entry = ".labb/"

    if gitignore.exists():
        lines = gitignore.read_text(encoding="utf-8").splitlines()
        if entry in lines:
            return
        existing = gitignore.read_text(encoding="utf-8")
        if not existing.endswith("\n"):
            existing += "\n"
        gitignore.write_text(existing + entry + "\n", encoding="utf-8")
    else:
        gitignore.write_text(entry + "\n", encoding="utf-8")


def _merge_cotton_dir(src_dir: Path, dest_dir: Path) -> None:
    """Merge a block's templates/cotton/ into .labb/templates/cotton/."""
    import shutil

    for item in src_dir.rglob("*"):
        if not item.is_file():
            continue
        rel = item.relative_to(src_dir)
        dest_file = dest_dir / rel
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            if dest_file.exists() or dest_file.is_symlink():
                dest_file.unlink()
            dest_file.symlink_to(item.resolve())
        except (OSError, NotImplementedError):
            shutil.copy2(item, dest_file)


def _symlink_subdir(src_dir: Path, dest_dir: Path) -> None:
    """Recursively symlink all files from src_dir into dest_dir."""
    import shutil

    dest_dir.mkdir(parents=True, exist_ok=True)
    for item in sorted(src_dir.rglob("*")):
        if not item.is_file():
            continue
        rel = item.relative_to(src_dir)
        dest_file = dest_dir / rel
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            dest_file.symlink_to(item.resolve())
        except (OSError, NotImplementedError):
            shutil.copy2(item, dest_file)


def _build_template_tree(repo_path: Path, vendor: str) -> None:
    """
    Symlink block templates into .labb/templates/{vendor}/{category}/{slug}/.

    Source repo structure: {category}/{slug}/templates/ (no vendor prefix in path).
    Cotton subdirectories (templates/cotton/) are merged into .labb/templates/cotton/
    so they are accessible as normal cotton components.
    Subdirectories other than cotton/ (e.g. pages/) are symlinked recursively.

    commons/templates/cotton/ is merged the same way, so components shared by
    several blocks are authored once.
    """
    import shutil

    labb_templates = repo_path / ".labb" / "templates"
    src_root = blocks_root(repo_path)

    if labb_templates.exists():
        shutil.rmtree(labb_templates)
    labb_templates.mkdir(parents=True)

    for category_dir in sorted(src_root.iterdir()):
        if not category_dir.is_dir():
            continue
        if (
            category_dir.name in _SKIP_DIRS
            or category_dir.name.startswith(".")
            or category_dir.name.startswith("_")
        ):
            continue

        for slug_dir in sorted(category_dir.iterdir()):
            if not slug_dir.is_dir() or slug_dir.name.startswith("_"):
                continue

            templates_src = slug_dir / "templates"
            if not templates_src.exists() or not templates_src.is_dir():
                continue

            dest_dir = labb_templates / vendor / category_dir.name / slug_dir.name
            dest_dir.mkdir(parents=True, exist_ok=True)

            for src_item in sorted(templates_src.iterdir()):
                if src_item.name == "cotton" and src_item.is_dir():
                    _merge_cotton_dir(src_item, labb_templates / "cotton")
                elif src_item.is_file():
                    dest_file = dest_dir / src_item.name
                    try:
                        dest_file.symlink_to(src_item.resolve())
                    except (OSError, NotImplementedError):
                        shutil.copy2(src_item, dest_file)
                elif src_item.is_dir():
                    _symlink_subdir(src_item, dest_dir / src_item.name)

    commons_cotton = commons_dir(src_root) / "templates" / "cotton"
    if commons_cotton.is_dir():
        _merge_cotton_dir(commons_cotton, labb_templates / "cotton")


def _build_vendor_package(repo_path: Path, vendor: str) -> None:
    """
    Create a synthetic vendor Python package at .labb/{vendor}/ that wraps the
    source repo's models and block categories. This lets Django and lm() treat the
    vendor as a normal app package (e.g. 'lb') without requiring a vendor directory
    in the source repo's folder structure.

    After this call, adding repo_path/.labb to sys.path makes `import {vendor}`
    resolve to a package containing:
      {vendor}.models  → repo_path/models/
      {vendor}.crud    → repo_path/crud/   (and other category dirs)
    """
    import shutil

    vendor_pkg = repo_path / ".labb" / vendor
    if vendor_pkg.exists():
        shutil.rmtree(vendor_pkg)
    vendor_pkg.mkdir(parents=True)

    (vendor_pkg / "__init__.py").write_text("")

    src_root = blocks_root(repo_path)
    models_src = src_root / "models"
    if models_src.exists():
        (vendor_pkg / "models").symlink_to(models_src.resolve())

    for item in sorted(src_root.iterdir()):
        if not item.is_dir():
            continue
        if (
            item.name in _SKIP_DIRS
            or item.name.startswith(".")
            or item.name.startswith("_")
        ):
            continue
        (vendor_pkg / item.name).symlink_to(item.resolve())


def _discover_blocks(repo_path: Path) -> dict:
    """
    Discover blocks in a source repo. Blocks live at {category}/{slug}/block.yaml
    (no vendor prefix in the path — vendor is declared in blocks.yaml).
    Returns {(category, slug): {"type": ..., "preview_context": ...}}.
    """
    discovered = {}
    src_root = blocks_root(repo_path)

    for block_yaml_path in sorted(src_root.glob("*/*/block.yaml")):
        parts = block_yaml_path.relative_to(src_root).parts
        if any(part in _SKIP_DIRS for part in parts):
            continue
        if any(part.startswith(".") for part in parts):
            continue

        slug = block_yaml_path.parent.name
        category = block_yaml_path.parent.parent.name

        try:
            with block_yaml_path.open("r", encoding="utf-8") as f:
                block_meta = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: could not parse {block_yaml_path}: {e}")
            continue

        block_type = block_meta.get("type", "fe")
        discovered[(category, slug)] = {
            "type": block_type,
            "name": block_meta.get("name", slug),
            "description": block_meta.get("description", ""),
            "preview_context": block_meta.get("preview_context", {}),
            "tags": block_meta.get("tags", []),
            "status": _block_status(block_meta),
            "thumbnail": block_meta.get("thumbnail"),
        }

    return discovered


def _read_vendor(blocks_yaml_path: Path) -> str:
    content = blocks_yaml_path.read_text()
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("vendor:"):
            value = line[len("vendor:") :].strip()
            if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")
            ):
                value = value[1:-1]
            return value
    console.print("[red]Error: No 'vendor' key found in blocks.yaml.[/red]")
    raise typer.Exit(1)


def _create_block_yaml(
    block_dir: Path, vendor: str, slug: str, full_ref: str, block_type: str, today: str
) -> None:
    name = slug.replace("-", " ").title()
    content = (
        f"name: {name}\n"
        f"ref: {full_ref}\n"
        f"type: {block_type}\n"
        f"tier: free\n"
        f'labb_version: ">=0.5.0"\n'
        f'description: ""\n'
        f"changelog:\n"
        f'  - date: "{today}"\n'
        f"    notes:\n"
        f'      - "Initial release"\n'
    )
    (block_dir / "block.yaml").write_text(content)


def _create_template(
    templates_dir: Path, vendor: str, category: str, slug: str
) -> None:
    pages_dir = templates_dir / "pages"
    pages_dir.mkdir()
    (pages_dir / "index.html").write_text(
        f"<div>\n  <!-- {vendor}/{category}/{slug} -->\n</div>\n"
    )


def _create_views_py(block_dir: Path, vendor: str, category: str, slug: str) -> None:
    template_path = f"{vendor}/{category}/{slug}/pages/index.html"
    content = (
        "from labb.contrib.blocks import lm, render_page\n"
        "\n"
        '# LbMyModel = lm("LbMyModel")\n'
        "\n"
        f'TEMPLATE = "{template_path}"\n'
        "\n"
        "\n"
        "def index(request):\n"
        "    return render_page(request, TEMPLATE, {})\n"
    )
    (block_dir / "views.py").write_text(content)


def _create_urls_py(block_dir: Path, category: str, slug: str) -> None:
    slug_underscored = slug.replace("-", "_")
    app_name = f"block_{category}_{slug_underscored}"
    content = (
        "from django.urls import path\n"
        "\n"
        "from . import views\n"
        "\n"
        f'app_name = "{app_name}"\n'
        "\n"
        "urlpatterns = [\n"
        '    path("", views.index, name="index"),\n'
        "]\n"
    )
    (block_dir / "urls.py").write_text(content)


def _create_blocks_yaml(project_path: Path, vendor: str, name: str) -> None:
    content = (
        f"vendor: {vendor}\n"
        f"name: {name}\n"
        f'description: ""\n'
        f"blocks_dir: {DEFAULT_BLOCKS_DIR}\n"
    )
    (project_path / "blocks.yaml").write_text(content)


def _create_models_init(project_path: Path) -> None:
    """Create models/__init__.py beside the categories so lm() can resolve models."""
    models_dir = blocks_root(project_path) / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    (models_dir / "__init__.py").write_text("")


def _create_gitignore(project_path: Path) -> None:
    content = (
        "__pycache__/\n"
        "*.py[cod]\n"
        "*.so\n"
        ".Python\n"
        "*.egg-info/\n"
        "venv/\n"
        ".venv/\n"
        "*.log\n"
        "node_modules/\n"
        ".labb/\n"
    )
    (project_path / ".gitignore").write_text(content)


def _create_block_labb_yaml(project_path: Path) -> None:
    """CSS config for the block repo: pull in labb's themes + block-renderer CSS."""
    content = (
        "css:\n"
        "  build:\n"
        "    input: static_src/input.css\n"
        "    output: static/css/output.css\n"
        "    minify: true\n"
        "  packages:\n"
        "    labb: [themes, blocks]\n"
        "  scan:\n"
        "    templates:\n"
        "    - templates/**/*.html\n"
        "    - '*/templates/**/*.html'\n"
        "    - '**/templates/**/*.html'\n"
    )
    (project_path / "labb.yaml").write_text(content)


def _create_block_input_css(project_path: Path) -> None:
    """Write static_src/input.css from the shared scaffold template (single seam)."""
    import labb.cli

    template = Path(labb.cli.__file__).parent / "templates" / "input.template.css"
    src_dir = project_path / "static_src"
    src_dir.mkdir(parents=True, exist_ok=True)
    (src_dir / "input.css").write_text(template.read_text(encoding="utf-8"))


def _create_block_package_json(project_path: Path, name: str) -> None:
    content = {
        "name": name,
        "version": "1.0.0",
        "private": True,
        "devDependencies": {
            "@tailwindcss/cli": TAILWIND_VERSION,
            "daisyui": DAISYUI_VERSION,
            "tailwindcss": TAILWIND_VERSION,
        },
    }
    (project_path / "package.json").write_text(json.dumps(content, indent=2) + "\n")


def _create_readme(project_path: Path, name: str, labb_cmd: str) -> None:
    content = f"""# {name}

A labb block source repo.

## Development

Start the block renderer:
```
{labb_cmd} block dev serve
```

Scaffold a new block:
```
{labb_cmd} block dev new crud/my-block
```

Validate all blocks:
```
{labb_cmd} block dev validate
```

Build the index:
```
{labb_cmd} block dev build
```
"""
    (project_path / "README.md").write_text(content)


def _create_renderer_base_template(repo_path: Path) -> None:
    """Write a minimal base.html into .labb/templates/ for block previews."""
    base = repo_path / ".labb" / "templates" / "base.html"
    base.parent.mkdir(parents=True, exist_ok=True)
    base.write_text(
        "{% load lb_tags %}\n"
        "<!DOCTYPE html>\n"
        '<html lang="en" {% labb_theme %}>\n'
        "<head>\n"
        '    <meta charset="UTF-8">\n'
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        "    <title>{% block title %}Block Preview{% endblock %}</title>\n"
        "    <c-lbb.dependencies />\n"
        "    {% block head %}{% endblock %}\n"
        "</head>\n"
        '<body class="min-h-screen bg-base-100 antialiased">\n'
        '    <div data-on:popstate__window="@get(location.pathname)" hidden></div>\n'
        "    {% block body %}{% endblock %}\n"
        "</body>\n"
        "</html>\n",
        encoding="utf-8",
    )


# ── Commands ──────────────────────────────────────────────────────────────────


def build_index(path: str = ".") -> None:
    root = Path(path).resolve()

    blocks_yaml_path = root / "blocks.yaml"
    if not blocks_yaml_path.exists():
        print(f"Error: blocks.yaml not found at {blocks_yaml_path}")
        return

    with blocks_yaml_path.open("r", encoding="utf-8") as f:
        blocks_config = yaml.safe_load(f) or {}

    vendor = blocks_config.get("vendor", "")
    src_root = blocks_root(root)

    blocks = []

    for block_yaml_path in sorted(src_root.glob("*/*/block.yaml")):
        parts = block_yaml_path.relative_to(src_root).parts
        if any(part in _SKIP_DIRS for part in parts):
            continue

        slug = block_yaml_path.parent.name
        category = block_yaml_path.parent.parent.name

        try:
            with block_yaml_path.open("r", encoding="utf-8") as f:
                block_data = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: could not parse {block_yaml_path}: {e}")
            continue

        required_fields = ["name", "type", "description"]
        missing = [field for field in required_fields if field not in block_data]
        if missing:
            print(
                f"Warning: skipping {block_yaml_path} — missing required field(s): {', '.join(missing)}"
            )
            continue

        ref = f"{vendor}/{category}/{slug}"

        entry = {
            "ref": ref,
            "name": block_data["name"],
            "type": block_data["type"],
            "description": block_data["description"],
        }
        if "tier" in block_data:
            entry["tier"] = block_data["tier"]
        if block_data.get("category"):
            entry["category"] = block_data["category"]
        if block_data.get("tags"):
            entry["tags"] = block_data["tags"]
        entry["status"] = _block_status(block_data)
        if block_data.get("thumbnail"):
            entry["thumbnail"] = block_data["thumbnail"]

        blocks.append(entry)

    index_path = root / "index.yaml"
    with index_path.open("w", encoding="utf-8") as f:
        yaml.dump(
            {"blocks": blocks},
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )

    print(f"✓ Indexed {len(blocks)} blocks → index.yaml")


def _block_template_files(block_dir: Path) -> list[Path]:
    templates_dir = block_dir / "templates"
    if not templates_dir.exists():
        return []
    return sorted(f for f in templates_dir.rglob("*") if f.is_file())


def _default_tour_file(block_dir: Path) -> Optional[Path]:
    """The file a tour step points at when it does not name one."""
    index = block_dir / "templates" / "index.html"
    if index.exists():
        return index
    templates = _block_template_files(block_dir)
    return templates[0] if len(templates) == 1 else None


def _resolve_match(lines: list[str], needle: str) -> tuple[Optional[int], int]:
    """Resolve a tour step's `match:` to a 1-indexed line. Returns (line, hits)."""
    hits = [i for i, line in enumerate(lines, start=1) if needle in line]
    if len(hits) == 1:
        return hits[0], 1
    return None, len(hits)


def _validate_tour(block_dir: Path, errors: list[str]) -> None:
    """Validate a block's tour.yaml against the code it claims to teach.

    Two guarantees, and they are the reason the template needs no markers:
    a `match:` must resolve to exactly one line (so the highlight is never
    arbitrary and can never silently rot), and a `teaches:` claim must be borne
    out by the code (so the coverage matrix is derived, not asserted).
    """
    tour_path = block_dir / "tour.yaml"
    if not tour_path.exists():
        return

    try:
        with tour_path.open("r", encoding="utf-8") as f:
            tour = yaml.safe_load(f) or {}
    except Exception as e:
        errors.append(f"tour.yaml could not be parsed: {e}")
        return

    steps = tour.get("steps")
    if not isinstance(steps, list) or not steps:
        errors.append("tour.yaml has no steps")
        return

    # Everything the block ships — a teaches: claim may be proven by any of it.
    searchable = _block_template_files(block_dir) + [
        block_dir / "views.py",
        block_dir / "urls.py",
    ]
    block_source = "\n".join(
        f.read_text(encoding="utf-8") for f in searchable if f.exists()
    )

    for n, step in enumerate(steps, start=1):
        label = step.get("title") or f"step {n}"

        needle = step.get("match")
        if not needle:
            errors.append(f"tour step '{label}' has no match:")
        teaches = step.get("teaches")
        if not teaches:
            errors.append(f"tour step '{label}' has no teaches: (it is required)")
        elif not isinstance(teaches, list):
            errors.append(f"tour step '{label}': teaches must be a list")
        else:
            for cap in teaches:
                if cap not in CAPABILITY_SIGNATURES:
                    errors.append(
                        f"tour step '{label}': unknown capability '{cap}' "
                        f"(known: {', '.join(sorted(CAPABILITY_SIGNATURES))})"
                    )
                    continue
                signatures = CAPABILITY_SIGNATURES[cap]
                if signatures and not any(sig in block_source for sig in signatures):
                    errors.append(
                        f"tour step '{label}': teaches '{cap}' but the block's code "
                        f"contains none of {', '.join(signatures)}"
                    )

        if not needle:
            continue

        if step.get("file"):
            target = block_dir / step["file"]
            if not target.exists():
                errors.append(
                    f"tour step '{label}': file '{step['file']}' does not exist"
                )
                continue
        else:
            target = _default_tour_file(block_dir)
            if target is None:
                errors.append(
                    f"tour step '{label}': block has no templates/index.html and more than one "
                    "template — name the file explicitly with file:"
                )
                continue

        lines = target.read_text(encoding="utf-8").splitlines()

        line, hits = _resolve_match(lines, needle)
        if line is None:
            if hits == 0:
                errors.append(
                    f"tour step '{label}': match '{needle}' resolves to nothing in {target.name} "
                    "— the code it points at has changed or gone"
                )
            else:
                errors.append(
                    f"tour step '{label}': match '{needle}' is ambiguous "
                    f"({hits} matches in {target.name}) — make it unique"
                )
            continue

        end = step.get("through")
        if end:
            end_line, end_hits = _resolve_match(lines, end)
            if end_line is None:
                if end_hits == 0:
                    errors.append(
                        f"tour step '{label}': through '{end}' resolves to nothing in {target.name}"
                    )
                else:
                    errors.append(
                        f"tour step '{label}': through '{end}' is ambiguous "
                        f"({end_hits} matches in {target.name})"
                    )
            elif end_line < line:
                errors.append(
                    f"tour step '{label}': through '{end}' (line {end_line}) resolves above "
                    f"match '{needle}' (line {line})"
                )


def _allowed_fixed_colours(block_dir: Path) -> set[str]:
    """Curated fixed colours a block may hardcode, declared in block.yaml as
    `allow_fixed_colours: ["#6366f1", …]`.

    The one sanctioned exception to token-only colour: a deliberate brand gradient
    that must render *identically* in every theme (so it cannot be a theme token,
    which changes per theme). Narrow by construction — only the exact listed values
    pass; every other fixed colour still fails.
    """
    manifest = block_dir / "block.yaml"
    if not manifest.exists():
        return set()
    try:
        data = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
    except Exception:
        return set()
    return {str(v).strip().lower() for v in (data.get("allow_fixed_colours") or [])}


def _validate_theme_tokens(block_dir: Path, errors: list[str]) -> None:
    """Fail a block that hardcodes a colour.

    Blocks must look deliberate in every daisyUI theme, and a fixed colour cannot.
    Theme-token gradients (from-primary) stay legal — only the fixed palette is caught.
    A block may allowlist a curated set via block.yaml `allow_fixed_colours` for a
    deliberate cross-theme brand gradient (see _allowed_fixed_colours).
    """
    allowed = _allowed_fixed_colours(block_dir)
    for template in _block_template_files(block_dir):
        for n, line in enumerate(
            template.read_text(encoding="utf-8").splitlines(), start=1
        ):
            for pattern in _FIXED_COLOUR_PATTERNS:
                for hit in pattern.findall(line):
                    if hit.strip().lower() in allowed:
                        continue
                    errors.append(
                        f"fixed colour '{hit}' in {template.name}:{n} — blocks must survive every "
                        "daisyUI theme; use a theme token (primary, base-100, base-content, …)"
                    )


def validate(path: str = ".") -> bool:
    root = Path(path).resolve()

    errors: list[str] = []
    warnings: list[str] = []

    blocks_yaml_path = root / "blocks.yaml"
    if not blocks_yaml_path.exists():
        print(f"Error: blocks.yaml not found at {root}")
        raise typer.Exit(code=1)

    try:
        with blocks_yaml_path.open("r", encoding="utf-8") as f:
            blocks_config = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Error: could not parse blocks.yaml: {e}")
        raise typer.Exit(code=1)

    repo_errors: list[str] = []
    repo_warnings: list[str] = []

    if not blocks_config.get("vendor"):
        repo_errors.append("blocks.yaml is missing required 'vendor' key")

    src_root = blocks_root(root)
    models_dir = src_root / "models"
    if models_dir.exists() and any(models_dir.iterdir()):
        if not (models_dir / "__init__.py").exists():
            repo_warnings.append(f"{models_dir.name}/__init__.py is missing")
        if not (src_root / "fixtures.json").exists():
            repo_warnings.append(
                f"fixtures.json is missing at {src_root} (required when models exist)"
            )

    if repo_errors or repo_warnings:
        for msg in repo_errors:
            print(f"✗ [repo] {msg}")
        for msg in repo_warnings:
            print(f"⚠  [repo] {msg}")
        print()

    if repo_errors:
        print("Aborting: repo-level errors must be fixed before block validation.")
        raise typer.Exit(code=1)

    block_yaml_paths = sorted(src_root.glob("*/*/block.yaml"))
    valid_block_paths = []
    for p in block_yaml_paths:
        parts = p.relative_to(src_root).parts
        if any(part in _SKIP_DIRS for part in parts):
            continue
        valid_block_paths.append(p)

    print(f"Validating {len(valid_block_paths)} blocks...")
    print()

    passed = 0
    failed = 0
    warned = 0

    required_fields = ["name", "ref", "type", "labb_version", "description"]
    valid_types = {"fe", "fullstack"}

    for block_yaml_path in valid_block_paths:
        slug = block_yaml_path.parent.name
        category = block_yaml_path.parent.parent.name
        ref = f"{category}/{slug}"
        block_dir = block_yaml_path.parent

        block_errors: list[str] = []
        block_warnings: list[str] = []

        try:
            with block_yaml_path.open("r", encoding="utf-8") as f:
                block_data = yaml.safe_load(f) or {}
        except Exception as e:
            block_errors.append(f"block.yaml could not be parsed: {e}")
            _print_block_result(ref, block_errors, block_warnings)
            failed += 1
            errors.extend(block_errors)
            continue

        for field in required_fields:
            if field not in block_data:
                block_errors.append(f"block.yaml missing field: {field}")

        block_type = block_data.get("type")
        if block_type is not None and block_type not in valid_types:
            block_errors.append(
                f"invalid type '{block_type}' (must be 'fe' or 'fullstack')"
            )

        block_category = block_data.get("category")
        if block_category is not None and block_category not in VALID_CATEGORIES:
            block_errors.append(
                f"invalid category '{block_category}' "
                f"(must be one of {', '.join(sorted(VALID_CATEGORIES))})"
            )

        block_status = block_data.get("status")
        if block_status is not None and block_status not in VALID_STATUSES:
            block_errors.append(
                f"invalid status '{block_status}' (must be 'launch' or 'backlog')"
            )

        block_tags = block_data.get("tags")
        if block_tags is not None and not (
            isinstance(block_tags, list) and all(isinstance(t, str) for t in block_tags)
        ):
            block_errors.append("tags must be a list of strings")

        block_thumbnail = block_data.get("thumbnail")
        if block_thumbnail is not None and not isinstance(block_thumbnail, str):
            block_errors.append("thumbnail must be a string path")

        if not block_thumbnail:
            # Warn, never fail: a block captured before the light/dark split
            # still renders, it just does not follow the theme.
            missing = [
                mode
                for mode in ("light", "dark")
                if not (block_dir / "thumbnails" / f"{slug}.{mode}.png").is_file()
            ]
            if len(missing) == 1:
                block_warnings.append(
                    f"thumbnails/{slug}.{missing[0]}.png is missing "
                    f"(run scripts/capture_thumbnails.py)"
                )

        templates_dir = block_dir / "templates"
        if not templates_dir.exists():
            block_errors.append("templates/ directory is missing")
        else:
            template_files = list(templates_dir.rglob("*"))
            template_files = [f for f in template_files if f.is_file()]
            if not template_files:
                block_errors.append("templates/ directory is empty")

        if block_type == "fullstack":
            views_py = block_dir / "views.py"
            urls_py = block_dir / "urls.py"

            if not views_py.exists():
                block_errors.append(
                    "views.py is missing (required for fullstack blocks)"
                )
            else:
                views_content = views_py.read_text(encoding="utf-8")
                if "from labb.contrib.blocks import lt" in views_content:
                    block_errors.append(
                        "views.py imports 'lt' — use 'lm' instead (from labb.contrib.blocks import lm)"
                    )
                elif "from labb.contrib.blocks import lm" not in views_content:
                    block_warnings.append(
                        "views.py does not import 'lm' from labb.contrib.blocks"
                    )

            if not urls_py.exists():
                block_errors.append(
                    "urls.py is missing (required for fullstack blocks)"
                )

        elif block_type == "fe":
            if "preview_context" not in block_data:
                block_warnings.append(
                    "no preview_context defined (FE-only block will render with empty context)"
                )

        _validate_tour(block_dir, block_errors)
        _validate_theme_tokens(block_dir, block_errors)

        _print_block_result(ref, block_errors, block_warnings)

        if block_errors:
            failed += 1
            errors.extend(block_errors)
        elif block_warnings:
            warned += 1
            warnings.extend(block_warnings)
        else:
            passed += 1

    parts_out = []
    if passed:
        parts_out.append(f"{passed} passed")
    if failed:
        parts_out.append(f"{failed} failed")
    if warned:
        parts_out.append(f"{warned} warning{'s' if warned != 1 else ''}")

    print(", ".join(parts_out) if parts_out else "No blocks found.")

    if errors:
        raise typer.Exit(code=1)

    return True


def new_block(ref: str, block_type: str = "fullstack") -> None:
    parts = ref.split("/")
    if len(parts) != 2:
        console.print(
            f"[red]Error: ref must be category/slug (e.g. crud/todos), got: '{ref}'[/red]"
        )
        raise typer.Exit(1)

    category, slug = parts[0], parts[1]

    blocks_yaml_path = Path.cwd() / "blocks.yaml"
    if not blocks_yaml_path.exists():
        console.print(
            "[red]Error: No blocks.yaml found. "
            "Run `labb block dev start` to create a source repo first.[/red]"
        )
        raise typer.Exit(1)

    vendor = _read_vendor(blocks_yaml_path)
    full_ref = f"{vendor}/{category}/{slug}"

    src_root = blocks_root(Path.cwd())
    block_dir = src_root / category / slug
    if block_dir.exists():
        console.print(
            f"[red]Error: {block_dir.relative_to(Path.cwd())}/ already exists.[/red]"
        )
        raise typer.Exit(1)

    block_dir.mkdir(parents=True)
    templates_dir = block_dir / "templates"
    templates_dir.mkdir()

    today = datetime.date.today().isoformat()

    _create_block_yaml(block_dir, vendor, slug, full_ref, block_type, today)
    _create_template(templates_dir, vendor, category, slug)

    if block_type == "fullstack":
        _create_views_py(block_dir, vendor, category, slug)
        _create_urls_py(block_dir, category, slug)

    files_created = [
        f"  {category}/{slug}/block.yaml",
    ]
    if block_type == "fullstack":
        files_created.append(f"  {category}/{slug}/views.py")
        files_created.append(f"  {category}/{slug}/urls.py")
    files_created.append(f"  {category}/{slug}/templates/index.html")

    files_list = "\n".join(files_created)
    console.print(f"[green]✓ Created {full_ref}[/green]\n")
    console.print(f"[bold]Files:[/bold]\n{files_list}\n")
    console.print(
        "[bold]Next:[/bold]\n"
        "  labb block dev serve                to preview in the renderer\n"
        "  labb block dev validate             to check spec conformance"
    )


def start(
    name: Optional[str] = None,
    vendor: Optional[str] = None,
    package_manager: Optional[str] = None,
) -> None:
    console.print(
        Panel.fit(
            "[bold cyan]🧱 Create a new labb block source repo[/bold cyan]",
            border_style="cyan",
        )
    )

    if not vendor:
        vendor = questionary.text(
            "Vendor key (e.g. lb, myco):",
            validate=lambda v: bool(re.match(r"^[a-z][a-z0-9]*$", v.strip()))
            or "Vendor key must be lowercase letters only (e.g. lb, myco)",
        ).ask()
        if vendor is None:
            raise typer.Exit(1)
        vendor = vendor.strip()

    if not name:
        name = questionary.text(
            "Directory name:",
            default=f"{vendor}-blocks",
        ).ask()
        if name is None:
            raise typer.Exit(1)
        name = name.strip()

    if not package_manager:
        package_manager = prompt_package_manager()
        if package_manager is None:
            raise typer.Exit(1)

    pkg_mgr = package_manager

    project_path = Path.cwd() / name
    if project_path.exists():
        console.print(f"[red]Error: Directory '{name}' already exists.[/red]")
        raise typer.Exit(1)

    project_path.mkdir(parents=True)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Setting up package manager...", total=None)
        if pkg_mgr == "poetry":
            success = setup_poetry_project(project_path)
        elif pkg_mgr == "pip":
            success = setup_pip_project(project_path)
        elif pkg_mgr == "uv":
            success = setup_uv_project(project_path)
        else:
            success = False

        if not success:
            progress.remove_task(task)
            console.print("[red]Error: Failed to set up package manager.[/red]")
            raise typer.Exit(1)
        progress.remove_task(task)

        task = progress.add_task("Installing labbui...", total=None)
        if not install_labb(project_path, pkg_mgr):
            progress.remove_task(task)
            console.print("[red]Error: Failed to install labbui.[/red]")
            raise typer.Exit(1)
        progress.remove_task(task)

    labb_cmd = " ".join(get_labb_command(project_path, pkg_mgr))

    _create_blocks_yaml(project_path, vendor, name)
    _create_models_init(project_path)
    _create_gitignore(project_path)
    _create_readme(project_path, name, labb_cmd)
    _create_block_labb_yaml(project_path)
    _create_block_input_css(project_path)
    _create_block_package_json(project_path, name)

    success_message = (
        f"[bold green]✨ Created '{name}'![/bold green]\n\n"
        f"[bold]Next steps:[/bold]\n"
        f"  [cyan]cd {name}[/cyan]\n"
        f"  [cyan]{labb_cmd} block dev new crud/my-block[/cyan]   # scaffold your first block\n"
        f"  [cyan]{labb_cmd} block dev serve[/cyan]               # start the renderer"
    )
    console.print(Panel(success_message, border_style="green", padding=(1, 2)))


def serve(path: str = ".", port: int = 8765) -> None:
    repo_path = Path(path).resolve()

    blocks_yaml_path = repo_path / "blocks.yaml"
    if not blocks_yaml_path.exists():
        print(f"Error: blocks.yaml not found at {blocks_yaml_path}")
        raise typer.Exit(code=1)

    with blocks_yaml_path.open("r", encoding="utf-8") as f:
        blocks_config = yaml.safe_load(f) or {}

    vendor = blocks_config.get("vendor", "")
    if not vendor:
        print("Error: blocks.yaml is missing required 'vendor' key")
        raise typer.Exit(code=1)

    labb_dir = repo_path / ".labb"
    labb_dir.mkdir(exist_ok=True)
    _ensure_gitignore(repo_path)

    _build_template_tree(repo_path, vendor)
    _create_renderer_base_template(repo_path)
    _build_vendor_package(repo_path, vendor)

    discovered_blocks = _discover_blocks(repo_path)

    # Add .labb/ to sys.path so the synthetic vendor package is importable
    labb_pkg_root = str(labb_dir)
    if labb_pkg_root not in sys.path:
        sys.path.insert(0, labb_pkg_root)

    # Clear any DJANGO_SETTINGS_MODULE so our configure() call always wins.
    os.environ.pop("DJANGO_SETTINGS_MODULE", None)

    # Point labb at the repo's labb.yaml so m.dependencies resolves CSS correctly.
    labb_yaml = repo_path / "labb.yaml"
    if labb_yaml.exists():
        os.environ["LABB_CONFIG_PATH"] = str(labb_yaml)

    try:
        from django.conf import settings as django_settings

        if not django_settings.configured:
            django_settings.configure(
                SECRET_KEY="labb-dev-not-for-production",
                DEBUG=True,
                ALLOWED_HOSTS=["*"],
                INSTALLED_APPS=[
                    "django.contrib.contenttypes",
                    "django.contrib.auth",
                    "django.contrib.staticfiles",
                    "django_cotton",
                    "labb",
                    "labbicons",
                    vendor,
                ],
                MIDDLEWARE=[
                    "labb.middleware.ReactivityMiddleware",
                ],
                DATABASES={
                    "default": {
                        "ENGINE": "django.db.backends.sqlite3",
                        "NAME": str(repo_path / ".labb" / "dev.sqlite3"),
                    }
                },
                TEMPLATES=[
                    {
                        "BACKEND": "django.template.backends.django.DjangoTemplates",
                        "DIRS": [str(repo_path / ".labb" / "templates")],
                        "APP_DIRS": False,
                        "OPTIONS": {
                            "context_processors": [
                                "django.template.context_processors.request",
                            ],
                            "loaders": [
                                (
                                    "django_cotton.cotton_loader.Loader",
                                    [
                                        "django.template.loaders.filesystem.Loader",
                                        "django.template.loaders.app_directories.Loader",
                                    ],
                                ),
                            ],
                        },
                    }
                ],
                STATIC_URL="/static/",
                STATICFILES_DIRS=[str(repo_path / "static")]
                if (repo_path / "static").exists()
                else [],
                ROOT_URLCONF="labb.contrib.blocks.renderer.urls",
            )
    except RuntimeError:
        pass

    import django

    django.setup()

    from labb.contrib.blocks import renderer

    block_registry = {
        f"{vendor}/{category}/{slug}": {
            "type": block_meta["type"],
            "vendor": vendor,
            "category": category,
            "slug": slug,
            "name": block_meta.get("name", slug),
            "description": block_meta.get("description", ""),
            "preview_context": block_meta.get("preview_context", {}),
            "tags": block_meta.get("tags", []),
            "status": _block_status(block_meta),
            "thumbnail": block_meta.get("thumbnail"),
        }
        for (category, slug), block_meta in discovered_blocks.items()
    }
    # The renderer resolves block files as repo_path/{category}/{slug}, so it
    # points at the blocks directory, not the repo root.
    renderer.configure(block_registry, blocks_root(repo_path), vendor)

    from django.core.management import call_command

    call_command("migrate", "--run-syncdb", verbosity=0)

    fixtures_path = blocks_root(repo_path) / "fixtures.json"
    if fixtures_path.exists():
        call_command("loaddata", str(fixtures_path), verbosity=0)

    block_count = len(discovered_blocks)
    print(f"Starting labb block renderer at http://localhost:{port}/")
    print(
        f"Vendor: {vendor} | {block_count} block{'s' if block_count != 1 else ''} discovered"
    )
    print("Press Ctrl+C to stop.")

    call_command("runserver", f"0.0.0.0:{port}", use_reloader=True)
