---
title: Installation
description: "Install labb in new or existing Django projects: labbstart for greenfield apps, or pip install labbui with django-cotton. Tailwind CSS and daisyUI 5 ready."
keywords: "install labb django, labb django setup, django-cotton install, labbstart, pip labbui, tailwind django project"
---

{% load docs_tags %}

labb installs in two ways. Start a brand new project with **labbstart**, which scaffolds everything for you, or add labb to an existing Django project with pip. Pick the track that fits below.

**Prerequisites:** Python 3.8+ and Django 4.2+.

## Set up your project

<c-lb.tabs name="install_track" style="border" size="sm" class="mt-4">

<c-lb.tabs.content name="install_track" title="New project" checked="true" class="pt-6">

<c-lbdocs.steps>

<c-lbdocs.steps.step number="1" title="Install labbstart">

**labbstart** scaffolds a new Django project with labb already configured.

```bash
pip install labbstart
```

</c-lbdocs.steps.step>

<c-lbdocs.steps.step number="2" title="Scaffold your project">

Run the generator. It prompts for the project name, Django version, package manager, and starter kit:

```bash
labbstart new
```

Or pass the choices as flags:

```bash
labbstart new myproject --django-version 5 --package-manager poetry --kit welcome --app-name starter
```

</c-lbdocs.steps.step>

<c-lbdocs.steps.step number="3" title="Run it">

Start two terminals: the CSS watcher and the Django server.

```bash
# Terminal 1: CSS watcher
cd your-project-name && labb dev

# Terminal 2: Django server
cd your-project-name && python manage.py runserver
```

</c-lbdocs.steps.step>

<c-lbdocs.steps.step number="4" title="Open localhost" last>

Visit [http://localhost:8000](http://localhost:8000) and you are ready to build.

</c-lbdocs.steps.step>

</c-lbdocs.steps>

</c-lb.tabs.content>

<c-lb.tabs.content name="install_track" title="Existing project" class="pt-6">

<c-lbdocs.steps>

<c-lbdocs.steps.step number="1" title="Install labbui">

```bash
pip install labbui
```

Or with Poetry:

```bash
poetry add labbui
```

</c-lbdocs.steps.step>

<c-lbdocs.steps.step number="2" title="Add to Django settings">

Add `labb` to your `INSTALLED_APPS`. This automatically configures the required template loader and templatetags.

<c-lbdocs.codeblock.title title="settings.py">
```python
INSTALLED_APPS = [
    # ... other apps
    'django_cotton',
    'labb',
]
```
</c-lbdocs.codeblock.title>

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

</c-lbdocs.steps.step>

<c-lbdocs.steps.step number="3" title="Set up Tailwind and daisyUI">

Initialize the project and install the Node.js dependencies that power the CSS build:

```bash
labb init --defaults
labb setup
```

`labb init` creates the project configuration and structure. `labb setup` installs the required Node.js dependencies.

Add `<c-lb.m.dependencies />` to your base template's `<head>`:

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

Keep the CSS watcher running while you develop:

```bash
labb dev
```

<c-lb.collapse title="Add icons (optional)" class="my-4" style="arrow">
To use icons in your components, install **labbicons**:

```bash
pip install labbicons
# or together with labb
pip install labbui[icons]
```

Add `labbicons` to `INSTALLED_APPS`:

<c-lbdocs.codeblock.title title="settings.py">
```python
INSTALLED_APPS = [
    # ... other apps
    'django_cotton',
    'labb',
    'labbicons',
]
```
</c-lbdocs.codeblock.title>

Then use icons in any component that accepts an `icon` prop, or directly:

```html
<c-lb.button icon="rmx.heart">Like</c-lb.button>
<c-lbi.rmx.heart w="24" h="24" />
```

See the <a href="{% doc_url '1_getting_started/5_icons.md' 'guide' %}">Icons guide</a> for the full reference.
</c-lb.collapse>

</c-lbdocs.steps.step>

<c-lbdocs.steps.step number="4" title="Write your first component" last>

Start the Django server in a second terminal:

```bash
python manage.py runserver
```

Then use labb components in your templates with HTML-like syntax:

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

Browse the <a href="{% doc_url '1_actions/button.md' 'ui' %}">component documentation</a> for everything available.

</c-lbdocs.steps.step>

</c-lbdocs.steps>

</c-lb.tabs.content>

</c-lb.tabs>

## Reactive components

Make any component prop reactive by binding it to a signal. Declare the signal, then change it from the page:

<c-lbdocs.codeblock.title title="templates/example.html">
```html
<c-lbr.signals $variant="primary" />

<c-lb.button variant="$variant:primary">
    <span data-text="$variant"></span> button
</c-lb.button>

<c-lb.button btnStyle="ghost" data-on:click="$variant = 'success'">Change</c-lb.button>
```
</c-lbdocs.codeblock.title>

See the <a href="{% doc_url '3_reactivity/1_overview.md' 'guide' %}">Reactivity guide</a> for the full picture.

## Next Steps

- <a href="{% doc_url '2_concepts/1_theming.md' 'guide' %}">Theming</a>: customize colors and themes
- <a href="{% doc_url '2_concepts/2_building_css.md' 'guide' %}">Building CSS</a>: CSS build process and production builds
- <a href="{% doc_url '3_reactivity/1_overview.md' 'guide' %}">Reactivity</a>: add interactivity with signals and server actions
- <a href="{% doc_url '3_references/0_labb_cli.md' 'guide' %}">CLI Reference</a>: component inspection, icon search, and more
- <a href="{% doc_url '1_getting_started/5_icons.md' 'guide' %}">Icons</a>: install labbicons for 2,800+ Remix icons
