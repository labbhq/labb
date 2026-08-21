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

## Keep signal state through morphs

A [server action]({% doc_url '3_reactivity/5_server_actions.md' 'guide' %}) re-renders the whole page, including the `<c-lbr.signals>` declaration. `:schema` and `$` declarations behave differently after that morph.

A `:schema` declaration seeds signals the browser does not have, then sends back only fields the view changed. Suppose an input sends a request at `atla` and you type `atlas` before its response arrives. If the view did not assign `q`, labb leaves `q` alone.

A `$` declaration cannot identify fields the view changed, so labb reapplies its declared value with each morph. Add `ifmissing` for a value the browser owns after the first render:

```html
<c-lbr.signals $open="false" ifmissing />
```

Without it, opening the dropdown and then triggering any server action closes it again.

A view changes a schema signal by assigning to it:

```python
def index(request):
    s = TodoSignals(request)
    s.page = min(s.page, total_pages)   # a clamp the browser must accept
    return render(request, "todos/index.html", {"signals": s})
```

An assignment sends a field back only when its value differs. `s.page = 1` on a page that was already `1` sends nothing.

Two cases need `mark_changed`, because the value alone does not show the intent:

```python
s.mark_changed("page")          # overwrite even though the value matches
ui.selected["7"] = False        # in-place mutation of a Dict field
ui.mark_changed("selected")     # ...never passes through the assignment
```

Datastar reapplies a changed signal declaration only when its rendered attribute changes. Two consecutive responses that set a signal to the same value apply it once. Use `Signals.patch()` in an `SSEResponse` when the server must apply the same value more than once.

## Bound fields and morphing

A bound field's value belongs to its signal. labb marks `<c-lb.input>`, `<c-lb.checkbox>`, `<c-lb.toggle>`, and `<c-lb.range>` so Datastar leaves their values intact while it morphs the page. To change one from the server, change its signal.

Datastar updates a `<c-lb.select>` through its `<option>` attributes and a `<c-lb.textarea>` through its child text, so the same marker cannot protect them. Render their selected state or text from the bound signal rather than from the record:

```html
<c-lb.select :bind=edit_signals.fields.status>
    {% for value, label in status_choices %}
    <option value="{{ value }}" {% if edit_signals.status == value %}selected{% endif %}>{{ label }}</option>
    {% endfor %}
</c-lb.select>
```

Read `edit_signals.status` rather than `customer.status` so an unsaved choice survives the next morph.

## A search box, step one

The next three pages build a search control one step at a time. It starts with two unused signals.

<c-lbdocs.component_example path="guide/reactivity/thread-1-signals" previewStyle="flex-col" />

Continue to [Events & bindings]({% doc_url '3_reactivity/3_events_and_bindings.md' 'guide' %}) to connect the signals to the search control. The [Reactivity reference]({% doc_url '5_references/7_reactivity_reference.md' 'guide' %}) lists every prop.
