from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models


class SearchDocument(models.Model):
    """One polymorphic row per indexed item, discriminated by `type`.

    Populated (truncate + reinsert) by the `build_search_index` command from a
    reader per source. `search_vector` (weighted FTS) and `search_name`
    (lowercased title+keywords, for trigram fuzzy/prefix) are bulk-computed
    after insert — the index is static between builds, so no triggers.
    """

    TYPE_GUIDE = "guide"
    TYPE_COMPONENT = "component"
    TYPE_ICON = "icon"
    TYPE_BLOCK = "block"
    TYPE_CHOICES = [
        (TYPE_GUIDE, "Guide"),
        (TYPE_COMPONENT, "Component"),
        (TYPE_ICON, "Icon"),
        (TYPE_BLOCK, "Block"),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    category = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    keywords = models.TextField(blank=True)
    body = models.TextField(blank=True)
    url = models.CharField(max_length=500)
    weight = models.FloatField(default=0)
    metadata = models.JSONField(default=dict)

    search_vector = SearchVectorField(null=True)
    search_name = models.TextField(blank=True)

    class Meta:
        indexes = [
            GinIndex(fields=["search_vector"]),
            GinIndex(
                fields=["search_name"],
                name="search_name_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ]

    def __str__(self):
        return f"{self.type}: {self.title}"


class SearchQueryLog(models.Model):
    """One row per executed search request. Zero PII by design: the raw query
    text, its result count, and a timestamp — no IP, no user, no session."""

    query = models.CharField(max_length=255)
    result_count = models.PositiveIntegerField()
    has_results = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["has_results", "created"]),
        ]

    def __str__(self):
        return f"{self.query!r} ({self.result_count})"
