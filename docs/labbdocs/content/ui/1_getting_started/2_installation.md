---
title: Installation
description: How to install and set up labb in your Django project
---

## Prerequisites

Before installing labb, make sure you have:

- Django 4.2 or higher
- Python 3.8 or higher

## Install labb

### Using pip

```bash
pip install labbui
```

### Using Poetry

```bash
poetry add labbui
```

## Add to Django Settings

Add `labb` to your `INSTALLED_APPS` in your Django settings:

### Automatic configuration:

<c-lbdocs.codeblock.title title="settings.py">
```python
INSTALLED_APPS = [
    # ... other apps
    'django_cotton',
    'labb',
]
```
</c-lbdocs.codeblock.title>

This will attempt to automatically handle the settings.py by adding the required loader and templatetags.

### Custom configuration

If your project requires any non-default loaders or you do not wish Cotton to manage your settings, you should instead provide `django_cotton.apps.SimpleAppConfig` in your INSTALLED_APPS:

<c-lbdocs.codeblock.title title="settings.py">
```python
INSTALLED_APPS = [
    # ... other apps
    'django_cotton.apps.SimpleAppConfig',
    'labb',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': False,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                (
                    'django.template.loaders.cached.Loader',
                    [
                        'django_cotton.cotton_loader.Loader',
                        'django.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader',
                    ],
                )
            ],
            'builtins': [
                'django_cotton.templatetags.cotton',
            ],
        },
    },
]
```
</c-lbdocs.codeblock.title>

## Initialize labb Project

After adding labb to your Django settings, you need to initialize and set up labb in your project:

### Step 1: Initialize Project

Initialize labb project with configuration and project structure:

```bash
labb init
```

For quick setup with defaults:

```bash
labb init --defaults
```

**Init Options:**

```bash
# Force overwrite existing files created by labb init
labb init --force
```
### Step 2: Install Dependencies

Install the required Node.js dependencies:

```bash
labb setup
```

**Setup Options:**

```bash
# Install dependencies automatically
labb setup --install-deps

# Skip dependency installation
labb setup --no-install-deps
```

## Add Dependencies to Your Template

<c-lb.alert variant="info" style="soft" icon="rmx.information" iconFill class="mb-4">
<span>Add `<c-lb.m.dependencies />` to your main HTML template's `<head>` section. This includes the required CSS and JavaScript for labb components to work properly.</span>
</c-lb.alert>

<c-lbdocs.codeblock.title title="templates/base.html">
{% verbatim %}
```html
{% load lb_tags %}

<!DOCTYPE html>
<html lang="en" {% labb_theme %}>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My labb App</title>

    <!-- Required: Add labb dependencies -->
    <c-lb.m.dependencies setThemeEndpoint="{% url 'set_theme' %}" />
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
```
{% endverbatim %}
</c-lbdocs.codeblock.title>

<c-lb.alert variant="warning" style="outline" class="mt-4">
<span>Without `<c-lb.m.dependencies />`, components will not have the correct styling and interactive features may not work.</span>
</c-lb.alert>

## Basic Usage

Once installed and setup, you can start using components in your templates.

First, start the labb development watcher to monitor changes and build CSS:

```bash
labb dev
```

This will start both CSS building and template scanning in watch mode. Keep this running while you develop.

Next, in a **separate terminal**, start your Django development server:

```bash
python manage.py runserver
```

Now you can create templates with labb components:

<c-lbdocs.codeblock.title title="templates/example.html">
{% verbatim %}
```html
{% extends "base.html" %}

{% block content %}
    <!-- Basic button -->
    <c-lb.button variant="primary">Click me</c-lb.button>

    <!-- Card component -->
    <c-lb.card>
      <c-lb.card.body>
        <c-lb.card.title>Card Title</c-lb.card.title>
        <p>Card content goes here</p>
      </c-lb.card.body>
    </c-lb.card>
{% endblock %}
```
{% endverbatim %}
</c-lbdocs.codeblock.title>

## Next Steps

Head to the <a href="{% doc_url '1_getting_started/3_quick_start.md' 'ui' %}">Quick Start guide</a> for a concise step-by-step overview of using labb.
