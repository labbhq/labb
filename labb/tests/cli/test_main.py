from unittest.mock import patch

from typer.testing import CliRunner

from labb.cli.main import app

runner = CliRunner()


@patch("labb.cli.main.init_project")
def test_init_command_defaults(mock_init_project):
    result = runner.invoke(app, ["init"])

    assert result.exit_code == 0
    mock_init_project.assert_called_once_with(use_defaults=False, force=False)


@patch("labb.cli.main.init_project")
def test_init_command_with_defaults(mock_init_project):
    result = runner.invoke(app, ["init", "--defaults"])

    assert result.exit_code == 0
    mock_init_project.assert_called_once_with(use_defaults=True, force=False)


@patch("labb.cli.main.setup_project_with_config")
def test_setup_command_defaults(mock_setup):
    result = runner.invoke(app, ["setup"])

    assert result.exit_code == 0
    mock_setup.assert_called_once_with(None)


@patch("labb.cli.main.setup_project_with_config")
def test_setup_command_with_options(mock_setup):
    result = runner.invoke(
        app,
        [
            "setup",
            "--install-deps",
        ],
    )

    assert result.exit_code == 0
    mock_setup.assert_called_once_with(True)


@patch("labb.cli.main.build_css")
def test_build_command_defaults(mock_build):
    result = runner.invoke(app, ["build"])

    assert result.exit_code == 0
    mock_build.assert_called_once_with(
        watch=False, scan=False, minify=None, input_file=None, output_file=None
    )


@patch("labb.cli.main.build_css")
def test_build_command_watch(mock_build):
    result = runner.invoke(app, ["build", "--watch"])

    assert result.exit_code == 0
    mock_build.assert_called_once_with(
        watch=True, scan=False, minify=None, input_file=None, output_file=None
    )


@patch("labb.cli.main.build_css")
def test_build_command_scan(mock_build):
    result = runner.invoke(app, ["build", "--scan"])

    assert result.exit_code == 0
    mock_build.assert_called_once_with(
        watch=False, scan=True, minify=None, input_file=None, output_file=None
    )


@patch("labb.cli.main.build_css")
def test_build_command_all_options(mock_build, tmp_path):
    custom_dir = tmp_path / "custom"
    custom_dir.mkdir()
    input_css = str(custom_dir / "input.css")
    output_css = str(custom_dir / "output.css")
    result = runner.invoke(
        app,
        [
            "build",
            "--watch",
            "--scan",
            "--minify",
            "--input",
            input_css,
            "--output",
            output_css,
        ],
    )

    assert result.exit_code == 0
    mock_build.assert_called_once_with(
        watch=True,
        scan=True,
        minify=True,
        input_file=input_css,
        output_file=output_css,
    )


@patch("labb.cli.main.build_css")
def test_build_command_no_minify(mock_build):
    result = runner.invoke(app, ["build", "--no-minify"])

    assert result.exit_code == 0
    mock_build.assert_called_once_with(
        watch=False, scan=False, minify=False, input_file=None, output_file=None
    )


@patch("labb.cli.main.build_css")
def test_dev_command_defaults(mock_build):
    result = runner.invoke(app, ["dev"])

    assert result.exit_code == 0
    mock_build.assert_called_once_with(
        watch=True, scan=True, minify=False, input_file=None, output_file=None
    )


@patch("labb.cli.main.build_css")
def test_dev_command_with_options(mock_build):
    result = runner.invoke(
        app,
        ["dev", "--minify", "--input", "dev/input.css", "--output", "dev/output.css"],
    )

    assert result.exit_code == 0
    mock_build.assert_called_once_with(
        watch=True,
        scan=True,
        minify=True,
        input_file="dev/input.css",
        output_file="dev/output.css",
    )


@patch("labb.cli.main.inspect_components")
def test_components_command_defaults(mock_inspect):
    result = runner.invoke(app, ["components", "inspect"])

    assert result.exit_code == 0
    mock_inspect.assert_called_once_with(None, False, False)


@patch("labb.cli.main.inspect_components")
def test_components_command_list_all(mock_inspect):
    result = runner.invoke(app, ["components", "inspect", "--list"])

    assert result.exit_code == 0
    mock_inspect.assert_called_once_with(None, True, False)


@patch("labb.cli.main.inspect_components")
def test_components_command_specific_component(mock_inspect):
    result = runner.invoke(app, ["components", "inspect", "button"])

    assert result.exit_code == 0
    mock_inspect.assert_called_once_with("button", False, False)


@patch("labb.cli.main.inspect_components")
def test_components_command_verbose(mock_inspect):
    result = runner.invoke(app, ["components", "inspect", "button", "--verbose"])

    assert result.exit_code == 0
    mock_inspect.assert_called_once_with("button", False, True)


@patch("labb.cli.main.inspect_components")
def test_components_command_list_verbose(mock_inspect):
    result = runner.invoke(app, ["components", "inspect", "--list", "--verbose"])

    assert result.exit_code == 0
    mock_inspect.assert_called_once_with(None, True, True)


@patch("labb.cli.main.scan_templates")
def test_scan_command_defaults(mock_scan):
    result = runner.invoke(app, ["scan"])

    assert result.exit_code == 0
    mock_scan.assert_called_once_with(False, None, None, False)


@patch("labb.cli.main.scan_templates")
def test_scan_command_watch(mock_scan):
    result = runner.invoke(app, ["scan", "--watch"])

    assert result.exit_code == 0
    mock_scan.assert_called_once_with(True, None, None, False)


@patch("labb.cli.main.scan_templates")
def test_scan_command_with_options(mock_scan):
    result = runner.invoke(
        app,
        [
            "scan",
            "--watch",
            "--output",
            "custom/classes.txt",
            "--patterns",
            "custom/**/*.html,other/**/*.html",
            "--verbose",
        ],
    )

    assert result.exit_code == 0
    mock_scan.assert_called_once_with(
        True, "custom/classes.txt", "custom/**/*.html,other/**/*.html", True
    )


def test_app_help():
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "labb Django UI Components CLI" in result.output
    assert "init" in result.output
    assert "setup" in result.output
    assert "build" in result.output
    assert "dev" in result.output
    assert "components" in result.output
    assert "scan" in result.output


def test_app_no_args_shows_help():
    result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert "labb Django UI Components CLI" in result.output


def test_command_help_messages():
    commands = ["init", "setup", "build", "dev", "components", "scan"]

    for command in commands:
        result = runner.invoke(app, [command, "--help"])
        assert result.exit_code == 0
        assert command in result.output.lower() or "usage" in result.output.lower()


@patch("labb.cli.main.scan_templates")
def test_scan_command_short_options(mock_scan):
    result = runner.invoke(app, ["scan", "-w", "-o", "output.txt", "-v"])

    assert result.exit_code == 0
    mock_scan.assert_called_once_with(True, "output.txt", None, True)


@patch("labb.cli.main.build_css")
def test_build_command_short_options(mock_build, tmp_path):
    custom_dir = tmp_path / "custom"
    custom_dir.mkdir()
    input_css = str(custom_dir / "input.css")
    output_css = str(custom_dir / "output.css")
    result = runner.invoke(
        app,
        [
            "build",
            "-w",
            "-s",
            # "-m",  # removed for debugging
            "-i",
            input_css,
            "-o",
            output_css,
        ],
    )
    assert result.exit_code == 0
    mock_build.assert_called_once_with(
        watch=True,
        scan=True,
        minify=None,
        input_file=input_css,
        output_file=output_css,
    )


# Now that imports are at module level, we can add tests for config command branches
@patch("labb.cli.main.show_config")
def test_config_command_defaults(mock_show_config):
    result = runner.invoke(app, ["config"])

    assert result.exit_code == 0
    mock_show_config.assert_called_once_with(False, None)


@patch("labb.cli.main.show_config")
def test_config_command_with_metadata(mock_show_config):
    result = runner.invoke(app, ["config", "--metadata"])

    assert result.exit_code == 0
    mock_show_config.assert_called_once_with(True, None)


@patch("labb.cli.main.show_config")
def test_config_command_with_config_path(mock_show_config, tmp_path):
    custom_dir = tmp_path / "custom"
    custom_dir.mkdir()
    config_path = str(custom_dir / "labb.yaml")
    result = runner.invoke(app, ["config", "--config", config_path])

    assert result.exit_code == 0
    mock_show_config.assert_called_once_with(False, config_path)


@patch("labb.cli.main.validate_config")
def test_config_command_validate(mock_validate_config):
    result = runner.invoke(app, ["config", "--validate"])

    assert result.exit_code == 0
    mock_validate_config.assert_called_once_with(None)


@patch("labb.cli.main.validate_config")
def test_config_command_validate_with_path(mock_validate_config, tmp_path):
    custom_dir = tmp_path / "custom"
    custom_dir.mkdir()
    config_path = str(custom_dir / "labb.yaml")
    result = runner.invoke(app, ["config", "--validate", "--config", config_path])

    assert result.exit_code == 0
    mock_validate_config.assert_called_once_with(config_path)


@patch("labb.cli.main.edit_config")
def test_config_command_edit(mock_edit_config):
    result = runner.invoke(app, ["config", "--edit"])

    assert result.exit_code == 0
    mock_edit_config.assert_called_once_with(None)


@patch("labb.cli.main.edit_config")
def test_config_command_edit_with_path(mock_edit_config, tmp_path):
    custom_dir = tmp_path / "custom"
    custom_dir.mkdir()
    config_path = str(custom_dir / "labb.yaml")
    result = runner.invoke(app, ["config", "--edit", "--config", config_path])

    assert result.exit_code == 0
    mock_edit_config.assert_called_once_with(config_path)


# Test error handling in CLI commands
@patch("labb.cli.main.init_project")
def test_init_command_error_handling(mock_init_project):
    mock_init_project.side_effect = Exception("Test error")

    result = runner.invoke(app, ["init"])

    assert result.exit_code != 0
    mock_init_project.assert_called_once_with(use_defaults=False, force=False)


@patch("labb.cli.main.setup_project_with_config")
def test_setup_command_error_handling(mock_setup):
    mock_setup.side_effect = Exception("Test error")

    result = runner.invoke(app, ["setup"])

    assert result.exit_code != 0
    mock_setup.assert_called_once_with(None)


@patch("labb.cli.main.build_css")
def test_build_command_error_handling(mock_build):
    mock_build.side_effect = Exception("Test error")

    result = runner.invoke(app, ["build"])

    assert result.exit_code != 0
    mock_build.assert_called_once_with(
        watch=False, scan=False, minify=None, input_file=None, output_file=None
    )


@patch("labb.cli.main.inspect_components")
def test_components_command_error_handling(mock_inspect):
    mock_inspect.side_effect = Exception("Test error")

    result = runner.invoke(app, ["components", "inspect"])

    assert result.exit_code != 0
    mock_inspect.assert_called_once_with(None, False, False)


@patch("labb.cli.main.scan_templates")
def test_scan_command_error_handling(mock_scan):
    mock_scan.side_effect = Exception("Test error")

    result = runner.invoke(app, ["scan"])

    assert result.exit_code != 0
    mock_scan.assert_called_once_with(False, None, None, False)


@patch("labb.cli.main.show_config")
def test_config_command_error_handling(mock_show_config):
    mock_show_config.side_effect = Exception("Test error")

    result = runner.invoke(app, ["config"])

    assert result.exit_code != 0
    mock_show_config.assert_called_once_with(False, None)
