import hashlib
import re
from pathlib import Path

import frontmatter
import markdown
import yaml
from django.conf import settings
from django.utils.text import slugify

from .seo_utils import generate_and_save_og_image_svg

BASE_DIR = Path(__file__).resolve().parent.parent

CONTENT_BASE_PATH = BASE_DIR / "labbdocs" / "content"


_yaml_cache = {}


def resolve_file_path_to_url(file_path, url_prefix=""):
    """
    Convert a markdown file path to its corresponding URL path.

    Args:
        file_path (str): Relative path to the markdown file (e.g., "1_getting_started/2_installation.md")
        url_prefix (str): URL prefix to prepend (default: "")

    Returns:
        str: URL path (e.g., "/getting-started/installation/")
    """
    try:
        # Convert string path to Path object
        path_obj = Path(file_path)

        # Convert to URL segments
        segments = []
        for part in path_obj.parts:
            # Remove file extension
            if part.endswith(".md"):
                part = part[:-3]

            # Remove number prefixes and convert to URL format
            if "_" in part and part.split("_")[0].isdigit():
                part = "_".join(part.split("_")[1:])

            # Convert to lowercase and replace underscores with hyphens
            part = part.lower().replace("_", "-")
            segments.append(part)

        # Create URL path with prefix and trailing slash
        base_path = "/" + "/".join(segments) + "/"
        url_prefix = url_prefix.rstrip("/") if url_prefix else ""

        if url_prefix:
            return url_prefix + base_path
        return base_path

    except Exception:
        # todo: capture this error in sentry
        # Return a fallback URL on error
        return f"#error-resolving-{file_path}"


class DocParser:
    def __init__(
        self,
        name,
        content_path,
        build_path,
        template_dir,
        url_prefix="",
        yaml_output_path=None,
        seo_config=None,
    ):
        """
        Initialize the DocParser with a path to a folder.

        Args:
            name (str): Name of the documentation
            content_path (str): Path to the folder to process
            build_path (str): Build path for generated HTML files
            url_prefix (str): URL prefix to prepend to generated paths (e.g., "/docs", "/ui")
            yaml_output_path (str, optional): Path for docs.yaml output. If not provided, uses current working directory
            seo_config (dict, optional): SEO configuration from settings
        """
        self.name = name
        self.content_path = Path(content_path)
        self.url_prefix = url_prefix.rstrip("/") if url_prefix else ""
        self.seo_config = seo_config or {}

        # Set YAML output path - default to current working directory if not specified
        if yaml_output_path:
            self.docs_yaml_path = Path(yaml_output_path)
        else:
            self.docs_yaml_path = Path.cwd() / "docs.yaml"

        self.build_path = Path(build_path)
        self.template_dir = Path(template_dir)

    def _process_markdown_file(self, md_file_path):
        """
        Process markdown file to generate HTML content, TOC data, and extract frontmatter.
        Consolidates all markdown processing into a single operation.

        Args:
            md_file_path (Path): Path to the markdown file

        Returns:
            tuple: (html_content, toc_data, frontmatter_data)
        """

        # Read and parse the markdown file with frontmatter (single read)
        with open(md_file_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        # Extract frontmatter and content
        frontmatter_data = post.metadata
        raw_content = post.content

        # Convert markdown to HTML with TOC extension (single instance)
        md = markdown.Markdown(extensions=["tables", "fenced_code", "toc"])
        html_content = md.convert(raw_content)

        # Make headings clickable with anchor links
        def make_headings_clickable(html):
            # Pattern to match headings and make them clickable
            def replace_heading(match):
                tag = match.group(1)  # h1, h2, h3, etc.
                attrs = match.group(2)  # existing attributes
                content = match.group(3)  # heading content

                # Extract existing ID from attributes (markdown parser always generates IDs)
                id_match = re.search(r'id="([^"]*)"', attrs)
                heading_id = id_match.group(1)

                # Make the entire heading clickable, preserving existing attributes
                return f'<{tag}{attrs}><a href="#{heading_id}">{content}</a></{tag}>'

            # Apply to all headings
            html = re.sub(
                r"<(h[1-6])([^>]*)>(.*?)</\1>",
                replace_heading,
                html,
                flags=re.DOTALL,
            )
            return html

        html_content = make_headings_clickable(html_content)

        # Post-processing to protect Cotton components and Django template tags
        def protect_components(html):
            # Define common patterns
            cotton_tag = r"(?:c-lb\.[^>]*|c-lbdocs\.[^>]*)"
            django_tag = r"{% [^}]* %}"

            # Remove paragraph tags around Django template tags (general case)
            html = re.sub(rf"<p>({django_tag})</p>", r"\1", html)
            html = re.sub(rf"<p>({django_tag})", r"\1", html)
            html = re.sub(rf"({django_tag})</p>", r"\1", html)

            # Remove paragraph tags around Cotton component tags
            html = re.sub(rf"<p>(<{cotton_tag}>)", r"\1", html)
            html = re.sub(rf"(</{cotton_tag}>)</p>", r"\1", html)
            html = re.sub(rf"<p>(<{cotton_tag}/>)</p>", r"\1", html)

            # Remove orphaned paragraph tags near Cotton components
            html = re.sub(rf"(<{cotton_tag}>)\s*</p>", r"\1", html)
            html = re.sub(rf"<p>\s*(</{cotton_tag}>)", r"\1", html)

            # Remove paragraph tags around Django tags inside Cotton components
            html = re.sub(rf"(<{cotton_tag}>)\s*<p>({django_tag})</p>", r"\1\2", html)
            html = re.sub(rf"<p>({django_tag})</p>\s*(</{cotton_tag}>)", r"\1\2", html)

            return html

        html_content = protect_components(html_content)

        # Optimize TOC data to only include fields used in template
        def optimize_toc_item(item):
            """Extract only the fields needed by the template."""
            optimized = {
                "name": item.get("name", ""),
                "id": item.get("id", ""),  # Use original ID from markdown parser
                "level": item.get("level", 1),
            }

            # Recursively optimize children
            if item.get("children"):
                optimized["children"] = [
                    optimize_toc_item(child) for child in item["children"]
                ]
            else:
                optimized["children"] = []

            return optimized

        # Optimize the TOC tokens (preserving original IDs from markdown parser)
        optimized_toc = [optimize_toc_item(item) for item in md.toc_tokens]

        return html_content, optimized_toc, frontmatter_data

    def _save_html_to_build_folder(self, html_content, template_path):
        """
        Save HTML content to build folder as template file.

        Args:
            html_content (str): HTML content to save
            template_path (Path): Path where to save the template file
        """
        # Ensure the directory exists
        template_path.parent.mkdir(parents=True, exist_ok=True)

        # Save the HTML content
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    def _build_seo_metadata(self, frontmatter_data, url_path):
        """
        Pre-compute SEO metadata during parsing.

        Args:
            frontmatter_data (dict): Frontmatter data from markdown
            url_path (str): URL path for the page

        Returns:
            dict: Pre-computed SEO metadata
        """

        # Get title
        title = frontmatter_data.get("title", "")
        component = frontmatter_data.get("component", "")
        meta_title = title or component or "Documentation"

        # Build page title with site name
        site_name = self.seo_config.get("site_name", "Labb")
        page_title = f"{meta_title} | {site_name}"

        # Get description
        description = frontmatter_data.get(
            "description", f"Documentation for {meta_title}"
        )

        # Get keywords
        keywords = frontmatter_data.get("keywords", [])
        if isinstance(keywords, list):
            keywords_str = ", ".join(keywords) if keywords else None
        else:
            keywords_str = keywords or None

        # Handle OG image - generate at build time if needed
        og_image = frontmatter_data.get("og_image")

        # If no custom image and auto-generation is enabled, generate and save PNG
        if not og_image and self.seo_config.get("auto_generate_og_images", True):
            # Get OG image configuration
            og_image_config = self.seo_config.get("og_image", {})
            base_storage_path = og_image_config.get("storage_path")
            base_static_url_prefix = og_image_config.get(
                "static_url_prefix", "/static/labbdocs/ograph"
            )

            if base_storage_path:
                # Add doc type as subdirectory to storage path and URL prefix
                doc_type = self.name  # e.g., "ui", "icons"
                storage_path = Path(base_storage_path) / doc_type
                static_url_prefix = f"{base_static_url_prefix.rstrip('/')}/{doc_type}"

                # Generate filename with title prefix and URL hash (no doc type in filename)
                title_slug = slugify(meta_title) if meta_title else ""
                # Limit length to keep filenames manageable
                if title_slug and len(title_slug) > 30:
                    title_slug = title_slug[:30].rstrip("-")

                url_hash = hashlib.md5(url_path.encode()).hexdigest()[:12]

                # Build filename: {title-slug}-{hash}.png
                if title_slug:
                    filename = f"{title_slug}-{url_hash}.png"
                else:
                    filename = f"{url_hash}.png"

                # Build full path to save the file
                output_path = storage_path / filename

                og_style = self.seo_config.get("og_image_style", {})
                # Get component tag for display in OG image
                component_tag = frontmatter_data.get("component", "")

                # Generate and save PNG to file
                og_image = generate_and_save_og_image_svg(
                    title=meta_title,
                    output_path=output_path,
                    static_url_prefix=static_url_prefix,
                    description=description,
                    site_name=site_name,
                    component_tag=component_tag if component_tag else None,
                    **og_style,
                )

        # Build SEO data
        seo_data = {
            "title": page_title,
            "meta_title": meta_title,
            "description": description,
            "keywords": keywords_str,
            "canonical_url": url_path,  # Will be made absolute at runtime
            "robots": frontmatter_data.get("robots", "index, follow"),
            "author": frontmatter_data.get(
                "author", self.seo_config.get("default_author", "Labb Team")
            ),
            # Open Graph
            "og_type": frontmatter_data.get("og_type", "article"),
            "og_image": og_image,
            "published_time": frontmatter_data.get("published_time"),
            "modified_time": frontmatter_data.get("modified_time"),
            # Twitter
            "twitter_card": frontmatter_data.get("twitter_card", "summary_large_image"),
            "twitter_creator": frontmatter_data.get("twitter_creator"),
            # Sitemap
            "sitemap_priority": frontmatter_data.get("sitemap_priority", "0.8"),
            "sitemap_changefreq": frontmatter_data.get("sitemap_changefreq", "weekly"),
            # Component tags for structured data
            "tags": self._get_component_tags(frontmatter_data),
        }

        return seo_data

    def _get_component_tags(self, frontmatter_data):
        """Get component-related tags for structured data."""
        tags = []
        if component := frontmatter_data.get("component"):
            tags.append(component)
        if daisy_ui := frontmatter_data.get("daisy_ui_component_name"):
            tags.append(daisy_ui)
        tags.extend(frontmatter_data.get("tags", []))
        return tags

    def _build_navigation_data(self, menu):
        """
        Build navigation data for all pages by flattening menu structure.

        Args:
            menu (list): Menu structure from create_menu_structure

        Returns:
            dict: Navigation mapping with prev/next for each page path
        """
        # Flatten menu to get ordered list of pages
        page_order = []

        def extract_pages(menu_items):
            """Recursively extract pages from menu structure."""
            for item in menu_items:
                if item.get("path"):
                    # This is a page
                    page_order.append({"path": item["path"], "title": item["title"]})
                elif item.get("children"):
                    # This is a section with children
                    extract_pages(item["children"])

        extract_pages(menu)

        # Build navigation mapping
        navigation_data = {}
        for i, page in enumerate(page_order):
            prev_page = page_order[i - 1] if i > 0 else None
            next_page = page_order[i + 1] if i < len(page_order) - 1 else None

            navigation_data[page["path"]] = {"prev": prev_page, "next": next_page}

        return navigation_data

    def create_menu_structure(self):
        """
        Create a menu tree structure of folders and files in the directory.

        Returns:
            dict: Menu structure representation with paths
        """
        pages = {}

        def format_title(name):
            """Convert file/folder name to readable title."""
            # Remove file extension
            if name.endswith(".md"):
                name = name[:-3]

            # Remove number prefixes (e.g., "1_", "2_")
            if "_" in name and name.split("_")[0].isdigit():
                name = "_".join(name.split("_")[1:])

            # Convert underscores to spaces and title case
            return name.replace("_", " ").title()

        def create_url_path(file_path):
            """Convert file path to URL path."""
            # Get relative path from base
            relative_path = file_path.relative_to(self.content_path)
            # Use the extracted function
            return resolve_file_path_to_url(str(relative_path), self.url_prefix)

        def build_menu(current_path):
            menu_items = []

            if not current_path.exists():
                return menu_items

            for item in sorted(current_path.iterdir()):
                if item.is_dir():
                    children = build_menu(item)
                    menu_item = {"title": format_title(item.name)}
                    if children:
                        menu_item["children"] = children
                    menu_items.append(menu_item)
                elif item.is_file() and item.suffix == ".md":
                    url_path = create_url_path(item)

                    # Process markdown file to get HTML, TOC, and frontmatter in one operation
                    html_content, toc_data, frontmatter_data = (
                        self._process_markdown_file(item)
                    )

                    # Create template path relative to build folder
                    relative_path = item.relative_to(self.content_path)
                    template_name = str(relative_path).replace(".md", ".html")
                    template_path = self.build_path / template_name

                    # Save HTML to build folder
                    self._save_html_to_build_folder(html_content, template_path)

                    # Pre-compute SEO metadata
                    seo_data = self._build_seo_metadata(frontmatter_data, url_path)

                    # Store file path, template path, TOC tokens, frontmatter, and SEO in pages mapping
                    pages[url_path] = {
                        "file_path": str(item.relative_to(self.content_path)),
                        "template_path": str(self.template_dir / template_name),
                        "toc": toc_data,
                        "frontmatter": frontmatter_data,
                        "seo": seo_data,  # Pre-computed SEO metadata
                    }

                    # Skip index.md from menu and navigation
                    if item.name == "index.md":
                        continue

                    # Try to get title from frontmatter (already extracted), fall back to filename
                    frontmatter_title = frontmatter_data.get("title")
                    title = (
                        frontmatter_title
                        if frontmatter_title
                        else format_title(item.name)
                    )

                    menu_items.append({"title": title, "path": url_path})

            return menu_items

        menu = build_menu(self.content_path)

        # Build navigation data for all pages
        navigation_data = self._build_navigation_data(menu)

        return {
            "menu": menu,
            "pages": pages,
            "navigation": navigation_data,
            "doc_name": self.name,
        }

    def _clear_build_directory(self):
        """Clear the build directory before generating new docs."""
        try:
            if self.build_path.exists():
                import shutil

                shutil.rmtree(self.build_path)
                print(f"🧹 Cleared build directory: {self.build_path}")
        except Exception as e:
            print(f"Warning: Could not clear build directory {self.build_path}: {e}")

    def _clear_og_image_directory(self):
        """Clear the OG image directory for this doc type before generating new images."""
        og_image_config = self.seo_config.get("og_image", {})
        clear_before_build = og_image_config.get("clear_before_build", True)

        if not clear_before_build:
            return

        base_storage_path = og_image_config.get("storage_path")
        if not base_storage_path:
            return

        # Clear only the doc type's subdirectory, not the entire folder
        doc_type = self.name
        storage_path = Path(base_storage_path) / doc_type

        try:
            if storage_path.exists() and storage_path.is_dir():
                import shutil

                # Remove all files in the doc type's directory
                for file_path in storage_path.iterdir():
                    if file_path.is_file():
                        file_path.unlink()
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)

                print(f"🧹 Cleared OG image directory for {doc_type}: {storage_path}")
        except Exception as e:
            print(f"Warning: Could not clear OG image directory {storage_path}: {e}")

    def save_to_yaml(self):
        """
        Save the menu structure to docs.yaml file.
        """
        # Clear the build directory first
        self._clear_build_directory()

        # Clear OG image directory if configured
        self._clear_og_image_directory()

        menu_structure = self.create_menu_structure()

        with open(self.docs_yaml_path, "w") as f:
            yaml.dump(menu_structure, f, default_flow_style=False, indent=2)

        print(f"Menu structure saved to {self.docs_yaml_path}")


class DocRender:
    def __init__(self, yaml_file_path):
        """
        Initialize the DocRender with a path to a docs.yaml file.

        Args:
            yaml_file_path (str): Full path to the docs.yaml file
        """
        self.docs_yaml_path = Path(yaml_file_path)
        self.docs_data = self._load_docs_yaml()

    @staticmethod
    def _is_cache_enabled():
        """
        Check if YAML caching is enabled via Django settings.

        Returns:
            bool: True if caching is enabled, False otherwise
        """
        labb_docs = getattr(settings, "LABB_DOCS", {})
        return labb_docs.get("cache_yaml", True)

    @staticmethod
    def clear_cache(file_path=None):
        """
        Clear the YAML cache for a specific file or all files.

        Args:
            file_path (str, optional): Path to clear from cache. If None, clears all.
        """
        global _yaml_cache
        if file_path:
            file_path_str = str(Path(file_path).resolve())
            _yaml_cache.pop(file_path_str, None)
        else:
            _yaml_cache.clear()

    def _load_docs_yaml(self):
        """
        Load the docs.yaml file with optional caching.

        Returns:
            dict: Parsed docs.yaml data
        """
        # Check if file exists
        if not self.docs_yaml_path.exists():
            raise FileNotFoundError(f"YAML file not found: {self.docs_yaml_path}")

        file_path_str = str(self.docs_yaml_path.resolve())
        cache_enabled = self._is_cache_enabled()

        # Get modification time (needed for both cache check and cache update)
        current_mtime = self.docs_yaml_path.stat().st_mtime

        if cache_enabled:
            # Check cache
            if file_path_str in _yaml_cache:
                cached_mtime, cached_data = _yaml_cache[file_path_str]
                # If file hasn't changed, return cached data
                if cached_mtime == current_mtime:
                    return cached_data

        # Load from file (cache miss or cache disabled)
        with open(self.docs_yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Update cache if enabled
        if cache_enabled:
            _yaml_cache[file_path_str] = (current_mtime, data)

        return data

    def get_doc_info(self, url_path):
        """
        Get document information without rendering the template.

        Args:
            url_path (str): URL path (e.g., "/docs/ui/getting-started/introduction/")
        Returns:
            dict: Object containing template_path, toc, frontmatter, metadata, and doc_layout
        """

        # Helper function to create standardized response
        def create_response(error=None, template_loaded=False):
            """Create standardized response dictionary."""
            response = {
                "template_path": "",
                "toc": [],
                "frontmatter": {},
                "file_path": "",
                "url_path": url_path,
                "doc_layout": "base",
                "navigation": {"prev": None, "next": None},
                "seo": {},  # Pre-computed SEO metadata
                "error": error,
            }

            # Populate with actual data if template loads successfully
            if template_loaded and url_path in self.docs_data.get("pages", {}):
                path_info = self.docs_data["pages"][url_path]
                file_relative_path = path_info["file_path"]
                # Use content_path from YAML
                content_path = CONTENT_BASE_PATH / self.docs_data["doc_name"]
                file_path = Path(content_path) / file_relative_path
                doc_layout = (
                    path_info.get("frontmatter", {}).get("doc_layout") or "base"
                )
                navigation = self.docs_data.get("navigation", {}).get(
                    url_path, {"prev": None, "next": None}
                )

                response.update(
                    {
                        "template_path": path_info["template_path"],
                        "toc": path_info["toc"],
                        "frontmatter": path_info["frontmatter"],
                        "file_path": str(file_path),
                        "doc_layout": doc_layout,
                        "navigation": navigation,
                        "seo": path_info.get(
                            "seo", {}
                        ),  # Include pre-computed SEO data
                    }
                )

            return response

        # Check if path exists in pages
        if url_path not in self.docs_data.get("pages", {}):
            return create_response(error="Document not found")

        return create_response(template_loaded=True)
