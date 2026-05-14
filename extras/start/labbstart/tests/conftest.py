"""Test fixtures for labbstart integration tests."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from labbstart.cli.handlers import new_handler

# tests/conftest.py → labbstart/ → start/ → extras/ → repo root (labbui source).
_REPO_ROOT = Path(__file__).resolve().parents[4]
_LABBUI_SRC = _REPO_ROOT
_LABBICONS_SRC = _REPO_ROOT / "extras" / "icons"


@pytest.fixture(scope="session")
def labb_wheels(tmp_path_factory):
    """Build labbui + labbicons wheels from this branch once per session."""
    out = tmp_path_factory.mktemp("labb-wheels")
    for src in (_LABBUI_SRC, _LABBICONS_SRC):
        subprocess.run(
            [
                "poetry",
                "build",
                f"--project={src}",
                f"--output={out}",
                "--format=wheel",
            ],
            check=True,
            capture_output=True,
        )
    wheels = list(out.glob("*.whl"))
    labbui = next(w for w in wheels if w.name.startswith("labbui-"))
    labbicons = next(w for w in wheels if w.name.startswith("labbicons-"))
    return labbui, labbicons


@pytest.fixture(autouse=True)
def install_labb_from_source(monkeypatch, request):
    """Make install_labb_packages use the locally-built wheels so integration
    tests exercise this branch instead of the published PyPI release."""

    # Only patch for tests that need it — skip the unit suite to keep their
    # autouse fixture footprint zero.
    if "integration" not in request.keywords:
        return

    labbui, labbicons = request.getfixturevalue("labb_wheels")
    real_run_command = new_handler.run_command

    def install_from_wheels(project_path, package_manager):
        # Copy wheels into the project so package managers reference a stable
        # local path (poetry add stores the file path verbatim in pyproject.toml).
        dest_dir = project_path / "_labb_wheels"
        dest_dir.mkdir(exist_ok=True)
        local_labbui = dest_dir / labbui.name
        local_labbicons = dest_dir / labbicons.name
        shutil.copy(labbui, local_labbui)
        shutil.copy(labbicons, local_labbicons)

        if package_manager == "poetry":
            return real_run_command(
                ["poetry", "add", str(local_labbui), str(local_labbicons)],
                cwd=project_path,
                clean_env=True,
            )
        if package_manager == "uv":
            return real_run_command(
                ["uv", "add", str(local_labbui), str(local_labbicons)],
                cwd=project_path,
            )
        if package_manager == "pip":
            venv_pip = (
                project_path
                / "venv"
                / ("Scripts" if sys.platform == "win32" else "bin")
                / ("pip.exe" if sys.platform == "win32" else "pip")
            )
            success = real_run_command(
                [str(venv_pip), "install", str(local_labbui), str(local_labbicons)],
                cwd=project_path,
            )
            if success:
                requirements = project_path / "requirements.txt"
                content = requirements.read_text() if requirements.exists() else ""
                if "# Python" not in content:
                    content = f"# Python >=3.10,<4\n{content}"
                with open(requirements, "a") as f:
                    f.write(f"{local_labbui}\n{local_labbicons}\n")
            return success
        return False

    monkeypatch.setattr(new_handler, "install_labb_packages", install_from_wheels)
