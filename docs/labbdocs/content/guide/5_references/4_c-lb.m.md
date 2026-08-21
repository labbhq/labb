---
doc_layout: component
component: c-lb.m
title: c-lb.m
description: "Meta components for labb django templates: c-lb.m helpers for django-cotton composition and advanced UI patterns."
keywords: "c-lb.m, labb meta components, django-cotton meta, labb django templates"
---

`c-lb.m.*` are the meta components that go in your `<head>`: dependency loading, theme wiring, and asset stacks. They render no visible UI.

{% load docs_tags %}

## Overview

Meta components handle setup and configuration for labb applications: global dependencies, styling, and framework integration.

## Reference
### `c-lb.m.dependencies`

<c-lbdocs.indented_block>
Includes the CSS, JavaScript, and styling dependencies for labb components, with optional theme switching.

**Usage:**
{% verbatim %}
```html
<!-- Basic usage -->
<c-lb.m.dependencies />

<!-- With theme switching endpoint -->
<c-lb.m.dependencies setThemeEndpoint="/api/set-theme/" />

<!-- Force-load the reactivity runtime for hand-rolled data-* markup -->
<c-lb.m.dependencies datastar />

<!-- Without global CSS -->
<c-lb.m.dependencies noGlobalCSS />
```
{% endverbatim %}

**Parameters:**

- `noGlobalCSS` (boolean, default: `False`) - Skip including the global labb CSS file
- `datastar` (boolean, default: `False`) - Force-load the reactivity runtime. You rarely need this: signals, reactive props, `c-lbr.` components, and reactive charts each load the runtime on their own where they are used, so static pages ship zero JS. Set it only when you hand-roll `data-*` reactivity with no labb component to trigger the load. See the [Reactivity guide]({% doc_url '3_reactivity/1_overview.md' 'guide' %}).
- `setThemeEndpoint` (string, default: `""`) - Django endpoint for theme switching via AJAX

**What it includes:**

- **Global CSS**: Automatically includes labb CSS using `lb_css_path` template tag
- **Reactivity runtime**: The small runtime that powers reactive props and `c-lbr.` components. It is not loaded by default; each reactive surface loads it where it is used, so static pages ship zero JS. Pass `datastar` to force it on for hand-rolled `data-*` markup.
- **Theme Controller**: JavaScript for theme switching with session persistence when `setThemeEndpoint` is provided. See the [theming documentation]({% doc_url '2_building_uis/5_theming.md' 'guide' %}) for more details.

**CSRF Token Requirements:**

When using `setThemeEndpoint` for theme persistence, add {% verbatim %}`{% csrf_token %}`{% endverbatim %} in your template's `<body>` to provide Django's CSRF token for the AJAX request.

</c-lbdocs.indented_block>
