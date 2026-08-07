---
title: Changelog
description: "Release history and version notes for labb: django component library, labbui, and labbdocs."
keywords: "labb changelog, labbui release notes, django labb versions"
---

{% load docs_tags %}


## 0.5.0a1 <c-lb.badge size="sm">latest</c-lb.badge>

**Jul 14, 2026**

0.5.0 introduces Datastar-based reactivity and removes the Alpine `.x` variants. See [Migrating to 0.5](/docs/guide/about/migrating-to-0-5) if your project uses the old API.

### Reactivity
- **Datastar reactivity.** Signals, reactive props, and server actions work with server-rendered Django templates.
- **Signals and reactive props.** Declare browser state with `<c-lbr.signals>`, bind inputs to it, and drive compatible props with values such as `variant="$status:primary"`.
- **Server actions.** `c-lbr.get`, `c-lbr.post`, and `c-lbr.delete` call ordinary Django views and morph their responses into the page. `post` handles CSRF.
- **Reactive charts.** Pass `data="$signal"` to update a chart when the signal changes.
- **Opt-in runtime.** Datastar loads only on pages that use reactive features.

### Blocks
- **35 blocks across seven categories.** Auth, dashboard, data tables, hero, pricing, settings, and wizard blocks are ready to copy into a project.
- **`labb block` CLI.** Create collections, preview blocks, validate them, and install them from the command line.

### Components
- **Reactive-capable inputs and charts.** Schema updates across charts, data display, and data input so components accept reactive props.
- Component API tables now mark which props are reactive.

### Docs
- **Reactivity guide.** New guides cover signals, reactive props, bindings, server actions, and patterns.
- **Restructured guide.** Installation, introduction, and the first-page tutorial have been reorganised.

### Removed / breaking
- **Alpine `.x` variants are gone.** The whole Alpine layer has been removed: the `.x` component variants, the bundled Alpine runtime, and `x-model` / `x-on` bindings. Move to Datastar with the [Migrating to 0.5](/docs/guide/about/migrating-to-0-5) guide.

### Tooling
- **CLI.** Reworked internals behind the new reactivity and blocks commands.
- **Versioning and pre-commit.** Updated release tooling and pre-commit hooks.

---

## 0.4.0

**Apr 19, 2026**

### Features
- **Alpine.js integration.** Opt-in client-side reactivity through `.x` component variants like `<c-lb.button.x>`. Alpine loads only when a reactive variant is used, so static pages stay zero-JS. Adds `window.lb` helpers (`extendComponent`, `lbProps`) for extending reactive components. ([#31](https://github.com/labbhq/labb/issues/31))
- **Charts.** New Chart.js-backed components (`chart.bar`, `chart.line`, `chart.pie`, `chart.doughnut`, `chart.radar`, `chart.polar-area`, `chart.scatter`, `chart.bubble`) with live daisyUI theming, auto-palette colouring, `-light` translucent variants, and reactive data. A `<c-lb.chart />` page-level provider sets global Chart.js config.
- **Icons.** Added around 85 new Remix icons (AI/ML, signal, chat, painting, network, chart, and misc).

### Fixes
- **Alert.** Renamed the `style` prop to `alertStyle` so it no longer clashes with the HTML `style` attribute on cotton passthrough.

---

## 0.3.0

**Mar 08, 2026**

### Features

- Full daisyUI components support 🎉
- Restructure of docs for better readability
- Introduction of props modifiers for icon props in supported components. See components like button, badge, etc.

---

## 0.2.0

**Feb 09, 2026**

### Features
- **labbstart**. Starter kit scaffolding tool ([#20](https://github.com/labbhq/labb/issues/20))
- **Breadcrumbs**. New breadcrumbs component ([#25](https://github.com/labbhq/labb/issues/25))
- **Carousel**. New carousel component ([#27](https://github.com/labbhq/labb/issues/27))

### Maintenance
- Enhanced README ([#22](https://github.com/labbhq/labb/issues/22))

---

## 0.1.1

**Jan 03, 2026**

### Maintenance
- Documentation site cleanup ([#14](https://github.com/labbhq/labb/issues/14))

---

## 0.1.0

**Dec 30, 2025**

Initial stable release.

---

## 0.0.2

**Dec 30, 2025**

### Maintenance
- Blog post support for docs ([#2](https://github.com/labbhq/labb/issues/2))
- Community menu ([#4](https://github.com/labbhq/labb/issues/4))

---

## 0.0.1a2

**Oct 29, 2025**

Alpha pre-release with early feature and bug fix work.

---

## 0.0.1a

**Oct 26, 2025**

First alpha pre-release.
