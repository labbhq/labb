import subprocess
from unittest.mock import Mock, patch

import pytest

from labb.cli.handlers.build_handler import (
    _check_dependencies,
    _run_build_process,
    _run_build_watcher,
    _run_concurrent_build_and_scan,
    _run_scan_watcher,
    build_css,
)

# Tests for dependency checking


@patch("labb.cli.handlers.build_handler.subprocess.run")
@patch("pathlib.Path.exists")
@patch("labb.cli.handlers.build_handler.console")
def test_check_dependencies_all_present(mock_console, mock_path_exists, mock_run):
    """Test dependency check when all dependencies are present"""
    mock_run.return_value = Mock(returncode=0)  # npx available
    mock_path_exists.return_value = True  # All paths exist

    # Should not raise any exception
    _check_dependencies()

    # Should check npx
    mock_run.assert_called_once()


@patch("labb.cli.handlers.build_handler.subprocess.run")
@patch("labb.cli.handlers.build_handler.console")
def test_check_dependencies_npx_not_available(mock_console, mock_run):
    """Test dependency check when npx is not available"""
    mock_run.side_effect = FileNotFoundError()

    with pytest.raises(SystemExit):
        _check_dependencies()

    # Should print error about npx
    print_calls = mock_console.print.call_args_list
    error_text = str(print_calls)
    assert "npx" in error_text.lower()


@patch("labb.cli.handlers.build_handler.subprocess.run")
@patch("labb.cli.handlers.build_handler.console")
def test_check_dependencies_package_json_missing(mock_console, mock_run, temp_dir):
    """Test dependency check when package.json is missing"""
    mock_run.return_value = Mock(returncode=0)  # npx available

    with patch("labb.cli.handlers.build_handler.Path.cwd", return_value=temp_dir):
        with pytest.raises(SystemExit):
            _check_dependencies()

    # Should print error about package.json
    print_calls = mock_console.print.call_args_list
    error_text = str(print_calls)
    assert "package.json" in error_text.lower()
    assert "labb init" in error_text


@patch("labb.cli.handlers.build_handler.subprocess.run")
@patch("labb.cli.handlers.build_handler.console")
def test_check_dependencies_node_modules_missing(mock_console, mock_run, temp_dir):
    """Test dependency check when node_modules is missing"""
    mock_run.return_value = Mock(returncode=0)  # npx available

    # Create package.json but not node_modules
    (temp_dir / "package.json").write_text("{}")

    with patch("labb.cli.handlers.build_handler.Path.cwd", return_value=temp_dir):
        with pytest.raises(SystemExit):
            _check_dependencies()

    # Should print error about node_modules
    print_calls = mock_console.print.call_args_list
    error_text = str(print_calls)
    assert "node_modules" in error_text.lower()
    assert "labb setup" in error_text


@patch("labb.cli.handlers.build_handler.subprocess.run")
@patch("labb.cli.handlers.build_handler.console")
def test_check_dependencies_tailwind_not_installed(mock_console, mock_run, temp_dir):
    """Test dependency check when Tailwind CSS is not installed"""
    mock_run.return_value = Mock(returncode=0)  # npx available

    # Create package.json and node_modules but not Tailwind
    (temp_dir / "package.json").write_text("{}")
    (temp_dir / "node_modules").mkdir()

    with patch("labb.cli.handlers.build_handler.Path.cwd", return_value=temp_dir):
        with pytest.raises(SystemExit):
            _check_dependencies()

    # Should print error about Tailwind CSS
    print_calls = mock_console.print.call_args_list
    error_text = str(print_calls)
    assert "tailwind" in error_text.lower()
    assert "labb setup" in error_text


# Tests for build_css


@patch("labb.cli.handlers.build_handler._check_dependencies")
@patch("pathlib.Path.exists")
@patch("labb.cli.handlers.commons.load_config")
@patch("labb.cli.handlers.build_handler._run_build_process")
@patch("labb.cli.handlers.build_handler.console")
def test_build_css_simple(
    mock_console,
    mock_run_build,
    mock_load_config,
    mock_path_exists,
    mock_check_deps,
    mock_config,
):
    mock_load_config.return_value = mock_config
    mock_path_exists.return_value = True

    build_css()

    mock_check_deps.assert_called_once()
    mock_run_build.assert_called_once_with(
        mock_config.input_file, mock_config.output_file, mock_config.minify, watch=False
    )


@patch("labb.cli.handlers.build_handler._check_dependencies")
@patch("pathlib.Path.exists")
@patch("labb.cli.handlers.commons.load_config")
@patch("labb.cli.handlers.build_handler._run_concurrent_build_and_scan")
@patch("labb.cli.handlers.build_handler.console")
def test_build_css_watch_only(
    mock_console,
    mock_run_concurrent,
    mock_load_config,
    mock_path_exists,
    mock_check_deps,
    mock_config,
):
    mock_load_config.return_value = mock_config
    mock_path_exists.return_value = True

    build_css(watch=True, scan=False)

    mock_check_deps.assert_called_once()
    mock_run_concurrent.assert_called_once()


@patch("labb.cli.handlers.build_handler._check_dependencies")
@patch("pathlib.Path.exists")
@patch("labb.cli.handlers.commons.load_config")
@patch("labb.cli.handlers.build_handler._run_concurrent_build_and_scan")
@patch("labb.cli.handlers.build_handler.console")
def test_build_css_watch_and_scan(
    mock_console,
    mock_run_concurrent,
    mock_load_config,
    mock_path_exists,
    mock_check_deps,
    mock_config,
):
    mock_load_config.return_value = mock_config
    mock_path_exists.return_value = True

    build_css(watch=True, scan=True)

    mock_check_deps.assert_called_once()
    mock_run_concurrent.assert_called_once()


@patch("labb.cli.handlers.build_handler._check_dependencies")
@patch("pathlib.Path.exists")
@patch("labb.cli.handlers.commons.load_config")
@patch("labb.cli.handlers.build_handler._run_build_process")
@patch("labb.cli.handlers.build_handler.console")
def test_build_css_with_overrides(
    mock_console,
    mock_run_build,
    mock_load_config,
    mock_path_exists,
    mock_check_deps,
    mock_config,
    tmp_path,
):
    mock_load_config.return_value = mock_config
    mock_path_exists.return_value = True

    input_css = str(tmp_path / "custom" / "input.css")
    output_css = str(tmp_path / "custom" / "output.css")
    (tmp_path / "custom").mkdir(exist_ok=True)

    build_css(minify=False, input_file=input_css, output_file=output_css)

    mock_check_deps.assert_called_once()
    mock_run_build.assert_called_once_with(input_css, output_css, False, watch=False)


@patch("labb.cli.handlers.commons.load_config")
@patch("labb.cli.handlers.build_handler.console")
def test_build_css_input_file_not_found(
    mock_console, mock_load_config, mock_config, temp_dir
):
    mock_config.input_file = str(temp_dir / "nonexistent.css")
    mock_load_config.return_value = mock_config

    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(SystemExit):
            build_css()


@patch("labb.cli.handlers.build_handler.subprocess.run")
@patch("labb.cli.handlers.build_handler.console")
def test_run_build_process_success(mock_console, mock_run, temp_dir):
    input_file = temp_dir / "input.css"
    output_file = temp_dir / "output.css"
    input_file.write_text("/* test css */")

    # Mock successful subprocess call (npx check is now in _check_dependencies)
    mock_run.return_value = Mock(returncode=0, stderr="", stdout="")

    _run_build_process(str(input_file), str(output_file), True, False)

    assert mock_run.call_count == 1


@patch("labb.cli.handlers.build_handler.subprocess.run")
@patch("labb.cli.handlers.build_handler.console")
def test_run_build_process_watch_mode(mock_console, mock_run, temp_dir):
    input_file = temp_dir / "input.css"
    output_file = temp_dir / "output.css"
    input_file.write_text("/* test css */")

    # Mock keyboard interrupt (npx check is now in _check_dependencies)
    mock_run.side_effect = KeyboardInterrupt()

    with pytest.raises(SystemExit):
        _run_build_process(str(input_file), str(output_file), True, True)


@patch("labb.cli.handlers.build_handler.subprocess.run")
@patch("labb.cli.handlers.build_handler.console")
def test_run_build_process_npx_not_found(mock_console, mock_run, temp_dir):
    """Test that build process fails if npx command fails"""
    input_file = temp_dir / "input.css"
    output_file = temp_dir / "output.css"
    input_file.write_text("/* test css */")

    # npx check is now in _check_dependencies, this tests the build command failing
    mock_run.side_effect = FileNotFoundError()

    with pytest.raises(SystemExit):
        _run_build_process(str(input_file), str(output_file), True, False)


@patch("labb.cli.handlers.build_handler.subprocess.run")
@patch("labb.cli.handlers.build_handler.console")
def test_run_build_process_build_error(mock_console, mock_run, temp_dir):
    input_file = temp_dir / "input.css"
    output_file = temp_dir / "output.css"
    input_file.write_text("/* test css */")

    # Mock build failure (npx check is now in _check_dependencies)
    mock_run.side_effect = subprocess.CalledProcessError(
        1, "npx", stderr="Build failed"
    )

    with pytest.raises(SystemExit):
        _run_build_process(str(input_file), str(output_file), True, False)


@patch("labb.cli.handlers.build_handler.threading")
@patch("labb.cli.handlers.build_handler.console")
def test_run_concurrent_build_and_scan(mock_console, mock_threading, mock_config):
    mock_thread1 = Mock()
    mock_thread2 = Mock()
    mock_threading.Thread.side_effect = [mock_thread1, mock_thread2]
    mock_threading.Event.return_value = Mock()

    # Mock threads as not alive to exit the loop quickly
    mock_thread1.is_alive.return_value = False
    mock_thread2.is_alive.return_value = False

    _run_concurrent_build_and_scan("input.css", "output.css", True, mock_config)

    mock_thread1.start.assert_called_once()
    mock_thread2.start.assert_called_once()
    assert mock_threading.Thread.call_count == 2


@patch("labb.cli.handlers.build_handler.subprocess.Popen")
@patch("labb.cli.handlers.build_handler.console")
def test_run_build_watcher(mock_console, mock_popen):
    mock_stop_event = Mock()
    mock_stop_event.is_set.side_effect = [False, True]  # Stop after one iteration

    mock_process = Mock()
    mock_process.poll.return_value = None  # Process still running
    mock_popen.return_value = mock_process

    _run_build_watcher("input.css", "output.css", True, mock_stop_event)

    mock_popen.assert_called_once()


@patch("labb.cli.handlers.scan_handler._watch_and_scan_with_stop_event_live")
@patch("labb.cli.handlers.build_handler.console")
def test_run_scan_watcher(mock_console, mock_watch_scan):
    mock_stop_event = Mock()
    template_patterns = ["templates/**/*.html"]
    output_path = "classes.txt"

    _run_scan_watcher(template_patterns, output_path, mock_stop_event)

    mock_watch_scan.assert_called_once_with(
        template_patterns, output_path, False, mock_stop_event, scan_apps=None
    )


@patch("labb.cli.handlers.scan_handler._watch_and_scan_with_stop_event_live")
@patch("labb.cli.handlers.build_handler.console")
def test_run_scan_watcher_with_scan_apps(mock_console, mock_watch_scan):
    """Test scan watcher with scan_apps configuration"""
    mock_stop_event = Mock()
    template_patterns = ["templates/**/*.html"]
    output_path = "classes.txt"
    scan_apps = {"myapp": ["templates/components/**/*.html"]}

    _run_scan_watcher(template_patterns, output_path, mock_stop_event, scan_apps)

    mock_watch_scan.assert_called_once_with(
        template_patterns, output_path, False, mock_stop_event, scan_apps=scan_apps
    )


@patch("labb.cli.handlers.build_handler.subprocess.run")
@patch("labb.cli.handlers.build_handler.console")
def test_run_build_process_with_file_size(mock_console, mock_run, temp_dir):
    input_file = temp_dir / "input.css"
    output_file = temp_dir / "output.css"
    input_file.write_text("/* test css */")
    output_file.write_text("/* output css */")

    # Mock successful subprocess call (npx check is now in _check_dependencies)
    mock_run.return_value = Mock(returncode=0, stderr="", stdout="")

    _run_build_process(str(input_file), str(output_file), True, False)

    print_calls = mock_console.print.call_args_list
    printed_text = str(print_calls)
    assert "File size:" in printed_text or "KB" in printed_text


@patch("labb.cli.handlers.build_handler.subprocess.run")
@patch("labb.cli.handlers.build_handler.console")
def test_run_build_process_command_construction(mock_console, mock_run, temp_dir):
    input_file = temp_dir / "input.css"
    output_file = temp_dir / "output.css"
    input_file.write_text("/* test css */")

    # Mock successful subprocess call (npx check is now in _check_dependencies)
    mock_run.return_value = Mock(returncode=0, stderr="", stdout="")

    _run_build_process(str(input_file), str(output_file), True, False)

    # Check the build command was constructed correctly
    build_call = mock_run.call_args_list[0]
    command = build_call[0][0]

    assert "npx" in command
    assert "@tailwindcss/cli" in command
    assert "-i" in command
    assert str(input_file) in command
    assert "-o" in command
    assert str(output_file) in command
    assert "--minify" in command


# Additional tests for improved coverage


@patch("labb.cli.handlers.build_handler.subprocess.run")
@patch("labb.cli.handlers.build_handler.console")
def test_run_build_process_with_warnings(mock_console, mock_run, temp_dir):
    """Test build process with warnings"""
    input_file = temp_dir / "input.css"
    output_file = temp_dir / "output.css"
    input_file.write_text("/* test css */")

    # Mock build with warnings (npx check is now in _check_dependencies)
    error = subprocess.CalledProcessError(1, "npx")
    error.stderr = "Warning: some warning"
    mock_run.side_effect = error

    with pytest.raises(SystemExit):
        _run_build_process(str(input_file), str(output_file), True, False)

    # Should show warning/error message
    print_calls = mock_console.print.call_args_list
    error_calls = [
        call
        for call in print_calls
        if "failed" in str(call).lower() or "error" in str(call).lower()
    ]
    assert len(error_calls) > 0


@patch("labb.cli.handlers.build_handler.subprocess.run")
@patch("labb.cli.handlers.build_handler.console")
def test_run_build_process_with_stdout_output(mock_console, mock_run, temp_dir):
    """Test build process with stdout output"""
    input_file = temp_dir / "input.css"
    output_file = temp_dir / "output.css"
    input_file.write_text("/* test css */")

    # Mock build failure with stdout (npx check is now in _check_dependencies)
    mock_run.side_effect = subprocess.CalledProcessError(
        1, "npx", output="Build completed", stderr=""
    )

    with pytest.raises(SystemExit):
        _run_build_process(str(input_file), str(output_file), True, False)

    # Should show stdout output in error case
    print_calls = mock_console.print.call_args_list
    stdout_calls = [call for call in print_calls if "Build completed" in str(call)]
    assert len(stdout_calls) > 0


@patch("labb.cli.handlers.build_handler.subprocess.run")
@patch("labb.cli.handlers.build_handler.console")
def test_run_build_process_file_size_error(mock_console, mock_run, temp_dir):
    """Test build process when file size calculation fails"""
    input_file = temp_dir / "input.css"
    output_file = temp_dir / "output.css"
    input_file.write_text("/* test css */")

    # Mock successful subprocess call (npx check is now in _check_dependencies)
    mock_run.return_value = Mock(returncode=0, stderr="", stdout="")

    # Mock Path.stat to raise an exception
    with patch("pathlib.Path.stat", side_effect=OSError("File not found")):
        _run_build_process(str(input_file), str(output_file), True, False)

    # Should still complete successfully without file size
    success_calls = [
        call
        for call in mock_console.print.call_args_list
        if "successfully" in str(call).lower()
    ]
    assert len(success_calls) > 0


@patch("labb.cli.handlers.build_handler.subprocess.run")
@patch("labb.cli.handlers.build_handler.console")
def test_run_build_process_tailwind_error(mock_console, mock_run, temp_dir):
    """Test build process with tailwind-specific error"""
    input_file = temp_dir / "input.css"
    output_file = temp_dir / "output.css"
    input_file.write_text("/* test css */")

    # Mock build failure with tailwind error (npx check is now in _check_dependencies)
    mock_run.side_effect = subprocess.CalledProcessError(
        1, "npx tailwindcss", stderr="tailwindcss error"
    )

    with pytest.raises(SystemExit):
        _run_build_process(str(input_file), str(output_file), True, False)

    # Should show troubleshooting message
    print_calls = mock_console.print.call_args_list
    troubleshooting_calls = [
        call for call in print_calls if "Troubleshooting" in str(call)
    ]
    assert len(troubleshooting_calls) > 0


@patch("labb.cli.handlers.build_handler.subprocess.run")
@patch("labb.cli.handlers.build_handler.console")
def test_run_build_process_unexpected_error(mock_console, mock_run, temp_dir):
    """Test build process with unexpected error"""
    input_file = temp_dir / "input.css"
    output_file = temp_dir / "output.css"
    input_file.write_text("/* test css */")

    # Mock build failure with unexpected error (npx check is now in _check_dependencies)
    mock_run.side_effect = Exception("Unexpected error")

    with pytest.raises(SystemExit):
        _run_build_process(str(input_file), str(output_file), True, False)

    # Should show unexpected error message
    print_calls = mock_console.print.call_args_list
    error_calls = [call for call in print_calls if "Unexpected error" in str(call)]
    assert len(error_calls) > 0


@patch("labb.cli.handlers.build_handler.subprocess.Popen")
@patch("labb.cli.handlers.build_handler.console")
def test_run_build_watcher_process_error(mock_console, mock_popen):
    """Test build watcher when process encounters an error"""
    mock_stop_event = Mock()
    mock_stop_event.is_set.return_value = False

    mock_process = Mock()
    mock_process.poll.return_value = 1  # Process exited with error
    mock_popen.return_value = mock_process

    _run_build_watcher("input.css", "output.css", True, mock_stop_event)

    mock_popen.assert_called_once()
    # Should not call terminate since process already exited


@patch("labb.cli.handlers.build_handler.subprocess.Popen")
@patch("labb.cli.handlers.build_handler.console")
def test_run_build_watcher_exception_handling(mock_console, mock_popen):
    """Test build watcher exception handling"""
    mock_stop_event = Mock()
    mock_stop_event.is_set.return_value = False

    mock_popen.side_effect = Exception("Process creation failed")

    _run_build_watcher("input.css", "output.css", True, mock_stop_event)

    # Should handle the exception gracefully
    mock_popen.assert_called_once()


@patch("labb.cli.handlers.build_handler.subprocess.Popen")
@patch("labb.cli.handlers.build_handler.console")
def test_run_build_watcher_process_termination(mock_console, mock_popen):
    """Test build watcher process termination"""
    mock_stop_event = Mock()
    mock_stop_event.is_set.side_effect = [False, True]  # Stop after one iteration

    mock_process = Mock()
    mock_process.poll.return_value = None  # Process still running
    mock_popen.return_value = mock_process

    _run_build_watcher("input.css", "output.css", True, mock_stop_event)

    mock_popen.assert_called_once()
    mock_process.terminate.assert_called_once()
    mock_process.wait.assert_called_once()


@patch("labb.cli.handlers.build_handler.subprocess.Popen")
@patch("labb.cli.handlers.build_handler.console")
def test_run_build_watcher_process_already_terminated(mock_console, mock_popen):
    """Test build watcher when process is already terminated"""
    mock_stop_event = Mock()
    mock_stop_event.is_set.side_effect = [False, True]  # Stop after one iteration

    mock_process = Mock()
    mock_process.poll.return_value = 0  # Process already terminated normally
    mock_popen.return_value = mock_process

    _run_build_watcher("input.css", "output.css", True, mock_stop_event)

    mock_popen.assert_called_once()
    # Should not call terminate since process already exited
    mock_process.terminate.assert_not_called()


@patch("labb.cli.handlers.scan_handler._watch_and_scan_with_stop_event_live")
@patch("labb.cli.handlers.build_handler.console")
def test_run_scan_watcher_exception_handling(mock_console, mock_watch_scan):
    """Test scan watcher exception handling"""
    mock_stop_event = Mock()
    mock_stop_event.is_set.return_value = False
    template_patterns = ["templates/**/*.html"]
    output_path = "classes.txt"

    mock_watch_scan.side_effect = Exception("Scan error")

    _run_scan_watcher(template_patterns, output_path, mock_stop_event)

    # Should handle the exception gracefully
    mock_watch_scan.assert_called_once()


@patch("labb.cli.handlers.build_handler.threading")
@patch("labb.cli.handlers.build_handler.console")
def test_run_concurrent_build_and_scan_keyboard_interrupt(mock_console, mock_threading):
    """Test concurrent build and scan with keyboard interrupt"""
    mock_thread1 = Mock()
    mock_thread2 = Mock()
    mock_threading.Thread.side_effect = [mock_thread1, mock_thread2]
    mock_stop_event = Mock()
    mock_threading.Event.return_value = mock_stop_event

    # Mock config with proper attributes
    mock_config = Mock()
    mock_config.classes_output = "classes.txt"
    mock_config.template_patterns = ["templates/**/*.html"]
    mock_config.scan_apps = {"myapp": ["templates/components/**/*.html"]}

    # Mock threads as alive, then raise KeyboardInterrupt
    mock_thread1.is_alive.return_value = True
    mock_thread2.is_alive.return_value = True

    # Mock time.sleep to raise KeyboardInterrupt after threads start
    with patch(
        "labb.cli.handlers.build_handler.time.sleep",
        side_effect=[0.5, 0.1, KeyboardInterrupt],  # Allow threads to start first
    ):
        with pytest.raises(SystemExit):
            _run_concurrent_build_and_scan("input.css", "output.css", True, mock_config)

    mock_thread1.start.assert_called_once()
    mock_thread2.start.assert_called_once()
    mock_stop_event.set.assert_called_once()


@patch("labb.cli.handlers.build_handler.threading")
@patch("labb.cli.handlers.build_handler.console")
def test_run_concurrent_build_and_scan_thread_join_timeout(
    mock_console, mock_threading
):
    """Test concurrent build and scan with thread join timeout"""
    mock_thread1 = Mock()
    mock_thread2 = Mock()
    mock_threading.Thread.side_effect = [mock_thread1, mock_thread2]
    mock_stop_event = Mock()
    mock_threading.Event.return_value = mock_stop_event

    # Mock config with proper attributes
    mock_config = Mock()
    mock_config.classes_output = "classes.txt"
    mock_config.template_patterns = ["templates/**/*.html"]
    mock_config.scan_apps = {"myapp": ["templates/components/**/*.html"]}

    # Mock threads as alive initially, then one becomes dead
    mock_thread1.is_alive.side_effect = [True, False]
    mock_thread2.is_alive.side_effect = [True, False]

    # Mock time.sleep to raise KeyboardInterrupt after threads start
    with patch(
        "labb.cli.handlers.build_handler.time.sleep",
        side_effect=[0.1, KeyboardInterrupt],
    ):
        with pytest.raises(SystemExit):
            _run_concurrent_build_and_scan("input.css", "output.css", True, mock_config)

    mock_thread1.start.assert_called_once()
    mock_thread2.start.assert_called_once()
    mock_stop_event.set.assert_called_once()


@patch("labb.cli.handlers.build_handler.subprocess.run")
@patch("labb.cli.handlers.build_handler.console")
def test_run_build_process_no_minify(mock_console, mock_run, temp_dir):
    """Test build process without minification"""
    input_file = temp_dir / "input.css"
    output_file = temp_dir / "output.css"
    input_file.write_text("/* test css */")

    # Mock successful subprocess call (npx check is now in _check_dependencies)
    mock_run.return_value = Mock(returncode=0, stderr="", stdout="")

    _run_build_process(str(input_file), str(output_file), False, False)

    # Check that --minify was not included in the command
    build_call = mock_run.call_args_list[0]  # First call is the build
    cmd = build_call[0][0]  # First argument is the command list
    assert "--minify" not in cmd


@patch("labb.cli.handlers.build_handler.subprocess.run")
@patch("labb.cli.handlers.build_handler.console")
def test_run_build_process_watch_mode_keyboard_interrupt(
    mock_console, mock_run, temp_dir
):
    """Test build process in watch mode with keyboard interrupt"""
    input_file = temp_dir / "input.css"
    output_file = temp_dir / "output.css"
    input_file.write_text("/* test css */")

    # Mock keyboard interrupt during watch (npx check is now in _check_dependencies)
    mock_run.side_effect = KeyboardInterrupt()

    with pytest.raises(SystemExit):
        _run_build_process(str(input_file), str(output_file), True, True)

    # Should show stop message
    print_calls = mock_console.print.call_args_list
    stop_calls = [call for call in print_calls if "stopped" in str(call).lower()]
    assert len(stop_calls) > 0


@patch("labb.cli.handlers.build_handler.subprocess.run")
@patch("labb.cli.handlers.build_handler.console")
@patch("labb.cli.handlers.build_handler.sys.platform", "win32")
def test_check_dependencies_windows_uses_shell(mock_console, mock_run):
    """On Windows, npx version check must use shell=True so npx.cmd resolves."""
    mock_run.return_value = Mock(returncode=0)
    with patch("pathlib.Path.exists", return_value=True):
        _check_dependencies()
    _, kwargs = mock_run.call_args
    assert kwargs.get("shell") is True


@patch("labb.cli.handlers.build_handler.subprocess.Popen")
@patch("labb.cli.handlers.build_handler.console")
@patch("labb.cli.handlers.build_handler.sys.platform", "win32")
def test_run_build_watcher_windows_uses_shell(mock_console, mock_popen):
    """On Windows, Popen must use shell=True so npx.cmd resolves."""
    mock_stop_event = Mock()
    mock_stop_event.is_set.return_value = True
    mock_process = Mock()
    mock_process.poll.return_value = 0
    mock_popen.return_value = mock_process

    _run_build_watcher("input.css", "output.css", False, mock_stop_event)

    _, kwargs = mock_popen.call_args
    assert kwargs.get("shell") is True
