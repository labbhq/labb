---
title: Signals
description: "Declare client-side state in labb with c-lbr.signals. Named values that live in the browser and drive reactive props, bindings, and server actions."
keywords: "labb signals, c-lbr.signals, datastar signals django, django client state, reactive state django"
---

A signal is a named value that lives in the browser. Signals are a [Datastar](https://data-star.dev/) concept; labb declares and reads them through the [`c-lbr.` components]({% doc_url '3_reactivity/7_reference.md' 'guide' %}) (thin Cotton wrappers over Datastar) so you rarely touch Datastar directly. Form components bind to signals, `data-` attributes read and write them, and [server actions]({% doc_url '3_reactivity/5_server_actions.md' 'guide' %}) send them along with every request. You declare signals with `<c-lbr.signals>`, usually once near the top of the page body:

```html
<c-lbr.signals $count="0" $open="false" />
```

That one tag also loads the reactivity runtime, so you do not add anything else to make signals work. On a page with no reactivity, leave it out and the page ships no JavaScript.

This example drives two buttons and a label from one signal. The buttons change the count; the label reads it:

<c-lbdocs.component_example path="reactivity/counter" />

## Naming signals

Signal names are camelCase JavaScript identifiers. Group related values by nesting with dots:

```html
<c-lbr.signals $filters.q="" $filters.status="all" $page="1" />
```

That declares a `filters` object with `q` and `status`, plus a top-level `page`. You read them back the same way: `$filters.q`, `$page`.

Paths you bind to from the DOM must stay lowercase or snake_case, because browsers lowercase attribute names. Use `filters.q`, not `filters.firstName`. camelCase is fine inside JavaScript expressions.

## Declaration forms

There are three ways to give a signal its starting value.

### Scalar props with `$`

A `$`-prefixed prop declares a signal inline. The value is JSON-encoded as a **literal**, not evaluated:

```html
<c-lbr.signals $name="" $open="false" $status="active" />
```

Only `"true"` and `"false"` become booleans. Every other quoted value stays a string, so `$page="1"` is the string `"1"`, not the number `1`.

### Numbers, lists, and objects with `:$`

For a non-string value, use a Cotton `:` binding so the value is evaluated and JSON-encoded:

```html
<c-lbr.signals
    :$count="0"
    :$tags="['new', 'urgent']"
    :$order="{'variant': 'primary', 'label': 'Pending'}"
/>
```

`:$count="0"` is the number `0`, so `$count++` does arithmetic instead of string concatenation. Objects are useful when several related props change together (see [Patterns]({% doc_url '1_getting_started/3_patterns.md' 'guide' %})).

### A typed schema from the view

For anything non-trivial, define a `Signals` class in Python and pass the instance in. This gives you typed, validated access on the server and one place that owns the signal paths:

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

Bind form fields by field descriptor so the path comes from the schema, not a hand-typed string:

```html
<c-lb.input :bind=signals.fields.q />
```

Schema mode keeps paths in one place, which pays off as the number of signals grows. Prop mode is self-documenting and best for a handful of simple values. You can mix them: use a schema for query state and `$` props for a couple of local flags.

## Reading signals on the server

Datastar sends the **whole** signal bag to the backend on every action request, by default. You do not choose which signals to include or wire up any serialisation. When a `c-lbr.` action fires, the current client state arrives at your view, and labb's `ReactivityMiddleware` decodes it into `request.signals`:

```python
def index(request):
    q = request.signals.get("filters", {}).get("q", "")
    page = int(request.signals.get("page", 1))
    todos = Todo.objects.filter(text__icontains=q)
    return render(request, "todos/index.html", {"todos": todos})
```

`request.signals` is a plain dict of the current signals. For typed, validated access, read them through a `Signals` class instead (the same one you passed to `<c-lbr.signals :schema=...>`). See [Server actions]({% doc_url '3_reactivity/5_server_actions.md' 'guide' %}) for the full round trip.

## Keeping state in the URL with `syncQuery`

Add `syncQuery` to write the signals back into the URL query string on every change, and restore them on load. Use it for state a user would bookmark or share, like filters, sort, and pagination:

```html
<c-lbr.signals :schema=signals syncQuery />
```

Never sync free-text form input such as names or emails. It leaks the values into the URL. A page can have several `<c-lbr.signals>` tags, so keep URL-persisted query state and page-local state on separate declarations and apply `syncQuery` only to the first:

```html
<c-lbr.signals id="query" :schema=query_signals syncQuery />
<c-lbr.signals id="ui" :schema=ui_signals />
```

`syncQuery` writes an opaque bag that it restores automatically on load, which is right for state nobody reads back. When you want a clean, shareable URL (`?q=atlas&sort=mrr&page=2`), use [`c-lbr.replace-url`]({% doc_url '3_reactivity/7_reference.md' 'guide' %}) instead: it writes whatever URL the server names, and `Signals.from_query` reads it back on a cold load. Pick one, never both. The [data-table block](/blocks/data-table/) is a live example: search, sort, and pagination all sync to the address bar with `c-lbr.replace-url`.

## Per-instance signal names

Signals are global to the page. Two copies of the same widget share a signal unless you give each one its own name. Derive the name from an `id` the caller passes:

{% verbatim %}
```html
<c-vars id="cp" />

<c-lbr.signals data-signals="{cp_{{ id }}: false}" />

<div
    data-on:click="$cp_{{ id }} = !$cp_{{ id }}"
    data-class="{'active': $cp_{{ id }}}"
>
    ...
</div>
```
{% endverbatim %}

```html
<c-my-widget id="a" />
<c-my-widget id="b" />
```

The dynamic name goes in a `data-signals` **value**, not a `$`-prop name. Cotton captures attribute names literally, so {% verbatim %}`{{ id }}`{% endverbatim %} only expands inside an attribute value.

## Computing an initial value in the browser

When a starting value has to be computed on load (reading `matchMedia`, or something already in the DOM), write a raw `data-signals` attribute **on** `<c-lbr.signals>`. Any non-`$` attribute is forwarded as-is and evaluated as JavaScript, and you still get the runtime loaded:

```html
<c-lbr.signals
    data-signals="{theme: (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')}"
/>
```

Do not mix a raw `data-signals` and `$` props on the same element. Passing `data-signals` through `<c-lbr.signals>` is the only time you should write it by hand.

See the [Reference]({% doc_url '3_reactivity/7_reference.md' 'guide' %}) for every prop, and [Events & bindings]({% doc_url '3_reactivity/4_events_and_bindings.md' 'guide' %}) for reading and writing signals from the page.
