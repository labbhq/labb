---
title: Events & bindings
description: "Connect labb inputs and page events to signals with bind and Datastar data attributes."
keywords: "labb bind, data-on django, datastar data-show, django form binding, labb data attributes, reactive events django"
---

After declaring a [signal]({% doc_url '3_reactivity/2_signals.md' 'guide' %}), connect it to the page with `bind` and `data-` attributes. labb forwards Datastar’s attributes to its components. The examples on this page run in the browser without a request to Django.

This example binds an input, reads a signal with `data-text`, changes it with `data-on:click`, and responds with `data-show`.

<c-lbdocs.component_example path="guide/reactivity/toggle" previewStyle="flex-col" />

## Bind an input

The `bind` prop keeps a signal in sync with what the user types or selects.

```html
<c-lbr.signals $filters.q="" />

<c-lb.input type="search" bind="$filters.q" placeholder="Search" />
```

`filters.q` now holds the search text. `bind` works with `input`, `textarea`, `select`, `checkbox`, `toggle`, and `range`. When you use a typed schema, bind through the field descriptor.

```html
<c-lb.input type="search" :bind=signals.fields.q />
```

## Responding to events

Use `data-on:<event>` for a short expression that runs on an event. Read and update signals with `$`.

```html
<c-lbr.signals $open="false" />

<c-lb.button data-on:click="$open = !$open">Toggle</c-lb.button>

<div data-show="$open">Now you can see me.</div>
```

Inside a `data-on` expression, the event is `evt` and the element is `el`. Write both without `$`, which is reserved for signals.

Add a timing modifier with `__`.

```html
<c-lb.input data-on:input__debounce.300ms="..." />
<div data-on:mousemove__throttle.50ms="$mx = evt.clientX"></div>
```

## The `data-` attributes

These attributes cover most local interface changes. They work on any element after a `c-lbr.` component or reactive `$` prop loads the runtime.

| Attribute | Does |
|-----------|------|
| `data-show="$open"` | Shows or hides the element. |
| `data-text="$label"` | Sets the element's text content. |
| `data-class="{'active': $open}"` | Toggles classes. A key may hold several space-separated classes. |
| `data-attr:href="$url"` | Sets any attribute reactively. `data-attr:style`, `data-attr:disabled`, and so on. |

Use them for local toggles, tabs, and dropdowns. Use a [server action]({% doc_url '3_reactivity/5_server_actions.md' 'guide' %}) when Django needs to own the change.

## The search box, step two

Continuing the [signals]({% doc_url '3_reactivity/2_signals.md' 'guide' %}) example, the input now binds to `filters.q`, a handler sets `status`, and Clear appears only when needed.

<c-lbdocs.component_example path="guide/reactivity/thread-2-bindings" previewStyle="flex-col" />

The example still runs entirely in the browser. Continue to [Reactive props]({% doc_url '3_reactivity/4_reactive_props.md' 'guide' %}) to let the signal drive the result badge.
