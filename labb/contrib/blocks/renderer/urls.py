from django.urls import include, path

from . import views
from .registry import registry


def build_urlpatterns():
    patterns = [
        path("", views.gallery, name="gallery"),
    ]
    for ref, meta in registry.blocks.items():
        vendor = meta["vendor"]
        category = meta["category"]
        slug = meta["slug"]
        patterns.append(
            path(
                f"{vendor}/{category}/{slug}/",
                views.detail,
                {"ref": ref},
                name=f"detail-{ref.replace('/', '-')}",
            )
        )
        patterns.append(
            path(
                f"{vendor}/{category}/{slug}/thumbnail",
                views.thumbnail,
                {"ref": ref},
                name=f"thumbnail-{ref.replace('/', '-')}",
            )
        )
        if meta["type"] == "fullstack":
            module_path = f"{vendor}.{category}.{slug}.urls"
            patterns.append(
                path(f"{vendor}/{category}/{slug}/preview/", include(module_path))
            )
        else:
            patterns.append(
                path(
                    f"{vendor}/{category}/{slug}/preview/",
                    views.fe_preview,
                    {"ref": ref},
                    name=f"preview-{ref.replace('/', '-')}",
                )
            )
    return patterns


urlpatterns = build_urlpatterns()
