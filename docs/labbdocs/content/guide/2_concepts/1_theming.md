---
title: "Theming"
description: "Customize themes, create custom color schemes, and integrate daisyUI theming with labb components."
---

{% load docs_tags %}

labb's theming is built on <a href="https://daisyui.com/docs/themes/" target="_blank">daisyUI 5</a>. Themes are defined as CSS variables in `input.css`, applied via template tags, and optionally persisted server-side.

## Setup

Add the `{% verbatim %}{% labb_theme %}{% endverbatim %}` tag to your `<html>` element and register the theme persistence URL:

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
    {% csrf_token %}
    <!-- Your content -->
</body>
</html>
```
{% endverbatim %}
</c-lbdocs.codeblock.title>

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

`{% verbatim %}{% labb_theme %}{% endverbatim %}` outputs `data-theme="theme-name"` on the `<html>` element, reading from the user's session or falling back to `LABB_SETTINGS['DEFAULT_THEME']`. The `{% verbatim %}{% csrf_token %}{% endverbatim %}` is required for the theme persistence POST request.

<c-lb.alert variant="info" style="outline" class="mt-4">
<span>Use `{% verbatim %}{% labb_theme_val %}{% endverbatim %}` instead if you need the raw theme value for conditional logic (e.g., `{% verbatim %}{% labb_theme_val as current_theme %}{% endverbatim %}`).</span>
</c-lb.alert>

## Built-in Themes

`labb init` generates an `input.css` with four themes:

- `labb-light` (default) — custom labb light theme
- `labb-dark` — custom labb dark theme
- `light` — daisyUI default light
- `dark` — daisyUI default dark

<c-lbdocs.codeblock.title title="static_src/input.css">
```css
@import "tailwindcss";
@plugin "daisyui" {
  themes: light, dark;
}

@plugin "daisyui/theme" {
  name: "labb-light";
  default: true;
  prefersdark: false;
  color-scheme: light;

  --color-base-100: oklch(100% 0 0);
  --color-primary: oklch(9% 0.005 247);
  /* ... */
}

@plugin "daisyui/theme" {
  name: "labb-dark";
  default: false;
  prefersdark: true;
  color-scheme: dark;
  /* ... */
}
```
</c-lbdocs.codeblock.title>

## Custom Themes

Add `@plugin "daisyui/theme"` blocks to `input.css`. Use the <a href="https://daisyui.com/theme-generator/" target="_blank">daisyUI Theme Generator</a> for interactive creation.

<c-lbdocs.codeblock.title title="static_src/input.css">
```css
@plugin "daisyui/theme" {
  name: "my-brand";
  default: false;
  color-scheme: light;

  --color-primary: oklch(55% 0.3 240);
  --color-secondary: oklch(70% 0.25 200);
  --color-accent: oklch(65% 0.25 160);
  --color-base-100: oklch(98% 0.02 240);
  --color-base-content: oklch(20% 0.05 240);
  --radius-selector: 1rem;
  --radius-field: 0.25rem;
  --radius-box: 0.5rem;
}
```
</c-lbdocs.codeblock.title>

See the <a href="https://daisyui.com/docs/themes/" target="_blank">daisyUI themes documentation</a> for all available variables.

## Theme Controllers

Any radio or checkbox component becomes a theme switcher by adding the `theme-controller` class. When server-side persistence is enabled, the choice is automatically sent to the server.

```html
<!-- Toggle between light and dark -->
<c-lb.toggle class="theme-controller" value="labb-dark" size="sm" title="Toggle theme" />

<!-- Or use a checkbox -->
<c-lb.checkbox class="theme-controller" value="labb-dark" title="Dark mode" />
```

See the <a href="{% doc_url '1_actions/theme-controller.md' 'ui' %}">Theme Controller component documentation</a> for more examples.

## Django Settings

<c-lbdocs.codeblock.title title="settings.py">
```python
LABB_SETTINGS = {
    'DEFAULT_THEME': 'labb-light',  # Fallback when no theme is set
}
```
</c-lbdocs.codeblock.title>

See <a href="{% doc_url '3_references/2_django_settings.md' 'guide' %}">settings reference</a> for all options.

## Advanced Usage

<c-lb.collapse title="Custom theme view" class="my-4" style="arrow">
If you need custom logic instead of the pre-built `set_theme_view`, use the utility functions directly:

<c-lbdocs.codeblock.title title="views.py">
```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from labb.shortcuts import set_labb_theme, get_labb_theme

@require_http_methods(["POST"])
def set_theme(request):
    theme = request.POST.get("theme")
    if not theme:
        return JsonResponse({"success": False, "error": "Theme parameter is required"}, status=400)

    success = set_labb_theme(request, theme)
    if success:
        return JsonResponse({"success": True, "theme": theme})
    return JsonResponse({"success": False, "error": "Failed to set theme"}, status=500)
```
</c-lbdocs.codeblock.title>

**Available functions** (import from `labb.shortcuts`):

- `set_labb_theme(request, theme)` — sets the theme in the session, returns `True`/`False`
- `get_labb_theme(request)` — retrieves the current theme from the session
- `set_theme_view` — pre-built view for theme persistence
</c-lb.collapse>

## Troubleshooting

- **Theme not applying** — Run `labb build` to rebuild CSS, verify theme names match in CSS and HTML
- **Persistence not working** — Ensure `{% verbatim %}{% csrf_token %}{% endverbatim %}` is in the `<body>` and `setThemeEndpoint` is set on `<c-lb.m.dependencies />`
- **Styles not updating** — Hard refresh browser, restart `labb dev`

## Resources

- <a href="https://daisyui.com/docs/themes/" target="_blank">daisyUI Themes Documentation</a>
- <a href="https://daisyui.com/theme-generator/" target="_blank">daisyUI Theme Generator</a>
- <a href="https://oklch.com/" target="_blank">OKLCH Color Picker</a>
