---
doc_layout: component
component: c-lb.breadcrumbs
title: Breadcrumbs
description: "Breadcrumbs component for Django: add accessible navigation trails to multi-level pages. Built with django-cotton, Tailwind CSS, and daisyUI 5."
keywords: "django breadcrumbs component, breadcrumbs django, daisyui breadcrumbs django, tailwind breadcrumbs django, breadcrumbs django-cotton, django ui breadcrumbs, navigation breadcrumbs django"
daisy_ui_component_name: breadcrumbs
icon: rmx.route
---

Breadcrumbs renders an accessible `<nav>` with a separator-joined trail of links. Pass each crumb as a `c-lb.breadcrumbs.item` with an `href`. The last item renders without a link to indicate the current page.

## Basic Usage
<c-lbdocs.component_example path="breadcrumbs/basic" />

## With Icons
<c-lbdocs.component_example path="breadcrumbs/with-icons" />

## Sizes
<c-lbdocs.component_example path="breadcrumbs/sizes" />

## Icon Only
<c-lbdocs.component_example path="breadcrumbs/icon-only" />

## Max Width (Scrollable)
<c-lbdocs.component_example path="breadcrumbs/max-width" />

## Custom Styling
<c-lbdocs.component_example path="breadcrumbs/custom-styling" />

## Using Django View Names
Use `viewname` instead of `href` to link to Django views by name. Pass URL arguments with the `l:` prefix.

<c-lbdocs.component_example path="breadcrumbs/viewname" />

## API Reference

### `c-lb.breadcrumbs`
<c-lbdocs.api_table component_name="breadcrumbs" />

### `c-lb.breadcrumbs.item`
<c-lbdocs.api_table component_name="breadcrumbs.item" />
