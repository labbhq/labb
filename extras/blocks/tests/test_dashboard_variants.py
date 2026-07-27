"""
Integration tests for the four lb/dashboard/* variants that sit beside the overview anchor.

Three of them are static, and one is not — which is the claim the surface is making:

1. `compact-kpi`, `activity-feed` and `first-run` ship **no script[src] at all**. A
   dashboard is the page people assume must be a SPA; these three are HTML.
2. `split-charts` redraws three Chart.js charts from a client signal with **zero network
   requests**. Chart labels live on the canvas, never in the DOM, so the assertion reads
   `window.Chart.getChart(canvas).data` rather than the page text.
3. `first-run` reads as a designed empty state — the CTA, the reason and the setup path
   all render.

Assertions target ids and roles, or copy unique to the block under test. A string that
also lives on a sibling page would give a false green.
"""

from pathlib import Path

import pytest

pytestmark = pytest.mark.django_db(transaction=True)

DASHBOARD_DIR = Path(__file__).resolve().parent.parent / "dashboard"

STATIC_SLUGS = ["compact-kpi", "activity-feed", "first-run"]
SLUGS = STATIC_SLUGS + ["split-charts"]

DATASTAR = 'script[src*="datastar.js"]'


def preview(slug: str) -> str:
    return f"/lb/dashboard/{slug}/preview/"


def block_templates(slug: str) -> list[Path]:
    return [p for p in (DASHBOARD_DIR / slug / "templates").rglob("*.html") if p.is_file()]


def _watch_requests(page):
    """Record every request the page fires from now on (favicon excluded)."""
    seen = []
    page.on("request", lambda r: seen.append(r.url))
    return seen


def _fired(seen):
    return [u for u in seen if "favicon" not in u]


def _chart_data(page, chart_id):
    """Chart.js keeps labels on the canvas, not in the DOM — ask Chart.js."""
    return page.evaluate(
        """(id) => {
            const canvas = document.querySelector('#' + id + ' canvas');
            const chart = window.Chart.getChart(canvas);
            return {
                labels: chart.data.labels,
                datasets: chart.data.datasets.map(d => ({label: d.label, data: d.data})),
            };
        }""",
        chart_id,
    )


# --- the three static dashboards: no JavaScript, at all ----------------------


@pytest.mark.parametrize("slug", STATIC_SLUGS)
def test_static_dashboard_emits_no_script_src(page, live_server, slug):
    """The claim a dashboard is least expected to make: this page downloads nothing."""
    page.goto(f"{live_server.url}{preview(slug)}")

    srcs = page.eval_on_selector_all("script[src]", "els => els.map(e => e.getAttribute('src'))")
    assert srcs == [], f"{slug} pulled {srcs}"
    assert page.locator(DATASTAR).count() == 0


@pytest.mark.parametrize("slug", STATIC_SLUGS)
def test_static_dashboard_templates_contain_no_script_tag(slug):
    """Belt and braces at the source, where the renderer chrome cannot mask a regression."""
    offenders = [p.name for p in block_templates(slug) if "<script" in p.read_text()]
    assert offenders == []


# --- compact-kpi: density, and digits that line up ---------------------------


def test_compact_kpi_renders_eight_metrics_with_sparklines(page, live_server):
    page.goto(f"{live_server.url}{preview('compact-kpi')}")

    assert page.locator("#kpi-grid article").count() == 8
    assert page.locator("#kpi-grid svg polyline").count() == 8
    assert page.locator("#kpi-mrr").inner_text().startswith("MRR")


def test_compact_kpi_figures_are_tabular(page, live_server):
    """Rule 5 of the premium bar, asserted rather than eyeballed."""
    page.goto(f"{live_server.url}{preview('compact-kpi')}")

    value = page.locator("#kpi-arr p").first
    assert "tabular-nums" in value.get_attribute("class")
    assert page.locator("#segment-table td.tabular-nums").count() >= 12


def test_compact_kpi_carries_more_than_the_grid(page, live_server):
    """Premium bar rule 2 — the segment table and the account list are the block."""
    page.goto(f"{live_server.url}{preview('compact-kpi')}")

    assert page.locator("#segment-enterprise").is_visible()
    assert page.locator("#top-accounts li").count() == 5
    assert page.locator("#kpi-footnote").is_visible()


# --- activity-feed: numbers beside the events that produced them -------------


def test_activity_feed_pairs_stats_with_a_timeline(page, live_server):
    page.goto(f"{live_server.url}{preview('activity-feed')}")

    assert page.locator("#stat-net-new").inner_text() == "$4,740"
    assert page.locator("#activity-log li.timeline-item, #activity-log li").count() >= 8
    assert page.locator("#event-ironvale-upgrade").is_visible()
    assert page.locator("#event-kite-downgrade").is_visible()


def test_activity_feed_groups_events_by_day(page, live_server):
    page.goto(f"{live_server.url}{preview('activity-feed')}")

    assert page.locator("#activity-log ul.timeline").count() == 3
    assert page.get_by_text("Earlier this week", exact=True).is_visible()


def test_activity_feed_carries_more_than_the_feed(page, live_server):
    """Premium bar rule 2 — the team panel and the digest card."""
    page.goto(f"{live_server.url}{preview('activity-feed')}")

    assert page.locator("#team-list li").count() == 3
    assert page.locator("#digest-card").is_visible()
    assert page.get_by_role("button", name="Turn on the digest").is_visible()


# --- first-run: the empty dashboard, designed ---------------------------------


def test_first_run_reads_as_a_designed_empty_state(page, live_server):
    """Not a dashboard with the data deleted: it explains, and it offers one thing to do."""
    page.goto(f"{live_server.url}{preview('first-run')}")

    empty = page.locator("#first-run-empty")
    assert empty.is_visible()
    assert "Your revenue graph starts with one connection." in empty.inner_text()
    assert "backfills 24 months" in empty.inner_text()
    assert page.get_by_role("button", name="Connect billing").first.is_visible()
    assert page.get_by_role("button", name="Import a CSV instead").is_visible()


def test_first_run_shows_a_setup_path_not_a_wall_of_zeroes(page, live_server):
    page.goto(f"{live_server.url}{preview('first-run')}")

    assert page.locator("#setup-steps li").count() == 4
    assert page.locator("#setup-progress").get_attribute("value") == "25"
    assert page.locator("#step-workspace").is_visible()
    assert page.locator("#first-looks li").count() == 3


def test_first_run_placeholders_refuse_to_guess(page, live_server):
    """An empty MRR tile reading $0 is a lie — these say what they are waiting for."""
    page.goto(f"{live_server.url}{preview('first-run')}")

    tiles = page.locator("#sample-data article")
    assert tiles.count() == 4
    assert page.locator("#placeholder-mrr").inner_text().strip().startswith("MRR")
    assert "Ready after the first sync" in page.locator("#placeholder-mrr").inner_text()
    assert page.locator("#first-run-help").is_visible()


# --- split-charts: three charts, one signal, zero server ----------------------


def test_split_charts_renders_thirty_days_by_default(page, live_server):
    page.goto(f"{live_server.url}{preview('split-charts')}")
    page.wait_for_selector(DATASTAR, state="attached")
    page.wait_for_function("window.Chart && window.Chart.getChart(document.querySelector('#mrr-chart canvas'))")

    assert _chart_data(page, "mrr-chart")["labels"] == [
        "9 Jun", "15 Jun", "21 Jun", "27 Jun", "3 Jul", "9 Jul",
    ]
    assert page.locator("#summary-net-new").inner_text() == "16,740"


def test_split_charts_switch_redraws_every_chart_with_no_network_request(page, live_server):
    """The surface's claim: a client signal swaps three datasets, and the wire stays silent."""
    page.goto(f"{live_server.url}{preview('split-charts')}")
    page.wait_for_selector(DATASTAR, state="attached")
    page.wait_for_function("window.Chart && window.Chart.getChart(document.querySelector('#movement-chart canvas'))")

    seen = _watch_requests(page)
    page.get_by_role("button", name="7 days").click()

    page.wait_for_function(
        "document.getElementById('summary-net-new').textContent === '4,740'"
    )

    mrr = _chart_data(page, "mrr-chart")
    assert mrr["labels"] == ["Thu", "Fri", "Sat", "Sun", "Mon", "Tue", "Wed"]
    assert mrr["datasets"][0]["data"][-1] == 412900

    movement = _chart_data(page, "movement-chart")
    assert movement["labels"] == ["Thu", "Fri", "Sat", "Sun", "Mon", "Tue", "Wed"]
    assert [d["label"] for d in movement["datasets"]] == ["Expansion", "Churn and contraction"]

    source = _chart_data(page, "source-chart")
    assert source["datasets"][0]["data"] == [2300, 9180, 700]

    assert _fired(seen) == [], f"expected zero requests, got {_fired(seen)}"


def test_split_charts_switch_updates_the_summary_and_the_caption(page, live_server):
    page.goto(f"{live_server.url}{preview('split-charts')}")
    page.wait_for_selector(DATASTAR, state="attached")

    page.get_by_role("button", name="90 days").click()
    page.wait_for_function("document.getElementById('summary-net-new').textContent === '52,910'")

    assert page.locator("#summary-expansion").inner_text() == "118,400"
    assert page.locator("#summary-churn").inner_text() == "65,490"
    assert page.locator("#summary-logos").inner_text() == "34"
    assert "the window the board reviews" in page.locator("#range-note").inner_text()


def test_split_charts_range_buttons_restyle_from_the_signal(page, live_server):
    """`btnStyle="$view.d7Style:ghost"` — a reactive prop, not a class the handler toggles."""
    page.goto(f"{live_server.url}{preview('split-charts')}")
    page.wait_for_selector(DATASTAR, state="attached")

    seven = page.get_by_role("button", name="7 days")
    thirty = page.get_by_role("button", name="30 days")

    page.wait_for_function(
        "!document.evaluate(\"//button[normalize-space()='30 days']\", document, null, 9, null)"
        ".singleNodeValue.classList.contains('btn-ghost')"
    )
    assert "btn-ghost" in seven.get_attribute("class")

    seven.click()
    page.wait_for_function(
        "document.evaluate(\"//button[normalize-space()='30 days']\", document, null, 9, null)"
        ".singleNodeValue.classList.contains('btn-ghost')"
    )
    assert "btn-ghost" not in seven.get_attribute("class")
    assert "btn-ghost" in thirty.get_attribute("class")


def test_split_charts_keeps_the_watchlist_across_a_switch(page, live_server):
    """Premium bar rule 2 — the block is more than its charts, and risk has no window."""
    page.goto(f"{live_server.url}{preview('split-charts')}")

    assert page.locator("#watchlist li").count() == 4
    page.get_by_role("button", name="7 days").click()
    assert page.locator("#watchlist li").count() == 4


# --- the catalogue rework's whole point ---------------------------------------


@pytest.mark.parametrize("slug", SLUGS)
def test_dashboard_variant_is_ardens_not_labbs(page, live_server, slug):
    page.goto(f"{live_server.url}{preview(slug)}")

    body = page.locator("main").inner_text()
    assert "Arden" in body
    assert "labb" not in body.lower()


@pytest.mark.parametrize("slug", SLUGS)
def test_dashboard_variant_source_never_mentions_labb(slug):
    for template in block_templates(slug):
        assert "labb" not in template.read_text().lower(), f"{template} mentions labb"


@pytest.mark.parametrize("slug", SLUGS)
def test_dashboard_variant_has_no_lorem(slug):
    for template in block_templates(slug):
        assert "lorem" not in template.read_text().lower()
