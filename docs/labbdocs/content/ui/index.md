---
title: UI Components
description: labb UI component library documentation
doc_show_toc: false
---

{% load docs_tags %}

## Getting Started

<c-lbdocs.doc_card.grid cols="3">
  <c-lbdocs.doc_card
    title="Introduction"
    summary="Learn about labb and how it simplifies Django UI development"
    href="{% doc_url '1_getting_started/1_introduction.md' 'ui' %}"
    icon="rmx.file-text"
  />

  <c-lbdocs.doc_card
    title="Installation"
    summary="Add labb to your existing and new Django projects"
    href="{% doc_url '1_getting_started/2_installation.md' 'ui' %}"
    icon="rmx.download"
  />

  <c-lbdocs.doc_card
    title="Quick Start"
    summary="A quick start guide to get you up and running with labb features"
    href="{% doc_url '1_getting_started/3_quick_start.md' 'ui' %}"
    icon="rmx.rocket"
  />
</c-lbdocs.doc_card.grid>

## References

<c-lbdocs.doc_card.grid cols="2">
  <c-lbdocs.doc_card
    title="labb CLI"
    summary="Command-line tools for component development"
    href="{% doc_url '2_references/0_labb_cli.md' 'ui' %}"
    icon="rmx.terminal"
  />

  <c-lbdocs.doc_card
    title="Configuration"
    summary="Configure labb for your project"
    href="{% doc_url '2_references/1_config_yaml.md' 'ui' %}"
    icon="rmx.settings-3"
  />
</c-lbdocs.doc_card.grid>

## Components

{% get_components_menu as components %}

<div class="not-prose grid md:grid-cols-2 gap-4 my-8">
{% for component in components %}
  <div><a class="link link-hover text-lg" href="{{ component.path }}">{{ component.title }}</a></div>
{% endfor %}
</div>
