---
title: Server actions
description: "Server-driven updates in labb with c-lbr.get, post, and delete. Send a request to a normal Django view, read request.signals, and morph the response into the page. No JSON endpoints."
keywords: "labb server actions, c-lbr.get post delete, request.signals, is_datastar, django ajax without javascript, datastar django views"
---

When the change involves data the server owns, use a server action. The [`c-lbr.` action components]({% doc_url '3_reactivity/7_reference.md' 'guide' %}) (`<c-lbr.get>`, `<c-lbr.post>`, and `<c-lbr.delete>`, thin Cotton wrappers over [Datastar](https://data-star.dev/)) send a request to a normal Django view, and Datastar morphs the response into the page.

Wrap the element that triggers the action. This search box re-runs a Django view as the user types:

```html
<c-lbr.get to="todos:index" on="input__debounce.300ms">
    <c-lb.input type="search" bind="filters.q" placeholder="Search todos" />
</c-lbr.get>
```

The view is an ordinary Django view. It reads the current [signals]({% doc_url '3_reactivity/2_signals.md' 'guide' %}) from `request.signals`, does its work, and returns the whole page. Datastar compares the response with what is on screen and morphs only the parts that changed:

```python
def index(request):
    q = request.signals.get("filters", {}).get("q", "")
    todos = Todo.objects.filter(text__icontains=q)
    return render(request, "todos/index.html", {"todos": todos})
```

There is no separate JSON endpoint and no partial template. The same view serves the first page load and every update after it. The [data-table block](/blocks/data-table/) builds search, sort, and pagination this way, and the [dashboard block](/blocks/dashboard/) drives live charts from a server action.

## Wrap the trigger, not the container

Put the action as close as possible to the element that fires it. Wrapping a whole card means every click anywhere inside it fires the action:

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

`<c-lbr.post>` is the exception: it renders a `<form>` and legitimately wraps its own inputs. Keep layout containers outside it.

## `c-lbr.get` for reads and navigation

`<c-lbr.get>` fires a GET on any event. Use it for search, sort, pagination, filtering, and navigation. The `on` prop chooses the event, and `before` runs an expression first, usually to set a signal:

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

`before` is raw, unescaped JavaScript. Only ever put hardcoded expressions in it, such as signal assignments and integer primary keys from the ORM. Never interpolate user text into it.

## `c-lbr.post` for forms

`<c-lbr.post>` renders a real `<form>` and, on submit, posts the current signal bag as JSON. csrf is handled for you, so there is no manual `{% csrf_token %}`. Bind the inputs to signals and read them from `request.signals` in the view:

```html
<c-lbr.signals $text="" />

<c-lbr.post to="todos:create">
    <c-lb.input type="text" bind="text" placeholder="What needs doing?" required />
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

`request.is_datastar` is `True` when the request came from a reactive action. Return the page for an in-place update, or redirect for a full navigation. That one check lets the same view work with and without reactivity. A real `<form>` is what makes password managers and Enter-to-submit work, so use it for anything a user submits. The [auth blocks](/blocks/auth/) show sign-in and register forms with live validation built this way.

For a POST that is not a form submit (bulk actions, row buttons), give `<c-lbr.post>` a `tag="div" on="click"`. It still posts the signal bag as JSON. If you instead need a classic form whose named inputs arrive in `request.POST`, opt in with `options="{contentType: 'form'}"`; `request.signals` is then empty by design, so carry any view state in the action URL.

## `c-lbr.delete` with a confirm

`<c-lbr.delete>` fires a DELETE, optionally behind a browser confirm dialog:

```html
<c-lbr.delete to="todos:delete" pk=todo.pk confirm="Delete this todo?">
    <c-lb.button variant="error" btnStyle="ghost" size="sm">Delete</c-lb.button>
</c-lbr.delete>
```

## How the update lands

Datastar does not replace the page. It morphs the response into the current DOM, keeping form focus and scroll position, and touching only what differs. It matches elements by their `id`, so give every region that changes between requests a stable `id`:

```html
<div id="todo-header">...</div>   {# the count updates here #}
<div id="todo-list">...</div>     {# items morph here #}
```

Always set an `id` on list items and table rows, for example {% verbatim %}`id="todo-{{ todo.pk }}"`{% endverbatim %}. Without stable ids, rows can flicker or merge when the list changes.

## Naming a target

`<c-lbr.target>` marks a named region as a stable anchor for updates, so you can refer to it by name from the server instead of by id:

{% verbatim %}
```html
<c-lbr.target name="todo-list">
    {% for todo in todos %}
        <div id="todo-{{ todo.pk }}">{{ todo.text }}</div>
    {% endfor %}
</c-lbr.target>
```
{% endverbatim %}

Server-side, `@todo-list` resolves to that target. Most views return the full page and let the morph sort out the diff; [Patterns]({% doc_url '1_getting_started/3_patterns.md' 'guide' %}) covers targets and finer-grained updates.
