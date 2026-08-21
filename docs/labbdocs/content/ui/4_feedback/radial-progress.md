---
doc_layout: component
component: c-lb.radial-progress
title: Radial Progress
description: "Radial progress component for Django: display percentage completion as a circular gauge. Built with django-cotton, Tailwind CSS, and daisyUI 5."
keywords: "django radial progress, circular progress django, daisyui radial progress django, tailwind radial progress, radial progress django-cotton, circular chart django"
daisy_ui_component_name: radial-progress
icon: rmx.dashboard-3
---

Radial Progress renders a CSS circular gauge with a percentage value at its centre. Set `value` (0–100), plus `size` and `thickness` to adjust the ring.

## Basic Radial Progress
<c-lbdocs.component_example path="radial-progress/basic" />

## Custom Size and Thickness
<c-lbdocs.component_example path="radial-progress/custom-size" />

## Color Variants
<c-lbdocs.component_example path="radial-progress/with-colors" />

## Background Variant
<c-lbdocs.component_example path="radial-progress/with-border" />

## Reactive value
Bind `value` to a signal and the ring tracks it. `aria-valuenow` follows the same signal, so assistive tech stays in step.

<c-lbdocs.component_example path="radial-progress/reactive" />

## API Reference
### `c-lb.radial-progress`
<c-lbdocs.api_table component_name="radial-progress" />
