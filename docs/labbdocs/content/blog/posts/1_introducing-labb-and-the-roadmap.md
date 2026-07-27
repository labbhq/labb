---
title: Introducing labb, and the roadmap
description: "Why I built labb, a Django UI component library on django-cotton and daisyUI, and what comes next: Alpine.js integration, the full daisyUI component set, more icon packs, and starter blocks."
keywords: "labb django, django component library, django-cotton, daisyui django, labb roadmap, django ui components"
published_time: 2025-12-29
modified_time: 2025-12-29
author: zadiq
doc_layout: blog
doc_show_toc: false
tags:
  - announcement
  - introduction
  - roadmap
  - django
  - ui-components
---

Hi djangonauts,

I have been developing with Django for over 7 years now, both professionally and on the side. I have never wanted to switch to another framework. Django gets the balance right between flexibility and speed of development.

Building a highly interactive web interface with Django, though, drags you into the part of the stack most of us would rather avoid: JavaScript. That usually means standing up a full SPA and demoting Django to an API backend. It works in some cases, but you pay for it with the simplicity and speed Django gives you, and you lose server-side rendering.

I tried several Django packages aimed at this problem and none of them stuck, until I found [Django Cotton](https://django-cotton.com/). Cotton lets you write templates that read like HTML while Django's template system keeps working underneath. It carries over the piece I missed most from the JavaScript world: component-based design. Halfway through adding Cotton to an existing project, I realized that Cotton plus a couple of other tools would let me build interactive web apps that stay server-side rendered. Hence the birth of labb.

Pairing Cotton with my favorite CSS UI framework, [daisyUI](https://daisyui.com/), gave me a foundation I can keep building on.

### A Measured Start

The first release of labb ships a small set of components and features. That is deliberate: I want feedback from the community, and a clearer read on what Django developers need day to day. It won't solve the problems I described above, but it is the groundwork for the releases that will.

### The Roadmap

What I'm working on next:

**Alpine.js Integration**
I've been experimenting with several ways of integrating Alpine.js:

- **Reactive component props**: change a component's props from the client side
- **labbwire**: HTML over the wire, the Django (cotton) way. It should let you build interactive components that stay server-side rendered, closer to the HTMX philosophy than to Livewire. So far my experiments suggest Alpine.js on its own covers most of this, with no extra dependencies. More on that later.

**Complete DaisyUI Component Library**
The rest of the DaisyUI components, ready to use in your Django projects.

**Expanded Icon Collections**
Support for more icon packs, including Hero Icons and Tabler Icons.

**IDE Extensions**
Autocomplete and documentation for component names and props, in your favorite editor.

**Advanced Components**
Date pickers, calendars, rich text editors, file upload widgets, charts, and data visualization tools.

**Starter Kits, Blocks, and Templates**
Pre-built templates to start a project from, plus blocks you can copy into a page and build on.

### Get Involved

labb is early, and your feedback shapes where it goes. Try it in a project, pass it on to other developers, and tell me which components you need most.

Come say hello in [GitHub Discussions](https://github.com/labbhq/labb/discussions).

Happy labbing! 🚀
