---
doc_layout: component
component: c-lb.m
title: c-lb.m
description: "Meta components for labb django templates: c-lb.m helpers for django-cotton composition and advanced UI patterns."
keywords: "c-lb.m, labb meta components, django-cotton meta, labb django templates"
---

{% load docs_tags %}

## Overview

Meta components provide essential setup and configuration functionality for labb applications. These components handle global dependencies, styling, and framework integration.

## Reference
### `c-lb.m.dependencies`

<c-lbdocs.indented_block>
Includes essential CSS, JavaScript, and styling dependencies for labb components with optional theme switching functionality.

**Usage:**
{% verbatim %}
```html
<!-- Basic usage -->
<c-lb.m.dependencies />

<!-- Force-load Alpine (e.g. you use Alpine in your own templates) -->
<c-lb.m.dependencies alpine />

<!-- With theme switching endpoint -->
<c-lb.m.dependencies setThemeEndpoint="/api/set-theme/" />

<!-- Without global CSS -->
<c-lb.m.dependencies noGlobalCSS />
```
{% endverbatim %}

**Parameters:**

- `noGlobalCSS` (boolean, default: `False`) - Skip including the global labb CSS file
- `alpine` (boolean, default: `False`) - Always load Alpine.js, regardless of whether any `.x` reactive components are on the page. Useful when you use Alpine directly in your own templates. See the [Reactivity guide]({% doc_url '2_concepts/1_reactivity.md' 'guide' %}) for details.
- `setThemeEndpoint` (string, default: `""`) - Django endpoint for theme switching via AJAX

**What it includes:**

- **Global CSS**: Automatically includes labb CSS using `lb_css_path` template tag
- **Alpine.js + component scripts**: Loaded automatically when `.x` reactive components are used on the page. Pass `alpine` to force-load Alpine even without `.x` components. Alpine is never loaded twice — if the `alpine` flag is set, the stack loader skips it.
- **Theme Controller**: JavaScript for theme switching with session persistence when `setThemeEndpoint` is provided. See the [theming documentation]({% doc_url '2_concepts/2_theming.md' 'guide' %}) for more details.

**CSRF Token Requirements:**

When using `setThemeEndpoint` for theme persistence, add {% verbatim %}`{% csrf_token %}`{% endverbatim %} in your template's `<body>` to provide Django's CSRF token for the AJAX request.

</c-lbdocs.indented_block>
