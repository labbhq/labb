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
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from labb.config import load_config
from labb.django_settings import get_default_theme, get_labb_setting
from labb.shortcuts import get_labb_theme

_icon_logger = logging.getLogger("labb.icons")

register = template.Library()

# ---------------------------------------------------------------------------
# Compiled regex patterns
# ---------------------------------------------------------------------------

# Parses HTML attribute strings: name, optional =, optional quoted/unquoted value.
_ATTRS_RE = re.compile(
    r'([@:]?[\w.:-]+)(=)?(?:"([^"]*)"|\'([^\']*)\'|([^\s>]+))?'
)
# Matches icon dot-notation attr names (icon, icon.fill, icon.class, etc.).
_ICON_ATTR_RE = re.compile(r"^icon(?:\.[\w.]+)?$")
# Matches l:name="value" or l:name='value' in serialised attr strings.
_L_ATTR_RE = re.compile(r'l:(\w+)=["\']([^"\']*)["\']')
# Strips l:* attrs from a serialised attr string.
_L_ATTR_STRIP_RE = re.compile(r'\s*l:\w+=["\'][^"\']*["\']')
# Strips icon* attrs from a serialised attr string (used by remove_l_attrs input).
_ICON_ATTR_STRIP_RE = re.compile(r'\s*\bicon(?:\.[\w.]+)?\s*=["\'][^"\']*["\']')
# Collapses runs of whitespace.
_WHITESPACE_RE = re.compile(r"\s+")

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
        {% lb_push_stack name="components" path="labb/js/vendor/datastar.js" mode="module" %}
        {% lb_push_stack name="components" path="labb/js/vendor/chart.umd.min.js" mode="src" %}
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
    chartjs_path = get_labb_setting("CHART_JS_PATH", "labb/js/vendor/chart.umd.min.js")
    for path, mode in (
        (chartjs_path, "src"),
        ("labb/js/chart/lb-daisy-plugin.js", "src"),
        ("labb/js/chart/lb-chart-defaults.js", "inline"),
    ):
        lb_push_stack("components", path, mode)
    return ""


@register.simple_tag
def lb_stack_has(name, path):
    """True if `path` is registered in the named stack.

    Lets a head component detect a body-pushed dependency (children render first),
    e.g. gating the CSRF helper on the reactive bundle actually being loaded.
    """
    return path in _get_stacks().get(name, {})


@register.simple_tag
def lb_load_stack(name):
    """
    Emit all scripts registered to a named stack.

    Pre-helpers defined in LABB_SETTINGS["STACK_HELPERS"][name] are inlined first,
    then src/module paths as cacheable <script> tags, then inline paths.

    Emission order:
      1. Pre-helpers (inline)
      2. mode="src" / mode="module" paths as <script> tags (sorted)
      3. mode="inline" paths (sorted)

    Usage: {% lb_load_stack name="components" %}
    """
    stacks = _get_stacks()
    path_modes = stacks.get(name, {})

    if not path_modes:
        return ""

    stack_helpers_config = get_labb_setting("STACK_HELPERS", {})
    inline_helpers = stack_helpers_config.get(name, [])
    helper_set = set(inline_helpers)

    src_paths = sorted(
        p for p, m in path_modes.items() if m in ("src", "module") and p not in helper_set
    )
    inline_paths = sorted(
        p for p, m in path_modes.items() if m not in ("src", "module") and p not in helper_set
    )

    script_tags = []

    for path in inline_helpers:
        content = _read_static_file(path)
        if content is not None:
            script_tags.append(f"<script>\n{content}\n</script>")

    for path in src_paths:
        mode = path_modes[path]
        type_attr = ' type="module"' if mode == "module" else ""
        if path.startswith(("http://", "https://")):
            script_tags.append(f'<script{type_attr} src="{path}"></script>')
        else:
            url = django_static(path)
            script_tags.append(f'<script{type_attr} src="{url}"></script>')

    for path in inline_paths:
        if path.startswith(("http://", "https://")):
            script_tags.append(f'<script src="{path}"></script>')
            continue
        content = _read_static_file(path)
        if content is not None:
            script_tags.append(f"<script>\n{content}\n</script>")

    return mark_safe("\n".join(script_tags))


def parse_attrs_to_dict(attrs):
    """
    Parse an HTML attributes string into a dictionary.

    Handles standard attributes, Cotton bindings (:, ::), Datastar bindings (@*, data-*), boolean
    attributes, and unquoted values.

    Returns:
        dict: attribute name → value (True for boolean attributes)
    """
    if not attrs:
        return {}

    attrs_str = str(attrs).strip()
    if not attrs_str:
        return {}

    result = {}

    for attr_name, eq, double_quoted, single_quoted, unquoted in _ATTRS_RE.findall(attrs_str):
        attr_value = double_quoted or single_quoted or unquoted or None
        has_equals = bool(eq)

        if attr_value is None or attr_value == "":
            result[attr_name] = "" if has_equals else True
        else:
            result[attr_name] = attr_value

    return result


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
    """Remove l:* attributes from a serialised HTML attribute string."""
    if not attrs:
        return ""
    cleaned = _L_ATTR_STRIP_RE.sub("", str(attrs))
    return mark_safe(_WHITESPACE_RE.sub(" ", cleaned).strip())


@register.simple_tag
def parse_icon(attrs=""):
    """Parse icon dot-notation keys from a Cotton Attrs mapping or attrs string.

    Supports icon, icon.fill, icon.end, icon.fill.end, icon.end.fill, icon.class.
    Returns dict: name, fill (bool), end (bool), css_class.
    """
    result = {"name": "", "fill": False, "end": False, "css_class": ""}
    if not attrs:
        return result
    if hasattr(attrs, "attrs_dict"):
        attrs = attrs.attrs_dict()
    elif not hasattr(attrs, "get"):
        attrs = parse_attrs_to_dict(str(attrs))
    result["css_class"] = str(attrs.get("icon.class") or "")
    for key in ("icon.fill.end", "icon.end.fill"):
        if key in attrs:
            result.update(name=str(attrs[key]), fill=True, end=True)
            return result
    if "icon.fill" in attrs:
        result.update(name=str(attrs["icon.fill"]), fill=True)
        return result
    if "icon.end" in attrs:
        result.update(name=str(attrs["icon.end"]), end=True)
        return result
    val = attrs.get("icon")
    if val and val is not True:
        result["name"] = str(val)
    return result


@register.filter
def strip_icon_attrs(attrs):
    """Return Cotton attrs as an HTML string, omitting icon* keys."""
    if not attrs:
        return ""
    from django.utils.html import escape as _escape
    if hasattr(attrs, "attrs_dict"):
        attrs_map = attrs.attrs_dict()
    elif hasattr(attrs, "items"):
        attrs_map = attrs
    else:
        attrs_map = parse_attrs_to_dict(str(attrs))
    parts = []
    for k, v in attrs_map.items():
        if _ICON_ATTR_RE.match(k):
            continue
        if v is True:
            parts.append(k)
        else:
            parts.append(f'{k}="{_escape(str(v))}"')
    return mark_safe(" ".join(parts))


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
            msg = (
                f'Icon "{name}" requested but labbicons is not installed. '
                'Add "labbicons" to INSTALLED_APPS to use icons.'
            )
        else:
            msg = (
                f'Icon "{name}" not found in labbicons. Check the icon name is correct.'
            )

        if settings.DEBUG:
            raise ValueError(msg) from None

        _icon_logger.warning(msg)
        return False


@register.simple_tag
def lb_css_path():
    """
    Template tag to get the CSS output path from labb configuration.
    Usage: {% lb_css_path %}
    """
    labb_config = load_config(raise_not_found=False, warn=False)

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
        theme = get_default_theme()

    if theme == "__system__" or not theme:
        return ""

    # format_html, not an f-string: a plain str is autoescaped into
    # data-theme=&quot;x&quot;, whose attribute value carries literal quotes and
    # never matches [data-theme="x"]. The theme is unvalidated session input, so
    # it must still be escaped — format_html marks up the quotes and escapes the
    # value.
    return format_html('data-theme="{}"', theme)


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
    """Resolve a Django view name to a URL using l:* keys from Cotton attrs for kwargs."""
    if not viewname:
        return ""
    kwargs = {}
    if hasattr(attrs, "items"):
        kwargs = {k[2:]: str(v) for k, v in attrs.items() if k.startswith("l:")}
    elif attrs:
        kwargs = {k: v for k, v in _L_ATTR_RE.findall(str(attrs)) if v}
    try:
        return reverse(viewname, kwargs=kwargs) if kwargs else reverse(viewname)
    except NoReverseMatch:
        return ""


