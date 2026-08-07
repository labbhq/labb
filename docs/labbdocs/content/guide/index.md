---
title: Guide
description: "labb guides for Django: installation, building UIs, reactivity, CSS, and reference. Learn django-cotton components, Tailwind CSS, daisyUI 5, and theming on labb.io."
keywords: "labb guide django, django-cotton guide, labb documentation, django ui tutorial, tailwind django guide, daisyui django"
doc_show_toc: false
---

{% load docs_tags %}

Read it in order and you go from installing labb to shipping a reactive page. Dip in anywhere if you already know what you are looking for.

<c-lbdocs.doc_card.grid cols="2">
  <c-lbdocs.doc_card
    title="Getting started"
    summary="Install labb and build one real page from components"
    href="{% doc_url '1_getting_started/1_introduction.md' 'guide' %}"
    icon="rmx.play-circle"
  />

  <c-lbdocs.doc_card
    title="Building UIs"
    summary="Compose components, write your own, add icons, blocks, and themes"
    href="{% doc_url '2_building_uis/1_composition.md' 'guide' %}"
    icon="rmx.layout-grid"
  />

  <c-lbdocs.doc_card
    title="Reactivity"
    summary="Signals, bindings, reactive props, and server actions over plain Django views"
    href="{% doc_url '3_reactivity/1_overview.md' 'guide' %}"
    icon="rmx.flashlight"
  />

  <c-lbdocs.doc_card
    title="Going further"
    summary="How the CSS build works, and how to ship your own labb packages"
    href="{% doc_url '4_going_further/1_building_css.md' 'guide' %}"
    icon="rmx.css3"
  />

  <c-lbdocs.doc_card
    title="References"
    summary="The CLI, labb.yaml, settings, template tags, and the reactivity API"
    href="{% doc_url '5_references/0_labb_cli.md' 'guide' %}"
    icon="rmx.terminal"
  />

  <c-lbdocs.doc_card
    title="About"
    summary="Changelog, roadmap, and migrating to 0.5"
    href="{% doc_url '6_about/1_changelog.md' 'guide' %}"
    icon="rmx.information"
  />
</c-lbdocs.doc_card.grid>

## New to labb

Three pages and you have something running:

1. [Introduction]({% doc_url '1_getting_started/1_introduction.md' 'guide' %}) covers what labb is and what you write.
2. [Installation]({% doc_url '1_getting_started/2_installation.md' 'guide' %}) gets it into a project.
3. [Your first page]({% doc_url '1_getting_started/3_first_page.md' 'guide' %}) builds a real page from a Django view.

After that, [Building UIs]({% doc_url '2_building_uis/1_composition.md' 'guide' %}) is where most of the day-to-day lives, and [Reactivity]({% doc_url '3_reactivity/1_overview.md' 'guide' %}) is what you reach for when a page needs to do something.
