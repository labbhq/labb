---
title: Reactive props
description: "Make labb component props react to a signal. Prefix a prop with $signal and the component re-renders in the browser when the signal changes, with a server-rendered fallback."
keywords: "labb reactive props, datastar reactive attributes, django reactive component, signal prop django, labb $ prop"
---

To make a component react to a [signal]({% doc_url '3_reactivity/2_signals.md' 'guide' %}), prefix a prop value with `$` and the signal name. The value after the colon is what the server renders on the first load:

```html
<c-lbr.signals $status="success" />

<c-lb.badge variant="$status:success">Active</c-lb.badge>
```

When `$status` changes, the badge re-colours on its own (Datastar recomputes the prop in the browser). No handler, no re-render call. The pattern is always `prop="$signal:fallback"`: `$signal` is the client value, `:fallback` is the first paint the server sends.

This button reads its colour, size, and style from signals; the controls below change them:

<c-lbdocs.component_example path="button/reactive" previewStyle="flex-col" />

## The runtime loads itself

A reactive `$`-prop is enough on its own. Even with no `<c-lbr.signals>` and no action on the page, a single `$`-prop pulls in the reactivity runtime where it is used. You still declare the signal (usually with `<c-lbr.signals>`) to give it a starting value, but you never have to add a runtime include by hand.

## Finding which props are reactive

Not every prop is reactive. Each component's API reference table marks the reactive ones with a flashlight icon, so check there to see which props accept a `$signal`. You do not have to enumerate the values a reactive prop can take; the [Building CSS]({% doc_url '2_concepts/2_building_css.md' 'guide' %}) page explains how labb emits the classes for every possible value automatically.

## Driving several props at once

A prop can read from a nested signal, so one object signal can feed several props on one or more components. Hold the related values together and swap the whole object to update them in one step. See [Patterns]({% doc_url '1_getting_started/3_patterns.md' 'guide' %}) for the full approach, and the [Reference]({% doc_url '3_reactivity/7_reference.md' 'guide' %}) for the exact syntax.
