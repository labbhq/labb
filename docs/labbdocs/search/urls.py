from django.urls import path

from . import views

app_name = "labbdocs_search"

urlpatterns = [
    path("", views.search_page, name="page"),
    path("palette/", views.palette, name="palette"),
]
