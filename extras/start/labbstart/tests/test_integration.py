"""Integration tests for labbstart CLI - creates real projects"""

import tempfile
from pathlib import Path

import pytest

from labbstart.cli.handlers.new_handler import create_new_project


def verify_project_structure(project_path: Path, project_name: str, app_name: str):
    """Verify that the created project has the expected structure"""
    # Django project directory
    assert (project_path / project_name).is_dir()
    assert (project_path / project_name / "settings.py").exists()
    assert (project_path / project_name / "urls.py").exists()
    assert (project_path / project_name / "wsgi.py").exists()

    # App directory
    assert (project_path / app_name).is_dir()
    assert (project_path / app_name / "views.py").exists()
    assert (project_path / app_name / "urls.py").exists()

    # Labb files
    assert (project_path / "static_src").is_dir()
    assert (project_path / "static_src" / "input.css").exists()
    assert (project_path / "static").is_dir()

    # Configuration files
    assert (project_path / ".gitignore").exists()
    assert (project_path / "README.md").exists()
    assert (project_path / "manage.py").exists()

    # Database should exist after migrations
    assert (project_path / "db.sqlite3").exists(), (
        "Database file should exist after migrations"
    )

    # CSS files should exist after build (in static/css/ subdirectory)
    css_files = list((project_path / "static").rglob("*.css"))
    assert len(css_files) > 0, "CSS files should exist in static directory after build"

    # Verify output.css specifically exists
    output_css = project_path / "static" / "css" / "output.css"
    assert output_css.exists(), "output.css should exist in static/css/ directory"
    assert output_css.stat().st_size > 0, "output.css should have content"


def verify_settings_py(project_path: Path, project_name: str, app_name: str):
    """Verify settings.py has correct configuration"""
    settings_file = project_path / project_name / "settings.py"
    content = settings_file.read_text()

    # Check that labb apps are installed
    assert "labb" in content
    assert "labbicons" in content
    assert "django_cotton" in content
    assert app_name in content

    # Check STATICFILES_DIRS
    assert "STATICFILES_DIRS" in content


def verify_urls_py(project_path: Path, project_name: str, app_name: str):
    """Verify urls.py has correct configuration"""
    urls_file = project_path / project_name / "urls.py"
    content = urls_file.read_text()

    # Check that include is imported
    assert "include" in content

    # Check that app URLs are included
    assert f"{app_name}.urls" in content


# Integration Tests


@pytest.mark.integration
def test_create_project_with_poetry():
    """Integration test: Create a real project with Poetry"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save current directory
        original_cwd = Path.cwd()

        try:
            # Change to temp directory
            import os

            os.chdir(tmpdir)

            # Create project with all parameters specified
            create_new_project(
                name="test_poetry_project",
                django_version=5,
                package_manager="poetry",
                kit="welcome",
                app_name="starter",
            )

            project_path = Path(tmpdir) / "test_poetry_project"

            # Verify project structure
            assert project_path.exists()
            verify_project_structure(project_path, "test_poetry_project", "starter")
            verify_settings_py(project_path, "test_poetry_project", "starter")
            verify_urls_py(project_path, "test_poetry_project", "starter")

            # Verify Poetry-specific files
            assert (project_path / "pyproject.toml").exists()
            assert (project_path / ".venv").is_dir()

            # Verify pyproject.toml content
            pyproject_content = (project_path / "pyproject.toml").read_text()
            assert "django" in pyproject_content.lower()
            assert "labbui" in pyproject_content.lower()
            # package-mode may be in [tool.poetry] or implicit in new [project] format
            # Either format is acceptable

        finally:
            # Restore original directory
            os.chdir(original_cwd)


@pytest.mark.integration
def test_create_project_with_uv():
    """Integration test: Create a real project with UV"""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = Path.cwd()

        try:
            import os

            os.chdir(tmpdir)

            # Create project with UV
            create_new_project(
                name="test_uv_project",
                django_version=5,
                package_manager="uv",
                kit="welcome",
                app_name="starter",
            )

            project_path = Path(tmpdir) / "test_uv_project"

            # Verify project structure
            assert project_path.exists()
            verify_project_structure(project_path, "test_uv_project", "starter")
            verify_settings_py(project_path, "test_uv_project", "starter")
            verify_urls_py(project_path, "test_uv_project", "starter")

            # Verify UV-specific files
            assert (project_path / "pyproject.toml").exists()
            assert (project_path / "uv.lock").exists()
            assert (project_path / ".venv").is_dir()

            # Verify pyproject.toml content
            pyproject_content = (project_path / "pyproject.toml").read_text()
            assert "django" in pyproject_content.lower()
            assert "labbui" in pyproject_content.lower()
            assert "requires-python" in pyproject_content

        finally:
            os.chdir(original_cwd)


@pytest.mark.integration
def test_create_project_with_pip():
    """Integration test: Create a real project with pip"""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = Path.cwd()

        try:
            import os

            os.chdir(tmpdir)

            # Create project with pip
            create_new_project(
                name="test_pip_project",
                django_version=5,
                package_manager="pip",
                kit="welcome",
                app_name="starter",
            )

            project_path = Path(tmpdir) / "test_pip_project"

            # Verify project structure
            assert project_path.exists()
            verify_project_structure(project_path, "test_pip_project", "starter")
            verify_settings_py(project_path, "test_pip_project", "starter")
            verify_urls_py(project_path, "test_pip_project", "starter")

            # Verify pip-specific files
            assert (project_path / "requirements.txt").exists()
            assert (project_path / "venv").is_dir()

            # Verify requirements.txt content
            requirements_content = (project_path / "requirements.txt").read_text()
            assert "django" in requirements_content.lower()
            assert "labbui" in requirements_content.lower()

        finally:
            os.chdir(original_cwd)


@pytest.mark.integration
def test_create_project_with_django_4():
    """Integration test: Create project with Django 4.2 (LTS)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = Path.cwd()

        try:
            import os

            os.chdir(tmpdir)

            create_new_project(
                name="test_django4_project",
                django_version=4,  # Django 4.2
                package_manager="poetry",
                kit="welcome",
                app_name="starter",
            )

            project_path = Path(tmpdir) / "test_django4_project"

            # Verify project was created
            assert project_path.exists()
            verify_project_structure(project_path, "test_django4_project", "starter")

            # Verify Django 4.2 is in dependencies
            pyproject_content = (project_path / "pyproject.toml").read_text()
            assert "django" in pyproject_content.lower()
            # Django 4.2 should be specified
            assert "4.2" in pyproject_content

        finally:
            os.chdir(original_cwd)


@pytest.mark.integration
def test_css_build_successful():
    """Integration test: Verify that CSS build process runs and produces output"""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = Path.cwd()

        try:
            import os

            os.chdir(tmpdir)

            create_new_project(
                name="test_css_project",
                django_version=5,
                package_manager="poetry",
                kit="welcome",
                app_name="starter",
            )

            project_path = Path(tmpdir) / "test_css_project"

            # Verify static directory structure exists
            static_dir = project_path / "static"
            assert static_dir.exists(), "Static directory should exist"

            static_src_dir = project_path / "static_src"
            assert static_src_dir.exists(), "Static source directory should exist"
            assert (static_src_dir / "input.css").exists(), "input.css should exist"

            # CSS files MUST be present after build (in static/css/ subdirectory)
            css_files = list(static_dir.rglob("*.css"))
            assert len(css_files) > 0, (
                "CSS build should produce output files in static directory"
            )

            # Verify output.css specifically exists and has content
            output_css = project_path / "static" / "css" / "output.css"
            assert output_css.exists(), (
                "output.css should exist in static/css/ directory"
            )
            assert output_css.stat().st_size > 0, "output.css should have content"

        finally:
            os.chdir(original_cwd)


@pytest.mark.integration
def test_custom_app_name():
    """Integration test: Create project with custom app name"""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = Path.cwd()

        try:
            import os

            os.chdir(tmpdir)

            create_new_project(
                name="test_custom_app",
                django_version=5,
                package_manager="poetry",
                kit="welcome",
                app_name="myapp",  # Custom app name
            )

            project_path = Path(tmpdir) / "test_custom_app"

            # Verify custom app directory exists
            assert (project_path / "myapp").is_dir()
            assert (project_path / "myapp" / "views.py").exists()

            # Verify app is in settings
            verify_settings_py(project_path, "test_custom_app", "myapp")
            verify_urls_py(project_path, "test_custom_app", "myapp")

        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
