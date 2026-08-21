---
doc_layout: component
component: c-lb.link
title: Link
description: "Link component for Django: apply consistent link styles across your Django templates. Built with django-cotton, Tailwind CSS, and daisyUI 5."
keywords: "django link component, styled link django, daisyui link django, tailwind link django, link django-cotton, django ui link, anchor component django, django-cotton"
daisy_ui_component_name: link
icon: rmx.link
---

Link wraps an `<a>` element with daisyUI link styling and colour variants. Use it in prose, navigation lists, or anywhere you need a consistently styled, theme-aware hyperlink.

## Basic Link
<c-lbdocs.component_example path="link/basic" />

## Color Variants
Apply DaisyUI color variants to your links.

<c-lbdocs.component_example path="link/variants" />

## Hover Effect
Show underline only on hover for a cleaner look.

<c-lbdocs.component_example path="link/hover" />

## Using Viewname
Resolve Django view names automatically. Use `l:` prefixed attributes to pass URL arguments.

<c-lbdocs.component_example path="link/viewname" />

## With Text Component
Combine with text component for styled link text, including icons.

<c-lbdocs.component_example path="link/with-text" />

## API Reference
### `c-lb.link`
<c-lbdocs.api_table component_name="link" />
