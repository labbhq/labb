---
doc_layout: component
component: c-lb.hover3d
title: Hover 3D
description: "Hover 3D component for Django: add perspective tilt effects to cards and images. Built with django-cotton and Tailwind CSS, and ships no JavaScript."
keywords: "django hover 3d component, 3d tilt django, daisyui 3d django, tailwind 3d django, hover effect django, django-cotton hover 3d, interactive card django"
daisy_ui_component_name: hover-3d
icon: rmx.box-3
---

Hover3d applies a CSS 3D perspective tilt to its content when the pointer moves over it. Use it to add visual depth to cards, hero images, or profile panels.

## Basic
<c-lbdocs.component_example path="hover3d/basic" />

## With Card
<c-lbdocs.component_example path="hover3d/with-card" />

<c-lb.alert variant="warning" icon="rmx.alert" alertStyle="outline" class="mt-4">
<span>Only non-interactive content (no buttons or links) should be placed inside the `hover-3d` wrapper. For clickable cards, wrap the entire `c-lb.hover3d` element in an anchor tag instead.</span>
</c-lb.alert>

## API Reference
### `c-lb.hover3d`
<c-lbdocs.api_table component_name="hover3d" />
