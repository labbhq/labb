---
title: Quick Start
description: Get started with labb Icons in minutes
---

{% load docs_tags %}

## Basic Usage

After installing labb Icons, you can start using icons immediately. Icons can be referenced in two ways:

### 1. Direct Component Syntax
```html
<!-- Using the pattern <c-lbi.<pack>.<icon> /> -->
<c-lbi.rmx.heart w="24" h="24" class="text-red-500" />
<c-lbi.rmx.arrow-down-box w="24" h="24" />
```

### 2. Name Attribute Syntax
```html
<!-- Using the n attribute -->
<c-lbi n="rmx.heart" w="24" h="24" class="text-red-500" />
<c-lbi n="rmx.arrow-down-box" w="24" h="24" />
```


### 3. In Components (if supported)
Some labb components support an `icon` parameter:

```html
<!-- Badge with integrated icon -->
<c-lb.badge variant="info" icon="rmx.information">Info</c-lb.badge>

<!-- Button with icon -->
<c-lb.button variant="primary" icon="rmx.save">Save</c-lb.button>
```

## Icon Packs

labb Icons supports multiple icon packs. Currently available:

- **Remix Icons (rmx)**: 1600+ icons across 19 categories
- More packs coming soon!

Use the CLI to explore available packs:

```bash
# List all available packs
labb icons packs

# Search for icons across all packs
labb icons search "arrow"
```

## Icon Variants

Most icons come in two variants - line (outlined) and fill (solid):

```html
<!-- Line variant (default) -->
<c-lbi.rmx.camera w="24" h="24" class="text-blue-500" />

<!-- Fill variant -->
<c-lbi.rmx.camera w="24" h="24" class="text-blue-500" fill />

<!-- Line variant (explicit) -->
<c-lbi.rmx.camera w="24" h="24" class="text-blue-500" line />
```

## Customizing Icons

### Size

Control the size of your icons using the `w` (width) and `h` (height) attributes:

```html
<!-- Small icon -->
<c-lbi.rmx.heart w="16" h="16" class="text-red-500" />

<!-- Large icon -->
<c-lbi.rmx.heart w="32" h="32" class="text-red-500" />

<!-- Using em units -->
<c-lbi.rmx.heart w="1em" h="1em" class="text-red-500" />

<!-- Using pixel units -->
<c-lbi.rmx.heart w="2px" h="2px" class="text-red-500" />

<!-- Different width and height -->
<c-lbi.rmx.heart w="20" h="24" class="text-red-500" />
```

### Styling

Apply CSS classes to style your icons:

```html
<!-- Basic styling -->
<c-lbi.rmx.heart w="24" h="24" class="text-red-500" />

<!-- With hover effects -->
<c-lbi.rmx.heart w="24" h="24" class="text-red-500 hover:text-red-700 transition-colors" />

<!-- With custom classes -->
<c-lbi.rmx.heart w="24" h="24" class="text-red-500 my-custom-icon-class" />
```


## CLI Commands

The `labbicons` CLI is available by default. When using `labb`, you can access it under `labb icons`:

```bash
# Using labbicons directly
labbicons search "arrow"
labbicons info rmx.arrow-down
labbicons packs

# Using through labb (if labb is installed)
labb icons search "arrow"
labb icons info rmx.arrow-down
labb icons packs
```

For complete CLI documentation, see the <a href="{% doc_url '2_references/0_labb_cli.md' 'ui' %}#labb-icons">labb icons command reference</a>.
