---
title: UI Components
description: "Browse 50+ Django UI components for labb: buttons, forms, charts, and layouts. Built with django-cotton, Tailwind CSS, and daisyUI 5; server-rendered by default."
keywords: "django ui components, django component library, labb components, django-cotton, tailwind django, daisyui django, labb.io docs"
doc_show_toc: false
---

{% load docs_tags %}


{% get_components_menu as components %}

<div class="not-prose grid md:grid-cols-3 gap-3 my-4">
{% for component in components %}
  <div><a class="link link-hover text-sm" href="{{ component.path }}">{{ component.title }}</a></div>
{% endfor %}
</div>
