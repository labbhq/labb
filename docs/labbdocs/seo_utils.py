"""
SEO utilities for labb documentation.
Provides metadata extraction and generation for search engine optimization.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage


class SEOMetadata:
    """
    Extracts and manages SEO metadata from documentation.
    """

    def __init__(
        self,
        doc_info: Dict,
        site_name: str = "labb",
        site_url: str = "",
        default_image: str = "",
        default_author: str = "labb",
        default_locale: str = "en_US",
    ):
        """
        Initialize SEO metadata.

        Args:
            doc_info: Document information from DocRender
            site_name: Name of the website
            site_url: Base URL of the website
            default_image: Default OG image URL
            default_author: Default author name
            default_locale: Default locale for Open Graph
        """
        self.doc_info = doc_info
        self.site_name = site_name
        self.site_url = site_url.rstrip("/")
        self.default_image = default_image
        self.default_author = default_author
        self.default_locale = default_locale
        self.frontmatter = doc_info.get("frontmatter", {})

    def get_title(self) -> str:
        """Get the page title with site name."""
        doc_title = self.frontmatter.get("title", "")
        component = self.frontmatter.get("component", "")
        title = doc_title or component or "Documentation"

        # Add site name suffix
        return f"{title} | {self.site_name}"

    def get_meta_title(self) -> str:
        """Get the meta title (without site name for social media)."""
        doc_title = self.frontmatter.get("title", "")
        component = self.frontmatter.get("component", "")
        return doc_title or component or "Documentation"

    def get_description(self) -> str:
        """Get the page description."""
        return self.frontmatter.get(
            "description",
            f"Documentation for {self.get_meta_title()}",
        )

    def get_keywords(self) -> Optional[str]:
        """Get keywords from frontmatter."""
        keywords = self.frontmatter.get("keywords", [])
        if isinstance(keywords, list):
            return ", ".join(keywords)
        return keywords or None

    def get_canonical_url(self) -> str:
        """Get the canonical URL for the page."""
        url_path = self.doc_info.get("url_path", "")
        if self.site_url and url_path:
            return urljoin(self.site_url, url_path)
        return url_path

    def get_og_image(self) -> str:
        """
        Get Open Graph image URL.
        Images are pre-generated at build time and stored as static files.

        Returns: Image URL (static file path or absolute URL)
        """
        # Check pre-computed SEO data first (from YAML)
        seo_data = self.doc_info.get("seo", {})
        og_image = seo_data.get("og_image")

        # Fall back to frontmatter if not in SEO data
        if not og_image:
            og_image = self.frontmatter.get("og_image")

        # Fall back to default image if still not found
        if not og_image:
            og_image = self.default_image

        return og_image or ""

    def get_og_type(self) -> str:
        """Get Open Graph type."""
        return self.frontmatter.get("og_type", "article")

    def get_robots(self) -> str:
        """Get robots meta tag value."""
        return self.frontmatter.get("robots", "index, follow")

    def get_author(self) -> str:
        """Get author name."""
        return self.frontmatter.get("author", self.default_author)

    def get_published_time(self) -> Optional[str]:
        """Get published time for articles."""
        return self.frontmatter.get("published_time")

    def get_modified_time(self) -> Optional[str]:
        """Get modified time for articles."""
        return self.frontmatter.get("modified_time")

    def get_twitter_card(self) -> str:
        """Get Twitter card type."""
        return self.frontmatter.get("twitter_card", "summary_large_image")

    def get_twitter_site(self) -> Optional[str]:
        """Get Twitter site handle."""
        return self.frontmatter.get("twitter_site")

    def get_twitter_creator(self) -> Optional[str]:
        """Get Twitter creator handle."""
        return self.frontmatter.get("twitter_creator")

    def get_component_tags(self) -> List[str]:
        """Get component-related tags for structured data."""
        tags = []
        if component := self.frontmatter.get("component"):
            tags.append(component)
        if daisy_ui := self.frontmatter.get("daisy_ui_component_name"):
            tags.append(daisy_ui)
        tags.extend(self.frontmatter.get("tags", []))
        return tags

    def to_dict(self) -> Dict:
        """Convert to dictionary for template context."""
        return {
            "title": self.get_title(),
            "meta_title": self.get_meta_title(),
            "description": self.get_description(),
            "keywords": self.get_keywords(),
            "canonical_url": self.get_canonical_url(),
            "og_image": self.get_og_image(),
            "og_type": self.get_og_type(),
            "robots": self.get_robots(),
            "author": self.get_author(),
            "published_time": self.get_published_time(),
            "modified_time": self.get_modified_time(),
            "twitter_card": self.get_twitter_card(),
            "twitter_site": self.get_twitter_site(),
            "twitter_creator": self.get_twitter_creator(),
            "site_name": self.site_name,
            "locale": self.default_locale,
            "tags": self.get_component_tags(),
        }


def generate_breadcrumb_schema(url_path: str, site_url: str) -> Dict:
    """
    Generate JSON-LD breadcrumb schema.

    Args:
        url_path: Current URL path (e.g., "/docs/ui/components/button/")
        site_url: Base site URL

    Returns:
        Dict with breadcrumb schema
    """
    parts = [p for p in url_path.strip("/").split("/") if p]
    breadcrumbs = []

    current_path = ""
    for i, part in enumerate(parts, start=1):
        current_path += f"/{part}"
        # Format breadcrumb name
        name = part.replace("-", " ").title()
        if i == 1:
            name = "Home"

        breadcrumbs.append(
            {
                "@type": "ListItem",
                "position": i,
                "name": name,
                "item": urljoin(site_url, current_path + "/"),
            }
        )

    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": breadcrumbs,
    }


def generate_article_schema(
    seo_metadata: SEOMetadata,
    site_url: str,
) -> Dict:
    """
    Generate JSON-LD article schema.

    Args:
        seo_metadata: SEO metadata object
        site_url: Base site URL

    Returns:
        Dict with article schema
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": seo_metadata.get_meta_title(),
        "description": seo_metadata.get_description(),
        "url": seo_metadata.get_canonical_url(),
        "author": {
            "@type": "Organization",
            "name": seo_metadata.get_author(),
        },
        "publisher": {
            "@type": "Organization",
            "name": seo_metadata.site_name,
            "url": site_url,
        },
    }

    # Add optional fields
    if og_image := seo_metadata.get_og_image():
        # For structured data, we need absolute URLs
        # If it's not already a full URL, resolve it using Django's static file storage
        if og_image and not og_image.startswith(("http://", "https://")):
            try:
                # Resolve static file URL using Django's static file storage
                static_url = staticfiles_storage.url(og_image)
            except Exception:
                # Fallback: construct URL manually using STATIC_URL setting
                static_url = urljoin(settings.STATIC_URL, og_image)

            if site_url:
                schema["image"] = urljoin(site_url, static_url)
            else:
                schema["image"] = static_url
        else:
            schema["image"] = og_image

    if published_time := seo_metadata.get_published_time():
        # Convert datetime objects to ISO format strings for JSON serialization
        if isinstance(published_time, datetime):
            schema["datePublished"] = published_time.isoformat()
        else:
            schema["datePublished"] = str(published_time)

    if modified_time := seo_metadata.get_modified_time():
        # Convert datetime objects to ISO format strings for JSON serialization
        if isinstance(modified_time, datetime):
            schema["dateModified"] = modified_time.isoformat()
        else:
            schema["dateModified"] = str(modified_time)

    if tags := seo_metadata.get_component_tags():
        schema["keywords"] = tags

    return schema


def generate_software_schema(
    component_name: str,
    description: str,
    site_url: str,
) -> Dict:
    """
    Generate JSON-LD software/code schema for component documentation.

    Args:
        component_name: Name of the component
        description: Component description
        site_url: Base site URL

    Returns:
        Dict with software schema
    """
    return {
        "@context": "https://schema.org",
        "@type": "SoftwareSourceCode",
        "name": component_name,
        "description": description,
        "programmingLanguage": "Django",
        "codeRepository": site_url,
        "runtimePlatform": "Django",
    }


def escape_svg_text(text: str) -> str:
    """
    Escape special characters for SVG text elements.

    Args:
        text: Text to escape

    Returns:
        Escaped text safe for SVG
    """
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def wrap_text(text: str, max_length: int) -> List[str]:
    """
    Wrap text into multiple lines based on max length.

    Args:
        text: Text to wrap
        max_length: Maximum characters per line

    Returns:
        List of text lines
    """
    if len(text) <= max_length:
        return [text]

    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        word_length = len(word) + 1  # +1 for space

        if current_length + word_length <= max_length:
            current_line.append(word)
            current_length += word_length
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)

    if current_line:
        lines.append(" ".join(current_line))

    return lines[:3]  # Max 3 lines


def generate_and_save_og_image_svg(
    title: str,
    output_path: Path,
    static_url_prefix: str,
    description: str = "",
    site_name: str = "Labb",
    component_tag: Optional[str] = None,
    doc_url: str = "labb.io",
    github_url: str = "github.com/labbhq/labb",
    width: int = 1200,
    height: int = 630,
    bg_color: str = "#ffffff",
    text_color: str = "#000000",
    accent_color: str = "#6366f1",
) -> str:
    """
    Generate an Open Graph image (PNG) from SVG and save it to a file.
    Returns the static file path using the provided static_url_prefix.

    Args:
        title: Page title (component name)
        output_path: Full path where to save the PNG file (should have .png extension)
        static_url_prefix: URL prefix for the static file (e.g., "/static/lbdocs/ograph")
        description: Component description
        site_name: Site name
        component_tag: Component tag (e.g., "c-lb.accordion")
        doc_url: Documentation URL (shortened for sustainability)
        github_url: GitHub repository URL (shortened for sustainability)
        width: Image width (default: 1200)
        height: Image height (default: 630)
        bg_color: Background color (default: white)
        text_color: Text color (default: black)
        accent_color: Accent color for highlights

    Returns:
        Static file path (e.g., "/static/lbdocs/ograph/abc123def456.png")
    """
    # Generate the SVG content
    svg = _generate_og_image_svg_content(
        title=title,
        description=description,
        site_name=site_name,
        component_tag=component_tag,
        doc_url=doc_url,
        github_url=github_url,
        width=width,
        height=height,
        bg_color=bg_color,
        text_color=text_color,
        accent_color=accent_color,
    )

    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Import cairosvg only when needed
    try:
        import cairosvg
    except ImportError:
        raise ImportError(
            "cairosvg is required for generating OG images. "
            "Install it with: pip install cairosvg"
        )

    # Convert SVG to PNG and save
    cairosvg.svg2png(
        bytestring=svg.encode("utf-8"),
        write_to=str(output_path),
        output_width=width,
        output_height=height,
    )

    # Return the static file path using the provided prefix
    filename = output_path.name
    # Ensure static_url_prefix ends with / if it doesn't already
    prefix = static_url_prefix.rstrip("/")
    return f"{prefix}/{filename}"


def _get_logo_svg_content(logo_fill: str, logo_text_fill: str, size: int = 140) -> str:
    """
    Get the labb logo SVG content as a string (copied from logo.html template).

    Args:
        logo_fill: Fill color for the logo background rectangles
        logo_text_fill: Fill color for the logo text/letters
        size: Height of the logo (default: 140 to match proportion)

    Returns:
        SVG string for the logo
    """
    # Using the actual logo from labb/docs/labbdocs/templates/cotton/lbdocs/logo.html
    # ViewBox: "30 140 310 100" - scaled to fit requested size
    # Original aspect ratio: 310:100 = 3.1:1
    width = size * 3.1

    return f'''<svg xmlns="http://www.w3.org/2000/svg" height="{size}" width="{width}" viewBox="30 140 310 100" preserveAspectRatio="xMidYMid meet">
        <!-- First L shape background -->
        <g>
            <path d="M 49.5 177.339844 L 78.878906 177.339844 C 82.0625 177.339844 85.113281 178.605469 87.363281 180.855469 C 89.613281 183.105469 90.878906 186.160156 90.878906 189.339844 L 90.878906 218.71875 C 90.878906 221.902344 89.613281 224.953125 87.363281 227.203125 C 85.113281 229.453125 82.0625 230.71875 78.878906 230.71875 L 49.5 230.71875 C 46.316406 230.71875 43.265625 229.453125 41.015625 227.203125 C 38.765625 224.953125 37.5 221.902344 37.5 218.71875 L 37.5 189.339844 C 37.5 186.160156 38.765625 183.105469 41.015625 180.855469 C 43.265625 178.605469 46.316406 177.339844 49.5 177.339844 Z" fill="{logo_fill}"/>
            <!-- First L letter -->
            <path d="M 9.078125 -0.3125 C 9.078125 -0.0703125 7.71875 0.046875 5 0.046875 C 2.863281 0.015625 1.796875 -0.09375 1.796875 -0.28125 L 1.796875 -27.515625 C 1.796875 -27.921875 3.09375 -28.125 5.6875 -28.125 C 7.945312 -28.039062 9.078125 -27.90625 9.078125 -27.71875 Z" fill="{logo_text_fill}" transform="translate(58.734376, 217.841294)"/>
        </g>
        <!-- Second L shape background -->
        <g>
            <path d="M 82.5625 144.28125 L 111.9375 144.28125 C 115.121094 144.28125 118.171875 145.546875 120.425781 147.796875 C 122.675781 150.046875 123.9375 153.097656 123.9375 156.28125 L 123.9375 185.660156 C 123.9375 188.839844 122.675781 191.894531 120.425781 194.144531 C 118.171875 196.394531 115.121094 197.660156 111.9375 197.660156 L 82.5625 197.660156 C 79.378906 197.660156 76.324219 196.394531 74.074219 194.144531 C 71.824219 191.894531 70.5625 188.839844 70.5625 185.660156 L 70.5625 156.28125 C 70.5625 153.097656 71.824219 150.046875 74.074219 147.796875 C 76.324219 145.546875 79.378906 144.28125 82.5625 144.28125 Z" fill="{logo_fill}"/>
            <!-- Second L letter (b shape) -->
            <path d="M 2 -27.875 C 2 -28.195312 3.148438 -28.359375 5.453125 -28.359375 C 7.765625 -28.359375 8.921875 -28.1875 8.921875 -27.84375 L 8.921875 -20.078125 C 10.066406 -20.296875 10.878906 -20.40625 11.359375 -20.40625 C 16.960938 -20.40625 19.765625 -17.191406 19.765625 -10.765625 C 19.765625 -7.191406 18.898438 -4.4375 17.171875 -2.5 C 15.453125 -0.5625 13.015625 0.40625 9.859375 0.40625 C 6.703125 0.40625 4.082031 -0.300781 2 -1.71875 Z M 10.234375 -14.15625 C 9.785156 -14.15625 9.347656 -14.007812 8.921875 -13.71875 L 8.921875 -6.078125 C 9.296875 -5.921875 9.6875 -5.84375 10.09375 -5.84375 C 10.507812 -5.84375 10.929688 -6 11.359375 -6.3125 C 12.109375 -6.851562 12.484375 -8.097656 12.484375 -10.046875 C 12.484375 -12.785156 11.734375 -14.15625 10.234375 -14.15625 Z" fill="{logo_text_fill}" transform="translate(86.83801, 184.780711)"/>
        </g>
        <!-- "labb" text -->
        <g fill="{logo_fill}">
            <path d="M 20.4375 -0.71875 C 20.4375 -0.175781 17.375 0.09375 11.25 0.09375 C 6.445312 0.03125 4.046875 -0.207031 4.046875 -0.625 L 4.046875 -61.953125 C 4.046875 -62.847656 6.957031 -63.296875 12.78125 -63.296875 C 17.882812 -63.117188 20.4375 -62.820312 20.4375 -62.40625 Z" transform="translate(150.726163, 218.249986)"/>
            <path d="M 9.71875 -32.6875 C 8.039062 -35.6875 7.203125 -38.128906 7.203125 -40.015625 C 7.203125 -41.910156 7.710938 -43.128906 8.734375 -43.671875 C 12.160156 -45.171875 16.859375 -45.921875 22.828125 -45.921875 C 28.796875 -45.921875 33.007812 -44.523438 35.46875 -41.734375 C 37.9375 -38.941406 39.171875 -34.816406 39.171875 -29.359375 L 39.171875 -15.125 L 42.234375 -15.125 C 43.253906 -15.125 44.046875 -14.523438 44.609375 -13.328125 C 45.179688 -12.128906 45.46875 -10.476562 45.46875 -8.375 C 45.46875 -6.269531 44.941406 -4.195312 43.890625 -2.15625 C 42.847656 -0.113281 41.425781 0.90625 39.625 0.90625 C 36.382812 0.90625 33.769531 0.0351562 31.78125 -1.703125 C 30.882812 -2.429688 30.195312 -3.304688 29.71875 -4.328125 C 26.957031 -0.835938 22.664062 0.90625 16.84375 0.90625 C 12.457031 0.90625 8.765625 -0.65625 5.765625 -3.78125 C 2.765625 -6.90625 1.265625 -10.597656 1.265625 -14.859375 C 1.265625 -24.640625 7.113281 -29.53125 18.8125 -29.53125 L 23.765625 -29.53125 L 23.765625 -30.4375 C 23.765625 -32 23.507812 -33.003906 23 -33.453125 C 22.488281 -33.898438 21.304688 -34.125 19.453125 -34.125 C 17.171875 -34.125 13.925781 -33.644531 9.71875 -32.6875 Z M 16.921875 -16.125 C 16.921875 -14.800781 17.28125 -13.789062 18 -13.09375 C 18.726562 -12.40625 19.644531 -12.0625 20.75 -12.0625 C 21.863281 -12.0625 22.867188 -12.515625 23.765625 -13.421875 L 23.765625 -20.34375 L 21.25 -20.34375 C 18.363281 -20.34375 16.921875 -18.9375 16.921875 -16.125 Z" transform="translate(181.522807, 218.249986)"/>
            <path d="M 4.5 -62.765625 C 4.5 -63.484375 7.09375 -63.84375 12.28125 -63.84375 C 17.476562 -63.84375 20.078125 -63.453125 20.078125 -62.671875 L 20.078125 -45.203125 C 22.660156 -45.679688 24.492188 -45.921875 25.578125 -45.921875 C 38.179688 -45.921875 44.484375 -38.6875 44.484375 -24.21875 C 44.484375 -16.175781 42.546875 -9.976562 38.671875 -5.625 C 34.796875 -1.269531 29.300781 0.90625 22.1875 0.90625 C 15.082031 0.90625 9.1875 -0.6875 4.5 -3.875 Z M 23.046875 -31.875 C 22.023438 -31.875 21.035156 -31.546875 20.078125 -30.890625 L 20.078125 -13.6875 C 20.921875 -13.320312 21.804688 -13.140625 22.734375 -13.140625 C 23.660156 -13.140625 24.609375 -13.503906 25.578125 -14.234375 C 27.253906 -15.429688 28.09375 -18.222656 28.09375 -22.609375 C 28.09375 -28.785156 26.410156 -31.875 23.046875 -31.875 Z" transform="translate(234.380946, 218.249986)"/>
            <path d="M 4.5 -62.765625 C 4.5 -63.484375 7.09375 -63.84375 12.28125 -63.84375 C 17.476562 -63.84375 20.078125 -63.453125 20.078125 -62.671875 L 20.078125 -45.203125 C 22.660156 -45.679688 24.492188 -45.921875 25.578125 -45.921875 C 38.179688 -45.921875 44.484375 -38.6875 44.484375 -24.21875 C 44.484375 -16.175781 42.546875 -9.976562 38.671875 -5.625 C 34.796875 -1.269531 29.300781 0.90625 22.1875 0.90625 C 15.082031 0.90625 9.1875 -0.6875 4.5 -3.875 Z M 23.046875 -31.875 C 22.023438 -31.875 21.035156 -31.546875 20.078125 -30.890625 L 20.078125 -13.6875 C 20.921875 -13.320312 21.804688 -13.140625 22.734375 -13.140625 C 23.660156 -13.140625 24.609375 -13.503906 25.578125 -14.234375 C 27.253906 -15.429688 28.09375 -18.222656 28.09375 -22.609375 C 28.09375 -28.785156 26.410156 -31.875 23.046875 -31.875 Z" transform="translate(287.509224, 218.249986)"/>
        </g>
    </svg>'''


def _generate_og_image_svg_content(
    title: str,
    description: str = "",
    site_name: str = "Labb",
    component_tag: Optional[str] = None,
    doc_url: str = "labb.io",
    github_url: str = "github.com/labbhq/labb",
    width: int = 1200,
    height: int = 630,
    bg_color: str = "#ffffff",
    text_color: str = "#000000",
    accent_color: str = "#6366f1",
) -> str:
    """
    Generate the SVG content string (shared by both data URL and file save functions).
    """
    # Escape and truncate text
    title = escape_svg_text(title)[:80]
    description = escape_svg_text(description)[:150]
    component_tag = escape_svg_text(component_tag) if component_tag else None

    # Wrap text
    title_lines = wrap_text(title, 40)
    desc_lines = wrap_text(description, 70) if description else []

    # Layout positions
    logo_height = 70
    logo_width = logo_height * 3.1  # Aspect ratio from viewBox
    logo_x = width - logo_width - 80  # Right side with margin
    logo_y = 60
    title_x = 80
    title_y = 200  # Centered vertically
    title_line_height = 80

    # Component tag below title (reduced spacing)
    component_tag_y = title_y + (len(title_lines) * title_line_height) - 40
    desc_y = component_tag_y + 70
    desc_line_height = 36

    # Footer
    footer_y = height - 80
    icon_size = 24

    # Determine logo color based on background
    # Use dark logo on light background, light logo on dark background
    is_light_bg = bg_color.lower() in ["#ffffff", "#fff", "white"]
    logo_fill = "#1a1a1a" if is_light_bg else "#ffffff"
    logo_text_fill = "#ffffff" if is_light_bg else "#000000"

    # Get logo SVG content
    logo_svg = _get_logo_svg_content(logo_fill, logo_text_fill, logo_height)

    # Build SVG
    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <!-- Background -->
    <rect width="{width}" height="{height}" fill="{bg_color}"/>

    <!-- Subtle border -->
    <rect x="0" y="0" width="{width}" height="{height}" fill="none" stroke="#e5e7eb" stroke-width="2"/>

    <!-- Labb Logo -->
    <g transform="translate({logo_x}, {logo_y})">
        {logo_svg}
    </g>

    <!-- Title (Component Name) -->'''

    for i, line in enumerate(title_lines):
        y = title_y + (i * title_line_height)
        svg += f'''
    <text x="{title_x}" y="{y}" fill="{text_color}" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="72" font-weight="700" letter-spacing="-0.02em">
        {line}
    </text>'''

    # Component tag (code style)
    if component_tag:
        tag_text = f"&lt;{component_tag} /&gt;"
        svg += f'''

    <!-- Component Tag (code style) -->
    <text x="{title_x}" y="{component_tag_y}" fill="#374151" font-family="'SF Mono', 'Monaco', 'Courier New', monospace" font-size="24" font-weight="600" letter-spacing="0.02em">
        {tag_text}
    </text>'''

    # Description
    if desc_lines:
        svg += """

    <!-- Description -->"""
        for i, line in enumerate(desc_lines):
            y = desc_y + (i * desc_line_height)
            svg += f'''
    <text x="{title_x}" y="{y}" fill="#6b7280" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="28" font-weight="400">
        {line}
    </text>'''

    # Footer with proper SVG icons (centered with text)
    icon_offset_y = footer_y - (icon_size / 2) - 6

    svg += f'''

    <!-- Footer Links -->
    <!-- Globe Icon (Remix Icon) - centered with text -->
    <g transform="translate(80, {icon_offset_y})">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="{icon_size}" height="{icon_size}" fill="#9ca3af">
            <path d="M12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12C22 17.5228 17.5228 22 12 22ZM9.71002 19.6674C8.74743 17.6259 8.15732 15.3742 8.02731 13H4.06189C4.458 16.1765 6.71639 18.7747 9.71002 19.6674ZM10.0307 13C10.1811 15.4388 10.8778 17.7297 12 19.752C13.1222 17.7297 13.8189 15.4388 13.9693 13H10.0307ZM19.9381 13H15.9727C15.8427 15.3742 15.2526 17.6259 14.29 19.6674C17.2836 18.7747 19.542 16.1765 19.9381 13ZM4.06189 11H8.02731C8.15732 8.62577 8.74743 6.37407 9.71002 4.33256C6.71639 5.22533 4.458 7.8235 4.06189 11ZM10.0307 11H13.9693C13.8189 8.56122 13.1222 6.27025 12 4.24799C10.8778 6.27025 10.1811 8.56122 10.0307 11ZM14.29 4.33256C15.2526 6.37407 15.8427 8.62577 15.9727 11H19.9381C19.542 7.8235 17.2836 5.22533 14.29 4.33256Z"></path>
        </svg>
    </g>

    <!-- Doc URL (shortened) -->
    <text x="116" y="{footer_y}" fill="#6b7280" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="20" font-weight="400">
        {escape_svg_text(doc_url)}
    </text>

    <!-- GitHub Icon (Remix Icon) - centered with text -->
    <g transform="translate(280, {icon_offset_y})">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="{icon_size}" height="{icon_size}" fill="#9ca3af">
            <path d="M5.88401 18.6533C5.58404 18.4526 5.32587 18.1975 5.0239 17.8369C4.91473 17.7065 4.47283 17.1524 4.55811 17.2583C4.09533 16.6833 3.80296 16.417 3.50156 16.3089C2.9817 16.1225 2.7114 15.5499 2.89784 15.0301C3.08428 14.5102 3.65685 14.2399 4.17672 14.4263C4.92936 14.6963 5.43847 15.1611 6.12425 16.0143C6.03025 15.8974 6.46364 16.441 6.55731 16.5529C6.74784 16.7804 6.88732 16.9182 6.99629 16.9911C7.20118 17.1283 7.58451 17.1874 8.14709 17.1311C8.17065 16.7489 8.24136 16.3783 8.34919 16.0358C5.38097 15.3104 3.70116 13.3952 3.70116 9.63971C3.70116 8.40085 4.0704 7.28393 4.75917 6.3478C4.5415 5.45392 4.57433 4.37284 5.06092 3.15636C5.1725 2.87739 5.40361 2.66338 5.69031 2.57352C5.77242 2.54973 5.81791 2.53915 5.89878 2.52673C6.70167 2.40343 7.83573 2.69705 9.31449 3.62336C10.181 3.41879 11.0885 3.315 12.0012 3.315C12.9129 3.315 13.8196 3.4186 14.6854 3.62277C16.1619 2.69 17.2986 2.39649 18.1072 2.52651C18.1919 2.54013 18.2645 2.55783 18.3249 2.57766C18.6059 2.66991 18.8316 2.88179 18.9414 3.15636C19.4279 4.37256 19.4608 5.45344 19.2433 6.3472C19.9342 7.28337 20.3012 8.39208 20.3012 9.63971C20.3012 13.3968 18.627 15.3048 15.6588 16.032C15.7837 16.447 15.8496 16.9105 15.8496 17.4121C15.8496 18.0765 15.8471 18.711 15.8424 19.4225C15.8412 19.6127 15.8397 19.8159 15.8375 20.1281C16.2129 20.2109 16.5229 20.5077 16.6031 20.9089C16.7114 21.4504 16.3602 21.9773 15.8186 22.0856C14.6794 22.3134 13.8353 21.5538 13.8353 20.5611C13.8353 20.4708 13.836 20.3417 13.8375 20.1145C13.8398 19.8015 13.8412 19.599 13.8425 19.4094C13.8471 18.7019 13.8496 18.0716 13.8496 17.4121C13.8496 16.7148 13.6664 16.2602 13.4237 16.051C12.7627 15.4812 13.0977 14.3973 13.965 14.2999C16.9314 13.9666 18.3012 12.8177 18.3012 9.63971C18.3012 8.68508 17.9893 7.89571 17.3881 7.23559C17.1301 6.95233 17.0567 6.54659 17.199 6.19087C17.3647 5.77663 17.4354 5.23384 17.2941 4.57702L17.2847 4.57968C16.7928 4.71886 16.1744 5.0198 15.4261 5.5285C15.182 5.69438 14.8772 5.74401 14.5932 5.66413C13.7729 5.43343 12.8913 5.315 12.0012 5.315C11.111 5.315 10.2294 5.43343 9.40916 5.66413C9.12662 5.74359 8.82344 5.69492 8.57997 5.53101C7.8274 5.02439 7.2056 4.72379 6.71079 4.58376C6.56735 5.23696 6.63814 5.77782 6.80336 6.19087C6.94565 6.54659 6.87219 6.95233 6.61423 7.23559C6.01715 7.8912 5.70116 8.69376 5.70116 9.63971C5.70116 12.8116 7.07225 13.9683 10.023 14.2999C10.8883 14.3971 11.2246 15.4769 10.5675 16.0482C10.3751 16.2156 10.1384 16.7802 10.1384 17.4121V20.5611C10.1384 21.5474 9.30356 22.2869 8.17878 22.09C7.63476 21.9948 7.27093 21.4766 7.36613 20.9326C7.43827 20.5204 7.75331 20.2116 8.13841 20.1276V19.1381C7.22829 19.1994 6.47656 19.0498 5.88401 18.6533Z"></path>
        </svg>
    </g>

    <!-- GitHub URL (shortened) -->
    <text x="316" y="{footer_y}" fill="#6b7280" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="20" font-weight="400">
        {escape_svg_text(github_url)}
    </text>
</svg>'''

    return svg
