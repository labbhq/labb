---
title: Guide
description: Getting started guides and reference documentation for labb
doc_show_toc: false
---

{% load docs_tags %}

## Getting Started

<c-lbdocs.doc_card.grid cols="2">
  <c-lbdocs.doc_card
    title="Introduction"
    summary="Learn about labb and how it simplifies Django UI development"
    href="{% doc_url '1_getting_started/1_introduction.md' 'guide' %}"
    icon="rmx.file-text"
  />

  <c-lbdocs.doc_card
    title="Installation"
    summary="Set up labb for new or existing Django projects"
    href="{% doc_url '1_getting_started/2_installation.md' 'guide' %}"
    icon="rmx.download"
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
