import yaml

from labb.cli.handlers.migrate_handler import _backup, _plan_packages, migrate_config


def test_plan_packages_maps_apps_to_components():
    plan = _plan_packages(
        {"labb": ["templates/cotton/lbb/**/*.html"], "labbdocs": None}
    )
    assert plan["labb"] == {"components": ["templates/cotton/lbb/**/*.html"]}
    assert plan["labbdocs"] == {"components": []}


def _legacy_project(tmp_path):
    (tmp_path / "static_src").mkdir()
    (tmp_path / "labb.yaml").write_text(
        "css:\n"
        "  build:\n"
        "    input: static_src/input.css\n"
        "    output: static/css/output.css\n"
        "    minify: true\n"
        "  scan:\n"
        "    apps:\n"
        "      labb:\n"
        "      - templates/cotton/lbb/**/*.html\n"
        "    output: static_src/labb-classes.txt\n"
        "    templates:\n"
        "    - templates/**/*.html\n"
    )
    (tmp_path / "static_src" / "input.css").write_text(
        '@import "tailwindcss";\n@plugin "daisyui" {\n  themes: light, dark;\n}\n'
        '@source "../../labb-fullstack-reactivity/labb/templates";\n'
    )
    (tmp_path / "static_src" / "labb-classes.txt").write_text("old\n")
    (tmp_path / ".gitignore").write_text("__pycache__/\n")


def test_migrate_rewrites_yaml_input_and_cleans_up(tmp_path):
    _legacy_project(tmp_path)
    migrate_config(path=str(tmp_path), assume_yes=True)

    cfg = yaml.safe_load((tmp_path / "labb.yaml").read_text())
    # scan.apps → packages.components; scan.output dropped; templates kept
    assert cfg["css"]["packages"]["labb"] == {
        "components": ["templates/cotton/lbb/**/*.html"]
    }
    assert "apps" not in cfg["css"]["scan"]
    assert "output" not in cfg["css"]["scan"]
    assert cfg["css"]["scan"]["templates"] == ["templates/**/*.html"]

    input_css = (tmp_path / "static_src" / "input.css").read_text()
    assert '@import "../.labb/labb.css";' in input_css

    assert not (tmp_path / "static_src" / "labb-classes.txt").exists()
    assert ".labb/" in (tmp_path / ".gitignore").read_text()


def test_migrate_backs_up_every_file_it_overwrites(tmp_path):
    _legacy_project(tmp_path)
    original_yaml = (tmp_path / "labb.yaml").read_text()
    original_css = (tmp_path / "static_src" / "input.css").read_text()

    migrate_config(path=str(tmp_path), assume_yes=True)

    assert (tmp_path / "labb.yaml.bak").read_text() == original_yaml
    assert (tmp_path / "static_src" / "input.css.bak").read_text() == original_css


def test_backup_never_clobbers_an_existing_backup(tmp_path):
    target = tmp_path / "labb.yaml"
    target.write_text("first\n")
    assert _backup(target).name == "labb.yaml.bak"

    target.write_text("second\n")
    assert _backup(target).name == "labb.yaml.bak.1"

    assert (tmp_path / "labb.yaml.bak").read_text() == "first\n"
    assert (tmp_path / "labb.yaml.bak.1").read_text() == "second\n"


def test_migrate_noop_when_no_scan_apps(tmp_path):
    (tmp_path / "labb.yaml").write_text(
        "css:\n  build:\n    input: static_src/input.css\n  packages:\n    labb: [themes]\n"
    )
    migrate_config(path=str(tmp_path), assume_yes=True)
    cfg = yaml.safe_load((tmp_path / "labb.yaml").read_text())
    # untouched
    assert cfg["css"]["packages"] == {"labb": ["themes"]}
