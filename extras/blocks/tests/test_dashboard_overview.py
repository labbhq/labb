"""
Integration tests for the lb/dashboard/overview block — the catalogue's dashboard anchor.

Drives the block through its preview URL in a real browser and asserts only what a
user (or Chart.js) can observe: the charts render from signals, switching the series
redraws them off a normal Django view, the theme switch recolours them, and the live
metric streams in over SSE.
"""

import datetime

import pytest

pytestmark = pytest.mark.django_db(transaction=True)

BASE = "/lb/dashboard/overview/preview"

# The chart instance Chart.js holds for a given wrapper id — the only honest way to
# assert a canvas actually redrew.
CHART_DATASET = """
(id) => {
    const canvas = document.querySelector('#' + id + ' canvas');
    const chart = canvas && window.Chart && window.Chart.getChart(canvas);
    if (!chart) return null;
    return {
        label: chart.data.datasets[0].label,
        colour: String(chart.data.datasets[0].backgroundColor),
        points: chart.data.datasets[0].data.length,
    };
}
"""


@pytest.fixture
def arden(db):
    from django.utils import timezone
    from lb.models import LbCustomer, LbEvent, LbInvoice, LbMember, LbPlan, LbWorkspace

    growth = LbPlan.objects.create(
        name="Arden Growth",
        slug="growth",
        tagline="For revenue teams",
        price_monthly=149,
        price_yearly=1490,
        seats_included=10,
        is_featured=True,
    )
    scale = LbPlan.objects.create(
        name="Arden Scale",
        slug="scale",
        tagline="For RevOps",
        price_monthly=449,
        price_yearly=4490,
        seats_included=25,
    )
    workspace = LbWorkspace.objects.create(
        name="Beacon Labs",
        slug="beacon-labs",
        plan=scale,
        region="eu-west-1",
        currency="USD",
        billing_email="billing@beaconlabs.com",
        created_at=timezone.now(),
    )
    LbMember.objects.create(
        workspace=workspace,
        name="Mira Chen",
        email="mira@beaconlabs.com",
        title="Founder",
        role="owner",
        status="active",
        joined_on=datetime.date(2024, 1, 12),
        last_active_at=timezone.now(),
    )

    def customer(company, contact, mrr, status, health, plan, signed_up, renews):
        return LbCustomer.objects.create(
            workspace=workspace,
            company=company,
            contact_name=contact,
            email=f"{contact.split()[0].lower()}@example.com",
            plan=plan,
            status=status,
            health=health,
            mrr=mrr,
            seats=12,
            industry="Software",
            country="United States",
            signed_up_on=signed_up,
            renews_on=renews,
        )

    atlas = customer(
        "AtlasForge",
        "Dana Whitfield",
        2927,
        "active",
        "good",
        scale,
        datetime.date(2023, 4, 18),
        datetime.date(2026, 8, 18),
    )
    kite = customer(
        "Kite & Bell",
        "Rosa Linden",
        555,
        "active",
        "good",
        growth,
        datetime.date(2024, 6, 2),
        datetime.date(2026, 8, 2),
    )
    northwind = customer(
        "Northwind Co",
        "Peter Vance",
        2278,
        "active",
        "watch",
        scale,
        datetime.date(2025, 7, 25),
        datetime.date(2026, 8, 25),
    )
    oakhurst = customer(
        "Oakhurst Retail",
        "Nina Oakhurst",
        381,
        "past_due",
        "at_risk",
        growth,
        datetime.date(2025, 3, 9),
        datetime.date(2026, 8, 22),
    )
    customer(
        "Rookwood Interactive",
        "Sam Rookwood",
        0,
        "churned",
        "at_risk",
        growth,
        datetime.date(2024, 2, 14),
        None,
    )

    def invoice(cust, number, amount, status, issued, paid=None):
        return LbInvoice.objects.create(
            customer=cust,
            number=number,
            amount=amount,
            currency="USD",
            status=status,
            period=issued.strftime("%b %Y"),
            issued_on=issued,
            due_on=issued + datetime.timedelta(days=14),
            paid_on=paid,
        )

    invoice(
        atlas,
        "ARD-2026-0001",
        2927,
        "paid",
        datetime.date(2026, 1, 18),
        datetime.date(2026, 1, 27),
    )
    invoice(
        kite,
        "ARD-2026-0002",
        555,
        "paid",
        datetime.date(2026, 1, 20),
        datetime.date(2026, 1, 25),
    )
    invoice(
        atlas,
        "ARD-2026-0003",
        2927,
        "paid",
        datetime.date(2026, 2, 18),
        datetime.date(2026, 2, 21),
    )
    invoice(
        northwind,
        "ARD-2026-0004",
        2278,
        "paid",
        datetime.date(2026, 2, 19),
        datetime.date(2026, 2, 26),
    )
    invoice(
        atlas,
        "ARD-2026-0005",
        3045,
        "paid",
        datetime.date(2026, 3, 18),
        datetime.date(2026, 3, 23),
    )
    invoice(oakhurst, "ARD-2026-0006", 381, "open", datetime.date(2026, 3, 20))
    invoice(kite, "ARD-2026-0007", 555, "open", datetime.date(2026, 3, 21))
    invoice(northwind, "ARD-2026-0008", 2278, "open", datetime.date(2026, 3, 22))

    LbEvent.objects.create(
        workspace=workspace,
        customer=kite,
        kind="upgrade",
        label="Kite & Bell moved to Arden Growth",
        mrr_delta=410,
        occurred_at=datetime.datetime(2026, 3, 4, 11, 20, tzinfo=datetime.timezone.utc),
    )
    LbEvent.objects.create(
        workspace=workspace,
        customer=oakhurst,
        kind="downgrade",
        label="Oakhurst Retail dropped 4 seats",
        mrr_delta=-172,
        occurred_at=datetime.datetime(2026, 3, 8, 9, 5, tzinfo=datetime.timezone.utc),
    )
    LbEvent.objects.create(
        workspace=workspace,
        customer=atlas,
        kind="payment",
        label="AtlasForge paid $2,927.00",
        mrr_delta=0,
        occurred_at=datetime.datetime(
            2026, 3, 12, 15, 40, tzinfo=datetime.timezone.utc
        ),
    )
    return workspace


def _dataset(page, chart_id):
    return page.evaluate(CHART_DATASET, chart_id)


# --- the page (premium bar rule 2: there is more here than the charts) ------


def test_overview_loads_with_the_book_of_business(page, live_server, arden):
    page.goto(f"{live_server.url}{BASE}/")

    assert "Revenue overview" in page.title()
    assert page.locator("text=Beacon Labs").first.is_visible()
    # MRR of the three active accounts: 2927 + 555 + 2278.
    assert page.locator("text=$5,760").first.is_visible()
    assert page.locator("text=Logo churn").is_visible()


def test_overview_carries_more_than_charts(page, live_server, arden):
    """The watchlist and the movement feed are the surrounding matter."""
    page.goto(f"{live_server.url}{BASE}/")

    assert page.locator("text=Accounts to watch").is_visible()
    assert page.locator("text=Oakhurst Retail").first.is_visible()
    assert page.locator("text=Past due").first.is_visible()
    assert page.locator("text=Northwind Co").first.is_visible()
    assert page.locator("text=Kite & Bell moved to Arden Growth").is_visible()


def test_block_is_not_labb_centric(page, live_server, arden):
    page.goto(f"{live_server.url}{BASE}/")

    body = page.locator("main").inner_text()
    assert "Arden" in body
    assert "labb" not in body.lower()


# --- charts render from signals --------------------------------------------


def test_all_three_charts_render(page, live_server, arden):
    page.goto(f"{live_server.url}{BASE}/")
    page.wait_for_function(
        "() => window.Chart && document.querySelectorAll('canvas').length === 3"
    )

    revenue = _dataset(page, "revenue-chart")
    assert revenue["label"] == "Collected"
    assert revenue["points"] == 3  # Jan, Feb, Mar 2026

    assert _dataset(page, "cohort-chart")["label"] == "Still paying (%)"
    assert _dataset(page, "plan-chart")["label"] == "MRR"


def test_switching_series_redraws_the_chart(page, live_server, arden):
    """The button sets a signal, the view rebuilds the series, the chart morphs."""
    page.goto(f"{live_server.url}{BASE}/")
    page.wait_for_function(
        "() => window.Chart && window.Chart.getChart(document.querySelector('#revenue-chart canvas'))"
    )
    assert _dataset(page, "revenue-chart")["label"] == "Collected"

    page.locator("#series-movement").click()

    page.wait_for_function(
        "() => { const c = window.Chart.getChart(document.querySelector('#revenue-chart canvas'));"
        " return c && c.data.datasets[0].label === 'New and expansion'; }"
    )
    assert _dataset(page, "revenue-chart")["label"] == "New and expansion"


# --- live theming ------------------------------------------------------------


def test_theme_switch_recolours_the_charts(page, live_server, arden):
    page.goto(f"{live_server.url}{BASE}/")
    page.wait_for_function(
        "() => window.Chart && window.Chart.getChart(document.querySelector('#revenue-chart canvas'))"
    )
    before = _dataset(page, "revenue-chart")["colour"]

    page.locator("#theme-toggle").click()

    page.wait_for_function(
        "(before) => { const c = window.Chart.getChart(document.querySelector('#revenue-chart canvas'));"
        " return c && String(c.data.datasets[0].backgroundColor) !== before; }",
        arg=before,
    )
    after = _dataset(page, "revenue-chart")["colour"]
    assert after != before
    assert "#" not in after  # resolved from a theme token, not a fixed hex


# --- the SSE metric ----------------------------------------------------------


def test_collected_today_streams_in(page, live_server, arden):
    page.goto(f"{live_server.url}{BASE}/")
    assert page.locator("#collected-today").is_visible()

    # The open invoices settle one per tick: 381 + 555 + 2278 = $3,214.
    page.wait_for_function(
        "() => document.querySelector('#collected-today').textContent.trim() === '$3,214'"
    )
    assert page.locator("text=3 invoices settled").is_visible()


def test_streamed_metric_survives_a_series_switch(page, live_server, arden):
    """The live signals are declared apart from the chart signals, so a morph
    that rewrites the charts must not wind the streamed total back to zero."""
    page.goto(f"{live_server.url}{BASE}/")
    page.wait_for_function(
        "() => document.querySelector('#collected-today').textContent.trim() === '$3,214'"
    )

    page.locator("#series-movement").click()
    page.wait_for_function(
        "() => { const c = window.Chart.getChart(document.querySelector('#revenue-chart canvas'));"
        " return c && c.data.datasets[0].label === 'New and expansion'; }"
    )

    assert page.locator("#collected-today").inner_text().strip() == "$3,214"
