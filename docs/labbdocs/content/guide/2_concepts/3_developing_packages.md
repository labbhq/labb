---
title: Developing packages
description: "Build a third-party package for labb: ship django-cotton components and templates, publish CSS groups with labb-provides.yaml, and let projects install and subscribe to them."
keywords: "labb third party package, develop labb package, labb-provides.yaml, django cotton component library, labb css packages, publish labb components"
---

{% load docs_tags %}

A labb project pulls components, templates, and CSS from installed Python packages. `labb` itself is one such package. This guide shows how to build your own (a component pack, a theme, or a full feature library) so other projects can install it and subscribe to its CSS by name.

If you have not read [Building CSS]({% doc_url '2_concepts/2_building_css.md' 'guide' %}), start there. This guide assumes you know how the scan → build pipeline works.

## What a package ships

A labb-consumable package is an ordinary installable Python package that contains some combination of:

- **Templates**: django-cotton components under `templates/cotton/<ns>/` and/or example/page templates.
- **CSS**: themes or other stylesheets under a directory like `css/`.
- **`labb-provides.yaml`**: the manifest that publishes named CSS **groups** so consumers do not hardcode your internal paths.

```
my_pack/
  __init__.py
  labb-provides.yaml
  templates/
    cotton/
      mypack/
        card.html
  css/
    theme.css
```

<c-lb.alert variant="info" alertStyle="outline" class="my-4">
  <span>Use your own cotton namespace (e.g. <code>cotton/mypack/</code> → <code>&lt;c-mypack.card&gt;</code>). Do not ship components under <code>cotton/lb/</code>. That namespace belongs to the labb library.</span>
</c-lb.alert>

## Step 1: build your components

Author components with [django-cotton]({% doc_url '1_getting_started/2_introduction.md' 'guide' %}) the same way you would in an app. A component that composes labb components is fine. The consumer's build picks up their classes through your `components` group (next step).

Remember the rule from [Building CSS]({% doc_url '2_concepts/2_building_css.md' 'guide' %}): labb resolves a component's variant classes from **usage**, and Tailwind compiles **raw** utility classes it can scan literally. Your package's templates need both handled, which is what the groups are for.

## Step 2: publish CSS groups

Add a `labb-provides.yaml` at your package root declaring the groups you want consumers to subscribe to. Each group lists any of `components` (usage-scanned), `literals` (Tailwind `@source`), and `imports` (CSS inlined into the build):

```yaml
provides:
  components:
    components: [templates/cotton/mypack/**/*.html]
    literals:   [templates/cotton/mypack/**/*.html]
  theme:
    imports: [css/theme.css]
```

- Put templates that **use** `<c-lb.*>` or `<c-mypack.*>` under `components`.
- Put templates with **raw utility classes** (layout, spacing, etc.) under `literals`. When in doubt, list the same glob under both (labb de-dups).
- Put shippable CSS (themes, keyframes) under `imports`. If a file contains a daisyUI `@plugin "daisyui/theme"` block, `imports` is the right place: it is inlined so the plugin resolves in the consumer's project.

See the [`labb-provides.yaml` reference]({% doc_url '4_references/5_labb_provides.md' 'guide' %}) for the full schema.

## Step 3: package and distribute

Ship it as a normal Python package. Two things to get right so the files reach consumers:

1. **Include the data files**: `labb-provides.yaml`, `templates/**`, and `css/**` are not Python modules, so declare them as package data (e.g. in `pyproject.toml` / `MANIFEST.in`) or they will be missing from the wheel.
2. **Be importable**: labb resolves your package by `import <name>`, so the name a consumer puts in `css.packages` must be the importable module name.

Then publish to PyPI (or a private index, or use a path/VCS dependency during development).

## Step 4: how a consumer uses it

The consumer installs your package, adds it to `INSTALLED_APPS` if it ships templates, and subscribes to your groups:

```yaml
# their labb.yaml
css:
  packages:
    labb:   [themes, components]
    my_pack: [theme, components]
```

On the next `labb build`, labb resolves `my_pack` by import, reads your `labb-provides.yaml`, and folds your groups into their generated `.labb/labb.css`. They never reference your internal paths. If you restructure your templates, bump the group globs in `labb-provides.yaml` and consumers are unaffected.

<c-lb.alert variant="warning" alertStyle="outline" class="my-4">
  <span>A package that ships no <code>labb-provides.yaml</code> can still be consumed with the raw form (<code>my_pack: { literals: [templates/**/*.html] }</code>), but then the consumer is coupled to your paths. Publishing groups is the better contract.</span>
</c-lb.alert>

## Testing your package locally

During development, add your package as a path dependency in a test project and iterate:

```bash
# in a consumer project
labb build            # resolves your package, regenerates .labb/labb.css
```

A bad package name or unknown group fails the build with a clear message, so typos surface immediately.

## Keep going

<c-lbdocs.doc_card.grid cols="2">
  <c-lbdocs.doc_card title="labb-provides.yaml" summary="Full schema for publishing CSS groups" href="{% doc_url '4_references/5_labb_provides.md' 'guide' %}" icon="rmx.file-list-3" />
  <c-lbdocs.doc_card title="Building CSS" summary="The scan and build pipeline your package plugs into" href="{% doc_url '2_concepts/2_building_css.md' 'guide' %}" icon="rmx.css3" />
</c-lbdocs.doc_card.grid>
