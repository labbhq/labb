---
title: Quick Start
description: Get up and running with labb components in minutes
---

{% load docs_tags %}


A concise step-by-step overview to get you started with labb. For detailed explanations, follow the links provided.

## 1. Installation

Install labb and set up your Django project. See <a href="{% doc_url '1_getting_started/2_installation.md' 'ui' %}">full installation guide</a> for details.

```bash
# Install labb
pip install labbui

# Initialize and setup
labb init --defaults && labb setup
```

## 2. Add Dependencies to HTML Header

Add `<c-lb.m.dependencies />` to your main HTML template header. This includes required CSS and JavaScript for components. Learn more about <a href="{% doc_url '2_references/4_c-lb.m.md' 'ui' %}">dependencies configuration</a>.

<c-lbdocs.codeblock.title title="templates/base.html">
{% verbatim %}
```html
{% load lb_tags %}

<!DOCTYPE html>
<html lang="en" {% labb_theme %}>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My App</title>
    <c-lb.m.dependencies setThemeEndpoint="{% url 'set_theme' %}" />
</head>
<body>
    <!-- Your content here -->
</body>
</html>
```
{% endverbatim %}
</c-lbdocs.codeblock.title>

## 3. Using Components in Templates

Use labb components in your templates with simple HTML-like syntax. Browse <a href="{% doc_url '3_components/1_basics/button.md' 'ui' %}">component documentation</a> for available components.

```html
<!-- Button -->
<c-lb.button variant="primary">Click me</c-lb.button>

<!-- Card -->
<c-lb.card>
    <c-lb.card.body>
        <c-lb.card.title>Card Title</c-lb.card.title>
        <p>Card content goes here</p>
    </c-lb.card.body>
</c-lb.card>

<!-- Alert -->
<c-lb.alert variant="success">Success message!</c-lb.alert>
```

## 4. Start labb Dev CLI Command

In your first terminal, start the labb development watcher to monitor template changes and build CSS automatically. Learn more about <a href="{% doc_url '2_references/0_labb_cli.md' 'ui' %}#labb-dev">labb dev command</a>.

```bash
labb dev
```

This watches your templates, scans for components, and rebuilds CSS on changes. Keep this running while developing.

## 5. Start Django Server

In a **separate terminal**, start your Django development server:

```bash
python manage.py runserver
```

## 6. Exploring CLI Commands

The labb CLI offers powerful tools for component discovery and inspection. See <a href="{% doc_url '2_references/0_labb_cli.md' 'ui' %}">complete CLI reference</a>.

```bash
# List all available components
labb components inspect --list

# View component examples
labb components ex button
labb components ex card

# Search for icons (requires labbicons)
labb icons search "arrow"

# View configuration
labb config
```

## 7. Using Icons in Components

Add icons to components using the `icon` attribute. Requires installing <a href="{% doc_url '2_installation.md' 'icons' %}">labbicons package</a>.

```bash
# Install icons package
pip install labbui[icons]
```

```html
<!-- Button with icon -->
<c-lb.button variant="primary" icon="rmx.save">Save</c-lb.button>

<!-- Badge with icon -->
<c-lb.badge variant="info" icon="rmx.information">Info</c-lb.badge>

<!-- Direct icon usage -->
<c-lbi.rmx.heart w="24" h="24" class="text-red-500" />
```

## 8. Configuration (labb.yaml)

The `labb.yaml` file controls CSS building, template scanning, and more. See <a href="{% doc_url '2_references/1_config_yaml.md' 'ui' %}">configuration reference</a>.

```yaml
css:
  build:
    input: static_src/input.css
    output: static/css/output.css
    minify: true
  scan:
    output: static_src/labb-classes.txt
    templates:
      - templates/**/*.html
```

Edit with:

```bash
# View configuration
labb config

# Edit configuration
labb config --edit

# Validate configuration
labb config --validate
```

## 9. Theming

labb includes light and dark themes by default. Add a theme switcher to let users toggle between themes. See <a href="{% doc_url '1_getting_started/4_theming.md' 'ui' %}">complete theming guide</a>.

**Set up theme persistence** by adding the theme endpoint to your URLs:

<c-lbdocs.codeblock.title title="urls.py">
```python
from django.urls import path
from labb.shortcuts import set_theme_view

urlpatterns = [
    # ... your other URLs
    path('set-theme/', set_theme_view, name='set_theme'),
]
```
</c-lbdocs.codeblock.title>

**Add a theme toggle** to your template:

```html
<!-- Simple toggle between light and dark -->
<c-lb.toggle
    class="theme-controller"
    value="labb-dark"
    size="sm"
    title="Toggle theme"
/>

<!-- Or checkbox -->
<c-lb.checkbox
    class="theme-controller"
    value="labb-dark"
    title="Dark mode"
/>
```

**Available themes:**

- `labb-light` (default) - Custom labb light theme
- `labb-dark` - Custom labb dark theme
- `light` - daisyUI light theme
- `dark` - daisyUI dark theme
- `__system__` - Use system preference

**Create custom themes** in your `static_src/input.css`:

```css
@plugin "daisyui/theme" {
  name: "my-theme";
  default: false;
  color-scheme: light;

  --color-primary: oklch(55% 0.3 240);
  --color-base-100: oklch(98% 0.02 240);
  /* ... more colors */
}
```

Learn more about <a href="{% doc_url '1_getting_started/4_theming.md' 'ui' %}">theme customization</a> and <a href="{% doc_url '3_components/1_basics/theme-controller.md' 'ui' %}">theme controller component</a>.

## 10. Building for Production

Build optimized CSS for production deployment. See <a href="{% doc_url '1_getting_started/5_building_css.md' 'ui' %}">CSS building guide</a> for details.

```bash
# Build minified CSS for production
labb build --minify

# Or use config defaults
labb build
```

**Production Checklist:**

1. Run `labb scan` to extract all CSS classes from templates
2. Run `labb build --minify` to generate optimized CSS
3. Set `DEBUG = False` in Django settings
4. Run `python manage.py collectstatic` for static files
5. Deploy with your preferred hosting service

## Next Steps

- <a href="{% doc_url '1_getting_started/4_theming.md' 'ui' %}">Theming</a> — Customize colors and design system
- <a href="{% doc_url '1_getting_started/5_building_css.md' 'ui' %}">Building CSS</a> — Understand the CSS build process
- Browse component examples in the documentation

You're ready to build with labb! 🚀
