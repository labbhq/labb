import base64
import json

from labb.django_settings import get_reactivity_setting

# Datastar always uses "datastar" as its own GET/POST parameter for request signals.
# lbr syncQuery uses a configurable key (LABB_SETTINGS["REACTIVITY"]["QUERY_KEY"]) with a
# configurable encoding ("base64" | "flat" | "json") for URL-persisted state.
_DATASTAR_KEY = "datastar"


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
        path = key[len(dot_prefix):]
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
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.is_datastar = request.headers.get("Datastar-Request") == "true"

        # 1. Datastar's own GET/POST parameter (always raw JSON, hardcoded in Datastar)
        raw = request.GET.get(_DATASTAR_KEY) or request.POST.get(_DATASTAR_KEY, "")
        if raw:
            request.signals = _decode_signals(raw, "json")
            return self.get_response(request)

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
                return self.get_response(request)
        else:
            raw = request.GET.get(key) or request.POST.get(key, "")
            if raw:
                request.signals = _decode_signals(raw, encoding)
                return self.get_response(request)

        # 3. JSON request body — Datastar @post without contentType:'form'
        if (request.content_type or "").startswith("application/json"):
            try:
                raw = request.body.decode("utf-8")
                request.signals = _decode_signals(raw, "json")
                return self.get_response(request)
            except Exception:
                pass

        request.signals = {}
        return self.get_response(request)
