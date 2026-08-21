---
title: Overview
description: "Add browser state and server-driven updates to Django templates with labb signals and server actions."
keywords: "django reactivity, labb reactivity, django-cotton interactivity, datastar django, django signals, django ajax without javascript"
---

labb components handle many interactions without JavaScript. Menus, modals, tabs, and accordions use daisyUI’s CSS.

Use labb’s reactive tools when the page needs shared state, live validation, or a server update. They build on [Datastar](https://data-star.dev/). You can use them without learning Datastar, or use its lower-level attributes when you need them.

The [`c-lbr.` components]({% doc_url '5_references/7_reactivity_reference.md' 'guide' %}) declare signals and trigger actions. [Signals]({% doc_url '3_reactivity/2_signals.md' 'guide' %}) hold the named browser state that these components read and update.

## Choose the right tool

Start with these questions.

1. **Does a daisyUI or labb component already provide the interaction?** Use it as-is for menus, modals, tabs, and accordions.
2. **Does the interaction need browser state?** Use [signals]({% doc_url '3_reactivity/2_signals.md' 'guide' %}) and `data-` attributes for client-only behaviour such as a toggle or value that follows the pointer.
3. **Does the server need to validate, save, search, or paginate?** Use a server action.

Both approaches use the same signals. A search field can update client-side feedback as the user types, then request new results from Django.

## Server actions use ordinary views

A server action calls an ordinary Django view, which returns the whole page. Datastar compares that response with the current DOM and updates the changed parts. Read browser state from `request.signals`, render the normal template, and keep the view usable for a first load too.

## Load the runtime only where you need it

A page using only `c-lb.` components does not load a reactive runtime. `<c-lb.m.dependencies>` does not add one on its own.

The runtime loads when a page uses one of these features.

- a `<c-lbr.signals>` declaration,
- any `c-lbr.` action (`get`, `post`, `delete`),
- a reactive `$`-prop on a plain component, such as `variant="$status:neutral"`,
- a reactive chart with `data="$signal"`.

The first reactive feature loads the runtime. labb de-duplicates it, so the page loads it once.

Hand-written `data-` markup cannot trigger the runtime by itself. Add the `datastar` flag when the page uses those attributes without a reactive labb component.

```html
<c-lb.m.dependencies datastar />
```

Use this only for raw Datastar attributes on ordinary elements. A `c-lbr.` component or reactive `$` prop already loads the runtime.

## In this section

<c-lbdocs.doc_card.grid cols="2">
  <c-lbdocs.doc_card title="Signals" summary="Declare client-side state with c-lbr.signals" href="{% doc_url '3_reactivity/2_signals.md' 'guide' %}" icon="rmx.pulse" />
  <c-lbdocs.doc_card title="Events & bindings" summary="bind, data-on, and the data- attributes" href="{% doc_url '3_reactivity/3_events_and_bindings.md' 'guide' %}" icon="rmx.cursor" />
  <c-lbdocs.doc_card title="Reactive props" summary="Drive component props from a signal" href="{% doc_url '3_reactivity/4_reactive_props.md' 'guide' %}" icon="rmx.flashlight" />
  <c-lbdocs.doc_card title="Server actions" summary="c-lbr.get / post / delete over normal Django views" href="{% doc_url '3_reactivity/5_server_actions.md' 'guide' %}" icon="rmx.server" />
  <c-lbdocs.doc_card title="Patterns" summary="Proven approaches for reactive widgets and charts" href="{% doc_url '3_reactivity/6_patterns.md' 'guide' %}" icon="rmx.compasses-2" />
  <c-lbdocs.doc_card title="Reference" summary="Every c-lbr component and prop, in detail" href="{% doc_url '5_references/7_reactivity_reference.md' 'guide' %}" icon="rmx.book-2" />
</c-lbdocs.doc_card.grid>
