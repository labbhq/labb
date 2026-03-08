---
title: settings.py
description: Learn how to configure labb settings in your Django project
---

## Overview

labb provides a simple way to configure labb-specific settings through Django's `settings.py` file. All labb-specific settings are organized under a `LABB_SETTINGS` object for easy management.

Add the `LABB_SETTINGS` object to your Django `settings.py` file, and configure the variables as needed:

<c-lbdocs.codeblock.title title="settings.py">
```python
LABB_SETTINGS = {
    'DEFAULT_THEME': 'default',  # system's default theme
}
```
</c-lbdocs.codeblock_with_title>

These settings can be accessed in your code using `labb.django_settings.get_labb_setting`. For example:

```python
from labb.django_settings import get_labb_setting

default_theme = get_labb_setting('DEFAULT_THEME')
```

## Settings

| Variable | Default | Description |
|---------|---------|-------------|
| `DEFAULT_THEME` | `default` | Default theme for new users. Can be any daisyui theme configured in your project's `input.css`. |


## Functions

### `get_labb_setting(key, default=None)`

<c-lbdocs.indented_block>
Retrieves a labb setting from Django settings with fallback to defaults.

**Parameters:**

- `key` (str): The setting key to retrieve
- `default`: Default value if setting is not found

**Returns:**

- The setting value or default

**Example:**

```python
from labb.django_settings import get_labb_setting

# Get a specific setting
theme = get_labb_setting('DEFAULT_THEME', 'labb-light')
```
</c-lbdocs.indented_block>

### `get_default_theme()`

<c-lbdocs.indented_block>
Convenience function to get the default theme setting.

**Returns:**

- The default theme value from settings

**Example:**

```python
from labb.django_settings import get_default_theme

default_theme = get_default_theme()
print(f"Default theme: {default_theme}")
```
</c-lbdocs.indented_block>
