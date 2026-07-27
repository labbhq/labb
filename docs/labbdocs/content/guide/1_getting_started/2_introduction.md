---
title: Introduction
description: "Build Django interfaces with labb: HTML-like components, icons, theming, and optional reactivity. A quick tour of how you develop with labb."
keywords: "django ui components, django component library, django-cotton, labb django, tailwind django, daisyui django, django frontend"
---
{% load static %}

labb is a component library for Django. You build interfaces by writing HTML-like tags in your templates, and labb renders accessible, styled markup on the server. No JavaScript framework, no build step for components, and nothing ships to the browser unless you ask for it.

This page is a quick tour of how you build with labb. If you have not installed it yet, start with [Installation]({% doc_url '1_getting_started/1_installation.md' 'guide' %}).

## Your first component

A component is a tag that starts with `c-lb.`. Drop it into any Django template:

```html
<c-lb.button variant="primary">Save</c-lb.button>
```

Props control how it looks. Change the colour, the size, or add an icon by setting attributes:

<c-lbdocs.component_example path="button/variants" />

Every component has a page in the [component docs]({% url 'ui_docs' %}) listing its props and examples. You can also inspect a component from the command line:

```bash
labb components inspect button
```

## Compose components

Components nest. Build a card by combining the card pieces:

```html
<c-lb.card class="w-80">
    <c-lb.card.body>
        <c-lb.card.title>Air Max Pro</c-lb.card.title>
        <p class="text-base-content/60">Lightweight. Fast. Built for the road.</p>
        <c-lb.button variant="primary">Add to cart</c-lb.button>
    </c-lb.card.body>
</c-lb.card>
```

When a piece of markup shows up more than once, move it into your own component and reuse it. Your templates end up reading like an outline of the page instead of a wall of `<div>` tags.

## Add an icon

Any component with an `icon` prop takes an icon name. Search for one from the command line:

```bash
labb icons search "arrow"
```

```html
<c-lb.button icon="rmx.arrow-right-line">Next</c-lb.button>
```

Icons come from the optional `labbicons` package. See the [Icons]({% doc_url '1_getting_started/5_icons.md' 'guide' %}) page for install and usage, or browse them all in the [icon browser]({% url 'icons_docs' %}).

## Make it interactive

Pages are static HTML by default. When you need interactivity, prefix a prop with `$` to bind it to a signal, and change that signal from the page. Here a button's colour and size are driven by the controls next to it:

<c-lbdocs.component_example path="button/reactive" previewStyle="block" />

The same idea powers server-driven interactions like search, forms, and inline editing, without writing separate JSON endpoints. The [Reactivity]({% doc_url '3_reactivity/1_overview.md' 'guide' %}) guide walks through both.

## What you get

- **50+ components** covering buttons, cards, modals, drawers, forms, tables, charts, and more
- **Live examples** on every component page, ready to copy
- **2,800+ icons** through the optional `labbicons` package
- **Theming** with light, dark, and custom themes out of the box
- **Optional reactivity** that loads only on the pages that use it
- **A CLI** for setup, component inspection, and AI-assisted development

## Next steps

<c-lbdocs.doc_card.grid cols="3">
  <c-lbdocs.doc_card title="Reactivity" summary="Add interactivity with signals and server actions" href="{% doc_url '3_reactivity/1_overview.md' 'guide' %}" icon="rmx.flashlight" />
  <c-lbdocs.doc_card title="Patterns" summary="Practices for building maintainable UIs" href="{% doc_url '1_getting_started/4_patterns.md' 'guide' %}" icon="rmx.compasses-2" />
  <c-lbdocs.doc_card title="Components" summary="Browse every component and its examples" href="{% url 'ui_docs' %}" icon="rmx.layout-grid" />
</c-lbdocs.doc_card.grid>
