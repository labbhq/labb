"""Search analytics — one privacy-safe SearchQueryLog row per executed search,
and only when the consumer opts in. Zero PII by design: query text, result
count, timestamp only."""

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from ..models import SearchQueryLog


def _log_queries(enabled):
    """override_settings for LABB_DOCS["search"]["log_queries"], preserving the
    rest of the dict (the readers list in particular)."""
    docs = {**(getattr(settings, "LABB_DOCS", None) or {})}
    docs["search"] = {**(docs.get("search") or {}), "log_queries": enabled}
    return override_settings(LABB_DOCS=docs)


@_log_queries(True)
class SearchAnalyticsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("build_search_index")

    def _get(self, q=None):
        params = {"q": q} if q is not None else {}
        return self.client.get(reverse("labbdocs_search:page"), params)

    def test_query_with_results_logs_one_row(self):
        self._get("button")
        logs = SearchQueryLog.objects.all()
        self.assertEqual(logs.count(), 1)
        log = logs.first()
        self.assertEqual(log.query, "button")
        self.assertTrue(log.has_results)
        self.assertGreater(log.result_count, 0)

    def test_no_results_query_logs_zero_count(self):
        self._get("zzzzznotathing")
        log = SearchQueryLog.objects.get(query="zzzzznotathing")
        self.assertFalse(log.has_results)
        self.assertEqual(log.result_count, 0)

    def test_blank_query_logs_nothing(self):
        self._get("")
        self.assertEqual(SearchQueryLog.objects.count(), 0)

    def test_no_query_param_logs_nothing(self):
        self._get()
        self.assertEqual(SearchQueryLog.objects.count(), 0)

    def test_no_pii_fields(self):
        names = {f.name for f in SearchQueryLog._meta.get_fields()}
        for banned in ("ip", "ip_address", "user", "session", "session_key"):
            self.assertNotIn(banned, names)


@_log_queries(False)
class LoggingDisabledTests(TestCase):
    """The shipped default. A consumer who never opts in collects nothing."""

    @classmethod
    def setUpTestData(cls):
        call_command("build_search_index")

    def test_query_logs_nothing_when_disabled(self):
        self.client.get(reverse("labbdocs_search:page"), {"q": "button"})
        self.assertEqual(SearchQueryLog.objects.count(), 0)

    def test_search_still_returns_results_when_disabled(self):
        response = self.client.get(reverse("labbdocs_search:page"), {"q": "button"})
        self.assertEqual(response.status_code, 200)
