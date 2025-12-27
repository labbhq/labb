import tempfile
from pathlib import Path
from unittest.mock import patch

import django
import pytest
import yaml
from django.conf import settings

from labb.components.registry import ComponentRegistry
from labb.config import LabbConfig, clear_config_cache


def pytest_configure():
    """Configure Django settings for all tests"""
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
                "django.contrib.sessions",
                "django_cotton",
                "labb",
                "labbicons",
            ],
            MIDDLEWARE=[
                "django.contrib.sessions.middleware.SessionMiddleware",
            ],
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [
                        Path(__file__).parent.parent / "templates",
                    ],
                    "APP_DIRS": True,
                    "OPTIONS": {
                        "context_processors": [
                            "django.template.context_processors.debug",
                            "django.template.context_processors.request",
                            "django.contrib.auth.context_processors.auth",
                        ],
                    },
                },
            ],
            SECRET_KEY="test-secret-key",
            SESSION_ENGINE="django.contrib.sessions.backends.cache",
            SESSION_CACHE_ALIAS="default",
            CACHES={
                "default": {
                    "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                }
            },
            LABB_SETTINGS={
                "DEFAULT_THEME": "labb-light",
            },
            USE_TZ=True,
        )
        django.setup()


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def config_data(temp_dir):
    return {
        "css": {
            "build": {
                "input": str(temp_dir / "static_src" / "input.css"),
                "output": str(temp_dir / "static" / "css" / "output.css"),
                "minify": True,
            },
            "scan": {
                "output": str(temp_dir / "static_src" / "labb-classes.txt"),
                "templates": ["templates/**/*.html", "*/templates/**/*.html"],
            },
        }
    }


@pytest.fixture
def config_file(temp_dir, config_data):
    config_path = temp_dir / "labb.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)
    return config_path


@pytest.fixture
def mock_config(temp_dir):
    config = LabbConfig()
    config.input_file = str(temp_dir / "static_src" / "input.css")
    config.output_file = str(temp_dir / "static" / "css" / "output.css")
    config.minify = True
    config.classes_output = str(temp_dir / "static_src" / "labb-classes.txt")
    config.template_patterns = ["templates/**/*.html"]
    return config


@pytest.fixture
def template_fixtures_dir():
    """Get the path to the template fixtures directory"""
    return Path(__file__).parent / "fixtures" / "templates"


@pytest.fixture
def template_files(template_fixtures_dir):
    """Return dict of template files keyed by name"""
    templates = {}
    for template_file in template_fixtures_dir.glob("*.html"):
        templates[template_file.stem] = template_file
    return templates


@pytest.fixture
def sample_template_content(template_files):
    """Get content from button_examples.html as default template content"""
    with open(template_files["button_examples"], "r") as f:
        return f.read()


@pytest.fixture
def mock_template_file(temp_dir):
    """Create a temporary template file with mixed component content for testing"""
    template_dir = temp_dir / "templates"
    template_dir.mkdir()
    template_file = template_dir / "test.html"
    template_content = """
    <html>
        <c-lb.button variant="primary" size="lg">Button</c-lb.button>
        <c-lb.drawer end id="test">
            <c-lb.drawer.toggle />
            <c-lb.drawer.content>Content</c-lb.drawer.content>
        </c-lb.drawer>
        <c-lb.menu direction="horizontal">Menu</c-lb.menu>
    </html>
    """
    with open(template_file, "w") as f:
        f.write(template_content)
    return template_file


@pytest.fixture
def multiple_template_files(temp_dir, template_files):
    """Create multiple template files in temp directory from fixtures"""
    template_dir = temp_dir / "templates"
    template_dir.mkdir()

    created_files = []
    for name, fixture_path in template_files.items():
        template_file = template_dir / f"{name}.html"
        with open(fixture_path, "r") as src, open(template_file, "w") as dst:
            dst.write(src.read())
        created_files.append(template_file)

    return created_files


@pytest.fixture
def mock_components_registry():
    registry = ComponentRegistry()
    return registry


@pytest.fixture
def components_yaml_content(mock_components_registry):
    """Load components configuration using ComponentRegistry"""

    return mock_components_registry.get_all_components()


@pytest.fixture
def mock_console():
    with patch("labb.cli.handlers.scan_handler.console") as mock:
        yield mock


@pytest.fixture
def django_project_dir(temp_dir):
    manage_py = temp_dir / "manage.py"
    manage_py.write_text("# Django manage.py")
    return temp_dir


@pytest.fixture(autouse=True)
def clear_labb_config_cache():
    clear_config_cache()
