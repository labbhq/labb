---
title: "Theming"
description: "Set up labb themes, add a custom daisyUI colour scheme, and persist a visitor’s theme choice."
keywords: "labb theming django, daisyui themes django, tailwind themes django, django dark mode, labb_theme tag"
---

{% load docs_tags %}

labb uses <a href="https://daisyui.com/docs/themes/" target="_blank">daisyUI 5</a> for themes. Define the colours in `input.css`, set the active theme on the page, and save a visitor’s choice in their session if you need to.

## Connect the theme controls

Start with the `<c-lb.m.dependencies />` tag from [Installation]({% doc_url '1_getting_started/2_installation.md' 'guide' %}). Add `{% verbatim %}{% labb_theme %}{% endverbatim %}` to the `<html>` element and give the dependency tag the endpoint that stores a theme choice.

<c-lbdocs.codeblock.title title="templates/base.html">
{% verbatim %}
```html
<html lang="en" {% labb_theme %}>
<head>
    <c-lb.m.dependencies setThemeEndpoint="{% url 'set_theme' %}" />
</head>
<body>
    {% csrf_token %}
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

`{% verbatim %}{% labb_theme %}{% endverbatim %}` writes `data-theme="theme-name"` to `<html>`. It reads the user’s session and falls back to `LABB_SETTINGS['DEFAULT_THEME']`. Keep `{% verbatim %}{% csrf_token %}{% endverbatim %}` in the page because the theme controller sends a POST request.

<c-lb.alert variant="info" alertStyle="outline" class="mt-4">
<span>Use `{% verbatim %}{% labb_theme_val %}{% endverbatim %}` when template logic needs the raw value. For example, `{% verbatim %}{% labb_theme_val as current_theme %}{% endverbatim %}` stores it in a variable.</span>
</c-lb.alert>

## Built-in themes

`labb init` subscribes the project to labb’s `themes` CSS group. During a build, labb imports that group into `.labb/labb.css`. Keep the generated import in `input.css`.

The standard labb themes are `labb-light` and `labb-dark`. The starter CSS also enables daisyUI’s `light` and `dark` themes.

<c-lbdocs.codeblock.title title="static_src/input.css">
```css
@import "tailwindcss";
@plugin "daisyui" {
  themes: light, dark;
}

/* labb CSS - don't remove this line */
@import "../.labb/labb.css";
```
</c-lbdocs.codeblock.title>

## Add a custom theme

Add an `@plugin "daisyui/theme"` block below the generated labb import in `input.css`. Do not edit `.labb/labb.css`; labb replaces it on every build. The <a href="https://daisyui.com/theme-generator/" target="_blank">daisyUI Theme Generator</a> can help you choose values.

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

The <a href="https://daisyui.com/docs/themes/" target="_blank">daisyUI theme documentation</a> lists the available variables.

## Add a theme switcher

Add the `theme-controller` class to a radio control, checkbox, or toggle. With the endpoint configured, labb posts the selected value to Django.

<c-lbdocs.component_example path="guide/theming/switcher" previewStyle="block" />

```html
<!-- Toggle dark mode -->
<c-lb.toggle class="theme-controller" value="dark" size="sm" title="Toggle dark mode" />

<!-- A checkbox works too -->
<c-lb.checkbox class="theme-controller" value="dark" title="Dark mode" />
```

See the <a href="{% doc_url '1_actions/theme-controller.md' 'ui' %}">Theme Controller component documentation</a> for more examples.

## Choose the default

<c-lbdocs.codeblock.title title="settings.py">
```python
LABB_SETTINGS = {
    'DEFAULT_THEME': 'labb-light',  # Fallback when no theme is set
}
```
</c-lbdocs.codeblock.title>

See <a href="{% doc_url '5_references/2_django_settings.md' 'guide' %}">settings reference</a> for all options.

## Write a custom view

<c-lb.collapse title="Custom theme view" class="my-4" style="arrow">
Use the utility functions when your app needs custom theme-selection logic instead of `set_theme_view`.

<c-lbdocs.codeblock.title title="views.py">
```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from labb.shortcuts import set_labb_theme, get_labb_theme
from labb.contrib.theme import is_valid_theme_name

@require_http_methods(["POST"])
def set_theme(request):
    theme = request.POST.get("theme")
    if not theme:
        return JsonResponse({"success": False, "error": "Theme parameter is required"}, status=400)

    if not is_valid_theme_name(theme):
        return JsonResponse({"success": False, "error": "Invalid theme name"}, status=400)

    success = set_labb_theme(request, theme)
    if success:
        return JsonResponse({"success": True, "theme": theme})
    return JsonResponse({"success": False, "error": "Failed to set theme"}, status=500)
```
</c-lbdocs.codeblock.title>

Import these functions from `labb.shortcuts`.

- `set_labb_theme(request, theme)` stores the theme in the session and returns `True` or `False`
- `get_labb_theme(request)` returns the current session value
- `set_theme_view` provides the built-in persistence view

`set_labb_theme` stores whatever you give it. The theme name ends up in a `data-theme` attribute and in a
CSS selector, so check it first. `set_theme_view` already does; a custom view should call
`is_valid_theme_name` as above.
</c-lb.collapse>

## Fix common problems

- **The theme does not apply**. Run `labb build` and confirm that the CSS and HTML use the same theme name.
- **The selection does not persist**. Put `{% verbatim %}{% csrf_token %}{% endverbatim %}` in `<body>` and set `setThemeEndpoint` on `<c-lb.m.dependencies />`.
- **Styles do not update**. Refresh the browser without its cache, then restart `labb dev`.

## Related

<c-lbdocs.doc_card.grid cols="2">
  <c-lbdocs.doc_card title="Building CSS" summary="Why a theme change needs a rebuild" href="{% doc_url '4_going_further/1_building_css.md' 'guide' %}" icon="rmx.css3" />
  <c-lbdocs.doc_card title="settings.py" summary="DEFAULT_THEME and the rest of LABB_SETTINGS" href="{% doc_url '5_references/2_django_settings.md' 'guide' %}" icon="rmx.settings-3" />
</c-lbdocs.doc_card.grid>

<c-lbdocs.block_grid refs="lb/pricing/highlight-tiers, lb/pricing/comparison-table, lb/pricing/three-tier-toggle" />

Useful references include <a href="https://daisyui.com/docs/themes/" target="_blank">daisyUI themes</a>, the <a href="https://daisyui.com/theme-generator/" target="_blank">theme generator</a>, and an <a href="https://oklch.com/" target="_blank">OKLCH colour picker</a>.
