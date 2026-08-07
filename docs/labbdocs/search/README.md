# labbdocs search

A ⌘K command palette on every docs page, a `/search` results page with type facets, and a build step that indexes guides, component pages, and icons.

It is off until you install it. A labbdocs site that never enables search renders no palette, no keyboard shortcut, and no JavaScript for either.

## Requirements

Search stores its index in Postgres and queries it with `SearchVector`, `SearchQuery`, and GIN indexes. These have no SQLite equivalent, so `migrate` fails outright rather than degrading.

> **Search requires PostgreSQL.** If the docs site runs on SQLite, leave search off.

Fuzzy matching adds a trigram index, which requires the `pg_trgm` extension. The migration creates it, but `CREATE EXTENSION` needs a superuser role. If the application connects as an unprivileged user, create it once as an admin first:

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

## Install

Add both apps. `labbdocs.search` is separate from `labbdocs` so that a site without Postgres can still install the docs package.

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "django.contrib.postgres",
    "labbdocs",
    "labbdocs.search",
]
```

Then mount the URLs. The path is yours to choose, and the palette and results page reverse every link against it:

```python
# urls.py
urlpatterns = [
    path("", include("labbdocs.urls")),
    path("search/", include("labbdocs.search.urls")),
]
```

Installing the app is what enables the feature. The base layout gates the palette on `apps.is_installed("labbdocs.search")`, so there is no separate on switch to forget.

## Build the index

```bash
python manage.py migrate
python manage.py build_docs guide
python manage.py build_search_index
```

Order matters. `build_search_index` reads the built doc output, so running it before `build_docs` indexes the previous build.

The command truncates and reinserts every row, so it is safe to re-run and always reflects current content. In deployment it belongs after `migrate`, as its own step.

Editing a `.md` file leaves search stale until you reindex. `build_docs` does not touch the index.

## Configuration

Every key under `LABB_DOCS["search"]` is optional.

```python
LABB_DOCS = {
    "types": { ... },
    "search": {
        "readers": [...],       # content sources; defaults to the three below
        "log_queries": False,   # record searches; off by default
        "shortcuts": [...],     # blank-query browse links
    },
}
```

### readers

A reader turns one content source into index rows. Three ship with labbdocs:

| Reader | Indexes |
|---|---|
| `labbdocs.search.readers.guides.GuidesReader` | Every declared doc type, at page and heading level |
| `labbdocs.search.readers.components.ComponentsReader` | Component doc pages, enriched with prop and variant names |
| `labbdocs.search.readers.icons.IconsReader` | Every icon in every installed pack |

`GuidesReader` reads from `LABB_DOCS["types"]`, so a doc type you declare is indexed without extra code. It skips `ui`, which `ComponentsReader` owns.

`IconsReader` needs `labbicons` installed. Without it the reader logs that it skipped itself, and the other sources still index.

Setting `readers` replaces the default list, so adding a source and removing one are the same edit:

```python
"readers": [
    "labbdocs.search.readers.guides.GuidesReader",
    "labbdocs.search.readers.icons.IconsReader",
    "myproject.search_readers.ChangelogReader",
]
```

A path that cannot be imported raises `ImproperlyConfigured` at build time. Failures during reading only log a warning, so one malformed file cannot cost the whole index.

### shortcuts

These links fill the palette before anyone types. The default is one per declared doc type. Override it when the site has surfaces that are not doc types, as labbio does for `/blocks/`:

```python
"shortcuts": [
    {"label": "Browse components", "href": "/docs/ui/", "icon": "rmx.layout-grid"},
    {"label": "Browse guides", "href": "/docs/guide/", "icon": "rmx.book-2"},
]
```

## Indexing your own content

A reader is any class with a `read()` method that yields dictionaries. There is no base class to inherit and nothing to register beyond the settings list.

```python
# myproject/search_readers.py
from django.urls import reverse

from labbdocs.search.models import SearchDocument


class ChangelogReader:
    type = SearchDocument.TYPE_GUIDE

    def read(self):
        for release in Release.objects.all():
            yield {
                "type": self.type,
                "title": f"Release {release.version}",
                "url": reverse("changelog", args=[release.version]),
                "category": "changelog",
                "summary": release.headline,
                "keywords": release.tags,
                "body": release.notes,
            }
```

Only `type`, `title`, and `url` are required. The rest default on the model.

Ranking weights the fields: `title` highest, then `keywords`, then `category` and `summary`, then `body`. Put the words someone would search for in `keywords` rather than relying on `body`.

Add the dotted path to `readers` and rebuild. `labbio/search_readers.py` is the worked example: it reads labbio's installed blocks and links through `blocks_detail`, a labbio URL name, which is why it lives in labbio rather than here.

## Query logging

Search can record what people searched for and how many results they got. It is off by default, because the query text is whatever a visitor typed and storing it in a database should be the site owner's decision.

```python
"log_queries": True,
```

It records submitted searches only. The palette searches as you type and logs nothing, so looking up `button` stores one row instead of six prefixes.

Rows carry the query, the result count, whether it matched, and a timestamp. No IP address, no user, no session key.

Read the log with:

```bash
python manage.py search_report --days 30
```

```
Top queries (30d, 412 searches)
  47  button
  31  chart

Zero results (18 queries, 4%)
   9  datepicker
   5  data table
```

The zero-result list is the useful half. It names the things people expected the docs to cover.

Rows stay until you delete them. There is no automatic expiry, so nothing removes data from the database on a schedule nobody set. To trim old rows, add this to a cron:

```bash
python manage.py search_report --purge-older-than 90
```

## Sites without search

With `labbdocs.search` uninstalled, the docs layout renders no palette markup, no ⌘K handler, and no search button in the top navigation. Nothing loads Datastar, so a static docs site ships no JavaScript.
