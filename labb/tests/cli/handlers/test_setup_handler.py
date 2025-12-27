import subprocess
from unittest.mock import Mock, patch

import pytest
import typer

from labb.cli.handlers.setup_handler import (
    _install_daisyui,
    _install_tailwind_cli,
    setup_project,
    setup_project_with_config,
)


@patch("labb.cli.handlers.commons.load_config")
@patch("labb.cli.handlers.setup_handler.setup_project")
def test_setup_project_with_config_defaults(
    mock_setup_project, mock_load_config, mock_config, temp_dir
):
    mock_load_config.return_value = mock_config

    setup_project_with_config()

    mock_setup_project.assert_called_once_with(None)


@patch("labb.cli.handlers.commons.load_config")
@patch("labb.cli.handlers.setup_handler.setup_project")
def test_setup_project_with_config_overrides(
    mock_setup_project, mock_load_config, mock_config
):
    mock_load_config.return_value = mock_config

    setup_project_with_config(install_deps=True)

    mock_setup_project.assert_called_once_with(True)


@patch("labb.cli.handlers.setup_handler.console")
def test_setup_project_no_package_json(mock_console, temp_dir):
    """Test setup_project when package.json doesn't exist"""
    with patch("pathlib.Path.cwd", return_value=temp_dir):
        with pytest.raises(typer.Exit):
            setup_project(install_deps=True)

        mock_console.print.assert_called_with(
            "[red]❌ Error: package.json not found. Run 'labb init' first to initialize the project.[/red]"
        )


@patch("labb.cli.handlers.setup_handler.Confirm")
@patch("labb.cli.handlers.setup_handler.console")
def test_setup_project_with_package_json_install_deps(
    mock_console, mock_confirm, temp_dir
):
    """Test setup_project when package.json exists and user chooses to install deps"""
    package_json = temp_dir / "package.json"
    package_json.write_text('{"name": "test"}')
    mock_confirm.ask.return_value = True

    with patch("pathlib.Path.cwd", return_value=temp_dir):
        with patch(
            "labb.cli.handlers.setup_handler._install_tailwind_cli"
        ) as mock_tailwind:
            with patch(
                "labb.cli.handlers.setup_handler._install_daisyui"
            ) as mock_daisyui:
                setup_project(install_deps=None)

    mock_confirm.ask.assert_called_once_with(
        "Install Tailwind CSS CLI and DaisyUI?", default=True
    )
    mock_tailwind.assert_called_once_with(temp_dir)
    mock_daisyui.assert_called_once_with(temp_dir)


@patch("labb.cli.handlers.setup_handler.Confirm")
@patch("labb.cli.handlers.setup_handler.console")
def test_setup_project_with_package_json_skip_deps(
    mock_console, mock_confirm, temp_dir
):
    """Test setup_project when package.json exists and user chooses to skip deps"""
    package_json = temp_dir / "package.json"
    package_json.write_text('{"name": "test"}')
    mock_confirm.ask.return_value = False

    with patch("pathlib.Path.cwd", return_value=temp_dir):
        with patch(
            "labb.cli.handlers.setup_handler._install_tailwind_cli"
        ) as mock_tailwind:
            with patch(
                "labb.cli.handlers.setup_handler._install_daisyui"
            ) as mock_daisyui:
                setup_project(install_deps=None)

    mock_confirm.ask.assert_called_once_with(
        "Install Tailwind CSS CLI and DaisyUI?", default=True
    )
    mock_tailwind.assert_not_called()
    mock_daisyui.assert_not_called()
    mock_console.print.assert_any_call(
        "[yellow]Skipped Node.js dependencies installation.[/yellow]"
    )


@patch("labb.cli.handlers.setup_handler.console")
def test_setup_project_install_deps_explicit_true(temp_dir):
    """Test setup_project with explicit install_deps=True"""
    package_json = temp_dir / "package.json"
    package_json.write_text('{"name": "test"}')

    with patch("pathlib.Path.cwd", return_value=temp_dir):
        with patch(
            "labb.cli.handlers.setup_handler._install_tailwind_cli"
        ) as mock_tailwind:
            with patch(
                "labb.cli.handlers.setup_handler._install_daisyui"
            ) as mock_daisyui:
                setup_project(install_deps=True)

    mock_tailwind.assert_called_once_with(temp_dir)
    mock_daisyui.assert_called_once_with(temp_dir)


@patch("labb.cli.handlers.setup_handler.console")
def test_setup_project_install_deps_explicit_false(mock_console, temp_dir):
    """Test setup_project with explicit install_deps=False"""
    package_json = temp_dir / "package.json"
    package_json.write_text('{"name": "test"}')

    with patch("pathlib.Path.cwd", return_value=temp_dir):
        with patch(
            "labb.cli.handlers.setup_handler._install_tailwind_cli"
        ) as mock_tailwind:
            with patch(
                "labb.cli.handlers.setup_handler._install_daisyui"
            ) as mock_daisyui:
                setup_project(install_deps=False)

    mock_tailwind.assert_not_called()
    mock_daisyui.assert_not_called()
    mock_console.print.assert_any_call(
        "[yellow]Skipped Node.js dependencies installation.[/yellow]"
    )


@patch("labb.cli.handlers.setup_handler.subprocess.run")
@patch("labb.cli.handlers.setup_handler.console")
def test_install_tailwind_cli_success(mock_console, mock_run, temp_dir):
    """Test successful Tailwind CLI installation"""
    mock_run.return_value = Mock()

    _install_tailwind_cli(temp_dir)

    mock_run.assert_called_once_with(
        ["npm", "install", "-D", "tailwindcss", "@tailwindcss/cli"],
        cwd=temp_dir,
        check=True,
        capture_output=True,
        text=True,
    )
    mock_console.print.assert_called_with(
        "[green]✅ Installed tailwindcss & @tailwindcss/cli[/green]"
    )


@patch("labb.cli.handlers.setup_handler.subprocess.run")
@patch("labb.cli.handlers.setup_handler.console")
def test_install_tailwind_cli_error(mock_console, mock_run, temp_dir):
    """Test Tailwind CLI installation error"""
    mock_run.side_effect = subprocess.CalledProcessError(1, "npm")

    with pytest.raises(typer.Exit):
        _install_tailwind_cli(temp_dir)

    mock_console.print.assert_called_with(
        "[red]❌ Error installing Tailwind CSS CLI: Command 'npm' returned non-zero exit status 1.[/red]"
    )


@patch("labb.cli.handlers.setup_handler.subprocess.run")
@patch("labb.cli.handlers.setup_handler.console")
def test_install_daisyui_success(mock_console, mock_run, temp_dir):
    """Test successful DaisyUI installation"""
    mock_run.return_value = Mock()

    _install_daisyui(temp_dir)

    mock_run.assert_called_once_with(
        ["npm", "install", "-D", "daisyui@latest"],
        cwd=temp_dir,
        check=True,
        capture_output=True,
        text=True,
    )
    mock_console.print.assert_called_with("[green]✅ Installed daisyui@latest[/green]")


@patch("labb.cli.handlers.setup_handler.subprocess.run")
@patch("labb.cli.handlers.setup_handler.console")
def test_install_daisyui_error(mock_console, mock_run, temp_dir):
    """Test DaisyUI installation error"""
    mock_run.side_effect = subprocess.CalledProcessError(1, "npm")

    with pytest.raises(typer.Exit):
        _install_daisyui(temp_dir)

    mock_console.print.assert_called_with(
        "[red]❌ Error installing DaisyUI: Command 'npm' returned non-zero exit status 1.[/red]"
    )
