---
title: Installation
description: "Install labb in new or existing Django projects: labbstart for greenfield apps, or pip install labbui with django-cotton. Tailwind CSS and daisyUI 5 ready."
keywords: "install labb django, labb django setup, django-cotton install, labbstart, pip labbui, tailwind django project"
---

{% load docs_tags %}

## New Django Project with labbstart

The fastest way to get started is with **labbstart**, which scaffolds a new Django project with labb pre-configured.

```bash
pip install labbstart
labbstart new
```

This interactively prompts you for project name, Django version, package manager, and starter kit. You can also pass flags directly:

```bash
labbstart new myproject --django-version 5 --package-manager poetry --kit welcome --app-name starter
```

Once created, start two terminals:

```bash
# Terminal 1 — CSS watcher
cd your-project-name && labb dev

# Terminal 2 — Django server
cd your-project-name && python manage.py runserver
```

Open [http://localhost:8000](http://localhost:8000) and you're ready to build.

---

## Existing Project

### Prerequisites

- Python 3.8+
- Django 4.2+

### Step 1: Install labb

```bash
pip install labbui
```

Or with Poetry:

```bash
poetry add labbui
```

### Step 2: Add to Django Settings

Add `labb` to your `INSTALLED_APPS`:

<c-lbdocs.codeblock.title title="settings.py">
```python
INSTALLED_APPS = [
    # ... other apps
    'django_cotton',
    'labb',
]
```
</c-lbdocs.codeblock.title>

This automatically configures the required template loader and templatetags.

<c-lb.collapse title="Custom configuration" class="my-4" style="arrow">
If your project uses non-default loaders or you don't want Cotton to manage your settings, use `django_cotton.apps.SimpleAppConfig` instead:

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
</c-lb.collapse>

### Step 3: Initialize and Set Up

```bash
labb init --defaults
labb setup
```

`labb init` creates the project configuration and structure. `labb setup` installs the required Node.js dependencies.

### Step 4: Add Dependencies to Your Template

Add `<c-lb.m.dependencies />` to your base template's `<head>` section:

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
    <c-lb.m.dependencies setThemeEndpoint="{% url 'set_theme' %}" />
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
```
{% endverbatim %}
</c-lbdocs.codeblock.title>

<c-lb.alert variant="warning" alertStyle="outline" class="mt-4">
<span>Without `<c-lb.m.dependencies />`, components will not have the correct styling and interactive features may not work.</span>
</c-lb.alert>

### Step 5: Start Developing

Start two terminals:

```bash
# Terminal 1 — CSS watcher
labb dev

# Terminal 2 — Django server
python manage.py runserver
```

---

## Basic Usage

Use labb components in your templates with HTML-like syntax:

<c-lbdocs.codeblock.title title="templates/example.html">
{% verbatim %}
```html
<c-lb.button variant="primary">Click me</c-lb.button>

<c-lb.card>
    <c-lb.card.body>
        <c-lb.card.title>Card Title</c-lb.card.title>
        <p>Card content goes here</p>
    </c-lb.card.body>
</c-lb.card>

<c-lb.alert variant="success">Success message!</c-lb.alert>
```
{% endverbatim %}
</c-lbdocs.codeblock.title>

Browse <a href="{% doc_url '1_actions/button.md' 'ui' %}">component documentation</a> for all available components.

### Reactive Components

Add `.x` to any component name to get a reactive twin. Props can be changed at runtime using Alpine.js:

<c-lbdocs.codeblock.title title="templates/example.html">
{% verbatim %}
```html
<div x-data="{ btn: { variant: 'primary' } }">
    <c-lb.button.x x-model="btn" variant="primary">
        <span x-text="btn.variant"></span> button
    </c-lb.button.x>

    <c-lb.button variant="ghost" @click="btn.variant = 'success'">Change</c-lb.button>
</div>
```
{% endverbatim %}
</c-lbdocs.codeblock.title>

See the <a href="{% doc_url '2_concepts/1_reactivity.md' 'guide' %}">Reactivity guide</a> for the full picture.

## Next Steps

- <a href="{% doc_url '2_concepts/2_theming.md' 'guide' %}">Theming</a> — Customize colors and themes
- <a href="{% doc_url '2_concepts/3_building_css.md' 'guide' %}">Building CSS</a> — CSS build process and production builds
- <a href="{% doc_url '2_concepts/1_reactivity.md' 'guide' %}">Reactivity</a> — Add Alpine.js-powered interactivity to components with `.x` variants
- <a href="{% doc_url '3_references/0_labb_cli.md' 'guide' %}">CLI Reference</a> — Component inspection, icon search, and more
- <a href="{% doc_url '1_getting_started/1_introduction.md' 'icons' %}">Icons</a> — Install labbicons for 2,800+ Remix icons
