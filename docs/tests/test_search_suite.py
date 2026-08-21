"""Makes the search suite's absence visible.

Without this, a run with no PostgreSQL would quietly collect nothing from
labbdocs/search/tests and look identical to a run where search passed.
"""

from django.conf import settings


def test_search_suite_ran():
    if settings.SEARCH_SKIP_REASON:
        import pytest

        pytest.skip(settings.SEARCH_SKIP_REASON)
    assert "labbdocs.search" in settings.INSTALLED_APPS
