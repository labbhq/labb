from django.urls import path

from . import views

urlpatterns = [
    path("docs/ui/", views.ui_docs, name="ui_docs"),
    path(
        "docs/ui/<path:path>/",
        views.ui_docs,
        name="ui_docs_detail",
    ),
    path("docs/icons/", views.icons_docs, name="icons_docs"),
    path(
        "docs/icons/packs/remix/load/",
        views.load_icon_categories,
        name="load_icon_categories",
    ),
    path(
        "docs/icons/<path:path>/",
        views.icons_docs,
        name="icons_docs_detail",
    ),
    path("blog/", views.blog_docs, name="blog_docs"),
    path(
        "blog/<path:path>/",
        views.blog_docs,
        name="blog_docs_detail",
    ),
    path("sitemap.xml", views.sitemap_view, name="sitemap"),
    path("robots.txt", views.robots_txt_view, name="robots_txt"),
]
