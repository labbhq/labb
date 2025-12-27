---
title: Installation
description: Learn how to install and set up labb Icons in your Django project.

---

{% load docs_tags %}



## Install labb Icons

### Using pip

```bash
pip install labbicons
# or both labbui and labbicons
pip install labbui[icons]
```

### Using Poetry

```bash
poetry add labbicons
# or both labbui and labbicons
poetry add labbui[icons]
```

## Add to Django Settings

Add `labbicons` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps
    'django_cotton',
    # 'labb',  # optional, add if you are using the labb components
    'labbicons',
]
```

<c-lb.alert variant="info" style="soft" class="not-prose">
  <span><strong>Note:</strong> labb Icons only requires the `django-cotton` package and can be used independently of the labb UI components in any Django project. If you have already installed `labb`, you would have already <a href="{% doc_url '1_getting_started/2_installation.md' 'ui' %}#add-to-django-settings">added</a> `django_cotton`.</span>
</c-lb.alert>

## Basic Usage

Once installed, you can start using icons in your templates:

```html
<!-- Basic usage -->
<c-lbi.rmx.heart w="24" h="24" class="text-red-500" />

<!-- Fill variant -->
<c-lbi.rmx.heart w="24" h="24" class="text-red-500" fill />
```

## CLI Commands

Use the `labb icons` command to search and manage icons:

```bash
# Search for icons
labb icons search "arrow"

# List available packs
labb icons packs

# Get detailed icon information
labb icons info rmx.arrow-down
```

For complete CLI documentation, see the <a href="{% doc_url '2_references/0_labb_cli.md' 'ui' %}#labb-icons">labb icons command reference</a>.
