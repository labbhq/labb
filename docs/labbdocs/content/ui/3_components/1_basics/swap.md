---
doc_layout: component
component: c-lb.swap
title: Swap
description: Toggle between two elements with smooth transitions and animations
daisy_ui_component_name: swap
---

## Basic Swap
<c-lbdocs.component_example path="swap/basic" />

## With Icons
<c-lbdocs.component_example path="swap/with-icons" />

## Rotate Effect
<c-lbdocs.component_example path="swap/rotate-effect" />

## Flip Effect
<c-lbdocs.component_example path="swap/flip-effect" />

## Hamburger Menu
<c-lbdocs.component_example path="swap/hamburger-menu" />

## Checked State
<c-lbdocs.component_example path="swap/checked-state" />

## Disabled State
<c-lbdocs.component_example path="swap/disabled-state" />

## Indeterminate State
💡 Click the child (document) checkboxes to see the parent's indeterminate state.
<c-lbdocs.component_example path="swap/indeterminate-state" />

Note: JavaScript is required to set the checkbox's `indeterminate` property.
Example:
```javascript
document.querySelector('input[type="checkbox"]').indeterminate = true;
```

## API Reference
### `c-lb.swap`
<c-lbdocs.api_table component_name="swap" />

### `c-lb.swap.on`
<c-lbdocs.api_table component_name="swap.on" />

### `c-lb.swap.off`
<c-lbdocs.api_table component_name="swap.off" />

### `c-lb.swap.indeterminate`
<c-lbdocs.api_table component_name="swap.indeterminate" />
