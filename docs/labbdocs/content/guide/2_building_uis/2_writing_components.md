---
title: Writing components
description: "Build components for a labb project with c-vars, props, bindings, slots, and forwarded attributes."
keywords: "django cotton c-vars, django cotton slots, write django component, labb custom component, cotton attrs"
---

{% load docs_tags %}

Your components use the same conventions as labb’s. Put a template under `templates/cotton/`, then call it as a tag from another template. It can receive props and nested markup. [django-cotton](https://django-cotton.com/) documents the wider API.

## Create the template

Create a file in `templates/cotton/`. Its path determines the tag name.

<c-lbdocs.codeblock.title title="templates/cotton/product_card.html">
{% verbatim %}
```html
<c-vars title="" price="" />

<c-lb.card border>
    <c-lb.card.body>
        <c-lb.card.title>{{ title }}</c-lb.card.title>
        <p class="text-sm text-base-content/60">{{ price }}</p>
    </c-lb.card.body>
</c-lb.card>
```
{% endverbatim %}
</c-lbdocs.codeblock.title>

```html
<c-product-card title="Air Max Pro" price="£120" />
```

Hyphens become underscores in the filename and dots become directories. `<c-product-card>` maps to `cotton/product_card.html`. `<c-shop.product.card>` maps to `cotton/shop/product/card.html`. Check this mapping first when Django cannot find a component.

## Declare props with `c-vars`

List each prop in `<c-vars>` and provide a default. Undeclared attributes pass through to `attrs`.

```html
<c-vars title="" variant="primary" border />
```

A bare declaration creates a boolean prop. Include the attribute to enable it.

```html
<c-product-card title="Air Max Pro" border />
```

Omit the attribute to leave it off. You do not need `border="true"` or `:border="False"`.

## Bind values with a leading colon

A plain attribute passes text. A leading `:` passes the evaluated Python value. Use it for objects, numbers, lists, and context variables.

{% verbatim %}
```html
<!-- The literal string "product" -->
<c-product-card product="product" />

<!-- The Product object -->
<c-product-card :product=product />

<!-- Python literals also work -->
<c-product-card :count=3 :tags="['new', 'sale']" />
```
{% endverbatim %}

<c-lb.alert variant="warning" alertStyle="outline" class="my-4">
<span>Do not wrap a context variable in `{% verbatim %}{{ }}{% endverbatim %}` inside a component attribute. Django turns it into text before the component receives it. Write `:product=product`.</span>
</c-lb.alert>

Give a bound prop a typed default, such as `<c-vars :product="{}" :count=0 />`.

## Accept markup with slots

`{% verbatim %}{{ slot }}{% endverbatim %}` holds the content between the opening and closing tags.

<c-lbdocs.codeblock.title title="templates/cotton/panel.html">
{% verbatim %}
```html
<c-vars title="" />

<section class="rounded-xl border border-base-300 p-4">
    <h2 class="font-semibold">{{ title }}</h2>
    {{ slot }}
</section>
```
{% endverbatim %}
</c-lbdocs.codeblock.title>

```html
<c-panel title="Shipping">
    <p>Anything here lands in the slot.</p>
</c-panel>
```

Name a slot when the component needs more than one content area. `<c-slot name="header">` fills `{% verbatim %}{{ header }}{% endverbatim %}`.

{% verbatim %}
```html
<c-panel>
    <c-slot name="header"><strong>Shipping</strong></c-slot>
    Body content goes in the default slot.
</c-panel>
```
{% endverbatim %}

Use a named slot for markup. Use a prop for a short text value.

## Forward the rest with `attrs`

`{% verbatim %}{{ attrs }}{% endverbatim %}` outputs attributes that the component did not declare. Add it to the root element so callers can pass `id`, `data-*`, and `aria-*`. Declare and merge `class` so callers can extend the component’s styling.

{% verbatim %}
```html
<c-vars title="" class="" />

<div class="rounded-xl border p-4 {{ class }}" {{ attrs }}>
    {{ slot }}
</div>
```
{% endverbatim %}

```html
<c-panel id="shipping" class="mt-6" data-testid="panel">…</c-panel>
```

Reactive attributes also pass through `attrs`. In `data-on:click` and `data-bind:*`, the colon is part of the attribute name. Only a leading colon binds a Python value.

## Compound components

A directory with `index.html` and sibling templates creates a component family. labb’s `card` uses this structure.

```
templates/cotton/shop/product/index.html   ->  <c-shop.product>
templates/cotton/shop/product/price.html   ->  <c-shop.product.price>
```

Use this structure when a component has distinct pieces instead of adding a long list of props.

## Related

<c-lbdocs.doc_card.grid cols="2">
  <c-lbdocs.doc_card title="Composition" summary="When to extract a component in the first place" href="{% doc_url '2_building_uis/1_composition.md' 'guide' %}" icon="rmx.compasses-2" />
  <c-lbdocs.doc_card title="Reactivity" summary="Make your own components interactive" href="{% doc_url '3_reactivity/1_overview.md' 'guide' %}" icon="rmx.flashlight" />
</c-lbdocs.doc_card.grid>
