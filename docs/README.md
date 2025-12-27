# labbdocs

The documentation is available online at [https://labb.io/docs](https://labb.io/docs).

This documentation is installed as a django app in the django project that powers the [labb.io](https://labb.io) website.

## Installation

```bash
pip install labbdocs
```

## Integration with a django site

### 1. Add to INSTALLED_APPS

Add `labbdocs` to your Django project's `INSTALLED_APPS`:

```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'labbdocs',
]
```

### 2. Configure LABB_DOCS

Set up your documentation configuration in your Django settings:

```python
# settings.py
LABB_DOCS = {
    "ui": {
        "config": "/path/to/your/ui.yaml",
        "title": "UI Components",
        "name": "ui",
        "url_prefix": "/docs/ui",
        "template_dir": "labbdocs/docs/ui/",
        "build_path": "/path/to/templates/build/docs/ui"
    },
    "icons": {
        "config": "/path/to/your/icons.yaml",
        "title": "Icon Library",
        "name": "icons",
        "url_prefix": "/docs/icons",
        "template_dir": "labbdocs/docs/icons/",
        "build_path": "/path/to/templates/build/docs/icons"
    }
}
```

### 3. Include URLs

Add labbdocs URLs to your main URL configuration:

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    # ... other patterns
    path("", include("labbdocs.urls")),
]
```

### 4. Build Documentation

Use the management command to build your documentation:

```bash
# Build all documentation
python manage.py build_docs ui
python manage.py build_docs icons

# Or build with quiet output
python manage.py build_docs ui --quiet
```
