"""Wiring a block collection into a Django urlconf."""

from pathlib import Path
from typing import Optional


def include_blocks(collection, ref: Optional[str] = None):
    """
    Wire blocks from a collection into a Django urlconf.

    Auto-discovery (no ref):
        Walks collection.__path__[0] for directories at depth
        {vendor}/{category}/{slug}/ that contain a urls.py file.
        Returns a list of path() entries, each mounted at
        "{vendor}/{category}/{slug}/".

    Single-block (ref="vendor/category/slug"):
        Parses the ref and returns include("collection.vendor.category.slug.urls").
        No prefix is added; the caller's path() prefix applies.
    """
    from django.urls import include, path as django_path

    collection_root = Path(collection.__path__[0])
    collection_name = collection.__name__

    if ref is not None:
        parts = ref.split("/")
        if len(parts) != 3:
            raise ValueError(f"Block ref must be vendor/category/slug, got: {ref!r}")
        vendor, category, slug = parts
        module_path = f"{collection_name}.{vendor}.{category}.{slug}.urls"
        return include(module_path)

    # Auto-discover all blocks
    patterns = []
    skip_vendor = {"models", "migrations", "templates", "fixtures", "__pycache__"}
    skip_category = {"models", "__pycache__"}

    for vendor_dir in sorted(collection_root.iterdir()):
        if (
            not vendor_dir.is_dir()
            or vendor_dir.name in skip_vendor
            or vendor_dir.name.startswith("_")
        ):
            continue
        for category_dir in sorted(vendor_dir.iterdir()):
            if (
                not category_dir.is_dir()
                or category_dir.name in skip_category
                or category_dir.name.startswith("_")
            ):
                continue
            for slug_dir in sorted(category_dir.iterdir()):
                if not slug_dir.is_dir() or slug_dir.name.startswith("_"):
                    continue
                if not (slug_dir / "urls.py").exists():
                    continue
                vendor = vendor_dir.name
                category = category_dir.name
                slug = slug_dir.name
                prefix = f"{vendor}/{category}/{slug}/"
                module_path = f"{collection_name}.{vendor}.{category}.{slug}.urls"
                patterns.append(django_path(prefix, include(module_path)))

    return patterns
