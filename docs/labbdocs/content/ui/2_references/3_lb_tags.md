---
title: lb_tags
description: Template tags for labb components and theming in Django templates
---

{% load docs_tags %}

## Overview

labb provides convenient Django template tags through the `lb_tags` module to help integrate integrate with labb components and theming.

## Loading Template Tags

You can load the template tags in two ways:

### Method 1: Manual Loading (Per Template)

Load the template tags in individual Django templates:

<c-lbdocs.codeblock.title title="templates/base.html">
{% verbatim %}
```html
{% load lb_tags %}

<!DOCTYPE html>
<html lang="en" {% labb_theme %}>
<head>
    <link rel="stylesheet" href="{% static 'css/' %}{% lb_css_path %}">
</head>
<body>
    <!-- Your content -->
</body>
</html>
```
{% endverbatim %}
</c-lbdocs.codeblock.title>

### Method 2: Automatic Loading (Global)

Register the template tags globally in your Django settings to make them available in all templates without manual loading:

<c-lbdocs.codeblock.title title="settings.py">
```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # ... your context processors
            ],
            'builtins': [
                'labb.templatetags.lb_tags',  # Auto-load lb_tags globally
            ],
        },
    },
]
```
</c-lbdocs.codeblock.title>

With this configuration, you can use all available template tags directly in any template without `{% verbatim %}{% load lb_tags %}{% endverbatim %}`.

## Reference

### `lb_css_path`

<c-lbdocs.indented_block>
Returns the CSS output path from your labb configuration, making it easy to include the generated CSS file in your templates.

**Usage:**
{% verbatim %}
```html
{% load lb_tags %}

{% lb_css_path as css_path %}
<link rel="stylesheet" href="{% static css_path %}">
```
{% endverbatim %}

**Returns:**
- The CSS output filename from `labb.yaml` configuration
- Falls back to `"css/output.css"` if configuration is not found

**Example:**
{% verbatim %}
```html
<!-- If labb.yaml has output: static/css/styles.css -->
{% lb_css_path as css_path %}
<!-- css_path variable now contains: "css/styles.css" -->

<!-- Full usage in template -->
<link rel="stylesheet" href="{% static css_path %}">
<!-- Renders as: <link rel="stylesheet" href="/static/css/styles.css"> -->
```
{% endverbatim %}

**Configuration Integration:**
This tag automatically reads from your `labb.yaml` file:
```yaml
css:
  build:
    output: static/css/output.css  # lb_css_path returns "css/output.css"
```

{% verbatim %}
**Note:** This CSS is automatically included when using `<c-lb.m.dependencies>` component, so you typically don't need to include it manually unless you're setting `no_global_css` variable (i.e. `<c-lb.m.dependencies no_global_css>`).
{% endverbatim %}

</c-lbdocs.indented_block>

### `labb_theme`

<c-lbdocs.indented_block>
Returns the current theme as a complete `data-theme` attribute from the user's session or the default theme from Django settings.

**Usage:**
{% verbatim %}
```html
{% load lb_tags %}
<html {% labb_theme %}>
```
{% endverbatim %}

**Context-aware:**
- Takes the current request context to check user's session
- Falls back to `DEFAULT_THEME` from Django settings
- Returns empty string for `__system__` theme (no data-theme attribute)

**Example:**
{% verbatim %}
```html
<!-- Basic usage -->
<html {% labb_theme %}>
<!-- Renders as: <html data-theme="dark"> or <html> (for __system__) -->

<!-- Store in variable -->
{% labb_theme as theme_attr %}
<html {{ theme_attr }}>
```
{% endverbatim %}

**Returns:**
- `data-theme="theme-name"` for regular themes (e.g., `data-theme="dark"`)
- Empty string for `__system__` theme (no attribute set)

**Session Integration:**
This tag works with labb's theme switching system:
- Reads theme preference from user session
- Integrates with theme controller components
- Supports server-side theme persistence
</c-lbdocs.indented_block>

### `labb_theme_val`

<c-lbdocs.indented_block>
Returns the raw theme value from the user's session or the default theme from Django settings.

**Usage:**
{% verbatim %}
```html
{% load lb_tags %}
{% labb_theme_val as theme_value %}
<span>{{ theme_value }}</span>
```
{% endverbatim %}

**Context-aware:**
- Takes the current request context to check user's session
- Falls back to `DEFAULT_THEME` from Django settings
- Returns the actual theme name without formatting

**Example:**
{% verbatim %}
```html
<!-- Display theme value -->
{% labb_theme_val as current_theme %}
<p>Current theme: {{ current_theme }}</p>

<!-- Conditional logic -->
{% if current_theme == "dark" %}
    <p>Dark mode is active</p>
{% elif current_theme == "__system__" %}
    <p>System theme is being used</p>
{% endif %}
```
{% endverbatim %}

**Returns:**
- Raw theme value (e.g., `"dark"`, `"light"`, `"__system__"`)
- No formatting or HTML attributes

**Use Cases:**
- Display theme name in UI
- Conditional logic based on theme
- JavaScript integration
- Debugging theme values
</c-lbdocs.indented_block>


See the [configuration documentation]({% doc_url '2_references/1_config_yaml.md' 'ui' %}) and [Django settings documentation]({% doc_url '2_references/2_django_settings.md' 'ui' %}) for more details about using some of these tags.
