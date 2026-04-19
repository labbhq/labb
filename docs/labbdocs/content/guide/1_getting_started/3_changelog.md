---
title: Changelog
description: "Release history and version notes for labb: django component library, labbui, and labbdocs."
keywords: "labb changelog, labbui release notes, django labb versions"
---

{% load docs_tags %}


## 0.4.0 <c-lb.badge size="sm">latest</c-lb.badge>

**Apr 19, 2026**

### Features
- **AlpineJS integration** — opt-in client-side reactivity via `.x` component variants (e.g. `<c-lb.button.x>`). Alpine is only injected when a reactive variant is used; static pages stay zero-JS. New `window.lb` helpers (`extendComponent`, `lbProps`) for extending reactive components. ([#31](https://github.com/labbhq/labb/issues/31))
- **Charts** — new Chart.js-backed components (`chart.bar`, `chart.line`, `chart.pie`, `chart.doughnut`, `chart.radar`, `chart.polar-area`, `chart.scatter`, `chart.bubble`) with live DaisyUI theming, auto-palette colouring, `-light` translucent variants, and `x-model` reactivity. `<c-lb.chart />` page-level provider for global Chart.js config.
- **Icons** — added ~85 new Remix icons (AI/ML, signal, chat, painting, network, chart, misc).

### Fixes
- **Alert** — renamed the `style` prop to `alertStyle` to avoid clashing with the HTML `style` attribute on cotton passthrough.

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
- **labbstart** — Starter kit scaffolding tool ([#20](https://github.com/labbhq/labb/issues/20))
- **Breadcrumbs** — New breadcrumbs component ([#25](https://github.com/labbhq/labb/issues/25))
- **Carousel** — New carousel component ([#27](https://github.com/labbhq/labb/issues/27))

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
