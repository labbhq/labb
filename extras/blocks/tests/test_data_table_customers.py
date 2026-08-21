"""
Integration tests for the lb/data-table/customers block — the catalogue's data-table anchor.

Drives the block through its preview URL in a real browser and asserts only what a
user can observe: the search filters, the sort reorders, the pager pages, an inline
edit persists, a bulk delete removes — and, the guarantee that makes this block
different from a markup table, that a reload after searching lands on the same view.

Arden's models carry explicit date fields (no auto_now_add), so the fixture supplies them.
"""

import datetime
from decimal import Decimal

import pytest

pytestmark = pytest.mark.django_db(transaction=True)

BASE = "/lb/data-table/customers/preview"

# Alphabetical, so page 1 (8 rows) ends at Halcyon Air and page 2 opens at Ironvale.
COMPANIES = [
    ("AtlasForge", "Dana Whitfield", "Manufacturing", 2927),
    ("Beacon Labs", "Mira Chen", "Software", 1180),
    ("Corvid Health", "Ola Ferreira", "Healthcare", 940),
    ("Dunmore Systems", "Petra Vance", "Logistics", 610),
    ("Ellery Foods", "Sam Okonjo", "Food", 380),
    ("Fenwick Media", "Tess Marlow", "Media", 275),
    ("Grayline Retail", "Uma Bright", "Retail", 1490),
    ("Halcyon Air", "Vic Aldana", "Travel", 820),
    ("Ironvale Group", "Wes Coburn", "Manufacturing", 3120),
    ("Kite & Bell", "Rosa Linden", "Retail", 555),
    ("Northwind Co", "Ivo Larsen", "Energy", 2040),
    ("Verity Labs", "Nadia Roth", "Research", 1675),
]


@pytest.fixture
def customers(db):
    from django.utils import timezone
    from lb.models import LbCustomer, LbInvoice, LbPlan, LbWorkspace

    plans = [
        LbPlan.objects.create(
            name="Arden Starter",
            slug="starter",
            tagline="For the first ten customers",
            price_monthly=49,
            price_yearly=490,
            seats_included=3,
        ),
        LbPlan.objects.create(
            name="Arden Growth",
            slug="growth",
            tagline="For teams finding their shape",
            price_monthly=149,
            price_yearly=1490,
            seats_included=10,
        ),
        LbPlan.objects.create(
            name="Arden Scale",
            slug="scale",
            tagline="For a real revenue org",
            price_monthly=449,
            price_yearly=4490,
            seats_included=25,
        ),
    ]
    workspace = LbWorkspace.objects.create(
        name="Beacon Labs",
        slug="beacon-labs",
        plan=plans[2],
        region="eu-west",
        currency="USD",
        billing_email="billing@beaconlabs.com",
        created_at=timezone.now(),
    )

    made = []
    for i, (company, contact, industry, mrr) in enumerate(COMPANIES):
        made.append(
            LbCustomer.objects.create(
                workspace=workspace,
                company=company,
                contact_name=contact,
                email=f"{contact.split()[0].lower()}@{company.split()[0].lower()}.com",
                plan=plans[i % 3],
                status="active" if i % 4 else "trial",
                health="at_risk" if i == 0 else "good",
                mrr=Decimal(mrr),
                seats=4 + i,
                industry=industry,
                country="United States",
                signed_up_on=datetime.date(2025, 3, 1) + datetime.timedelta(days=i * 7),
                renews_on=datetime.date(2026, 9, 1) + datetime.timedelta(days=i),
            )
        )

    atlas = made[0]
    LbInvoice.objects.create(
        customer=atlas,
        number="ARD-2026-0001",
        amount=Decimal(2927),
        status="paid",
        period="Jan 2026",
        issued_on=datetime.date(2026, 1, 18),
        due_on=datetime.date(2026, 2, 1),
        paid_on=datetime.date(2026, 1, 27),
    )
    LbInvoice.objects.create(
        customer=atlas,
        number="ARD-2026-0002",
        amount=Decimal(2927),
        status="overdue",
        period="Feb 2026",
        issued_on=datetime.date(2026, 2, 18),
        due_on=datetime.date(2026, 3, 1),
    )
    return made


def _rows(page):
    return page.locator("tbody tr")


def _search(page, term):
    box = page.locator('input[type="search"]')
    box.fill(term)
    box.dispatch_event("input")


# --- the block is a page, not a table (premium bar rule 2) -------------------


def test_table_loads_with_arden_framing_and_a_summary(page, live_server, customers):
    page.goto(f"{live_server.url}{BASE}/")

    assert page.locator("h1", has_text="Customers").is_visible()
    # The surrounding matter: a summary computed off the same queryset.
    assert page.locator("text=Monthly recurring").is_visible()
    assert page.locator("text=Overdue invoices").is_visible()
    assert page.locator(".stat-title", has_text="At risk").is_visible()
    assert _rows(page).count() == 8  # PAGE_SIZE


def test_block_is_arden_not_labb(page, live_server, customers):
    page.goto(f"{live_server.url}{BASE}/")

    body = page.locator("main").inner_text()
    assert "Arden" in body
    assert "labb" not in body.lower()


# --- search -----------------------------------------------------------------


def test_search_filters_the_table(page, live_server, customers):
    page.goto(f"{live_server.url}{BASE}/")
    _search(page, "atlas")

    page.wait_for_function("document.querySelectorAll('tbody tr').length === 1")
    assert page.locator("text=AtlasForge").first.is_visible()
    assert not page.locator("td", has_text="Kite & Bell").count()


def test_search_by_industry_finds_more_than_one(page, live_server, customers):
    page.goto(f"{live_server.url}{BASE}/")
    _search(page, "Manufacturing")

    page.wait_for_function("document.querySelectorAll('tbody tr').length === 2")


def test_search_recomputes_the_summary(page, live_server, customers):
    """Fat-morph: the stat strip is outside the table and updates in the same response."""
    page.goto(f"{live_server.url}{BASE}/")
    _search(page, "atlas")

    page.wait_for_function("document.querySelectorAll('tbody tr').length === 1")
    assert page.locator("text=$2,927").first.is_visible()


# --- replace-url: the state is shareable and survives a reload ---------------


def test_search_is_written_into_the_url(page, live_server, customers):
    page.goto(f"{live_server.url}{BASE}/")
    _search(page, "atlas")

    page.wait_for_function("location.search.includes('q=atlas')")
    assert "q=atlas" in page.url


def test_reload_after_searching_restores_the_filtered_view(
    page, live_server, customers
):
    page.goto(f"{live_server.url}{BASE}/")
    _search(page, "atlas")
    page.wait_for_function("location.search.includes('q=atlas')")

    page.reload()

    page.wait_for_selector("tbody tr")
    assert _rows(page).count() == 1
    assert page.locator("text=AtlasForge").first.is_visible()
    assert page.locator('input[type="search"]').input_value() == "atlas"


def test_a_shared_url_lands_on_the_same_view(page, live_server, customers):
    """The URL alone, with no signals in flight, rebuilds the view."""
    page.goto(f"{live_server.url}{BASE}/?lbr.sort.field=mrr&lbr.sort.dir=desc")

    page.wait_for_selector("tbody tr")
    assert "Ironvale Group" in _rows(page).first.inner_text()  # highest MRR


def test_sort_state_is_written_into_the_url(page, live_server, customers):
    page.goto(f"{live_server.url}{BASE}/")
    page.locator("thead").get_by_role("button", name="MRR").click()

    page.wait_for_function("location.search.includes('sort.field=mrr')")
    assert "lbr.sort.field=mrr" in page.url


# --- sort -------------------------------------------------------------------


def test_sort_reorders_the_rows(page, live_server, customers):
    page.goto(f"{live_server.url}{BASE}/")
    assert "AtlasForge" in _rows(page).first.inner_text()

    page.locator("thead").get_by_role("button", name="Customer").click()  # asc → desc

    page.wait_for_function(
        "document.querySelector('tbody tr').innerText.includes('Verity Labs')"
    )


# --- pagination -------------------------------------------------------------


def test_pagination_pages(page, live_server, customers):
    page.goto(f"{live_server.url}{BASE}/")
    assert page.locator("text=Page 1 of 2").is_visible()

    page.get_by_role("button", name="Next").click()

    page.wait_for_function(
        "document.querySelector('tbody tr').innerText.includes('Ironvale Group')"
    )
    assert _rows(page).count() == 4
    assert "page=2" in page.url


# --- inline edit ------------------------------------------------------------


def test_inline_edit_persists(page, live_server, customers):
    from lb.models import LbCustomer

    page.goto(f"{live_server.url}{BASE}/")
    page.get_by_role("button", name="Edit AtlasForge").click()

    page.wait_for_selector('input[name="contact_name"]')
    page.locator('input[name="contact_name"]').fill("Dana Whitfield-Reyes")
    page.locator('input[name="mrr"]').fill("3500")
    page.get_by_role("button", name="Save").click()

    page.wait_for_function("document.body.innerText.includes('Dana Whitfield-Reyes')")
    saved = LbCustomer.objects.get(company="AtlasForge")
    assert saved.contact_name == "Dana Whitfield-Reyes"
    assert saved.mrr == Decimal("3500")


def test_inline_edit_keeps_the_filtered_view(page, live_server, customers):
    """The filter survives a form POST.

    A form submit carries no signal bag, so the view has to recover the query
    state some other way. Currently it does not, and every row comes back.
    """
    page.goto(f"{live_server.url}{BASE}/?lbr.filters.q=atlas")
    page.get_by_role("button", name="Edit AtlasForge").click()

    page.wait_for_selector('input[name="contact_name"]')
    page.locator('input[name="contact_name"]').fill("Dana Reyes")
    page.get_by_role("button", name="Save").click()

    page.wait_for_function("document.body.innerText.includes('Dana Reyes')")
    assert _rows(page).count() == 1
    assert page.locator('input[type="search"]').input_value() == "atlas"


# --- bulk delete ------------------------------------------------------------


def test_bulk_delete_removes_the_selected_rows(page, live_server, customers):
    from lb.models import LbCustomer

    atlas, beacon = customers[0], customers[1]

    page.goto(f"{live_server.url}{BASE}/")
    page.locator(f"#customer-{atlas.pk} input[type='checkbox']").check()
    page.locator(f"#customer-{beacon.pk} input[type='checkbox']").check()

    page.get_by_role("button", name="Delete", exact=True).click()

    page.wait_for_function("!document.body.innerText.includes('AtlasForge')")
    assert not LbCustomer.objects.filter(pk__in=[atlas.pk, beacon.pk]).exists()
    assert LbCustomer.objects.count() == len(COMPANIES) - 2


# --- the empty state ships (premium bar rule 4) ------------------------------


def test_zero_results_shows_a_deliberate_empty_state(page, live_server, customers):
    page.goto(f"{live_server.url}{BASE}/")
    _search(page, "zzzzz")

    page.wait_for_selector("text=No customers match that filter")
    assert page.locator("button", has_text="Clear filters").is_visible()


def test_clearing_from_the_empty_state_brings_the_table_back(
    page, live_server, customers
):
    page.goto(f"{live_server.url}{BASE}/")
    _search(page, "zzzzz")
    page.wait_for_selector("text=No customers match that filter")

    page.get_by_role("button", name="Clear filters").click()

    page.wait_for_selector("tbody tr")
    assert _rows(page).count() == 8


# --- state the browser owns survives a morph --------------------------------


def _open_editor(page, company, value):
    page.get_by_role("button", name=f"Edit {company}").click()
    page.wait_for_selector('input[name="contact_name"]')
    field = page.locator('input[name="contact_name"]')
    field.fill(value)
    field.dispatch_event("input")
    return field


def test_an_unsaved_edit_survives_a_search(page, live_server, customers):
    """A morph that keeps the row on screen must not touch the open editor.

    Asserts the server sent no change blob. Checking the input alone passes on a
    broken server, since Datastar skips an attribute whose string did not change.
    """
    atlas = customers[0]
    page.goto(f"{live_server.url}{BASE}/")
    field = _open_editor(page, "AtlasForge", "Dana Reyes")

    _search(page, "atlas")  # AtlasForge stays, so the editor stays with it
    page.wait_for_function("document.querySelectorAll('tbody tr').length === 1")

    edit_signals = page.locator("#customer-edit-signals")
    assert edit_signals.get_attribute("data-signals") is None, (
        "the search response sent edit values the browser already owns"
    )
    assert edit_signals.get_attribute("data-signals__ifmissing") is not None
    assert field.input_value() == "Dana Reyes"
    atlas.refresh_from_db()
    assert atlas.contact_name != "Dana Reyes"  # still unsaved


def test_an_unsaved_edit_survives_the_row_leaving_the_page(
    page, live_server, customers
):
    """The buffer belongs to the row, not the page, so it survives the round trip."""
    page.goto(f"{live_server.url}{BASE}/")
    _open_editor(page, "AtlasForge", "Dana Reyes")

    sort = page.get_by_role("button", name="Customer", exact=True)
    sort.click()  # desc — AtlasForge off page 1
    page.wait_for_function("!document.body.innerText.includes('AtlasForge')")
    sort.click()  # asc — and back
    page.wait_for_selector('input[name="contact_name"]')

    assert page.locator('input[name="contact_name"]').input_value() == "Dana Reyes"


def test_editing_another_row_loads_that_row(page, live_server, customers):
    """The one case that must overwrite: the buffer belongs to another row."""
    page.goto(f"{live_server.url}{BASE}/")
    page.get_by_role("button", name="Edit AtlasForge").click()
    page.wait_for_selector('input[name="contact_name"]')
    page.locator('input[name="contact_name"]').fill("Dana Reyes")

    page.get_by_role("button", name="Edit Beacon Labs").click()
    page.wait_for_function(
        "document.querySelector('input[name=\"contact_name\"]')?.value === 'Mira Chen'"
    )


def test_select_all_tracks_the_rows_it_selected(page, live_server, customers):
    page.goto(f"{live_server.url}{BASE}/")
    header = page.locator("thead input[type='checkbox']")
    rows = page.locator("tbody input[type='checkbox']")

    header.check()
    page.wait_for_timeout(200)
    assert rows.count() == 8
    for i in range(rows.count()):
        assert rows.nth(i).is_checked()

    rows.nth(0).uncheck()
    page.wait_for_timeout(200)
    assert not header.is_checked()
    assert header.evaluate("el => el.indeterminate")


def test_deleting_a_row_drops_it_from_the_selection(page, live_server, customers):
    """A deleted row must stop counting towards the selection."""
    atlas, beacon = customers[0], customers[1]
    page.goto(f"{live_server.url}{BASE}/")
    page.locator(f"#customer-{atlas.pk} input[type='checkbox']").check()
    page.locator(f"#customer-{beacon.pk} input[type='checkbox']").check()

    count = page.locator("text=selected")
    assert count.inner_text().strip() == "2 selected"

    page.get_by_role("button", name="Delete", exact=True).click()
    page.wait_for_function("!document.body.innerText.includes('AtlasForge')")

    # The rows are gone either way, so checkboxes prove nothing; the toolbar does.
    assert not count.is_visible()
    assert page.locator("tbody input[type='checkbox']:checked").count() == 0
