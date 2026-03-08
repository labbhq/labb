---
title: UI Components
description: labb UI component library documentation
doc_show_toc: false
---

{% load docs_tags %}


{% get_components_menu as components %}

<div class="not-prose grid md:grid-cols-3 gap-3 my-4">
{% for component in components %}
  <div><a class="link link-hover text-sm" href="{{ component.path }}">{{ component.title }}</a></div>
{% endfor %}
</div>
