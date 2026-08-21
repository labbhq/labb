"""URLconf for the labbdocs test suite.

labbdocs templates reverse a few names the consumer site owns (`index`,
`set_theme`, `llms_txt`), so they get placeholder routes here. Search is mounted
at /search/; test_mount_point.py overrides this urlconf to prove nothing in the
package assumes that path.
"""

from django.apps import apps
from django.http import HttpResponse
from django.urls import include, path

from labb.shortcuts import set_theme_view


def _stub(request, *args, **kwargs):
    return HttpResponse("")


urlpatterns = [
    path("", _stub, name="index"),
    path("", include("labbdocs.urls")),
    path("set-theme/", set_theme_view, name="set_theme"),
    path("llms.txt", _stub, name="llms_txt"),
    # The blocks reader in tests/blocks_reader.py links results here.
    path("blocks/<slug:category>/<slug:slug>/", _stub, name="blocks_detail"),
]

if apps.is_installed("labbdocs.search"):
    urlpatterns += [path("search/", include("labbdocs.search.urls"))]
