---
title: Migrating to 0.5
description: "Move a labb project from Alpine .x variants to Datastar signals, bindings, reactive props, and server actions."
keywords: "labb migration, alpine to datastar, labb 0.5 upgrade, c-lbr, reactive props django, labb x variants removed"
---

labb 0.5 replaces Alpine with [Datastar](https://data-star.dev/). The `.x` component variants, `x-model`, and `x-on` are gone. Use this guide to update an existing project.

If your project never used `.x` variants, you do not need to change its static pages.

<c-lb.alert variant="info" alertStyle="outline" class="my-4">
  <span>Reactivity is opt-in. Datastar loads only on pages that use a `c-lbr.` component or a reactive `$` prop.</span>
</c-lb.alert>

## Replace the Alpine API

- Replace `.x` components such as `<c-lb.button.x>` with their plain component.
- Replace `x-model`, `x-on`, `x-show`, and `x-text` with `bind`, `data-on:*`, `data-show`, and `data-text`.
- Declare client state with `<c-lbr.signals>`.
- Use `c-lbr.get`, `c-lbr.post`, and `c-lbr.delete` for server-driven updates.

## The mapping

| Alpine (0.4) | labb 0.5 |
|---|---|
| `<c-lb.button.x>` | `<c-lb.button>` (no variant) |
| `x-data="{ open: false }"` | `<c-lbr.signals $open="false" />` |
| `x-model="q"` | `bind="$q"` |
| `x-on:click="..."` | `data-on:click="..."` |
| `x-show="open"` | `data-show="$open"` |
| `x-text="label"` | `data-text="$label"` |
| Reactive prop via Alpine | `variant="$signal:fallback"` |
| Manual `fetch` or a JSON endpoint | `c-lbr.get` / `c-lbr.post` / `c-lbr.delete` |

Read and write signals with the `$` prefix. Split an Alpine `x-data` object into named signals.

## Convert a toggle

The 0.4 Alpine version:

```html
<c-lb.button.x x-data="{ open: false }" x-on:click="open = !open">
  Toggle
</c-lb.button.x>

<div x-show="open">Now you can see me.</div>
```

The 0.5 Datastar version:

```html
<c-lbr.signals $open="false" />

<c-lb.button data-on:click="$open = !$open">Toggle</c-lb.button>

<div data-show="$open">Now you can see me.</div>
```

## Reactive props

Drive a component prop from a signal with `$` and provide a fallback for the initial server response.

```html
<c-lbr.signals $status="success" />

<c-lb.badge variant="$status:success">Active</c-lb.badge>
```

When `$status` changes, the badge updates in the browser. Use `prop="$signal:fallback"`.

## Server actions and csrf

Use a server action for a change Django owns. It calls a normal view, which reads `request.signals` and returns the whole page. Datastar updates the changed regions in the current DOM.

<c-lb.alert variant="success" alertStyle="outline" class="my-4">
  <span>`c-lbr.post` handles CSRF. You do not need a manual `{% templatetag openblock %} csrf_token {% templatetag closeblock %}` inside the form.</span>
</c-lb.alert>

```html
<c-lbr.get to="todos:index" on="input__debounce.300ms">
  <c-lb.input type="search" bind="$filters.q" placeholder="Search todos" />
</c-lbr.get>
```

## Charts

Bind a chart’s `data` prop to a signal with `data="$signal"`. The chart updates when the signal changes.

## Update the CSS configuration

0.5 replaces `css.scan.apps` in `labb.yaml` with `css.packages`. Packages publish named CSS groups such as themes, components, and blocks. Subscribe to the groups instead of pointing Tailwind at package template paths.

The old schema works during the deprecation window and logs a warning. Run this command to update the project.

```bash
labb migrate
```

It rewrites `labb.yaml`, adds `@import "../.labb/labb.css";` to `input.css`, deletes `static_src/labb-classes.txt`, and adds `.labb/` to `.gitignore`. It also reports any remaining manual cleanup.

### By hand

To make the changes yourself, update the configuration and stylesheet, then remove the old safelist file.

#### Update `labb.yaml`

Replace `css.scan.apps` with `css.packages` and delete `css.scan.output`. Keep `css.scan.templates`.

```yaml
# before
css:
  scan:
    apps:
      labb: [templates/lb-examples/**/*.html]
    output: static_src/labb-classes.txt

# after
css:
  packages:
    labb: '*'          # or a list of groups, e.g. [themes, components]
```

#### Update `input.css`

Remove hardcoded `@source "...labb/templates"` lines and inline `@plugin "daisyui/theme"` blocks. Add this import.

```css
@plugin "daisyui" { themes: light, dark; }

/* labb css - don't remove this line */
@import "../.labb/labb.css";
```
```

Delete `static_src/labb-classes.txt` and add `.labb/` to `.gitignore`.

<c-lb.alert variant="warning" alertStyle="outline" class="my-4">
  <span>`labb migrate` adds `components` only. If a package template uses raw utilities, add a `literals` list or subscribe to a group that includes it. labb’s `'*'` subscribes to the full library.</span>
</c-lb.alert>

See the [config reference]({% doc_url '5_references/1_config_yaml.md' 'guide' %}) and [building CSS]({% doc_url '4_going_further/1_building_css.md' 'guide' %}) for the full schema.

## Related

Read the reactivity guide for the full API.

<c-lbdocs.doc_card.grid cols="2">
  <c-lbdocs.doc_card title="Reactivity overview" summary="Signals, reactive props, and server actions, start to finish" href="{% doc_url '3_reactivity/1_overview.md' 'guide' %}" icon="rmx.flashlight" />
  <c-lbdocs.doc_card title="Signals" summary="Declare and read client state with c-lbr.signals" href="{% doc_url '3_reactivity/2_signals.md' 'guide' %}" icon="rmx.pulse" />
</c-lbdocs.doc_card.grid>
