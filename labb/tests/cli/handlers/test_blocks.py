"""Tests for blocks.py: block_init, block_add, block_remove, block_sync, block_list, block_search, source_add, source_list."""

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
import typer

from labb.cli.handlers.blocks import (
    _clone_source,
    _parse_ref,
    _resolve_source_for_ref,
    block_add,
    block_init,
    block_list,
    block_remove,
    block_search,
    block_sync,
    source_add,
    source_list,
)
from labb.config import (
    BlockCollection,
    BlocksConfig,
    BlockSource,
    LabbConfig,
    clear_config_cache,
)

# ===========================================================================
# block_init
# ===========================================================================


def write_minimal_labb_yaml(path: Path) -> Path:
    config_path = path / "labb.yaml"
    config_path.write_text(
        "css:\n  build:\n    input: static_src/input.css\n    output: static/css/output.css\n"
    )
    return config_path


def test_block_init_creates_folder_structure(tmp_path):
    config_path = write_minimal_labb_yaml(tmp_path)
    clear_config_cache()

    saved = []

    def fake_save(cfg, path=None):
        saved.append((cfg, path))

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.save_config", side_effect=fake_save),
    ):
        clear_config_cache()
        block_init(name="blocks", path=str(tmp_path / "blocks"), silent=True)

    col_dir = tmp_path / "blocks"
    assert (col_dir / "__init__.py").exists()
    assert (col_dir / "apps.py").exists()
    assert (col_dir / "models").is_dir()
    assert (col_dir / "models" / "__init__.py").exists()
    assert (col_dir / "templates").is_dir()
    assert (col_dir / "fixtures").is_dir()
    assert (col_dir / "migrations").is_dir()
    assert (col_dir / "migrations" / "__init__.py").exists()


def test_block_init_no_vendor_dir_created(tmp_path):
    """block_init must not create any vendor-specific directory."""
    config_path = write_minimal_labb_yaml(tmp_path)
    clear_config_cache()

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.save_config"),
    ):
        clear_config_cache()
        block_init(name="blocks", path=str(tmp_path / "blocks"), silent=True)

    col_dir = tmp_path / "blocks"
    # No hardcoded vendor dir (e.g. "lb") should be created
    assert not (col_dir / "lb").exists()


def test_block_init_apps_py_content(tmp_path):
    config_path = write_minimal_labb_yaml(tmp_path)
    clear_config_cache()

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.save_config"),
    ):
        clear_config_cache()
        block_init(name="blocks", path=str(tmp_path / "blocks"), silent=True)

    apps_content = (tmp_path / "blocks" / "apps.py").read_text()
    assert "class BlocksConfig(AppConfig):" in apps_content
    assert 'name = "blocks"' in apps_content
    assert 'label = "blocks"' in apps_content
    assert "from django.apps import AppConfig" in apps_content


def test_block_init_named_collection(tmp_path):
    config_path = write_minimal_labb_yaml(tmp_path)
    clear_config_cache()

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.save_config"),
    ):
        clear_config_cache()
        block_init(name="premium", path=str(tmp_path / "premium"), silent=True)

    apps_content = (tmp_path / "premium" / "apps.py").read_text()
    assert "class PremiumConfig(AppConfig):" in apps_content
    assert 'name = "premium"' in apps_content
    assert 'label = "premium"' in apps_content


def test_block_init_writes_blocks_section_to_config(tmp_path):
    config_path = write_minimal_labb_yaml(tmp_path)
    clear_config_cache()

    saved = []

    def fake_save(cfg, path=None):
        saved.append((cfg, path))

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.save_config", side_effect=fake_save),
    ):
        clear_config_cache()
        block_init(name="blocks", path=str(tmp_path / "blocks"), silent=True)

    assert len(saved) == 1
    cfg, _ = saved[0]
    assert cfg.blocks is not None
    assert len(cfg.blocks.collections) == 1
    assert cfg.blocks.collections[0].name == "blocks"
    assert len(cfg.blocks.sources) == 1
    assert cfg.blocks.sources[0].name == "labbhq"


def test_block_init_default_collection_is_true(tmp_path):
    config_path = write_minimal_labb_yaml(tmp_path)
    clear_config_cache()

    saved = []

    def fake_save(cfg, path=None):
        saved.append((cfg, path))

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.save_config", side_effect=fake_save),
    ):
        clear_config_cache()
        block_init(name="blocks", path=str(tmp_path / "blocks"), silent=True)

    cfg, _ = saved[0]
    assert cfg.blocks.collections[0].default is True


def test_block_init_second_collection_not_default(tmp_path):
    config_path = write_minimal_labb_yaml(tmp_path)
    clear_config_cache()

    existing_config = LabbConfig(
        blocks=BlocksConfig(
            collections=[
                BlockCollection(
                    name="blocks", path=str(tmp_path / "blocks"), default=True
                )
            ],
            sources=[
                BlockSource(name="labbhq", url="https://github.com/labbhq/blocks")
            ],
        )
    )

    saved = []

    def fake_save(cfg, path=None):
        saved.append((cfg, path))

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=existing_config),
        patch("labb.cli.handlers.blocks.save_config", side_effect=fake_save),
    ):
        block_init(name="premium", path=str(tmp_path / "premium"), silent=True)

    assert len(saved) == 1
    cfg, _ = saved[0]
    assert len(cfg.blocks.collections) == 2
    first = next(c for c in cfg.blocks.collections if c.name == "blocks")
    second = next(c for c in cfg.blocks.collections if c.name == "premium")
    assert first.default is True
    assert second.default is False


def test_block_init_duplicate_name_errors(tmp_path):
    config_path = write_minimal_labb_yaml(tmp_path)
    clear_config_cache()

    existing_config = LabbConfig(
        blocks=BlocksConfig(
            collections=[
                BlockCollection(
                    name="blocks", path=str(tmp_path / "blocks"), default=True
                )
            ],
            sources=[],
        )
    )

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=existing_config),
        patch("labb.cli.handlers.blocks.save_config") as mock_save,
        pytest.raises(typer.Exit),
    ):
        block_init(name="blocks", path=str(tmp_path / "blocks"), silent=True)

    mock_save.assert_not_called()


def test_block_init_labbhq_not_added_twice(tmp_path):
    config_path = write_minimal_labb_yaml(tmp_path)
    clear_config_cache()

    existing_config = LabbConfig(
        blocks=BlocksConfig(
            collections=[
                BlockCollection(
                    name="blocks", path=str(tmp_path / "blocks"), default=True
                )
            ],
            sources=[
                BlockSource(name="labbhq", url="https://github.com/labbhq/blocks")
            ],
        )
    )

    saved = []

    def fake_save(cfg, path=None):
        saved.append((cfg, path))

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=existing_config),
        patch("labb.cli.handlers.blocks.save_config", side_effect=fake_save),
    ):
        block_init(name="premium", path=str(tmp_path / "premium"), silent=True)

    cfg, _ = saved[0]
    source_names = [s.name for s in cfg.blocks.sources]
    assert source_names.count("labbhq") == 1


def test_block_init_silent_mode_no_output(tmp_path, capsys):
    config_path = write_minimal_labb_yaml(tmp_path)
    clear_config_cache()

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.save_config"),
    ):
        clear_config_cache()
        block_init(name="blocks", path=str(tmp_path / "blocks"), silent=True)

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_block_init_no_labb_yaml_errors(tmp_path):
    clear_config_cache()

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=None),
        patch("labb.cli.handlers.blocks.save_config") as mock_save,
        pytest.raises(typer.Exit),
    ):
        block_init(name="blocks", path=str(tmp_path / "blocks"), silent=True)

    mock_save.assert_not_called()


# ===========================================================================
# block_add
# ===========================================================================


def make_source_repo(base: Path, vendor: str = "lb") -> Path:
    src = base / "source"
    src.mkdir(parents=True, exist_ok=True)

    (src / "blocks.yaml").write_text(f"vendor: {vendor}\n")

    models_dir = src / "models"
    models_dir.mkdir()
    (models_dir / "__init__.py").write_text(
        f"from .todo import Lb{vendor.title()}Todo\n"
    )
    (models_dir / "todo.py").write_text(
        f"from django.db import models\n"
        f"class Lb{vendor.title()}Todo(models.Model):\n"
        f"    text = models.CharField(max_length=200)\n"
    )

    block_dir = src / "crud" / "todos"
    block_dir.mkdir(parents=True)
    (block_dir / "block.yaml").write_text(
        "name: Todo List\n"
        "ref: crud/todos\n"
        "type: fullstack\n"
        "tier: free\n"
        "labb_version: '>=0.5.0'\n"
        "description: Todo list\n"
    )
    (block_dir / "views.py").write_text(
        f"from labb.contrib.blocks import lm\nModel = lm('Lb{vendor.title()}Todo')\n"
    )
    (block_dir / "urls.py").write_text(
        "from django.urls import path\nurlpatterns = []\n"
    )
    templates_dir = block_dir / "templates"
    templates_dir.mkdir()
    (templates_dir / "index.html").write_text("<div>todos</div>")

    (src / "index.yaml").write_text(
        f"blocks:\n"
        f"  - ref: {vendor}/crud/todos\n"
        f"    name: Todo List\n"
        f"    type: fullstack\n"
        f"    tier: free\n"
        f"    description: Todo list\n"
    )

    (src / "fixtures.json").write_text(
        f'[{{"model": "{vendor}.lb{vendor.lower()}todo", "pk": 1, "fields": {{"text": "Test"}}}}\n]\n'
    )

    return src


def make_collection(base: Path, name: str = "blocks") -> Path:
    col = base / name
    col.mkdir()
    (col / "__init__.py").write_text("")
    (col / "apps.py").write_text(
        f"from django.apps import AppConfig\n\n"
        f"class BlocksConfig(AppConfig):\n"
        f"    name = '{name}'\n"
        f"    label = '{name}'\n"
    )
    models_dir = col / "models"
    models_dir.mkdir()
    (models_dir / "__init__.py").write_text("")
    (col / "templates").mkdir()
    (col / "fixtures").mkdir()
    return col


def make_labb_config_add(
    tmp_path: Path, source_path: Path, collection_path: Path
) -> Path:
    config_path = tmp_path / "labb.yaml"
    config_path.write_text(
        f"css:\n"
        f"  build:\n"
        f"    input: in.css\n"
        f"    output: out.css\n"
        f"blocks:\n"
        f"  collections:\n"
        f"    - name: blocks\n"
        f"      path: {collection_path}\n"
        f"      default: true\n"
        f"  sources:\n"
        f"    - name: local\n"
        f"      path: {source_path}\n"
    )
    return config_path


def make_labb_config_object_add(source_path: Path, collection_path: Path) -> LabbConfig:
    return LabbConfig(
        blocks=BlocksConfig(
            collections=[
                BlockCollection(
                    name="blocks",
                    path=str(collection_path),
                    default=True,
                )
            ],
            sources=[
                BlockSource(name="local", path=str(source_path)),
            ],
        )
    )


def test_block_add_first_time(tmp_path):
    source_path = make_source_repo(tmp_path)
    collection_path = make_collection(tmp_path)
    config_path = make_labb_config_add(tmp_path, source_path, collection_path)
    config_obj = make_labb_config_object_add(source_path, collection_path)

    clear_config_cache()

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config_obj),
    ):
        block_add("lb/crud/todos")

    assert (collection_path / "lb" / "crud" / "todos" / "views.py").exists()
    assert (collection_path / "lb" / "crud" / "todos" / "urls.py").exists()
    assert (
        collection_path / "templates" / "lb" / "crud" / "todos" / "index.html"
    ).exists()
    assert (collection_path / "lb" / "models" / "todo.py").exists()

    fixture_file = collection_path / "fixtures" / "lb.json"
    assert fixture_file.exists()
    content = fixture_file.read_text()
    assert '"blocks.' in content
    assert '"lb.' not in content

    models_init = (collection_path / "models" / "__init__.py").read_text()
    assert "from ..lb.models import *" in models_init


def test_block_add_second_time_skips_models(tmp_path):
    source_path = make_source_repo(tmp_path)
    collection_path = make_collection(tmp_path)
    config_path = make_labb_config_add(tmp_path, source_path, collection_path)
    config_obj = make_labb_config_object_add(source_path, collection_path)

    clear_config_cache()

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config_obj),
    ):
        block_add("lb/crud/todos")

    todo_file = collection_path / "lb" / "models" / "todo.py"
    original_content = todo_file.read_text()
    sentinel = "# DO NOT OVERWRITE\n"
    todo_file.write_text(sentinel + original_content)

    clear_config_cache()

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config_obj),
    ):
        block_add("lb/crud/todos")

    assert sentinel in todo_file.read_text()

    models_init_content = (collection_path / "models" / "__init__.py").read_text()
    assert models_init_content.count("from ..lb.models import *") == 1


def test_block_add_invalid_ref_format(tmp_path):
    source_path = make_source_repo(tmp_path)
    collection_path = make_collection(tmp_path)
    config_path = make_labb_config_add(tmp_path, source_path, collection_path)
    config_obj = make_labb_config_object_add(source_path, collection_path)

    clear_config_cache()

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config_obj),
        pytest.raises(typer.Exit),
    ):
        block_add("lb/crud")


def test_block_add_source_not_found(tmp_path):
    source_path = make_source_repo(tmp_path)
    collection_path = make_collection(tmp_path)
    config_path = make_labb_config_add(tmp_path, source_path, collection_path)
    config_obj = make_labb_config_object_add(source_path, collection_path)

    clear_config_cache()

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config_obj),
        pytest.raises(typer.Exit),
    ):
        block_add("lb/crud/nonexistent")


def test_block_add_creates_init_files(tmp_path):
    source_path = make_source_repo(tmp_path)
    collection_path = make_collection(tmp_path)
    config_path = make_labb_config_add(tmp_path, source_path, collection_path)
    config_obj = make_labb_config_object_add(source_path, collection_path)

    clear_config_cache()

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config_obj),
    ):
        block_add("lb/crud/todos")

    assert (collection_path / "lb" / "__init__.py").exists()
    assert (collection_path / "lb" / "crud" / "__init__.py").exists()
    assert (collection_path / "lb" / "crud" / "todos" / "__init__.py").exists()


# ===========================================================================
# block_remove
# ===========================================================================


def make_installed_block(
    tmp_path: Path,
    vendor: str = "lb",
    category: str = "crud",
    slug: str = "todos",
) -> Path:
    col = tmp_path / "blocks"
    block_dir = col / vendor / category / slug
    block_dir.mkdir(parents=True)
    (block_dir / "views.py").write_text("# views")
    (block_dir / "urls.py").write_text("# urls")
    templates_dir = col / "templates" / vendor / category / slug
    templates_dir.mkdir(parents=True)
    (templates_dir / "index.html").write_text("<div></div>")
    models_dir = col / vendor / "models"
    models_dir.mkdir(parents=True)
    (models_dir / "todo.py").write_text("# model")
    fixtures_dir = col / "fixtures"
    fixtures_dir.mkdir(parents=True)
    (fixtures_dir / f"{vendor}.json").write_text("[]")
    top_models = col / "models"
    top_models.mkdir(exist_ok=True)
    (top_models / "__init__.py").write_text("from ..lb.models import *\n")
    return col


def make_labb_config_remove(tmp_path: Path, collection_path: Path) -> Path:
    config_path = tmp_path / "labb.yaml"
    config_path.write_text(
        f"css:\n  build:\n    input: in.css\n    output: out.css\n"
        f"blocks:\n"
        f"  collections:\n"
        f"    - name: blocks\n"
        f"      path: {collection_path}\n"
        f"      default: true\n"
        f"  sources: []\n"
    )
    return config_path


def make_config_remove(collection_path: Path) -> LabbConfig:
    return LabbConfig(
        blocks=BlocksConfig(
            collections=[
                BlockCollection(
                    name="blocks",
                    path=str(collection_path),
                    default=True,
                )
            ],
            sources=[],
        )
    )


@pytest.fixture(autouse=True)
def clear_cache():
    clear_config_cache()
    yield
    clear_config_cache()


def _patch_remove_config(tmp_path: Path, col: Path):
    config_path = make_labb_config_remove(tmp_path, col)
    cfg = make_config_remove(col)
    return (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=cfg),
    )


def test_block_remove_deletes_block_files(tmp_path):
    col = make_installed_block(tmp_path)
    p1, p2 = _patch_remove_config(tmp_path, col)
    with p1, p2:
        block_remove(ref="lb/crud/todos")
    assert not (col / "lb" / "crud" / "todos").exists()


def test_block_remove_deletes_templates(tmp_path):
    col = make_installed_block(tmp_path)
    p1, p2 = _patch_remove_config(tmp_path, col)
    with p1, p2:
        block_remove(ref="lb/crud/todos")
    assert not (col / "templates" / "lb" / "crud" / "todos").exists()


def test_block_remove_keeps_models(tmp_path):
    col = make_installed_block(tmp_path)
    p1, p2 = _patch_remove_config(tmp_path, col)
    with p1, p2:
        block_remove(ref="lb/crud/todos")
    assert (col / "lb" / "models" / "todo.py").exists()


def test_block_remove_keeps_fixtures(tmp_path):
    col = make_installed_block(tmp_path)
    p1, p2 = _patch_remove_config(tmp_path, col)
    with p1, p2:
        block_remove(ref="lb/crud/todos")
    assert (col / "fixtures" / "lb.json").exists()


def test_block_remove_keeps_models_init(tmp_path):
    col = make_installed_block(tmp_path)
    p1, p2 = _patch_remove_config(tmp_path, col)
    with p1, p2:
        block_remove(ref="lb/crud/todos")
    init_file = col / "models" / "__init__.py"
    assert init_file.exists()
    assert init_file.read_text() == "from ..lb.models import *\n"


def test_block_remove_output_uses_variables(tmp_path, capsys):
    """block_remove output includes the vendor name and the models path using variables."""
    col = make_installed_block(tmp_path)
    p1, p2 = _patch_remove_config(tmp_path, col)
    with p1, p2:
        block_remove(ref="lb/crud/todos")
    captured = capsys.readouterr()
    full_out = captured.out.replace("\n", " ")
    # The path to the vendor models dir should appear in the output (via variable)
    assert "lb/models/" in full_out


def test_block_remove_not_installed_errors(tmp_path):
    col = make_installed_block(tmp_path)
    p1, p2 = _patch_remove_config(tmp_path, col)
    with p1, p2:
        with pytest.raises((SystemExit, typer.Exit)) as exc_info:
            block_remove(ref="lb/crud/nonexistent")
    code = (
        exc_info.value.code
        if isinstance(exc_info.value, SystemExit)
        else exc_info.value.exit_code
    )
    assert code == 1


def test_block_remove_invalid_ref_format(tmp_path):
    col = make_installed_block(tmp_path)
    p1, p2 = _patch_remove_config(tmp_path, col)
    with p1, p2:
        with pytest.raises((SystemExit, typer.Exit)) as exc_info:
            block_remove(ref="lb/todos")
    code = (
        exc_info.value.code
        if isinstance(exc_info.value, SystemExit)
        else exc_info.value.exit_code
    )
    assert code == 1


# ===========================================================================
# block_sync
# ===========================================================================


def make_source_with_vendor(base: Path, vendor: str = "lb") -> Path:
    src = base / "source"
    src.mkdir()
    models_dir = src / "models"
    models_dir.mkdir()
    (models_dir / "__init__.py").write_text(
        f"from .todo import Lb{vendor.title()}Todo\n"
    )
    (models_dir / "todo.py").write_text(
        f"from django.db import models\n"
        f"class Lb{vendor.title()}Todo(models.Model):\n"
        f"    text = models.CharField(max_length=500)\n"
        f"    updated = models.BooleanField(default=False)\n"
    )
    (src / "fixtures.json").write_text(
        f'[{{"model": "{vendor}.lb{vendor.lower()}todo", "pk": 1, "fields": {{"text": "Test", "updated": false}}}}]\n'
    )
    (src / "index.yaml").write_text(
        f"blocks:\n  - ref: {vendor}/crud/todos\n    name: Todos\n    type: fullstack\n    tier: free\n    description: Todos\n"
    )
    return src


def make_installed_vendor(col: Path, vendor: str = "lb"):
    vendor_dir = col / vendor
    vendor_dir.mkdir(parents=True, exist_ok=True)
    models_dir = vendor_dir / "models"
    models_dir.mkdir()
    (models_dir / "__init__.py").write_text("# old content\n")
    (models_dir / "todo.py").write_text("# old model\n")
    fixtures_dir = col / "fixtures"
    fixtures_dir.mkdir(exist_ok=True)
    (fixtures_dir / f"{vendor}.json").write_text(
        '[{"model": "blocks.lbtodo", "pk": 1, "fields": {"text": "old"}}]\n'
    )


def make_labb_config_sync(
    tmp_path: Path, collection_path: Path, source_path: Path
) -> Path:
    config_path = tmp_path / "labb.yaml"
    config_path.write_text(
        f"css:\n  build:\n    input: in.css\n    output: out.css\n"
        f"blocks:\n"
        f"  collections:\n"
        f"    - name: blocks\n"
        f"      path: {collection_path}\n"
        f"      default: true\n"
        f"  sources:\n"
        f"    - name: localsrc\n"
        f"      path: {source_path}\n"
    )
    return config_path


def make_labb_config_object_sync(
    source_path: Path, collection_path: Path
) -> LabbConfig:
    return LabbConfig(
        blocks=BlocksConfig(
            collections=[
                BlockCollection(
                    name="blocks",
                    path=str(collection_path),
                    default=True,
                )
            ],
            sources=[
                BlockSource(name="localsrc", path=str(source_path)),
            ],
        )
    )


def setup_sync_test(tmp_path: Path, vendor: str = "lb"):
    col = tmp_path / "blocks"
    col.mkdir()
    (col / "models").mkdir()
    (col / "models" / "__init__.py").write_text("from ..lb.models import *\n")

    src = make_source_with_vendor(tmp_path, vendor)
    make_installed_vendor(col, vendor)
    config_path = make_labb_config_sync(tmp_path, col, src)
    config_obj = make_labb_config_object_sync(src, col)
    return config_path, config_obj, col


def test_sync_models_overwrites_existing(tmp_path):
    config_path, config_obj, col = setup_sync_test(tmp_path)

    clear_config_cache()
    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config_obj),
    ):
        block_sync(vendor="lb")

    todo_file = col / "lb" / "models" / "todo.py"
    content = todo_file.read_text()
    assert "# old model" not in content
    assert "models.CharField(max_length=500)" in content


def test_sync_fixtures_overwrites_existing(tmp_path):
    config_path, config_obj, col = setup_sync_test(tmp_path)

    clear_config_cache()
    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config_obj),
    ):
        block_sync(vendor="lb")

    fixture_file = col / "fixtures" / "lb.json"
    content = fixture_file.read_text()
    assert '"blocks.' in content
    assert '"lb.' not in content
    assert "Test" in content
    assert "old" not in content


def test_sync_models_only_skips_fixtures(tmp_path):
    config_path, config_obj, col = setup_sync_test(tmp_path)

    fixture_file = col / "fixtures" / "lb.json"
    original_fixture_content = fixture_file.read_text()

    clear_config_cache()
    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config_obj),
    ):
        block_sync(vendor="lb", models_only=True)

    assert fixture_file.read_text() == original_fixture_content


def test_sync_fixtures_only_skips_models(tmp_path):
    config_path, config_obj, col = setup_sync_test(tmp_path)

    todo_file = col / "lb" / "models" / "todo.py"
    original_model_content = todo_file.read_text()

    clear_config_cache()
    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config_obj),
    ):
        block_sync(vendor="lb", fixtures_only=True)

    assert todo_file.read_text() == original_model_content


def test_sync_does_not_touch_collection_models_init(tmp_path):
    config_path, config_obj, col = setup_sync_test(tmp_path)

    collection_init = col / "models" / "__init__.py"
    original_init_content = collection_init.read_text()

    clear_config_cache()
    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config_obj),
    ):
        block_sync(vendor="lb")

    assert collection_init.read_text() == original_init_content


def test_sync_vendor_not_installed_errors(tmp_path):
    col = tmp_path / "blocks"
    col.mkdir()

    src = make_source_with_vendor(tmp_path, "lb")
    config_path = make_labb_config_sync(tmp_path, col, src)
    config_obj = make_labb_config_object_sync(src, col)

    clear_config_cache()
    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config_obj),
        pytest.raises(typer.Exit),
    ):
        block_sync(vendor="lb")


def test_sync_no_source_for_vendor_errors(tmp_path):
    col = tmp_path / "blocks"
    col.mkdir()
    make_installed_vendor(col, "lb")

    src = tmp_path / "source"
    src.mkdir()
    (src / "index.yaml").write_text(
        "blocks:\n  - ref: other/crud/todos\n    name: Other\n    type: fullstack\n    tier: free\n    description: Other\n"
    )
    (src / "models").mkdir()
    (src / "fixtures.json").write_text("[]")

    config_path = make_labb_config_sync(tmp_path, col, src)
    config_obj = make_labb_config_object_sync(src, col)

    clear_config_cache()
    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config_obj),
        pytest.raises(typer.Exit),
    ):
        block_sync(vendor="lb")


# ---------------------------------------------------------------------------
# block_sync — template coverage (cotton-merge split)
# ---------------------------------------------------------------------------


def add_source_block_templates(
    src: Path,
    vendor: str = "lb",
    category: str = "crud",
    slug: str = "todos",
    page_body: str = "<div>page</div>",
    cotton_body: str = "<li>row</li>",
) -> None:
    """Give the source repo a block with pages/ + cotton/ templates."""
    block_dir = src / category / slug
    (block_dir / "templates" / "pages").mkdir(parents=True, exist_ok=True)
    (block_dir / "templates" / "pages" / "index.html").write_text(page_body)
    (block_dir / "templates" / "cotton" / slug).mkdir(parents=True, exist_ok=True)
    (block_dir / "templates" / "cotton" / slug / "row.html").write_text(cotton_body)


def add_installed_block_dir(
    col: Path, vendor: str = "lb", category: str = "crud", slug: str = "todos"
) -> None:
    """Give the installed collection a block package so sync iterates it."""
    d = col / vendor / category / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / "__init__.py").write_text("")


def setup_template_sync_test(tmp_path: Path, vendor: str = "lb"):
    config_path, config_obj, col = setup_sync_test(tmp_path, vendor)
    src = tmp_path / "source"
    add_source_block_templates(src, vendor)
    add_installed_block_dir(col, vendor)
    return config_path, config_obj, col


def _run_sync(config_path, config_obj, **kwargs):
    clear_config_cache()
    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config_obj),
    ):
        block_sync(vendor="lb", **kwargs)


def test_sync_templates_pages_go_under_vendor_path(tmp_path):
    config_path, config_obj, col = setup_template_sync_test(tmp_path)
    _run_sync(config_path, config_obj)

    page = col / "templates" / "lb" / "crud" / "todos" / "pages" / "index.html"
    assert page.exists()
    assert page.read_text() == "<div>page</div>"


def test_sync_templates_cotton_merged_into_global_root(tmp_path):
    config_path, config_obj, col = setup_template_sync_test(tmp_path)
    _run_sync(config_path, config_obj)

    # cotton lands in the global templates/cotton/, NOT nested under the block path
    merged = col / "templates" / "cotton" / "todos" / "row.html"
    assert merged.exists()
    assert merged.read_text() == "<li>row</li>"
    nested = col / "templates" / "lb" / "crud" / "todos" / "cotton"
    assert not nested.exists()


def test_sync_templates_overwrites_existing(tmp_path):
    config_path, config_obj, col = setup_template_sync_test(tmp_path)
    # stale copies already present
    page = col / "templates" / "lb" / "crud" / "todos" / "pages" / "index.html"
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text("STALE")
    cotton = col / "templates" / "cotton" / "todos" / "row.html"
    cotton.parent.mkdir(parents=True, exist_ok=True)
    cotton.write_text("STALE")

    _run_sync(config_path, config_obj)

    assert page.read_text() == "<div>page</div>"
    assert cotton.read_text() == "<li>row</li>"


def test_sync_templates_only_skips_models_and_fixtures(tmp_path):
    config_path, config_obj, col = setup_template_sync_test(tmp_path)
    model = col / "lb" / "models" / "todo.py"
    original_model = model.read_text()
    fixture = col / "fixtures" / "lb.json"
    original_fixture = fixture.read_text()

    _run_sync(config_path, config_obj, templates_only=True)

    assert model.read_text() == original_model
    assert fixture.read_text() == original_fixture
    assert (col / "templates" / "cotton" / "todos" / "row.html").exists()


def test_sync_models_only_skips_templates(tmp_path):
    config_path, config_obj, col = setup_template_sync_test(tmp_path)
    _run_sync(config_path, config_obj, models_only=True)

    assert not (col / "templates" / "cotton" / "todos" / "row.html").exists()
    assert not (col / "templates" / "lb" / "crud" / "todos" / "pages").exists()


def test_sync_default_covers_models_fixtures_and_templates(tmp_path):
    config_path, config_obj, col = setup_template_sync_test(tmp_path)
    _run_sync(config_path, config_obj)

    assert (
        "models.CharField(max_length=500)"
        in (col / "lb" / "models" / "todo.py").read_text()
    )
    assert '"blocks.' in (col / "fixtures" / "lb.json").read_text()
    assert (col / "templates" / "cotton" / "todos" / "row.html").exists()


def _add_source_block_code(tmp_path, category="crud", slug="todos"):
    """Give the source block a views.py + block.yaml (templates helper omits them)."""
    block = tmp_path / "source" / category / slug
    block.mkdir(parents=True, exist_ok=True)
    (block / "views.py").write_text("def index(request):\n    return FRESH\n")
    (block / "block.yaml").write_text("name: Todos\n")


def test_sync_default_copies_block_code(tmp_path):
    config_path, config_obj, col = setup_template_sync_test(tmp_path)
    _add_source_block_code(tmp_path)
    # A stale installed views.py must be overwritten from source.
    installed = col / "lb" / "crud" / "todos" / "views.py"
    installed.write_text("STALE")

    _run_sync(config_path, config_obj)

    assert installed.read_text() == "def index(request):\n    return FRESH\n"
    assert (col / "lb" / "crud" / "todos" / "block.yaml").read_text() == "name: Todos\n"


def test_sync_templates_only_skips_block_code(tmp_path):
    config_path, config_obj, col = setup_template_sync_test(tmp_path)
    _add_source_block_code(tmp_path)
    installed = col / "lb" / "crud" / "todos" / "views.py"
    installed.write_text("STALE")

    _run_sync(config_path, config_obj, templates_only=True)

    assert installed.read_text() == "STALE"


# ===========================================================================
# block_list and block_search
# ===========================================================================


def make_local_source(
    tmp_path: Path, name: str = "mysource", vendor: str = "lb"
) -> Path:
    src = tmp_path / name
    src.mkdir()
    (src / "index.yaml").write_text(
        f"blocks:\n"
        f"  - ref: {vendor}/crud/todos\n"
        f"    name: Todo List\n"
        f"    type: fullstack\n"
        f"    tier: free\n"
        f"    description: A todo list with CRUD operations\n"
        f"  - ref: {vendor}/crud/contacts\n"
        f"    name: Contact List\n"
        f"    type: fullstack\n"
        f"    tier: free\n"
        f"    description: A contacts manager\n"
    )
    return src


def make_config_with_local_source(tmp_path: Path, source_path: Path) -> Path:
    config_path = tmp_path / "labb.yaml"
    config_path.write_text(
        f"css:\n  build:\n    input: in.css\n    output: out.css\n"
        f"blocks:\n"
        f"  collections: []\n"
        f"  sources:\n"
        f"    - name: mysource\n"
        f"      path: {source_path}\n"
    )
    return config_path


def _make_list_config(sources=None) -> LabbConfig:
    return LabbConfig(
        blocks=BlocksConfig(
            collections=[],
            sources=list(sources) if sources else [],
        )
    )


def test_block_list_shows_all_blocks(tmp_path, capsys):
    source_path = make_local_source(tmp_path)
    config_path = make_config_with_local_source(tmp_path, source_path)
    config = LabbConfig(
        blocks=BlocksConfig(
            collections=[],
            sources=[BlockSource(name="mysource", path=str(source_path))],
        )
    )

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config),
    ):
        block_list()

    captured = capsys.readouterr()
    assert "lb/crud/todos" in captured.out
    assert "Todo List" in captured.out
    assert "lb/crud/contacts" in captured.out
    assert "Contact List" in captured.out


def test_block_list_source_column(tmp_path, capsys):
    source_path = make_local_source(tmp_path)
    config_path = make_config_with_local_source(tmp_path, source_path)
    config = LabbConfig(
        blocks=BlocksConfig(
            collections=[],
            sources=[BlockSource(name="mysource", path=str(source_path))],
        )
    )

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config),
    ):
        block_list()

    captured = capsys.readouterr()
    assert "mysource" in captured.out


def test_block_list_filter_by_source(tmp_path, capsys):
    source_a = make_local_source(tmp_path, name="sourcea", vendor="lb")
    source_b_dir = tmp_path / "sourceb"
    source_b_dir.mkdir()
    (source_b_dir / "index.yaml").write_text(
        "blocks:\n"
        "  - ref: lb/auth/login\n"
        "    name: Login Card\n"
        "    type: fe\n"
        "    tier: free\n"
        "    description: A login card\n"
    )
    config_path = tmp_path / "labb.yaml"
    config_path.write_text("css:\n  build:\n    input: in.css\n    output: out.css\n")
    config = LabbConfig(
        blocks=BlocksConfig(
            collections=[],
            sources=[
                BlockSource(name="sourcea", path=str(source_a)),
                BlockSource(name="sourceb", path=str(source_b_dir)),
            ],
        )
    )

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config),
    ):
        block_list(source_name="sourcea")

    captured = capsys.readouterr()
    assert "lb/crud/todos" in captured.out
    assert "lb/auth/login" not in captured.out


def test_block_list_unknown_source_errors(tmp_path, capsys):
    source_path = make_local_source(tmp_path)
    config_path = make_config_with_local_source(tmp_path, source_path)
    config = LabbConfig(
        blocks=BlocksConfig(
            collections=[],
            sources=[BlockSource(name="mysource", path=str(source_path))],
        )
    )

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config),
    ):
        block_list(source_name="nonexistent")

    captured = capsys.readouterr()
    assert "nonexistent" in captured.out


def test_block_list_no_sources_configured(tmp_path, capsys):
    config_path = tmp_path / "labb.yaml"
    config_path.write_text("css:\n  build:\n    input: in.css\n    output: out.css\n")
    config = LabbConfig(blocks=BlocksConfig(collections=[], sources=[]))

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config),
    ):
        block_list()

    captured = capsys.readouterr()
    assert "No sources configured." in captured.out


def test_block_list_missing_index_yaml(tmp_path, capsys):
    source_dir = tmp_path / "emptysource"
    source_dir.mkdir()
    config_path = tmp_path / "labb.yaml"
    config_path.write_text("css:\n  build:\n    input: in.css\n    output: out.css\n")
    config = LabbConfig(
        blocks=BlocksConfig(
            collections=[],
            sources=[BlockSource(name="emptysource", path=str(source_dir))],
        )
    )

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config),
    ):
        block_list()

    captured = capsys.readouterr()
    assert "emptysource" in captured.out


def test_block_list_no_blocks_section(tmp_path, capsys):
    config_path = tmp_path / "labb.yaml"
    config_path.write_text("css:\n  build:\n    input: in.css\n    output: out.css\n")
    config = LabbConfig(blocks=None)

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config),
    ):
        block_list()

    captured = capsys.readouterr()
    assert "No sources configured." in captured.out


def test_block_search_matches_name(tmp_path, capsys):
    source_path = make_local_source(tmp_path)
    config_path = make_config_with_local_source(tmp_path, source_path)
    config = LabbConfig(
        blocks=BlocksConfig(
            collections=[],
            sources=[BlockSource(name="mysource", path=str(source_path))],
        )
    )

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config),
    ):
        block_search("todo")

    captured = capsys.readouterr()
    assert "Todo List" in captured.out
    assert "Contact List" not in captured.out


def test_block_search_matches_ref(tmp_path, capsys):
    source_path = make_local_source(tmp_path)
    config_path = make_config_with_local_source(tmp_path, source_path)
    config = LabbConfig(
        blocks=BlocksConfig(
            collections=[],
            sources=[BlockSource(name="mysource", path=str(source_path))],
        )
    )

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config),
    ):
        block_search("contacts")

    captured = capsys.readouterr()
    assert "lb/crud/contacts" in captured.out
    assert "lb/crud/todos" not in captured.out


def test_block_search_matches_description(tmp_path, capsys):
    source_path = make_local_source(tmp_path)
    config_path = make_config_with_local_source(tmp_path, source_path)
    config = LabbConfig(
        blocks=BlocksConfig(
            collections=[],
            sources=[BlockSource(name="mysource", path=str(source_path))],
        )
    )

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config),
    ):
        block_search("CRUD")

    captured = capsys.readouterr()
    assert "Todo List" in captured.out


def test_block_search_no_results(tmp_path, capsys):
    source_path = make_local_source(tmp_path)
    config_path = make_config_with_local_source(tmp_path, source_path)
    config = LabbConfig(
        blocks=BlocksConfig(
            collections=[],
            sources=[BlockSource(name="mysource", path=str(source_path))],
        )
    )

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config),
    ):
        block_search("xyzzy")

    captured = capsys.readouterr()
    assert "No blocks found matching 'xyzzy'." in captured.out


# ===========================================================================
# source_add and source_list
# ===========================================================================


def make_config_with_blocks_src(tmp_path: Path) -> Path:
    config_path = tmp_path / "labb.yaml"
    config_path.write_text(
        "css:\n"
        "  build:\n"
        "    input: static_src/input.css\n"
        "    output: static/css/output.css\n"
        "blocks:\n"
        "  collections: []\n"
        "  sources: []\n"
    )
    return config_path


def _make_source_config(sources=None) -> LabbConfig:
    return LabbConfig(
        blocks=BlocksConfig(
            collections=[],
            sources=list(sources) if sources else [],
        )
    )


def test_source_add_remote(tmp_path):
    config_path = make_config_with_blocks_src(tmp_path)
    clear_config_cache()

    saved = []

    def fake_save(cfg, path=None):
        saved.append((cfg, path))

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.save_config", side_effect=fake_save),
    ):
        clear_config_cache()
        source_add("labbhq", url="https://github.com/labbhq/blocks", path=None)

    assert len(saved) == 1
    cfg, _ = saved[0]
    assert len(cfg.blocks.sources) == 1
    s = cfg.blocks.sources[0]
    assert s.name == "labbhq"
    assert s.url == "https://github.com/labbhq/blocks"
    assert s.path is None


def test_source_add_local(tmp_path):
    config_path = make_config_with_blocks_src(tmp_path)
    clear_config_cache()

    saved = []

    def fake_save(cfg, path=None):
        saved.append((cfg, path))

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.save_config", side_effect=fake_save),
    ):
        clear_config_cache()
        source_add("local", url=None, path="./my-blocks")

    assert len(saved) == 1
    cfg, _ = saved[0]
    s = cfg.blocks.sources[0]
    assert s.name == "local"
    assert s.url is None
    assert s.path == "./my-blocks"


def test_source_add_duplicate_name_errors(tmp_path):
    config_path = make_config_with_blocks_src(tmp_path)
    clear_config_cache()

    existing_config = LabbConfig(
        blocks=BlocksConfig(
            collections=[],
            sources=[
                BlockSource(name="labbhq", url="https://github.com/labbhq/blocks")
            ],
        )
    )

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=existing_config),
        patch("labb.cli.handlers.blocks.save_config") as mock_save,
        pytest.raises(typer.Exit),
    ):
        source_add("labbhq", url="https://github.com/other/repo", path=None)

    mock_save.assert_not_called()


def test_source_add_both_url_and_path_errors(tmp_path):
    config_path = make_config_with_blocks_src(tmp_path)
    clear_config_cache()

    empty_config = _make_source_config()

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=empty_config),
        patch("labb.cli.handlers.blocks.save_config") as mock_save,
        pytest.raises(typer.Exit),
    ):
        source_add("mysource", url="https://example.com/repo", path="./local-path")

    mock_save.assert_not_called()


def test_source_add_neither_url_nor_path_errors(tmp_path):
    config_path = make_config_with_blocks_src(tmp_path)
    clear_config_cache()

    empty_config = _make_source_config()

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=empty_config),
        patch("labb.cli.handlers.blocks.save_config") as mock_save,
        pytest.raises(typer.Exit),
    ):
        source_add("mysource", url=None, path=None)

    mock_save.assert_not_called()


def test_source_add_no_blocks_section_errors(tmp_path, capsys):
    config_path = tmp_path / "labb.yaml"
    config_path.write_text(
        "css:\n  build:\n    input: static_src/input.css\n    output: static/css/output.css\n"
    )

    no_blocks_config = LabbConfig(blocks=None)

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=no_blocks_config),
        patch("labb.cli.handlers.blocks.save_config") as mock_save,
        pytest.raises(typer.Exit),
    ):
        source_add("labbhq", url="https://github.com/labbhq/blocks", path=None)

    mock_save.assert_not_called()


def test_source_list_empty(tmp_path, capsys):
    config_path = make_config_with_blocks_src(tmp_path)
    clear_config_cache()

    empty_config = _make_source_config()

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=empty_config),
    ):
        source_list()

    captured = capsys.readouterr()
    assert "No sources configured." in captured.out


def test_source_list_shows_remote_and_local(tmp_path, capsys):
    config_path = make_config_with_blocks_src(tmp_path)
    clear_config_cache()

    config_with_sources = _make_source_config(
        sources=[
            BlockSource(name="labbhq", url="https://github.com/labbhq/blocks"),
            BlockSource(name="local", path="./my-custom-blocks"),
        ]
    )

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config_with_sources),
    ):
        source_list()

    captured = capsys.readouterr()
    assert "Sources:" in captured.out
    assert "labbhq" in captured.out
    assert "https://github.com/labbhq/blocks" in captured.out
    assert "remote" in captured.out
    assert "local" in captured.out
    assert "./my-custom-blocks" in captured.out


def test_source_add_remote_with_subdir(tmp_path):
    config_path = make_config_with_blocks_src(tmp_path)
    clear_config_cache()

    saved = []

    def fake_save(cfg, path=None):
        saved.append((cfg, path))

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.save_config", side_effect=fake_save),
    ):
        clear_config_cache()
        source_add(
            "labbhq",
            url="https://github.com/labbhq/labb",
            path=None,
            subdir="extras/blocks",
        )

    cfg, _ = saved[0]
    assert cfg.blocks.sources[0].subdir == "extras/blocks"


def test_source_add_without_subdir_leaves_it_unset(tmp_path):
    config_path = make_config_with_blocks_src(tmp_path)
    clear_config_cache()

    saved = []

    def fake_save(cfg, path=None):
        saved.append((cfg, path))

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.save_config", side_effect=fake_save),
    ):
        clear_config_cache()
        source_add("local", url=None, path="./my-blocks")

    cfg, _ = saved[0]
    assert cfg.blocks.sources[0].subdir is None


UNSAFE_REFS = [
    "../etc/passwd",
    "lb/../../etc",
    "lb/crud/..",
    "lb/./todos",
    "lb//todos",
    "/lb/crud/todos",
    "lb/crud/to dos",
    "LB/crud/todos",
    "-lb/crud/todos",
]


@pytest.mark.parametrize(
    "ref",
    [
        "lb/data-table/customers",
        "lb/auth/centred-card",
        "lb/wizard/horizontal-steps",
        "lb/crud/todos",
        "acme2/dashboard/v1.2",
        "a_b/c_d/e_f",
    ],
)
def test_parse_ref_accepts_real_refs(ref):
    vendor, category, slug = _parse_ref(ref)
    assert f"{vendor}/{category}/{slug}" == ref


@pytest.mark.parametrize("ref", UNSAFE_REFS)
def test_parse_ref_rejects_unsafe_refs(ref):
    with pytest.raises(typer.Exit):
        _parse_ref(ref)


@pytest.mark.parametrize("ref", UNSAFE_REFS)
def test_block_add_rejects_unsafe_ref(tmp_path, ref):
    source_path = make_source_repo(tmp_path)
    collection_path = make_collection(tmp_path)
    config_path = make_labb_config_add(tmp_path, source_path, collection_path)
    config_obj = make_labb_config_object_add(source_path, collection_path)

    clear_config_cache()

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config_obj),
        pytest.raises(typer.Exit),
    ):
        block_add(ref)


def test_block_remove_traversal_ref_leaves_outside_dir_alone(tmp_path):
    col = make_installed_block(tmp_path)
    victim = tmp_path / "victim" / "inner"
    victim.mkdir(parents=True)
    (victim / "keep.txt").write_text("keep")

    p1, p2 = _patch_remove_config(tmp_path, col)
    with p1, p2, pytest.raises(typer.Exit):
        block_remove(ref="../victim/inner")

    assert (victim / "keep.txt").exists()


@pytest.mark.parametrize("ref", UNSAFE_REFS)
def test_block_remove_rejects_unsafe_ref(tmp_path, ref):
    col = make_installed_block(tmp_path)
    p1, p2 = _patch_remove_config(tmp_path, col)
    with p1, p2, pytest.raises(typer.Exit):
        block_remove(ref=ref)

    assert (col / "lb" / "crud" / "todos").exists()


@pytest.mark.parametrize("vendor", ["..", "../lb", "lb/..", "L B"])
def test_block_sync_rejects_unsafe_vendor(tmp_path, vendor):
    config_path, config_obj, col = setup_sync_test(tmp_path)

    clear_config_cache()
    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config_obj),
        pytest.raises(typer.Exit),
    ):
        block_sync(vendor=vendor)


def test_clone_source_returns_none_on_timeout():
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="git", timeout=60)

    source = BlockSource(name="slow", url="https://x/hangs")
    with patch("labb.cli.handlers.blocks.subprocess.run", timeout):
        assert _clone_source(source, "/tmp/clone") is None


def test_clone_source_returns_none_when_git_is_missing():
    def no_git(*args, **kwargs):
        raise FileNotFoundError("git")

    source = BlockSource(name="s", url="https://x/blocks")
    with patch("labb.cli.handlers.blocks.subprocess.run", no_git):
        assert _clone_source(source, "/tmp/clone") is None


def _fake_clone_env(tmp_path, index_ref="lb/crud/other"):
    """Remote source whose clone lands in tmp_path and never matches."""
    made = []

    def fake_mkdtemp(*args, **kwargs):
        d = tmp_path / f"clone{len(made)}"
        d.mkdir()
        made.append(d)
        return str(d)

    def fake_clone(source, tmp_dir):
        root = Path(tmp_dir)
        (root / "index.yaml").write_text(f"blocks:\n  - ref: {index_ref}\n")
        return root

    return made, fake_mkdtemp, fake_clone


def test_resolve_source_removes_clones_when_ref_not_found(tmp_path):
    made, fake_mkdtemp, fake_clone = _fake_clone_env(tmp_path)
    sources = [BlockSource(name="remote", url="https://x/blocks")]

    with (
        patch("labb.cli.handlers.blocks.tempfile.mkdtemp", fake_mkdtemp),
        patch("labb.cli.handlers.blocks._clone_source", fake_clone),
        pytest.raises(typer.Exit),
    ):
        with _resolve_source_for_ref("lb/crud/todos", sources, tmp_path):
            pass

    assert made
    assert not any(d.exists() for d in made)


def test_resolve_source_removes_clones_when_vendor_not_found(tmp_path):
    made, fake_mkdtemp, fake_clone = _fake_clone_env(tmp_path)
    sources = [BlockSource(name="remote", url="https://x/blocks")]

    with (
        patch("labb.cli.handlers.blocks.tempfile.mkdtemp", fake_mkdtemp),
        patch("labb.cli.handlers.blocks._clone_source", fake_clone),
        pytest.raises(typer.Exit),
    ):
        with _resolve_source_for_ref("acme", sources, tmp_path, match_by="vendor"):
            pass

    assert made
    assert not any(d.exists() for d in made)


def test_resolve_source_removes_clones_on_the_match_path(tmp_path):
    made, fake_mkdtemp, fake_clone = _fake_clone_env(
        tmp_path, index_ref="lb/crud/todos"
    )
    sources = [BlockSource(name="remote", url="https://x/blocks")]

    with (
        patch("labb.cli.handlers.blocks.tempfile.mkdtemp", fake_mkdtemp),
        patch("labb.cli.handlers.blocks._clone_source", fake_clone),
    ):
        with _resolve_source_for_ref("lb/crud/todos", sources, tmp_path) as (
            matched,
            root,
            entry,
        ):
            assert matched.name == "remote"
            assert root.exists()
            assert entry["ref"] == "lb/crud/todos"

    assert made
    assert not any(d.exists() for d in made)


def _mark_index_demo(source_path: Path) -> None:
    index = source_path / "index.yaml"
    index.write_text(index.read_text() + "    demo: true\n")


def test_block_add_warns_for_a_demo_block(tmp_path, capsys):
    source_path = make_source_repo(tmp_path)
    _mark_index_demo(source_path)
    collection_path = make_collection(tmp_path)
    config_path = make_labb_config_add(tmp_path, source_path, collection_path)
    config_obj = make_labb_config_object_add(source_path, collection_path)

    clear_config_cache()

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config_obj),
    ):
        block_add("lb/crud/todos")

    assert "is a UI demo" in capsys.readouterr().out


def test_block_add_stays_quiet_for_a_normal_block(tmp_path, capsys):
    source_path = make_source_repo(tmp_path)
    collection_path = make_collection(tmp_path)
    config_path = make_labb_config_add(tmp_path, source_path, collection_path)
    config_obj = make_labb_config_object_add(source_path, collection_path)

    clear_config_cache()

    with (
        patch("labb.cli.handlers.blocks.find_config_file", return_value=config_path),
        patch("labb.cli.handlers.blocks.load_config", return_value=config_obj),
    ):
        block_add("lb/crud/todos")

    assert "is a UI demo" not in capsys.readouterr().out
