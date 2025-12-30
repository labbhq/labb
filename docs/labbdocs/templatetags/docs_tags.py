import json

from django import template
from django.conf import settings
from django.template.loader import get_template
from django.utils.safestring import mark_safe

from labb.components.registry import (
    ComponentRegistry,
    get_component_names,
    load_component_spec,
)
from labbicons.metadata import remix

from ..doc_parser import resolve_file_path_to_url
from ..seo_utils import (
    SEOMetadata,
    generate_article_schema,
    generate_breadcrumb_schema,
    generate_software_schema,
)

register = template.Library()


@register.filter
def get_component_spec(component_name):
    """
    Get component specification from the labb registry.
    Usage: {{ "button"|get_component_spec }}
    """
    return load_component_spec(component_name)


@register.simple_tag
def show_component_example(path, style="tab", previewStyle="flex-center"):
    """
    Show a component example by reading from a template file and rendering it.

    Args:
        path (str): Path to the example template relative to lb-examples/
        style (str): Style to display the example (default: "tab")

    Returns:
        str: Rendered component example
    """
    # Get the template for rendering
    template = get_template(f"lb-examples/{path}.html")
    rendered_content = template.render({})

    # Get raw content from the registry
    registry = ComponentRegistry()
    raw_content = registry.get_example_raw_content(path)
    if raw_content is None:
        raise ValueError(f"Template does not exist: {path}")

    # Load the component_example template
    component_example_template = get_template(
        f"cotton/lbdocs/component_example/style/{style}.html"
    )

    # Create context for the component_example template
    context = {
        "slot": rendered_content,
        "code": raw_content,
        "title": path.replace("/", "_").replace("-", "_"),
        "previewStyle": previewStyle,
    }

    # Render the component_example template with the context
    return component_example_template.render(context)


@register.simple_tag
def load_icon_metadata():
    """
    Load icon metadata from the labbicons metadata module and return as a dictionary.
    Uses caching to avoid repeated JSON parsing.
    Usage: {% load_icon_metadata as icons_data %}
    """
    from django.core.cache import cache

    cache_key = "labbicons_remix_metadata"
    icons_data = cache.get(cache_key)

    if icons_data is None:
        icons_data = remix()
        # Cache for 1 hour (or longer in production)
        cache.set(cache_key, icons_data, 3600)

    return icons_data


@register.simple_tag
def get_all_component_names():
    """
    Get sorted list of all component names from the component registry.
    Usage: {% get_all_component_names as component_names %}
    """
    names = get_component_names()
    return sorted(names)


@register.simple_tag(takes_context=True)
def get_components_menu(context):
    """
    Get high-level components from the Components menu in the doc config.
    Returns a list of dicts with 'title' and 'path' keys.
    Usage: {% get_components_menu as components %}
    """
    config = context.get("config", {})
    menu = config.get("menu", [])

    # Find the Components menu item
    components_menu = None
    for item in menu:
        if item.get("title") == "Components":
            components_menu = item
            break

    if not components_menu:
        return []

    # Get the children (should be the "Basics" section)
    children = components_menu.get("children", [])
    if not children:
        return []

    # Find the "Basics" section and get its direct children (high-level components)
    components = []
    for child in children:
        if child.get("title") == "Basics":
            # Get direct children - these are the high-level components
            basics_children = child.get("children", [])
            for component in basics_children:
                # Only include items that have a path (not nested submenus)
                if component.get("path"):
                    components.append(
                        {
                            "title": component.get("title", ""),
                            "path": component.get("path", ""),
                        }
                    )
            break

    # Sort by title
    return sorted(components, key=lambda x: x["title"])


@register.simple_tag(takes_context=True)
def doc_url(context, file_path, doc_name=None):
    """
    Resolve a markdown file path to its corresponding URL path.
    Uses the doc_name from context to determine the appropriate URL prefix.

    Args:
        context: Django template context
        file_path (str): Relative path to the markdown file (e.g., "1_getting_started/2_installation.md")

    Usage:
        {% doc_url "1_getting_started/2_installation.md" %}

    Returns:
        str: URL path (e.g., "/docs/ui/getting-started/installation/")
    """
    # Get the doc_name from context to determine URL prefix
    doc_name = doc_name or context.get("doc_name")

    # Map view names to URL prefixes
    url_prefix_map = {
        "ui": "/docs/ui",
        "icons": "/docs/icons",
    }

    if doc_name not in url_prefix_map:
        raise ValueError(
            f"Invalid doc_name: {doc_name} when resolving doc_url for {file_path}"
        )

    url_prefix = url_prefix_map[doc_name]

    # Use the extracted function from doc_parser
    return resolve_file_path_to_url(file_path, url_prefix)


@register.simple_tag
def doc_github_url(component_name):
    """
    Get the GitHub URL for a component.
    Usage: {% doc_github_url "button" %}
    """
    component_name = component_name.replace("c-lb.", "")
    return f"https://github.com/labbhq/labb/tree/main/labb/templates/cotton/lb/{component_name}"


@register.filter
def is_full_url(value):
    """
    Check if a value is a full URL (starts with http:// or https://).
    Usage: {{ seo.og_image|is_full_url }}
    """
    if not value:
        return False
    return value.startswith(("http://", "https://"))


@register.simple_tag(takes_context=True)
def get_seo_metadata(context, doc_info=None):
    """
    Get SEO metadata for the current page.
    Uses pre-computed data from YAML (generated at build time).

    Usage: {% get_seo_metadata doc_info as seo %}
    """
    doc_info = doc_info or context.get("doc_info", {})
    request = context.get("request")

    # Get site URL from request
    site_url = ""
    if request:
        protocol = "https" if request.is_secure() else "http"
        site_url = f"{protocol}://{request.get_host()}"

    # Get SEO configuration from LABB_DOCS.seo
    labb_docs = getattr(settings, "LABB_DOCS", {})
    seo_config = labb_docs.get("seo", {})

    # Use pre-computed SEO data from YAML
    metadata = doc_info.get("seo", {}).copy()

    # Make canonical URL absolute
    if metadata.get("canonical_url"):
        metadata["canonical_url"] = site_url + metadata["canonical_url"]

    # Add site-level twitter handles if not set
    if not metadata.get("twitter_site"):
        metadata["twitter_site"] = seo_config.get("twitter_site")

    # Add site name and locale
    metadata["site_name"] = seo_config.get("site_name", "Labb")
    metadata["locale"] = seo_config.get("default_locale", "en_US")

    return metadata


@register.simple_tag(takes_context=True)
def generate_structured_data(context, doc_info=None):
    """
    Generate JSON-LD structured data for the current page.
    Usage: {% generate_structured_data doc_info %}
    """
    doc_info = doc_info or context.get("doc_info", {})
    request = context.get("request")

    # Get site URL from request
    site_url = ""
    if request:
        protocol = "https" if request.is_secure() else "http"
        site_url = f"{protocol}://{request.get_host()}"

    # Get SEO configuration from LABB_DOCS.seo
    labb_docs = getattr(settings, "LABB_DOCS", {})
    seo_config = labb_docs.get("seo", {})

    site_name = seo_config.get("site_name", "Labb")
    default_image = seo_config.get("default_image", "")
    default_author = seo_config.get("default_author", "Labb Team")
    default_locale = seo_config.get("default_locale", "en_US")

    # Create SEO metadata
    seo = SEOMetadata(
        doc_info=doc_info,
        site_name=site_name,
        site_url=site_url,
        default_image=default_image,
        default_author=default_author,
        default_locale=default_locale,
    )

    schemas = []

    # Add breadcrumb schema
    url_path = doc_info.get("url_path", "")
    if url_path:
        schemas.append(generate_breadcrumb_schema(url_path, site_url))

    # Add article schema
    schemas.append(generate_article_schema(seo, site_url))

    # Add software schema for component pages
    frontmatter = doc_info.get("frontmatter", {})
    if component_name := frontmatter.get("component"):
        description = frontmatter.get("description", "")
        schemas.append(generate_software_schema(component_name, description, site_url))

    # Convert to JSON
    json_ld = json.dumps(schemas, indent=2)

    return mark_safe(f'<script type="application/ld+json">\n{json_ld}\n</script>')


@register.simple_tag(takes_context=True)
def get_blog_posts(context, doc_name="blog"):
    """
    Get all blog posts sorted by published_time (most recent first).
    Excludes the index page and returns posts with their metadata.

    Usage: {% get_blog_posts as posts %}
    """
    config = context.get("config", {})
    pages = config.get("pages", {})

    posts = []
    for url_path, page_data in pages.items():
        # Skip the index page
        if url_path.endswith("/index/"):
            continue

        # Only include posts (pages under /blog/posts/)
        if "/posts/" in url_path:
            frontmatter = page_data.get("frontmatter", {})
            seo = page_data.get("seo", {})

            # Get published_time for sorting (use seo data if available, fallback to frontmatter)
            published_time = seo.get("published_time") or frontmatter.get(
                "published_time"
            )

            posts.append(
                {
                    "url_path": url_path,
                    "title": frontmatter.get("title", ""),
                    "description": frontmatter.get("description", ""),
                    "author": frontmatter.get("author", ""),
                    "published_time": published_time,
                    "modified_time": frontmatter.get("modified_time", ""),
                    "tags": frontmatter.get("tags", []),
                    "og_image": seo.get("og_image", ""),
                }
            )

    # Sort by published_time (most recent first)
    # Posts without published_time go to the end
    def sort_key(post):
        published = post.get("published_time") or ""
        if not published:
            # Posts without dates go to the end
            return (False, "")

        # Handle both date objects and strings
        from datetime import date, datetime

        if isinstance(published, (date, datetime)):
            # Convert date/datetime object to string for sorting
            date_str = published.strftime("%Y-%m-%d")
        elif isinstance(published, str):
            # Extract date portion for consistent sorting (handle datetime strings)
            date_str = published[:10] if len(published) >= 10 else published
        else:
            # Fallback: convert to string
            date_str = (
                str(published)[:10] if len(str(published)) >= 10 else str(published)
            )

        # Return tuple: (has_date, date_string) for proper sorting
        # Reverse=True will put newest dates first
        return (True, date_str)

    posts.sort(key=sort_key, reverse=True)

    return posts
