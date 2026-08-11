"""Tests for labb.signals — schema-based signal parsing."""

import pytest

from labb.signals import (
    Bool,
    Dict,
    Int,
    List,
    Signals,
    SignalValidationError,
    Str,
)

# ── Helpers ───────────────────────────────────────────────────────────────────


class FakeRequest:
    def __init__(self, signals):
        self.signals = signals


# ── Field parsing ─────────────────────────────────────────────────────────────


class TestStrField:
    def _make(self, **kwargs):
        class S(Signals):
            v = Str(**kwargs)

        return S

    def test_coerces_to_str(self):
        S = self._make(default="")
        assert S({"v": 42}).v == "42"

    def test_strips_by_default(self):
        S = self._make(default="")
        assert S({"v": "  foo  "}).v == "foo"

    def test_no_strip_when_disabled(self):
        S = self._make(default="", strip=False)
        assert S({"v": "  foo  "}).v == "  foo  "

    def test_default_on_missing(self):
        S = self._make(default="hello")
        assert S({}).v == "hello"

    def test_nested_path(self):
        class S(Signals):
            q = Str(path="filters.q", default="")

        assert S({"filters": {"q": "foo"}}).q == "foo"

    def test_accepts_request(self):
        class S(Signals):
            q = Str(path="filters.q", default="")

        req = FakeRequest({"filters": {"q": "bar"}})
        assert S(req).q == "bar"

    def test_choices_validator(self):
        S = self._make(default="a", choices=("a", "b"))
        s = S({"v": "a"})
        assert s.validate() is True

    def test_choices_validator_fail(self):
        S = self._make(default="a", choices=("a", "b"))
        s = S({"v": "c"})
        assert s.validate() is False
        assert "v" in s.errors

    def test_choices_fallback_on_parse(self):
        # choices are validated, not coerced — value is accepted on parse
        S = self._make(default="a", choices=("a", "b"))
        s = S({"v": "c"})
        assert s.v == "c"  # parse doesn't run validators

    def test_min_length_validator(self):
        S = self._make(default="", min_length=3)
        s = S({"v": "ab"})
        assert s.validate() is False

    def test_max_length_validator(self):
        S = self._make(default="", max_length=2)
        s = S({"v": "abc"})
        assert s.validate() is False


class TestIntField:
    def _make(self, **kwargs):
        class S(Signals):
            v = Int(**kwargs)

        return S

    def test_coerces_str_to_int(self):
        S = self._make(default=0)
        assert S({"v": "5"}).v == 5

    def test_default_on_bad_coercion(self):
        S = self._make(default=1)
        assert S({"v": "abc"}).v == 1

    def test_min_value_validator(self):
        S = self._make(default=1, min_value=1)
        s = S({"v": 0})
        assert s.validate() is False

    def test_max_value_validator(self):
        S = self._make(default=10, max_value=10)
        s = S({"v": 11})
        assert s.validate() is False

    def test_nested_path(self):
        class S(Signals):
            editing_pk = Int(path="ui.editingPk", default=0)

        assert S({"ui": {"editingPk": 7}}).editing_pk == 7


class TestBoolField:
    def _make(self, **kwargs):
        class S(Signals):
            v = Bool(**kwargs)

        return S

    def test_true_bool(self):
        assert self._make()({"v": True}).v is True

    def test_false_str(self):
        assert self._make()({"v": "false"}).v is False

    def test_zero_str(self):
        assert self._make()({"v": "0"}).v is False

    def test_truthy_str(self):
        assert self._make()({"v": "yes"}).v is True

    def test_off_str(self):
        assert self._make()({"v": "off"}).v is False

    def test_no_str(self):
        assert self._make()({"v": "no"}).v is False


class TestDictField:
    def test_passes_dict_through(self):
        class S(Signals):
            selected = Dict(default_factory=dict)

        s = S({"selected": {"1": True, "2": False}})
        assert s.selected == {"1": True, "2": False}

    def test_default_factory(self):
        class S(Signals):
            selected = Dict(default_factory=dict)

        assert S({}).selected == {}

    def test_non_dict_falls_back(self):
        class S(Signals):
            selected = Dict(default_factory=dict)

        assert S({"selected": "not-a-dict"}).selected == {}


class TestListField:
    def test_passes_list_through(self):
        class S(Signals):
            ids = List(default_factory=list)

        assert S({"ids": [1, 2, 3]}).ids == [1, 2, 3]

    def test_non_list_falls_back(self):
        class S(Signals):
            ids = List(default_factory=list)

        assert S({"ids": "not-a-list"}).ids == []


# ── Required fields ───────────────────────────────────────────────────────────


class TestRequired:
    def test_missing_required_raises_at_parse(self):
        class S(Signals):
            pk = Int(required=True)

        with pytest.raises(SignalValidationError):
            S({})

    def test_present_required_passes(self):
        class S(Signals):
            pk = Int(required=True)

        assert S({"pk": 5}).pk == 5

    def test_bad_type_required_raises(self):
        class S(Signals):
            pk = Int(required=True)

        with pytest.raises(SignalValidationError):
            S({"pk": "not-int"})


# ── validate= and s.validate() ────────────────────────────────────────────────


class TestValidation:
    def test_validate_true_raises_on_failure(self):
        class S(Signals):
            v = Str(default="a", choices=("a", "b"))

        with pytest.raises(SignalValidationError):
            S({"v": "c"}, validate=True)

    def test_validate_false_no_raise(self):
        class S(Signals):
            v = Str(default="a", choices=("a", "b"))

        s = S({"v": "c"}, validate=False)
        assert s.v == "c"  # no raise

    def test_manual_validate_returns_bool(self):
        class S(Signals):
            v = Str(default="a", choices=("a", "b"))

        s = S({"v": "c"})
        assert s.validate() is False
        assert "v" in s.errors

    def test_manual_validate_success(self):
        class S(Signals):
            v = Str(default="a", choices=("a", "b"))

        s = S({"v": "b"})
        assert s.validate() is True
        assert s.errors == {}

    def test_validate_method_custom(self):
        class S(Signals):
            sort = Str(default="name")

            def validate_sort(self, value):
                if value == "evil":
                    raise SignalValidationError("bad sort")
                return value.upper()

        s = S({"sort": "name"})
        assert s.validate() is True
        assert s.sort == "NAME"  # validate method transforms the value

    def test_validate_method_failure(self):
        class S(Signals):
            sort = Str(default="name")

            def validate_sort(self, value):
                raise SignalValidationError("always bad")

        s = S({"sort": "name"})
        assert s.validate() is False
        assert "sort" in s.errors

    def test_multiple_errors(self):
        class S(Signals):
            a = Int(default=0, min_value=1)
            b = Str(default="x", choices=("x", "y"))

        s = S({"a": 0, "b": "z"})
        s.validate()
        assert "a" in s.errors
        assert "b" in s.errors


# ── Inheritance ───────────────────────────────────────────────────────────────


class TestInheritance:
    def test_child_inherits_parent_fields(self):
        class Base(Signals):
            page = Int(default=1)

        class Child(Base):
            q = Str(default="")

        s = Child({"page": 3, "q": "foo"})
        assert s.page == 3
        assert s.q == "foo"

    def test_child_overrides_parent_field(self):
        class Base(Signals):
            page = Int(default=1)

        class Child(Base):
            page = Int(default=99)  # different default

        assert Child({}).page == 99

    def test_grandchild_inherits(self):
        class A(Signals):
            x = Int(default=0)

        class B(A):
            y = Int(default=0)

        class C(B):
            z = Int(default=0)

        s = C({"x": 1, "y": 2, "z": 3})
        assert s.x == 1 and s.y == 2 and s.z == 3


# ── Path inference ────────────────────────────────────────────────────────────


class TestPathInference:
    def test_implicit_path_from_name(self):
        class S(Signals):
            page = Int(default=1)

        assert S({"page": 5}).page == 5

    def test_explicit_path_overrides_name(self):
        class S(Signals):
            q = Str(path="filters.q", default="")

        assert S({"filters": {"q": "bar"}}).q == "bar"
        assert S({"q": "bar"}).q == ""  # "q" top-level key is ignored

    def test_deeply_nested_path(self):
        class S(Signals):
            editing_pk = Int(path="ui.editingPk", default=0)

        assert S({"ui": {"editingPk": 3}}).editing_pk == 3


# ── fields property ───────────────────────────────────────────────────────────


class TestFields:
    def test_fields_returns_field_descriptors(self):
        class S(Signals):
            page = Int(default=1)

        s = S({"page": 2})
        assert s.fields["page"] is S._fields["page"]

    def test_path_accessible(self):
        class S(Signals):
            q = Str(path="filters.q", default="")

        assert S({}).fields["q"].path == "filters.q"


# ── to_signals_dict ───────────────────────────────────────────────────────────


class TestToSignalsDict:
    def test_flat_path(self):
        class S(Signals):
            page = Int(default=1)

        assert S({"page": 3}).to_signals_dict() == {"page": 3}

    def test_nested_path(self):
        class S(Signals):
            q = Str(path="filters.q", default="")

        assert S({"filters": {"q": "foo"}}).to_signals_dict() == {
            "filters": {"q": "foo"}
        }

    def test_multiple_fields_merge_nested(self):
        class S(Signals):
            field = Str(path="sort.field", default="name")
            direction = Str(path="sort.dir", default="asc")

        result = S({"sort": {"field": "email", "dir": "desc"}}).to_signals_dict()
        assert result == {"sort": {"field": "email", "dir": "desc"}}

    def test_defaults_used_when_missing(self):
        class S(Signals):
            page = Int(default=1)
            q = Str(path="filters.q", default="")

        assert S({}).to_signals_dict() == {"page": 1, "filters": {"q": ""}}

    def test_roundtrip(self):
        class S(Signals):
            q = Str(path="filters.q", default="")
            page = Int(default=1)

        original = {"filters": {"q": "foo"}, "page": 2}
        assert S(original).to_signals_dict() == original


# ── Plain dict in tests ───────────────────────────────────────────────────────


class TestPlainDict:
    def test_accepts_plain_dict(self):
        class S(Signals):
            page = Int(default=1)

        assert S({"page": 2}).page == 2

    def test_accepts_request(self):
        class S(Signals):
            page = Int(default=1)

        req = FakeRequest({"page": 3})
        assert S(req).page == 3

    def test_none_gives_all_defaults(self):
        class S(Signals):
            page = Int(default=1)
            q = Str(default="")

        s = S(None)
        assert s.page == 1 and s.q == ""


class TestMissingMiddleware:
    """A request without .signals means ReactivityMiddleware is not installed —
    without the check every field would silently fall back to its default."""

    def _request(self):
        from django.test import RequestFactory

        return RequestFactory().get("/?page=2")

    def test_request_without_signals_raises(self):
        from django.core.exceptions import ImproperlyConfigured

        class S(Signals):
            page = Int(default=1)

        with pytest.raises(ImproperlyConfigured, match="ReactivityMiddleware"):
            S(self._request())

    def test_request_with_empty_signals_is_fine(self):
        class S(Signals):
            page = Int(default=1)

        request = self._request()
        request.signals = {}
        assert S(request).page == 1

    def test_plain_dict_still_works(self):
        class S(Signals):
            page = Int(default=1)

        assert S({"page": 2}).page == 2


# ── from_query — clean query string → signals (replace-url reverse) ────────────


class FakeGetRequest:
    def __init__(self, get):
        self.GET = get


class QuerySchema(Signals):
    q = Str(path="filters.q", default="", query="q")
    status = Str(path="filters.st", default="", query="status")
    sort_field = Str(path="sort.field", default="name", query="sort")
    page = Int(default=1, min_value=1, query="page")
    editing_pk = Int(path="ui.editingPk", default=0)  # no query key


class TestFromQuery:
    def test_hydrates_query_keys_onto_paths(self):
        s = QuerySchema.from_query({"q": "atlas", "sort": "mrr", "page": "3"})
        assert s.q == "atlas"
        assert s.sort_field == "mrr"
        assert s.page == 3

    def test_reads_dot_get_from_request(self):
        req = FakeGetRequest({"q": "beacon", "status": "active"})
        s = QuerySchema.from_query(req)
        assert s.q == "beacon"
        assert s.status == "active"

    def test_missing_and_empty_params_keep_defaults(self):
        s = QuerySchema.from_query({"q": "", "page": ""})
        assert s.q == ""
        assert s.page == 1
        assert s.sort_field == "name"

    def test_fields_without_query_key_are_ignored(self):
        # A URL param colliding with a non-query field name must not leak in.
        s = QuerySchema.from_query({"editing_pk": "99"})
        assert s.editing_pk == 0

    def test_coerces_via_field_type(self):
        s = QuerySchema.from_query({"page": "not-a-number"})
        assert s.page == 1  # bad coercion falls back to default
