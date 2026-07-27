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
}
```
</c-lbdocs.codeblock.title>

Only set what you need. Every setting is optional and has a built-in default.

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

### `CHART_JS_PATH`

<c-lbdocs.indented_block>

| | |
|---|---|
| **Default** | `"labb/js/vendor/chart.umd.min.js"` |
| **Type** | `str` |

Path to the Chart.js file used by the chart components. By default labb serves its own bundled copy. Set a full URL to load Chart.js from a CDN instead.

```python
LABB_SETTINGS = {
    'CHART_JS_PATH': 'https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js',
}
```

</c-lbdocs.indented_block>

### `REACTIVITY`

<c-lbdocs.indented_block>

Options for how reactive state is stored in the URL when a `c-lbr.signals` uses `syncQuery`.

| Key | Default | Description |
|---|---|---|
| `QUERY_KEY` | `"lbr"` | The query-string parameter that holds the synced signals. |
| `QUERY_ENCODING` | `"flat"` | How the signals are written to the URL: `"flat"` (readable), `"json"`, or `"base64"` (compact). |

```python
LABB_SETTINGS = {
    'REACTIVITY': {
        'QUERY_KEY': 'lbr',
        'QUERY_ENCODING': 'flat',
    },
}
```

See the [Reactivity guide]({% doc_url '3_reactivity/1_overview.md' 'guide' %}) for how reactivity works.

</c-lbdocs.indented_block>

---

## Functions

### `get_labb_setting()`

<c-lbdocs.indented_block>

Retrieves a setting from `LABB_SETTINGS` with fallback to labb's built-in defaults:

```python
from labb.django_settings import get_labb_setting

theme = get_labb_setting('DEFAULT_THEME')
chart_path = get_labb_setting('CHART_JS_PATH')
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
