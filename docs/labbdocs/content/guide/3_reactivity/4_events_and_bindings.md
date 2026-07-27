---
title: Events & bindings
description: "Wire labb inputs and events to signals: bind form fields with bind, run expressions with data-on, and show, set, or toggle with data-show, data-text, data-class, and data-attr."
keywords: "labb bind, data-on django, datastar data-show, django form binding, labb data attributes, reactive events django"
---

Once a [signal]({% doc_url '3_reactivity/2_signals.md' 'guide' %}) exists, you read and write it from the page with a `bind` prop and a few `data-` attributes. These are [Datastar](https://data-star.dev/) attributes, forwarded straight through the labb components, so anything Datastar supports works here. Everything on this page stays in the browser and needs no server round-trip.

This example uses all of them: an input `bind`s to a signal, `data-text` reads a signal, `data-on:click` flips one, and `data-show` reacts to it:

<c-lbdocs.component_example path="reactivity/toggle" previewStyle="flex-col" />

## Reading input into a signal

Form components accept a `bind` prop that keeps a signal in sync with what the user types or selects:

```html
<c-lbr.signals $filters.q="" />

<c-lb.input type="search" bind="filters.q" placeholder="Search" />
```

Now `filters.q` always holds the current search text. `bind` works on any labb form component: `input`, `textarea`, `select`, `checkbox`, `toggle`, and `range`. When you have a typed schema, bind by field instead of by string so the path comes from the schema:

```html
<c-lb.input type="search" :bind=signals.fields.q />
```

## Responding to events

Use `data-on:<event>` to run a short expression when something happens. Read and write signals with the `$` prefix:

```html
<c-lbr.signals $open="false" />

<c-lb.button data-on:click="$open = !$open">Toggle</c-lb.button>

<div data-show="$open">Now you can see me.</div>
```

Inside a `data-on` expression the event is `evt` and the element is `el`. Write them bare, never `$evt` or `$el`. The `$` prefix is only for signals, so `$el` would read a signal named `el` and fail.

Add timing modifiers to an event with `__`:

```html
<c-lb.input data-on:input__debounce.300ms="..." />
<div data-on:mousemove__throttle.50ms="$mx = evt.clientX"></div>
```

## The `data-` attributes

A few attributes cover most local UI. They are available on any element once a `c-lbr.` component (or a reactive `$`-prop) has loaded the runtime.

| Attribute | Does |
|-----------|------|
| `data-show="$open"` | Shows or hides the element. |
| `data-text="$label"` | Sets the element's text content. |
| `data-class="{'active': $open}"` | Toggles classes. A key may hold several space-separated classes. |
| `data-attr:href="$url"` | Sets any attribute reactively. `data-attr:style`, `data-attr:disabled`, and so on. |

Toggles, tabs, dropdowns, and accordions all work with these alone, no server involved. When the change is something the server owns, reach for a [server action]({% doc_url '3_reactivity/5_server_actions.md' 'guide' %}) instead.
