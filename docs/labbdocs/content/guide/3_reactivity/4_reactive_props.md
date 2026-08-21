---
title: Reactive props
description: "Drive compatible labb component props from a signal while retaining a server-rendered starting value."
keywords: "labb reactive props, datastar reactive attributes, django reactive component, signal prop django, labb $ prop"
---

Set a component prop to `$signal:fallback` to drive it from a [signal]({% doc_url '3_reactivity/2_signals.md' 'guide' %}). The fallback is the value Django renders on the first load.

```html
<c-lbr.signals $status="success" />

<c-lb.badge variant="$status:success">Active</c-lb.badge>
```

When `$status` changes, the badge updates in the browser. The pattern is `prop="$signal:fallback"`. The signal provides the client value and the fallback covers the initial response.

This button reads its colour, size, and style from signals. The controls below change them.

<c-lbdocs.component_example path="button/reactive" previewStyle="flex-col" />

## The runtime loads with the prop

A reactive `$` prop loads the runtime even when the page has no `<c-lbr.signals>` or action. You still declare the signal, usually with `<c-lbr.signals>`, to set its starting value.

## Check whether a prop supports it

Only selected props are reactive. The component API tables mark them with a flashlight icon. The [Building CSS]({% doc_url '4_going_further/1_building_css.md' 'guide' %}) guide explains how labb includes classes for the prop’s possible values.

## The search box, step three

The same search example now has a badge whose colour reads an existing signal.

<c-lbdocs.component_example path="guide/reactivity/thread-3-props" previewStyle="flex-col" />

`$tone` contains `neutral` and `info`, both valid `variant` values. A reactive prop still needs a value the component accepts.

Continue to [Server actions]({% doc_url '3_reactivity/5_server_actions.md' 'guide' %}) to send the search state to Django and render new results.

## Driving several props at once

Props can read nested signals, so one object can provide values to several components. Replace the object to update those values together. [Patterns]({% doc_url '3_reactivity/6_patterns.md' 'guide' %}) shows the approach and the [Reference]({% doc_url '5_references/7_reactivity_reference.md' 'guide' %}) lists the syntax.

<c-lbdocs.block_grid refs="lb/dashboard/overview, lb/dashboard/compact-kpi, lb/dashboard/split-charts" />
