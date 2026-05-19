import json
import logging
import re
from functools import lru_cache
from pathlib import Path
from threading import local

from django import template
from django.apps import apps
from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.signals import request_finished
from django.dispatch import receiver
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.templatetags.static import static as django_static
from django.urls import NoReverseMatch, reverse
from django.utils.safestring import mark_safe

from labb.config import load_config
from labb.django_settings import get_default_theme, get_labb_setting
from labb.shortcuts import get_labb_theme

_icon_logger = logging.getLogger("labb.icons")

register = template.Library()

# ---------------------------------------------------------------------------
# Thread-local stack storage
# ---------------------------------------------------------------------------

_local = local()


def _get_stacks():
    """Get the current request's component stacks.

    Each named stack is a dict mapping ``path → mode`` where mode is either
    ``"inline"`` (file content inlined in a <script> tag) or ``"src"`` (served
    as a cacheable <script src="..."> tag via Django's static files URL).
    """
    if not hasattr(_local, "stacks"):
        _local.stacks = {}
    return _local.stacks


def _clear_stacks():
    """Clear all stacks (called at end of each request)."""
    if hasattr(_local, "stacks"):
        _local.stacks.clear()


@receiver(request_finished)
def clear_stacks_after_request(sender, **kwargs):
    """Clear stacks after each request to prevent leaking between requests."""
    _clear_stacks()


# ---------------------------------------------------------------------------
# Stack template tags
# ---------------------------------------------------------------------------


@register.simple_tag
def lb_push_stack(name, path, mode="inline"):
    """
    Register a script path to a named stack.

    mode="inline" (default) — file content is inlined in a <script> tag.
    mode="src"              — served as <script src="{% static path %}"> for
                              browser caching; use for large chart bundles.

    Duplicate paths are silently ignored; first push wins.

    Usage:
        {% lb_push_stack name="components" path="labb/js/alpine/button.js" %}
        {% lb_push_stack name="components" path="labb/js/chart/chart-core.min.js" mode="src" %}
    """
    stacks = _get_stacks()
    if name not in stacks:
        stacks[name] = {}
    if path not in stacks[name]:
        stacks[name][path] = mode
    return ""


# Static file contents don't change within a server process; cache reads so we
# don't hit disk on every request for shared helpers like lb-chart-defaults.js.
@lru_cache(maxsize=None)
def _read_static_file(path):
    static_path = finders.find(path)
    if not static_path:
        return None
    try:
        return Path(static_path).read_text(encoding="utf-8")
    except Exception:
        return None


def _make_alpine_script_tag():
    """Return a deferred Alpine script tag resolved from LABB_SETTINGS."""
    alpine_path = get_labb_setting("ALPINE_JS_PATH", "labb/js/alpine/alpine.min.js")
    if alpine_path.startswith(("http://", "https://")):
        src = alpine_path
    else:
        src = django_static(alpine_path)
    return f'<script defer src="{src}"></script>'


@register.simple_tag
def lb_alpine_script():
    """
    Emit the deferred Alpine.js script tag resolved from LABB_SETTINGS["ALPINE_JS_PATH"].

    Use this to load Alpine on pages that don't use .x components but still need Alpine.
    Usage: {% lb_alpine_script %}
    """
    return mark_safe(_make_alpine_script_tag())


@register.simple_tag
def lb_chart_deps():
    """
    Push the Chart.js bundle, DaisyUI plugin, and global defaults to the
    components stack as cacheable <script src> / inline files.

    The Chart.js URL is read from LABB_SETTINGS["CHART_JS_PATH"]; defaults to
    the bundled file shipped with labb. Override to use a CDN:

        LABB_SETTINGS = {"CHART_JS_PATH": "https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"}

    Used by the chart provider (<c-lb.chart />) and every chart sub-component
    template. Multiple charts on the same page share the same scripts
    (deduplicated by the stack).

    Usage: {% lb_chart_deps %}
    """
    chartjs_path = get_labb_setting("CHART_JS_PATH", "labb/js/chart/chart.umd.min.js")
    for path, mode in (
        (chartjs_path, "src"),
        ("labb/js/chart/lb-daisy-plugin.js", "src"),
        ("labb/js/chart/lb-chart-defaults.js", "inline"),
    ):
        lb_push_stack("components", path, mode)
    return ""


@register.simple_tag
def lb_load_stack(name, alpine_loaded=False):
    """
    Emit all scripts registered to a named stack.

    For each stack, pre-helpers defined in LABB_SETTINGS["STACK_HELPERS"] are
    inlined first.  The special token "alpine" in the helpers list is resolved
    to a ``<script defer src="...">`` tag using LABB_SETTINGS["ALPINE_JS_PATH"],
    and is always placed last so Alpine initialises after all component scripts.

    Pass alpine_loaded=True to suppress the Alpine script tag (e.g. when
    <c-lb.m.dependencies alpine /> has already emitted it).

    Emission order:
      1. Pre-helpers (inline)
      2. mode="src" paths as <script src="..."> tags (sorted)
      3. mode="inline" component paths (sorted)
      4. Deferred Alpine <script defer src="..."> (always last)

    Usage: {% lb_load_stack name="components" %}
    """
    stacks = _get_stacks()
    path_modes = stacks.get(name, {})

    if not path_modes:
        return ""

    stack_helpers_config = get_labb_setting("STACK_HELPERS", {})
    helpers = stack_helpers_config.get(name, [])

    # Split helpers: inline paths vs the special "alpine" deferred token
    inline_helpers = [h for h in helpers if h != "alpine"]
    include_alpine = "alpine" in helpers and not alpine_loaded

    helper_set = set(inline_helpers)

    # Split component paths by mode (exclude helper paths)
    src_paths = sorted(
        p for p, m in path_modes.items() if m == "src" and p not in helper_set
    )
    inline_paths = sorted(
        p for p, m in path_modes.items() if m != "src" and p not in helper_set
    )

    script_tags = []

    # 1. Inline pre-helpers (e.g. labb-component.js)
    for path in inline_helpers:
        content = _read_static_file(path)
        if content is not None:
            script_tags.append(f"<script>\n{content}\n</script>")

    # 2. src-mode paths as <script src="..."> (cacheable)
    for path in src_paths:
        if path.startswith(("http://", "https://")):
            script_tags.append(f'<script src="{path}"></script>')
        else:
            url = django_static(path)
            script_tags.append(f'<script src="{url}"></script>')

    # 3. Inline component scripts (e.g. Alpine data components)
    for path in inline_paths:
        if path.startswith(("http://", "https://")):
            script_tags.append(f'<script src="{path}"></script>')
            continue
        content = _read_static_file(path)
        if content is not None:
            script_tags.append(f"<script>\n{content}\n</script>")

    # 4. Deferred Alpine script tag (always last so it initialises after the above)
    if include_alpine:
        script_tags.append(_make_alpine_script_tag())

    return mark_safe("\n".join(script_tags))


# ---------------------------------------------------------------------------
# Alpine defaults helpers
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _load_component_variables():
    """Load and cache the component-variables.json lookup file.

    Cached for the life of the process; call ``_load_component_variables.cache_clear()``
    in tests that regenerate the JSON.
    """
    json_path = finders.find("labb/js/alpine/component-variables.json")
    if json_path:
        try:
            return json.loads(Path(json_path).read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def parse_attrs_to_dict(attrs):
    """
    Parse an HTML attributes string into a dictionary.

    Handles standard attributes, Alpine bindings (x-*, :*, @*), boolean
    attributes, and unquoted values.

    Returns:
        dict: attribute name → value (True for boolean attributes)
    """
    if not attrs:
        return {}

    attrs_str = str(attrs).strip()
    if not attrs_str:
        return {}

    # Capture the `=` explicitly so we can tell `foo` (bare) from `foo=""` (empty
    # string) without re-scanning the source string — .find() was mis-detecting
    # when the same attribute name appears more than once.
    attr_pattern = r'([@:]?[\w.-]+)(=)?(?:"([^"]*)"|\'([^\']*)\'|([^\s>]+))?'
    result = {}

    for attr_name, eq, double_quoted, single_quoted, unquoted in re.findall(
        attr_pattern, attrs_str
    ):
        attr_value = double_quoted or single_quoted or unquoted or None
        has_equals = bool(eq)

        if attr_value is None or attr_value == "":
            result[attr_name] = "" if has_equals else True
        else:
            result[attr_name] = attr_value

    return result


@register.filter
def lb_attrs_to_dict(attrs):
    """
    Convert an HTML attributes string to a dictionary.

    Usage: {{ attrs|lb_attrs_to_dict }}
    """
    return parse_attrs_to_dict(attrs)


@register.simple_tag
def lb_alpine_defaults(attrs, component_name):
    """
    Extract schema-relevant props from an attrs string as a JSON string.

    Only includes attributes that exist in the component's schema (loaded from
    component-variables.json).  Alpine bindings (:attr, @event) are skipped.

    Usage: {% lb_alpine_defaults attrs "button" %}
    """
    if not attrs or not component_name:
        return ""

    variables_map = _load_component_variables()
    component_vars = variables_map.get(component_name, {})
    if not component_vars:
        return ""

    all_attrs = parse_attrs_to_dict(attrs)
    filtered = {}

    for attr_name, attr_value in all_attrs.items():
        if attr_name.startswith(":") or attr_name.startswith("@"):
            continue
        if attr_name not in component_vars:
            continue

        var_type = component_vars[attr_name]
        if var_type == "boolean":
            if isinstance(attr_value, str) and attr_value.lower() == "false":
                filtered[attr_name] = False
            elif isinstance(attr_value, bool):
                filtered[attr_name] = attr_value
            else:
                filtered[attr_name] = True
        else:
            filtered[attr_name] = str(attr_value) if attr_value else ""

    try:
        return mark_safe(json.dumps(filtered))
    except Exception:
        return ""


@register.filter
def get_dict_item(dictionary, key):
    """
    Get an item from a dictionary, returning an empty string instead of None
    if the key is not found or the value is None.

    Usage: {{ myDict|get_dict_item:myKey }}
    """
    if dictionary is None:
        return ""

    if not isinstance(dictionary, dict):
        return ""

    value = dictionary.get(key)
    return "" if value is None else value


@register.filter
def make_range(value):
    """
    Create a range list from a number for use in template loops.

    Usage: {% for i in max|make_range %}
    """
    try:
        return range(1, int(value) + 1)
    except (ValueError, TypeError):
        return range(1, 6)


@register.filter
def is_half_rate(rate, i):
    """
    Check if rate matches i-0.5 (for half-star rating checked state).

    Usage: {% if rate|is_half_rate:i %}checked{% endif %}
    """
    try:
        return float(rate) == int(i) - 0.5
    except (ValueError, TypeError):
        return False


@register.filter
def is_whole_rate(rate, i):
    """
    Check if rate matches whole number i (for rating checked state).

    Usage: {% if rate|is_whole_rate:i %}checked{% endif %}
    """
    try:
        return float(rate) == int(i)
    except (ValueError, TypeError):
        return False


@register.filter
def remove_l_attrs(attrs):
    """
    Remove all attributes starting with 'l:' from an HTML attributes string.

    This filter is used to clean up attrs before rendering, removing labb-specific
    attributes (l:*) that are used for URL resolution but shouldn't appear in the final HTML.

    Usage: {{ attrs|remove_l_attrs }}

    Args:
        attrs (str): HTML attributes string

    Returns:
        str: Attributes string with l:* attributes removed
    """
    if not attrs:
        return ""

    # Convert to string in case it's not already
    attrs_str = str(attrs)

    # Pattern to match l:attrname="value" or l:attrname='value'
    pattern = r'\s*l:\w+=["\'][^"\']*["\']'
    cleaned = re.sub(pattern, "", attrs_str)
    # Clean up any extra whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return mark_safe(cleaned)


@register.simple_tag
def parse_icon(attrs=""):
    """
    Parse icon dot-notation attributes from a cotton attrs string.

    Supports:
        icon="name"              → icon name, line style, start position
        icon.fill="name"         → icon name, fill style
        icon.end="name"          → icon name, end position
        icon.fill.end="name"     → icon name, fill style, end position
        icon.end.fill="name"     → icon name, fill style, end position
        icon.class="classes"     → additional CSS classes for the icon

    Usage:
        {% parse_icon attrs as i %}
        {{ i.name }}  {{ i.fill }}  {{ i.end }}  {{ i.css_class }}

    Returns:
        dict with keys: name (str), fill (bool), end (bool), css_class (str)
    """
    result = {
        "name": "",
        "fill": False,
        "end": False,
        "css_class": "",
    }

    if not attrs:
        return result

    s = str(attrs)

    # Extract icon.class="..."
    class_match = re.search(r'\bicon\.class=["\']([^"\']*)["\']', s)
    if class_match:
        result["css_class"] = class_match.group(1)

    # Extract the main icon attribute: icon[.fill][.end]="name"
    # Matches: icon="x", icon.fill="x", icon.end="x", icon.fill.end="x", icon.end.fill="x"
    # Does NOT match icon.class="x" because .class is not .fill or .end
    main_match = re.search(r'\bicon((?:\.(?:fill|end))*)\s*=["\']([^"\']*)["\']', s)
    if main_match:
        modifiers = main_match.group(1) or ""
        result["name"] = main_match.group(2)
        result["fill"] = ".fill" in modifiers
        result["end"] = ".end" in modifiers

    return result


@register.filter
def strip_icon_attrs(attrs):
    """
    Remove all icon-related attributes from an attrs string.

    Removes attributes matching: icon="...", icon.fill="...", icon.class="...", etc.

    Usage: {{ attrs|strip_icon_attrs }}
    """
    if not attrs:
        return ""

    s = str(attrs)

    # Remove icon attributes with values: icon="...", icon.fill="...", icon.class="...", etc.
    s = re.sub(r'\s*\bicon(?:\.[\w.]+)?\s*=["\'][^"\']*["\']', "", s)

    # Clean up whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return mark_safe(s)


@register.filter
def lb_icon_exists(name):
    """
    Return True if the named labbicons icon template exists and labbicons is installed.

    Returns False (with a warning logged) when:
    - name is empty or falsy
    - labbicons is not in INSTALLED_APPS
    - the icon template does not exist

    Usage: {% if i.name|lb_icon_exists %}
    """
    if not name:
        return False

    cotton_dir = getattr(settings, "COTTON_DIR", "cotton")
    # Match cotton's path resolution: dots → slashes, hyphens → underscores (when COTTON_SNAKE_CASED_NAMES is True)
    icon_tpl_path = str(name).replace(".", "/")
    if getattr(settings, "COTTON_SNAKE_CASED_NAMES", True):
        icon_tpl_path = icon_tpl_path.replace("-", "_")
    icon_path = f"{cotton_dir}/lbi/{icon_tpl_path}.html"

    try:
        get_template(icon_path)
        return True
    except TemplateDoesNotExist:
        if not apps.is_installed("labbicons"):
            _icon_logger.warning(
                'Icon "%s" requested but labbicons is not installed. '
                'Install labbicons and add "labbicons" to '
                "INSTALLED_APPS to use icons.",
                name,
            )
        else:
            _icon_logger.warning(
                'Icon "%s" not found in labbicons. Check the icon name is correct.',
                name,
            )
        return False


@register.simple_tag
def lb_css_path():
    """
    Template tag to get the CSS output path from labb configuration.
    Usage: {% lb_css_path %}
    """
    labb_config = load_config(raise_not_found=False)

    try:
        # Stay POSIX — this string is emitted into an HTML href, not a filesystem path.
        output_path = labb_config.output_file.replace("\\", "/")
        if not output_path:
            return "."
        output_path = output_path.rstrip("/") or "static"
        if output_path.startswith("static/"):
            return output_path[7:]
        return output_path
    except Exception:
        return "css/output.css"


@register.simple_tag(takes_context=True)
def labb_theme(context):
    """
    Get the current theme from the request session and return as data-theme attribute.

    Usage:
        {% labb_theme as theme_attr %}
        <html {{ theme_attr }}>
    """
    request = context.get("request")
    if request:
        theme = get_labb_theme(request)
    else:
        # Get default theme from Django settings
        theme = get_default_theme()

    # Return empty string for __system__ theme (no data-theme attribute)
    if theme == "__system__" or not theme:
        return ""

    # Return data-theme attribute with theme value
    return f'data-theme="{theme}"'


@register.simple_tag(takes_context=True)
def labb_theme_val(context):
    """
    Get the current theme value from the request session.

    Usage:
        {% labb_theme_val as theme_value %}
        <span>{{ theme_value }}</span>
    """
    request = context.get("request")
    if request:
        return get_labb_theme(request)

    # Get default theme from Django settings
    return get_default_theme()


@register.simple_tag
def resolve_labb_link(viewname, attrs=""):
    """
    Resolve a Django view name to a URL, extracting l: prefixed attributes from attrs.

    Parses the attrs string to find attributes starting with 'l:' and uses them
    as keyword arguments for Django's reverse() function.

    Args:
        viewname (str): Django view name (e.g., 'blog:post')
        attrs (str): HTML attributes string (e.g., 'l:id="1" l:author="sample" class="link"')

    Returns:
        str: Resolved URL or empty string if viewname is not provided

    Usage:
        {% resolve_labb_link "blog:post" attrs as resolved_url %}
        or
        {% resolve_labb_link "blog:post" 'l:id="1" l:author="sample"' %}
    """
    if not viewname:
        return ""

    # Handle None or empty attrs
    if not attrs:
        attrs = ""

    # Parse attrs string to extract l: prefixed attributes
    # Pattern matches: l:attrname="value" or l:attrname='value'
    pattern = r'l:(\w+)=["\']([^"\']+)["\']'
    matches = re.findall(pattern, str(attrs))

    # Build kwargs dictionary from matches
    kwargs = {}
    for attr_name, attr_value in matches:
        kwargs[attr_name] = attr_value

    try:
        # Use reverse() to resolve the view name with kwargs
        if kwargs:
            return reverse(viewname, kwargs=kwargs)
        else:
            return reverse(viewname)
    except NoReverseMatch:
        # Return empty string if view name cannot be resolved
        return ""
