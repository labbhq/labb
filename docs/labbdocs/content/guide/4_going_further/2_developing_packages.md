---
title: Developing packages
description: "Publish a labb package with Cotton components, templates, styles, and a labb-provides.yaml manifest."
keywords: "labb third party package, develop labb package, labb-provides.yaml, django cotton component library, labb css packages, publish labb components"
---

{% load docs_tags %}

Package components, themes, or icon sets for other labb projects. A consumer reads templates and styles from installed Python packages, including `labb` itself.

<c-lb.alert variant="info" alertStyle="outline" class="my-4">
  <span>Package support arrived in 0.5.0 and will gain features. The next planned addition is package-provided component schemas, allowing <code>labb scan</code> to resolve variant classes for <code>&lt;c-mypack.*&gt;</code> tags. See the <a href="{% doc_url '6_about/2_roadmap.md' 'guide' %}">roadmap</a>.</span>
</c-lb.alert>

Read [Building CSS]({% doc_url '4_going_further/1_building_css.md' 'guide' %}) first if the scan and build pipeline is new to you.

## What a package ships

A labb package is an installable Python package containing some of the following files.

- **Templates** under `templates/cotton/<ns>/` and optional page or example templates
- **CSS** such as themes under a directory like `css/`
- **`labb-provides.yaml`**, which publishes named CSS groups

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
  <span>Use your own Cotton namespace, such as <code>cotton/mypack/</code> for <code>&lt;c-mypack.card&gt;</code>. The <code>cotton/lb/</code> namespace belongs to labb.</span>
</c-lb.alert>

## Step 1: build your components

Write components with [django-cotton]({% doc_url '1_getting_started/1_introduction.md' 'guide' %}) as you would in an app. A package component can compose labb components. The consumer’s build finds those classes through your `components` group.

labb resolves component variant classes from usage. Tailwind compiles raw utility classes that it can scan literally. CSS groups cover both kinds of template output.

## Step 2: publish CSS groups

Add `labb-provides.yaml` at the package root. Each group can list `components` for usage scanning, `literals` for Tailwind `@source` files, and `imports` for CSS included in the build.

```yaml
provides:
  components:
    components: [templates/cotton/mypack/**/*.html]
    literals:   [templates/cotton/mypack/**/*.html]
  theme:
    imports: [css/theme.css]
```

- Put templates that use `<c-lb.*>` components under `components`. The scanner reads labb’s schemas and resolves component props such as `variant="primary"`.
- Put templates containing raw utility classes under `literals`. You can list the same glob in both groups because labb de-duplicates it.

`labb scan` currently understands labb’s schemas only. It cannot infer that `<c-mypack.card variant="fancy">` needs `mypack-card-fancy`. Until package schemas arrive, list your own component templates under `literals` and include dynamic classes in a plain text file.

```yaml
provides:
  components:
    literals: [templates/cotton/mypack/**/*.html, mypack-classes.txt]
```

`@source` reads plain text, one class per line. Put shippable CSS such as themes and keyframes under `imports`. A daisyUI `@plugin "daisyui/theme"` block must be imported so it resolves in the consumer’s project.

See the [`labb-provides.yaml` reference]({% doc_url '5_references/5_labb_provides.md' 'guide' %}) for the full schema.

## Step 3: package and distribute

Distribute the package as you would any Python package. Make sure these two requirements are met.

1. Include `labb-provides.yaml`, `templates/**`, and `css/**` as package data. They are not Python modules and will otherwise be missing from the wheel.
2. Use an importable module name in `css.packages` because labb resolves it with `import <name>`.

Then publish to PyPI (or a private index, or use a path/VCS dependency during development).

## Step 4: how a consumer uses it

The consumer installs the package, adds it to `INSTALLED_APPS` when it ships templates, and subscribes to its groups.

```yaml
# their labb.yaml
css:
  packages:
    labb:   [themes, components]
    my_pack: [theme, components]
```

On the next `labb build`, labb imports `my_pack`, reads `labb-provides.yaml`, and adds the groups to `.labb/labb.css`. Consumers do not need to know your internal paths.

<c-lb.alert variant="warning" alertStyle="outline" class="my-4">
  <span>A package without <code>labb-provides.yaml</code> can use the raw form <code>my_pack: { literals: [templates/**/*.html] }</code>. Named groups keep consumers independent of your paths.</span>
</c-lb.alert>

## Testing your package locally

During development, add the package as a path dependency in a test project.

```bash
# in a consumer project
labb build            # resolves your package, regenerates .labb/labb.css
```

A bad package name or group causes the build to fail with an error.

## Related

<c-lbdocs.doc_card.grid cols="2">
  <c-lbdocs.doc_card title="labb-provides.yaml" summary="Full schema for publishing CSS groups" href="{% doc_url '5_references/5_labb_provides.md' 'guide' %}" icon="rmx.file-list-3" />
  <c-lbdocs.doc_card title="Building CSS" summary="The scan and build pipeline your package plugs into" href="{% doc_url '4_going_further/1_building_css.md' 'guide' %}" icon="rmx.css3" />
</c-lbdocs.doc_card.grid>
