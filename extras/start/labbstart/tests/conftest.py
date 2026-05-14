"""Test fixtures for labbstart integration tests."""

from pathlib import Path

import pytest

from labbstart.cli.handlers import new_handler

# tests/conftest.py → labbstart/ → start/ → extras/ → repo root (labbui source).
_REPO_ROOT = Path(__file__).resolve().parents[4]
_LABBUI_SRC = _REPO_ROOT
_LABBICONS_SRC = _REPO_ROOT / "extras" / "icons"


@pytest.fixture(autouse=True)
def install_labb_from_source(monkeypatch):
    """Use the branch's labbui/labbicons sources instead of PyPI releases."""

    real_run_command = new_handler.run_command
    labbui = _LABBUI_SRC.as_posix()
    labbicons = _LABBICONS_SRC.as_posix()

    def install_from_source(project_path, package_manager):
        if package_manager == "poetry":
            return real_run_command(
                ["poetry", "add", labbui, labbicons],
                cwd=project_path,
                clean_env=True,
            )
        if package_manager == "uv":
            return real_run_command(
                ["uv", "add", labbui, labbicons],
                cwd=project_path,
            )
        if package_manager == "pip":
            import sys as _sys

            venv_pip = (
                project_path
                / "venv"
                / ("Scripts" if _sys.platform == "win32" else "bin")
                / ("pip.exe" if _sys.platform == "win32" else "pip")
            )
            success = real_run_command(
                [str(venv_pip), "install", labbui, labbicons],
                cwd=project_path,
            )
            if success:
                requirements = project_path / "requirements.txt"
                content = requirements.read_text() if requirements.exists() else ""
                if "# Python" not in content:
                    content = f"# Python >=3.10,<4\n{content}"
                with open(requirements, "a") as f:
                    f.write(f"{labbui}\n{labbicons}\n")
            return success
        return False

    monkeypatch.setattr(new_handler, "install_labb_packages", install_from_source)
