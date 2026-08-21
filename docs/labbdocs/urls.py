from django.urls import path, re_path

from . import views

# Raw markdown: appending .md to any doc URL serves the source. The no-slash
# form is matched explicitly so cited URLs resolve without an APPEND_SLASH redirect.
urlpatterns = [
    re_path(r"^docs/ui/(?P<path>.+\.md)$", views.ui_docs, name="ui_docs_md"),
    re_path(r"^docs/guide/(?P<path>.+\.md)$", views.guide_docs, name="guide_docs_md"),
    re_path(r"^docs/icons/(?P<path>.+\.md)$", views.icons_docs, name="icons_docs_md"),
    re_path(r"^blog/(?P<path>.+\.md)$", views.blog_docs, name="blog_docs_md"),
    path("docs/ui/", views.ui_docs, name="ui_docs"),
    path(
        "docs/ui/<path:path>/",
        views.ui_docs,
        name="ui_docs_detail",
    ),
    path("docs/guide/", views.guide_docs, name="guide_docs"),
    path(
        "docs/guide/<path:path>/",
        views.guide_docs,
        name="guide_docs_detail",
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
    path("docs/banner/dismiss/", views.dismiss_banner, name="dismiss_banner"),
]
