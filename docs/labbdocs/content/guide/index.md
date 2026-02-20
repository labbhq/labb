---
title: Guide
description: Getting started guides and reference documentation for labb
doc_show_toc: false
---

{% load docs_tags %}

## Getting Started

<c-lbdocs.labbstart_info class="my-6" />

<c-lbdocs.doc_card.grid cols="3">
  <c-lbdocs.doc_card
    title="labbstart"
    summary="Scaffold a new Django project with labb—quickest way to get running"
    href="{% doc_url '1_getting_started/0_labbstart.md' 'guide' %}"
    icon="rmx.rocket-2"
  />

  <c-lbdocs.doc_card
    title="Introduction"
    summary="Learn about labb and how it simplifies Django UI development"
    href="{% doc_url '1_getting_started/1_introduction.md' 'guide' %}"
    icon="rmx.file-text"
  />

  <c-lbdocs.doc_card
    title="Installation"
    summary="Add labb to your existing Django project"
    href="{% doc_url '1_getting_started/2_installation.md' 'guide' %}"
    icon="rmx.download"
  />

  <c-lbdocs.doc_card
    title="Quick Start"
    summary="A quick start guide to get you up and running with labb features"
    href="{% doc_url '1_getting_started/3_quick_start.md' 'guide' %}"
    icon="rmx.rocket"
  />
</c-lbdocs.doc_card.grid>

## References

<c-lbdocs.doc_card.grid cols="2">
  <c-lbdocs.doc_card
    title="labb CLI"
    summary="Command-line tools for component development"
    href="{% doc_url '3_references/0_labb_cli.md' 'guide' %}"
    icon="rmx.terminal"
  />

  <c-lbdocs.doc_card
    title="Configuration"
    summary="Configure labb for your project"
    href="{% doc_url '3_references/1_config_yaml.md' 'guide' %}"
    icon="rmx.settings-3"
  />
</c-lbdocs.doc_card.grid>
