---
doc_layout: component
component: c-lb.dropdown
title: Dropdown
description: "Dropdown component for Django: build menus and contextual actions with keyboard navigation. Built with django-cotton, Tailwind CSS, and daisyUI 5."
keywords: "django dropdown component, dropdown django, daisyui dropdown django, tailwind dropdown django, dropdown django-cotton, django ui dropdown, django-cotton"
daisy_ui_component_name: dropdown
icon: rmx.dropdown-list
---

Dropdown renders a container that reveals a positioned menu when toggled. Use it for navigation submenus, action menus on data rows, or contextual option lists. The trigger can be any element that wraps a `c-lb.dropdown.menu`.

## Basic Dropdown
<c-lbdocs.component_example path="dropdown/basic" />

## With Placement
<c-lbdocs.component_example path="dropdown/with-placement" />

## With Alignment
<c-lbdocs.component_example path="dropdown/with-alignment" />

## Hover Activation
<c-lbdocs.component_example path="dropdown/hover" />

## Forced Open
<c-lbdocs.component_example path="dropdown/open" />

## With Card Content
<c-lbdocs.component_example path="dropdown/with-card" />

## API Reference
### `c-lb.dropdown`
<c-lbdocs.api_table component_name="dropdown" />

### `c-lb.dropdown.trigger`
<c-lbdocs.api_table component_name="dropdown.trigger" />

The trigger carries `tabindex="0"` so the dropdown opens on focus. `as="a"` is the exception: daisyUI sets `pointer-events: none` on a focused dropdown's first `[tabindex]` child, which would stop an anchor from navigating, so an anchor trigger relies on its `href` for focus instead and needs one. Every other element keeps `tabindex="0"`, including `as="button"`: WebKit is documented not to focus a button on a mouse click, so without it the dropdown may never open in Safari.

### `c-lb.dropdown.content`
<c-lbdocs.api_table component_name="dropdown.content" />
