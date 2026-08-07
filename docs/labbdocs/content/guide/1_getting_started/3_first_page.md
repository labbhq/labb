---
title: Your first page
description: "Build a task list with a Django view and labb components. Render server-side data, compose a styled page, and use icons."
keywords: "labb first page, django labb tutorial, labb getting started, django component page, labb example view"
---

{% load docs_tags %}

Build a small task list with the Django patterns you already use: a view prepares context and a template renders it. labb supplies the page’s components and styles; Django renders the finished HTML on the server.

This is what you are building:

<c-lbdocs.component_example path="guide/first-page/task-list" previewStyle="block" />

## Add the view

Create a view that passes tasks and their open count to a template. labb does not change how views, queries, or template context work.

<c-lbdocs.codeblock.title title="tasks/views.py">
```python
from django.shortcuts import render

TASKS = [
    {"title": "Install labb", "done": True},
    {"title": "Write a view", "done": False},
    {"title": "Render a page", "done": False},
]


def today(request):
    return render(request, "tasks/today.html", {
        "tasks": TASKS,
        "open_count": sum(1 for task in TASKS if not task["done"]),
    })
```
</c-lbdocs.codeblock.title>

Map the site root to that view:

<c-lbdocs.codeblock.title title="urls.py">
```python
from django.urls import path
from tasks import views

urlpatterns = [
    path("", views.today, name="today"),
]
```
</c-lbdocs.codeblock.title>

## Build the template

Create `tasks/today.html`. The example extends the `base.html` you set up during [installation]({% doc_url '1_getting_started/2_installation.md' 'guide' %}); it needs `<c-lb.m.dependencies />` in its `<head>` so the compiled CSS loads.

Use labb components as tags. Nest them in the same structure you would use for HTML:

<c-lbdocs.codeblock.title title="tasks/today.html">
{% verbatim %}
```html
{% extends "base.html" %}

{% block content %}
<c-lb.card border class="w-full max-w-md">
    <c-lb.card.body>

        <div class="flex items-center justify-between">
            <c-lb.card.title>Today</c-lb.card.title>
            <c-lb.badge variant="primary" size="sm">{{ open_count }} open</c-lb.badge>
        </div>

        <c-lb.list>
            {% for task in tasks %}
            <c-lb.list.row>
                {% if task.done %}
                    <c-lbi n="rmx.checkbox-circle" w="18" h="18" class="text-success shrink-0" />
                    <span class="line-through text-base-content/40">{{ task.title }}</span>
                {% else %}
                    <c-lbi n="rmx.checkbox-blank-circle" w="18" h="18" class="text-base-content/30 shrink-0" />
                    <span>{{ task.title }}</span>
                {% endif %}
            </c-lb.list.row>
            {% endfor %}
        </c-lb.list>

        <c-lb.card.actions>
            <c-lb.button variant="primary" size="sm" icon="rmx.add">Add task</c-lb.button>
        </c-lb.card.actions>

    </c-lb.card.body>
</c-lb.card>
{% endblock %}
```
{% endverbatim %}
</c-lbdocs.codeblock.title>

## Read the component structure

`<c-lb.card>` contains `<c-lb.card.body>` and `<c-lb.card.actions>`. The dot identifies a component within the card family. Each piece has a focused responsibility, so you can arrange the card’s title, content, and actions without a long list of layout props.

The `{% verbatim %}{% for %}{% endverbatim %}` loop and `{% verbatim %}{% if %}{% endverbatim %}` branch remain ordinary Django template code. Components accept the surrounding content as a slot, so you can put loops, conditions, and variables inside them.

The `icon="rmx.add"` prop renders the button icon. The standalone `<c-lbi>` tags render the status icons in each row. Search the icon catalogue before adding a name: an invalid name produces no icon and no template error.

```bash
labb icons search "checkbox"
```

## Start the page

Run the CSS watcher and Django server in separate terminals:

```bash
labb dev                    # terminal 1
python manage.py runserver  # terminal 2
```

Open [http://localhost:8000](http://localhost:8000). If the page renders without styles, check that `labb dev` is running. It scans your templates for the utility classes it needs to compile.

## Next steps

You now have the basic labb workflow: keep your Django view, compose the template from components, and run the CSS watcher during development. Browse the component docs to expand the page, or extract repeated markup into a component of your own.

<c-lbdocs.block_grid :blocks="[
  {'name': 'Centred bold', 'type': 'fe', 'detail_url': '/blocks/hero/#centred-bold', 'thumbnail': '/static/lb/hero/centred-bold/thumbnails/centred-bold.light.png', 'thumbnail_dark': '/static/lb/hero/centred-bold/thumbnails/centred-bold.dark.png'},
  {'name': 'App screenshot', 'type': 'fe', 'detail_url': '/blocks/hero/#app-screenshot', 'thumbnail': '/static/lb/hero/app-screenshot/thumbnails/app-screenshot.light.png', 'thumbnail_dark': '/static/lb/hero/app-screenshot/thumbnails/app-screenshot.dark.png'},
  {'name': 'Split visual', 'type': 'fe', 'detail_url': '/blocks/hero/#split-visual', 'thumbnail': '/static/lb/hero/split-visual/thumbnails/split-visual.light.png', 'thumbnail_dark': '/static/lb/hero/split-visual/thumbnails/split-visual.dark.png'}
]" />

## Related

<c-lbdocs.doc_card.grid cols="2">
  <c-lbdocs.doc_card title="Components" summary="Every component, with live examples" href="{% url 'ui_docs' %}" icon="rmx.layout-grid" />
  <c-lbdocs.doc_card title="Icons" summary="Install labbicons and find icon names" href="{% doc_url '2_building_uis/3_icons.md' 'guide' %}" icon="rmx.shapes" />
</c-lbdocs.doc_card.grid>
