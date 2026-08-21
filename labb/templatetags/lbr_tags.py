import html as _html
import json
import re

from django import template
from django.urls import NoReverseMatch, reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe

from labb.django_settings import get_reactivity_setting
from labb.templatetags.lb_tags import _ICON_ATTR_RE, lb_push_stack, parse_attrs_to_dict

register = template.Library()


@register.simple_tag
def lbr_resolve_url(to, kwargs_json="", pk=""):
    """Resolve a URL from the ``to`` prop.

    to: a Django URL name (e.g. "todos:detail") or a direct URL (e.g. "/todos/1/").
        Detected by a leading "/" or "http" prefix — everything else is passed to reverse().
    kwargs_json: URL kwargs as a JSON string '{"pk": 1}' or a Python dict from context.
    pk: shorthand — sets {"pk": pk} when kwargs does not already contain "pk".
    """
    if not to:
        return ""
    # "//host" is protocol-relative, so it leaves the origin despite the leading "/".
    if to.startswith("//"):
        return ""
    if to.startswith(("/", "http://", "https://")):
        return to
    try:
        if isinstance(kwargs_json, dict):
            kwargs = kwargs_json
        else:
            kwargs = json.loads(kwargs_json) if kwargs_json else {}
        if pk != "" and "pk" not in kwargs:
            kwargs["pk"] = pk
        return reverse(to, kwargs=kwargs)
    except (NoReverseMatch, json.JSONDecodeError, ValueError, AttributeError):
        return ""


def _safe_json(value):
    # Safe only in a single-quoted attribute: <, > and & are left literal.
    return json.dumps(value).replace("'", "&#x27;")


# Anything outside this set would reach the emitted JS raw.
_SIGNAL_PATH_RE = re.compile(r"^[\w.]+$")


def _coerce_signal_value(v):
    """Coerce string attr values to Python booleans for correct JSON output.

    HTML attrs are always strings; "true"/"false" map to JSON booleans.
    Numeric strings ("0", "1.5") are preserved as strings — callers that want
    a JS number should pass a Python int/float directly via context.
    """
    if not isinstance(v, str):
        return v
    if v == "true":
        return True
    if v == "false":
        return False
    return v


def _blob_attr(blob: dict, ifmissing=False) -> str:
    """Render a signal blob as a data-signals attribute.

    `__ifmissing` seeds only what the browser lacks, so a morph cannot clobber it.
    """
    if not blob:
        return ""
    mod = "__ifmissing" if ifmissing else ""
    return f"data-signals{mod}='{_safe_json(blob)}'"


@register.simple_tag
def lbr_build_signals(attrs, ifmissing=""):
    """Build data-signals HTML attribute(s) from $-prefixed Cotton attrs.

    - $key=val            → JSON blob:  data-signals='{"key": val}'
    - $path.key__mod=val  → per-signal: data-signals:path.key__mod='"val"'

    Dots before __ are path separators; dots after __ are modifier options.
    Both forms can coexist on the same element. Pass ifmissing for state the
    browser owns after the first render.
    """
    blob = {}
    individual = []

    for key, value in attrs.items():
        if not key.startswith("$"):
            continue
        signal_key = key[1:]

        if "__" in signal_key:
            # Has modifier — render as individual data-signals:path__mod attr.
            # Value is a JS expression, so JSON-encode it.
            individual.append(f"data-signals:{signal_key}='{_safe_json(value)}'")
        else:
            # No modifier — accumulate into the JSON blob.
            parts = signal_key.split(".")
            d = blob
            for part in parts[:-1]:
                d = d.setdefault(part, {})
            d[parts[-1]] = _coerce_signal_value(value)

    out = [_blob_attr(blob, ifmissing), *individual]
    return mark_safe(" ".join(part for part in out if part))


def _sync_query_signals(attrs):
    """Return list of signal paths for non-modifier $ signals."""
    paths = []
    for key in attrs:
        if not key.startswith("$"):
            continue
        signal_key = key[1:]
        if "__" in signal_key:
            continue
        paths.append(signal_key)
    return paths


def _build_datastar_js_obj(paths):
    """Build a nested JS object literal with $signal references as leaves.

    e.g. ["filters.q", "page"] → '{"filters":{"q":$filters.q},"page":$page}'
    """

    def _nest(d):
        parts = []
        for k, v in d.items():
            if isinstance(v, dict):
                parts.append(f'"{k}":{{{_nest(v)}}}')
            else:
                parts.append(f'"{k}":{v}')
        return ",".join(parts)

    obj = {}
    for path in paths:
        if not _SIGNAL_PATH_RE.match(path):
            continue
        segments = path.split(".")
        d = obj
        for seg in segments[:-1]:
            d = d.setdefault(seg, {})
        d[segments[-1]] = f"${path}"

    return "{" + _nest(obj) + "}"


@register.filter
def lbr_bind_path(bind):
    """Signal path for a form component's `bind` prop.

    Accepts a schema field (`:bind=signals.fields.q`), a bare path
    (`bind="filters.q"`), or a `$`-prefixed path (`bind="$filters.q"`). The
    `$` form matches how signals are named everywhere else; the bare form
    predates it and still works.
    """
    path = getattr(bind, "path", None) or bind
    if not isinstance(path, str):
        path = str(path)
    return path[1:] if path.startswith("$") else path


# What a morph would rewrite on each bindable element. "" means the element
# cannot be guarded this way (select: the attribute is on each <option>;
# textarea: the value is child text). Both are covered in the guide.
BIND_PRESERVE = {
    "checkbox": "checked",
    "input": "value",
    "range": "value",
    "select": "",
    "textarea": "",
    "toggle": "checked",
}


@register.simple_tag
def lbr_bind(component_name, bind):
    """Render the data-bind attribute for a form component, plus its morph guard."""
    if not bind:
        return ""
    if component_name not in BIND_PRESERVE:
        raise KeyError(
            f"'{component_name}' binds a signal but has no BIND_PRESERVE entry. "
            'Add one naming the attribute a morph would rewrite, or "" when '
            "the element cannot be guarded this way."
        )

    path = lbr_bind_path(bind)
    # Attribute-NAME position: a space alone breaks out, so escaping is not enough.
    if not _SIGNAL_PATH_RE.match(path):
        raise ValueError(
            f"bind={path!r} is not a signal path. Datastar camel-cases attribute "
            "keys, so a name survives the round trip only as word characters and "
            "dots: a hyphen would bind to a different signal than the one you "
            "named. Strip them from a UUID or slug key, as in "
            "{{ customer.pk|stringformat:'s'|cut:'-' }}."
        )

    out = f"data-bind:{path}"
    preserve = BIND_PRESERVE[component_name]
    if preserve:
        out += f' data-preserve-attr="{preserve}"'
    return mark_safe(out)


@register.filter
def lbr_signals_json(schema):
    """Convert a Signals instance to a JSON string for data-signals='...'."""
    from labb.signals import Signals

    if not isinstance(schema, Signals):
        return mark_safe("{}")
    return mark_safe(_safe_json(schema.to_signals_dict()))


@register.simple_tag
def lbr_schema_signals(schema):
    """Render a Signals instance as the data-signals attribute(s) for an element.

    Two blobs: the whole schema as `__ifmissing`, plus the fields the view
    assigned as a plain blob. See the reactivity guide, "Who owns a signal".
    """
    from labb.signals import Signals

    if not isinstance(schema, Signals):
        return ""
    out = [
        _blob_attr(schema.to_signals_dict(), ifmissing=True),
        _blob_attr(schema.changed_signals_dict()),
    ]
    return mark_safe(" ".join(part for part in out if part))


@register.simple_tag
def lbr_query_sync_js(attrs, schema=""):
    """JS for data-on-signal-patch — writes signals to URL as ?<key>=<encoded>."""
    from labb.signals import Signals

    if isinstance(schema, Signals):
        paths = [field.path for field in schema._fields.values()]
    else:
        paths = _sync_query_signals(attrs)
    paths = [p for p in paths if _SIGNAL_PATH_RE.match(p)]
    if not paths:
        return ""
    key = get_reactivity_setting("QUERY_KEY")
    encoding = get_reactivity_setting("QUERY_ENCODING")

    if encoding == "flat":
        # Each signal path becomes its own ?<key>.<path>=<value> param.
        # $path is a Datastar signal ref; URLSearchParams handles value encoding.
        # Empty/null signals are skipped so the URL only carries active state.
        sets_parts = [
            f'if(${p}!=null&&${p}!=="")p.set("{key}.{p}",${p})' for p in paths
        ]
        sets = ";".join(sets_parts)
        js = (
            f"(function(){{var p=new URLSearchParams();{sets};"
            f"var s=p.toString();"
            f'history.replaceState(null,"",s?"?"+s:location.pathname)}})()'
        )
    else:
        js_obj = _build_datastar_js_obj(paths)
        if encoding == "base64":
            js = (
                f"(function(){{var _s=JSON.stringify({js_obj});"
                f'history.replaceState(null,"","?{key}="'
                f"+btoa(unescape(encodeURIComponent(_s)))"
                f'.replace(/\\+/g,"-").replace(/\\//g,"_").replace(/=/g,""))}})()'
            )
        else:
            js = f'history.replaceState(null,"","?{key}="+encodeURIComponent(JSON.stringify({js_obj})))'
    return mark_safe(js)


def _js_escape(s) -> str:
    """Escape a value for safe inclusion inside a single-quoted JS string literal.

    Used for URLs/text that may be derived from model or user data before being
    interpolated into a Datastar action expression (e.g. @get('...')).
    """
    return (
        str(s)
        .replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )


def _wrap_before(before, action):
    # SECURITY: before is raw JS — caller must not pass user-controlled data.
    return mark_safe(f"{before}; {action}" if before else action)


@register.simple_tag
def lbr_get_action(
    href, before="", replace_url="", push_url="", preserve_query="", options=""
):
    """Build the full @get(...) action expression for data-on.

    SECURITY: before and options are raw JS — treat like |safe.
    """
    opts = f", {options}" if options else ""
    href_js = _js_escape(href)
    action = f"@get('{href_js}'{opts})"
    if push_url:
        loc = f"'{href_js}'" + ("+location.search" if preserve_query else "")
        action += f";history.pushState(null,'',{loc})"
    elif replace_url:
        loc = f"'{href_js}'" + ("+location.search" if preserve_query else "")
        action += f";history.replaceState(null,'',{loc})"
    return _wrap_before(before, action)


# CSRF: the header VALUE is the client-side JS call labbGetCSRFToken(), evaluated
# by Datastar at request time — never a server-rendered token string. The helper
# is defined in cotton/lb/m/dependencies.html whenever the reactive bundle loads.
_CSRF_HEADER_JS = "headers: {'X-CSRFToken': labbGetCSRFToken()}"


def _as_bool(value):
    # csrf arrives as a real Python bool from the template; guard string forms.
    if isinstance(value, str):
        return value.strip().lower() not in ("", "false", "0", "none", "no")
    return bool(value)


def _write_options(options, csrf, defaults=None):
    """Build the Datastar options object string for a write action (@post/@delete).

    Order of fragments: `defaults` (tag-based, e.g. contentType), then an explicit
    caller `options` object (braces stripped), then the CSRF header. The CSRF header
    is appended last, so on a `headers` key collision it wins over caller-supplied
    headers — pass csrf=False (noCSRF) to suppress it entirely.

    Returns "" (no options object) or ", {frag, frag, ...}".
    SECURITY: `options` is raw JS — treat like |safe.
    """
    frags = list(defaults or [])
    if options:
        inner = options.strip()
        if inner.startswith("{") and inner.endswith("}"):
            inner = inner[1:-1].strip()
        if inner:
            frags.append(inner)
    if csrf:
        frags.append(_CSRF_HEADER_JS)
    return ", {" + ", ".join(frags) + "}" if frags else ""


@register.simple_tag
def lbr_post_action(href, before="", tag="form", options="", csrf=True):
    """Build the @post(...) action expression.

    Every tag — including ``form`` — posts the signal store as JSON. That is the
    only body the reactivity middleware reads back into ``request.signals``; a
    form-encoded body arrives as empty signals. A caller who genuinely wants a
    classic form submission (server reads ``request.POST``) opts in explicitly
    with ``options="{contentType: 'form'}"``.

    CSRF: by default a X-CSRFToken header (labbGetCSRFToken()) is merged into the
    options so Django accepts the write. Pass csrf=False (c-lbr noCSRF) to omit it.
    An explicit options object is still merged with the CSRF header (appended last
    — see _write_options for precedence).
    SECURITY: before and options are raw JS — treat like |safe.
    """
    opts = _write_options(options, _as_bool(csrf))
    action = f"@post('{_js_escape(href)}'{opts})"
    return _wrap_before(before, action)


@register.simple_tag
def lbr_delete_action(href, before="", confirm="", options="", csrf=True):
    """Build the @delete(...) action expression.

    CSRF: by default a X-CSRFToken header (labbGetCSRFToken()) is merged in so Django
    accepts the write. Pass csrf=False (c-lbr noCSRF) to omit it. An explicit options
    object is merged with the CSRF header (appended last — see _write_options).
    SECURITY: before and options are raw JS — treat like |safe. confirm is JS-escaped.
    """
    opts = _write_options(options, _as_bool(csrf))
    action = f"@delete('{_js_escape(href)}'{opts})"
    if confirm:
        # HTML-unescape the prop, then re-escape for a single-quoted JS string literal.
        js_safe = _js_escape(_html.unescape(confirm))
        action = f"confirm('{js_safe}') && {action}"
    return _wrap_before(before, action)


@register.simple_tag
def lbr_replace_url_js(href, push=""):
    """JS expression for history.pushState/replaceState.

    If href contains $signal refs (e.g. /todos/$todoId/) they are converted to
    a JS template literal so Datastar resolves them client-side.

    When push is set, only pushState if the pathname differs from the target;
    otherwise replaceState — prevents duplicate history entries on direct loads.
    """
    if "$" in href:
        # Escape \ first, then backticks and ${, so signal-ref substitution inserts ${…} safely.
        safe = href.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
        js_href = re.sub(r"\$([\w.]+)", r"${$\1}", safe)
        url_expr = f"`{js_href}`"
    else:
        url_expr = "'" + _js_escape(href) + "'"

    if push:
        return mark_safe(
            f"(function(){{var _u={url_expr};"
            f"location.pathname===_u?"
            f"history.replaceState(null,'',_u):"
            f"history.pushState(null,'',_u)}})()"
        )
    return mark_safe(f"history.replaceState(null,'',{url_expr})")


@register.filter
def strip_signal_attrs(attrs):
    """Return Cotton attrs as an HTML string, omitting $-prefixed signal attrs."""
    if not attrs:
        return ""
    if hasattr(attrs, "attrs_dict"):
        attrs_map = attrs.attrs_dict()
    elif hasattr(attrs, "items"):
        attrs_map = attrs
    else:
        attrs_map = {}
    parts = []
    for k, v in attrs_map.items():
        if k.startswith("$"):
            continue
        if v is True:
            parts.append(k)
        else:
            parts.append(f'{k}="{escape(str(v))}"')
    return mark_safe(" ".join(parts))


# ---------------------------------------------------------------------------
# Reactive prop system — $signal:fallback convention (D-RX1)
# ---------------------------------------------------------------------------


def _parse_reactive(value: str) -> tuple:
    """Parse a prop value for ``$signal.path:fallback`` syntax.

    A reactive prop is ``$`` + a signal path made of word chars and dots, optionally
    followed by ``:fallback`` (the value rendered server-side / used for the static
    class lookup). Examples::

        "$badge.variant:neutral"  → (True, "badge.variant", "neutral")
        "$open"                   → (True, "open", "")
        "primary"                 → (False, None, "primary")

    If the ``$`` value carries a signal path with characters outside ``[\\w.]``, it is
    treated as static (``is_reactive=False``) so no unsafe JS is emitted.

    Returns (is_reactive, signal_path, fallback_or_static_value).
    """
    v = str(value) if value is not None else ""
    if v.startswith("$"):
        body = v[1:]
        signal_path, _, fallback = body.partition(":")
        if _SIGNAL_PATH_RE.match(signal_path):
            return True, signal_path, fallback
    return False, None, v


class _RxResult:
    """Return value of lbr_props.

    .classes — full class string: base classes + prop classes + user class
    .attrs   — passthrough HTML attrs (schema props, class, icon attrs stripped)
               plus data-attr:class="..." appended if any prop is reactive
    """

    __slots__ = ("classes", "attrs")

    def __init__(self, classes, attrs=""):
        self.classes = classes
        self.attrs = mark_safe(attrs)

    def __str__(self):
        return self.attrs

    def __html__(self):
        return self.attrs


def _dict_to_attrs(d):
    """Reconstruct an HTML attribute string from a dict, preserving insertion order.

    Values parsed out of an attrs string are already HTML-escaped as the author
    wrote them, so they are unescaped before re-escaping — escaping them twice
    turns a `&amp;` in the source into a literal "&amp;" in the DOM.
    """
    parts = []
    for k, v in d.items():
        if v is True:
            parts.append(k)
        elif v == "":
            parts.append(f'{k}=""')
        else:
            parts.append(f'{k}="{escape(_html.unescape(str(v)))}"')
    return " ".join(parts)


class _StyleResult:
    """Return value of lbr_style_vars.

    .style — server-rendered CSS custom properties for the style attribute
    .attrs — data-attr:style="..." when any value is reactive, else empty
    """

    __slots__ = ("style", "attrs")

    def __init__(self, style, attrs=""):
        self.style = style
        self.attrs = mark_safe(attrs)

    def __str__(self):
        return self.attrs

    def __html__(self):
        return self.attrs


@register.simple_tag
def lbr_style_vars(**kwargs):
    """Render CSS custom properties, reactive when a value is a signal.

    Each kwarg name becomes a custom property, underscores to hyphens::

        {% lbr_style_vars value=value size=progressSize as sv %}
        <div class="radial-progress" style="{{ sv.style }}" {{ sv.attrs }}>

    Empty values are omitted. A "$signal:fallback" value renders the fallback
    server-side and adds data-attr:style so the property tracks the signal —
    the reactive-props equivalent for properties that are not CSS classes.
    """
    static_parts = []
    js_parts = []
    reactive = False

    for name, raw in kwargs.items():
        raw = "" if raw is None else str(raw)
        is_rx, signal_path, fallback = _parse_reactive(raw)
        prop = "--" + name.replace("_", "-")

        if fallback != "":
            static_parts.append(f"{prop}:{fallback};")

        if is_rx:
            reactive = True
            js_parts.append(f"{prop}:${{${signal_path}}};")
        elif fallback != "":
            js_parts.append(f"{prop}:{_js_escape(fallback)};")

    style = "".join(static_parts)
    if not reactive:
        return _StyleResult(style)

    lb_push_stack("components", "labb/js/vendor/datastar.js", "module")
    literal = "`" + "".join(js_parts) + "`"
    return _StyleResult(style, f'data-attr:style="{literal}"')


class _TextResult:
    """Return value of lbr_reactive_text.

    .text  — server-rendered fallback value
    .attrs — data-text="$signal" when the value is reactive, else empty
    """

    __slots__ = ("text", "attrs")

    def __init__(self, text, attrs=""):
        self.text = text
        self.attrs = mark_safe(attrs)

    def __str__(self):
        return self.text

    def __html__(self):
        return escape(self.text)


@register.simple_tag
def lbr_reactive_text(value):
    """Render a value as element text, tracking a signal when one is bound.

    {% lbr_reactive_text value as rt %}
    <span {{ rt.attrs }}>{{ rt.text }}</span>
    """
    raw = "" if value is None else str(value)
    is_rx, signal_path, fallback = _parse_reactive(raw)
    if not is_rx:
        return _TextResult(fallback)

    lb_push_stack("components", "labb/js/vendor/datastar.js", "module")
    return _TextResult(fallback, f'data-text="${signal_path}"')


@register.simple_tag
def lbr_reactive_attr(name, value):
    """Bind an HTML attribute to a signal when one is bound.

        {% lbr_reactive_attr "aria-valuenow" value as av %}
        <div aria-valuenow="{{ av.text }}" {{ av.attrs }}>

    Returns the same shape as lbr_reactive_text: .text is the server-rendered
    fallback, .attrs carries data-attr:<name> when the value is reactive.
    """
    raw = "" if value is None else str(value)
    is_rx, signal_path, fallback = _parse_reactive(raw)
    if not is_rx:
        return _TextResult(fallback)

    lb_push_stack("components", "labb/js/vendor/datastar.js", "module")
    return _TextResult(fallback, f'data-attr:{name}="${signal_path}"')


@register.simple_tag
def lbr_props(component_name, attrs=None, extra="", **override_kwargs):
    """Compute server-rendered classes and passthrough attrs from component schema.

    Reads prop values from the Cotton attrs string using the component schema —
    no c-vars or explicit prop kwargs needed for plain components.

    Returns an _RxResult with:
      .classes — base classes + prop-resolved classes + user class (from attrs or extra)
      .attrs   — passthrough attrs with schema props, class, and icon attrs stripped,
                 plus data-attr:class="..." appended if any prop is reactive

    Plain component::

        {% lbr_props "badge" attrs=attrs as rx %}
        <span class="{{ rx.classes }}" {{ rx.attrs }}>

    Component with custom-logic props (declared in c-vars, passed as overrides)::

        {% lbr_props "button" attrs=attrs btnStyle=btnStyle as rx %}
    """
    from labb.components.registry import ComponentRegistry

    spec = ComponentRegistry().get_all_components().get(component_name, {})
    variables = spec.get("variables", {})
    base_classes = spec.get("base_classes", [])

    attrs_dict = parse_attrs_to_dict(attrs) if attrs is not None else {}
    extra_class = str(attrs_dict.pop("class", "") or extra)

    server_classes = list(base_classes)
    reactive = {}
    static_vals = {}
    ordered_props = []
    consumed = set()

    for prop_name, var_spec in variables.items():
        css_mapping = var_spec.get("css_mapping")
        if css_mapping is None:
            continue

        if prop_name in override_kwargs:
            raw = (
                str(override_kwargs[prop_name])
                if override_kwargs[prop_name] is not None
                else ""
            )
        elif prop_name in attrs_dict:
            raw = str(attrs_dict[prop_name])
            consumed.add(prop_name)
        else:
            raw = str(var_spec.get("default", ""))

        ordered_props.append(prop_name)
        is_rx, signal_path, fallback = _parse_reactive(raw)
        # Boolean css_mapping keys (YAML true/false) need string normalization.
        if fallback.lower() in ("true", "false"):
            lookup = fallback.lower() == "true"
            mapped = css_mapping.get(lookup, css_mapping.get(fallback, ""))
        else:
            mapped = css_mapping.get(fallback, "")
        server_classes.append(mapped)
        if is_rx:
            reactive[prop_name] = signal_path
        else:
            static_vals[prop_name] = fallback

    if extra_class:
        server_classes.append(extra_class)
    classes = " ".join(filter(None, server_classes))

    # Passthrough: strip consumed schema props, class, and icon attrs.
    remaining = {
        k: v
        for k, v in attrs_dict.items()
        if k not in consumed and not _ICON_ATTR_RE.match(k)
    }
    passthrough = _dict_to_attrs(remaining)

    if not reactive:
        return _RxResult(classes=classes, attrs=passthrough)

    # A reactive prop emits data-attr:class="lb.classes(...)" — that needs
    # lb.classes (lb-schema.js) and Datastar to evaluate it. Self-declare the
    # runtime so a lone $-prop works with zero config under opt-in loading.
    lb_push_stack("components", "labb/js/lb-schema.js", "src")
    lb_push_stack("components", "labb/js/vendor/datastar.js", "module")

    def _js_str(s):
        return "'" + _js_escape(s) + "'"

    js_parts = []
    for prop_name in ordered_props:
        if prop_name in reactive:
            js_parts.append(f"{prop_name}: ${reactive[prop_name]}")
        else:
            js_parts.append(f"{prop_name}: {_js_str(static_vals.get(prop_name, ''))}")

    js_obj = "{" + ", ".join(js_parts) + "}"
    # Single-quoted JS string — safe inside the double-quoted HTML attribute.
    extra_js = _js_str(extra_class)

    rx_attr = (
        f"data-attr:class=\"lb.classes('{component_name}', {js_obj}, {extra_js})\""
    )
    combined = " ".join(filter(None, [passthrough, rx_attr]))
    return _RxResult(classes=classes, attrs=combined)


@register.simple_tag
def lbr_chart_signal(data):
    """Parse a chart data prop for $signal:fallback syntax.

    Returns the bare JS signal reference (e.g. '$chartData') if reactive,
    or '' if the prop is a plain static JSON string.

    Usage::

        {% lbr_chart_signal data as chart_signal %}
        {% if chart_signal %}
            data-effect="lbChart.handle(el, {{ chart_signal }})"
        {% else %}
            data-lb-chart-data="{{ data }}"
            data-init="lbChart.initFromEl(el)"
        {% endif %}
    """
    v = str(data) if data is not None else ""
    # Both chart branches drive off Datastar attributes (data-init / data-effect),
    # so a chart always needs the runtime alongside its chart-ds.js plugin.
    lb_push_stack("components", "labb/js/chart-ds.js")
    lb_push_stack("components", "labb/js/vendor/datastar.js", "module")
    if v.startswith("$"):
        signal_path, _, _ = v[1:].partition(":")
        # Reject paths with characters that would be interpolated raw into JS —
        # fall back to the static-data path instead.
        if _SIGNAL_PATH_RE.match(signal_path):
            return mark_safe(f"${signal_path}")
    return ""
