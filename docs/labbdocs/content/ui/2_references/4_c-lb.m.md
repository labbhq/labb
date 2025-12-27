---
doc_layout: component
component: c-lb.m
title: c-lb.m
description: A set of meta components for labb
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

<!-- With theme switching endpoint -->
<c-lb.m.dependencies setThemeEndpoint="/api/set-theme/" />

<!-- Without global CSS -->
<c-lb.m.dependencies no_global_css />
```
{% endverbatim %}

**Parameters:**

- `no_global_css` (boolean, default: `False`) - Skip including the global labb CSS file
- `setThemeEndpoint` (string, default: `""`) - Django endpoint for theme switching via AJAX

**What it includes:**

- **Global CSS**: Automatically includes labb CSS using `lb_css_path` template tag
- **Theme Controller**: A small piece of JavaScript for handling theme switching with session persistence when the `setThemeEndpoint` parameter is provided. See the [theming documentation]({% doc_url '1_getting_started/4_theming.md' 'ui' %}) for more details.

**CSRF Token Requirements:**

When using `setThemeEndpoint` for theme persistence, you should add {% verbatim %}`{% csrf_token %}`{% endverbatim %} in your template's `<body>` section to provide Django's CSRF token for the AJAX request.

</c-lbdocs.indented_block>
