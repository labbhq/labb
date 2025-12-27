---
doc_layout: component
title: Theme Controller
description: Theme switching components with backend persistence support
daisy_ui_component_name: theme-controller
---

This page shows different ways of using existing components to implement theme controllers. For complete theming setup and configuration, see the <a href="{% doc_url '1_getting_started/4_theming.md' 'ui' %}">Theming</a> documentation.

## Toggle Theme Controller
<c-lbdocs.component_example path="theme-controller/toggle" />

## Swap Theme Controller
<c-lbdocs.component_example path="theme-controller/swap" />

## Dropdown Theme Controller
<c-lbdocs.component_example path="theme-controller/dropdown" />

## Backend Persistence

For backend theme persistence, use the `c-lb.m.dependencies` component to automatically handle theme switching with Django sessions. See <a href="{% doc_url '1_getting_started/4_theming.md' 'ui' %}#4-server-side-theme-persistence">theme persistence</a> for more details.

<c-lbdocs.component_example path="theme-controller/with-dependencies" />
