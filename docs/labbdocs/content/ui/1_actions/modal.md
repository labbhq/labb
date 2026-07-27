---
doc_layout: component
component: c-lb.modal
title: Modal
description: "Modal component for Django: create accessible dialogs and overlays without JavaScript. Built with django-cotton, Tailwind CSS, and daisyUI 5."
keywords: "django modal component, modal django, daisyui modal django, tailwind modal django, modal django-cotton, django ui modal, django dialog component, django-cotton"
daisy_ui_component_name: modal
icon: rmx.window-2
---

Modal uses CSS-driven dialog toggling via checkbox state, so no JavaScript is required. The `c-lb.modal.action` slot is the trigger; `c-lb.modal.content` holds the panel body. Closing works via the built-in close button or a backdrop click.

## Basic Modal
<c-lbdocs.component_example path="modal/basic" style="tab" />

## Default Slot Only
<c-lbdocs.component_example path="modal/default-slot-only" style="tab" />

## Custom Box
<c-lbdocs.component_example path="modal/custom-box" style="tab" />

## With Box Class
<c-lbdocs.component_example path="modal/with-box-class" style="tab" />

## Click Outside to Close
<c-lbdocs.component_example path="modal/backdrop-close" style="tab" />

## Corner Close Button
<c-lbdocs.component_example path="modal/corner-close" style="tab" />

## Close Button Positions
<c-lbdocs.component_example path="modal/close-positions" style="tab" />

## Modal Sizes
<c-lbdocs.component_example path="modal/sizes" style="tab" />

## Modal Placement
<c-lbdocs.component_example path="modal/placement" style="tab" />

## Responsive Modal
<c-lbdocs.component_example path="modal/responsive" style="tab" />

## Confirmation Dialog
<c-lbdocs.component_example path="modal/confirmation" style="tab" />

## Notification Modal
<c-lbdocs.component_example path="modal/notification" style="tab" />

## Combined Features
<c-lbdocs.component_example path="modal/combined-features" style="tab" />

## API Reference
### `c-lb.modal`
<c-lbdocs.api_table component_name="modal" />

### `c-lb.modal.box`
<c-lbdocs.api_table component_name="modal.box" />

### `c-lb.modal.action`
<c-lbdocs.api_table component_name="modal.action" />

### `c-lb.modal.backdrop`
<c-lbdocs.api_table component_name="modal.backdrop" />

### `c-lb.modal.close`
<c-lbdocs.api_table component_name="modal.close" />
