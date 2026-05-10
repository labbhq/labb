---
title: labb blog
description: "labb blog: Django UI tutorials, releases, and opinions on django-cotton, Tailwind CSS, and daisyUI. Updates from the labb.io team."
keywords: "labb blog, django ui blog, django components tutorial, labb.io, django-cotton news"
doc_show_toc: false
doc_hide_title: true
doc_hide_drawer: true
---

{% load docs_tags %}

## Latest Posts

{% get_blog_posts as posts %}

{% if posts %}
  <c-lbdocs.doc_card.grid cols="1">
    {% for post in posts %}
      <c-lbdocs.doc_card
        title="{{ post.title }}"
        summary="{{ post.description }}"
        href="{% if post.is_external %}{{ post.external_url }}{% else %}{{ post.url_path }}{% endif %}"
        {% if post.is_external %}external="1"{% endif %}
        icon="{{ post.card_icon }}"
      />
    {% endfor %}
  </c-lbdocs.doc_card.grid>
{% else %}
  <p class="text-base-content/60">No blog posts yet. Check back soon!</p>
{% endif %}
