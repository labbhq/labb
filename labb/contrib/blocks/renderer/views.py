"""Block renderer views — dev/preview surface only, never mounted in production."""

from pathlib import Path

from django.http import FileResponse, Http404
from django.shortcuts import render

from labb.contrib.blocks import render_page

from .registry import registry
from .tree import file_tree

THUMBNAIL_MODES = ("light", "dark")


def _thumbnail_path(meta, mode=None):
    """The captured thumbnail for a block, preferring the theme-specific capture.

    The capture script writes `{stem}.light.png` and `{stem}.dark.png`. A
    block.yaml `thumbnail:` field names the base file; its themed siblings are
    tried first, so a manifest written before the light/dark split needs no edit
    and a block with only one image still renders.
    """
    block_dir = Path(registry.repo_path) / meta["category"] / meta["slug"]
    declared = Path(meta.get("thumbnail") or f"thumbnails/{meta['slug']}.png")
    stem = declared.with_suffix("")

    candidates = []
    if mode in THUMBNAIL_MODES:
        candidates.append(f"{stem}.{mode}{declared.suffix}")
    candidates.append(f"{stem}.light{declared.suffix}")
    candidates.append(str(declared))

    for candidate in candidates:
        path = block_dir / candidate
        if path.is_file():
            return path
    return None


def gallery(request):
    by_category = {}
    for ref, meta in registry.blocks.items():
        cat = meta["category"]
        card = {"ref": ref, **meta}
        base = f"/{meta['vendor']}/{cat}/{meta['slug']}/thumbnail"
        card["thumbnail_url"] = base if _thumbnail_path(meta) else ""
        # Both sources are rendered and CSS picks one, so the image follows the
        # theme toggle without a reload.
        card["thumbnail_url_dark"] = (
            f"{base}?mode=dark" if _thumbnail_path(meta, "dark") else ""
        )
        by_category.setdefault(cat, []).append(card)
    for cards in by_category.values():
        cards.sort(key=lambda c: c["slug"])

    return render(
        request,
        "cotton/lbb/renderer/gallery.html",
        {
            "categories": sorted(by_category.items()),
        },
    )


def thumbnail(request, ref):
    """Serve a block's captured thumbnail PNG for the gallery grid."""
    meta = registry.blocks.get(ref)
    mode = request.GET.get("mode")
    path = _thumbnail_path(meta, mode) if meta else None
    if path is None:
        raise Http404("thumbnail not captured")
    return FileResponse(path.open("rb"), content_type="image/png")


def detail(request, ref):
    meta = registry.blocks.get(ref, {})
    vendor = meta.get("vendor", "")
    category = meta.get("category", "")
    slug = meta.get("slug", "")

    block_dir = Path(registry.repo_path) / category / slug

    raw_tabs = {}
    for fname in ["views.py", "urls.py"]:
        fpath = block_dir / fname
        if fpath.exists():
            raw_tabs[fname] = fpath.read_text()

    templates_dir = block_dir / "templates"
    if templates_dir.exists():
        for tfile in sorted(templates_dir.rglob("*")):
            if tfile.is_file():
                rel = tfile.relative_to(block_dir)
                raw_tabs[str(rel)] = tfile.read_text()

    tabs = [{"fname": fname, "content": content} for fname, content in raw_tabs.items()]

    return render(
        request,
        "cotton/lbb/renderer/detail.html",
        {
            "meta": meta,
            "slug": slug,
            "vendor": vendor,
            "category": category,
            "preview_url": f"/{vendor}/{category}/{slug}/preview/",
            "tabs": tabs,
            "tree": file_tree(raw_tabs),
        },
    )


def fe_preview(request, ref):
    meta = registry.blocks.get(ref, {})
    vendor = meta.get("vendor", "")
    category = meta.get("category", "")
    slug = meta.get("slug", "")

    template_name = f"{vendor}/{category}/{slug}/pages/index.html"
    preview_context = dict(meta.get("preview_context", {}))
    return render_page(request, template_name, preview_context, title=slug)
