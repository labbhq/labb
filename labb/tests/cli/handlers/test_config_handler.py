import os
from pathlib import Path
from unittest.mock import patch

from labb.cli.handlers.config_handler import (
    _load_config_with_metadata,
    _show_config_metadata,
    _show_raw_config,
    edit_config,
    show_config,
    validate_config,
)
from labb.config import LabbConfig, LabbConfigNotFound


@patch("labb.cli.handlers.config_handler.console")
@patch("labb.cli.handlers.config_handler._load_config_with_metadata")
@patch("labb.cli.handlers.config_handler._show_raw_config")
def test_show_config_basic(mock_show_raw, mock_load_config, mock_console, mock_config):
    metadata = {"warnings": [], "from_env": False, "config_path": None}
    mock_load_config.return_value = (mock_config, metadata)

    show_config()

    mock_load_config.assert_called_once_with(None)
    mock_show_raw.assert_called_once_with(None, mock_config)
    mock_console.print.assert_called()


@patch("labb.cli.handlers.config_handler.console")
@patch("labb.cli.handlers.config_handler._load_config_with_metadata")
@patch("labb.cli.handlers.config_handler._show_config_metadata")
@patch("labb.cli.handlers.config_handler._show_raw_config")
def test_show_config_with_metadata_and_custom_path(
    mock_show_raw,
    mock_show_metadata,
    mock_load_config,
    mock_console,
    mock_config,
    tmp_path,
):
    metadata = {
        "warnings": ["test warning"],
        "from_env": True,
        "config_path": str(tmp_path / "custom" / "config.yaml"),
    }
    mock_load_config.return_value = (mock_config, metadata)

    show_config(show_metadata=True, config_path=str(tmp_path / "custom" / "path"))

    mock_load_config.assert_called_once_with(str(tmp_path / "custom" / "path"))
    mock_show_raw.assert_called_once_with(
        str(tmp_path / "custom" / "config.yaml"), mock_config
    )
    mock_show_metadata.assert_called_once_with(metadata)


@patch(
    "labb.cli.handlers.config_handler.os.environ",
    {"LABB_CONFIG_PATH": "/env/config.yaml"},
)
@patch("labb.cli.handlers.config_handler.find_config_file")
@patch("labb.cli.handlers.config_handler.load_config")
def test_load_config_with_metadata_from_env(
    mock_load_config, mock_find_config, mock_config
):
    mock_find_config.return_value = Path("/env/config.yaml")
    mock_load_config.return_value = mock_config

    with patch("pathlib.Path.exists", return_value=True):
        config, metadata = _load_config_with_metadata()

    assert metadata["from_env"] is True
    assert "LABB_CONFIG_PATH" in metadata["env_vars_used"]
    assert metadata["config_path"] == "/env/config.yaml"


@patch("labb.cli.handlers.config_handler.os.environ", {})
@patch("labb.cli.handlers.config_handler.find_config_file")
@patch("labb.cli.handlers.config_handler.load_config")
def test_load_config_with_metadata_no_file(
    mock_load_config, mock_find_config, mock_config
):
    mock_find_config.return_value = None
    mock_load_config.return_value = mock_config

    config, metadata = _load_config_with_metadata()

    assert "No configuration file found - using defaults" in metadata["warnings"]
    assert metadata["config_exists"] is False


@patch("labb.cli.handlers.config_handler.console")
def test_show_config_metadata(mock_console):
    metadata = {
        "config_path": "/path/to/config.yaml",
        "from_env": True,
        "env_vars_used": ["LABB_CONFIG_PATH"],
        "warnings": ["Test warning"],
    }

    _show_config_metadata(metadata)

    mock_console.print.assert_called()
    # Check that Panel was called with metadata info
    call_args = mock_console.print.call_args_list
    assert call_args[0][0][0].title == "Configuration Metadata"


@patch("labb.cli.handlers.config_handler.console")
@patch("labb.cli.handlers.config_handler._show_effective_config")
def test_show_raw_config_no_file(mock_show_effective, mock_console, mock_config):
    _show_raw_config(None, mock_config)

    mock_console.print.assert_called()
    mock_show_effective.assert_called_once_with(mock_config)
    call_args = str(mock_console.print.call_args_list)
    assert "No configuration file found" in call_args


@patch("labb.cli.handlers.config_handler.console")
@patch("labb.cli.handlers.config_handler._load_config_with_metadata")
def test_validate_config_all_good(
    mock_load_config, mock_console, mock_config, temp_dir
):
    # Create test files
    input_file = temp_dir / "input.css"
    output_dir = temp_dir / "output"
    classes_dir = temp_dir / "classes"

    input_file.write_text("/* test css */")
    output_dir.mkdir()
    classes_dir.mkdir()

    # Create a template file
    template_file = temp_dir / "template.html"
    template_file.write_text("<html></html>")

    # Mock config with test paths
    mock_config.input_file = str(input_file)
    mock_config.output_file = str(output_dir / "output.css")
    mock_config.classes_output = str(classes_dir / "classes.txt")
    mock_config.template_patterns = [str(temp_dir / "*.html")]

    metadata = {"warnings": []}
    mock_load_config.return_value = (mock_config, metadata)

    validate_config()

    # Check that success messages were printed
    call_args = str(mock_console.print.call_args_list)
    assert "Configuration looks good!" in call_args


@patch("labb.cli.handlers.config_handler.console")
@patch("labb.cli.handlers.config_handler.find_config_file")
def test_edit_config_no_file(mock_find_config, mock_console):
    mock_find_config.return_value = None

    edit_config()

    mock_console.print.assert_any_call(
        "[yellow]⚠️  No configuration file found[/yellow]"
    )


@patch("labb.cli.handlers.config_handler.console")
@patch("labb.cli.handlers.config_handler.find_config_file")
@patch("subprocess.run")
@patch("sys.platform", "linux")
def test_edit_config_linux(mock_run, mock_find_config, mock_console):
    config_path = Path("/path/to/config.yaml")
    mock_find_config.return_value = config_path

    # Mock successful editor call
    mock_run.return_value = None

    with patch("pathlib.Path.exists", return_value=True):
        edit_config()

    # Should try to open with 'code' (first in the list)
    mock_run.assert_called_with(["code", str(config_path)])


@patch("labb.cli.handlers.config_handler.console")
@patch("glob.glob")
def test_validate_config_template_scanning(mock_glob, mock_console, mock_config):
    # Mock template files found
    mock_glob.return_value = ["template1.html", "template2.html", "not_html.txt"]

    mock_config.input_file = "/nonexistent/input.css"  # Will fail other checks
    mock_config.output_file = "/nonexistent/output.css"
    mock_config.classes_output = "/nonexistent/classes.txt"
    mock_config.template_patterns = ["templates/*.html"]

    with patch(
        "labb.cli.handlers.config_handler._load_config_with_metadata"
    ) as mock_load:
        metadata = {"warnings": []}
        mock_load.return_value = (mock_config, metadata)

        validate_config()

    # Should find 2 HTML files
    call_args = str(mock_console.print.call_args_list)
    assert "Found 2 template files" in call_args


@patch("labb.cli.handlers.config_handler.find_config_file")
@patch("labb.cli.handlers.config_handler.load_config")
@patch("labb.cli.handlers.config_handler.console")
def test_load_config_with_metadata_config_path_not_exists(
    mock_console, mock_load_config, mock_find_config
):
    """Test _load_config_with_metadata when config path doesn't exist"""
    mock_find_config.return_value = Path("/nonexistent/config.yaml")
    mock_load_config.return_value = LabbConfig()

    config, metadata = _load_config_with_metadata()

    assert isinstance(config, LabbConfig)
    assert "No configuration file found" in metadata["warnings"][0]
    assert metadata["config_exists"] is False


@patch("labb.cli.handlers.config_handler.find_config_file")
@patch("labb.cli.handlers.config_handler.load_config")
@patch("labb.cli.handlers.config_handler.console")
def test_load_config_with_metadata_with_custom_path_not_exists(
    mock_console, mock_load_config, mock_find_config
):
    """Test _load_config_with_metadata with custom path that doesn't exist"""
    mock_load_config.side_effect = LabbConfigNotFound("Config not found")

    config, metadata = _load_config_with_metadata("/custom/path/config.yaml")

    assert isinstance(config, LabbConfig)
    # Check if the warning is in any of the warnings
    assert any(
        "Configuration file not found - using defaults" in warning
        for warning in metadata["warnings"]
    )


@patch("labb.cli.handlers.config_handler.console")
def test_show_config_metadata_with_all_fields(mock_console):
    """Test _show_config_metadata with all metadata fields populated"""
    metadata = {
        "config_path": "/path/to/config.yaml",
        "config_exists": True,
        "from_env": True,
        "env_vars_used": ["LABB_CONFIG_PATH", "LABB_DEBUG"],
        "warnings": ["Warning 1", "Warning 2"],
    }

    with patch.dict(
        os.environ, {"LABB_CONFIG_PATH": "/env/path", "LABB_DEBUG": "true"}
    ):
        _show_config_metadata(metadata)

    # Verify console.print was called with panel
    mock_console.print.assert_called_once()
    # Check that it's a Panel object
    call_args = mock_console.print.call_args[0][0]
    assert hasattr(call_args, "title")
    assert "Configuration Metadata" in str(call_args.title)


@patch("labb.cli.handlers.config_handler.console")
def test_show_config_metadata_with_minimal_fields(mock_console):
    """Test _show_config_metadata with minimal metadata fields"""
    metadata = {"warnings": ["No config found"]}

    _show_config_metadata(metadata)

    # Verify console.print was called with panel
    mock_console.print.assert_called_once()
    # Check that it's a Panel object
    call_args = mock_console.print.call_args[0][0]
    assert hasattr(call_args, "title")
    assert "Configuration Metadata" in str(call_args.title)


@patch("labb.cli.handlers.config_handler._show_effective_config")
@patch("labb.cli.handlers.config_handler.console")
def test_show_raw_config_file_exists(mock_console, mock_show_effective, temp_dir):
    """Test _show_raw_config when config file exists"""
    config_file = temp_dir / "config.yaml"
    config_file.write_text("css:\n  build:\n    input: input.css")

    config = LabbConfig()
    _show_raw_config(str(config_file), config)

    # Should show the actual file content
    mock_console.print.assert_called_once()
    # Check that it's a Panel object
    call_args = mock_console.print.call_args[0][0]
    assert hasattr(call_args, "title")
    assert "Configuration File" in str(call_args.title)
    mock_show_effective.assert_not_called()


@patch("labb.cli.handlers.config_handler._show_effective_config")
@patch("labb.cli.handlers.config_handler.console")
def test_show_raw_config_file_read_error(mock_console, mock_show_effective, temp_dir):
    """Test _show_raw_config when file exists but can't be read"""
    config_file = temp_dir / "config.yaml"
    config_file.write_text("css:\n  build:\n    input: input.css")

    config = LabbConfig()

    # Mock open to raise an exception
    with patch("builtins.open", side_effect=PermissionError("Access denied")):
        _show_raw_config(str(config_file), config)

    # Should show error and fall back to effective config
    error_calls = [
        call
        for call in mock_console.print.call_args_list
        if "Error reading" in str(call)
    ]
    assert len(error_calls) > 0
    mock_show_effective.assert_called_once_with(config)


@patch("labb.cli.handlers.config_handler._show_effective_config")
@patch("labb.cli.handlers.config_handler.console")
def test_show_raw_config_file_not_exists(mock_console, mock_show_effective):
    """Test _show_raw_config when config file doesn't exist"""
    config = LabbConfig()
    _show_raw_config("/nonexistent/config.yaml", config)

    # Should show warning and fall back to effective config
    warning_calls = [
        call
        for call in mock_console.print.call_args_list
        if "No configuration file found" in str(call)
    ]
    assert len(warning_calls) > 0
    mock_show_effective.assert_called_once_with(config)


@patch("labb.cli.handlers.config_handler.console")
def test_show_effective_config(mock_console):
    """Test _show_effective_config displays config as YAML"""
    from labb.cli.handlers.config_handler import _show_effective_config

    config = LabbConfig()
    config.input_file = "custom_input.css"
    config.output_file = "custom_output.css"
    config.minify = True

    _show_effective_config(config)

    # Should show effective configuration
    mock_console.print.assert_called_once()
    # Check that it's a Panel object
    call_args = mock_console.print.call_args[0][0]
    assert hasattr(call_args, "title")
    assert "Effective Configuration" in str(call_args.title)


@patch("labb.cli.handlers.config_handler._load_config_with_metadata")
@patch("labb.cli.handlers.config_handler._show_config_metadata")
@patch("labb.cli.handlers.config_handler.console")
def test_show_config_with_metadata_flag(
    mock_console, mock_show_metadata, mock_load_config
):
    """Test show_config with metadata flag"""
    mock_config = LabbConfig()
    mock_metadata = {"config_path": "/test/config.yaml"}
    mock_load_config.return_value = (mock_config, mock_metadata)

    show_config(show_metadata=True)

    mock_show_metadata.assert_called_once_with(mock_metadata)


@patch("labb.cli.handlers.config_handler._load_config_with_metadata")
@patch("labb.cli.handlers.config_handler._show_raw_config")
@patch("labb.cli.handlers.config_handler.console")
def test_show_config_with_custom_path(mock_console, mock_show_raw, mock_load_config):
    """Test show_config with custom config path"""
    mock_config = LabbConfig()
    mock_metadata = {"config_path": "/custom/config.yaml"}
    mock_load_config.return_value = (mock_config, mock_metadata)

    show_config(config_path="/custom/config.yaml")

    mock_show_raw.assert_called_once_with("/custom/config.yaml", mock_config)


@patch("labb.cli.handlers.config_handler.console")
def test_load_config_with_metadata_general_exception(mock_console):
    """Test _load_config_with_metadata with general exception"""
    with patch(
        "labb.cli.handlers.config_handler.load_config",
        side_effect=Exception("Test error"),
    ):
        config, metadata = _load_config_with_metadata()

    assert isinstance(config, LabbConfig)
    # Check if the warning is in any of the warnings
    assert any(
        "Error loading configuration: Test error" in warning
        for warning in metadata["warnings"]
    )


@patch("labb.cli.handlers.config_handler.console")
def test_show_effective_config_yaml_error(mock_console):
    """Test _show_effective_config with YAML dump error"""
    from labb.cli.handlers.config_handler import _show_effective_config

    config = LabbConfig()

    # Mock yaml.dump to raise an exception
    with patch(
        "labb.cli.handlers.config_handler.yaml.dump",
        side_effect=Exception("YAML error"),
    ):
        _show_effective_config(config)

    mock_console.print.assert_called_with(
        "[red]❌ Error generating configuration YAML: YAML error[/red]"
    )


@patch("labb.cli.handlers.config_handler.console")
def test_validate_config_with_issues(mock_console, temp_dir):
    """Test validate_config with configuration issues"""
    config = LabbConfig()
    config.input_file = "nonexistent/input.css"
    config.output_file = "nonexistent/output.css"
    config.classes_output = "nonexistent/classes.txt"
    config.template_patterns = ["nonexistent/**/*.html"]

    with patch(
        "labb.cli.handlers.config_handler._load_config_with_metadata"
    ) as mock_load:
        mock_load.return_value = (config, {})

        validate_config()

    # Should show issues
    issue_calls = [
        call
        for call in mock_console.print.call_args_list
        if "Issues found" in str(call)
    ]
    assert len(issue_calls) > 0

    # Should show suggested actions
    action_calls = [
        call
        for call in mock_console.print.call_args_list
        if "Suggested actions" in str(call)
    ]
    assert len(action_calls) > 0


@patch("labb.cli.handlers.config_handler.console")
def test_validate_config_no_issues(mock_console, temp_dir):
    """Test validate_config with no issues"""
    # Create test files
    input_file = temp_dir / "input.css"
    input_file.write_text("test")

    output_dir = temp_dir / "static" / "css"
    output_dir.mkdir(parents=True)

    classes_dir = temp_dir / "static_src"
    classes_dir.mkdir(parents=True)

    template_file = temp_dir / "templates" / "test.html"
    template_file.parent.mkdir(parents=True)
    template_file.write_text("<html></html>")

    config = LabbConfig()
    config.input_file = str(input_file)
    config.output_file = str(output_dir / "output.css")
    config.classes_output = str(classes_dir / "classes.txt")
    config.template_patterns = [str(temp_dir / "templates/**/*.html")]

    with patch(
        "labb.cli.handlers.config_handler._load_config_with_metadata"
    ) as mock_load:
        mock_load.return_value = (config, {})

        validate_config()

    # Should show success message
    success_calls = [
        call
        for call in mock_console.print.call_args_list
        if "Configuration looks good" in str(call)
    ]
    assert len(success_calls) > 0


@patch("labb.cli.handlers.config_handler.console")
@patch("subprocess.run")
def test_edit_config_macos(mock_run, mock_console, temp_dir):
    """Test edit_config on macOS"""
    config_file = temp_dir / "config.yaml"
    config_file.write_text("test")

    with patch(
        "labb.cli.handlers.config_handler.find_config_file", return_value=config_file
    ):
        with patch("sys.platform", "darwin"):
            edit_config()

    mock_run.assert_called_with(["open", str(config_file)])
    mock_console.print.assert_called_with(
        f"[green]✅ Opened {config_file} in editor[/green]"
    )


@patch("labb.cli.handlers.config_handler.console")
@patch("subprocess.run")
def test_edit_config_windows(mock_run, mock_console, temp_dir):
    """Test edit_config on Windows"""
    config_file = temp_dir / "config.yaml"
    config_file.write_text("test")

    with patch(
        "labb.cli.handlers.config_handler.find_config_file", return_value=config_file
    ):
        with patch("sys.platform", "win32"):
            edit_config()

    mock_run.assert_called_with(["notepad", str(config_file)])
    mock_console.print.assert_called_with(
        f"[green]✅ Opened {config_file} in editor[/green]"
    )


@patch("labb.cli.handlers.config_handler.console")
@patch("subprocess.run")
def test_edit_config_linux_success(mock_run, mock_console, temp_dir):
    """Test edit_config on Linux with successful editor"""
    config_file = temp_dir / "config.yaml"
    config_file.write_text("test")

    with patch(
        "labb.cli.handlers.config_handler.find_config_file", return_value=config_file
    ):
        with patch("sys.platform", "linux"):
            edit_config()

    # Should try code first
    mock_run.assert_called_with(["code", str(config_file)])
    mock_console.print.assert_called_with(
        f"[green]✅ Opened {config_file} in editor[/green]"
    )


@patch("labb.cli.handlers.config_handler.console")
@patch("subprocess.run")
def test_edit_config_linux_fallback(mock_run, mock_console, temp_dir):
    """Test edit_config on Linux with fallback to nano"""
    config_file = temp_dir / "config.yaml"
    config_file.write_text("test")

    # Mock code to fail, nano to succeed
    def run_side_effect(cmd, *args, **kwargs):
        if cmd[0] == "code":
            raise FileNotFoundError("code not found")
        return None

    mock_run.side_effect = run_side_effect

    with patch(
        "labb.cli.handlers.config_handler.find_config_file", return_value=config_file
    ):
        with patch("sys.platform", "linux"):
            edit_config()

    # Should try code first, then nano
    calls = mock_run.call_args_list
    assert calls[0][0][0] == ["code", str(config_file)]
    assert calls[1][0][0] == ["nano", str(config_file)]
    mock_console.print.assert_called_with(
        f"[green]✅ Opened {config_file} in editor[/green]"
    )


@patch("labb.cli.handlers.config_handler.console")
@patch("subprocess.run")
def test_edit_config_linux_no_editors(mock_run, mock_console, temp_dir):
    """Test edit_config on Linux with no editors available"""
    config_file = temp_dir / "config.yaml"
    config_file.write_text("test")

    # Mock all editors to fail
    mock_run.side_effect = FileNotFoundError("editor not found")

    with patch(
        "labb.cli.handlers.config_handler.find_config_file", return_value=config_file
    ):
        with patch("sys.platform", "linux"):
            edit_config()

    # Should show manual edit message
    manual_calls = [
        call
        for call in mock_console.print.call_args_list
        if "Please manually edit" in str(call)
    ]
    assert len(manual_calls) > 0


@patch("labb.cli.handlers.config_handler.console")
@patch("subprocess.run")
def test_edit_config_with_custom_path(mock_run, mock_console, temp_dir):
    """Test edit_config with custom config path"""
    config_file = temp_dir / "custom_config.yaml"
    config_file.write_text("test")

    with patch("sys.platform", "darwin"):
        edit_config(str(config_file))

    mock_run.assert_called_with(["open", str(config_file)])
    mock_console.print.assert_called_with(
        f"[green]✅ Opened {config_file} in editor[/green]"
    )


@patch("labb.cli.handlers.config_handler.console")
@patch("subprocess.run")
def test_edit_config_error(mock_run, mock_console, temp_dir):
    """Test edit_config with subprocess error"""
    config_file = temp_dir / "config.yaml"
    config_file.write_text("test")

    mock_run.side_effect = Exception("Editor error")

    with patch(
        "labb.cli.handlers.config_handler.find_config_file", return_value=config_file
    ):
        with patch("sys.platform", "darwin"):
            edit_config()

    error_calls = [
        call
        for call in mock_console.print.call_args_list
        if "Error opening editor" in str(call)
    ]
    assert len(error_calls) > 0

    manual_calls = [
        call
        for call in mock_console.print.call_args_list
        if "Please manually edit" in str(call)
    ]
    assert len(manual_calls) > 0
