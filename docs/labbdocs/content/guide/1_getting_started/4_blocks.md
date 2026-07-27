---
title: Blocks
description: "Add ready-made UI and full features to a Django project with labb blocks: install from a source with labb block add, then wire the collection into your app."
keywords: "labb blocks, django ui blocks, labb block add, django feature blocks, labb block cli"
---

Blocks are installable slices of a labb UI. A block can be frontend-only (a pricing section, a settings form) or fullstack (models, views, urls, and templates for a working feature like a searchable customer table). You add a block into your own project and own the code from then on. There is no runtime dependency on the source.

## What a block is

Every block belongs to a collection published from a source repo, and is named `vendor/category/slug`. The official collection uses the `lb` vendor, so a block reference looks like:

```
lb/data-table/customers
```

- **Frontend blocks** drop in templates and the components they use.
- **Fullstack blocks** also bring models, fixtures, views, and urls so the feature works end to end.

## Browse the catalogue

List or search what a configured source offers before you add anything:

```bash
labb block list
labb block search "table"
```

Each result prints its `vendor/category/slug` reference and whether it is frontend or fullstack.

## Add a block

Blocks go into a collection, an ordinary Django app that holds the blocks you install. Create one once, then add blocks into it:

```bash
# create a collection app (defaults to ./blocks)
labb block init --name blocks

# add a block into it
labb block add lb/data-table/customers
```

## What lands in your project

`labb block add` copies the block's code into your collection:

- **Cotton components** merge into the global `templates/cotton/` root so they resolve everywhere.
- **Page templates** land under `<collection>/templates/<vendor>/<category>/<slug>/`.
- **Fullstack blocks** also add `models/`, `fixtures/`, `views.py`, and `urls.py` to the collection, plus the block's `block.yaml` manifest and its `tour.yaml`.

Add the collection to `INSTALLED_APPS` and include its urls, the same as any Django app:

<c-lbdocs.codeblock.title title="settings.py">
```python
INSTALLED_APPS = [
    # ... other apps
    'labb',
    'blocks',
]
```
</c-lbdocs.codeblock.title>

For a fullstack block, run migrations and load any fixtures it shipped:

```bash
python manage.py migrate
python manage.py loaddata <fixture-name>
```

## Preview and follow the tour

Start your dev server and open the block's page to see it running:

```bash
labb dev                 # CSS watcher
python manage.py runserver
```

Fullstack blocks ship a `tour.yaml` teaching layer that walks through how the block is built, from the view down to the components. Read it alongside the code to learn the patterns the block uses, then adapt the block to your own data.

## Keep going

<c-lbdocs.doc_card.grid cols="2">
  <c-lbdocs.doc_card title="Components" summary="Every component the blocks are built from" href="{% url 'ui_docs' %}" icon="rmx.layout-grid" />
  <c-lbdocs.doc_card title="Reactivity" summary="How fullstack blocks stay interactive over plain Django views" href="{% doc_url '3_reactivity/1_overview.md' 'guide' %}" icon="rmx.flashlight" />
</c-lbdocs.doc_card.grid>
