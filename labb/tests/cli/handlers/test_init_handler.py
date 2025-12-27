from unittest.mock import patch

import pytest
import typer

from labb.cli.handlers.commons import is_django_project as _is_django_project
from labb.cli.handlers.init_handler import _prompt_for_config, init_project


@patch("labb.cli.handlers.init_handler._create_project_structure")
@patch("labb.cli.handlers.init_handler.console")
@patch("labb.cli.handlers.init_handler.save_config")
@patch("labb.cli.handlers.commons.is_django_project")
def test_init_project_defaults(
    mock_is_django, mock_save_config, mock_console, mock_create_structure, temp_dir
):
    mock_is_django.return_value = True

    with patch("pathlib.Path.cwd", return_value=temp_dir):
        init_project(use_defaults=True)

    mock_save_config.assert_called_once()
    config_path_arg = mock_save_config.call_args[0][1]
    assert config_path_arg == temp_dir / "labb.yaml"
    mock_create_structure.assert_called_once()


@patch("labb.cli.handlers.init_handler.console")
@patch("labb.cli.handlers.init_handler.save_config")
@patch("labb.cli.handlers.commons.is_django_project")
@patch("labb.cli.handlers.init_handler._prompt_for_config")
@patch("labb.cli.handlers.commons.Confirm")
def test_init_project_not_django_continue(
    mock_confirm,
    mock_prompt_config,
    mock_is_django,
    mock_save_config,
    mock_console,
    temp_dir,
    mock_config,
):
    mock_is_django.return_value = False
    mock_confirm.ask.return_value = True  # Continue anyway
    mock_prompt_config.return_value = mock_config

    with patch("pathlib.Path.cwd", return_value=temp_dir):
        init_project(use_defaults=False)

    assert mock_confirm.ask.call_count == 1
    mock_prompt_config.assert_called_once()
    mock_save_config.assert_called_once()


@patch("labb.cli.handlers.init_handler.console")
@patch("labb.cli.handlers.commons.is_django_project")
@patch("labb.cli.handlers.commons.Confirm")
def test_init_project_not_django_cancel(
    mock_confirm, mock_is_django, mock_console, temp_dir
):
    mock_is_django.return_value = False
    mock_confirm.ask.return_value = False

    with patch("pathlib.Path.cwd", return_value=temp_dir):
        with pytest.raises(typer.Exit):
            init_project(use_defaults=False)

    mock_confirm.ask.assert_called_once()


@patch("labb.cli.handlers.init_handler.console")
@patch("labb.cli.handlers.init_handler.save_config")
@patch("labb.cli.handlers.commons.is_django_project")
@patch("labb.cli.handlers.init_handler._prompt_for_config")
@patch("labb.cli.handlers.commons.Confirm")
@patch("labb.cli.handlers.init_handler.Confirm")
def test_init_project_existing_config_overwrite(
    mock_confirm_init,
    mock_confirm_commons,
    mock_prompt_config,
    mock_is_django,
    mock_save_config,
    mock_console,
    temp_dir,
    mock_config,
):
    mock_is_django.return_value = True
    mock_confirm_commons.ask.return_value = True  # Continue anyway
    mock_confirm_init.ask.return_value = True  # Overwrite config
    mock_prompt_config.return_value = mock_config

    # Create existing config file
    existing_config = temp_dir / "labb.yaml"
    existing_config.write_text("existing: config")

    with patch("pathlib.Path.cwd", return_value=temp_dir):
        init_project(use_defaults=False)

    assert mock_confirm_init.ask.call_count == 1
    mock_prompt_config.assert_called_once()
    mock_save_config.assert_called_once()


@patch("labb.cli.handlers.init_handler.console")
@patch("labb.cli.handlers.commons.is_django_project")
@patch("labb.cli.handlers.commons.Confirm")
@patch("labb.cli.handlers.init_handler.Confirm")
def test_init_project_existing_config_cancel(
    mock_confirm_init, mock_confirm_commons, mock_is_django, mock_console, temp_dir
):
    mock_is_django.return_value = True
    mock_confirm_commons.ask.return_value = True  # Continue anyway
    mock_confirm_init.ask.return_value = False  # Don't overwrite

    # Create existing config file
    existing_config = temp_dir / "labb.yaml"
    existing_config.write_text("existing: config")

    with patch("pathlib.Path.cwd", return_value=temp_dir):
        with pytest.raises(typer.Exit):
            init_project(use_defaults=False)

    mock_confirm_init.ask.assert_called_once()


@patch("labb.cli.handlers.init_handler.console")
@patch("labb.cli.handlers.init_handler.save_config")
@patch("labb.cli.handlers.commons.is_django_project")
@patch("labb.cli.handlers.init_handler._prompt_for_config")
@patch("labb.cli.handlers.commons.Confirm")
@patch("labb.cli.handlers.init_handler.Confirm")
def test_init_project_with_prompts(
    mock_confirm_init,
    mock_confirm_commons,
    mock_prompt_config,
    mock_is_django,
    mock_save_config,
    mock_console,
    temp_dir,
    mock_config,
):
    mock_is_django.return_value = True
    mock_prompt_config.return_value = mock_config
    mock_confirm_commons.ask.return_value = True  # Continue anyway

    with patch("pathlib.Path.cwd", return_value=temp_dir):
        init_project(use_defaults=False)

    mock_prompt_config.assert_called_once()

    mock_save_config.assert_called_once()


def test_is_django_project_true(django_project_dir):
    result = _is_django_project(django_project_dir)
    assert result is True


def test_is_django_project_false(temp_dir):
    result = _is_django_project(temp_dir)
    assert result is False


@patch("labb.cli.handlers.init_handler.Prompt")
@patch("labb.cli.handlers.init_handler.console")
def test_prompt_for_config(mock_console, mock_prompt, tmp_path):
    custom_dir = tmp_path / "custom"
    custom_dir.mkdir()
    input_css = str(custom_dir / "input.css")
    output_css = str(custom_dir / "output.css")
    mock_prompt.ask.side_effect = [input_css, output_css]

    config = _prompt_for_config()

    assert config.input_file == input_css
    assert config.output_file == output_css
    assert mock_prompt.ask.call_count == 2


@patch("labb.cli.handlers.init_handler.console")
def test_init_project_existing_yml_config(mock_console, temp_dir):
    # Test that .yml extension is also detected
    existing_config = temp_dir / "labb.yml"
    existing_config.write_text("existing: config")

    with patch("pathlib.Path.cwd", return_value=temp_dir):
        with patch("labb.cli.handlers.commons.is_django_project", return_value=True):
            with patch("labb.cli.handlers.commons.Confirm") as mock_confirm_commons:
                with patch(
                    "labb.cli.handlers.init_handler.Confirm"
                ) as mock_confirm_init:
                    mock_confirm_commons.ask.return_value = True  # Continue anyway
                    mock_confirm_init.ask.return_value = False  # Don't overwrite
                    with pytest.raises(typer.Exit):
                        init_project(use_defaults=False)

    # Test that the function exits when user chooses not to overwrite
    mock_confirm_init.ask.assert_called_once()
