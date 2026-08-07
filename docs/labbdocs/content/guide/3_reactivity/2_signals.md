---
title: Signals
description: "Declare browser state with c-lbr.signals, then use it in reactive props, bindings, and server actions."
keywords: "labb signals, c-lbr.signals, datastar signals django, django client state, reactive state django"
---

A signal is a named value in the browser. Form components bind to signals, `data-` attributes read and update them, and [server actions]({% doc_url '3_reactivity/5_server_actions.md' 'guide' %}) send them to Django. Declare signals with `<c-lbr.signals>`, usually near the top of the page body.

```html
<c-lbr.signals $count="0" $open="false" />
```

The tag also loads the runtime. Leave it out of pages that do not need reactivity.

This example uses one signal for two buttons and a label.

<c-lbdocs.component_example path="guide/reactivity/counter" />

Use `$` whenever you name a signal: in a declaration, `data-` expression, [reactive prop]({% doc_url '3_reactivity/4_reactive_props.md' 'guide' %}), or form binding.

## Naming signals

Signal names use camelCase JavaScript identifiers. Group related values with dots.

```html
<c-lbr.signals $filters.q="" $filters.status="all" $page="1" />
```

This creates a `filters` object with `q` and `status`, plus a top-level `page`. Read them as `$filters.q` and `$page`.

Paths bound from the DOM must use lowercase or snake_case because browsers lowercase attribute names. Use `filters.q` instead of `filters.firstName`. JavaScript expressions can use camelCase.

## Declaration forms

Choose a declaration form based on the value you need.

### Scalar props with `$`

A `$` prop declares a signal inline. labb treats the value as a JSON literal rather than an evaluated expression.

```html
<c-lbr.signals $name="" $open="false" $status="active" />
```

Only `"true"` and `"false"` become booleans. Other quoted values stay strings, so `$page="1"` is text rather than the number `1`.

### Numbers, lists, and objects with `:$`

Use a Cotton `:` binding for numbers, lists, and objects. It evaluates the value and encodes it as JSON.

```html
<c-lbr.signals
    :$count="0"
    :$tags="['new', 'urgent']"
    :$order="{'variant': 'primary', 'label': 'Pending'}"
/>
```

`:$count="0"` creates the number `0`, so `$count++` performs arithmetic. Use an object when related values change together. [Patterns]({% doc_url '3_reactivity/6_patterns.md' 'guide' %}) shows that approach.

### A typed schema from the view

Define a `Signals` class for state that needs typed, validated server access. It gives the signal paths one home.

```python
from labb.signals import Signals, Str, Int

class TodoSignals(Signals):
    q = Str(path="filters.q", default="")
    page = Int(default=1, min_value=1)

def index(request):
    s = TodoSignals(request)
    return render(request, "todos/index.html", {"signals": s})
```

```html
<c-lbr.signals :schema=signals />
```

Bind each form field through its descriptor so the path comes from the schema.

```html
<c-lb.input :bind=signals.fields.q />
```

Use a schema when the state has several paths or needs validation. Props suit a small number of local values. You can use both on the same page.

## A search box, step one

The next three pages build a search control one step at a time. It starts with two unused signals.

<c-lbdocs.component_example path="guide/reactivity/thread-1-signals" previewStyle="flex-col" />

Continue to [Events & bindings]({% doc_url '3_reactivity/3_events_and_bindings.md' 'guide' %}) to connect the signals to the search control. The [Reactivity reference]({% doc_url '5_references/7_reactivity_reference.md' 'guide' %}) lists every prop.
