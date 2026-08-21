---
title: Icons
description: "Install labbicons and add Remix icons to Django templates as components or through labb icon props."
keywords: "labbicons install, django icons pip, remix icons django, labb icon components, c-lbi"
---

{% load docs_tags %}

**labbicons** packages icon sets as Django components. Write `<c-lbi.rmx.heart />` in a template instead of maintaining copied SVG markup. Django renders the icon with the rest of the page.

Install it separately from labb.

## Install labbicons

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

## Render an icon

Use a direct component tag, the generic icon tag, or the `icon` prop on a labb component.

```html
<!-- Direct component syntax -->
<c-lbi.rmx.heart w="24" h="24" class="text-red-500" />

<!-- Name attribute syntax -->
<c-lbi n="rmx.heart" w="24" h="24" class="text-red-500" />

<!-- Inside labb components that accept an icon prop -->
<c-lb.button variant="primary" icon="rmx.save">Save</c-lb.button>
<c-lb.badge variant="info" icon="rmx.information">Info</c-lb.badge>
```

## Choose a variant

Most icons have an outlined version and a filled version.

```html
<!-- Outlined version -->
<c-lbi.rmx.camera w="24" h="24" />

<!-- Filled version -->
<c-lbi.rmx.camera w="24" h="24" fill />
```

## Set size and colour

Set the width and height with `w` and `h`. Add utility classes as you would on any other element.

```html
<!-- Pixel values -->
<c-lbi.rmx.heart w="16" h="16" />
<c-lbi.rmx.heart w="32" h="32" />

<!-- Em units scale with the font size -->
<c-lbi.rmx.heart w="1em" h="1em" />

<!-- Utility classes -->
<c-lbi.rmx.heart w="24" h="24" class="text-red-500 hover:text-red-700 transition-colors" />
```

## Find an icon

A misspelled icon name produces no icon and no template error. Search before you use a name.

Browse and copy from the [icon browser]({% url 'icons_docs' %}), or search from the command line:

```bash
# One search term
labb icons search "arrow"

# Several search terms
labb icons search "arrow,heart,user"

# Available packs
labb icons packs

# Confirm a name
labb icons info rmx.arrow-down
```

The current release includes Remix. The <a href="{% doc_url '5_references/0_labb_cli.md' 'guide' %}#labb-icons">labb icons reference</a> lists each command and option.

## Related

<c-lbdocs.doc_card.grid cols="2">
  <c-lbdocs.doc_card title="Icon browser" summary="Search and copy from all 2,800 icons" href="{% url 'icons_docs' %}" icon="rmx.search-eye" />
  <c-lbdocs.doc_card title="labb CLI" summary="Every icons subcommand and flag" href="{% doc_url '5_references/0_labb_cli.md' 'guide' %}" icon="rmx.terminal" />
</c-lbdocs.doc_card.grid>
