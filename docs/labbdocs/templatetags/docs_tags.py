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

from ..constants import DEFAULT_BANNER_ID, DISMISSED_BANNERS_SESSION_KEY
from ..doc_parser import DocRender, resolve_file_path_to_url
from ..seo_utils import (
    SEOMetadata,
    generate_article_schema,
    generate_breadcrumb_schema,
    generate_software_schema,
)

register = template.Library()


@register.simple_tag
def search_enabled():
    """Whether `labbdocs.search` is installed."""
    from django.apps import apps

    return apps.is_installed("labbdocs.search")


@register.simple_tag(takes_context=True)
def labb_docs_banner(context):
    """
    Return the announcement banner config from LABB_DOCS["banner"], or None.

    Dismissal is persisted server-side (session), so a dismissed banner is not
    re-emitted — a Datastar full-page morph therefore cannot bring it back.

    Usage: {% labb_docs_banner as banner %}
    """
    labb_docs = getattr(settings, "LABB_DOCS", {})
    banner = labb_docs.get("banner") or None
    if not banner or not banner.get("text"):
        return None
    request = context.get("request")
    if request is not None and banner.get("dismissible"):
        banner_id = banner.get("id", DEFAULT_BANNER_ID)
        dismissed = getattr(request, "session", {}).get(
            DISMISSED_BANNERS_SESSION_KEY, []
        )
        if banner_id in dismissed:
            return None
    return banner


@register.filter
def get_component_spec(component_name):
    """
    Get component specification from the labb registry.
    Usage: {{ "button"|get_component_spec }}
    """
    return load_component_spec(component_name)


@register.simple_tag(takes_context=True)
def show_component_example(context, path, style="", previewStyle="flex-center"):
    """
    Show a component example by reading from a template file and rendering it.

    Args:
        path (str): Path to the example template relative to lb-examples/
        style (str): Style to display the example. When empty, the default is
            chosen by doc type: guide docs render "stacked" (preview above code),
            everything else (ui component docs) renders "tab". An explicit style
            passed on the usage always wins.

    Returns:
        str: Rendered component example
    """
    if not style:
        style = "stacked" if context.get("doc_name") == "guide" else "tab"

    template = get_template(f"lb-examples/{path}.html")
    rendered_content = template.render({})

    registry = ComponentRegistry()
    raw_content = registry.get_example_raw_content(path)
    if raw_content is None:
        raise ValueError(f"Template does not exist: {path}")

    component_example_template = get_template(
        f"cotton/lbdocs/component_example/style/{style}.html"
    )

    context = {
        "slot": rendered_content,
        "code": raw_content,
        "title": path.replace("/", "_").replace("-", "_"),
        "previewStyle": previewStyle,
    }

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


# Stands in for a component whose doc page has no `icon:` frontmatter. Deliberately
# plain, so a missing icon reads as unfinished rather than as a choice.
COMPONENT_FALLBACK_ICON = "rmx.square"


def _doc_config(doc_name):
    """Load a doc type's config by name.

    DocRender holds an mtime-checked module-level cache, so this is an in-memory
    dict lookup after the first call.
    """
    labb_docs = getattr(settings, "LABB_DOCS", {})
    yaml_file_path = labb_docs.get("types", {}).get(doc_name, {}).get("config")
    if not yaml_file_path:
        return {}
    return DocRender(yaml_file_path).docs_data


@register.simple_tag(takes_context=True)
def get_components_menu(context, doc_name):
    """
    Get high-level components from the Components menu of a doc type's config.
    Returns a list of dicts with 'title', 'path' and 'icon' keys, sorted by title.

    The context `config` is used when it already holds the requested doc type
    (a doc page rendering its own grid); otherwise the config is loaded. This
    lets surfaces without a doc context — the homepage — render the same grid.

    Usage: {% get_components_menu "ui" as components %}
    """
    config = context.get("config") or {}
    if config.get("doc_name") != doc_name:
        config = _doc_config(doc_name)

    components = []
    for category in config.get("menu", []):
        for component in category.get("children", []):
            if component.get("path"):
                components.append(
                    {
                        "title": component.get("title", ""),
                        "path": component.get("path", ""),
                        "icon": component.get("icon") or COMPONENT_FALLBACK_ICON,
                    }
                )

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
    doc_name = doc_name or context.get("doc_name")

    url_prefix_map = {
        "ui": "/docs/ui",
        "guide": "/docs/guide",
        "icons": "/docs/icons",
    }

    if doc_name not in url_prefix_map:
        raise ValueError(
            f"Invalid doc_name: {doc_name} when resolving doc_url for {file_path}"
        )

    return resolve_file_path_to_url(file_path, url_prefix_map[doc_name])


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

    site_url = ""
    if request:
        protocol = "https" if request.is_secure() else "http"
        site_url = f"{protocol}://{request.get_host()}"

    labb_docs = getattr(settings, "LABB_DOCS", {})
    seo_config = labb_docs.get("seo", {})

    metadata = doc_info.get("seo", {}).copy()

    if metadata.get("canonical_url"):
        metadata["canonical_url"] = site_url + metadata["canonical_url"]

    if not metadata.get("twitter_site"):
        metadata["twitter_site"] = seo_config.get("twitter_site")

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

    site_url = ""
    if request:
        protocol = "https" if request.is_secure() else "http"
        site_url = f"{protocol}://{request.get_host()}"

    labb_docs = getattr(settings, "LABB_DOCS", {})
    seo_config = labb_docs.get("seo", {})

    site_name = seo_config.get("site_name", "Labb")
    default_image = seo_config.get("default_image", "")
    default_author = seo_config.get("default_author", "Labb Team")
    default_locale = seo_config.get("default_locale", "en_US")

    seo = SEOMetadata(
        doc_info=doc_info,
        site_name=site_name,
        site_url=site_url,
        default_image=default_image,
        default_author=default_author,
        default_locale=default_locale,
    )

    schemas = []

    url_path = doc_info.get("url_path", "")
    if url_path:
        schemas.append(generate_breadcrumb_schema(url_path, site_url))

    schemas.append(generate_article_schema(seo, site_url))

    frontmatter = doc_info.get("frontmatter", {})
    if component_name := frontmatter.get("component"):
        description = frontmatter.get("description", "")
        schemas.append(generate_software_schema(component_name, description, site_url))

    json_ld = json.dumps(schemas, indent=2)

    return mark_safe(f'<script type="application/ld+json">\n{json_ld}\n</script>')


@register.simple_tag(takes_context=True)
def get_blog_posts(context, doc_name="blog"):
    """
    Get all blog posts sorted by published_time (most recent first).
    Excludes the index page and returns posts with their metadata.

    Each post may include ``card_icon`` (from frontmatter, or inferred:
    YouTube URL → rmx.youtube, other external → rmx.external-link, else rmx.article).

    Usage: {% get_blog_posts as posts %}
    """
    config = context.get("config", {})
    pages = config.get("pages", {})

    posts = []
    for url_path, page_data in pages.items():
        if url_path.endswith("/index/"):
            continue

        if "/posts/" in url_path:
            frontmatter = page_data.get("frontmatter", {})
            seo = page_data.get("seo", {})

            published_time = seo.get("published_time") or frontmatter.get(
                "published_time"
            )

            external_url = (frontmatter.get("external_url") or "").strip()

            card_icon = (frontmatter.get("card_icon") or "").strip()
            if not card_icon:
                if external_url:
                    u = external_url.lower()
                    if "youtube.com" in u or "youtu.be" in u:
                        card_icon = "rmx.youtube"
                    else:
                        card_icon = "rmx.external-link"
                else:
                    card_icon = "rmx.article"

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
                    "external_url": external_url,
                    "is_external": bool(external_url),
                    "card_icon": card_icon,
                }
            )

    def sort_key(post):
        """Sort newest first; undated posts sort to the end."""
        published = post.get("published_time") or ""
        if not published:
            return (False, "")

        from datetime import date, datetime

        if isinstance(published, (date, datetime)):
            date_str = published.strftime("%Y-%m-%d")
        elif isinstance(published, str):
            date_str = published[:10] if len(published) >= 10 else published
        else:
            date_str = (
                str(published)[:10] if len(str(published)) >= 10 else str(published)
            )

        return (True, date_str)

    posts.sort(key=sort_key, reverse=True)

    return posts
