"""Tests for blocks_dev.py: build_index, validate, new_block, start, serve helpers."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer
import yaml

from labb.cli.handlers.blocks_dev import (
    _build_template_tree,
    _discover_blocks,
    _ensure_gitignore,
    build_index,
    new_block,
    serve,
    validate,
)
from labb.cli.handlers.commons import blocks_root

# ===========================================================================
# build_index
# ===========================================================================


def make_blocks_repo(tmp_path, vendor="lb"):
    (tmp_path / "blocks.yaml").write_text(f"vendor: {vendor}\nname: Test\n")
    block_dir = tmp_path / "crud" / "todos"
    block_dir.mkdir(parents=True)
    (block_dir / "block.yaml").write_text(
        "name: Todo List\nref: crud/todos\ntype: fullstack\ntier: free\ndescription: A todo list\n"
    )
    return tmp_path


def test_build_index_creates_index_yaml(tmp_path):
    repo = make_blocks_repo(tmp_path)
    build_index(path=str(repo))

    index_path = repo / "index.yaml"
    assert index_path.exists()

    data = yaml.safe_load(index_path.read_text())
    assert "blocks" in data
    assert len(data["blocks"]) == 1
    block = data["blocks"][0]
    assert block["name"] == "Todo List"
    assert block["type"] == "fullstack"
    assert block["tier"] == "free"
    assert block["description"] == "A todo list"


def test_build_index_includes_vendor_prefix(tmp_path):
    repo = make_blocks_repo(tmp_path, vendor="lb")
    build_index(path=str(repo))

    data = yaml.safe_load((repo / "index.yaml").read_text())
    assert data["blocks"][0]["ref"] == "lb/crud/todos"


def test_build_index_multiple_blocks(tmp_path):
    (tmp_path / "blocks.yaml").write_text("vendor: lb\n")

    for slug, name in [("todos", "Todo List"), ("contacts", "Contact List")]:
        block_dir = tmp_path / "crud" / slug
        block_dir.mkdir(parents=True)
        (block_dir / "block.yaml").write_text(
            f"name: {name}\ntype: fullstack\ntier: free\ndescription: A {slug} block\n"
        )

    build_index(path=str(tmp_path))

    data = yaml.safe_load((tmp_path / "index.yaml").read_text())
    assert len(data["blocks"]) == 2
    refs = {b["ref"] for b in data["blocks"]}
    assert "lb/crud/todos" in refs
    assert "lb/crud/contacts" in refs


def test_build_index_skips_invalid_block(tmp_path, capsys):
    make_blocks_repo(tmp_path)

    bad_dir = tmp_path / "crud" / "bad"
    bad_dir.mkdir(parents=True)
    (bad_dir / "block.yaml").write_text(
        "type: fullstack\ntier: free\ndescription: Missing name\n"
    )

    build_index(path=str(tmp_path))

    data = yaml.safe_load((tmp_path / "index.yaml").read_text())
    assert len(data["blocks"]) == 1
    assert data["blocks"][0]["ref"] == "lb/crud/todos"

    captured = capsys.readouterr()
    assert "Warning" in captured.out
    assert "name" in captured.out


def test_build_index_missing_blocks_yaml(tmp_path, capsys):
    build_index(path=str(tmp_path))

    captured = capsys.readouterr()
    assert "Error" in captured.out
    assert "blocks.yaml" in captured.out

    assert not (tmp_path / "index.yaml").exists()


def test_build_index_idempotent(tmp_path):
    repo = make_blocks_repo(tmp_path)

    build_index(path=str(repo))
    first_content = (repo / "index.yaml").read_text()

    build_index(path=str(repo))
    second_content = (repo / "index.yaml").read_text()

    assert first_content == second_content


def test_build_index_custom_path(tmp_path):
    repo = tmp_path / "my_blocks_repo"
    repo.mkdir()
    make_blocks_repo(repo, vendor="acme")

    build_index(path=str(repo))

    index_path = repo / "index.yaml"
    assert index_path.exists()
    data = yaml.safe_load(index_path.read_text())
    assert data["blocks"][0]["ref"] == "acme/crud/todos"


def test_build_index_skips_excluded_dirs(tmp_path):
    (tmp_path / "blocks.yaml").write_text("vendor: lb\n")

    valid_dir = tmp_path / "auth" / "login"
    valid_dir.mkdir(parents=True)
    (valid_dir / "block.yaml").write_text(
        "name: Login\ntype: fullstack\ntier: free\ndescription: Login block\n"
    )

    skip_dir = tmp_path / "migrations" / "some_block"
    skip_dir.mkdir(parents=True)
    (skip_dir / "block.yaml").write_text(
        "name: Migration Block\ntype: fullstack\ntier: free\ndescription: Should be skipped\n"
    )

    build_index(path=str(tmp_path))

    data = yaml.safe_load((tmp_path / "index.yaml").read_text())
    assert len(data["blocks"]) == 1
    assert data["blocks"][0]["ref"] == "lb/auth/login"


def test_build_index_includes_new_fields(tmp_path):
    (tmp_path / "blocks.yaml").write_text("vendor: lb\n")
    block_dir = tmp_path / "dashboard" / "analytics"
    block_dir.mkdir(parents=True)
    (block_dir / "block.yaml").write_text(
        "name: Analytics\ntype: fe\ntier: free\ndescription: Charts\n"
        "category: dashboard\nstatus: launch\n"
        "tags:\n  - reactive\n  - charts\n"
        "thumbnail: thumbnails/analytics.png\n"
    )

    build_index(path=str(tmp_path))

    block = yaml.safe_load((tmp_path / "index.yaml").read_text())["blocks"][0]
    assert block["category"] == "dashboard"
    assert block["status"] == "launch"
    assert block["tags"] == ["reactive", "charts"]
    assert block["thumbnail"] == "thumbnails/analytics.png"


def test_build_index_defaults_status_backlog(tmp_path):
    """A manifest without an explicit status is indexed as backlog (hidden by default)."""
    repo = make_blocks_repo(tmp_path)
    build_index(path=str(repo))

    block = yaml.safe_load((repo / "index.yaml").read_text())["blocks"][0]
    assert block["status"] == "backlog"


# ===========================================================================
# validate
# ===========================================================================


def make_fullstack_block(tmp_path, category="crud", slug="todos"):
    block_dir = tmp_path / category / slug
    block_dir.mkdir(parents=True)
    (block_dir / "block.yaml").write_text(
        "name: Todo List\nref: crud/todos\ntype: fullstack\ntier: free\n"
        "labb_version: '>=0.5.0'\ndescription: A todo list\n"
    )
    templates = block_dir / "templates"
    templates.mkdir()
    (templates / "index.html").write_text("<div>todos</div>")
    views_content = "from labb.contrib.blocks import lm\nLbTodo = lm('LbTodo')\n"
    (block_dir / "views.py").write_text(views_content)
    (block_dir / "urls.py").write_text(
        "from django.urls import path\nurlpatterns = []\n"
    )
    return block_dir


def make_fe_block(
    tmp_path, category="landing", slug="hero-split", with_preview_context=True
):
    block_dir = tmp_path / category / slug
    block_dir.mkdir(parents=True)
    yaml_content = (
        "name: Hero Split\nref: landing/hero-split\ntype: fe\ntier: free\n"
        "labb_version: '>=0.5.0'\ndescription: A hero section\n"
    )
    if with_preview_context:
        yaml_content += "preview_context:\n  title: Hello\n"
    (block_dir / "block.yaml").write_text(yaml_content)
    templates = block_dir / "templates"
    templates.mkdir()
    (templates / "index.html").write_text("<div>hero</div>")
    return block_dir


def make_repo_with_blocks_yaml(tmp_path, vendor="lb"):
    (tmp_path / "blocks.yaml").write_text(f"vendor: {vendor}\nname: Test\n")
    return tmp_path


def test_validate_valid_fullstack_block(tmp_path, capsys):
    make_repo_with_blocks_yaml(tmp_path)
    make_fullstack_block(tmp_path)

    result = validate(path=str(tmp_path))

    assert result is True
    captured = capsys.readouterr()
    assert "✓ crud/todos" in captured.out
    assert "1 passed" in captured.out


def test_validate_valid_fe_only_block_with_preview_context(tmp_path, capsys):
    make_repo_with_blocks_yaml(tmp_path)
    make_fe_block(tmp_path, with_preview_context=True)

    result = validate(path=str(tmp_path))

    assert result is True
    captured = capsys.readouterr()
    assert "✓ landing/hero-split" in captured.out
    assert "1 passed" in captured.out


def test_validate_fe_only_missing_preview_context(tmp_path, capsys):
    make_repo_with_blocks_yaml(tmp_path)
    make_fe_block(tmp_path, with_preview_context=False)

    result = validate(path=str(tmp_path))

    assert result is True
    captured = capsys.readouterr()
    assert "⚠" in captured.out
    assert "preview_context" in captured.out
    assert "1 warning" in captured.out


def test_validate_missing_required_field(tmp_path, capsys):
    make_repo_with_blocks_yaml(tmp_path)
    block_dir = tmp_path / "crud" / "todos"
    block_dir.mkdir(parents=True)
    (block_dir / "block.yaml").write_text(
        "name: Todo List\nref: crud/todos\ntype: fullstack\ntier: free\nlabb_version: '>=0.5.0'\n"
    )
    templates = block_dir / "templates"
    templates.mkdir()
    (templates / "index.html").write_text("<div>todos</div>")
    (block_dir / "views.py").write_text("from labb.contrib.blocks import lm\n")
    (block_dir / "urls.py").write_text("urlpatterns = []\n")

    with pytest.raises(typer.Exit) as exc:
        validate(path=str(tmp_path))

    assert exc.value.exit_code == 1
    captured = capsys.readouterr()
    assert "description" in captured.out


def test_validate_invalid_type(tmp_path, capsys):
    make_repo_with_blocks_yaml(tmp_path)
    block_dir = tmp_path / "crud" / "todos"
    block_dir.mkdir(parents=True)
    (block_dir / "block.yaml").write_text(
        "name: Todo List\nref: crud/todos\ntype: widget\ntier: free\n"
        "labb_version: '>=0.5.0'\ndescription: A todo list\n"
    )
    templates = block_dir / "templates"
    templates.mkdir()
    (templates / "index.html").write_text("<div>todos</div>")

    with pytest.raises(typer.Exit) as exc:
        validate(path=str(tmp_path))

    assert exc.value.exit_code == 1
    captured = capsys.readouterr()
    assert "widget" in captured.out


def test_validate_fullstack_missing_views_py(tmp_path, capsys):
    make_repo_with_blocks_yaml(tmp_path)
    block_dir = make_fullstack_block(tmp_path)
    (block_dir / "views.py").unlink()

    with pytest.raises(typer.Exit) as exc:
        validate(path=str(tmp_path))

    assert exc.value.exit_code == 1
    captured = capsys.readouterr()
    assert "views.py" in captured.out


def test_validate_fullstack_missing_urls_py(tmp_path, capsys):
    make_repo_with_blocks_yaml(tmp_path)
    block_dir = make_fullstack_block(tmp_path)
    (block_dir / "urls.py").unlink()

    with pytest.raises(typer.Exit) as exc:
        validate(path=str(tmp_path))

    assert exc.value.exit_code == 1
    captured = capsys.readouterr()
    assert "urls.py" in captured.out


def test_validate_fullstack_with_lt_import(tmp_path, capsys):
    make_repo_with_blocks_yaml(tmp_path)
    block_dir = make_fullstack_block(tmp_path)
    (block_dir / "views.py").write_text(
        "from labb.contrib.blocks import lt\nLbTodo = lt('LbTodo')\n"
    )

    with pytest.raises(typer.Exit) as exc:
        validate(path=str(tmp_path))

    assert exc.value.exit_code == 1
    captured = capsys.readouterr()
    assert "lt" in captured.out


def test_validate_empty_templates_dir(tmp_path, capsys):
    make_repo_with_blocks_yaml(tmp_path)
    block_dir = make_fullstack_block(tmp_path)
    templates_dir = block_dir / "templates"
    for f in templates_dir.iterdir():
        f.unlink()

    with pytest.raises(typer.Exit) as exc:
        validate(path=str(tmp_path))

    assert exc.value.exit_code == 1
    captured = capsys.readouterr()
    assert "templates/" in captured.out


def test_validate_missing_blocks_yaml(tmp_path, capsys):
    make_fullstack_block(tmp_path)

    with pytest.raises(typer.Exit) as exc:
        validate(path=str(tmp_path))

    assert exc.value.exit_code == 1
    captured = capsys.readouterr()
    assert "blocks.yaml" in captured.out


def test_validate_returns_false_on_errors(tmp_path):
    make_repo_with_blocks_yaml(tmp_path)
    block_dir = tmp_path / "crud" / "todos"
    block_dir.mkdir(parents=True)
    (block_dir / "block.yaml").write_text(
        "name: Todo\nref: crud/todos\ntype: fullstack\ntier: free\n"
    )
    templates = block_dir / "templates"
    templates.mkdir()
    (templates / "index.html").write_text("<div>x</div>")
    (block_dir / "views.py").write_text("from labb.contrib.blocks import lm\n")
    (block_dir / "urls.py").write_text("urlpatterns = []\n")

    with pytest.raises(typer.Exit) as exc:
        validate(path=str(tmp_path))

    assert exc.value.exit_code == 1


def test_validate_returns_true_on_warnings_only(tmp_path):
    make_repo_with_blocks_yaml(tmp_path)
    make_fe_block(tmp_path, with_preview_context=False)

    result = validate(path=str(tmp_path))

    assert result is True


def _write_block_yaml(tmp_path, extra: str, category="dashboard", slug="todos"):
    block_dir = tmp_path / category / slug
    block_dir.mkdir(parents=True)
    (block_dir / "block.yaml").write_text(
        "name: Todo List\nref: crud/todos\ntype: fullstack\ntier: free\n"
        "labb_version: '>=0.5.0'\ndescription: A todo list\n" + extra
    )
    templates = block_dir / "templates"
    templates.mkdir()
    (templates / "index.html").write_text("<div>todos</div>")
    (block_dir / "views.py").write_text("from labb.contrib.blocks import lm\n")
    (block_dir / "urls.py").write_text(
        "from django.urls import path\nurlpatterns = []\n"
    )
    return block_dir


def test_validate_valid_category_and_status(tmp_path, capsys):
    make_repo_with_blocks_yaml(tmp_path)
    _write_block_yaml(
        tmp_path,
        "category: dashboard\nstatus: launch\ntags:\n  - reactive\n  - datatable\n",
    )

    result = validate(path=str(tmp_path))

    assert result is True
    captured = capsys.readouterr()
    assert "1 passed" in captured.out


def test_validate_missing_category_and_status_ok(tmp_path):
    """category/status are optional; a manifest without them still validates."""
    make_repo_with_blocks_yaml(tmp_path)
    make_fullstack_block(tmp_path)

    result = validate(path=str(tmp_path))

    assert result is True


def test_validate_invalid_category(tmp_path, capsys):
    make_repo_with_blocks_yaml(tmp_path)
    _write_block_yaml(tmp_path, "category: widgets\n")

    with pytest.raises(typer.Exit) as exc:
        validate(path=str(tmp_path))

    assert exc.value.exit_code == 1
    captured = capsys.readouterr()
    assert "category" in captured.out
    assert "widgets" in captured.out


def test_validate_invalid_status(tmp_path, capsys):
    make_repo_with_blocks_yaml(tmp_path)
    _write_block_yaml(tmp_path, "status: archived\n")

    with pytest.raises(typer.Exit) as exc:
        validate(path=str(tmp_path))

    assert exc.value.exit_code == 1
    captured = capsys.readouterr()
    assert "status" in captured.out
    assert "archived" in captured.out


def test_validate_tags_not_a_list(tmp_path, capsys):
    make_repo_with_blocks_yaml(tmp_path)
    _write_block_yaml(tmp_path, "tags: reactive\n")

    with pytest.raises(typer.Exit) as exc:
        validate(path=str(tmp_path))

    assert exc.value.exit_code == 1
    captured = capsys.readouterr()
    assert "tags" in captured.out


# ===========================================================================
# new_block
# ===========================================================================


def _make_blocks_yaml(tmp_path: Path, vendor: str = "myco") -> None:
    (tmp_path / "blocks.yaml").write_text(
        f'vendor: {vendor}\nname: {vendor}-blocks\ndescription: ""\n'
    )


class TestNewBlockFullstack:
    def test_new_block_fullstack_creates_all_files(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_blocks_yaml(tmp_path)

        new_block(ref="crud/todos", block_type="fullstack")

        assert (tmp_path / "crud" / "todos" / "block.yaml").exists()
        assert (tmp_path / "crud" / "todos" / "views.py").exists()
        assert (tmp_path / "crud" / "todos" / "urls.py").exists()
        assert (
            tmp_path / "crud" / "todos" / "templates" / "pages" / "index.html"
        ).exists()

    def test_new_block_fe_skips_views_and_urls(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_blocks_yaml(tmp_path)

        new_block(ref="crud/todos", block_type="fe")

        assert (tmp_path / "crud" / "todos" / "block.yaml").exists()
        assert (
            tmp_path / "crud" / "todos" / "templates" / "pages" / "index.html"
        ).exists()
        assert not (tmp_path / "crud" / "todos" / "views.py").exists()
        assert not (tmp_path / "crud" / "todos" / "urls.py").exists()

    def test_new_block_invalid_ref_errors(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_blocks_yaml(tmp_path)

        with pytest.raises(typer.Exit) as exc_info:
            new_block(ref="crud", block_type="fullstack")

        assert exc_info.value.exit_code == 1

    def test_new_block_no_blocks_yaml_errors(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        with pytest.raises(typer.Exit) as exc_info:
            new_block(ref="crud/todos", block_type="fullstack")

        assert exc_info.value.exit_code == 1

    def test_new_block_already_exists_errors(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_blocks_yaml(tmp_path)

        (tmp_path / "crud" / "todos").mkdir(parents=True)

        with pytest.raises(typer.Exit) as exc_info:
            new_block(ref="crud/todos", block_type="fullstack")

        assert exc_info.value.exit_code == 1

    def test_new_block_block_yaml_content(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_blocks_yaml(tmp_path, vendor="acme")

        new_block(ref="crud/todos", block_type="fullstack")

        content = (tmp_path / "crud" / "todos" / "block.yaml").read_text()
        assert "ref: acme/crud/todos" in content
        assert "type: fullstack" in content
        assert "tier: free" in content

    def test_new_block_views_py_uses_lm_import(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_blocks_yaml(tmp_path)

        new_block(ref="crud/todos", block_type="fullstack")

        content = (tmp_path / "crud" / "todos" / "views.py").read_text()
        assert "from labb.contrib.blocks import lm" in content

    def test_new_block_urls_py_has_app_name(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_blocks_yaml(tmp_path)

        new_block(ref="crud/todos", block_type="fullstack")

        content = (tmp_path / "crud" / "todos" / "urls.py").read_text()
        assert 'app_name = "block_crud_todos"' in content


# ===========================================================================
# _ensure_gitignore
# ===========================================================================


def test_gitignore_created_with_labb_entry(tmp_path):
    _ensure_gitignore(tmp_path)

    gitignore = tmp_path / ".gitignore"
    assert gitignore.exists()
    assert ".labb/" in gitignore.read_text()


def test_gitignore_not_duplicated(tmp_path):
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text(".labb/\n")

    _ensure_gitignore(tmp_path)

    content = gitignore.read_text()
    assert content.count(".labb/") == 1


def test_gitignore_appends_to_existing_file(tmp_path):
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("*.pyc\n__pycache__/\n")

    _ensure_gitignore(tmp_path)

    content = gitignore.read_text()
    assert "*.pyc" in content
    assert "__pycache__/" in content
    assert ".labb/" in content


# ===========================================================================
# _build_template_tree
# ===========================================================================


def make_repo(tmp_path, vendor="lb"):
    (tmp_path / "blocks.yaml").write_text(f"vendor: {vendor}\nname: Test Repo\n")
    return tmp_path


def make_fullstack_block_serve(repo, category="crud", slug="todos"):
    block_dir = repo / category / slug
    block_dir.mkdir(parents=True)
    (block_dir / "block.yaml").write_text(
        f"name: {slug.title()}\nref: {category}/{slug}\n"
        "type: fullstack\ntier: free\nlabb_version: '>=0.5.0'\ndescription: A block\n"
    )
    templates = block_dir / "templates"
    templates.mkdir()
    (templates / "index.html").write_text(f"<div>{slug}</div>")
    (block_dir / "views.py").write_text("from labb.contrib.blocks import lm\n")
    (block_dir / "urls.py").write_text("urlpatterns = []\n")
    return block_dir


def make_fe_block_serve(repo, category="landing", slug="hero"):
    block_dir = repo / category / slug
    block_dir.mkdir(parents=True)
    (block_dir / "block.yaml").write_text(
        f"name: {slug.title()}\nref: {category}/{slug}\n"
        "type: fe\ntier: free\nlabb_version: '>=0.5.0'\ndescription: A hero\n"
        "preview_context:\n  title: Hello\n"
    )
    templates = block_dir / "templates"
    templates.mkdir()
    (templates / "index.html").write_text(f"<div>{slug}</div>")
    return block_dir


def test_build_template_tree(tmp_path):
    repo = make_repo(tmp_path)
    make_fullstack_block_serve(repo, "crud", "todos")

    _build_template_tree(repo, "lb")

    dest = repo / ".labb" / "templates" / "lb" / "crud" / "todos" / "index.html"
    assert dest.exists()
    content = dest.read_text()
    assert "todos" in content


def test_build_template_tree_clears_existing(tmp_path):
    repo = make_repo(tmp_path)
    make_fullstack_block_serve(repo, "crud", "todos")

    _build_template_tree(repo, "lb")

    stale_dir = repo / ".labb" / "templates" / "lb" / "old_cat" / "stale_block"
    stale_dir.mkdir(parents=True)
    stale_file = stale_dir / "stale.html"
    stale_file.write_text("<div>stale</div>")
    assert stale_file.exists()

    _build_template_tree(repo, "lb")

    assert not stale_file.exists()
    dest = repo / ".labb" / "templates" / "lb" / "crud" / "todos" / "index.html"
    assert dest.exists()


def test_build_template_tree_multiple_blocks(tmp_path):
    repo = make_repo(tmp_path)
    make_fullstack_block_serve(repo, "crud", "todos")
    make_fe_block_serve(repo, "landing", "hero")

    _build_template_tree(repo, "lb")

    assert (
        repo / ".labb" / "templates" / "lb" / "crud" / "todos" / "index.html"
    ).exists()
    assert (
        repo / ".labb" / "templates" / "lb" / "landing" / "hero" / "index.html"
    ).exists()


def test_build_template_tree_skips_no_templates_dir(tmp_path):
    repo = make_repo(tmp_path)

    block_dir = repo / "auth" / "login"
    block_dir.mkdir(parents=True)
    (block_dir / "block.yaml").write_text("name: Login\ntype: fe\n")

    _build_template_tree(repo, "lb")

    dest_dir = repo / ".labb" / "templates" / "lb" / "auth" / "login"
    assert not dest_dir.exists()


def test_build_template_tree_merges_cotton_subdir(tmp_path):
    repo = make_repo(tmp_path)
    block_dir = repo / "ui" / "hero"
    templates = block_dir / "templates"
    cotton = templates / "cotton" / "lb" / "ui" / "hero"
    cotton.mkdir(parents=True)
    (templates / "index.html").write_text("<div>hero</div>")
    (cotton / "index.html").write_text("<c-vars title='' />")

    _build_template_tree(repo, "lb")

    # Regular template lands at the vendor path
    assert (repo / ".labb" / "templates" / "lb" / "ui" / "hero" / "index.html").exists()
    # Cotton component merges into .labb/templates/cotton/, not nested under vendor
    merged = (
        repo / ".labb" / "templates" / "cotton" / "lb" / "ui" / "hero" / "index.html"
    )
    assert merged.exists()
    assert "c-vars" in merged.read_text()
    # Cotton dir must NOT appear nested under the vendor template path
    assert not (repo / ".labb" / "templates" / "lb" / "ui" / "hero" / "cotton").exists()


# ===========================================================================
# _discover_blocks
# ===========================================================================


def test_discover_blocks_fullstack(tmp_path):
    repo = make_repo(tmp_path)
    make_fullstack_block_serve(repo, "crud", "todos")

    result = _discover_blocks(repo)

    assert ("crud", "todos") in result
    assert result[("crud", "todos")]["type"] == "fullstack"


def test_discover_blocks_fe_only(tmp_path):
    repo = make_repo(tmp_path)
    make_fe_block_serve(repo, "landing", "hero")

    result = _discover_blocks(repo)

    assert ("landing", "hero") in result
    assert result[("landing", "hero")]["type"] == "fe"


def test_discover_blocks_skips_no_block_yaml(tmp_path):
    repo = make_repo(tmp_path)

    orphan = repo / "ui" / "button"
    orphan.mkdir(parents=True)
    (orphan / "views.py").write_text("# views\n")

    result = _discover_blocks(repo)

    assert ("ui", "button") not in result
    assert len(result) == 0


def test_discover_blocks_multiple(tmp_path):
    repo = make_repo(tmp_path)
    make_fullstack_block_serve(repo, "crud", "todos")
    make_fe_block_serve(repo, "landing", "hero")

    result = _discover_blocks(repo)

    assert len(result) == 2
    assert ("crud", "todos") in result
    assert ("landing", "hero") in result


def test_discover_blocks_skips_excluded_dirs(tmp_path):
    repo = make_repo(tmp_path)

    make_fullstack_block_serve(repo, "crud", "todos")

    skip_dir = repo / "migrations" / "some_block"
    skip_dir.mkdir(parents=True)
    (skip_dir / "block.yaml").write_text("name: Skip Me\ntype: fullstack\n")

    result = _discover_blocks(repo)

    assert ("crud", "todos") in result
    assert ("migrations", "some_block") not in result
    assert len(result) == 1


def test_discover_blocks_captures_preview_context(tmp_path):
    repo = make_repo(tmp_path)
    make_fe_block_serve(repo, "landing", "hero")

    result = _discover_blocks(repo)

    assert result[("landing", "hero")]["preview_context"] == {"title": "Hello"}


def test_discover_blocks_captures_status_and_tags(tmp_path):
    repo = make_repo(tmp_path)
    block_dir = repo / "dashboard" / "analytics"
    block_dir.mkdir(parents=True)
    (block_dir / "block.yaml").write_text(
        "name: Analytics\nref: dashboard/analytics\ntype: fe\n"
        "labb_version: '>=0.5.0'\ndescription: Charts\n"
        "category: dashboard\nstatus: launch\ntags:\n  - reactive\n  - charts\n"
    )
    (block_dir / "templates").mkdir()
    (block_dir / "templates" / "index.html").write_text("<div>a</div>")

    result = _discover_blocks(repo)

    meta = result[("dashboard", "analytics")]
    assert meta["status"] == "launch"
    assert meta["tags"] == ["reactive", "charts"]


# ===========================================================================
# serve() error handling
# ===========================================================================


def test_serve_missing_blocks_yaml_errors(tmp_path):
    with pytest.raises(typer.Exit) as exc:
        serve(path=str(tmp_path))

    assert exc.value.exit_code == 1


def test_serve_missing_vendor_errors(tmp_path, capsys):
    (tmp_path / "blocks.yaml").write_text("name: Vendorless Repo\n")

    with pytest.raises(typer.Exit) as exc:
        serve(path=str(tmp_path))

    assert exc.value.exit_code == 1
    captured = capsys.readouterr()
    assert "vendor" in captured.out


# ===========================================================================
# start
# ===========================================================================


def _run_start(tmp_path, vendor="myco", name=None, package_manager="poetry"):
    if name is None:
        name = f"{vendor}-blocks"

    target_dir = tmp_path / name

    with (
        patch("labb.cli.handlers.blocks_dev.questionary.text") as mock_text,
        patch(
            "labb.cli.handlers.blocks_dev.prompt_package_manager",
            return_value=package_manager,
        ),
        patch(
            "labb.cli.handlers.blocks_dev.setup_poetry_project",
            return_value=True,
        ),
        patch(
            "labb.cli.handlers.blocks_dev.setup_pip_project",
            return_value=True,
        ),
        patch(
            "labb.cli.handlers.blocks_dev.setup_uv_project",
            return_value=True,
        ),
        patch(
            "labb.cli.handlers.blocks_dev.install_labb",
            return_value=True,
        ),
        patch("labb.cli.handlers.blocks_dev.Path.cwd", return_value=tmp_path),
    ):
        mock_text.return_value = MagicMock(ask=MagicMock(side_effect=[vendor, name]))

        from labb.cli.handlers.blocks_dev import start

        start(name=name, vendor=vendor, package_manager=package_manager)

    return target_dir


class TestStartCreatesFiles:
    def test_start_creates_blocks_yaml(self, tmp_path):
        target_dir = _run_start(tmp_path, vendor="myco", name="myco-blocks")
        blocks_yaml = target_dir / "blocks.yaml"
        assert blocks_yaml.exists(), "blocks.yaml should be created"
        content = blocks_yaml.read_text()
        assert "vendor: myco" in content

    def test_start_creates_models_init(self, tmp_path):
        target_dir = _run_start(tmp_path, vendor="myco", name="myco-blocks")
        models_init = target_dir / "blocks" / "models" / "__init__.py"
        assert models_init.exists(), "blocks/models/__init__.py should be created"

    def test_start_declares_where_blocks_live(self, tmp_path):
        # Categories are nested so the repo root stays readable; every command
        # resolves them through blocks.yaml rather than assuming the root.
        target_dir = _run_start(tmp_path, vendor="myco", name="myco-blocks")
        assert "blocks_dir: blocks" in (target_dir / "blocks.yaml").read_text()

    def test_start_creates_gitignore(self, tmp_path):
        target_dir = _run_start(tmp_path, vendor="myco", name="myco-blocks")
        gitignore = target_dir / ".gitignore"
        assert gitignore.exists(), ".gitignore should be created"
        content = gitignore.read_text()
        assert ".labb/" in content

    def test_start_creates_readme(self, tmp_path):
        target_dir = _run_start(tmp_path, vendor="myco", name="myco-blocks")
        readme = target_dir / "README.md"
        assert readme.exists(), "README.md should be created"
        content = readme.read_text()
        assert "block dev serve" in content

    def test_start_directory_already_exists_errors(self, tmp_path):
        name = "myco-blocks"
        (tmp_path / name).mkdir()

        with (
            patch("labb.cli.handlers.blocks_dev.Path.cwd", return_value=tmp_path),
        ):
            from labb.cli.handlers.blocks_dev import start

            with pytest.raises(typer.Exit) as exc_info:
                start(name=name, vendor="myco", package_manager="poetry")

        assert exc_info.value.exit_code == 1


# ===========================================================================
# tour.yaml — the teaching layer (ticket 0012)
# ===========================================================================


TOUR_TEMPLATE = """\
<c-lbr.signals email="" password="" />

<c-lb.form c-lbr.post="{% url 'sign_in' %}">
  <c-lb.input name="email" data-bind="email" />
  <c-lb.button variant="$valid:primary">Sign in</c-lb.button>
</c-lb.form>
"""


def make_tour_block(
    tmp_path, tour, template=TOUR_TEMPLATE, category="auth", slug="split-brand"
):
    """A fullstack block carrying a tour.yaml, for exercising tour validation."""
    block_dir = tmp_path / category / slug
    block_dir.mkdir(parents=True)
    (block_dir / "block.yaml").write_text(
        f"name: Split Brand\nref: {category}/{slug}\ntype: fullstack\n"
        f"labb_version: '>=0.5.0'\ndescription: A sign-in block\n"
    )
    templates = block_dir / "templates"
    templates.mkdir()
    (templates / "index.html").write_text(template)
    (block_dir / "views.py").write_text(
        "from labb.contrib.blocks import lm\n\n\ndef sign_in(request):\n    return None\n"
    )
    (block_dir / "urls.py").write_text(
        "from django.urls import path\nurlpatterns = []\n"
    )
    (block_dir / "tour.yaml").write_text(tour)
    return block_dir


def test_validate_block_without_tour_still_passes(tmp_path):
    """tour.yaml is optional at the engine level."""
    make_repo_with_blocks_yaml(tmp_path)
    make_fullstack_block(tmp_path)

    assert validate(path=str(tmp_path)) is True


def test_validate_valid_tour(tmp_path, capsys):
    make_repo_with_blocks_yaml(tmp_path)
    make_tour_block(
        tmp_path,
        tour=(
            "steps:\n"
            "  - title: Declare the signals\n"
            '    match: "<c-lbr.signals"\n'
            "    teaches: [signals]\n"
            "    docs: [reactivity/signals]\n"
            "    body: Signals are client state.\n"
        ),
    )

    result = validate(path=str(tmp_path))

    assert result is True
    assert "1 passed" in capsys.readouterr().out


def test_validate_tour_match_resolves_to_nothing(tmp_path, capsys):
    """A match pointing at code that isn't there must fail — this is what stops tours rotting."""
    make_repo_with_blocks_yaml(tmp_path)
    make_tour_block(
        tmp_path,
        tour=(
            "steps:\n"
            "  - title: Gone\n"
            '    match: "<c-lbr.nonexistent"\n'
            "    teaches: [signals]\n"
            "    body: Nope.\n"
        ),
    )

    with pytest.raises(typer.Exit) as exc:
        validate(path=str(tmp_path))

    assert exc.value.exit_code == 1
    out = capsys.readouterr().out
    assert "match" in out
    assert "c-lbr.nonexistent" in out


def test_validate_tour_match_is_ambiguous(tmp_path, capsys):
    """A match resolving to more than one location must fail — the highlight would be arbitrary."""
    make_repo_with_blocks_yaml(tmp_path)
    make_tour_block(
        tmp_path,
        template='<c-lb.input name="a" />\n<c-lb.input name="b" />\n',
        tour=(
            "steps:\n"
            "  - title: The input\n"
            '    match: "<c-lb.input"\n'
            "    teaches: [binding]\n"
            "    body: An input.\n"
        ),
    )

    with pytest.raises(typer.Exit) as exc:
        validate(path=str(tmp_path))

    assert exc.value.exit_code == 1
    out = capsys.readouterr().out
    assert "ambiguous" in out.lower()


def test_validate_tour_teaches_capability_absent_from_code(tmp_path, capsys):
    """A tour claiming SSE when the block has no SSEResponse must fail.

    This is what makes the coverage matrix a check rather than an assertion.
    """
    make_repo_with_blocks_yaml(tmp_path)
    make_tour_block(
        tmp_path,
        tour=(
            "steps:\n"
            "  - title: Declare the signals\n"
            '    match: "<c-lbr.signals"\n'
            "    teaches: [signals, sse]\n"
            "    body: Signals are client state.\n"
        ),
    )

    with pytest.raises(typer.Exit) as exc:
        validate(path=str(tmp_path))

    assert exc.value.exit_code == 1
    out = capsys.readouterr().out
    assert "sse" in out
    assert "teaches" in out


def test_validate_tour_teaches_unknown_capability(tmp_path, capsys):
    """Closed vocabulary — a typo'd capability must not pass silently."""
    make_repo_with_blocks_yaml(tmp_path)
    make_tour_block(
        tmp_path,
        tour=(
            "steps:\n"
            "  - title: Declare the signals\n"
            '    match: "<c-lbr.signals"\n'
            "    teaches: [signalz]\n"
            "    body: Signals are client state.\n"
        ),
    )

    with pytest.raises(typer.Exit) as exc:
        validate(path=str(tmp_path))

    assert exc.value.exit_code == 1
    assert "signalz" in capsys.readouterr().out


def test_validate_tour_step_missing_teaches(tmp_path, capsys):
    """teaches: is required, not optional."""
    make_repo_with_blocks_yaml(tmp_path)
    make_tour_block(
        tmp_path,
        tour=(
            "steps:\n"
            "  - title: Declare the signals\n"
            '    match: "<c-lbr.signals"\n'
            "    body: Signals are client state.\n"
        ),
    )

    with pytest.raises(typer.Exit) as exc:
        validate(path=str(tmp_path))

    assert exc.value.exit_code == 1
    assert "teaches" in capsys.readouterr().out


def test_validate_tour_through_spans_a_range(tmp_path):
    """match: + through: resolves to a line range."""
    make_repo_with_blocks_yaml(tmp_path)
    make_tour_block(
        tmp_path,
        tour=(
            "steps:\n"
            "  - title: The form\n"
            '    match: "<c-lb.form"\n'
            '    through: "</c-lb.form>"\n'
            "    teaches: [server-actions]\n"
            "    body: Posts to a real view.\n"
        ),
    )

    assert validate(path=str(tmp_path)) is True


def test_validate_tour_through_before_match(tmp_path, capsys):
    """A through: that resolves above its match: is incoherent."""
    make_repo_with_blocks_yaml(tmp_path)
    make_tour_block(
        tmp_path,
        tour=(
            "steps:\n"
            "  - title: Backwards\n"
            '    match: "</c-lb.form>"\n'
            '    through: "<c-lbr.signals"\n'
            "    teaches: [signals]\n"
            "    body: Backwards.\n"
        ),
    )

    with pytest.raises(typer.Exit) as exc:
        validate(path=str(tmp_path))

    assert exc.value.exit_code == 1


def test_validate_tour_match_in_views_py(tmp_path):
    """A step can point at a file other than the template via file:."""
    make_repo_with_blocks_yaml(tmp_path)
    make_tour_block(
        tmp_path,
        tour=(
            "steps:\n"
            "  - title: The view\n"
            "    file: views.py\n"
            '    match: "def sign_in"\n'
            "    teaches: [server-actions]\n"
            "    body: An ordinary Django view.\n"
        ),
    )

    assert validate(path=str(tmp_path)) is True


def test_validate_tour_match_in_missing_file(tmp_path, capsys):
    make_repo_with_blocks_yaml(tmp_path)
    make_tour_block(
        tmp_path,
        tour=(
            "steps:\n"
            "  - title: Nowhere\n"
            "    file: nope.py\n"
            '    match: "def sign_in"\n'
            "    teaches: [server-actions]\n"
            "    body: Missing.\n"
        ),
    )

    with pytest.raises(typer.Exit) as exc:
        validate(path=str(tmp_path))

    assert exc.value.exit_code == 1
    assert "nope.py" in capsys.readouterr().out


# ===========================================================================
# theme parity — no fixed colours (ticket 0013)
# ===========================================================================


def make_block_with_template(tmp_path, markup, category="hero", slug="split-visual"):
    block_dir = tmp_path / category / slug
    block_dir.mkdir(parents=True)
    (block_dir / "block.yaml").write_text(
        f"name: Hero\nref: {category}/{slug}\ntype: fe\n"
        f"labb_version: '>=0.5.0'\ndescription: A hero\n"
        "preview_context:\n  title: Hello\n"
    )
    templates = block_dir / "templates"
    templates.mkdir()
    (templates / "index.html").write_text(markup)
    return block_dir


def test_validate_theme_tokens_pass(tmp_path):
    """daisyUI semantic tokens are the correct way to colour a block."""
    make_repo_with_blocks_yaml(tmp_path)
    make_block_with_template(
        tmp_path,
        '<div class="bg-base-100 text-primary border-base-300">Know your revenue.</div>\n',
    )

    assert validate(path=str(tmp_path)) is True


def test_validate_theme_token_gradient_passes(tmp_path):
    """Gradients built from theme tokens must remain legal — hero/gradient-mesh depends on it."""
    make_repo_with_blocks_yaml(tmp_path)
    make_block_with_template(
        tmp_path,
        '<div class="bg-gradient-to-br from-primary via-secondary to-base-100">Arden</div>\n',
    )

    assert validate(path=str(tmp_path)) is True


def test_validate_hex_literal_fails(tmp_path, capsys):
    make_repo_with_blocks_yaml(tmp_path)
    make_block_with_template(
        tmp_path,
        '<div style="background: #0f172a">Arden</div>\n',
    )

    with pytest.raises(typer.Exit) as exc:
        validate(path=str(tmp_path))

    assert exc.value.exit_code == 1
    out = capsys.readouterr().out
    assert "#0f172a" in out


def test_validate_rgb_literal_fails(tmp_path, capsys):
    make_repo_with_blocks_yaml(tmp_path)
    make_block_with_template(
        tmp_path,
        '<div style="color: rgb(15, 23, 42)">Arden</div>\n',
    )

    with pytest.raises(typer.Exit) as exc:
        validate(path=str(tmp_path))

    assert exc.value.exit_code == 1
    assert "rgb(" in capsys.readouterr().out


def test_validate_fixed_palette_utility_fails(tmp_path, capsys):
    """Tailwind's fixed palette bypasses the theme just as surely as a hex literal."""
    make_repo_with_blocks_yaml(tmp_path)
    make_block_with_template(
        tmp_path,
        '<div class="bg-slate-900 text-zinc-500">Arden</div>\n',
    )

    with pytest.raises(typer.Exit) as exc:
        validate(path=str(tmp_path))

    assert exc.value.exit_code == 1
    out = capsys.readouterr().out
    assert "bg-slate-900" in out


def test_validate_hex_error_names_the_remedy(tmp_path, capsys):
    """An author must be able to fix it without going to read the policy."""
    make_repo_with_blocks_yaml(tmp_path)
    make_block_with_template(tmp_path, '<div style="background: #fff">Arden</div>\n')

    with pytest.raises(typer.Exit):
        validate(path=str(tmp_path))

    out = capsys.readouterr().out
    assert "theme token" in out.lower()


def test_validate_html_entity_is_not_a_hex_colour(tmp_path):
    """&#123; must not be mistaken for a colour literal."""
    make_repo_with_blocks_yaml(tmp_path)
    make_block_with_template(tmp_path, "<div>Arden &#123; escaped &#125;</div>\n")

    assert validate(path=str(tmp_path)) is True


class TestBlocksRootResolution:
    """Where a source repo keeps its categories is configuration, not convention."""

    def test_defaults_to_repo_root_when_key_absent(self, tmp_path):
        # Repos written before blocks_dir existed keep categories at the root.
        (tmp_path / "blocks.yaml").write_text("vendor: lb\nname: x\n")
        assert blocks_root(tmp_path) == tmp_path

    def test_reads_blocks_dir(self, tmp_path):
        (tmp_path / "blocks.yaml").write_text(
            "vendor: lb\nname: x\nblocks_dir: blocks\n"
        )
        assert blocks_root(tmp_path) == tmp_path / "blocks"

    def test_falls_back_when_no_blocks_yaml(self, tmp_path):
        assert blocks_root(tmp_path) == tmp_path


class TestCommons:
    """commons/ holds components shared by several blocks in a source repo."""

    def _repo(self, tmp_path):
        (tmp_path / "blocks.yaml").write_text(
            "vendor: lb\nname: Test\nblocks_dir: blocks\n"
        )
        src = tmp_path / "blocks"
        block = src / "auth" / "login" / "templates" / "cotton" / "login"
        block.mkdir(parents=True)
        (block / "form.html").write_text("<div><c-brand.mark /></div>")
        shared = src / "commons" / "templates" / "cotton" / "brand"
        shared.mkdir(parents=True)
        (shared / "mark.html").write_text("<span>mark</span>")
        return tmp_path

    def test_commons_components_reach_the_template_tree(self, tmp_path):
        repo = self._repo(tmp_path)
        _build_template_tree(repo, vendor="lb")
        merged = repo / ".labb" / "templates" / "cotton" / "brand" / "mark.html"
        assert merged.exists(), "commons component was not merged"

    def test_block_components_still_merge(self, tmp_path):
        repo = self._repo(tmp_path)
        _build_template_tree(repo, vendor="lb")
        assert (
            repo / ".labb" / "templates" / "cotton" / "login" / "form.html"
        ).exists()

    def test_commons_is_not_a_category(self, tmp_path):
        # It has no block.yaml, and must never be walked as a category.
        repo = self._repo(tmp_path)
        assert "commons" not in {c for c, _ in _discover_blocks(repo)}

    def test_repo_without_commons_still_builds(self, tmp_path):
        (tmp_path / "blocks.yaml").write_text(
            "vendor: lb\nname: Test\nblocks_dir: blocks\n"
        )
        block = tmp_path / "blocks" / "auth" / "login" / "templates" / "pages"
        block.mkdir(parents=True)
        (block / "index.html").write_text("<div>hi</div>")
        _build_template_tree(tmp_path, vendor="lb")
        assert (tmp_path / ".labb" / "templates").exists()


def test_block_start_scaffolds_css_setup(tmp_path):
    """block dev start writes a working CSS setup: labb.yaml + input.css + package.json."""
    import json as _json

    import yaml as _yaml

    from labb.cli.handlers import blocks_dev as bd

    bd._create_block_labb_yaml(tmp_path)
    bd._create_block_input_css(tmp_path)
    bd._create_block_package_json(tmp_path, "myblocks")

    cfg = _yaml.safe_load((tmp_path / "labb.yaml").read_text())
    assert cfg["css"]["packages"] == {"labb": ["themes", "blocks"]}
    assert "apps" not in cfg["css"]["scan"]  # new schema, no legacy scan.apps

    input_css = (tmp_path / "static_src" / "input.css").read_text()
    assert '@import "../.labb/labb.css";' in input_css

    pkg = _json.loads((tmp_path / "package.json").read_text())
    assert {"tailwindcss", "daisyui", "@tailwindcss/cli"} <= set(pkg["devDependencies"])
