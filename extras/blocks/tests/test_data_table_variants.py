"""
Integration tests for the four `fe` variants on the lb/data-table surface.

The anchor on this surface (`data-table/customers`) is a fullstack CRUD table. These
four give a developer the same design language with no migration in their project, so
the claims under test are about what they do *not* need:

1. `with-filters` narrows the rows from a client signal with **no network request**.
2. `expandable-rows` opens a detail panel in place from a client signal, also silent.
3. `compact` and `card-grid` emit **no script[src] at all**.
4. Each block ships an empty state that actually renders.

Assertions target ids and row counts, never copy that another block might share — a
string that exists on two pages would give a false green.
"""

import pytest

pytestmark = pytest.mark.django_db(transaction=True)

COMPACT = "/lb/data-table/compact/preview/"
FILTERS = "/lb/data-table/with-filters/preview/"
CARDS = "/lb/data-table/card-grid/preview/"
EXPANDO = "/lb/data-table/expandable-rows/preview/"

DATASTAR = 'script[src*="datastar.js"]'

ALL_BLOCKS = [COMPACT, FILTERS, CARDS, EXPANDO]


def _watch_requests(page):
    """Record every request the page fires from now on (favicon excluded)."""
    seen = []
    page.on("request", lambda r: seen.append(r.url))
    return seen


def _fired(seen):
    return [u for u in seen if "favicon" not in u]


# --- compact: dense rows, no JavaScript ------------------------------------


def test_compact_renders_every_account_densely(page, live_server):
    page.goto(f"{live_server.url}{COMPACT}")

    assert page.locator("#compact-rows tr").count() == 8
    assert page.locator("#compact-row-1").inner_text().startswith("AF")
    assert page.locator("#compact-metrics").is_visible()


def test_compact_ships_no_javascript_at_all(page, live_server):
    """Static by default: nothing on this page is reactive, so nothing loads."""
    page.goto(f"{live_server.url}{COMPACT}")

    assert page.locator("script[src]").count() == 0


def test_compact_empty_state_renders(page, live_server):
    """The overdue panel has nothing in it, and says so on purpose."""
    page.goto(f"{live_server.url}{COMPACT}")

    empty = page.locator("#compact-attention-empty")
    assert empty.is_visible()
    assert "Nothing overdue" in empty.inner_text()


# --- card-grid: the same records as cards, no JavaScript --------------------


def test_card_grid_renders_a_card_per_account(page, live_server):
    page.goto(f"{live_server.url}{CARDS}")

    assert page.locator("#account-grid > *").count() == 8
    assert page.locator("#account-card-ig").is_visible()
    assert "6,720" in page.locator("#account-card-ig").inner_text()


def test_card_grid_ships_no_javascript_at_all(page, live_server):
    page.goto(f"{live_server.url}{CARDS}")

    assert page.locator("script[src]").count() == 0


def test_card_grid_empty_state_renders(page, live_server):
    page.goto(f"{live_server.url}{CARDS}")

    empty = page.locator("#flagged-empty")
    assert empty.is_visible()
    assert "No account flagged this week" in empty.inner_text()


# --- with-filters: chips narrow the table, with zero server -----------------


def test_filters_start_unfiltered(page, live_server):
    page.goto(f"{live_server.url}{FILTERS}")
    page.wait_for_selector(DATASTAR, state="attached")

    assert page.locator("#filter-rows tr:visible").count() == 8
    assert page.locator("#filter-empty").is_hidden()


def test_filter_chip_narrows_the_rows_with_no_network_request(page, live_server):
    """The whole point of the block: eight rows become one, and the wire stays silent."""
    page.goto(f"{live_server.url}{FILTERS}")
    page.wait_for_selector(DATASTAR, state="attached")
    page.locator("#filter-row-af").wait_for()

    seen = _watch_requests(page)
    page.locator("#chip-status-trial").click()

    page.wait_for_function("document.querySelectorAll('#filter-rows tr:not([style*=\"none\"])').length === 1")
    assert page.locator("#filter-rows tr:visible").count() == 1
    assert page.locator("#filter-row-nc").is_visible()
    assert page.locator("#filter-row-af").is_hidden()
    assert _fired(seen) == [], f"expected zero requests, got {_fired(seen)}"


def test_two_chips_intersect(page, live_server):
    page.goto(f"{live_server.url}{FILTERS}")
    page.wait_for_selector(DATASTAR, state="attached")

    page.locator("#chip-status-active").click()
    page.locator("#chip-health-watch").click()

    page.wait_for_function("document.querySelectorAll('#filter-rows tr:not([style*=\"none\"])').length === 2")
    assert page.locator("#filter-row-kb").is_visible()
    assert page.locator("#filter-row-hf").is_visible()
    assert page.locator("#filter-row-af").is_hidden()


def test_filters_zero_result_shows_the_empty_state_and_recovers(page, live_server):
    """Churned accounts are all at risk, so Churned + Watch is a real dead end."""
    page.goto(f"{live_server.url}{FILTERS}")
    page.wait_for_selector(DATASTAR, state="attached")

    seen = _watch_requests(page)
    page.locator("#chip-status-churned").click()
    page.locator("#chip-health-watch").click()

    page.wait_for_selector("#filter-empty", state="visible")
    assert page.locator("#filter-rows tr:visible").count() == 0
    assert page.locator("#filter-empty").is_visible()

    page.locator("#filter-empty button").click()
    page.wait_for_function("document.querySelectorAll('#filter-rows tr:not([style*=\"none\"])').length === 8")
    assert page.locator("#filter-empty").is_hidden()
    assert _fired(seen) == [], f"expected zero requests, got {_fired(seen)}"


def test_filter_badge_is_a_reactive_prop(page, live_server):
    """`variant="$filters.tone:neutral"` — labb recomputes the daisyUI class in the browser."""
    page.goto(f"{live_server.url}{FILTERS}")
    page.wait_for_selector(DATASTAR, state="attached")

    page.locator("#chip-status-active").click()
    page.wait_for_function(
        "document.getElementById('filter-tone').className.includes('badge-primary')"
    )
    assert page.locator("#filter-tone").inner_text() == "Filtered"
    assert "5 of 8 shown" in page.locator("#filter-count").inner_text()


# --- expandable-rows: a detail panel, in place ------------------------------


def test_rows_start_collapsed(page, live_server):
    page.goto(f"{live_server.url}{EXPANDO}")
    page.wait_for_selector(DATASTAR, state="attached")

    assert page.locator("#expando-row-1").is_visible()
    assert page.locator("#expando-detail-1").is_hidden()


def test_row_expands_in_place_with_no_network_request(page, live_server):
    page.goto(f"{live_server.url}{EXPANDO}")
    page.wait_for_selector(DATASTAR, state="attached")
    page.locator("#expando-row-1").wait_for()

    seen = _watch_requests(page)
    page.locator("#expando-row-1").click()

    page.wait_for_selector("#expando-detail-1", state="visible")
    detail = page.locator("#expando-detail-1")
    assert "INV-2041" in detail.inner_text()
    assert "Dara Osei" in detail.inner_text()
    assert _fired(seen) == [], f"expected zero requests, got {_fired(seen)}"


def test_opening_a_second_row_closes_the_first(page, live_server):
    """One integer signal holds the open id, so the accordion comes for free."""
    page.goto(f"{live_server.url}{EXPANDO}")
    page.wait_for_selector(DATASTAR, state="attached")

    page.locator("#expando-row-1").click()
    page.wait_for_selector("#expando-detail-1", state="visible")

    page.locator("#expando-row-5").click()
    page.wait_for_selector("#expando-detail-5", state="visible")
    assert page.locator("#expando-detail-1").is_hidden()
    assert "INV-2038" in page.locator("#expando-detail-5").inner_text()


def test_clicking_an_open_row_closes_it(page, live_server):
    page.goto(f"{live_server.url}{EXPANDO}")
    page.wait_for_selector(DATASTAR, state="attached")

    page.locator("#expando-row-1").click()
    page.wait_for_selector("#expando-detail-1", state="visible")

    page.locator("#expando-row-1").click()
    page.wait_for_selector("#expando-detail-1", state="hidden")
    assert page.locator("#expando-detail-1").is_hidden()


def test_expando_empty_state_renders_inside_the_panel(page, live_server):
    """Northwind Co is on trial, so its invoice list is a state, not an empty box."""
    page.goto(f"{live_server.url}{EXPANDO}")
    page.wait_for_selector(DATASTAR, state="attached")

    page.locator("#expando-row-3").click()
    page.wait_for_selector("#expando-invoices-empty-3", state="visible")

    empty = page.locator("#expando-invoices-empty-3")
    assert empty.is_visible()
    assert "No invoices yet" in empty.inner_text()


# --- the catalogue rule: these are Arden's blocks, not labb's ---------------


@pytest.mark.parametrize("url", ALL_BLOCKS)
def test_block_is_not_labb_centric(page, live_server, url):
    page.goto(f"{live_server.url}{url}")

    body = page.locator("main").inner_text()
    assert "Arden" in body
    assert "labb" not in body.lower()
