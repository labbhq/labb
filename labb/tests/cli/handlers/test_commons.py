from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import typer

from labb.cli.handlers.commons import (
    confirm_load_config,
    confirm_working_in_django_project,
    is_django_project,
)
from labb.config import LabbConfig, LabbConfigNotFound


class TestIsDjangoProject:
    """Test the is_django_project function"""

    def test_is_django_project_true(self, temp_dir):
        """Test when manage.py exists"""
        manage_py = temp_dir / "manage.py"
        manage_py.write_text("# Django manage.py")

        result = is_django_project(temp_dir)
        assert result is True

    def test_is_django_project_false(self, temp_dir):
        """Test when manage.py doesn't exist"""
        result = is_django_project(temp_dir)
        assert result is False

    def test_is_django_project_with_subdirectory(self, temp_dir):
        """Test with subdirectory that has manage.py"""
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        manage_py = subdir / "manage.py"
        manage_py.write_text("# Django manage.py")

        result = is_django_project(subdir)
        assert result is True

        # Parent directory should not be Django project
        result = is_django_project(temp_dir)
        assert result is False


class TestConfirmWorkingInDjangoProject:
    """Test the confirm_working_in_django_project function"""

    @patch("labb.cli.handlers.commons.is_django_project", return_value=True)
    def test_confirm_working_in_django_project_django_project(
        self, mock_is_django, mock_console
    ):
        """Test when working in a Django project"""
        path = Path("/test/django/project")

        confirm_working_in_django_project(path, mock_console)

        mock_is_django.assert_called_once_with(path)
        mock_console.print.assert_not_called()

    @patch("labb.cli.handlers.commons.is_django_project", return_value=False)
    @patch("labb.cli.handlers.commons.Confirm")
    def test_confirm_working_in_django_project_not_django_continue(
        self, mock_confirm, mock_is_django, mock_console
    ):
        """Test when not in Django project and user chooses to continue"""
        mock_confirm.ask.return_value = True
        path = Path("/test/non/django/project")

        confirm_working_in_django_project(path, mock_console)

        mock_is_django.assert_called_once_with(path)
        mock_console.print.assert_called_once_with(
            "[yellow]⚠️  Appears not to be a Django project directory (manage.py not found).[/yellow]"
        )
        mock_confirm.ask.assert_called_once_with("Continue anyway?", default=True)

    @patch("labb.cli.handlers.commons.is_django_project", return_value=False)
    @patch("labb.cli.handlers.commons.Confirm")
    def test_confirm_working_in_django_project_not_django_cancel(
        self, mock_confirm, mock_is_django, mock_console
    ):
        """Test when not in Django project and user chooses to cancel"""
        mock_confirm.ask.return_value = False
        path = Path("/test/non/django/project")

        with pytest.raises(typer.Exit) as exc_info:
            confirm_working_in_django_project(path, mock_console)

        assert exc_info.value.exit_code == 0
        mock_is_django.assert_called_once_with(path)
        # Check that both warning and cancellation messages were printed
        print_calls = mock_console.print.call_args_list
        assert len(print_calls) >= 2
        warning_call = print_calls[0]
        cancellation_call = print_calls[1]
        assert "manage.py not found" in str(warning_call)
        assert "cancelled" in str(cancellation_call).lower()


class TestConfirmLoadConfig:
    """Test the confirm_load_config function"""

    @patch("labb.cli.handlers.commons.load_config")
    def test_confirm_load_config_success(self, mock_load_config, mock_console):
        """Test successful config loading"""
        mock_config = Mock(spec=LabbConfig)
        mock_load_config.return_value = mock_config

        result = confirm_load_config(mock_console)

        assert result == mock_config
        mock_load_config.assert_called_once()
        mock_console.print.assert_called_once_with(
            "[dim]Using configuration from labb.yaml[/dim]"
        )

    @patch("labb.cli.handlers.commons.load_config")
    @patch("labb.cli.handlers.commons.Confirm")
    def test_confirm_load_config_not_found_use_defaults(
        self, mock_confirm, mock_load_config, mock_console
    ):
        """Test when config not found and user chooses to use defaults"""
        mock_load_config.side_effect = LabbConfigNotFound("Config not found")
        mock_confirm.ask.return_value = True

        result = confirm_load_config(mock_console)

        assert isinstance(result, LabbConfig)
        mock_load_config.assert_called_once()
        mock_console.print.assert_called_once_with(
            "[yellow]Warning: Could not resolve labb.yaml config file: Config not found[/yellow]"
        )
        mock_confirm.ask.assert_called_once_with(
            "Use default labb.yaml config values?", default=True
        )

    @patch("labb.cli.handlers.commons.load_config")
    @patch("labb.cli.handlers.commons.Confirm")
    def test_confirm_load_config_not_found_dont_use_defaults(
        self, mock_confirm, mock_load_config, mock_console
    ):
        """Test when config not found and user chooses not to use defaults"""
        mock_load_config.side_effect = LabbConfigNotFound("Config not found")
        mock_confirm.ask.return_value = False

        with pytest.raises(typer.Exit) as exc_info:
            confirm_load_config(mock_console)

        assert exc_info.value.exit_code == 0
        mock_load_config.assert_called_once()
        mock_console.print.assert_called_once_with(
            "[yellow]Warning: Could not resolve labb.yaml config file: Config not found[/yellow]"
        )
        mock_confirm.ask.assert_called_once_with(
            "Use default labb.yaml config values?", default=True
        )

    @patch("labb.cli.handlers.commons.load_config")
    @patch("labb.cli.handlers.commons.Confirm")
    def test_confirm_load_config_generic_exception_use_defaults(
        self, mock_confirm, mock_load_config, mock_console
    ):
        """Test when generic exception occurs and user chooses to use defaults"""
        mock_load_config.side_effect = Exception("Generic error")
        mock_confirm.ask.return_value = True

        result = confirm_load_config(mock_console)

        assert isinstance(result, LabbConfig)
        mock_load_config.assert_called_once()
        mock_console.print.assert_called_once_with(
            "[yellow]Warning: Could not load configuration: Generic error[/yellow]"
        )
        mock_confirm.ask.assert_called_once_with(
            "Use default labb.yaml config values?", default=True
        )

    @patch("labb.cli.handlers.commons.load_config")
    @patch("labb.cli.handlers.commons.Confirm")
    def test_confirm_load_config_generic_exception_dont_use_defaults(
        self, mock_confirm, mock_load_config, mock_console
    ):
        """Test when generic exception occurs and user chooses not to use defaults"""
        mock_load_config.side_effect = Exception("Generic error")
        mock_confirm.ask.return_value = False

        with pytest.raises(typer.Exit) as exc_info:
            confirm_load_config(mock_console)

        assert exc_info.value.exit_code == 0
        mock_load_config.assert_called_once()
        mock_console.print.assert_called_once_with(
            "[yellow]Warning: Could not load configuration: Generic error[/yellow]"
        )
        mock_confirm.ask.assert_called_once_with(
            "Use default labb.yaml config values?", default=True
        )
