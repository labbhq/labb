---
title: "Theming"
description: "Learn how to customize themes, create custom color schemes, and integrate daisyUI theming with labb components."
---

{% load docs_tags %}

labb provides a theming system built on top of <a href="https://daisyui.com/docs/themes/" target="_blank">daisyUI 5</a> that allows you to create beautiful, consistent designs with minimal effort. You can use built-in themes, create custom themes, or mix and match to create your perfect design system.

## How Theming Works

Theming in labb works through CSS variables defined in your `input.css` file. daisyUI uses CSS custom properties (variables) to define colors, spacing, and other design tokens that can be dynamically changed based on the active theme.

labb extends daisyUI's theming system with the following features:

1. **Theme Definition** - Defining custom or existing themes in `input.css` (labb comes with two custom themes by default).
2. **Template Integration** - Using the `{% verbatim %}{% labb_theme %}{% endverbatim %}` template tag to set `data-theme` attributes, or `{% verbatim %}{% labb_theme_val %}{% endverbatim %}` to get the raw theme value.
3. **Theme Controller** - Using existing components such as checkboxes, toggles, or radios with the `theme-controller` class to set the themes. When server-side persistence is enabled, the theme controller will automatically send the theme choice to the server.
4. **Server-side Persistence** - Providing utility helpers and a pre-built view (`set_theme_view`) to persist theme choices in user sessions. The `{% verbatim %}{% labb_theme %}{% endverbatim %}` tag always respects the user's theme choice.

## 1. Template Integration

The first step is integrating themes into your templates using the `{% verbatim %}{% labb_theme %}{% endverbatim %}` template tag. This tag retrieves the current theme from the user's session (when server-side persistence is enabled) or falls back to the default theme set in the Django settings, see [Django Settings Configuration](#django-settings-configuration).

### Using `labb_theme` for HTML Attributes

The `{% verbatim %}{% labb_theme %}{% endverbatim %}` tag returns a complete `data-theme` attribute that you can use directly in your HTML:

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

    <c-lb.m.dependencies />
</head>
<body>
    <!-- Your content -->
</body>
</html>
```
{% endverbatim %}
</c-lbdocs.codeblock.title>

The `data-theme` attribute on the `<html>` element tells daisyUI which theme to apply to the entire page.

### Using `labb_theme_val` for Theme Values

If you need the raw theme value for display or conditional logic, use the `{% verbatim %}{% labb_theme_val %}{% endverbatim %}` tag:

<c-lbdocs.codeblock.title title="templates/theme_info.html">
{% verbatim %}
```html
{% load lb_tags %}

<!-- Display current theme -->
{% labb_theme_val as current_theme %}
<p>Current theme: {{ current_theme }}</p>

<!-- Conditional logic based on theme -->
{% if current_theme == "dark" %}
    <p>Dark mode is active</p>
{% elif current_theme == "__system__" %}
    <p>System theme is being used</p>
{% endif %}
```
{% endverbatim %}
</c-lbdocs.codeblock.title>

**Key Differences:**

- `{% verbatim %}{% labb_theme %}{% endverbatim %}` returns `data-theme="theme-name"` or empty string for `__system__`
- `{% verbatim %}{% labb_theme_val %}{% endverbatim %}` returns the raw theme value (e.g., `"dark"`, `"light"`, `"__system__"`)

## 2. Theme Definition in input.css

When you initialize a labb project with `labb init`, your `input.css` includes both daisyUI's default themes and two custom labb themes:

<c-lbdocs.codeblock.title title="static_src/input.css">
```css
@import "tailwindcss";
@plugin "daisyui" {
  themes: light, dark;  /* daisyUI's built-in themes */
}

@plugin "daisyui/theme" {
  name: "labb-light";
  default: true;
  prefersdark: false;
  color-scheme: light;

  --color-base-100: oklch(100% 0 0);
  --color-base-200: oklch(96% 0.002 247);
  --color-base-300: oklch(89% 0.003 247);
  --color-base-content: oklch(9% 0.005 247);

  --color-primary: oklch(9% 0.005 247);
  --color-primary-content: oklch(98% 0.002 247);

  /* Additional color definitions... */
}

@plugin "daisyui/theme" {
  name: "labb-dark";
  default: false;
  prefersdark: true;
  color-scheme: dark;

  /* Dark theme color definitions... */
}
```
</c-lbdocs.codeblock.title>

This configuration provides you with:

- **daisyUI Default Themes**: `light` and `dark` with standard daisyUI styling
- **Custom labb Themes**: `labb-light` and `labb-dark` with custom color schemes optimized for labb components

## 3. Creating Custom Themes

You can create your own themes by adding more `@plugin "daisyui/theme"` blocks to your `input.css`. For detailed guidance on theme creation, refer to the <a href="https://daisyui.com/docs/themes/" target="_blank">daisyUI themes documentation</a> and use the <a href="https://daisyui.com/theme-generator/" target="_blank">daisyUI Theme Generator</a> for interactive theme creation.

<c-lbdocs.codeblock.title title="static_src/input.css">
```css
@plugin "daisyui/theme" {
  name: "my-brand";
  default: false;
  prefersdark: false;
  color-scheme: light;

  --color-primary: oklch(55% 0.3 240);
  --color-secondary: oklch(70% 0.25 200);
  --color-accent: oklch(65% 0.25 160);

  --color-base-100: oklch(98% 0.02 240);
  --color-base-200: oklch(95% 0.03 240);
  --color-base-300: oklch(92% 0.04 240);
  --color-base-content: oklch(20% 0.05 240);

  /* Border radius and other design tokens */
  --radius-selector: 1rem;
  --radius-field: 0.25rem;
  --radius-box: 0.5rem;

  /* Additional theme variables... */
}
```
</c-lbdocs.codeblock.title>

## 4. Server-side Theme Persistence

labb provides a pre-built view for theme persistence that you can use directly in your URLs. This eliminates the need to create your own view and ensures consistent behavior across projects.

### Option 1: Using the Pre-built View (Recommended)

Simply import and use the `set_theme_view` from labb shortcuts in your URLs:

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

### Option 2: Creating a Custom View

If you need custom logic, you can create your own view using the utility functions:

<c-lbdocs.codeblock.title title="views.py">
```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from labb.shortcuts import set_labb_theme, get_labb_theme

@require_http_methods(["POST"])
def set_theme(request):
    """
    AJAX view to set the theme in the session.

    Expected POST data:
        theme: Theme name (e.g., 'labb-light', 'labb-dark')
    """
    theme = request.POST.get("theme")

    if not theme:
        return JsonResponse(
            {"success": False, "error": "Theme parameter is required"},
            status=400
        )

    # Set the theme in session
    success = set_labb_theme(request, theme)

    if success:
        return JsonResponse({
            "success": True,
            "theme": theme,
            "current_theme": get_labb_theme(request)
        })
    else:
        return JsonResponse(
            {"success": False, "error": "Failed to set theme"},
            status=500
        )
```
</c-lbdocs.codeblock.title>

And add the URL pattern:

<c-lbdocs.codeblock.title title="urls.py">
```python
from django.urls import path
from . import views

urlpatterns = [
    # ... your other URLs
    path('set-theme/', views.set_theme, name='set_theme'),
]
```
</c-lbdocs.codeblock.title>

The `<c-lb.m.dependencies>` component in your base template automatically connects to this endpoint when you provide the `setThemeEndpoint` parameter:

<c-lbdocs.codeblock.title title="templates/base.html">
{% verbatim %}
```html
<!-- ... -->
<c-lb.m.dependencies
    setThemeEndpoint="{% url 'set_theme' %}"
/>
<!-- ... -->
```
{% endverbatim %}
</c-lbdocs.codeblock.title>

<c-lb.alert variant="info" style="outline" class="mt-4">
<span>When the `setThemeEndpoint` is provided, the `<c-lb.m.dependencies>` component injects a small script in the head of your base template that will send the theme choice to the server when the user changes the theme.</span>
</c-lb.alert>

### CSRF Token Requirements

For theme persistence to work, Django's CSRF protection requires a valid CSRF token. Add `{% verbatim %}{% csrf_token %}{% endverbatim %}` anywhere in your template's `<body>` section:

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

<c-lb.alert variant="warning" style="soft" class="mt-4">
<span>This important for the POST request to the `setThemeEndpoint` to be successful.</span>
</c-lb.alert>

## 4.1. Available Utility Functions

### Core Functions

**`set_labb_theme(request, theme)`**

- Sets the theme in the user's session
- Returns `True` if successful, `False` otherwise
- Usage: `set_labb_theme(request, 'labb-dark')`

**`get_labb_theme(request)`**

- Retrieves the current theme from the user's session
- Falls back to the system theme if `__system__` is set
- Usage: `current_theme = get_labb_theme(request)`

### Template Tags

{% verbatim %}
**`{% labb_theme %}`**

- Template tag that returns the current theme as a complete `data-theme` attribute
- Returns empty string for `__system__` theme (no attribute)
- Automatically handles session and system theme fallback

**`{% labb_theme_val %}`**

- Template tag that returns the raw theme value
- Returns the actual theme name (e.g., `"dark"`, `"light"`, `"__system__"`)
- Useful for display or conditional logic
{% endverbatim %}

### Importing Functions

```python
# Import from shortcuts (recommended)
from labb.shortcuts import set_labb_theme, get_labb_theme, set_theme_view

# Or import directly from contrib
from labb.contrib.theme import set_labb_theme, get_labb_theme, set_theme_view
```

## 5. Theme Controller Components

Any raido or checkbox input component can be used as a theme controller by adding the `theme-controller` class. When server-side persistence is enabled, the theme controller will automatically detect component with the `theme-controller` class and send the theme choice to the server.

### Toggle Switch
<c-lbdocs.codeblock.title title="templates/base.html">
```html
<c-lb.toggle
    class="theme-controller"
    value="labb-dark"
    size="sm"
    title="Toggle theme"
/>
```
</c-lbdocs.codeblock.title>

### Checkbox
<c-lbdocs.codeblock.title title="templates/base.html">
```html
<c-lb.checkbox
    class="theme-controller"
    value="labb-dark"
    title="Dark mode"
/>
```
</c-lbdocs.codeblock.title>


For more detailed examples and advanced usage, see the <a href="{% doc_url '3_components/1_basics/theme-controller.md' 'ui' %}">Theme Controller component documentation</a>.

## Django Settings Configuration

The default theme for your application can be configured in the `LABB_SETTINGS` dictionary in your `settings.py` file. See <a href="{% doc_url '2_references/2_django_settings.md' 'ui' %}">settings</a> for more details.

<c-lbdocs.codeblock.title title="settings.py">
```python
# labb configuration
LABB_SETTINGS = {
    'DEFAULT_THEME': 'labb-light',  # Default theme when no theme is set
}
```
</c-lbdocs.codeblock.title>


## Troubleshooting

###  Theme Testing

Test your application by manually setting different theme names when debugging.

<c-lbdocs.codeblock.title title="templates/base.html">
```html
<div data-theme="labb-light">Light theme components</div>
<div data-theme="labb-dark">Dark theme components</div>
<div data-theme="cupcake">Built-in theme components</div>
```
</c-lbdocs.codeblock.title>

### Theme Not Applying

1. **Check CSS Build** - Run `labb build` to rebuild CSS with new themes
2. **Verify Theme Name** - Ensure theme names match exactly in CSS and HTML
3. **Check Dependencies** - Make sure `<c-lb.m.dependencies>` is included
4. **Session Issues** - Clear browser cookies/session if theme switching isn't working

### Styles Not Updating

1. **CSS Variables** - Ensure you're using the correct CSS variable names
2. **Cache Issues** - Hard refresh browser or clear CSS cache
3. **Build Process** - Restart `labb dev` if changes aren't being picked up

## Resources

- <a href="https://daisyui.com/docs/themes/" target="_blank">daisyUI Themes Documentation</a> - Complete reference for daisyUI theming
- <a href="https://daisyui.com/theme-generator/" target="_blank">daisyUI Theme Generator</a> - Interactive tool to create custom themes
- <a href="https://oklch.com/" target="_blank">OKLCH Color Picker</a> - Tool for creating OKLCH color values used in daisyUI
