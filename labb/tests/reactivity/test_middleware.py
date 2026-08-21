"""
Tests for ReactivityMiddleware.

Signal sources (in priority order):
1. ?datastar= — Datastar's own GET/POST param (raw JSON, hardcoded in Datastar)
2. ?<QUERY_KEY>= — lbr syncQuery URL persistence param (default: ?lbr=flat)
3. JSON request body — Datastar @post without contentType:'form'

is_datastar reflects the Datastar-Request header only (not the signal source).
"""

import base64
import json
from urllib.parse import urlencode

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.test import RequestFactory

from labb.middleware import ReactivityMiddleware


def _make_middleware(response=None):
    get_response = lambda request: response  # noqa: E731
    return ReactivityMiddleware(get_response)


def _b64(signals):
    """Encode signals dict as base64url (default encoding)."""
    raw = json.dumps(signals)
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")


@pytest.fixture
def factory():
    return RequestFactory()


@pytest.fixture
def mw():
    return _make_middleware()


class TestIsDatastar:
    def test_true_when_header_present(self, factory, mw):
        request = factory.get("/")
        request.META["HTTP_DATASTAR_REQUEST"] = "true"
        mw(request)
        assert request.is_datastar is True

    def test_false_when_header_absent(self, factory, mw):
        request = factory.get("/")
        mw(request)
        assert request.is_datastar is False

    def test_false_when_header_wrong_value(self, factory, mw):
        request = factory.get("/")
        request.META["HTTP_DATASTAR_REQUEST"] = "1"
        mw(request)
        assert request.is_datastar is False


class TestSignalParsing:
    def test_empty_when_no_param(self, factory, mw):
        request = factory.get("/")
        mw(request)
        assert request.signals == {}

    # ── ?datastar= path (Datastar's own parameter, raw JSON) ─────────────────

    def test_datastar_param_parsed_as_json(self, factory, mw):
        qs = urlencode({"datastar": json.dumps({"count": 1})})
        request = factory.get(f"/?{qs}")
        mw(request)
        assert request.signals == {"count": 1}

    def test_datastar_param_works_without_header(self, factory, mw):
        qs = urlencode({"datastar": json.dumps({"filters": {"q": "foo"}})})
        request = factory.get(f"/?{qs}")
        mw(request)
        assert request.signals == {"filters": {"q": "foo"}}

    def test_datastar_post_param_parsed(self, factory, mw):
        signals = {"filters": {"q": "bar"}}
        request = factory.post(
            "/",
            data=urlencode({"datastar": json.dumps(signals)}),
            content_type="application/x-www-form-urlencoded",
        )
        mw(request)
        assert request.signals == {"filters": {"q": "bar"}}

    def test_datastar_param_takes_precedence_over_lbr(self, factory, mw):
        datastar_sigs = {"source": "datastar"}
        lbr_sigs = {"source": "lbr"}
        qs = urlencode(
            {
                "datastar": json.dumps(datastar_sigs),
                "lbr": _b64(lbr_sigs),
            }
        )
        request = factory.get(f"/?{qs}")
        mw(request)
        assert request.signals == {"source": "datastar"}

    # ── ?lbr= path (lbr syncQuery URL persistence, flat by default) ────

    def test_flat_default_params_unflattened(self, factory, mw):
        request = factory.get("/?lbr.filters.q=foo&lbr.page=2")
        mw(request)
        assert request.signals == {"filters": {"q": "foo"}, "page": "2"}

    def test_flat_default_empty_gives_empty_dict(self, factory, mw):
        request = factory.get("/?other=value")
        mw(request)
        assert request.signals == {}

    def test_flat_scalar_then_nested_collision_does_not_crash(self, factory, mw):
        # ?lbr.a=1 sets a scalar, ?lbr.a.b=2 would try to nest under it.
        # The conflicting key is skipped rather than raising a 500.
        request = factory.get("/?lbr.a=1&lbr.a.b=2")
        response = mw(request)  # must not raise
        assert isinstance(request.signals, dict)
        assert request.signals["a"] == "1"
        assert response is None  # get_response sentinel

    def test_flat_nested_then_scalar_collision_last_write_wins(self, factory, mw):
        # Reverse order: nested first, then scalar overwrites it — also no crash.
        request = factory.get("/?lbr.a.b=2&lbr.a=1")
        mw(request)
        assert request.signals["a"] == "1"

    # ── ?lbr= base64 (non-default, requires QUERY_ENCODING='base64') ──────────

    def test_lbr_param_decoded_as_base64(self, factory, mw):
        from unittest.mock import patch

        with patch(
            "labb.middleware.get_reactivity_setting",
            side_effect=lambda k: {"QUERY_KEY": "lbr", "QUERY_ENCODING": "base64"}.get(
                k
            ),
        ):
            signals = {"filters": {"q": "foo"}, "page": 2}
            qs = urlencode({"lbr": _b64(signals)})
            request = factory.get(f"/?{qs}")
            mw(request)
        assert request.signals == signals

    def test_lbr_empty_string_gives_empty_dict(self, factory, mw):
        from unittest.mock import patch

        with patch(
            "labb.middleware.get_reactivity_setting",
            side_effect=lambda k: {"QUERY_KEY": "lbr", "QUERY_ENCODING": "base64"}.get(
                k
            ),
        ):
            request = factory.get("/?lbr=")
            mw(request)
        assert request.signals == {}

    def test_lbr_invalid_base64_gives_empty_dict(self, factory, mw):
        from unittest.mock import patch

        with patch(
            "labb.middleware.get_reactivity_setting",
            side_effect=lambda k: {"QUERY_KEY": "lbr", "QUERY_ENCODING": "base64"}.get(
                k
            ),
        ):
            request = factory.get("/?lbr=not-valid!!!")
            mw(request)
        assert request.signals == {}

    # ── JSON body path (Datastar @post without contentType:'form') ────────────

    def test_json_body_parsed(self, factory, mw):
        signals = {"selected": {"1": True, "2": False}}
        body = json.dumps(signals).encode()
        request = factory.post("/", data=body, content_type="application/json")
        mw(request)
        assert request.signals == signals

    def test_get_response_called(self, factory):
        sentinel = object()
        mw = _make_middleware(response=sentinel)
        request = factory.get("/")
        assert mw(request) is sentinel


class TestDoesNotConsumeRequestBody:
    """The middleware must never parse a multipart body — that would run the whole
    upload through middleware and freeze request.upload_handlers before the view."""

    def _multipart(self, factory, extra=None):
        data = {"f": SimpleUploadedFile("x.txt", b"hello")}
        data.update(extra or {})
        return factory.post("/", data=data)

    def test_multipart_upload_handlers_still_settable(self, factory, mw):
        request = self._multipart(factory)
        mw(request)
        # Raises if the middleware touched request.POST.
        request.upload_handlers = [TemporaryFileUploadHandler(request)]

    def test_multipart_file_still_readable_after_middleware(self, factory, mw):
        request = self._multipart(factory)
        mw(request)
        assert request.FILES["f"].read() == b"hello"

    def test_multipart_signals_are_empty(self, factory, mw):
        request = self._multipart(factory, {"datastar": json.dumps({"count": 1})})
        mw(request)
        assert request.signals == {}

    def test_multipart_query_key_not_read_from_post(self, factory, mw):
        from unittest.mock import patch

        with patch(
            "labb.middleware.get_reactivity_setting",
            side_effect=lambda k: {"QUERY_KEY": "lbr", "QUERY_ENCODING": "base64"}.get(
                k
            ),
        ):
            request = self._multipart(factory, {"lbr": _b64({"page": 2})})
            mw(request)
        assert request.signals == {}
        request.upload_handlers = [TemporaryFileUploadHandler(request)]

    def test_get_request_never_reads_post(self, factory, mw):
        request = factory.get("/")
        mw(request)
        assert "_post" not in request.__dict__

    def test_form_encoded_query_key_still_read_from_post(self, factory, mw):
        from unittest.mock import patch

        with patch(
            "labb.middleware.get_reactivity_setting",
            side_effect=lambda k: {"QUERY_KEY": "lbr", "QUERY_ENCODING": "base64"}.get(
                k
            ),
        ):
            request = factory.post(
                "/",
                data=urlencode({"lbr": _b64({"page": 2})}),
                content_type="application/x-www-form-urlencoded",
            )
            mw(request)
        assert request.signals == {"page": 2}
