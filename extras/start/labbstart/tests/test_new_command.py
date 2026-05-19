"""Unit tests for labbstart CLI new command"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from labbstart.cli.handlers.new_handler import (
    AVAILABLE_KITS,
    DJANGO_MIN_PYTHON,
    DJANGO_VERSIONS,
    PACKAGE_MANAGERS,
    append_kit_styles,
    copy_kit_to_project,
    create_gitignore,
    create_project_readme,
    get_project_params,
    get_python_command,
    install_labb_packages,
    run_command,
    setup_pip_project,
    setup_poetry_project,
    setup_uv_project,
    update_settings_py,
    update_urls_py,
    validate_project_name,
)

# ============================================================================
# Test Project Name Validation
# ============================================================================


class TestValidateProjectName:
    """Test project name validation"""

    def test_valid_names(self):
        """Test that valid project names are accepted"""
        valid_names = [
            "myproject",
            "my_project",
            "MyProject",
            "project123",
            "_private",
            "project_123",
            "a",
            "A",
            "_",
            "a1b2c3",
        ]
        for name in valid_names:
            assert validate_project_name(name), f"{name} should be valid"

    def test_invalid_names(self):
        """Test that invalid project names are rejected"""
        invalid_names = [
            "",  # Empty
            "123project",  # Starts with number
            "my-project",  # Contains hyphen
            "my project",  # Contains space
            "my.project",  # Contains dot
            "my@project",  # Contains special char
            "my$project",  # Contains dollar sign
            "project!",  # Contains exclamation
            "my/project",  # Contains slash
        ]
        for name in invalid_names:
            assert not validate_project_name(name), f"{name} should be invalid"

    def test_empty_string(self):
        """Test that empty string is invalid"""
        assert not validate_project_name("")

    def test_none_value(self):
        """Test that None is invalid"""
        assert not validate_project_name(None)


# ============================================================================
# Test Get Project Params
# ============================================================================


class TestGetProjectParams:
    """Test project parameter collection"""

    def test_all_params_provided(self):
        """Test when all parameters are provided"""
        params = get_project_params(
            name="testproject",
            django_version=5,
            package_manager="poetry",
            kit="welcome",
            app_name="starter",
        )

        assert params["name"] == "testproject"
        assert params["django_version"] == 5
        assert params["package_manager"] == "poetry"
        assert params["kit"] == "welcome"
        assert params["app_name"] == "starter"

    @patch("labbstart.cli.handlers.new_handler.Prompt.ask")
    @patch("labbstart.cli.handlers.new_handler.questionary.select")
    @patch("labbstart.cli.handlers.new_handler.Path")
    def test_interactive_mode_all_defaults(
        self, mock_path, mock_questionary_select, mock_prompt
    ):
        """Test interactive mode with all default values"""
        # Mock Path.exists to return False (directory doesn't exist)
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance

        # Mock questionary.select to return values for Django version, package manager, and kit
        mock_select = MagicMock()
        mock_select.ask.side_effect = [5, "poetry", "welcome"]
        mock_questionary_select.return_value = mock_select

        # Set up prompts to return default values
        mock_prompt.side_effect = ["myproject", "starter"]

        params = get_project_params(
            name=None,
            django_version=None,
            package_manager=None,
            kit=None,
            app_name=None,
        )

        assert params["name"] == "myproject"
        assert params["django_version"] == 5
        assert params["package_manager"] == "poetry"
        assert params["kit"] == "welcome"
        assert params["app_name"] == "starter"

    @patch("labbstart.cli.handlers.new_handler.Prompt.ask")
    @patch("labbstart.cli.handlers.new_handler.questionary.select")
    @patch("labbstart.cli.handlers.new_handler.Path")
    def test_interactive_mode_custom_values(
        self, mock_path, mock_questionary_select, mock_prompt
    ):
        """Test interactive mode with custom values"""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance

        # Mock questionary.select for Django version, package manager, and kit
        mock_select = MagicMock()
        mock_select.ask.side_effect = [4, "uv", "welcome"]
        mock_questionary_select.return_value = mock_select

        mock_prompt.side_effect = ["customproject", "myapp"]

        params = get_project_params(
            name=None,
            django_version=None,
            package_manager=None,
            kit=None,
            app_name=None,
        )

        assert params["name"] == "customproject"
        assert params["django_version"] == 4
        assert params["package_manager"] == "uv"
        assert params["kit"] == "welcome"
        assert params["app_name"] == "myapp"

    @patch("labbstart.cli.handlers.new_handler.Prompt.ask")
    @patch("labbstart.cli.handlers.new_handler.Confirm.ask")
    @patch("labbstart.cli.handlers.new_handler.shutil.rmtree")
    @patch("labbstart.cli.handlers.new_handler.questionary.select")
    @patch("labbstart.cli.handlers.new_handler.Path")
    def test_existing_directory_overwrite(
        self, mock_path, mock_questionary_select, mock_rmtree, mock_confirm, mock_prompt
    ):
        """Test handling of existing directory with overwrite confirmation"""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        mock_confirm.return_value = True  # User confirms overwrite

        # Mock questionary.select for Django version, package manager, and kit
        mock_select = MagicMock()
        mock_select.ask.side_effect = [5, "poetry", "welcome"]
        mock_questionary_select.return_value = mock_select

        mock_prompt.side_effect = ["starter"]

        params = get_project_params(
            name="existing",
            django_version=None,
            package_manager=None,
            kit=None,
            app_name=None,
        )

        assert params["name"] == "existing"
        mock_rmtree.assert_called_once()

    @patch("labbstart.cli.handlers.new_handler.Confirm.ask")
    @patch("labbstart.cli.handlers.new_handler.Path")
    def test_existing_directory_abort(self, mock_path, mock_confirm):
        """Test aborting when directory exists and user declines overwrite"""
        import typer

        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        mock_confirm.return_value = False  # User declines overwrite

        with pytest.raises(typer.Exit):
            get_project_params(
                name="existing",
                django_version=None,
                package_manager=None,
                kit=None,
                app_name=None,
            )

    @patch("labbstart.cli.handlers.new_handler.Prompt.ask")
    @patch("labbstart.cli.handlers.new_handler.questionary.select")
    @patch("labbstart.cli.handlers.new_handler.Path")
    def test_partial_params_provided(
        self, mock_path, mock_questionary_select, mock_prompt
    ):
        """Test when some parameters are provided and some need prompting"""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance

        # Only kit will be prompted via questionary (django_version and package_manager are provided)
        mock_select = MagicMock()
        mock_select.ask.return_value = "welcome"
        mock_questionary_select.return_value = mock_select

        # Only app_name will be prompted via Prompt.ask
        mock_prompt.side_effect = ["starter"]

        params = get_project_params(
            name="myproject",
            django_version=5,
            package_manager="poetry",
            kit=None,
            app_name=None,
        )

        assert params["name"] == "myproject"
        assert params["django_version"] == 5
        assert params["package_manager"] == "poetry"
        assert params["kit"] == "welcome"
        assert params["app_name"] == "starter"

    @patch("labbstart.cli.handlers.new_handler.Prompt.ask")
    @patch("labbstart.cli.handlers.new_handler.questionary.select")
    @patch("labbstart.cli.handlers.new_handler.Path")
    def test_invalid_project_name_retry(
        self, mock_path, mock_questionary_select, mock_prompt
    ):
        """Test retrying when invalid project name is provided"""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance

        # Mock questionary.select for Django version, package manager, and kit
        mock_select = MagicMock()
        mock_select.ask.side_effect = [5, "poetry", "welcome"]
        mock_questionary_select.return_value = mock_select

        # First invalid name, then valid name, then app_name
        mock_prompt.side_effect = [
            "123invalid",  # Invalid (starts with number)
            "validproject",  # Valid
            "starter",
        ]

        params = get_project_params(
            name=None,
            django_version=None,
            package_manager=None,
            kit=None,
            app_name=None,
        )

        assert params["name"] == "validproject"


# ============================================================================
# Test Run Command
# ============================================================================


class TestRunCommand:
    """Test command execution function"""

    @patch("labbstart.cli.handlers.new_handler.subprocess.run")
    def test_run_command_success(self, mock_run):
        """Test successful command execution"""
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        result = run_command(["echo", "test"])

        assert result is True
        mock_run.assert_called_once()

    @patch("labbstart.cli.handlers.new_handler.subprocess.run")
    def test_run_command_failure(self, mock_run):
        """Test failed command execution"""
        mock_run.return_value = MagicMock(returncode=1, stderr="Error occurred")

        result = run_command(["false"])

        assert result is False

    @patch("labbstart.cli.handlers.new_handler.subprocess.run")
    def test_run_command_with_cwd(self, mock_run):
        """Test command execution with working directory"""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        cwd = Path("/tmp/test")

        run_command(["echo", "test"], cwd=cwd)

        args, kwargs = mock_run.call_args
        assert kwargs["cwd"] == cwd

    @patch("labbstart.cli.handlers.new_handler.subprocess.run")
    def test_run_command_with_clean_env(self, mock_run):
        """Test command execution with clean environment"""
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        # Set some env vars that should be removed
        with patch.dict(
            os.environ, {"VIRTUAL_ENV": "/path/to/venv", "POETRY_ACTIVE": "1"}
        ):
            run_command(["echo", "test"], clean_env=True)

            args, kwargs = mock_run.call_args
            env = kwargs["env"]
            assert "VIRTUAL_ENV" not in env
            assert "POETRY_ACTIVE" not in env

    @patch("labbstart.cli.handlers.new_handler.subprocess.run")
    def test_run_command_with_custom_env(self, mock_run):
        """Test command execution with custom environment"""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        custom_env = {"CUSTOM_VAR": "value"}

        run_command(["echo", "test"], env=custom_env)

        args, kwargs = mock_run.call_args
        assert kwargs["env"] == custom_env

    @patch("labbstart.cli.handlers.new_handler.subprocess.run")
    def test_run_command_exception_handling(self, mock_run):
        """Test exception handling in command execution"""
        mock_run.side_effect = Exception("Command failed")

        result = run_command(["echo", "test"])

        assert result is False


# ============================================================================
# Test Get Python Command
# ============================================================================


class TestGetPythonCommand:
    """Test Python command generation for different package managers"""

    def test_get_python_command_poetry_unix(self):
        """Test Python command for poetry on Unix"""
        with patch("sys.platform", "linux"):
            project_path = Path("/tmp/project")
            cmd = get_python_command(project_path, "poetry")
            assert str(project_path / ".venv" / "bin" / "python") in str(cmd[0])

    def test_get_python_command_poetry_windows(self):
        """Test Python command for poetry on Windows"""
        with patch("sys.platform", "win32"):
            project_path = Path("C:/project")
            cmd = get_python_command(project_path, "poetry")
            assert "Scripts" in str(cmd[0])
            assert "python" in str(cmd[0])

    def test_get_python_command_pip_unix(self):
        """Test Python command for pip on Unix"""
        with patch("sys.platform", "linux"):
            project_path = Path("/tmp/project")
            cmd = get_python_command(project_path, "pip")
            assert str(project_path / "venv" / "bin" / "python") in str(cmd[0])

    def test_get_python_command_pip_windows(self):
        """Test Python command for pip on Windows"""
        with patch("sys.platform", "win32"):
            project_path = Path("C:/project")
            cmd = get_python_command(project_path, "pip")
            assert "venv" in str(cmd[0])
            assert "Scripts" in str(cmd[0])

    def test_get_python_command_uv(self):
        """Test Python command for uv (platform independent)"""
        project_path = Path("/tmp/project")
        cmd = get_python_command(project_path, "uv")
        assert cmd == ["uv", "run", "python"]

    def test_get_python_command_unknown(self):
        """Test Python command for unknown package manager"""
        project_path = Path("/tmp/project")
        cmd = get_python_command(project_path, "unknown")
        assert cmd == ["python"]


# ============================================================================
# Test Setup Functions
# ============================================================================


class TestSetupPoetryProject:
    """Test Poetry project setup"""

    @patch("labbstart.cli.handlers.new_handler.run_command")
    def test_setup_poetry_success(self, mock_run_command):
        """Test successful Poetry project setup"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            mock_run_command.return_value = True

            result = setup_poetry_project(project_path, "5.0")

            assert result is True
            # Verify README was created
            assert (project_path / "README.md").exists()
            # Verify run_command was called for init, config, add, and install
            assert mock_run_command.call_count >= 3

    @patch("labbstart.cli.handlers.new_handler.run_command")
    def test_setup_poetry_init_failure(self, mock_run_command):
        """Test Poetry setup when init fails"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            mock_run_command.return_value = False

            result = setup_poetry_project(project_path, "5.0")

            assert result is False

    @patch("labbstart.cli.handlers.new_handler.run_command")
    def test_setup_poetry_adds_package_mode(self, mock_run_command):
        """Test that Poetry setup adds package-mode = false"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            pyproject_file = project_path / "pyproject.toml"

            def create_pyproject(*args, **kwargs):
                # Simulate poetry init creating pyproject.toml
                if args[0][1] == "init":
                    pyproject_file.write_text("[tool.poetry]\nname = 'test'\n")
                return True

            mock_run_command.side_effect = create_pyproject

            setup_poetry_project(project_path, "5.0")

            if pyproject_file.exists():
                content = pyproject_file.read_text()
                assert "package-mode" in content

    @patch("labbstart.cli.handlers.new_handler.run_command")
    def test_setup_poetry_django_version(self, mock_run_command):
        """Test that correct Django version is added"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            mock_run_command.return_value = True

            setup_poetry_project(project_path, "4.2")

            # Check that poetry add was called with correct Django version
            add_call = None
            for call in mock_run_command.call_args_list:
                if "add" in call[0][0]:
                    add_call = call
                    break

            assert add_call is not None
            assert "django~=4.2" in add_call[0][0]

    @patch("labbstart.cli.handlers.new_handler.run_command")
    @pytest.mark.parametrize("django_version", ["4.2", "5.0", "6.0"])
    def test_setup_poetry_all_django_versions(self, mock_run_command, django_version):
        """Test poetry setup across all supported Django versions"""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run_command.return_value = True
            setup_poetry_project(Path(tmpdir), django_version)
            add_calls = [c for c in mock_run_command.call_args_list if "add" in c[0][0]]
            assert add_calls, "poetry add was never called"
            assert f"django~={django_version}" in add_calls[0][0][0]


class TestSetupPipProject:
    """Test pip/venv project setup"""

    @patch("labbstart.cli.handlers.new_handler.subprocess.run")
    @patch("labbstart.cli.handlers.new_handler.run_command")
    @patch("labbstart.cli.handlers.new_handler.sys")
    def test_setup_pip_success_unix(self, mock_sys, mock_run_command, mock_subprocess):
        """Test successful pip project setup on Unix"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            mock_sys.platform = "linux"
            mock_sys.executable = "/usr/bin/python3"
            mock_run_command.return_value = True

            # Mock subprocess.run for Python version check
            mock_subprocess.return_value = MagicMock(
                returncode=0, stdout="Python 3.10.0", stderr=""
            )

            # Create venv/bin directory structure
            venv_bin = project_path / "venv" / "bin"
            venv_bin.mkdir(parents=True)
            (venv_bin / "pip").touch()
            (venv_bin / "python").touch()

            result = setup_pip_project(project_path, "5.0")

            assert result is True
            assert (project_path / "requirements.txt").exists()

    @patch("labbstart.cli.handlers.new_handler.subprocess.run")
    @patch("labbstart.cli.handlers.new_handler.run_command")
    @patch("labbstart.cli.handlers.new_handler.sys")
    def test_setup_pip_success_windows(
        self, mock_sys, mock_run_command, mock_subprocess
    ):
        """Test successful pip project setup on Windows"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            mock_sys.platform = "win32"
            mock_sys.executable = "C:\\Python\\python.exe"
            mock_run_command.return_value = True

            # Mock subprocess.run for Python version check
            mock_subprocess.return_value = MagicMock(
                returncode=0, stdout="Python 3.10.0", stderr=""
            )

            # Create venv/Scripts directory structure
            venv_scripts = project_path / "venv" / "Scripts"
            venv_scripts.mkdir(parents=True)
            (venv_scripts / "pip").touch()
            (venv_scripts / "python").touch()

            result = setup_pip_project(project_path, "5.0")

            assert result is True

    @patch("labbstart.cli.handlers.new_handler.run_command")
    def test_setup_pip_venv_failure(self, mock_run_command):
        """Test pip setup when venv creation fails"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            mock_run_command.return_value = False

            result = setup_pip_project(project_path, "5.0")

            assert result is False

    @patch("labbstart.cli.handlers.new_handler.subprocess.run")
    @patch("labbstart.cli.handlers.new_handler.run_command")
    @patch("labbstart.cli.handlers.new_handler.sys")
    def test_setup_pip_requirements_content(
        self, mock_sys, mock_run_command, mock_subprocess
    ):
        """Test that requirements.txt has correct content"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            mock_sys.platform = "linux"
            mock_sys.executable = "/usr/bin/python3"
            mock_run_command.return_value = True

            # Mock subprocess.run for Python version check
            mock_subprocess.return_value = MagicMock(
                returncode=0, stdout="Python 3.10.0", stderr=""
            )

            venv_bin = project_path / "venv" / "bin"
            venv_bin.mkdir(parents=True)
            (venv_bin / "pip").touch()
            (venv_bin / "python").touch()

            setup_pip_project(project_path, "4.2")

            requirements = project_path / "requirements.txt"
            content = requirements.read_text()
            assert "django~=4.2" in content
            assert "Python" in content  # Python version comment

    @patch("labbstart.cli.handlers.new_handler.subprocess.run")
    @patch("labbstart.cli.handlers.new_handler.run_command")
    @patch("labbstart.cli.handlers.new_handler.sys")
    @pytest.mark.parametrize(
        "django_version,expected_python",
        [("4.2", "3.10"), ("5.0", "3.10"), ("6.0", "3.12")],
    )
    def test_setup_pip_requirements_all_versions(
        self,
        mock_sys,
        mock_run_command,
        mock_subprocess,
        django_version,
        expected_python,
    ):
        """Test that requirements.txt records the correct min-python for each Django version"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            mock_sys.platform = "linux"
            mock_sys.executable = "/usr/bin/python3"
            mock_run_command.return_value = True
            mock_subprocess.return_value = MagicMock(
                returncode=0, stdout="Python 3.10.0", stderr=""
            )
            venv_bin = project_path / "venv" / "bin"
            venv_bin.mkdir(parents=True)
            (venv_bin / "pip").touch()
            (venv_bin / "python").touch()
            setup_pip_project(project_path, django_version)
            content = (project_path / "requirements.txt").read_text()
            assert f"django~={django_version}" in content
            assert expected_python in content


class TestSetupUvProject:
    """Test uv project setup"""

    @patch("labbstart.cli.handlers.new_handler.run_command")
    def test_setup_uv_success(self, mock_run_command):
        """Test successful uv project setup"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            def create_pyproject(*args, **kwargs):
                # Simulate uv init creating pyproject.toml
                if args[0][1] == "init":
                    pyproject_file = project_path / "pyproject.toml"
                    pyproject_file.write_text(
                        '[project]\nname = "test"\nrequires-python = ">=3.10"\n'
                    )
                return True

            mock_run_command.side_effect = create_pyproject

            result = setup_uv_project(project_path, "5.0")

            assert result is True

    @patch("labbstart.cli.handlers.new_handler.run_command")
    def test_setup_uv_init_failure(self, mock_run_command):
        """Test uv setup when init fails"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            mock_run_command.return_value = False

            result = setup_uv_project(project_path, "5.0")

            assert result is False

    @patch("labbstart.cli.handlers.new_handler.run_command")
    def test_setup_uv_python_version_constraint(self, mock_run_command):
        """Test that uv project has correct Python version constraint"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            pyproject_file = project_path / "pyproject.toml"

            def create_and_check(*args, **kwargs):
                if args[0][1] == "init":
                    pyproject_file.write_text(
                        '[project]\nname = "test"\nrequires-python = ">=3.10"\n'
                    )
                return True

            mock_run_command.side_effect = create_and_check

            setup_uv_project(project_path, "5.0")

            if pyproject_file.exists():
                content = pyproject_file.read_text()
                assert "requires-python" in content
                assert "3.10" in content

    @patch("labbstart.cli.handlers.new_handler.run_command")
    def test_setup_uv_django_version(self, mock_run_command):
        """Test that correct Django version is added with uv"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            pyproject_file = project_path / "pyproject.toml"

            def mock_command(*args, **kwargs):
                if "init" in args[0]:
                    pyproject_file.write_text(
                        '[project]\nname = "test"\nrequires-python = ">=3.10"\n'
                    )
                return True

            mock_run_command.side_effect = mock_command

            setup_uv_project(project_path, "6.0")

            # Check that uv add was called with correct Django version
            add_call = None
            for call in mock_run_command.call_args_list:
                if len(call[0]) > 0 and "add" in call[0][0]:
                    add_call = call
                    break

            assert add_call is not None
            assert "django~=6.0" in add_call[0][0]

    @patch("labbstart.cli.handlers.new_handler.run_command")
    @pytest.mark.parametrize(
        "django_version,expected_python",
        [("4.2", "3.10"), ("5.0", "3.10"), ("6.0", "3.12")],
    )
    def test_setup_uv_python_version_full_matrix(
        self, mock_run_command, django_version, expected_python
    ):
        """Test that uv init receives the correct --python flag for each Django version"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            pyproject_file = project_path / "pyproject.toml"

            def mock_command(*args, **kwargs):
                if "init" in args[0]:
                    pyproject_file.write_text(
                        f'[project]\nname = "test"\nrequires-python = ">={expected_python}"\n'
                    )
                return True

            mock_run_command.side_effect = mock_command
            setup_uv_project(project_path, django_version)

            init_call = mock_run_command.call_args_list[0]
            assert expected_python in init_call[0][0], (
                f"uv init for Django {django_version} should use Python {expected_python}"
            )
            content = pyproject_file.read_text()
            assert f">={expected_python}" in content


# ============================================================================
# Test Install Labb Packages
# ============================================================================


class TestInstallLabbPackages:
    """Test labb package installation for different package managers"""

    @patch("labbstart.cli.handlers.new_handler.run_command")
    def test_install_labb_poetry(self, mock_run_command):
        """Test labb installation with poetry"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            mock_run_command.return_value = True

            result = install_labb_packages(project_path, "poetry")

            assert result is True
            # Check that poetry add was called with labbui and labbicons
            call_args = mock_run_command.call_args[0][0]
            assert "poetry" in call_args
            assert "add" in call_args
            assert "labbui" in call_args
            assert "labbicons" in call_args

    @patch("labbstart.cli.handlers.new_handler.run_command")
    @patch("labbstart.cli.handlers.new_handler.sys")
    def test_install_labb_pip_unix(self, mock_sys, mock_run_command):
        """Test labb installation with pip on Unix"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            mock_sys.platform = "linux"
            mock_run_command.return_value = True

            # Create venv structure
            venv_bin = project_path / "venv" / "bin"
            venv_bin.mkdir(parents=True)
            (venv_bin / "pip").touch()

            # Create requirements.txt
            (project_path / "requirements.txt").write_text("django~=5.0\n")

            result = install_labb_packages(project_path, "pip")

            assert result is True
            # Check requirements.txt was updated
            requirements = project_path / "requirements.txt"
            content = requirements.read_text()
            assert "labbui" in content
            assert "labbicons" in content

    @patch("labbstart.cli.handlers.new_handler.run_command")
    @patch("labbstart.cli.handlers.new_handler.sys")
    def test_install_labb_pip_windows(self, mock_sys, mock_run_command):
        """Test labb installation with pip on Windows"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            mock_sys.platform = "win32"
            mock_run_command.return_value = True

            # Create venv structure
            venv_scripts = project_path / "venv" / "Scripts"
            venv_scripts.mkdir(parents=True)
            (venv_scripts / "pip").touch()

            (project_path / "requirements.txt").write_text("django~=5.0\n")

            result = install_labb_packages(project_path, "pip")

            assert result is True

    @patch("labbstart.cli.handlers.new_handler.run_command")
    def test_install_labb_uv(self, mock_run_command):
        """Test labb installation with uv"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            mock_run_command.return_value = True

            result = install_labb_packages(project_path, "uv")

            assert result is True
            call_args = mock_run_command.call_args[0][0]
            assert "uv" in call_args
            assert "add" in call_args
            assert "labbui" in call_args
            assert "labbicons" in call_args

    @patch("labbstart.cli.handlers.new_handler.run_command")
    def test_install_labb_unknown_manager(self, mock_run_command):
        """Test labb installation with unknown package manager"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            result = install_labb_packages(project_path, "unknown")

            assert result is False


# ============================================================================
# Test Django File Updates
# ============================================================================


class TestUpdateSettingsPy:
    """Test Django settings.py updates"""

    def test_update_settings_adds_apps(self):
        """Test that settings.py is updated with labb apps"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            project_name = "testproject"
            settings_dir = project_path / project_name
            settings_dir.mkdir()

            settings_file = settings_dir / "settings.py"
            settings_file.write_text(
                """
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
]
"""
            )

            result = update_settings_py(project_path, project_name, "starter")

            assert result is True
            content = settings_file.read_text()
            assert "labb" in content
            assert "labbicons" in content
            assert "django_cotton" in content
            assert "starter" in content

    def test_update_settings_adds_staticfiles_dirs(self):
        """Test that STATICFILES_DIRS is added"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            project_name = "testproject"
            settings_dir = project_path / project_name
            settings_dir.mkdir()

            settings_file = settings_dir / "settings.py"
            settings_file.write_text(
                """
INSTALLED_APPS = [
    'django.contrib.admin',
]

STATIC_URL = "static/"
"""
            )

            result = update_settings_py(project_path, project_name, "starter")

            assert result is True
            content = settings_file.read_text()
            assert "STATICFILES_DIRS" in content
            assert "BASE_DIR" in content

    def test_update_settings_missing_file(self):
        """Test handling of missing settings.py"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            result = update_settings_py(project_path, "nonexistent", "starter")
            assert result is False

    def test_update_settings_missing_installed_apps(self):
        """Test handling of settings.py without INSTALLED_APPS"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            project_name = "testproject"
            settings_dir = project_path / project_name
            settings_dir.mkdir()

            settings_file = settings_dir / "settings.py"
            settings_file.write_text("DEBUG = True\n")

            result = update_settings_py(project_path, project_name, "starter")

            assert result is False


class TestUpdateUrlsPy:
    """Test Django urls.py updates"""

    def test_update_urls_adds_include_to_existing_import(self):
        """Test that include is added to existing django.urls import"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            project_name = "testproject"
            urls_dir = project_path / project_name
            urls_dir.mkdir()

            urls_file = urls_dir / "urls.py"
            urls_file.write_text(
                """
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]
"""
            )

            result = update_urls_py(project_path, project_name, "starter")

            assert result is True
            content = urls_file.read_text()
            assert "include" in content
            assert 'include("starter.urls")' in content

    def test_update_urls_creates_import_if_missing(self):
        """Test that django.urls import is created if missing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            project_name = "testproject"
            urls_dir = project_path / project_name
            urls_dir.mkdir()

            urls_file = urls_dir / "urls.py"
            urls_file.write_text(
                """
from django.contrib import admin

urlpatterns = [
]
"""
            )

            result = update_urls_py(project_path, project_name, "myapp")

            assert result is True
            content = urls_file.read_text()
            assert "from django.urls import" in content
            assert "include" in content

    def test_update_urls_missing_file(self):
        """Test handling of missing urls.py"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            result = update_urls_py(project_path, "nonexistent", "starter")
            assert result is False

    def test_update_urls_missing_urlpatterns(self):
        """Test handling of urls.py without urlpatterns"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            project_name = "testproject"
            urls_dir = project_path / project_name
            urls_dir.mkdir()

            urls_file = urls_dir / "urls.py"
            urls_file.write_text("from django.contrib import admin\n")

            result = update_urls_py(project_path, project_name, "starter")

            assert result is False


# ============================================================================
# Test Gitignore and README Creation
# ============================================================================


class TestGitignoreCreation:
    """Test .gitignore file creation"""

    @patch("labbstart.cli.handlers.new_handler.console")
    def test_create_gitignore(self, mock_console):
        """Test that .gitignore is created with proper content"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            result = create_gitignore(project_path)

            assert result is True
            gitignore = project_path / ".gitignore"
            assert gitignore.exists()

            content = gitignore.read_text()
            # Check for important entries
            assert "__pycache__/" in content
            assert "venv/" in content
            assert "*.py[cod]" in content or "*.pyc" in content
            assert "db.sqlite3" in content
            assert ".env" in content
            assert "node_modules/" in content
            assert ".DS_Store" in content


class TestReadmeCreation:
    """Test README.md creation"""

    def test_create_readme_poetry(self):
        """Test README creation for poetry project"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            result = create_project_readme(
                project_path, "testproject", "starter", "poetry"
            )

            assert result is True
            readme = project_path / "README.md"
            assert readme.exists()

            content = readme.read_text()
            assert "testproject" in content
            assert "poetry run" in content
            assert "starter" in content
            assert "labb dev" in content
            assert "manage.py runserver" in content

    def test_create_readme_pip(self):
        """Test README creation for pip project"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            result = create_project_readme(
                project_path, "testproject", "starter", "pip"
            )

            assert result is True
            readme = project_path / "README.md"
            content = readme.read_text()
            assert "venv/bin/activate" in content

    def test_create_readme_uv(self):
        """Test README creation for uv project"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            result = create_project_readme(project_path, "testproject", "starter", "uv")

            assert result is True
            readme = project_path / "README.md"
            content = readme.read_text()
            assert "uv run" in content

    def test_create_readme_with_kit(self):
        """Test README creation with kit template"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            # Note: This tests the fallback to default README
            # since kit templates aren't available in test environment
            result = create_project_readme(
                project_path, "myproject", "myapp", "poetry", kit_name="welcome"
            )

            assert result is True
            readme = project_path / "README.md"
            assert readme.exists()


# ============================================================================
# Test Kit Operations
# ============================================================================


class TestCopyKitToProject:
    """Test kit copying functionality"""

    def test_copy_kit_nonexistent(self):
        """Test handling of non-existent kit"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            result = copy_kit_to_project(project_path, "nonexistent_kit", "starter")
            assert result is False

    def test_copy_kit_renames_static_to_app_name(self):
        """Test that static/welcome is renamed to static/<app_name> and references updated"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            result = copy_kit_to_project(project_path, "welcome", "starter")
            assert result is True
            app_dest = project_path / "starter"
            assert app_dest.exists()
            # Static files should be under static/starter/, not static/welcome/
            assert (app_dest / "static" / "starter").exists()
            assert not (app_dest / "static" / "welcome").exists()
            # urls.py should use app name
            urls_content = (app_dest / "urls.py").read_text()
            assert 'app_name = "starter"' in urls_content
            # base.html should reference starter for static and url
            base_html = app_dest / "templates" / "cotton" / "layouts" / "base.html"
            base_content = base_html.read_text()
            assert "{% static 'starter/" in base_content
            assert "{% url 'starter:set_theme' %}" in base_content
            # site.webmanifest should use /static/starter/
            manifest = (
                app_dest
                / "static"
                / "starter"
                / "img"
                / "labb"
                / "favicon"
                / "site.webmanifest"
            )
            assert manifest.exists()
            manifest_content = manifest.read_text()
            assert "/static/starter/" in manifest_content


class TestAppendKitStyles:
    """Test kit style appending"""

    def test_append_kit_styles_no_extrastyle(self):
        """Test appending when kit has no extrastyle.css"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            result = append_kit_styles(project_path, "nonexistent_kit")
            # Should return True even if no extrastyle (not an error)
            assert result is True


# ============================================================================
# Test Constants
# ============================================================================


class TestConstants:
    """Test that constants are properly defined"""

    def test_django_versions(self):
        """Test DJANGO_VERSIONS constant"""
        assert 4 in DJANGO_VERSIONS
        assert 5 in DJANGO_VERSIONS
        assert 6 in DJANGO_VERSIONS
        assert DJANGO_VERSIONS[4] == "4.2"
        assert DJANGO_VERSIONS[5] == "5.0"
        assert DJANGO_VERSIONS[6] == "6.0"

    def test_package_managers(self):
        """Test PACKAGE_MANAGERS constant"""
        assert "poetry" in PACKAGE_MANAGERS
        assert "pip" in PACKAGE_MANAGERS
        assert "uv" in PACKAGE_MANAGERS

    def test_available_kits(self):
        """Test AVAILABLE_KITS constant"""
        assert "welcome" in AVAILABLE_KITS

    def test_django_min_python(self):
        """Test that every DJANGO_VERSIONS entry has a DJANGO_MIN_PYTHON mapping"""
        for version_str in DJANGO_VERSIONS.values():
            assert version_str in DJANGO_MIN_PYTHON, (
                f"Django {version_str} missing from DJANGO_MIN_PYTHON"
            )

    def test_django_min_python_values(self):
        """Test DJANGO_MIN_PYTHON maps to the correct minimum Python versions"""
        assert DJANGO_MIN_PYTHON["4.2"] == "3.10"
        assert DJANGO_MIN_PYTHON["5.0"] == "3.10"
        assert DJANGO_MIN_PYTHON["6.0"] == "3.12"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
