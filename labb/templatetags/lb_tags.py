import re
from pathlib import Path

from django import template
from django.urls import NoReverseMatch, reverse
from django.utils.safestring import mark_safe

from labb.config import load_config
from labb.django_settings import get_default_theme
from labb.shortcuts import get_labb_theme

register = template.Library()


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


@register.simple_tag
def lb_css_path():
    """
    Template tag to get the CSS output path from labb configuration.
    Usage: {% lb_css_path %}
    """
    labb_config = load_config(raise_not_found=False)

    try:
        output_path = Path(labb_config.output_file)
        # Return the path relative to static root (remove leading directories if needed)
        if str(output_path).startswith("static/"):
            return str(output_path)[7:]  # Remove 'static/' prefix
        else:
            return str(output_path)
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
