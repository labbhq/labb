---
title: settings.py
description: "LABB_SETTINGS in Django settings.py: configure labb, django-cotton integration, and optional labbdocs for your django ui project."
keywords: "labb django settings, LABB_SETTINGS, django-cotton settings"
---

## Overview of LABB_SETTINGS

All labb-specific settings live under a single `LABB_SETTINGS` dict in your Django `settings.py`:

<c-lbdocs.codeblock.title title="settings.py">
```python
LABB_SETTINGS = {
    'DEFAULT_THEME': 'labb-light',
    'ALPINE_JS_PATH': 'https://cdn.jsdelivr.net/npm/alpinejs@3/dist/cdn.min.js',
}
```
</c-lbdocs.codeblock.title>

Only set what you need — all settings have built-in defaults and are fully optional.

## Settings Reference

### `DEFAULT_THEME`

<c-lbdocs.indented_block>

| | |
|---|---|
| **Default** | `"__system__"` |
| **Type** | `str` |

The theme applied to new users who have not yet made a selection. Can be any daisyUI theme registered in your project's `input.css`. The special value `"__system__"` defers to the OS-level light/dark preference.

```python
LABB_SETTINGS = {
    'DEFAULT_THEME': 'labb-light',
}
```

</c-lbdocs.indented_block>

### `ALPINE_JS_PATH`

<c-lbdocs.indented_block>

| | |
|---|---|
| **Default** | `"labb/js/alpine/alpine.min.js"` |
| **Type** | `str` |

Path to the Alpine.js file loaded when reactive (`.x`) components are used on a page. By default, labb serves Alpine from its own bundled static file.

- **Static path** — resolved via Django's static files system, emitted as `<script defer src="...">`
- **Full URL** (`http://` / `https://`) — emitted as-is, useful for CDN or custom builds

```python
LABB_SETTINGS = {
    # Use jsDelivr CDN instead of the bundled file
    'ALPINE_JS_PATH': 'https://cdn.jsdelivr.net/npm/alpinejs@3/dist/cdn.min.js',
}
```

See the [Reactivity guide]({% doc_url '2_concepts/1_reactivity.md' 'guide' %}) for more detail on how Alpine loading works.

</c-lbdocs.indented_block>

---

## Functions

### `get_labb_setting()`

<c-lbdocs.indented_block>

Retrieves a setting from `LABB_SETTINGS` with fallback to labb's built-in defaults:

```python
from labb.django_settings import get_labb_setting

theme = get_labb_setting('DEFAULT_THEME')
alpine_path = get_labb_setting('ALPINE_JS_PATH')
```

**Signature:** `get_labb_setting(key, default=None)`

| Parameter | Description |
|---|---|
| `key` | Setting name to retrieve |
| `default` | Fallback if the key is absent from both `LABB_SETTINGS` and labb's defaults |

</c-lbdocs.indented_block>

### `get_default_theme()`

<c-lbdocs.indented_block>

Convenience function to get the current default theme setting.

```python
from labb.django_settings import get_default_theme

theme = get_default_theme()
```

</c-lbdocs.indented_block>
