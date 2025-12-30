---
title: labb blog
description: labb blog posts and articles
doc_show_toc: false
doc_hide_title: true
doc_hide_sidebar: true
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
        href="{{ post.url_path }}"
        icon="rmx.article"
      />
    {% endfor %}
  </c-lbdocs.doc_card.grid>
{% else %}
  <p class="text-base-content/60">No blog posts yet. Check back soon!</p>
{% endif %}
