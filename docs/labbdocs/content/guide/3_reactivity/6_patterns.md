---
title: Patterns
description: "Practical labb patterns for reusable widgets, URL state, targeted updates, and reactive charts."
keywords: "labb reactivity patterns, reactive widgets, reactive charts, django signal patterns, patch_component labb"
---

Use these patterns once signals, reactive props, and server actions are familiar.

## Keep event handlers short

Keep template event handlers short. Move longer logic into a named function in a `<script>` tag.

```html
<script>
    function randomize(data) {
        return data.map(() => Math.floor(Math.random() * 100));
    }
</script>

<c-lb.button data-on:click="$values = randomize($values)">Randomize</c-lb.button>
```

## Keep shareable state in the URL

Add `syncQuery` to keep filter, sort, and page state in the URL. On a first load, the middleware restores those values before your view reads its signals. The customers block uses this pattern for its search and status filter.

```html
<c-lbr.signals :schema=signals syncQuery />
```

The default flat encoding keeps URLs readable, with namespaced parameters such as `?lbr.filters.q=atlas&lbr.page=2`. Configure the query key or encoding in `LABB_SETTINGS` when you need a different format.

Do not sync free-text fields such as names or email addresses because the values appear in the URL. Keep query state and page-local state in separate `<c-lbr.signals>` declarations.

```html
<c-lbr.signals id="query" :schema=query_signals syncQuery />
<c-lbr.signals id="ui" :schema=ui_signals />
```

<c-lbdocs.block_grid refs="lb/data-table/with-filters, lb/data-table/customers, lb/data-table/expandable-rows" />

## Namespace signals in reusable widgets

Signals belong to the whole page. Give reusable widgets an `id` and build their signal names from it so instances do not share state.

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

Callers provide a unique `id` for each instance.

```html
<c-my-widget id="a" />
<c-my-widget id="b" />
```

Put the dynamic name in `data-signals`, not a `$` prop name. Cotton treats attribute names literally, so {% verbatim %}`{{ id }}`{% endverbatim %} only expands inside a value.

## Driving several components from one object signal

Put values that change together in one object signal. Update it with a helper that returns the full object. This badge and status line both read `$order`.

<c-lbdocs.component_example path="guide/reactivity/object-signal" previewStyle="flex-col" />

The reactive props and `data-text` attributes read the same object. Replacing `$order` updates each consumer.

## Server-side UI state

A client signal can select the server-rendered state. For inline editing, an Edit button sets a signal and refetches the page. The view renders the selected row in edit mode.

```python
def index(request):
    editing_pk = int(request.signals.get("ui", {}).get("editingPk", 0))
    return render(request, "contacts/index.html", {
        "contacts": Contact.objects.all(),
        "editing_pk": editing_pk,
    })
```

{% verbatim %}
```html
{% if contact.pk == editing_pk %}
    {# render the edit form #}
{% else %}
    {# render the read row, with an Edit button:
       before="$ui.editingPk={{ contact.pk }}" #}
{% endif %}
```
{% endverbatim %}

After saving, render the page with `editing_pk` set to `0`. Include `<c-lbr.signals $ui.editingPk="0" />` in the response to reset the browser signal too.

## Patching a single component from the server

Most views return the whole page. To update one region, use `patch_component` to render a Cotton component by name and morph it into the target.

```python
from labb.reactivity import SSEResponse, patch_component
from datastar_py.consts import ElementPatchMode

def refresh_table(request):
    props = build_table_props(request)
    def generate():
        yield patch_component(request, "@table", "app.table",
                              mode=ElementPatchMode.INNER, **props)
    return SSEResponse(generate())
```

Pass only props declared by the component’s `<c-vars>`. Render the same `<c-app.table ... />` inside `<c-lbr.target name="table">` on the full page so both paths share the component. Use `patch_template` for a region with several components or template logic.

## Reactive charts

A chart becomes reactive when its `data` prop reads a signal. Changing the signal animates the chart to the new dataset.

<c-lbdocs.component_example path="chart/line-reactive" previewStyle="flex-col" />

Declare the initial dataset as an object signal with a `:` binding. Define alternatives in a `<script>`, then assign one from `data-on:click`. A server action can return new chart data in `<c-lbr.signals>` too.

## Computing an initial value in the browser

Use raw `data-signals` on `<c-lbr.signals>` when the browser must calculate the initial value on load, such as from `matchMedia`. Any non-`$` attribute passes through and evaluates as JavaScript.

```html
<c-lbr.signals
    data-signals="{theme: (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')}"
/>
```

Do not combine raw `data-signals` and `$` props on the same element. This is the only case where you need to write `data-signals` yourself.

## Related

<c-lbdocs.doc_card.grid cols="2">
  <c-lbdocs.doc_card title="Reactivity reference" summary="The full API for every c-lbr component and prop" href="{% doc_url '5_references/7_reactivity_reference.md' 'guide' %}" icon="rmx.book-2" />
  <c-lbdocs.doc_card title="Composition" summary="Habits that keep a reactive template readable" href="{% doc_url '2_building_uis/1_composition.md' 'guide' %}" icon="rmx.compasses-2" />
</c-lbdocs.doc_card.grid>

<c-lbdocs.block_grid refs="lb/wizard/vertical-steps, lb/wizard/progress-minimal, lb/wizard/with-summary" />
