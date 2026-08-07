---
title: Blocks
description: "Add reusable page sections and full Django features from labb blocks. Create a collection, install a block, and connect it to your app."
keywords: "labb blocks, django ui blocks, labb block add, django feature blocks, labb block cli"
---

{% load docs_tags %}

A block is a page section or feature that the CLI copies into your project. You own the resulting code and can change it to fit the application.

Choose between frontend and fullstack blocks.

<div class="not-prose my-6 grid gap-3 sm:grid-cols-2">
  <div class="rounded-xl border border-base-300 p-4">
    <div class="flex items-center gap-2 text-sm font-medium">
      <c-lbi n="rmx.html5" w="16" h="16" class="text-base-content/50" />
      Frontend
    </div>
    <p class="mt-1 text-sm text-base-content/60">Templates and the components they use. A pricing section, a settings form.</p>
  </div>
  <div class="rounded-xl border border-base-300 p-4">
    <div class="flex items-center gap-2 text-sm font-medium">
      <c-lbi n="rmx.stack" w="16" h="16" class="text-base-content/50" />
      Fullstack
    </div>
    <p class="mt-1 text-sm text-base-content/60">Models, fixtures, views, urls and templates. Fully interactive end to end, on real data.</p>
  </div>
</div>

Frontend blocks provide templates and components. Fullstack blocks also include models, views, URLs, and seed data. Use a fullstack block when you want a working feature as a starting point.

## Add a block

<c-lbdocs.steps>

<c-lbdocs.steps.step number="1" title="Check you have labb installed">

Blocks require a `labb.yaml` in the project root. If your project does not have one, start with [Installation]({% doc_url '1_getting_started/2_installation.md' 'guide' %}).

```bash
labb init --defaults   # only if labb.yaml does not exist
```

`--defaults` creates `labb.yaml` and the CSS starter files without asking configuration questions.

</c-lbdocs.steps.step>

<c-lbdocs.steps.step number="2" title="Find a block">

Browse the [block gallery](/blocks/) or search from the command line. Block references follow `vendor/category/slug`; the official collection uses `lb`.

```bash
labb block list
labb block search "table"
```

Each result includes its reference and type.

</c-lbdocs.steps.step>

<c-lbdocs.steps.step number="3" title="Create a collection">

A collection is a Django app that holds the blocks you install. `labb block add` creates the default collection automatically when one does not exist, so run this step only when you want to choose its name or path.

```bash
labb block init --name blocks
```

This command adds the collection and the official source to `labb.yaml`.

<c-lbdocs.codeblock.title title="labb.yaml">
```yaml
blocks:
  collections:
    - default: true
      name: blocks
      path: blocks
  sources:
    - name: labbhq
      url: https://github.com/labbhq/labb
      subdir: extras/blocks
```
</c-lbdocs.codeblock.title>

A source is a git repository containing `blocks.yaml` and `index.yaml`. When the collection lives inside a larger repository, `subdir` points at it. The official collection ships from `extras/blocks` in the labb monorepo.

</c-lbdocs.steps.step>

<c-lbdocs.steps.step number="4" title="Add the block">

```bash
labb block add lb/data-table/customers
```

`labb block add` creates the default `blocks` collection and adds the official source when they are missing. Otherwise it copies the block files into the existing collection.

</c-lbdocs.steps.step>

<c-lbdocs.steps.step number="5" title="See what changed">

After installation, the collection contains the copied block files.

```
myproject/                      myproject/
  manage.py                       manage.py
  labb.yaml                       labb.yaml
  myapp/                          myapp/
  templates/                      templates/
                                  blocks/                   <- the collection
                                    apps.py
                                    migrations/
                                    fixtures/lb.json        <- seed data
                                    models/__init__.py      <- imports the vendor models
                                    lb/
                                      models/               <- shared vendor models
                                      data-table/customers/
                                        block.yaml
                                        views.py
                                        urls.py
                                        tour.yaml
                                    templates/
                                      cotton/customers/     <- components, resolve everywhere
                                      lb/data-table/customers/pages/index.html
```

For a fullstack block, `models/__init__.py` imports the vendor models so Django discovers them. `fixtures/lb.json` uses your collection’s app label.

</c-lbdocs.steps.step>

<c-lbdocs.steps.step number="6" title="Wire it up">

Add the collection to `INSTALLED_APPS`:

<c-lbdocs.codeblock.title title="settings.py">
```python
INSTALLED_APPS = [
    # ... other apps
    'labb',
    'blocks',
]
```
</c-lbdocs.codeblock.title>

Use `include_blocks` to include the block routes.

<c-lbdocs.codeblock.title title="urls.py">
```python
from labb.contrib.blocks import include_blocks
import blocks

urlpatterns = [
    path("", include_blocks(blocks)),
]
```
</c-lbdocs.codeblock.title>

For a fullstack block, create the tables and load the seed data:

```bash
python manage.py makemigrations blocks
python manage.py migrate
python manage.py loaddata lb
```

</c-lbdocs.steps.step>

<c-lbdocs.steps.step number="7" title="Run it" last>

```bash
labb dev                    # CSS watcher
python manage.py runserver
```

Open the block’s page. A fullstack block now runs against your database, including its search, sorting, and pagination.

</c-lbdocs.steps.step>

</c-lbdocs.steps>

## Explore the interactive tour

Open a fullstack block in the [block gallery](/blocks/), switch the previewer to **Code**, and use the tour panel beside the source. It walks through the view, templates, and components that make up the feature.

## Related

<c-lbdocs.doc_card.grid cols="2">
  <c-lbdocs.doc_card title="Composition" summary="How a block's templates are structured" href="{% doc_url '2_building_uis/1_composition.md' 'guide' %}" icon="rmx.compasses-2" />
  <c-lbdocs.doc_card title="Reactivity" summary="How fullstack blocks stay interactive over plain Django views" href="{% doc_url '3_reactivity/1_overview.md' 'guide' %}" icon="rmx.flashlight" />
</c-lbdocs.doc_card.grid>
