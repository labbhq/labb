---
title: Overview
description: "How reactivity works in labb: add interactivity to Django components with signals and server actions, staying in your templates. Client-side state and server-driven updates, no JSON endpoints."
keywords: "django reactivity, labb reactivity, django-cotton interactivity, datastar django, django signals, django ajax without javascript"
---

labb components are interactive out of the box. Menus, modals, tabs, and accordions work through daisyUI's CSS, so they ship zero JavaScript.

When you need reactivity that CSS cannot express (shared state, server-driven updates, live validation), labb adds a thin set of primitives powered by [Datastar](https://data-star.dev/), a small hypermedia library. You do not need to know Datastar to use them. If you already do, the pages here map onto its signals, `data-` attributes, and backend actions, and you can drop down to raw Datastar whenever you want.

Those primitives are the [`c-lbr.` components]({% doc_url '3_reactivity/7_reference.md' 'guide' %}), labb's reactive action and signal components (thin Cotton wrappers over Datastar), plus [signals]({% doc_url '3_reactivity/2_signals.md' 'guide' %}), the named client state they read and write.

## Which approach fits

Work through two steps:

1. **Can a daisyUI or labb component already do it with CSS?** Menus, modals, tabs, and accordions are interactive on their own. Use the component as-is and ship no JavaScript.
2. **Do you need shared or JavaScript-driven state?** Then ask whether the server needs to know about the change.
    - **No.** It only affects what the page looks like right now (a hover, a value that follows the mouse, a client-only toggle). Keep it in the browser with [signals]({% doc_url '3_reactivity/2_signals.md' 'guide' %}) and `data-` attributes. It is instant and costs no request.
    - **Yes.** It touches the database, needs validation, or should be reflected elsewhere (search, saving, pagination). Use a server action.

Both use the same signals, so you can mix them on one page. A search box can bind to a signal for instant feedback and fire a server action to fetch results.

## Server actions return whole pages

labb has no partial endpoints and no per-widget JSON APIs. A server action calls an ordinary Django view, and the view returns the **whole page**. Datastar then morphs that response into the current DOM, touching only the parts that changed. You write views the way you always have, read the current client state from `request.signals`, and render your normal template. labb gives you the `c-lbr.` components and the reactive props; Datastar does the runtime work of transporting signals and reconciling the response. Reactivity is layered on in the template.

## Zero JavaScript by default

Nothing reactive loads until a page uses it. A static page built from `c-lb.` components ships no runtime at all, and `<c-lb.m.dependencies>` adds none on its own.

Every reactive surface loads its own runtime where it is used, with no configuration:

- a `<c-lbr.signals>` declaration,
- any `c-lbr.` action (`get`, `post`, `delete`),
- a reactive `$`-prop on a plain component, such as `variant="$status:neutral"`,
- a reactive chart with `data="$signal"`.

Each of these pulls in the runtime automatically the first time it appears, and labb de-duplicates it, so a page with ten reactive components still loads it once.

The one case that cannot self-declare is hand-written `data-` markup with no labb component to trigger the load. For that, force the runtime on with the `datastar` flag:

```html
<c-lb.m.dependencies datastar />
```

You only need this for raw Datastar attributes on plain elements. If a `c-lbr.` component or a reactive `$`-prop is on the page, the runtime is already there.

## In this section

<c-lbdocs.doc_card.grid cols="2">
  <c-lbdocs.doc_card title="Signals" summary="Declare client-side state with c-lbr.signals" href="{% doc_url '3_reactivity/2_signals.md' 'guide' %}" icon="rmx.pulse" />
  <c-lbdocs.doc_card title="Reactive props" summary="Drive component props from a signal" href="{% doc_url '3_reactivity/3_reactive_props.md' 'guide' %}" icon="rmx.flashlight" />
  <c-lbdocs.doc_card title="Events & bindings" summary="bind, data-on, and the data- attributes" href="{% doc_url '3_reactivity/4_events_and_bindings.md' 'guide' %}" icon="rmx.cursor" />
  <c-lbdocs.doc_card title="Server actions" summary="c-lbr.get / post / delete over normal Django views" href="{% doc_url '3_reactivity/5_server_actions.md' 'guide' %}" icon="rmx.server" />
  <c-lbdocs.doc_card title="Patterns" summary="Proven approaches for reactive widgets and charts" href="{% doc_url '1_getting_started/3_patterns.md' 'guide' %}" icon="rmx.compasses-2" />
  <c-lbdocs.doc_card title="Reference" summary="Every c-lbr component and prop, in detail" href="{% doc_url '3_reactivity/7_reference.md' 'guide' %}" icon="rmx.book-2" />
</c-lbdocs.doc_card.grid>
