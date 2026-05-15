import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

import questionary
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt

console = Console()

# Available options
DJANGO_VERSIONS = {4: "4.2", 5: "5.0", 6: "6.0"}
PACKAGE_MANAGERS = ["poetry", "pip", "uv"]
AVAILABLE_KITS = ["welcome"]

# Placeholder substituted with app name when copying a kit (e.g. __LABBSTART_APP_NAME__ -> "starter")
LABBSTART_APP_NAME_PLACEHOLDER = "__LABBSTART_APP_NAME__"


def validate_project_name(name: str) -> bool:
    """Validate project name follows Python package naming conventions"""
    if not name:
        return False
    # Must start with letter or underscore, contain only letters, numbers, underscores
    pattern = r"^[a-zA-Z_][a-zA-Z0-9_]*$"
    return bool(re.match(pattern, name))


def get_project_params(
    name: Optional[str],
    django_version: Optional[int],
    package_manager: Optional[str],
    kit: Optional[str],
    app_name: Optional[str],
) -> dict:
    """Get project parameters either from args or interactively"""

    # If all parameters are provided, use them
    if all([name, django_version, package_manager, kit, app_name]):
        return {
            "name": name,
            "django_version": django_version,
            "package_manager": package_manager,
            "kit": kit,
            "app_name": app_name,
        }

    # Interactive mode
    console.print(
        Panel.fit(
            "[bold cyan]🚀 Welcome to labbstart![/bold cyan]\n"
            "Let's create your new Django project with labb",
            border_style="cyan",
        )
    )

    # Get project name
    while True:
        if not name:
            name = Prompt.ask("\n[bold]Project name[/bold]", default="myproject")
        if validate_project_name(name):
            break
        console.print(
            "[red]Invalid project name. Must be a valid Python package name.[/red]"
        )
        name = None

    # Check if directory exists
    if Path(name).exists():
        console.print(f"[red]Directory '{name}' already exists![/red]")
        if not Confirm.ask("Overwrite existing directory?", default=False):
            console.print("[yellow]Aborted.[/yellow]")
            raise typer.Exit(0)
        shutil.rmtree(name)

    # Get Django version
    if not django_version:
        django_version = questionary.select(
            "Select Django version:",
            choices=[
                questionary.Choice("Django 4.2 (LTS)", value="4"),
                questionary.Choice("Django 5.x (Recommended)", value="5"),
                questionary.Choice("Django 6.x (Latest)", value="6"),
            ],
            default="5",
        ).ask()
        # Convert back to int
        django_version = int(django_version)

    # Get package manager
    if not package_manager:
        package_manager = questionary.select(
            "Select package manager:",
            choices=[
                questionary.Choice("poetry (Recommended)", value="poetry"),
                questionary.Choice("pip (Standard)", value="pip"),
                questionary.Choice("uv (Fast)", value="uv"),
            ],
            default="poetry",
        ).ask()

    # Get kit
    if not kit:
        kit = questionary.select(
            "Select starter kit:",
            choices=[
                questionary.Choice("welcome - Simple welcome page", value="welcome"),
            ],
            default="welcome",
        ).ask()

    # Get app name
    if not app_name:
        app_name = Prompt.ask(
            "\n[bold]Django app name for the kit[/bold]", default="starter"
        )

    return {
        "name": name,
        "django_version": django_version,
        "package_manager": package_manager,
        "kit": kit,
        "app_name": app_name,
    }


def run_command(
    cmd: list,
    cwd: Optional[Path] = None,
    env: Optional[dict] = None,
    clean_env: bool = False,
) -> bool:
    """Run a command and return success status"""
    try:
        # Prepare environment
        if clean_env:
            # Remove Poetry/virtualenv-related env vars to force fresh environment
            command_env = os.environ.copy()
            for var in ["VIRTUAL_ENV", "POETRY_ACTIVE", "PYTHONHOME"]:
                command_env.pop(var, None)
        else:
            command_env = env or os.environ.copy()

        result = subprocess.run(
            cmd,
            cwd=cwd,
            env=command_env,
            capture_output=True,
            text=True,
            check=False,
            shell=sys.platform == "win32",
        )
        if result.returncode != 0:
            # Include stdout — labb prints its errors via Rich, which writes to stdout.
            details = (result.stderr or "").strip()
            stdout = (result.stdout or "").strip()
            if stdout:
                details = f"{details}\n{stdout}" if details else stdout
            console.print(f"[red]Error: {details}[/red]")
            return False
        return True
    except Exception as e:
        console.print(f"[red]Error running command: {e}[/red]")
        return False


def setup_poetry_project(project_path: Path, django_version: str) -> bool:
    """Initialize project with poetry"""
    console.print("[cyan]Setting up poetry project...[/cyan]")

    # Create a dummy README.md to prevent poetry errors
    readme_file = project_path / "README.md"
    readme_file.write_text("# Project\n\nSetting up...\n")

    # Pin the Python constraint via pyproject.toml — passing "^3.10,<4" as an
    # argv arg breaks under shell=True on Windows because cmd.exe reads `<` as
    # input redirection.
    if not run_command(
        ["poetry", "init", "--no-interaction"],
        cwd=project_path,
        clean_env=True,
    ):
        return False

    pyproject_file = project_path / "pyproject.toml"
    if pyproject_file.exists():
        content = pyproject_file.read_text()
        if "[tool.poetry]" in content and "package-mode" not in content:
            content = content.replace(
                "[tool.poetry]", "[tool.poetry]\npackage-mode = false"
            )
        content = re.sub(
            r'(python\s*=\s*)"[^"]*"',
            r'\1"^3.10,<4"',
            content,
        )
        pyproject_file.write_text(content)

    # Configure poetry to create virtualenv in the project directory
    # This ensures a clean, isolated environment for the new project
    if not run_command(
        ["poetry", "config", "virtualenvs.in-project", "true", "--local"],
        cwd=project_path,
        clean_env=True,
    ):
        console.print("[yellow]Warning: Could not configure local virtualenv[/yellow]")

    # Add Django (with clean env to avoid using current active environment)
    if not run_command(
        ["poetry", "add", f"django~={django_version}"], cwd=project_path, clean_env=True
    ):
        return False

    # Ensure virtual environment is created by running install
    # This is necessary when running from within another Poetry environment
    if not run_command(
        ["poetry", "install", "--no-root"], cwd=project_path, clean_env=True
    ):
        console.print("[yellow]Warning: poetry install failed[/yellow]")

    return True


def setup_pip_project(project_path: Path, django_version: str) -> bool:
    """Initialize project with pip and venv"""
    console.print("[cyan]Setting up pip project with virtual environment...[/cyan]")

    # Create virtual environment
    venv_path = project_path / "venv"
    if not run_command([sys.executable, "-m", "venv", "venv"], cwd=project_path):
        return False

    # Determine pip path
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip.exe"
    else:
        pip_path = venv_path / "bin" / "pip"

    # Install Django
    if not run_command(
        [str(pip_path), "install", f"django~={django_version}"], cwd=project_path
    ):
        return False

    # Create requirements.txt with Python version comment
    requirements = project_path / "requirements.txt"
    requirements.write_text(f"# Python >=3.10,<4\ndjango~={django_version}\n")

    return True


def setup_uv_project(project_path: Path, django_version: str) -> bool:
    """Initialize project with uv"""
    console.print("[cyan]Setting up uv project...[/cyan]")

    # Initialize uv project with Python version constraint
    if not run_command(
        ["uv", "init", "--no-readme", "--python", "3.10"], cwd=project_path
    ):
        return False

    # Update pyproject.toml to set requires-python
    pyproject_file = project_path / "pyproject.toml"
    if pyproject_file.exists():
        content = pyproject_file.read_text()
        # Update or add requires-python
        if "requires-python" in content:
            content = re.sub(
                r'requires-python\s*=\s*"[^"]*"',
                'requires-python = ">=3.10,<4"',
                content,
            )
        else:
            # Add it after [project] section
            content = re.sub(
                r"(\[project\][^\[]*)", r'\1requires-python = ">=3.10,<4"\n', content
            )
        pyproject_file.write_text(content)

    # Add Django
    if not run_command(["uv", "add", f"django~={django_version}"], cwd=project_path):
        return False

    return True


def install_labb_packages(project_path: Path, package_manager: str) -> bool:
    """Install labbui and labbicons (labbui includes django-cotton)"""
    console.print("[cyan]Installing labbui and labbicons...[/cyan]")

    if package_manager == "poetry":
        return run_command(
            ["poetry", "add", "labbui", "labbicons"], cwd=project_path, clean_env=True
        )
    elif package_manager == "pip":
        venv_pip = (
            project_path
            / "venv"
            / ("Scripts" if sys.platform == "win32" else "bin")
            / ("pip.exe" if sys.platform == "win32" else "pip")
        )
        success = run_command(
            [str(venv_pip), "install", "labbui", "labbicons"], cwd=project_path
        )
        if success:
            # Update requirements.txt - prepend Python version if not already there
            requirements = project_path / "requirements.txt"
            content = requirements.read_text() if requirements.exists() else ""
            if "# Python" not in content:
                content = f"# Python >=3.10,<4\n{content}"
            with open(requirements, "a") as f:
                f.write("labbui\nlabbicons\n")
        return success
    elif package_manager == "uv":
        return run_command(["uv", "add", "labbui", "labbicons"], cwd=project_path)

    return False


def get_python_command(project_path: Path, package_manager: str) -> list:
    """Get the appropriate Python command for the package manager"""
    if package_manager == "poetry":
        # Use direct path to .venv python since we configured virtualenvs.in-project = true
        if sys.platform == "win32":
            return [str(project_path / ".venv" / "Scripts" / "python")]
        else:
            return [str(project_path / ".venv" / "bin" / "python")]
    elif package_manager == "pip":
        if sys.platform == "win32":
            return [str(project_path / "venv" / "Scripts" / "python")]
        else:
            return [str(project_path / "venv" / "bin" / "python")]
    elif package_manager == "uv":
        return ["uv", "run", "python"]

    return ["python"]


def _adapt_kit_to_app_name(app_dest: Path, app_name: str, kit_name: str) -> None:
    """Rename static/<kit_name> to static/<app_name> and substitute LABBSTART_APP_NAME_PLACEHOLDER in all files."""
    static_dir = app_dest / "static"
    kit_static = static_dir / kit_name
    app_static = static_dir / app_name
    if kit_static.exists() and kit_static.is_dir():
        app_static.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(kit_static), str(app_static))

    # Substitute placeholder with app_name in any file that might contain it
    text_extensions = (
        ".html",
        ".py",
        ".webmanifest",
        ".md",
        ".json",
        ".txt",
        ".yaml",
        ".yml",
    )
    for path in app_dest.rglob("*"):
        if path.is_file() and path.suffix.lower() in text_extensions:
            try:
                content = path.read_text(encoding="utf-8")
                if LABBSTART_APP_NAME_PLACEHOLDER in content:
                    path.write_text(
                        content.replace(LABBSTART_APP_NAME_PLACEHOLDER, app_name),
                        encoding="utf-8",
                    )
            except (OSError, UnicodeDecodeError):
                pass  # skip binary or unreadable files


def copy_kit_to_project(project_path: Path, kit_name: str, app_name: str) -> bool:
    """Copy kit files to project as a Django app"""
    console.print(f"[cyan]Adding '{kit_name}' kit as '{app_name}' app...[/cyan]")

    # Get kit source path
    kit_source = Path(__file__).parent.parent.parent / "kits" / kit_name
    if not kit_source.exists():
        console.print(f"[red]Kit '{kit_name}' not found![/red]")
        return False

    # Copy kit to project (excluding extrastyle.css)
    app_dest = project_path / app_name
    try:
        shutil.copytree(
            kit_source, app_dest, ignore=shutil.ignore_patterns("extrastyle.css")
        )

        # Create __init__.py if it doesn't exist
        init_file = app_dest / "__init__.py"
        if not init_file.exists():
            init_file.touch()

        # Update app name in files if needed
        apps_py = app_dest / "apps.py"
        if apps_py.exists():
            apps_py.write_text(
                f"from django.apps import AppConfig\n\n\n"
                f"class {app_name.capitalize()}Config(AppConfig):\n"
                f'    default_auto_field = "django.db.models.BigAutoField"\n'
                f'    name = "{app_name}"\n'
            )

        # Rename static/<kit_name> to static/<app_name> and update all references
        _adapt_kit_to_app_name(app_dest, app_name, kit_name)

        return True
    except Exception as e:
        console.print(f"[red]Error copying kit: {e}[/red]")
        return False


def update_settings_py(project_path: Path, project_name: str, app_name: str) -> bool:
    """Update Django settings.py to include labb and the kit app"""
    console.print("[cyan]Updating settings.py...[/cyan]")

    settings_file = project_path / project_name / "settings.py"
    if not settings_file.exists():
        console.print("[red]settings.py not found![/red]")
        return False

    content = settings_file.read_text()

    # Find INSTALLED_APPS
    apps_pattern = r"INSTALLED_APPS\s*=\s*\[(.*?)\]"
    match = re.search(apps_pattern, content, re.DOTALL)

    if not match:
        console.print("[red]Could not find INSTALLED_APPS in settings.py[/red]")
        return False

    # Add our apps
    apps_content = match.group(1)
    new_apps = f"""    # labb apps
    "labb",
    "labbicons",
    "django_cotton",
    "{app_name}",
"""

    # Insert before the closing bracket
    new_apps_section = f"INSTALLED_APPS = [{apps_content}{new_apps}]"
    content = content[: match.start()] + new_apps_section + content[match.end() :]

    # Add STATICFILES_DIRS configuration
    # Find where to insert it (after STATIC_URL or at the end)
    if "STATIC_URL" in content:
        # Add after STATIC_URL
        static_url_pattern = r"(STATIC_URL\s*=\s*['\"][^'\"]*['\"])"
        static_match = re.search(static_url_pattern, content)
        if static_match:
            staticfiles_dirs = """

# Static files directories
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
"""
            insert_pos = static_match.end()
            content = content[:insert_pos] + staticfiles_dirs + content[insert_pos:]
    else:
        # Add at the end if STATIC_URL not found
        staticfiles_dirs = """
# Static files configuration
STATIC_URL = "static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]
"""
        content += staticfiles_dirs

    settings_file.write_text(content)
    return True


def update_urls_py(project_path: Path, project_name: str, app_name: str) -> bool:
    """Update Django urls.py to include the kit app URLs"""
    console.print("[cyan]Updating urls.py...[/cyan]")

    urls_file = project_path / project_name / "urls.py"
    if not urls_file.exists():
        console.print("[red]urls.py not found![/red]")
        return False

    content = urls_file.read_text()

    # Check if django.urls import exists and if it includes 'include'
    # Match only actual import statements (not in comments/docstrings)
    # Look for the import at the beginning of a line (after optional whitespace)
    import_match = re.search(
        r"^from django\.urls import ([^\n]+)", content, re.MULTILINE
    )

    if import_match:
        # django.urls import exists, check if include is in it
        current_imports = import_match.group(1).strip()
        if "include" not in current_imports:
            # Add include to the imports
            new_imports = (
                f"include, {current_imports}" if current_imports else "include"
            )
            # Use re.sub to replace only the actual import line (not comments)
            content = re.sub(
                r"^from django\.urls import " + re.escape(current_imports),
                f"from django.urls import {new_imports}",
                content,
                count=1,
                flags=re.MULTILINE,
            )
    else:
        # No django.urls import at all, add it
        import_line = "from django.urls import include, path\n"
        if "from django.contrib import admin" in content:
            content = content.replace(
                "from django.contrib import admin",
                f"from django.contrib import admin\n{import_line}",
            )
        else:
            # Add at the beginning
            content = import_line + content

    # Find urlpatterns
    patterns_pattern = r"urlpatterns\s*=\s*\[(.*?)\]"
    match = re.search(patterns_pattern, content, re.DOTALL)

    if not match:
        console.print("[red]Could not find urlpatterns in urls.py[/red]")
        return False

    # Add our URL pattern at the beginning (before admin)
    patterns_content = match.group(1)
    new_pattern = f"""    path("", include("{app_name}.urls")),
"""

    new_patterns_section = f"urlpatterns = [{new_pattern}{patterns_content}]"
    content = content[: match.start()] + new_patterns_section + content[match.end() :]

    urls_file.write_text(content)
    return True


def append_kit_styles(project_path: Path, kit_name: str) -> bool:
    """Append kit's extrastyle.css to project's input.css if it exists"""
    # Get kit source path
    kit_source = Path(__file__).parent.parent.parent / "kits" / kit_name
    extrastyle_source = kit_source / "extrastyle.css"

    if extrastyle_source.exists():
        # Read the extra styles content
        extra_styles_content = extrastyle_source.read_text()

        # Append to input.css
        input_css = project_path / "static_src" / "input.css"
        if input_css.exists():
            content = input_css.read_text()
            # Append the extra styles to the end of input.css
            content += f"\n{extra_styles_content}\n"
            input_css.write_text(content)
            return True

    return True


def create_gitignore(project_path: Path) -> bool:
    """Create a .gitignore file for the project"""
    console.print("[cyan]Creating .gitignore...[/cyan]")

    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
/media
/staticfiles

# labb
node_modules/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Environment variables
.env
.env.local
"""

    gitignore_file = project_path / ".gitignore"
    gitignore_file.write_text(gitignore_content)
    return True


def create_project_readme(
    project_path: Path,
    project_name: str,
    app_name: str,
    package_manager: str,
    kit_name: Optional[str] = None,
) -> bool:
    """Create a README.md for the project"""
    console.print("[cyan]Creating README.md...[/cyan]")

    # Command prefix based on package manager
    if package_manager == "poetry":
        python_cmd = "poetry run python"
        labb_cmd = "poetry run labb"
    elif package_manager == "pip":
        python_cmd = "source venv/bin/activate && python"  # Unix
        labb_cmd = "source venv/bin/activate && labb"
    elif package_manager == "uv":
        python_cmd = "uv run python"
        labb_cmd = "uv run labb"

    # Check for kit-specific README template
    if kit_name:
        kit_source = Path(__file__).parent.parent.parent / "kits" / kit_name
        readme_template = kit_source / "README.md.template"
        if readme_template.exists():
            readme_content = readme_template.read_text()
            # Replace placeholders
            readme_content = readme_content.replace("{project_name}", project_name)
            readme_content = readme_content.replace("{app_name}", app_name)
            readme_content = readme_content.replace("{python_cmd}", python_cmd)
            readme_content = readme_content.replace("{labb_cmd}", labb_cmd)
            readme_file = project_path / "README.md"
            readme_file.write_text(readme_content)
            return True

    # Default README content
    readme_content = f"""# {project_name}

A Django project powered by [labb](https://labb.io) - the perfect Django UI components library.

## Getting Started

This project was created with `labbstart` and includes the `{app_name}` starter app.

### Development

You need to run two processes in separate terminals:

**Terminal 1 - CSS Development Server:**
```bash
{labb_cmd} dev
```

**Terminal 2 - Django Development Server:**
```bash
{python_cmd} manage.py runserver
```

Then visit `http://localhost:8000` to see your project!

### Project Structure

- `{project_name}/` - Django project settings
- `{app_name}/` - Your starter app with labb components
- `static/` - CSS output (generated by labb build)
- `static_src/` - CSS source files (Tailwind CSS)

### Available Commands

#### labb Commands

```bash
# Build CSS (one-time)
{labb_cmd} build

# Development mode (watch and rebuild CSS)
{labb_cmd} dev

# View configuration
{labb_cmd} config
```

#### Django Commands

```bash
# Run development server
{python_cmd} manage.py runserver

# Create migrations
{python_cmd} manage.py makemigrations

# Apply migrations
{python_cmd} manage.py migrate

# Create superuser
{python_cmd} manage.py createsuperuser
```

## Learn More

- [labb Documentation](https://labb.io/docs)
- [Django Documentation](https://docs.djangoproject.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [DaisyUI](https://daisyui.com/)

## License

This project is yours! Do whatever you want with it.
"""

    readme_file = project_path / "README.md"
    readme_file.write_text(readme_content)
    return True


def create_new_project(
    name: Optional[str],
    django_version: Optional[int],
    package_manager: Optional[str],
    kit: Optional[str],
    app_name: Optional[str],
):
    """Main function to create a new Django project with labb"""

    try:
        # Get all parameters
        params = get_project_params(
            name, django_version, package_manager, kit, app_name
        )

        project_name = params["name"]
        django_version_str = DJANGO_VERSIONS[params["django_version"]]
        pkg_mgr = params["package_manager"]
        kit_name = params["kit"]
        app_name_final = params["app_name"]

        # Create project directory
        project_path = Path.cwd() / project_name
        project_path.mkdir(exist_ok=True)

        console.print(
            f"\n[bold green]Creating project '{project_name}'...[/bold green]"
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Setup package manager
            task = progress.add_task("Setting up package manager...", total=None)
            if pkg_mgr == "poetry":
                if not setup_poetry_project(project_path, django_version_str):
                    raise Exception("Failed to setup poetry project")
            elif pkg_mgr == "pip":
                if not setup_pip_project(project_path, django_version_str):
                    raise Exception("Failed to setup pip project")
            elif pkg_mgr == "uv":
                if not setup_uv_project(project_path, django_version_str):
                    raise Exception("Failed to setup uv project")
            progress.remove_task(task)

            # Create Django project
            task = progress.add_task("Creating Django project...", total=None)
            python_cmd = get_python_command(project_path, pkg_mgr)
            django_admin_cmd = python_cmd + [
                "-m",
                "django",
                "startproject",
                project_name,
                ".",
            ]
            if not run_command(django_admin_cmd, cwd=project_path):
                raise Exception("Failed to create Django project")
            progress.remove_task(task)

            # Install labb packages (this also installs all dependencies)
            task = progress.add_task("Installing labbui and labbicons...", total=None)
            if not install_labb_packages(project_path, pkg_mgr):
                raise Exception("Failed to install labb packages")
            progress.remove_task(task)

            # Copy kit to project
            task = progress.add_task(f"Adding {kit_name} kit...", total=None)
            if not copy_kit_to_project(project_path, kit_name, app_name_final):
                raise Exception("Failed to copy kit")
            progress.remove_task(task)

            # Update settings.py
            task = progress.add_task("Configuring Django settings...", total=None)
            if not update_settings_py(project_path, project_name, app_name_final):
                raise Exception("Failed to update settings.py")
            progress.remove_task(task)

            # Update urls.py
            task = progress.add_task("Configuring URL routing...", total=None)
            if not update_urls_py(project_path, project_name, app_name_final):
                raise Exception("Failed to update urls.py")
            progress.remove_task(task)

            # Run labb init
            task = progress.add_task("Initializing labb...", total=None)
            if pkg_mgr == "poetry":
                labb_cmd = ["poetry", "run", "labb", "init", "--defaults"]
            elif pkg_mgr == "pip":
                labb_bin = (
                    project_path
                    / "venv"
                    / ("Scripts" if sys.platform == "win32" else "bin")
                    / ("labb.exe" if sys.platform == "win32" else "labb")
                )
                labb_cmd = [str(labb_bin), "init", "--defaults"]
            elif pkg_mgr == "uv":
                labb_cmd = ["uv", "run", "labb", "init", "--defaults"]

            # clean_env drops the outer VIRTUAL_ENV so the project venv is used.
            if not run_command(labb_cmd, cwd=project_path, clean_env=True):
                raise Exception("labb init failed")
            progress.remove_task(task)

            # Append kit styles to input.css (after labb init creates the file)
            task = progress.add_task("Adding kit styles...", total=None)
            append_kit_styles(project_path, kit_name)
            progress.remove_task(task)

            # Run labb setup
            task = progress.add_task("Setting up Tailwind CSS...", total=None)
            if pkg_mgr == "poetry":
                labb_setup_cmd = ["poetry", "run", "labb", "setup", "--install-deps"]
            elif pkg_mgr == "pip":
                labb_bin = (
                    project_path
                    / "venv"
                    / ("Scripts" if sys.platform == "win32" else "bin")
                    / ("labb.exe" if sys.platform == "win32" else "labb")
                )
                labb_setup_cmd = [str(labb_bin), "setup", "--install-deps"]
            elif pkg_mgr == "uv":
                labb_setup_cmd = ["uv", "run", "labb", "setup", "--install-deps"]

            if not run_command(labb_setup_cmd, cwd=project_path, clean_env=True):
                raise Exception("labb setup failed")
            progress.remove_task(task)

            # Run labb build
            task = progress.add_task("Building initial CSS...", total=None)
            if pkg_mgr == "poetry":
                labb_build_cmd = ["poetry", "run", "labb", "build"]
            elif pkg_mgr == "pip":
                labb_bin = (
                    project_path
                    / "venv"
                    / ("Scripts" if sys.platform == "win32" else "bin")
                    / ("labb.exe" if sys.platform == "win32" else "labb")
                )
                labb_build_cmd = [str(labb_bin), "build"]
            elif pkg_mgr == "uv":
                labb_build_cmd = ["uv", "run", "labb", "build"]

            if not run_command(labb_build_cmd, cwd=project_path, clean_env=True):
                raise Exception("labb build failed")
            progress.remove_task(task)

            # Run Django makemigrations
            task = progress.add_task("Running makemigrations...", total=None)
            python_cmd = get_python_command(project_path, pkg_mgr)
            makemigrations_cmd = python_cmd + ["manage.py", "makemigrations"]
            if not run_command(makemigrations_cmd, cwd=project_path, clean_env=True):
                raise Exception("Django makemigrations failed")
            progress.remove_task(task)

            # Run Django migrate
            task = progress.add_task("Running migrate...", total=None)
            migrate_cmd = python_cmd + ["manage.py", "migrate"]
            if not run_command(migrate_cmd, cwd=project_path, clean_env=True):
                raise Exception("Django migrate failed")
            progress.remove_task(task)

            # Create .gitignore
            task = progress.add_task("Creating .gitignore...", total=None)
            create_gitignore(project_path)
            progress.remove_task(task)

            # Create README
            task = progress.add_task("Creating README.md...", total=None)
            create_project_readme(
                project_path, project_name, app_name_final, pkg_mgr, kit_name
            )
            progress.remove_task(task)

        # Success message
        console.print("\n")

        # Determine commands based on package manager
        if pkg_mgr == "poetry":
            labb_dev_cmd = "poetry run labb dev"
            django_run_cmd = "poetry run python manage.py runserver"
        elif pkg_mgr == "uv":
            labb_dev_cmd = "uv run labb dev"
            django_run_cmd = "uv run python manage.py runserver"
        else:  # pip
            if sys.platform == "win32":
                labb_dev_cmd = "venv\\Scripts\\activate && labb dev"
                django_run_cmd = "venv\\Scripts\\activate && python manage.py runserver"
            else:
                labb_dev_cmd = "source venv/bin/activate && labb dev"
                django_run_cmd = (
                    "source venv/bin/activate && python manage.py runserver"
                )

        success_message = f"""[bold green]✨ Project '{project_name}' created successfully![/bold green]

[bold]Next steps:[/bold]

1. [bold]Navigate to your project:[/bold]
   [cyan]cd {project_name}[/cyan]

2. Start the development servers in [bold]separate terminals[/bold]:

   [bold]Terminal 1 - CSS Development Server:[/bold]
   [cyan]{labb_dev_cmd}[/cyan]

   [bold]Terminal 2 - Django Development Server:[/bold]
   [cyan]{django_run_cmd}[/cyan]

3. Open your browser:
   [cyan]http://localhost:8000[/cyan]

[dim]For more information, check out the README.md in your project directory.[/dim]
"""
        console.print(Panel(success_message, border_style="green", padding=(1, 2)))

    except typer.Exit:
        # User aborted or clean exit, just re-raise
        raise
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user.[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]Error creating project: {e}[/red]")
        raise typer.Exit(1)
