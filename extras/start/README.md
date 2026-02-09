# labbstart

The fastest way to get started with [labb](https://labb.io) - the UI for Django perfectionists.

## Installation

```bash
pip install labbstart
```

Or with poetry:

```bash
poetry add labbstart
```

Or with uv:

```bash
uv add labbstart
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
- Starter kit (welcome)
- App name for the starter kit

### Non-Interactive Mode

You can also pass all parameters as flags:

```bash
labbstart new myproject \
  --django-version 5 \
  --package-manager poetry \
  --kit welcome \
  --app-name starter
```

## What Does It Do?

The `labbstart new` command will:

1. ✨ Create a new Django project directory
2. 📦 Initialize your chosen package manager (poetry/pip/uv)
3. 🎯 Install Django with your specified version
4. 🚀 Set up a Django project structure
5. 🎨 Install labbui and labbicons (includes django-cotton)
6. 📋 Add a starter kit as a Django app
7. ⚙️  Configure settings.py and urls.py
8. 🎨 Initialize labb (Tailwind CSS + DaisyUI)
9. 🔨 Build initial CSS
10. 📝 Create .gitignore and README.md

After completion, you'll have a fully configured Django project with labb components ready to use!

## Available Kits

### Welcome Kit

A simple single-page starter that showcases basic labb components.

## Next Steps

After running `labbstart new`, you'll need to start two processes in separate terminals:

**Terminal 1 - CSS Development Server:**
```bash
cd your-project-name
labb dev
```

**Terminal 2 - Django Development Server:**
```bash
cd your-project-name
python manage.py runserver
```

Then visit `http://localhost:8000` to see your new project!

## Requirements

- Python 3.10+ (but < 4.0)
- One of: poetry, pip, or uv

## Documentation

For more information about labb components and usage, visit [labb.io](https://labb.io).
