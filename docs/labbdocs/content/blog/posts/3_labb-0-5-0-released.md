---
title: labb 0.5.0 and the move to Datastar
description: "labb 0.5.0 drops Alpine and rebuilds reactivity on Datastar. Why I switched, what signals and server actions look like now, and the 35 blocks shipping with the release."
keywords: "labb 0.5.0, labb datastar, alpine to datastar, django reactivity, django component library, django-cotton, daisyui django"
published_time: 2026-07-14
modified_time: 2026-07-14
author: zadiq
doc_layout: blog
doc_show_toc: false
tags:
  - announcement
  - release
  - reactivity
  - datastar
  - django
---

Hi djangonauts,

labb 0.5.0 is out, and it comes with a change I want to be upfront about.

> [IMAGE PLACEHOLDER: hero]

### I said Alpine. I changed my mind.

In 0.4.0 I shipped reactivity built on Alpine. You got `.x` component variants like `<c-lb.button.x>`, and they worked. I stood behind that choice at the time.

0.5.0 pulls Alpine out and replaces it with [Datastar](https://data-star.dev/).

That is a reversal, so I would rather own it than swap the engine and hope nobody notices. If you built on the `.x` variants, this affects you, and there is a migration guide at the end of this post to keep the move short.

### Why the change

The goal for labb has not moved. I want full-stack reactivity for Django with as little JavaScript as possible. You write Django and components, the server renders, and interactivity happens without you dropping into a JavaScript app.

Alpine got me part of the way. But the more I pushed on the full-stack side, the more the model fought me. State lived in the browser, the server rendered once, and keeping the two in sync meant writing more and more client code. It was the opposite of how I wanted labb to feel.

Datastar fits the goal better. It is built around signals and hypermedia: you send updates over the wire, the server stays in charge, and the client stays thin. That is the model I kept reaching for, so I moved labb onto a tool that already works that way.

The trade-off is community size. Alpine has a much bigger one than Datastar, which means a smaller ecosystem and fewer people who already know the syntax. I decided the fit with labb's goal was worth more than the size of the crowd. labb also abstracts Datastar, so you write labb components and props rather than Datastar syntax. And if a feature labb needs ever ends up behind a paywall, I can reproduce it, because the surface I depend on is small.

I wrote more about the reasoning in [this discussion](https://github.com/labbhq/labb/discussions/104#discussioncomment-17478897) if you want the longer version.

### What reactivity looks like now

Three pieces: signals, reactive props, and server actions. All of it renders on the server first.

Signals hold client state. You declare them once, then read and write them with the `$` prefix. Here is a toggle in 0.4.0 with Alpine:

```html
<c-lb.button.x x-data="{ open: false }" x-on:click="open = !open">
  Toggle
</c-lb.button.x>

<div x-show="open">Now you can see me.</div>
```

And the same toggle in 0.5.0 with Datastar:

```html
<c-lbr.signals $open="false" />

<c-lb.button data-on:click="$open = !$open">Toggle</c-lb.button>

<div data-show="$open">Now you can see me.</div>
```

Reactive props let a signal drive a component. Prefix the prop with `$`, give it a fallback for the first paint, and the component re-renders itself when the signal changes:

```html
<c-lbr.signals $status="success" />

<c-lb.badge variant="$status:success">Active</c-lb.badge>
```

Server actions handle anything the server owns. `c-lbr.get`, `c-lbr.post`, and `c-lbr.delete` fire a request on a DOM event, hit an ordinary Django view, and morph the response into the page. No JSON endpoint, no partial template, and csrf is handled for you:

```html
<c-lbr.get to="todos:index" on="input__debounce.300ms">
  <c-lb.input type="search" bind="$filters.q" placeholder="Search todos" />
</c-lbr.get>
```

Pages that use none of this are unchanged. Datastar loads only where you use it, so a static page still ships zero JavaScript.

### Blocks, to prove it

Talk is cheap, so 0.5.0 ships 35 blocks across 7 surfaces: auth, dashboard, data-table, hero, pricing, settings, and wizard. Five blocks each.

> [IMAGE PLACEHOLDER: blocks showcase]

Every block is server-rendered and reactive. You copy one into your project and it works, no wiring step. They were also the test I trusted most. Awkwardness in the new model would have shown up first in real blocks, and building these is what convinced me the move was right.

### If you are on the `.x` variants

The `.x` variants are gone in 0.5.0. Moving off them is mostly mechanical: `x-model` becomes `bind`, `x-on` becomes `data-on`, and client state moves into signals.

I wrote a short guide that maps the old patterns to their replacements, with before and after code.

Read [Migrating to 0.5](/docs/guide/about/migrating-to-0-5), then upgrade:

```bash
pip install --upgrade labbui
```

If you have questions or the move trips you up somewhere, come tell me in [GitHub Discussions](https://github.com/labbhq/labb/discussions).

Happy labbing. 🚀
