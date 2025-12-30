---
title: Introducing labb, and the roadmap
description: Meet labb - a modern UI component library for Django, and discover our roadmap for future development.
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

Name is [Zadiq](https://github.com/zadiq), and I have been developing with Django for over 7 years now, both professionally and on the side. I have never felt the need to switch to another framework because I believe Django strikes the right balance between flexibility, extendability, and speed of development.

However, as we all know, building highly interactive web interfaces with Django requires us to dip our feet into the world we djangonauts are not always fond of: the world of JavaScript. This often means setting up full SPA applications and relegating Django to a simple API backend. While this approach works in some cases, it comes at the cost of the simplicity and speed of development that Django provides, and most importantly, server-side rendering.

I've experimented with various Django packages that aim to solve these problems, but I was never truly satisfied until I stumbled upon [Django Cotton](https://django-cotton.com/). This package allows us to write Django templates as if we were writing HTML, but with the full power of Django's templating system. It brings some of the benefits we enjoy from the JavaScript world, such as component-based design. As I was integrating Django Cotton into an existing project, I realized that by blending Cotton with other tools, a solid solution could be developed to build highly interactive web apps that are server-side rendered. Hence the birth of labb.

By coupling my favorite CSS UI framework, [daisyUI](https://daisyui.com/), with Django Cotton, I've been able to establish a foundation that I can build upon to address these challenges and create modern, dynamic user experiences with Django.

### A Measured Start

The initial release of labb intentionally comes with a limited set of components and features. This is by design; to gather feedback from the community and understand the real needs of Django developers. The current feature set won't immediately solve all the aforementioned problems, but it lays the groundwork for what's to come.

### The Roadmap

I'm excited to share what's on the horizon:

**Alpine.js Integration**
I've been experimenting with various ways of integrating Alpine.js, including:

- **Reactive component props**: The ability to dynamically change component props from the client side
- **labbwire**: HTML over the wire, the Django (cotton) way. This will enable us to build highly interactive components that are fully server-side rendered, not the Livewire way, but more aligned with the HTMX philosophy. However, my experiments have shown that Alpine.js is often sufficient for this purpose without requiring additional dependencies. More on this later.

**Complete DaisyUI Component Library**
A comprehensive set of DaisyUI components ready to use in your Django projects.

**Expanded Icon Collections**
Support for additional icon packs including Hero Icons, Tabler Icons, and more.

**IDE Extensions**
Component names and props autocomplete and documentation support directly in your favorite code editor.

**Advanced Components**
Rich, interactive components including date pickers, calendars, rich text editors, file upload widgets, charts, data visualization tools, and more.

**Starter Kits, Blocks, and Templates**
Pre-built templates and components to kickstart your Django projects even faster. Also, ready to copy and build upon blocks to build components and pages faster.

### Get Involved

labb is just getting started, and your feedback is invaluable. Try it out in your projects, share your thoughts, share with other developers, and let me know what features and components you need most. Together, we can make building modern Django applications faster and more enjoyable.

Get involved by joining our [GitHub Discussions](https://github.com/labbhq/labb/discussions) or [join our Discord server](https://discord.gg/34eBUJMQv2).

Happy labbing! 🚀
