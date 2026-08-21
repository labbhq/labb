"""Search mounted somewhere other than /search/, to prove nothing assumes it."""

from django.urls import include, path

urlpatterns = [
    path("find/docs/", include("labbdocs.search.urls")),
]
