---
title: Icons
description: "Install labbicons for Django: Remix icon components with django-cotton, Tailwind CSS, and labb UI. pip install labbicons, then write <c-lbi.rmx.heart />."
keywords: "labbicons install, django icons pip, remix icons django, labb icon components, c-lbi"
---

{% load docs_tags %}

**labbicons** gives you icon packs as Django components. Write `<c-lbi.rmx.heart />` instead of copying SVG code. Backend-rendered, accessible, and zero JavaScript required.

## Installation

```bash
pip install labbicons
# or install alongside labbui
pip install labbui[icons]
```

Add `labbicons` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps
    'django_cotton',
    'labbicons',
]
```

<c-lb.alert variant="info" alertStyle="soft" class="not-prose">
  <span><strong>Note:</strong> labbicons only requires `django-cotton` and can be used independently of labb UI components. If you already have `labb` installed, `django_cotton` is already configured.</span>
</c-lb.alert>

## Usage

Reference icons in three ways:

```html
<!-- Direct component syntax -->
<c-lbi.rmx.heart w="24" h="24" class="text-red-500" />

<!-- Name attribute syntax -->
<c-lbi n="rmx.heart" w="24" h="24" class="text-red-500" />

<!-- Inside labb components that accept an icon prop -->
<c-lb.button variant="primary" icon="rmx.save">Save</c-lb.button>
<c-lb.badge variant="info" icon="rmx.information">Info</c-lb.badge>
```

## Variants

Most icons come in line (outlined) and fill (solid) variants:

```html
<!-- Line variant (default) -->
<c-lbi.rmx.camera w="24" h="24" />

<!-- Fill variant -->
<c-lbi.rmx.camera w="24" h="24" fill />
```

## Size and styling

Control size with `w` and `h`. Style with CSS classes:

```html
<!-- Numeric values (pixels) -->
<c-lbi.rmx.heart w="16" h="16" />
<c-lbi.rmx.heart w="32" h="32" />

<!-- Em units (scales with font size) -->
<c-lbi.rmx.heart w="1em" h="1em" />

<!-- Styling with classes -->
<c-lbi.rmx.heart w="24" h="24" class="text-red-500 hover:text-red-700 transition-colors" />
```

## Find an icon

Browse and copy from the [icon browser]({% url 'icons_docs' %}), or search from the command line:

```bash
# Search for icons
labb icons search "arrow"

# List available packs
labb icons packs

# Get icon info
labb icons info rmx.arrow-down
```

Remix is the pack available today, with more on the way. See the <a href="{% doc_url '3_references/0_labb_cli.md' 'guide' %}#labb-icons">labb icons command reference</a> for full documentation.
