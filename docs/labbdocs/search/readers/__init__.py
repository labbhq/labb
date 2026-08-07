"""Reader registry for the search index.

Each reader reads one content source and yields row dicts for
``SearchDocument``. Readers are named explicitly as dotted paths in
``LABB_DOCS["search"]["readers"]``, defaulting to the three labbdocs ships
(``conf.DEFAULT_READERS``) — so adding a source and disabling a shipped one are
the same edit, and the whole index composition is visible in one place.

To add a source: write a class with a ``.read()`` method (see ``base.Reader``)
anywhere importable, and name it in that list.
"""

from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from ..conf import reader_paths
from .base import Reader


def all_readers():
    """Instantiate every configured reader, in the order listed.

    A path that will not import is a configuration error, not a bad day for one
    source — a typo silently costing an entire content type is the failure
    nobody notices. Errors *inside* ``read()`` stay tolerant; see the build
    command.
    """
    readers = []
    for path in reader_paths():
        try:
            reader_class = import_string(path)
        except ImportError as exc:
            raise ImproperlyConfigured(
                f'LABB_DOCS["search"]["readers"] cannot import {path!r}: {exc}'
            ) from exc
        readers.append(reader_class())
    return readers


__all__ = ["Reader", "all_readers"]
