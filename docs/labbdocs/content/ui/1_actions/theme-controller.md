---
doc_layout: component
title: Theme Controller
description: "Theme controller component for Django: add light/dark mode and custom theme switching. Built with django-cotton, daisyUI 5 themes, and Tailwind CSS."
keywords: "django theme controller, dark mode django, theme switcher django, daisyui theme django, tailwind theme django, django-cotton theme, django dark mode component"
daisy_ui_component_name: theme-controller
icon: rmx.palette
---

This page shows different ways of using existing components to implement theme controllers. For complete theming setup and configuration, see the <a href="{% doc_url '2_building_uis/5_theming.md' 'guide' %}">Theming</a> documentation.

## Toggle Theme Controller
<c-lbdocs.component_example path="theme-controller/toggle" />

## Swap Theme Controller
<c-lbdocs.component_example path="theme-controller/swap" />

## Dropdown Theme Controller
<c-lbdocs.component_example path="theme-controller/dropdown" />

## Backend Persistence

For backend theme persistence, use the `c-lb.m.dependencies` component to automatically handle theme switching with Django sessions. See <a href="{% doc_url '2_building_uis/5_theming.md' 'guide' %}#connect-the-theme-controls">theme persistence</a> for more details.

<c-lbdocs.component_example path="theme-controller/with-dependencies" />
