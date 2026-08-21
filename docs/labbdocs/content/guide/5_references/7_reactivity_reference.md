---
title: Reactivity
description: "Reference for labb’s reactive components, signal bindings, and server request helpers."
keywords: "labb c-lbr reference, datastar django, labb signals api, django reactivity reference"
---

Use these components and attributes to keep browser state, component props, and Django views in sync. The `c-lbr.` components wrap [Datastar](https://data-star.dev/), which carries signals with requests and applies HTML updates. Start with the [Reactivity overview]({% doc_url '3_reactivity/1_overview.md' 'guide' %}) if you want the guided version.

## `c-lbr.signals`

Declare the state a page needs and load the reactivity runtime. Put the declaration near the top of the page body.

```html
<!-- Scalars are strings, except "true" and "false", which become booleans. -->
<c-lbr.signals $count="0" $filters.q="" $open="false" />

<!-- Use a : binding for a number, list, object, or context value. -->
<c-lbr.signals :$config="{'page': 1, 'sort': 'name'}" />

<!-- A typed schema instance supplied by the view. -->
<c-lbr.signals :schema=signals syncQuery />
```

Use a plain `$name="..."` prop for a string. For a number, list, or object, add `:` before the prop name. For example, `$page="1"` declares the string `"1"`, while `:$page="1"` declares the number `1`.

Add `ifmissing` when a `$` declaration holds state the browser owns after the first render, so a later morph does not reset it. A `:schema` declaration does this on its own. See [who owns a signal]({% doc_url '3_reactivity/2_signals.md' 'guide' %}).

Add `syncQuery` when filters, sorting, or pagination should survive a refresh and appear in a shareable URL. `ReactivityMiddleware` restores those values before the view reads its signals. See [URL state]({% doc_url '3_reactivity/6_patterns.md' 'guide' %}) for the pattern and its trade-offs.

<c-lbdocs.api_table component_name="lbr.signals" />

You can declare nested signals with dynamic props such as `$filters.q=""`. Give each declaration an `id` when a page has more than one `<c-lbr.signals>` element.

## Reactive props

Prefix a component prop with a signal name to update it in the browser. The value after the colon supplies the first server-rendered value.

```html
<c-lb.badge variant="$status:success" size="lg">Active</c-lb.badge>
```

labb recalculates the prop when `$status` changes. A reactive prop loads the runtime even without a separate action. labb also includes styles for the prop’s possible component variants in the generated CSS.

## Client-side attributes

These Datastar attributes handle browser-only interactions. They work after a `c-lbr.` component or reactive prop loads the runtime. Expressions receive the event as `evt` and the element as `el`.

| Attribute | Use |
|-----------|-----|
| `bind="$filters.q"` | Keep a form component and a signal in sync. Accepts a `$` path, a bare path such as `filters.q`, or `schema.fields.q`. |
| `data-on:click="$open = !$open"` | Run an expression for a DOM event. Add `__debounce.300ms` or `__throttle.50ms` when the event fires often. |
| `data-show="$open"` | Show or hide an element. |
| `data-text="$label"` | Replace an element’s text. |
| `data-class="{'active': $open}"` | Add or remove classes. A key can contain several space-separated classes. |
| `data-attr:href="$url"` | Set an attribute from a signal. |

## `c-lbr.get`

Send a GET request when the wrapped element fires its event.

```html
<c-lbr.get to="todos:detail" pk=todo.pk>
    <c-lb.button>Open</c-lb.button>
</c-lbr.get>
```

<c-lbdocs.api_table component_name="lbr.get" />

## `c-lbr.post`

Send a POST request. On a form, it runs on submit and sends the current signal bag as JSON, which you read from `request.signals`. labb handles CSRF protection. Pass `options="{contentType: 'form'}"` when a view expects a classic form body in `request.POST`.

```html
<c-lbr.signals $text="" />

<c-lbr.post to="todos:create">
    <c-lb.input type="text" bind="$text" required />
    <c-lb.button type="submit" variant="primary">Add</c-lb.button>
</c-lbr.post>
```

<c-lbdocs.api_table component_name="lbr.post" />

## `c-lbr.delete`

Send a DELETE request. Add `confirm` when the browser should ask before it sends the request.

```html
<c-lbr.delete to="todos:delete" pk=todo.pk confirm="Delete this todo?">
    <c-lb.button variant="error">Delete</c-lb.button>
</c-lbr.delete>
```

<c-lbdocs.api_table component_name="lbr.delete" />

## `c-lbr.target`

Name a stable update region. In a Django response, `@name` resolves to this element.

```html
<c-lbr.target name="results">
    ...
</c-lbr.target>
```

<c-lbdocs.api_table component_name="lbr.target" />

## `c-lbr.replace-url`

Replace the current address without navigating. Use it when an action changes a route or record URL. It does not serialize signal state. Use `syncQuery` on `<c-lbr.signals>` for filters, sorting, and pagination.

```html
<c-lbr.replace-url to="/settings/billing/" />
```

<c-lbdocs.api_table component_name="lbr.replace-url" />

## In a Django view

Reactive requests include the current signal bag. Read it from `request.signals`.

```python
def index(request):
    q = request.signals.get("filters", {}).get("q", "")
    return render(request, "todos/index.html", {"todos": search(q)})
```

| Object | Use |
|--------|-----|
| `request.signals` | The current signals as a dictionary. |
| `request.is_datastar` | `True` for a reactive request. Use it when a view needs an in-place response for Datastar and a full-page response otherwise. |

`ReactivityMiddleware` reads the signals before the view runs. Add it to `MIDDLEWARE`:

<c-lbdocs.codeblock.title title="settings.py">
```python
MIDDLEWARE = [
    # ...
    "labb.middleware.ReactivityMiddleware",
]
```
</c-lbdocs.codeblock.title>

### Typed signals

Define a `Signals` class when you want validated, typed fields instead of reading the dictionary by hand.

```python
from labb.signals import Signals, Str, Int

class TodoSignals(Signals):
    q = Str(path="filters.q", default="")
    page = Int(default=1, min_value=1)

def index(request):
    signals = TodoSignals(request)
    return render(request, "todos/index.html", {"signals": signals, "todos": search(signals.q)})
```

Pass the instance to `<c-lbr.signals :schema=signals />` to declare the same state in the browser.

### Sending a change back

Assigning to a field is how a view changes a signal. labb sends that field back only when its value differs and leaves the other schema signals unchanged.

```python
s = TodoSignals(request)
s.page = min(s.page, total_pages)   # sent only if the clamp did something
```

| Method | What it does |
|---|---|
| `s.mark_changed("page")` | Send a field even though its value already matches what the browser sent |
| `s.mark_changed()` | Send every field |
| `s.changed` | Names of the fields selected to send back |
| `s.changed_signals_dict()` | Those fields as a nested signal dict |

`mark_changed` covers the two cases an assignment cannot express: overwriting a value the browser sent, and mutating a `Dict` or `List` field in place.

### Sending a forced patch

An HTML morph reapplies a changed signal declaration only when its rendered attribute changes. When the server must apply the same value more than once, return a signal patch through `SSEResponse` instead:

```python
from labb.reactivity import SSEResponse

def reset_page(request):
    signals = TodoSignals(request)
    signals.page = 1
    return SSEResponse([signals.patch("page")])
```

`signals.patch()` emits a Datastar signal event every time the response yields it. Pass field names to patch only those fields, or omit them to patch the whole schema.

### Schema fields in templates

`signals.q` is the parsed value that your view uses. `signals.fields.q` is its `SignalField` descriptor. It carries the field’s declared path, so you can pass it directly to a form component with a Cotton binding.

```html
<c-lbr.signals :schema=signals />

<c-lb.input type="search" :bind=signals.fields.q placeholder="Search" />
```

The input reads the descriptor’s `filters.q` path and renders `data-bind:filters.q`. That keeps the schema, template binding, and server-side value on the same name. Use a string path such as `bind="$filters.q"` for small page-local state.

A bind path may contain only word characters and dots. labb validates the rendered path, so a template-built path such as `bind="$selected.{{ customer.pk }}"` works when it renders to a valid path.
