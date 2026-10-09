import base64
import json
import re

from asgiref.sync import iscoroutinefunction, markcoroutinefunction

from labb.django_settings import get_reactivity_setting
from labb.templatetags.lb_tags import (
    _get_drained,
    _get_stacks,
    _set_late_fill,
    render_stack_tags,
)

# Datastar always uses "datastar" as its own GET/POST parameter for request signals.
# lbr syncQuery uses a configurable key (LABB_SETTINGS["REACTIVITY"]["QUERY_KEY"]) with a
# configurable encoding ("base64" | "flat" | "json") for URL-persisted state.
_DATASTAR_KEY = "datastar"
_FORM_CONTENT_TYPE = "application/x-www-form-urlencoded"


def _form_post(request):
    """POST params, but only for form-encoded bodies.

    Reading request.POST on a multipart body would parse the upload in middleware.
    """
    if request.method != "POST":
        return {}
    if not (request.content_type or "").startswith(_FORM_CONTENT_TYPE):
        return {}
    return request.POST


def _decode_base64(raw: str) -> dict:
    padded = raw.replace("-", "+").replace("_", "/")
    padded += "=" * (-len(padded) % 4)
    return json.loads(base64.b64decode(padded))


def _decode_flat(request, prefix: str) -> dict:
    """Unflatten ?<prefix>.<path>=<value> params into a nested dict.

    Collision-safe: if a path segment conflicts with an already-set scalar
    (e.g. ?p.a=1&p.a.b=2), the conflicting key is skipped rather than raising.
    """
    dot_prefix = prefix + "."
    result: dict = {}
    for key in request.GET:
        if not key.startswith(dot_prefix):
            continue
        path = key[len(dot_prefix) :]
        parts = path.split(".")
        d = result
        for part in parts[:-1]:
            nxt = d.setdefault(part, {})
            if not isinstance(nxt, dict):
                # Parent segment already holds a scalar — skip this conflicting key.
                d = None
                break
            d = nxt
        if d is None:
            continue
        d[parts[-1]] = request.GET[key]
    return result


def _decode_signals(raw: str, encoding: str) -> dict:
    if not raw:
        return {}
    try:
        if encoding == "base64":
            return _decode_base64(raw)
        return json.loads(raw)
    except Exception:
        return {}


class ReactivityMiddleware:
    sync_capable = True
    async_capable = True

    def __init__(self, get_response):
        self.get_response = get_response
        self.async_mode = iscoroutinefunction(get_response)
        if self.async_mode:
            markcoroutinefunction(self)

    def __call__(self, request):
        if self.async_mode:
            return self.__acall__(request)
        self._attach_signals(request)
        return self.get_response(request)

    async def __acall__(self, request):
        self._attach_signals(request)
        return await self.get_response(request)

    def _attach_signals(self, request):
        """Set request.is_datastar and request.signals. Reads headers and the
        already-buffered body only, so it is safe on the async path."""
        request.is_datastar = request.headers.get("Datastar-Request") == "true"

        # 1. Datastar's own GET/POST parameter (always raw JSON, hardcoded in Datastar)
        raw = request.GET.get(_DATASTAR_KEY) or _form_post(request).get(
            _DATASTAR_KEY, ""
        )
        if raw:
            request.signals = _decode_signals(raw, "json")
            return

        # 2. lbr syncQuery URL persistence (configurable key + encoding)
        key = get_reactivity_setting("QUERY_KEY")
        encoding = get_reactivity_setting("QUERY_ENCODING")

        if encoding == "flat":
            try:
                signals = _decode_flat(request, key)
            except Exception:
                signals = {}
            if signals:
                request.signals = signals
                return
        else:
            raw = request.GET.get(key) or _form_post(request).get(key, "")
            if raw:
                request.signals = _decode_signals(raw, encoding)
                return

        # 3. JSON request body — Datastar @post without contentType:'form'
        if (request.content_type or "").startswith("application/json"):
            try:
                raw = request.body.decode("utf-8")
                request.signals = _decode_signals(raw, "json")
                return
            except Exception:
                pass

        request.signals = {}


_STACK_MARKER_RE = re.compile(rb"<!--labb-stack:([a-zA-Z0-9_-]+)-->")


class StackFillMiddleware:
    """Fill lb_load_stack markers after the template has rendered.

    lb_load_stack emits where it sits, so a script pushed by a body component
    never reaches a stack loaded in <head>. With this installed the tag leaves a
    marker and anything pushed later is injected into it, which makes the
    documented <head> placement work for reactive pages.
    """

    sync_capable = True
    async_capable = True

    def __init__(self, get_response):
        self.get_response = get_response
        self.async_mode = iscoroutinefunction(get_response)
        if self.async_mode:
            markcoroutinefunction(self)

    def __call__(self, request):
        if self.async_mode:
            return self.__acall__(request)
        _set_late_fill(True)
        return self._fill(self.get_response(request))

    async def __acall__(self, request):
        _set_late_fill(True)
        return self._fill(await self.get_response(request))

    def _fill(self, response):
        if getattr(response, "streaming", False):
            return response
        if not response.get("Content-Type", "").startswith("text/html"):
            return response
        if b"<!--labb-stack:" not in response.content:
            return response

        stacks = _get_stacks()
        drained = _get_drained()

        def replace(match):
            name = match.group(1).decode()
            late = {
                path: mode
                for path, mode in stacks.get(name, {}).items()
                if path not in drained.get(name, set())
            }
            if not late:
                return b""
            drained.setdefault(name, set()).update(late)
            return "\n".join(render_stack_tags(late)).encode()

        response.content = _STACK_MARKER_RE.sub(replace, response.content)
        if response.has_header("Content-Length"):
            response["Content-Length"] = str(len(response.content))
        return response
