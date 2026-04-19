# labbdocs

**labbdocs** packages the [labb.io](https://labb.io/) documentation as a Django app: UI component reference, guides, icons, and blog — all powered by **labb**, **django-cotton**, **Tailwind CSS**, and **daisyUI 5**.

The public site at [https://labb.io/](https://labb.io/) runs this app alongside the labb marketing pages. Install **labbdocs** in your own Django project if you want to embed or mirror that docs experience.

## Install the labbdocs package

```bash
pip install labbdocs
```

## Integrate labbdocs into Django

### 1. Add labbdocs to INSTALLED_APPS

Add `labbdocs` to your Django project's `INSTALLED_APPS`:

```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'labbdocs',
]
```

### 2. Configure LABB_DOCS in settings

Set up your documentation configuration in Django settings:

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

### 3. Include labbdocs URLs

Add labbdocs URLs to your main URL configuration:

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    # ... other patterns
    path("", include("labbdocs.urls")),
]
```

### 4. Build documentation

Use the management command to build your documentation:

```bash
# Build all documentation
python manage.py build_docs ui
python manage.py build_docs icons

# Or build with quiet output
python manage.py build_docs ui --quiet
```
