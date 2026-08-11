"""Session setup for the labbdocs suite.

The search tests need two things the rest of the suite does not: a PostgreSQL
server, and the docs build output that `build_search_index` reads. Postgres is
probed once in tests/settings.py; when it is missing the search app is left out
of INSTALLED_APPS and its tests are dropped here, with tests/test_search_suite.py
reporting the reason as a skip. Everything else still runs, so a developer
without Postgres gets a green run.
"""

from pathlib import Path

import pytest
from django.conf import settings

SEARCH_TESTS = Path(__file__).resolve().parent / "labbdocs" / "search" / "tests"

# Importing these modules pulls in labbdocs.search models, which need the app
# registry, which needs the driver. Drop them before import, not at run time.
collect_ignore_glob = (
    [str(SEARCH_TESTS / "*.py")] if settings.SEARCH_SKIP_REASON else []
)


def pytest_report_header(config):
    reason = settings.SEARCH_SKIP_REASON
    return f"labbdocs search: {reason or 'enabled'}"


def _is_search_test(item):
    return SEARCH_TESTS in Path(str(item.fspath)).parents


@pytest.fixture(scope="session", autouse=True)
def built_docs(request):
    """Build every declared doc type once, into the throwaway build directory.

    `build_search_index` reads the built configs, and the docs pages the search
    tests fetch are built templates. Nothing else in the suite needs them, so
    the build is skipped when no search test will run.
    """
    if settings.SEARCH_SKIP_REASON:
        return
    if not any(_is_search_test(item) for item in request.session.items):
        return

    from django.core.management import call_command

    settings.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    for name in settings.LABB_DOCS["types"]:
        call_command("build_docs", name, "--quiet")
