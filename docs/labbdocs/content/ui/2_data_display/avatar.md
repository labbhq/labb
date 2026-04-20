---
doc_layout: component
component: c-lb.avatar
title: Avatar
description: "Avatar component for Django: display user images, initials, and avatar groups. Built with django-cotton, Tailwind CSS, and daisyUI 5."
keywords: "django avatar component, avatar django, daisyui avatar django, tailwind avatar django, avatar django-cotton, django ui avatar, user avatar django, avatar group django"
daisy_ui_component_name: avatar
---

Avatar renders a circular image with optional status badges and group stacking. Use a single avatar for profile headers, or the group variant to stack overlapping avatars for contributor lists and team displays.

## Basic Avatar
<c-lbdocs.component_example path="avatar/basic" />

## Sizes
<c-lbdocs.component_example path="avatar/sizes" />

## Rounded
<c-lbdocs.component_example path="avatar/rounded" />

## Mask Shapes
<c-lbdocs.component_example path="avatar/masks" />

<c-lb.alert variant="warning" icon="rmx.alert" alertStyle="outline" class="mt-4">
<span>The `rounded` and `mask` attributes should not be used together. Use one or the other to avoid conflicting styles.</span>
</c-lb.alert>

## Status Indicators
<c-lbdocs.component_example path="avatar/status" />

## Placeholder Avatars
<c-lbdocs.component_example path="avatar/placeholders" />

## With Rings
<c-lbdocs.component_example path="avatar/rings" />

## Avatar Groups
<c-lbdocs.component_example path="avatar/groups" />

## Group Spacing
<c-lbdocs.component_example path="avatar/group-spacing" />

## Group with Counter
<c-lbdocs.component_example path="avatar/group-with-counter" />

## Custom Content
<c-lbdocs.component_example path="avatar/custom-content" />

## API Reference
### `c-lb.avatar`
<c-lbdocs.api_table component_name="avatar" />

### `c-lb.avatar.group`
<c-lbdocs.api_table component_name="avatar.group" />
