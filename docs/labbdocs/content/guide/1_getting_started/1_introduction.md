---
title: Introduction
description: Beautiful, accessible, and customizable UI components for your Django projects.
doc_show_toc: False
---
{% load static %}

**labb** is a Django component library that lets you build beautiful interfaces using simple, HTML-like syntax. Write `<c-lb.button>` instead of complex template tags. Build professional UIs in minutes, not hours.

<div class="not-prose flex justify-center my-8 mx-auto rounded-lg">
<c-lb.diff aspectRatio="16/9" class="w-full max-w-4xl">
  <c-lb.diff.item-1>
    <div class="flex flex-col items-center justify-center h-full bg-gradient-to-br from-purple-500 via-pink-500 to-orange-400">
        <c-lbdocs.codeblock.title title="labb.html" class="bg-black text-white rounded-lg">
        <c-lbdocs.codeblock language="html" class="w-full sm:w-100" :copyButton="False">&lt;c-lb.button
  variant=&quot;primary&quot;
  icon=&quot;rmx.terminal&quot;
  size=&quot;lg&quot;
  class=&quot;shadow-xl&quot;
&gt;
    pip install labbui
&lt;/c-lb.button&gt;</c-lbdocs.codeblock>
</c-lbdocs.codeblock.title>
    </div>
  </c-lb.diff.item-1>
  <c-lb.diff.item-2>
    <div class="flex flex-col items-center justify-center h-full bg-gradient-to-br from-purple-500 via-pink-500 to-orange-400">
        <c-lb.button variant="primary" icon="rmx.terminal" size="lg" class="shadow-xl">pip install labbui</c-lb.button>
    </div>
  </c-lb.diff.item-2>
  <c-lb.diff.resizer />
</c-lb.diff>
</div>

## Why labb?

**Simple Syntax** — Components look like HTML, not Django template tags. Clean, readable, and intuitive.

**Backend Rendered** — Server-side rendering means fast page loads, perfect SEO, and zero JavaScript overhead.

**Familiar Tooling** — Built on [Django Cotton](https://django-cotton.com/) with [daisyUI 5](https://daisyui.com/docs/intro/) styling. Accessible, customizable, and extensible.

**Developer Friendly** — Powerful CLI for setup, component inspection, and AI-assisted development. Works seamlessly with Cursor, VSCode Copilot, and other AI tools.

## What You Get

- **40+ Components** (in progress) — Buttons, cards, modals, drawers, forms, and more
- **Extensive examples** — Each component has multiple examples with different variations and use cases
- **Icon Libraries** — 2,800+ Remix icons and more via optional `labbicons` package
- **Theme Support** — Light, dark, and custom themes out of the box
- **Zero Config** — `labb init --defaults` and you're ready to go
- **No JavaScript Build Step** — Components work without JavaScript by default
- **CLI Tool** — `labb` command for project setup, component inspection, and AI-assisted development


## Coming Soon

- IDE extensions for autocomplete and documentation
- More icon packs
- Seamless integration with AlpineJS for interactive component properties
- Starter kits, blocks and templates.
