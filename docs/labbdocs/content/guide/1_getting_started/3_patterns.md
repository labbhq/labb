---
title: Patterns
description: "Practices for building maintainable Django UIs with labb: composing components, keeping templates readable, and structuring reactivity from the basics to advanced signal patterns."
keywords: "labb patterns, django-cotton best practices, labb reactivity patterns, django ui structure, reactive widgets, reactive charts"
---

A few habits keep labb templates readable as a project grows. None of these are rules the framework enforces; they are what tends to work well. Composition comes first, then reactivity, from the everyday basics to a handful of advanced recipes.

## Composition

### Build from small components

A component can contain other components. Lean on that. When a chunk of markup appears more than once, move it into its own component and give it a name that says what it is:

```html
<!-- Instead of repeating this block for every product -->
<c-product-card :product="product" />
```

A good page template reads like an outline: a header, a toolbar, a list of items. If you have to scroll through a wall of `<div>` tags to find the structure, that is a sign to pull some of it out into a component.

### Reach for a component before raw HTML

If labb has a component for something, use it instead of hand-writing the markup. A `<c-lb.button>` stays consistent with the rest of your UI and the theme, where a raw `<button class="...">` drifts over time. The same goes for inputs, badges, cards, tables, and pagination.

Keep plain HTML for structure that has no component, like a `<section>` or a table's `<thead>`. The line is repetition and meaning, not "never write HTML."

### Check props and icons before you guess

Prop and icon names are easy to get subtly wrong. Look them up:

```bash
labb components inspect button   # props, types, and defaults
labb icons search "arrow"        # exact icon names
```

A wrong icon name fails quietly, so it is worth the two seconds.

## Reactivity basics

The everyday habits for adding interactivity. For the full picture of how signals and server actions fit together, see the [Reactivity]({% doc_url '3_reactivity/1_overview.md' 'guide' %}) guide.

### Declare signals with c-lbr.signals

When you add reactivity, declare your signals with `<c-lbr.signals>` rather than writing `data-signals` by hand. It sets up the signals and loads the runtime in one place:

```html
<c-lbr.signals $open="false" $filters.q="" />
```

### Keep local state local

If a change only affects how the page looks right now, keep it in the browser with signals and `data-` attributes. Do not send it to the server. A dropdown opening or a tab switching should feel instant and cost no request. Save server requests for changes the server owns. The [Reactivity]({% doc_url '3_reactivity/1_overview.md' 'guide' %}) guide covers the split.

### Keep event handlers short

An event handler in a template should be a short, readable expression. When the logic grows, move it into a named function in a `<script>` tag and call it:

```html
<script>
    function randomize(data) {
        return data.map(() => Math.floor(Math.random() * 100));
    }
</script>

<c-lb.button data-on:click="$values = randomize($values)">Randomize</c-lb.button>
```

### Give changing regions a stable id

When a server action updates the page, Datastar matches elements by their `id` to figure out what changed. Put an `id` on each region that updates, and on list rows especially:

```html
<div id="results">
    {% verbatim %}{% for item in items %}{% endverbatim %}
        <div id="item-{% verbatim %}{{ item.pk }}{% endverbatim %}">...</div>
    {% verbatim %}{% endfor %}{% endverbatim %}
</div>
```

Stable ids keep rows from flickering or merging when the list changes.

## Reactivity patterns (advanced)

Recipes built on signals, reactive props, and server actions. Each one is small and copyable.

### Reusable widgets need per-instance signal names

Signals are global to the page, so two instances of the same widget share a signal unless you namespace it. Give the component an `id` and derive the signal name from it:

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

Callers pass a unique `id` to each copy, and the two no longer collide:

```html
<c-my-widget id="a" />
<c-my-widget id="b" />
```

The dynamic name goes in a `data-signals` value, not a `$`-prop name. Cotton captures attribute names literally, so {% verbatim %}`{{ id }}`{% endverbatim %} only expands inside an attribute value.

### Driving several components from one object signal

When related values change together, hold them in one object signal and update it with a helper that returns the whole object. Keep the handler a short call and put the logic in a `<script>` function. Here a badge and a status line both read from one `$order` signal, and one button advances the whole object:

<c-lbdocs.component_example path="reactivity/object-signal" previewStyle="flex-col" />

The reactive props (`variant="$order.variant:warning"` and the two `data-text` reads) all point at the same object, so replacing `$order` updates every consumer at once.

### Server-side UI state

A client signal can decide what the server renders, which gives you inline editing with no client-side branching. An "Edit" button sets a signal and re-fetches; the view reads the signal and renders that one row in edit mode:

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

After saving, render the page with `editing_pk` reset to `0`. The form disappears because the server rendered read mode, not because of any client callback. To reset the signal itself, include a `<c-lbr.signals $ui.editingPk="0" />` in the response and the morph updates the client.

### Patching a single component from the server

Most views return the whole page and let the morph diff it. When you want to push one region without re-rendering everything, `patch_component` renders a Cotton component by name and morphs it in. Do not create a one-line partial just to wrap a component you already have:

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

Pass only the props the component's `<c-vars>` declares. The same page renders `<c-app.table ... />` inside a `<c-lbr.target name="table">`, so the full-page render and the patch share one source of truth. Reserve `patch_template` for regions that are genuinely a template with several components or template logic, not a single component.

### Reactive charts

A chart becomes reactive when you pass a signal to its `data` prop. Change the signal and the chart animates to the new data, no redraw call. Here two buttons swap the dataset by writing to `$chartData`:

<c-lbdocs.component_example path="chart/line-reactive" previewStyle="flex-col" />

Declare the initial dataset as an object signal (with a `:` binding so it is a real object, not a string), define the alternative datasets in a `<script>`, and assign one to the signal from a `data-on:click`. The same works for a server action: return the page with new chart data in `<c-lbr.signals>` and the chart updates on morph.

## Next steps

<c-lbdocs.doc_card.grid cols="2">
  <c-lbdocs.doc_card title="Reactivity" summary="How signals and server actions work" href="{% doc_url '3_reactivity/1_overview.md' 'guide' %}" icon="rmx.flashlight" />
  <c-lbdocs.doc_card title="Reactivity reference" summary="The full API for every reactivity component" href="{% doc_url '3_reactivity/7_reference.md' 'guide' %}" icon="rmx.book-2" />
</c-lbdocs.doc_card.grid>
