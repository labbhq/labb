---
title: labb-provides.yaml
description: "labb-provides.yaml reference: publish named CSS groups (components, literals, imports) from a Python package so labb projects can subscribe by name."
keywords: "labb-provides.yaml, labb css packages, labb third party package, css provides groups, labb package authoring"
---

{% load docs_tags %}

`labb-provides.yaml` is how a **package** publishes CSS to labb projects. A package ships this file at its root; consumers then subscribe to its named **groups** from their own [`css.packages`]({% doc_url '5_references/1_config_yaml.md' 'guide' %}), instead of hardcoding the package's template paths.

This is the reference for the file. For a walkthrough of building a package, see [Developing packages]({% doc_url '4_going_further/2_developing_packages.md' 'guide' %}).

## Location

The file lives at the **package root**, the directory that contains the package's `__init__.py`:

```
my_package/
  __init__.py
  labb-provides.yaml     ← here
  templates/
  css/
```

labb finds it by importing the package (`import my_package`) and reading `labb-provides.yaml` next to its `__file__`. This works whether the package is a path dependency or installed from PyPI. The consumer never needs to know where it lives on disk.

## Schema

```yaml
provides:
  <group-name>:
    components: [<glob>, ...]   # optional
    literals:   [<glob>, ...]   # optional
    imports:    [<path>, ...]   # optional
```

- **`provides`**: a mapping of group name to its contributions. A consumer selects groups by name (`my_package: [group-a, group-b]`), `'*'` (or the `all` alias, or blank) for every group.
- Every path is **relative to the package root** and resolved at build time.

### The three contribution kinds

| Key | What it does | Use for |
|---|---|---|
| `components` | Template globs scanned for `<c-lb.*>` usage; their variant classes are added to the safelist. | Templates that *use* labb components, so the dynamic classes (`btn-primary`, `badge-lg`) compile. |
| `literals` | Template globs handed to Tailwind as `@source`. | Templates with **raw utility classes** written literally in the markup (e.g. `min-h-screen`, `-translate-x-1/2`) that Tailwind must scan directly. |
| `imports` | CSS files shipped in the package, **inlined** into the build. | Themes and other package CSS. Inlined (not `@import`ed) so any `@plugin` inside resolves against the consumer's `node_modules`. |

A group may set any combination of the three. See [Building CSS]({% doc_url '4_going_further/1_building_css.md' 'guide' %}) for why `components` and `literals` are separate.

## Example: labb's own file

The `labb` package publishes these groups:

```yaml
provides:
  themes:
    imports: [css/themes.css]
  components:
    components: [templates/cotton/lb/**/*.html]
    literals:   [templates/cotton/lb/**/*.html]
  reactivity:
    components: [templates/cotton/lbr/**/*.html]
    literals:   [templates/cotton/lbr/**/*.html]
  blocks:
    components: [templates/cotton/lbb/**/*.html]
    literals:   [templates/cotton/lbb/**/*.html]
  examples:
    components: [templates/lb-examples/**/*.html]
    literals:   [templates/lb-examples/**/*.html]
```

A consumer picks what it needs:

```yaml
# labb.yaml
css:
  packages:
    labb: [themes, components]   # a normal app
    # labb: '*'                  # everything (the docs site does this)
```

## Resolution and merging

- Selected groups are **merged**. `components`, `literals`, and `imports` lists are concatenated with **order-preserving de-duplication**, so two groups that share an import (e.g. both pull `themes`) inline it only once.
- If a consumer names a group the package does not publish, the build fails with a clear error listing the available groups.
- If a consumer subscribes by group to a package that ships **no** `labb-provides.yaml`, the build fails and points you at the raw-mapping form instead.

<c-lb.alert variant="info" alertStyle="outline" class="my-4">
  <span>A package does not have to publish groups. If it ships none, a consumer can still pull CSS from it with the raw form: <code>my_package: { literals: [templates/**/*.html] }</code>. Groups are the ergonomic layer on top.</span>
</c-lb.alert>

## Related

<c-lbdocs.doc_card.grid cols="2">
  <c-lbdocs.doc_card title="Developing packages" summary="Build and publish a package that ships components and CSS" href="{% doc_url '4_going_further/2_developing_packages.md' 'guide' %}" icon="rmx.box-3" />
  <c-lbdocs.doc_card title="labb.yaml" summary="The css.packages consumer schema" href="{% doc_url '5_references/1_config_yaml.md' 'guide' %}" icon="rmx.settings-3" />
</c-lbdocs.doc_card.grid>
