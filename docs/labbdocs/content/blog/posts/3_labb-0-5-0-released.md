---
title: labb 0.5.0 brings reactivity closer to Django
description: "labb 0.5.0 replaces Alpine with Datastar, adds signals and server actions, refreshes reactive components, and ships 35 blocks."
keywords: "labb 0.5.0, labb datastar, alpine to datastar, django reactivity, django component library, django-cotton, daisyui django"
published_time: 2026-07-14
modified_time: 2026-07-14
author: zadiq
doc_layout: blog
doc_show_toc: false
tags:
  - announcement
  - release
  - reactivity
  - datastar
  - django
---

labb 0.5.0 is out. It replaces Alpine with [Datastar](https://data-star.dev/), removes the `.x` component variants, and adds a smaller reactivity layer for Django pages.

<c-lbdocs.image
  src="/static/lbdocs/img/blog/labb-0-5-0-revenue-overview.png"
  alt="The Revenue overview block, with metrics, charts, and app navigation"
  loading="eager"
/>

## Why I changed direction

I added Alpine support in 0.4.0 because I wanted to build a small server-reactivity wrapper on top of it. Alpine was a good starting point for local interactions, and the `.x` variants gave me room to try the idea in labb.

As I worked through the wrapper, I found [Datastar](https://data-star.dev/). It already had the pieces I was trying to assemble: browser signals for local UI work, plus server actions that send state to Django and apply an HTML response. Its runtime was smaller too.

That made the custom Alpine layer hard to justify. I could give labb one API for client-side details and server-driven interactions, while keeping Django responsible for rendering and data work.

labb wraps the Datastar pieces you use most, so pages still read like labb and Django templates rather than an application built around a separate client framework.

I wrote up the longer reasoning in [the GitHub discussion](https://github.com/labbhq/labb/discussions/104#discussioncomment-17478897).

## What reactivity looks like now

Pages still render on the server first. You add reactivity only where a page needs it.

Signals hold page state. Declare one, update it from an event, then let the markup react to it:

```html
<c-lbr.signals $open="false" />

<c-lb.button data-on:click="$open = !$open">Toggle</c-lb.button>

<div data-show="$open">Now you can see me.</div>
```

Reactive props let a signal drive a component. The fallback value handles the first render:

```html
<c-lbr.signals $status="success" />

<c-lb.badge variant="$status:success">Active</c-lb.badge>
```

Server actions cover searches, mutations, and other work Django owns. `c-lbr.get`, `c-lbr.post`, and `c-lbr.delete` send the current signals to an ordinary view. The view returns HTML and Datastar updates the affected part of the page.

```html
<c-lbr.get to="todos:index" on="input__debounce.300ms">
  <c-lb.input type="search" bind="$filters.q" placeholder="Search todos" />
</c-lbr.get>
```

A static page does not load Datastar. The extra JavaScript only appears on pages that use these components.

## Thirty-five blocks built on the new model

This release also includes 35 blocks across auth, dashboards, data tables, heroes, pricing, settings, and wizards. I built them while working through the new API. They became both examples and pressure tests for the reactivity model.

<c-lbdocs.block_grid refs="lb/data-table/customers, lb/dashboard/overview, lb/wizard/onboarding" />

Each block is server-rendered. The interactive ones show a concrete pattern: searching a customer list, switching a chart range, opening table details, calculating a price, or stepping through onboarding. You can copy a block into a project, then pull out the pieces you need.

The new `labb block` commands cover the rest of that workflow. You can create and validate a block collection, run its preview, and install a block from the command line.

## The rest of 0.5.0

Reactivity also reached the component layer. Charts can read their data from a signal, and the input, data-display, and chart components now accept reactive props where they make sense. The component API tables show those props so you can spot the supported bindings without reading implementation details.

The docs have a new reactivity path covering signals, bindings, reactive props, server actions, and common patterns. I also reorganised the installation and first-page guides to make the route into the library less roundabout.

## Upgrading from `.x`

The `.x` variants are gone in 0.5.0. Most migrations are small:

- `x-model` becomes `bind`
- `x-on` becomes `data-on`
- Client state moves into signals

The [Migrating to 0.5 guide](/docs/guide/about/migrating-to-0-5) shows each change with before-and-after code.

```bash
pip install --upgrade labbui
```

If you hit a rough edge, let me know in [GitHub Discussions](https://github.com/labbhq/labb/discussions). I want the new model to stay small, legible, and useful in real Django projects.
