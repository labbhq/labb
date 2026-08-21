---
title: Server actions
description: "Use c-lbr actions to call ordinary Django views, read request.signals, and update the current page."
keywords: "labb server actions, c-lbr.get post delete, request.signals, is_datastar, django ajax without javascript, datastar django views"
---

Use a server action when Django owns the change. [`c-lbr.` action components]({% doc_url '5_references/7_reactivity_reference.md' 'guide' %}) such as `<c-lbr.get>`, `<c-lbr.post>`, and `<c-lbr.delete>` call a normal Django view. Datastar then updates the current page from the response.

Wrap the element that triggers the request. This search field calls a Django view as the user types.

```html
<c-lbr.get to="todos:index" on="input__debounce.300ms">
    <c-lb.input type="search" bind="$filters.q" placeholder="Search todos" />
</c-lbr.get>
```

The view reads the current [signals]({% doc_url '3_reactivity/2_signals.md' 'guide' %}) from `request.signals`, queries the data, and returns the whole page. Datastar compares the response with the DOM and updates the changed regions.

```python
def index(request):
    q = request.signals.get("filters", {}).get("q", "")
    todos = Todo.objects.filter(text__icontains=q)
    return render(request, "todos/index.html", {"todos": todos})
```

The same view serves the first page load and later updates.

<c-lbdocs.block_grid refs="lb/data-table/customers, lb/data-table/with-filters, lb/data-table/card-grid" />

## Reading signals on the server

Datastar sends the current signal bag with each action request. labb’s `ReactivityMiddleware` decodes it into `request.signals`, a plain dictionary.

For typed, validated access, use the same `Signals` class that you pass to `<c-lbr.signals :schema=...>`.

```python
def index(request):
    s = TodoSignals(request)
    todos = Todo.objects.filter(text__icontains=s.q)
    return render(request, "todos/index.html", {"todos": todos, "signals": s})
```

This keeps signal paths in one place. [Signals]({% doc_url '3_reactivity/2_signals.md' 'guide' %}) covers the declaration.

## Wrap the trigger, not the container

Place the action around the element that fires it. Wrapping an entire card makes each click inside the card trigger a request.

```html
{# Wrong: the entire card surface triggers #}
<c-lbr.get to="todos:detail" pk=todo.pk>
    <c-lb.card>...</c-lb.card>
</c-lbr.get>

{# Right: only the button fires #}
<c-lb.card>
    <c-lb.card.body>
        <c-lbr.get to="todos:detail" pk=todo.pk>
            <c-lb.button size="sm">Open</c-lb.button>
        </c-lbr.get>
    </c-lb.card.body>
</c-lb.card>
```

`<c-lbr.post>` is the exception because it renders a `<form>` around its inputs. Keep layout containers outside the form.

## `c-lbr.get` for reads and navigation

`<c-lbr.get>` sends a GET request on an event. Use it for search, sorting, pagination, filters, and navigation. `on` selects the event. `before` runs an expression first, usually to set a signal.

{% verbatim %}
```html
{# navigate #}
<c-lbr.get to="todos:detail" pk=todo.pk>
    <c-lb.button btnStyle="ghost" size="sm">View</c-lb.button>
</c-lbr.get>

{# fetch on load #}
<c-lbr.get to="todos:index" on="init" />

{# set a signal, then fetch #}
<c-lbr.get to="todos:index" before="$ui.editingPk={{ todo.pk }}">
    <c-lb.button btnStyle="ghost" size="sm">Edit</c-lb.button>
</c-lbr.get>
```
{% endverbatim %}

`before` contains raw JavaScript. Keep it to hardcoded expressions, signal assignments, and integer primary keys from the ORM. Do not interpolate user text into it.

## `c-lbr.post` for forms

`<c-lbr.post>` renders a real `<form>` and posts the current signal bag as JSON on submit. It handles CSRF. Bind inputs to signals and read them from `request.signals` in the view.

```html
<c-lbr.signals $text="" />

<c-lbr.post to="todos:create">
    <c-lb.input type="text" bind="$text" placeholder="What needs doing?" required />
    <c-lb.button type="submit" variant="primary">Add</c-lb.button>
</c-lbr.post>
```

```python
def create(request):
    if request.method == "POST":
        text = request.signals.get("text", "").strip()
        if text:
            Todo.objects.create(text=text)
        if request.is_datastar:
            return render(request, "todos/index.html", index_context(request))
    return redirect("todos:index")
```

`request.is_datastar` is `True` for a reactive action. Return the page for an in-place update or redirect after a normal navigation. A real `<form>` also supports password managers and Enter to submit, so use it for user-submitted data. The [auth blocks](/blocks/auth/) include sign-in and registration examples.

For bulk actions or row buttons, use `<c-lbr.post tag="div" on="click">`. It still posts the signal bag as JSON. For a classic form whose named inputs arrive in `request.POST`, use `options="{contentType: 'form'}"`. In that mode `request.signals` remains empty, so include view state in the action URL.

## `c-lbr.delete` with a confirm

`<c-lbr.delete>` fires a DELETE, optionally behind a browser confirm dialog:

```html
<c-lbr.delete to="todos:delete" pk=todo.pk confirm="Delete this todo?">
    <c-lb.button variant="error" btnStyle="ghost" size="sm">Delete</c-lb.button>
</c-lbr.delete>
```

## How the update lands

Datastar morphs the response into the current DOM while preserving form focus and scroll position. It matches elements by `id`, so give changing regions stable IDs.

```html
<div id="todo-header">...</div>   {# the count updates here #}
<div id="todo-list">...</div>     {# items morph here #}
```

Set an `id` on each list item and table row, such as {% verbatim %}`id="todo-{{ todo.pk }}"`{% endverbatim %}. Without stable IDs, rows can flicker or merge when the list changes.

## Naming a target

`<c-lbr.target>` gives an update region a stable name that server code can use.

{% verbatim %}
```html
<c-lbr.target name="todo-list">
    {% for todo in todos %}
        <div id="todo-{{ todo.pk }}">{{ todo.text }}</div>
    {% endfor %}
</c-lbr.target>
```
{% endverbatim %}

On the server, `@todo-list` resolves to that target. Most views return the whole page. [Patterns]({% doc_url '3_reactivity/6_patterns.md' 'guide' %}) covers targeted updates.
