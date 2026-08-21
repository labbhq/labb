"""`search_report` — the read surface for the query log, and its purge."""

from datetime import timedelta
from io import StringIO

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from ..models import SearchQueryLog


def _log_queries(enabled):
    docs = {**(getattr(settings, "LABB_DOCS", None) or {})}
    docs["search"] = {**(docs.get("search") or {}), "log_queries": enabled}
    return override_settings(LABB_DOCS=docs)


def _run(**kwargs):
    out = StringIO()
    call_command("search_report", stdout=out, **kwargs)
    return out.getvalue()


class SearchReportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        SearchQueryLog.objects.create(query="button", result_count=12, has_results=True)
        SearchQueryLog.objects.create(query="button", result_count=12, has_results=True)
        SearchQueryLog.objects.create(query="chart", result_count=3, has_results=True)
        SearchQueryLog.objects.create(
            query="datepicker", result_count=0, has_results=False
        )
        SearchQueryLog.objects.create(
            query="datepicker", result_count=0, has_results=False
        )
        SearchQueryLog.objects.create(query="toast", result_count=0, has_results=False)

    def test_reports_top_queries_most_frequent_first(self):
        output = _run()
        self.assertIn("Top queries", output)
        self.assertLess(output.index("button"), output.index("chart"))

    def test_zero_result_section_lists_only_misses(self):
        output = _run()
        zero_section = output[output.index("Zero results") :]
        self.assertIn("datepicker", zero_section)
        self.assertIn("toast", zero_section)
        self.assertNotIn("chart", zero_section)

    def test_zero_result_share_is_reported(self):
        # 3 of 6 logged searches found nothing.
        self.assertIn("3 queries, 50%", _run())

    def test_window_excludes_older_rows(self):
        SearchQueryLog.objects.all().update(created=timezone.now() - timedelta(days=90))
        self.assertIn("No searches logged", _run(days=30))


class PurgeTests(TestCase):
    def test_purge_deletes_only_rows_past_the_cutoff(self):
        old = SearchQueryLog.objects.create(
            query="old", result_count=0, has_results=False
        )
        SearchQueryLog.objects.filter(pk=old.pk).update(
            created=timezone.now() - timedelta(days=120)
        )
        SearchQueryLog.objects.create(query="new", result_count=1, has_results=True)

        output = _run(purge_older_than=90)

        self.assertIn("Purged 1 log rows", output)
        self.assertEqual(
            list(SearchQueryLog.objects.values_list("query", flat=True)), ["new"]
        )

    def test_purge_on_empty_table_is_harmless(self):
        self.assertIn("Purged 0 log rows", _run(purge_older_than=30))


@_log_queries(False)
class LoggingOffTests(TestCase):
    def test_explains_why_there_is_nothing_to_report(self):
        output = _run()
        self.assertIn("log_queries", output)
        self.assertNotIn("Traceback", output)


@_log_queries(True)
class EmptyLogTests(TestCase):
    def test_empty_table_with_logging_on_says_so(self):
        self.assertIn("No searches logged", _run())
