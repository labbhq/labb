from pathlib import Path

from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.template import Context, Template
from django.urls import reverse
from django_cotton import render_component

from labbicons.metadata import remix

from .doc_parser import DocRender


def _build_docs_context(
    config, topnav_title, doc_name, request, doc_info=None, doc_layout=None
):
    """
    Build common context for documentation views.

    Args:
        config: Configuration data from docs.yaml
        topnav_title: Title for the top navigation
        doc_name: Name of the documentation
        doc_info: Optional document info for specific page rendering
        doc_layout: Optional layout override

    Returns:
        dict: Context dictionary for template rendering
    """
    context = {
        "config": config,
        "topnavTitle": topnav_title,
        "showDrawerToggle": True,
        "doc_name": doc_name,
        "doc_url": request.build_absolute_uri(),
        "llms_txt_url": request.build_absolute_uri(reverse("llms_txt")),
    }

    if doc_info:
        context["doc_info"] = doc_info
        layout = doc_layout or doc_info.get("doc_layout") or "base"
        context["layout_component"] = f"lbdocs.layout.docs.{layout}"
    else:
        context["layout_component"] = "lbdocs.layout.docs.base"

    return context


def docs_view(request, doc_name, path=""):
    """
    Generic documentation view that handles documentation based on LABB_DOCS settings.

    Args:
        request: Django request object
        doc_name: Name of the documentation (must be configured in LABB_DOCS)
        path: Optional path within the documentation
    """
    # Get LABB_DOCS configuration from Django settings
    labb_docs = getattr(settings, "LABB_DOCS", {})
    doc_types = labb_docs.get("types", {})

    if doc_name not in doc_types:
        raise Http404(
            f"Documentation type '{doc_name}' not found in LABB_DOCS configuration"
        )

    doc_config = doc_types[doc_name]

    # Get the YAML file path from the configuration
    yaml_file_path = doc_config.get("config")
    if not yaml_file_path:
        raise Http404(f"No config path specified for documentation '{doc_name}'")

    # Initialize the DocRender with the YAML file path
    renderer = DocRender(yaml_file_path)

    # Load the docs.yaml file for menu
    docs_data = renderer.docs_data

    path = path or "index"

    # Check if this is a request for raw markdown (.md suffix)
    serve_raw_markdown = path.endswith(".md")
    if serve_raw_markdown:
        # Remove .md suffix for path processing
        path = path[:-3]

    # Get URL prefix from configuration or use default
    url_prefix = doc_config.get("url_prefix", f"/docs/{doc_name}")

    # Construct the full URL path
    url_path = f"{url_prefix}/{path}/"

    # Get document info (without rendering)
    doc_info = renderer.get_doc_info(url_path)

    # If there's an error loading the document, raise 404
    if doc_info.get("error"):
        raise Http404(f"Document not found: {doc_info['error']}")

    # If requesting raw markdown, serve the markdown content rendered with context
    if serve_raw_markdown:
        file_path = Path(doc_info.get("file_path", ""))
        if not file_path.exists():
            raise Http404("Markdown file not found")

        # Read the original markdown content
        with open(file_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()

        # Get title from configuration or use doc_name
        title = doc_config.get("title", doc_name.title())

        context = Context(
            {
                "request": request,
                "doc_info": doc_info,
                "config": docs_data,
                "topnavTitle": title,
            }
        )

        # Render the markdown content as a Django template
        template = Template(markdown_content)
        rendered_markdown = template.render(context)

        return HttpResponse(
            rendered_markdown, content_type="text/markdown; charset=utf-8"
        )

    # Get title and name from configuration or use defaults
    title = doc_config.get("title", doc_name.title())
    name = doc_config.get("name", doc_name)

    # Create context with the document info
    context = _build_docs_context(docs_data, title, name, request, doc_info)

    return render(request, "lbdocs/pages/docs.html", context)


def ui_docs(request, path=""):
    """UI documentation view."""
    return docs_view(request, "ui", path)


def icons_docs(request, path=""):
    """Icons documentation view."""
    return docs_view(request, "icons", path)


def blog_docs(request, path=""):
    """Blog documentation view."""
    return docs_view(request, "blog", path)


def sitemap_view(request):
    """
    Generate XML sitemap for all documentation pages.
    """
    from datetime import datetime

    # Get LABB_DOCS configuration from Django settings
    labb_docs = getattr(settings, "LABB_DOCS", {})
    doc_types = labb_docs.get("types", {})

    # Get current site URL
    protocol = "https" if request.is_secure() else "http"
    domain = request.get_host()
    site_url = f"{protocol}://{domain}"

    # Collect all URLs from all documentation types
    urls = []

    for doc_name, doc_config in doc_types.items():
        yaml_file_path = doc_config.get("config")
        if not yaml_file_path:
            continue

        # Initialize the DocRender with the YAML file path
        renderer = DocRender(yaml_file_path)
        docs_data = renderer.docs_data

        # Get all page paths
        pages = docs_data.get("pages", {})

        for url_path, page_data in pages.items():
            frontmatter = page_data.get("frontmatter", {})

            # Check if page should be indexed
            robots = frontmatter.get("robots", "index, follow")
            if "noindex" in robots:
                continue

            # Get priority and changefreq from frontmatter or use defaults
            priority = frontmatter.get("sitemap_priority", "0.8")
            changefreq = frontmatter.get("sitemap_changefreq", "weekly")

            # Get last modified time if available
            lastmod = frontmatter.get("modified_time")
            if not lastmod:
                lastmod = datetime.now().strftime("%Y-%m-%d")

            urls.append(
                {
                    "loc": f"{site_url}{url_path}",
                    "lastmod": lastmod,
                    "changefreq": changefreq,
                    "priority": priority,
                }
            )

    # Generate XML
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for url_data in urls:
        xml.append("  <url>")
        xml.append(f"    <loc>{url_data['loc']}</loc>")
        xml.append(f"    <lastmod>{url_data['lastmod']}</lastmod>")
        xml.append(f"    <changefreq>{url_data['changefreq']}</changefreq>")
        xml.append(f"    <priority>{url_data['priority']}</priority>")
        xml.append("  </url>")

    xml.append("</urlset>")

    return HttpResponse("\n".join(xml), content_type="application/xml")


def robots_txt_view(request):
    """
    Generate robots.txt file.
    """
    # Get current site URL for sitemap
    protocol = "https" if request.is_secure() else "http"
    domain = request.get_host()
    sitemap_url = f"{protocol}://{domain}/sitemap.xml"

    # Get robots.txt configuration from LABB_DOCS.seo
    labb_docs = getattr(settings, "LABB_DOCS", {})
    seo_config = labb_docs.get("seo", {})
    disallow_paths = seo_config.get("robots_disallow", [])

    lines = [
        "User-agent: *",
    ]

    # Add disallow directives
    if disallow_paths:
        for path in disallow_paths:
            lines.append(f"Disallow: {path}")
    else:
        lines.append("Disallow:")  # Allow all

    # Add sitemap URL
    lines.append("")
    lines.append(f"Sitemap: {sitemap_url}")

    return HttpResponse("\n".join(lines), content_type="text/plain")


def load_icon_categories(request):
    """
    Lazy load icon categories as rendered components.

    Accepts GET parameters:
    - offset: Starting index for categories (default: 0)
    - limit: Number of categories to load (default: 3)
    - icon_size: Size of icons (default: 24)

    Returns rendered HTML for the requested category sections.
    """
    from collections import defaultdict

    from django.core.cache import cache

    # Get parameters from request
    offset = int(request.GET.get("offset", 0))
    limit = int(request.GET.get("limit", 3))
    icon_size = request.GET.get("icon_size", "24")

    # Load icon metadata with caching
    cache_key = "labbicons_remix_metadata"
    icons_data = cache.get(cache_key)

    if icons_data is None:
        icons_data = remix()
        cache.set(cache_key, icons_data, 3600)

    icons = icons_data.get("icons", [])

    # Group icons by category (cache this too)
    categories_cache_key = "labbicons_categories_dict"
    categories_dict = cache.get(categories_cache_key)

    if categories_dict is None:
        categories_dict = defaultdict(list)
        for icon in icons:
            categories_dict[icon["category"]].append(icon)
        cache.set(categories_cache_key, dict(categories_dict), 3600)

    # Get sorted list of category names
    category_names = sorted(categories_dict.keys())

    # Slice categories based on offset and limit
    categories_to_load = category_names[offset : offset + limit]

    # Render each category component
    rendered_categories = []
    for idx, category_name in enumerate(categories_to_load):
        category_icons = categories_dict[category_name]
        start_index = offset + idx

        # Render the category section component
        rendered = render_component(
            request,
            "icon_category_section",  # TODO: Change to lbdocs.icon.category_section (seems to be a bug in cotton)
            category=category_name,
            icons=category_icons,
            icon_size=icon_size,
            start_index=str(start_index),
        )
        rendered_categories.append(rendered)

    # Concatenate all rendered categories
    return HttpResponse("".join(rendered_categories), content_type="text/html")
