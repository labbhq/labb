from typing import Iterable, Protocol


class Reader(Protocol):
    """A content source for the search index.

    Each reader yields plain row dicts ready for ``SearchDocument(**row)``
    (minus the vector fields — `search_vector`/`search_name` are computed by the
    build command after insert). A row dict carries: ``type``, ``category``,
    ``title``, ``summary``, ``keywords``, ``body``, ``url``, ``weight``,
    ``metadata``. Only ``type``, ``title`` and ``url`` are required; the rest
    default sensibly on the model.
    """

    def read(self) -> Iterable[dict]: ...
