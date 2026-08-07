"""Command seam — invariants not observable through the search HTTP path:
idempotency and per-source population, built over the REAL ui.yaml corpus.
"""

from django.core.management import call_command
from django.db.models import Count
from django.test import TestCase

from ..models import SearchDocument


class BuildSearchIndexTests(TestCase):
    def setUp(self):
        call_command("build_search_index")

    def test_component_rows_are_indexed(self):
        count = SearchDocument.objects.filter(
            type=SearchDocument.TYPE_COMPONENT
        ).count()
        self.assertGreater(count, 0)

    def test_rebuild_is_idempotent(self):
        # Truncate + reinsert: a rebuild reproduces the same corpus exactly,
        # both in total and per type (no rows lost, none duplicated).
        before = SearchDocument.objects.count()
        before_by_type = dict(
            SearchDocument.objects.values_list("type").annotate(n=Count("id"))
        )
        call_command("build_search_index")
        after = SearchDocument.objects.count()
        after_by_type = dict(
            SearchDocument.objects.values_list("type").annotate(n=Count("id"))
        )
        self.assertEqual(before, after)
        self.assertEqual(before_by_type, after_by_type)

    def test_button_component_row_exists(self):
        button = SearchDocument.objects.filter(
            type=SearchDocument.TYPE_COMPONENT, title="Button"
        ).first()
        self.assertIsNotNone(button)
        self.assertEqual(button.type, SearchDocument.TYPE_COMPONENT)
        self.assertIn("/docs/ui/", button.url)
        self.assertIn("button", button.url)
        # Enriched keywords carry the tag + prop/variant names.
        self.assertIn("c-lb.button", button.keywords)
        self.assertIn("variant", button.keywords)
        self.assertIn("primary", button.keywords)

    def test_search_name_is_populated(self):
        button = SearchDocument.objects.get(
            type=SearchDocument.TYPE_COMPONENT, title="Button"
        )
        self.assertTrue(button.search_name)
        self.assertEqual(button.search_name, button.search_name.lower())
