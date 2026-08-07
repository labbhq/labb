"""
Signal schema — typed, validated access to Datastar signals in Django views.

Usage::

    from labb.signals import Signals, Str, Int, Dict

    SORTABLE = {"name", "department", "role", "joined_at"}

    class EmployeeSignals(Signals):
        q          = Str(path="filters.q",    default="")
        sort_field = Str(path="sort.field",   default="name", choices=SORTABLE)
        sort_dir   = Str(path="sort.dir",     default="asc",  choices=("asc", "desc"))
        page       = Int(default=1, min_value=1)
        editing_pk = Int(path="ui.editingPk", default=0)
        selected   = Dict(default_factory=dict)

    # In a view:
    s = EmployeeSignals(request)               # parse only, use defaults on bad values
    s = EmployeeSignals(request, validate=True) # parse + validate, raise SignalValidationError

    # Manual validation:
    s = EmployeeSignals(request)
    if not s.validate():
        print(s.errors)  # {"sort_field": "'sort_field' must be one of ..."}

    # Custom field validation via method:
    class EmployeeSignals(Signals):
        sort_field = Str(path="sort.field", default="name")

        def validate_sort_field(self, value):
            if value not in SORTABLE:
                raise SignalValidationError(f"Unknown sort field: {value!r}")
            return value

    # Inheritance:
    class BaseSignals(Signals):
        page = Int(default=1, min_value=1)

    class EmployeeSignals(BaseSignals):
        q = Str(path="filters.q", default="")
        # inherits page

    # Tests — pass a plain dict instead of a request:
    s = EmployeeSignals({"filters": {"q": "foo"}, "page": 2})
"""

from __future__ import annotations

from typing import Any, Callable


def _get_nested(d: dict, path: str, default=None):
    """Traverse nested dict by dot-path.  'filters.q' -> d['filters']['q']."""
    for part in path.split("."):
        if not isinstance(d, dict):
            return default
        d = d.get(part)
        if d is None:
            return default
    return d


class SignalValidationError(Exception):
    """Raised when a required signal is missing or validate=True encounters errors."""

    def __init__(self, message_or_errors):
        if isinstance(message_or_errors, dict):
            self.error_dict = message_or_errors
            msg = "; ".join(f"{k}: {v}" for k, v in message_or_errors.items())
        else:
            self.error_dict = {}
            msg = str(message_or_errors)
        super().__init__(msg)


# ── Field base ────────────────────────────────────────────────────────────────


class SignalField:
    """Base descriptor for a single typed signal value."""

    def __init__(
        self,
        path: str | None = None,
        default: Any = None,
        default_factory: Callable | None = None,
        required: bool = False,
        query: str | None = None,
    ):
        self._explicit_path = path
        self.default = default
        self.default_factory = default_factory
        self.required = required
        # Clean query-string key this field hydrates from via Signals.from_query.
        # None means the field is not read from the URL.
        self.query = query
        self.name: str = ""  # set by __set_name__
        self.path: str = path or ""  # resolved in __set_name__

    def __set_name__(self, owner, name: str):
        self.name = name
        if self._explicit_path is None:
            self.path = name

    def get_default(self):
        if self.default_factory is not None:
            return self.default_factory()
        return self.default

    def coerce(self, value):
        """Convert raw value to target type. Override in subclasses."""
        return value

    def run_validators(self, value):
        """Run field-level built-in validators. Override in subclasses."""
        return value

    def parse(self, raw: dict):
        """Extract, coerce, and return a value from the raw signal dict."""
        raw_value = _get_nested(raw, self.path)
        if raw_value is None:
            if self.required:
                raise SignalValidationError(
                    f"Required signal '{self.path}' is missing."
                )
            return self.get_default()
        try:
            return self.coerce(raw_value)
        except (ValueError, TypeError):
            if self.required:
                raise SignalValidationError(
                    f"Signal '{self.path}' has an invalid value: {raw_value!r}"
                )
            return self.get_default()


# ── Concrete field types ──────────────────────────────────────────────────────


class Str(SignalField):
    def __init__(
        self,
        path=None,
        default="",
        default_factory=None,
        required=False,
        query=None,
        strip=True,
        choices=None,
        min_length: int | None = None,
        max_length: int | None = None,
    ):
        super().__init__(
            path=path,
            default=default,
            default_factory=default_factory,
            required=required,
            query=query,
        )
        self.strip = strip
        self.choices = choices
        self.min_length = min_length
        self.max_length = max_length

    def coerce(self, value):
        s = str(value)
        return s.strip() if self.strip else s

    def run_validators(self, value):
        if self.choices is not None and value not in self.choices:
            raise SignalValidationError(
                f"'{self.name}' must be one of {sorted(self.choices)}, got {value!r}"
            )
        if self.min_length is not None and len(value) < self.min_length:
            raise SignalValidationError(
                f"'{self.name}' must be at least {self.min_length} characters"
            )
        if self.max_length is not None and len(value) > self.max_length:
            raise SignalValidationError(
                f"'{self.name}' must be at most {self.max_length} characters"
            )
        return value


class Int(SignalField):
    def __init__(
        self,
        path=None,
        default=0,
        default_factory=None,
        required=False,
        query=None,
        min_value: int | None = None,
        max_value: int | None = None,
    ):
        super().__init__(
            path=path,
            default=default,
            default_factory=default_factory,
            required=required,
            query=query,
        )
        self.min_value = min_value
        self.max_value = max_value

    def coerce(self, value):
        return int(value)

    def run_validators(self, value):
        if self.min_value is not None and value < self.min_value:
            raise SignalValidationError(
                f"'{self.name}' must be >= {self.min_value}, got {value}"
            )
        if self.max_value is not None and value > self.max_value:
            raise SignalValidationError(
                f"'{self.name}' must be <= {self.max_value}, got {value}"
            )
        return value


class Float(SignalField):
    def __init__(
        self,
        path=None,
        default=0.0,
        default_factory=None,
        required=False,
        query=None,
        min_value: float | None = None,
        max_value: float | None = None,
    ):
        super().__init__(
            path=path,
            default=default,
            default_factory=default_factory,
            required=required,
            query=query,
        )
        self.min_value = min_value
        self.max_value = max_value

    def coerce(self, value):
        return float(value)

    def run_validators(self, value):
        if self.min_value is not None and value < self.min_value:
            raise SignalValidationError(f"'{self.name}' must be >= {self.min_value}")
        if self.max_value is not None and value > self.max_value:
            raise SignalValidationError(f"'{self.name}' must be <= {self.max_value}")
        return value


class Bool(SignalField):
    def __init__(
        self, path=None, default=False, default_factory=None, required=False, query=None
    ):
        super().__init__(
            path=path,
            default=default,
            default_factory=default_factory,
            required=required,
            query=query,
        )

    def coerce(self, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() not in ("false", "0", "no", "off", "")
        return bool(value)


class Dict(SignalField):
    def __init__(
        self, path=None, default=None, default_factory=dict, required=False, query=None
    ):
        super().__init__(
            path=path,
            default=default,
            default_factory=default_factory,
            required=required,
            query=query,
        )

    def coerce(self, value):
        return value if isinstance(value, dict) else {}


class List(SignalField):
    def __init__(
        self, path=None, default=None, default_factory=list, required=False, query=None
    ):
        super().__init__(
            path=path,
            default=default,
            default_factory=default_factory,
            required=required,
            query=query,
        )

    def coerce(self, value):
        return value if isinstance(value, list) else []


# ── Metaclass + base ──────────────────────────────────────────────────────────


class _SignalsMeta(type):
    """Collects SignalField descriptors across the MRO so inheritance works."""

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        fields: dict[str, SignalField] = {}
        for klass in reversed(cls.__mro__):
            for attr_name, value in vars(klass).items():
                if isinstance(value, SignalField):
                    fields[attr_name] = value
        cls._fields = fields
        return cls


class Signals(metaclass=_SignalsMeta):
    """Base class for signal schemas.

    Subclass and declare fields (see module docstring for full examples).
    """

    def __init__(self, data=None, validate: bool = False):
        raw: dict = {} if data is None else getattr(data, "signals", data)
        self._raw = raw
        self._errors: dict[str, str] = {}

        for attr_name, field in self._fields.items():
            # required=True raises SignalValidationError immediately on missing/bad value
            setattr(self, attr_name, field.parse(raw))

        if validate:
            if not self.validate():
                raise SignalValidationError(self._errors)

    @classmethod
    def from_query(cls, source):
        """Build an instance from a clean query string (the reverse of replace-url).

        A Datastar request carries the whole signal bag, so ``cls(request)`` is
        enough. A cold load of a shared link carries only the clean URL that
        ``c-lbr.replace-url`` wrote — this reads those params back into signals,
        mapping each field's ``query`` key onto its ``path``. Fields without a
        ``query`` key keep their default.

        ``source`` is a request (its ``.GET``) or a plain mapping for tests::

            class QuerySignals(Signals):
                q    = Str(path="filters.q", query="q")
                page = Int(default=1, query="page")

            s = QuerySignals.from_query(request)   # ?q=atlas&page=2
        """
        get = getattr(source, "GET", source)
        raw: dict = {}
        for field in cls._fields.values():
            if not field.query or field.query not in get:
                continue
            value = get[field.query]
            if value in (None, ""):
                continue
            parts = field.path.split(".")
            node = raw
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = value
        return cls(raw)

    def validate(self) -> bool:
        """Run all field validators and validate_<name> methods.

        Returns True if all pass. Populates self.errors on failure.
        Does NOT raise — check the return value or self.errors.
        """
        self._errors = {}
        for attr_name, field in self._fields.items():
            value = getattr(self, attr_name)
            try:
                value = field.run_validators(value)
                method = getattr(self, f"validate_{attr_name}", None)
                if method is not None:
                    value = method(value)
                setattr(self, attr_name, value)
            except SignalValidationError as e:
                self._errors[attr_name] = str(e)
        return len(self._errors) == 0

    @property
    def fields(self) -> dict:
        """Access field descriptors by name — useful for template bindings.

        Example::

            {{ query_signals.fields.q.bind }}  → data-bind:filters.q
            {{ query_signals.fields.q.path }}  → filters.q
        """
        return self._fields

    def to_signals_dict(self) -> dict:
        """Reconstruct the nested signal dict from current field values.

        Useful for passing a schema instance to <c-lbr.signals :schema=s />.
        """
        result = {}
        for attr_name, field in self._fields.items():
            value = getattr(self, attr_name)
            parts = field.path.split(".")
            d = result
            for part in parts[:-1]:
                d = d.setdefault(part, {})
            d[parts[-1]] = value
        return result

    def patch(self, *field_names: str, only_if_missing: bool = False):
        """Return a DatastarEvent patching this schema's current signal values.

        No args → emit all fields.
        Named args → emit only those fields (no mutation).
        """
        from datastar_py import ServerSentEventGenerator as _DS

        if field_names:
            signals: dict = {}
            for name in field_names:
                field = self._fields[name]
                parts = field.path.split(".")
                d = signals
                for part in parts[:-1]:
                    d = d.setdefault(part, {})
                d[parts[-1]] = getattr(self, name)
        else:
            signals = self.to_signals_dict()
        return _DS.patch_signals(signals, only_if_missing=only_if_missing)

    @property
    def errors(self) -> dict[str, str]:
        return self._errors
