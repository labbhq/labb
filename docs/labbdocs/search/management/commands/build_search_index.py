"""Rebuild the search index: truncate + reinsert every source, then bulk-populate
the FTS vectors and trigram names. Idempotent — safe to re-run on every deploy.
"""

from collections import Counter

from django.contrib.postgres.search import SearchVector
from django.core.management.base import BaseCommand

from ...models import SearchDocument
from ...readers import all_readers


class Command(BaseCommand):
    help = "Rebuild the search index from all registered readers (truncate + reinsert)."

    def handle(self, *args, **options):
        # 1. Truncate — a rebuild is a full replace, so re-running never dupes.
        SearchDocument.objects.all().delete()

        # 2. Insert rows from every reader.
        docs = []
        for reader in all_readers():
            for row in reader.read():
                doc = SearchDocument(**row)
                doc.search_name = f"{doc.title} {doc.keywords}".strip().lower()
                docs.append(doc)

        SearchDocument.objects.bulk_create(docs)

        # 3. Bulk-populate the weighted FTS vector after insert.
        SearchDocument.objects.update(
            search_vector=(
                SearchVector("title", weight="A", config="english")
                + SearchVector("keywords", weight="B", config="english")
                + SearchVector("category", weight="C", config="english")
                + SearchVector("summary", weight="C", config="english")
                + SearchVector("body", weight="D", config="english")
            )
        )

        # 4. Report per-type counts.
        counts = Counter(doc.type for doc in docs)
        total = len(docs)
        self.stdout.write(self.style.SUCCESS(f"Indexed {total} documents:"))
        for doc_type, count in sorted(counts.items()):
            self.stdout.write(f"  {doc_type}: {count}")
        if not total:
            self.stdout.write("  (no documents)")
