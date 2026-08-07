---
title: Composition
description: "Structure labb templates as a project grows. Extract repeated interface patterns, use components with intent, and verify props and icon names."
keywords: "labb patterns, django-cotton best practices, django ui structure, labb composition, django template structure"
---

{% load docs_tags %}

As a page grows, give repeated pieces a name and move them out of the page template. The result is easier to scan, safer to change, and simpler to reuse.

## Extract a repeated pattern

A component can contain other components. When the same chunk of markup appears more than once, turn it into a component named after the thing it represents.

This product grid contains three cards.

<c-lbdocs.component_example path="guide/composition/product-grid" previewStyle="block" />

Writing the card three times would bury the grid’s structure in repeated markup. After extracting it, the template shows the page’s job at a glance.

{% verbatim %}
```html
<div class="grid gap-4 sm:grid-cols-3">
    {% for product in products %}
        <c-product-card :product="product" />
    {% endfor %}
</div>
```
{% endverbatim %}

A page template should expose its main regions, such as a header, filter bar, and product grid. If nested `<div>` tags hide those regions, extract the part with its own purpose. [Writing components]({% doc_url '2_building_uis/2_writing_components.md' 'guide' %}) shows how to build it.

## Use the component for the job

Use a labb component when one matches the interface element you need. `<c-lb.button>` carries the same styling and behaviour as the other buttons in the project. A hand-written `<button class="...">` needs that work repeated and maintained.

Use plain HTML for structure that does not need a component, such as `<section>` or a table’s `<thead>`. Components should capture a reusable interface pattern, not replace each HTML element.

## Look up names before using them

Unknown props are ignored. An invalid icon name renders no icon. Inspect the component and search the icon catalogue before you add either to a template.

```bash
labb components inspect button
labb icons search "arrow,heart"
```

## Related

<c-lbdocs.doc_card.grid cols="2">
  <c-lbdocs.doc_card title="Writing components" summary="c-vars, props, slots, and attrs" href="{% doc_url '2_building_uis/2_writing_components.md' 'guide' %}" icon="rmx.code-box" />
  <c-lbdocs.doc_card title="Components" summary="Every component, with live examples" href="{% url 'ui_docs' %}" icon="rmx.layout-grid" />
</c-lbdocs.doc_card.grid>

<c-lbdocs.block_grid refs="lb/settings/profile, lb/settings/team-members, lb/settings/workspace" />
