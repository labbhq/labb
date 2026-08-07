---
title: Reactivity
description: "API reference for labb reactivity: c-lbr.signals, reactive props, c-lbr.get / post / delete, c-lbr.target, request.signals, and the data- attributes."
keywords: "labb c-lbr reference, datastar django, labb signals api, django reactivity reference"
---

Every reactivity component and prop. The `c-lbr.` components are thin Cotton wrappers over [Datastar](https://data-star.dev/), which does the runtime work of transporting signals and morphing responses into the DOM. For a walkthrough, start with the [Overview]({% doc_url '3_reactivity/1_overview.md' 'guide' %}).

## `c-lbr.signals`

Declares signals for the page and loads the reactivity runtime. Place it near the top of the body.

```html
<!-- scalar values: "true"/"false" become booleans, everything else is a string -->
<c-lbr.signals $count="0" $filters.q="" $open="false" />

<!-- a number, list, or object from a Python literal or context variable -->
<c-lbr.signals :$config="{'page': 1, 'sort': 'name'}" />

<!-- a typed schema instance from the view -->
<c-lbr.signals :schema=signals syncQuery />
```

Set signals in whichever form fits. A plain `$name="..."` prop is JSON-encoded as a literal string, so `$page="1"` is the string `"1"`. For a number, list, or object, use a `:$name="..."` Cotton binding: `:$page="1"` is the number `1`.

<c-lbdocs.api_table component_name="lbr.signals" />

Signals also accept `$`-prefixed props (`$name="value"`, `$path.sub="value"`) which are not listed above because they are dynamic. The `id` attribute names the element, which matters when a page has more than one `<c-lbr.signals>`.

## Reactive props

Prefix any component prop with `$` and a signal name to make it reactive. The value after the colon is the fallback the server renders on first load:

```html
<c-lb.badge variant="$status:success" size="lg">Active</c-lb.badge>
```

When the signal changes, the component recomputes that prop in the browser. A single reactive `$`-prop loads the runtime on its own, so it works with no other setup. You do not list the possible values anywhere; labb includes the styles for every value of a reactive prop in your CSS automatically.

## Client-side attributes

For interactivity that stays in the browser, use these attributes directly. They are available on any element once a `c-lbr.` component or a reactive `$`-prop has loaded the runtime. In an expression, the event is `evt` and the element is `el`, both written without a `$` prefix.

| Attribute | Does |
|-----------|------|
| `bind="$filters.q"` | On a form component, keeps a signal in sync with the input. Accepts a `$`-prefixed path, a bare path (`bind="filters.q"`), or `schema.fields.q`. |
| `data-on:click="$open = !$open"` | Runs an expression on a DOM event. Add timing with `__debounce.300ms` or `__throttle.50ms`. |
| `data-show="$open"` | Shows or hides the element. |
| `data-text="$label"` | Sets the element's text. |
| `data-class="{'active': $open}"` | Toggles classes. A key may hold several space-separated classes. |
| `data-attr:href="$url"` | Sets any attribute reactively. |

## `c-lbr.get`

Fires a GET request on any DOM event. Wrap the element that triggers it.

```html
<c-lbr.get to="todos:detail" pk=todo.pk>
    <c-lb.button>Open</c-lb.button>
</c-lbr.get>
```

<c-lbdocs.api_table component_name="lbr.get" />

## `c-lbr.post`

Fires a POST request. Defaults to a `<form>` on submit and posts the current signal bag as JSON, so the view reads `request.signals`. csrf is handled for you, so there is no manual `{% templatetag openblock %} csrf_token {% templatetag closeblock %}`. To send a classic form-encoded body that the view reads from `request.POST`, opt in with `options="{contentType: 'form'}"`.

```html
<c-lbr.signals $text="" />

<c-lbr.post to="todos:create">
    <c-lb.input type="text" bind="$text" required />
    <c-lb.button type="submit" variant="primary">Add</c-lb.button>
</c-lbr.post>
```

<c-lbdocs.api_table component_name="lbr.post" />

## `c-lbr.delete`

Fires a DELETE request, optionally behind a browser confirm dialog.

```html
<c-lbr.delete to="todos:delete" pk=todo.pk confirm="Delete this todo?">
    <c-lb.button variant="error">Delete</c-lb.button>
</c-lbr.delete>
```

<c-lbdocs.api_table component_name="lbr.delete" />

## `c-lbr.target`

Marks a named region as a stable anchor for updates. Server-side, `@name` resolves to that element.

```html
<c-lbr.target name="results">
    ...
</c-lbr.target>
```

<c-lbdocs.api_table component_name="lbr.target" />

## `c-lbr.replace-url`

Writes a clean, shareable URL into the address bar (`?q=atlas&sort=mrr&page=2`) with `history.replaceState`, so search, sort, and pagination land in a link a user can copy. The server names the URL; `Signals.from_query` reads it back on a cold load. Use this when the URL must be shareable, and `syncQuery` on `<c-lbr.signals>` when nobody reads the state back. Never run both; they fight over the address bar.

```html
<c-lbr.replace-url to="customers:index" />
```

<c-lbdocs.api_table component_name="lbr.replace-url" />

## On the server

Reactive actions send the current signals with every request. Read them in the view:

```python
def index(request):
    q = request.signals.get("filters", {}).get("q", "")
    return render(request, "todos/index.html", {"todos": search(q)})
```

| Object | Description |
|--------|------|
| `request.signals` | A dict of the current signals. |
| `request.is_datastar` | `True` when the request came from a reactive action, so you can return the page for an in-place update or redirect otherwise. |

`ReactivityMiddleware` populates `request.signals`, so add it to `MIDDLEWARE`:

<c-lbdocs.codeblock.title title="settings.py">
```python
MIDDLEWARE = [
    # ...
    "labb.middleware.ReactivityMiddleware",
]
```
</c-lbdocs.codeblock.title>

### Typed signals

For validated, typed access, define a `Signals` class instead of reading the dict by hand:

```python
from labb.signals import Signals, Str, Int

class TodoSignals(Signals):
    q = Str(path="filters.q", default="")
    page = Int(default=1, min_value=1)

def index(request):
    s = TodoSignals(request)
    return render(request, "todos/index.html", {"signals": s, "todos": search(s.q)})
```

Pass the instance to `<c-lbr.signals :schema=signals />` to declare the same signals on the page, and to a form component with `<c-lb.input :bind=signals.fields.q />` to bind by field.
