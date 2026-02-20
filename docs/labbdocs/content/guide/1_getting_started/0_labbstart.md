---
title: labbstart
description: Scaffold a new Django project with labb pre-configured—the quickest way to get running.
---
{% load static %}

**labbstart** is the fastest way to get started with labb. It scaffolds a new Django project with labb, your chosen package manager, and a starter kit—so you can start building in minutes.

<div class="not-prose my-6">
  <img src="{% static 'lbdocs/img/labb/labb_welcome_kit.jpg' %}" alt="Welcome kit: Your Django project is ready" class="rounded-lg border border-base-300 w-full max-w-4xl mx-auto shadow-lg" />
</div>

## Installation

It is recommended to install labbstart globally so the `labbstart` command is available everywhere:

```bash
pip install labbstart
```

## Quick Start

Create a new Django project with labb pre-configured:

```bash
labbstart new
```

This will interactively prompt you for:

- Project name
- Django version (4, 5, or 6)
- Package manager (poetry, pip, or uv)
- Starter kit (e.g. welcome)
- App name for the starter kit

### Non-Interactive Mode

You can pass all parameters as flags:

```bash
labbstart new myproject \
  --django-version 5 \
  --package-manager poetry \
  --kit welcome \
  --app-name starter
```

## Available Kits

### Welcome Kit

A simple single-page starter that showcases basic labb components.

More coming soon.

## Next Steps

After running `labbstart new`, start two processes in separate terminals:

**Terminal 1 — CSS development:**

```bash
cd your-project-name
labb dev
```

**Terminal 2 — Django development server:**

```bash
cd your-project-name
python manage.py runserver
```

Then open [http://localhost:8000](http://localhost:8000) to see your new project.

For more on labb components and usage, see the rest of the [documentation]({% doc_url '1_getting_started/1_introduction.md' 'guide' %}).
