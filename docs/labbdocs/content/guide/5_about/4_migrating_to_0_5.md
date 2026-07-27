---
title: Migrating to 0.5
description: "Move a labb project from Alpine .x variants to Datastar reactivity: map x-model and x-on to c-lbr.* components, $-reactive props, and signals."
keywords: "labb migration, alpine to datastar, labb 0.5 upgrade, c-lbr, reactive props django, labb x variants removed"
---

labb 0.5 replaces Alpine with [Datastar](https://data-star.dev/). The `.x` component variants are gone, along with `x-model` and `x-on`. This page maps the old patterns to the new ones so you can move an existing project over.

If you never used the `.x` variants, there is nothing to change. Your static pages already ship zero JavaScript, and they still do.

<c-lb.alert variant="info" alertStyle="outline" class="my-4">
  <span>Reactivity is opt-in now. Datastar loads only on pages that use a `c-lbr.` component or a `$`-reactive prop. A page with no reactivity ships no JavaScript.</span>
</c-lb.alert>

## What changed

- The `.x` component variants (`<c-lb.button.x>` and friends) no longer exist. Use the plain component.
- `x-model`, `x-on`, `x-show`, and `x-text` are gone. Use `bind`, `data-on:*`, `data-show`, and `data-text`.
- Client state now lives in signals, declared with `<c-lbr.signals>`.
- Server-driven updates use `c-lbr.get` / `c-lbr.post` / `c-lbr.delete` against ordinary Django views.

## The mapping

| Alpine (0.4) | labb 0.5 |
|---|---|
| `<c-lb.button.x>` | `<c-lb.button>` (no variant) |
| `x-data="{ open: false }"` | `<c-lbr.signals $open="false" />` |
| `x-model="q"` | `bind="q"` |
| `x-on:click="..."` | `data-on:click="..."` |
| `x-show="open"` | `data-show="$open"` |
| `x-text="label"` | `data-text="$label"` |
| Reactive prop via Alpine | `variant="$signal:fallback"` |
| Manual `fetch` or a JSON endpoint | `c-lbr.get` / `c-lbr.post` / `c-lbr.delete` |

Signals are read and written with the `$` prefix. The old `x-` state object becomes one or more named signals.

## Before and after

A toggle in 0.4 with Alpine:

```html
<c-lb.button.x x-data="{ open: false }" x-on:click="open = !open">
  Toggle
</c-lb.button.x>

<div x-show="open">Now you can see me.</div>
```

The same toggle in 0.5 with Datastar:

```html
<c-lbr.signals $open="false" />

<c-lb.button data-on:click="$open = !$open">Toggle</c-lb.button>

<div data-show="$open">Now you can see me.</div>
```

## Reactive props

Changing a prop from the client used to mean an Alpine binding. Now you prefix the prop with `$` and give it a fallback for the first paint:

```html
<c-lbr.signals $status="success" />

<c-lb.badge variant="$status:success">Active</c-lb.badge>
```

When `$status` changes, the badge re-colours on its own. The pattern is always `prop="$signal:fallback"`.

## Server actions and csrf

Anything that touched the server used to need your own request code and a manual csrf token. A server action replaces both. It calls a normal Django view, which reads `request.signals`, does its work, and returns the whole page. Datastar morphs the difference into place. There is no partial template and no JSON endpoint.

<c-lb.alert variant="success" alertStyle="outline" class="my-4">
  <span>csrf is handled for you. A `c-lbr.post` no longer needs a manual `{% templatetag openblock %} csrf_token {% templatetag closeblock %}`.</span>
</c-lb.alert>

```html
<c-lbr.get to="todos:index" on="input__debounce.300ms">
  <c-lb.input type="search" bind="filters.q" placeholder="Search todos" />
</c-lbr.get>
```

## Charts

Charts are reactive the same way as everything else. Bind the chart to a signal with `data="$signal"` and it redraws when the signal changes. The old `x-model` chart wiring is no longer needed.

## CSS build: css.scan.apps becomes css.packages

0.5 replaces `css.scan.apps` in `labb.yaml` with `css.packages`. A package now publishes named CSS groups (themes, components, blocks, ...) and you subscribe to the ones you want, instead of pointing Tailwind at another package's template paths by hand.

The old schema still works during the deprecation window and logs a warning. To move over, run:

```bash
labb migrate
```

This rewrites `labb.yaml`, adds the single `@import "../.labb/labb.css";` to your `input.css`, deletes the stale `static_src/labb-classes.txt`, and gitignores `.labb/`. It prints any manual cleanup left (removing old `@source` lines or inline theme blocks).

### By hand

If you would rather do it yourself:

1. **labb.yaml**: replace `css.scan.apps` with `css.packages`, and delete `css.scan.output` (the safelist now lives in `.labb/`). Keep `css.scan.templates`.

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

2. **input.css**: remove any hardcoded `@source "...labb/templates"` lines and inline `@plugin "daisyui/theme"` blocks, and add one line:

   ```css
   @plugin "daisyui" { themes: light, dark; }

   /* labb css - don't remove this line */
   @import "../.labb/labb.css";
   ```

3. Delete `static_src/labb-classes.txt`; add `.labb/` to `.gitignore`.

<c-lb.alert variant="warning" alertStyle="outline" class="my-4">
  <span>`labb migrate` fills in `components` only. If a package's templates use raw utilities you rely on, add a `literals` list or subscribe to a group that includes them (labb's `'*'` covers the whole library).</span>
</c-lb.alert>

See the [config reference]({% doc_url '4_references/1_config_yaml.md' 'guide' %}) and [building CSS]({% doc_url '2_concepts/2_building_css.md' 'guide' %}) for the full schema.

## Next steps

The reactivity guide covers all of this in depth.

<c-lbdocs.doc_card.grid cols="2">
  <c-lbdocs.doc_card title="Reactivity overview" summary="Signals, reactive props, and server actions, start to finish" href="{% doc_url '3_reactivity/1_overview.md' 'guide' %}" icon="rmx.flashlight" />
  <c-lbdocs.doc_card title="Signals" summary="Declare and read client state with c-lbr.signals" href="{% doc_url '3_reactivity/2_signals.md' 'guide' %}" icon="rmx.pulse" />
</c-lbdocs.doc_card.grid>
