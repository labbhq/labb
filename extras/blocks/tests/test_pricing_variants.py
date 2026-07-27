"""
Integration tests for the lb/pricing surface — the catalogue's canonical demo of
reactive props, and its clearest proof that reactivity is opt-in.

The two claims under test, both asserted through a real browser:

1. `three-tier-toggle` and `usage-calculator` re-price everything from a client
   signal with **no network request** — no server, no endpoint, nothing on the wire.
2. `single-plan` and `highlight-tiers` emit **no datastar.js script tag at all**.

Text assertions target ids, not copy, so an unrelated string elsewhere on the page
can never turn a broken block green.
"""

import pytest

pytestmark = pytest.mark.django_db(transaction=True)

TOGGLE = "/lb/pricing/three-tier-toggle/preview/"
MATRIX = "/lb/pricing/comparison-table/preview/"
CALC = "/lb/pricing/usage-calculator/preview/"
SINGLE = "/lb/pricing/single-plan/preview/"
HIGHLIGHT = "/lb/pricing/highlight-tiers/preview/"

DATASTAR = 'script[src*="datastar.js"]'


def _watch_requests(page):
    """Record every request the page fires from now on (favicon excluded)."""
    seen = []
    page.on("request", lambda r: seen.append(r.url))
    return seen


def _fired(seen):
    return [u for u in seen if "favicon" not in u]


# --- three-tier-toggle: the canonical reactive-props demo -------------------


def test_toggle_renders_monthly_prices_server_side(page, live_server):
    page.goto(f"{live_server.url}{TOGGLE}")

    assert page.locator("#price-starter").inner_text() == "49"
    assert page.locator("#price-growth").inner_text() == "149"
    assert page.locator("#price-scale").inner_text() == "449"


def test_toggle_reprices_every_plan_with_no_network_request(page, live_server):
    """The whole point of the surface: a signal flips, three prices change, wire is silent."""
    page.goto(f"{live_server.url}{TOGGLE}")
    page.wait_for_selector(DATASTAR, state="attached")
    page.locator("#price-growth").wait_for()

    seen = _watch_requests(page)
    page.get_by_role("button", name="Annual").click()

    page.wait_for_function("document.getElementById('price-growth').textContent === '1,490'")
    assert page.locator("#price-starter").inner_text() == "490"
    assert page.locator("#price-scale").inner_text() == "4,490"
    assert _fired(seen) == [], f"expected zero requests, got {_fired(seen)}"


def test_toggle_flips_back_to_monthly(page, live_server):
    page.goto(f"{live_server.url}{TOGGLE}")
    page.get_by_role("button", name="Annual").click()
    page.wait_for_function("document.getElementById('price-growth').textContent === '1,490'")

    page.get_by_role("button", name="Monthly").click()
    page.wait_for_function("document.getElementById('price-growth').textContent === '149'")
    assert page.locator("#price-starter").inner_text() == "49"


def test_toggle_reactive_prop_restyles_the_badge(page, live_server):
    """`variant="$period.saveVariant:neutral"` — a reactive prop, not a class swap."""
    page.goto(f"{live_server.url}{TOGGLE}")
    badge = page.locator("#period-note")
    page.wait_for_selector(DATASTAR, state="attached")

    page.get_by_role("button", name="Annual").click()
    page.wait_for_function(
        "document.getElementById('period-note').className.includes('badge-success')"
    )
    assert badge.inner_text() == "Saving 2 months"


def test_toggle_ships_surrounding_matter(page, live_server):
    """Premium bar rule 2 — a bare price grid would read as a template."""
    page.goto(f"{live_server.url}{TOGGLE}")

    assert page.get_by_text("Trusted by 2,400+ finance and ops teams").is_visible()
    assert page.get_by_text("Jonah Price").is_visible()
    assert page.get_by_text("Switch plans mid-cycle").is_visible()


# --- comparison-table ------------------------------------------------------


def test_matrix_renders_the_full_feature_grid(page, live_server):
    page.goto(f"{live_server.url}{MATRIX}")

    assert page.locator("#matrix-price-growth").inner_text() == "149"
    for group in ("The revenue graph", "Forecasting", "Alerts and integrations", "Governance and support"):
        assert page.get_by_role("columnheader", name=group).is_visible()
    assert page.get_by_role("cell", name="Custom revenue models").is_visible()


def test_matrix_reprices_headers_with_no_network_request(page, live_server):
    page.goto(f"{live_server.url}{MATRIX}")
    page.wait_for_selector(DATASTAR, state="attached")
    page.locator("#matrix-price-growth").wait_for()

    seen = _watch_requests(page)
    page.get_by_role("button", name="Annual").click()

    page.wait_for_function(
        "document.getElementById('matrix-price-growth').textContent === '1,490'"
    )
    assert page.locator("#matrix-price-starter").inner_text() == "490"
    assert page.locator("#matrix-price-scale").inner_text() == "4,490"
    assert _fired(seen) == [], f"expected zero requests, got {_fired(seen)}"


# --- usage-calculator: derived signals, no server ---------------------------


def test_calculator_renders_a_quote_server_side(page, live_server):
    page.goto(f"{live_server.url}{CALC}")

    assert page.locator("#seat-count-value").inner_text() == "12"
    assert page.locator("#recommended-plan").inner_text() == "Growth"
    assert page.locator("#usage-total").inner_text() == "257"


def test_calculator_recomputes_the_price_live_with_no_network_request(page, live_server):
    """Drag the slider to the top: plan, line items and total all re-derive client-side."""
    page.goto(f"{live_server.url}{CALC}")
    page.wait_for_selector(DATASTAR, state="attached")

    seen = _watch_requests(page)
    slider = page.locator("#seat-count")
    slider.focus()
    slider.press("End")

    page.wait_for_function("document.getElementById('seat-count-value').textContent === '60'")
    # 60 seats → Scale ($449 platform) + 60 × $9 = $989.
    assert page.locator("#recommended-plan").inner_text() == "Scale"
    assert page.locator("#usage-total").inner_text() == "989"
    assert _fired(seen) == [], f"expected zero requests, got {_fired(seen)}"


def test_calculator_drops_to_starter_at_the_bottom_of_the_slider(page, live_server):
    page.goto(f"{live_server.url}{CALC}")
    page.wait_for_selector(DATASTAR, state="attached")

    slider = page.locator("#seat-count")
    slider.focus()
    slider.press("Home")

    page.wait_for_function("document.getElementById('seat-count-value').textContent === '3'")
    # 3 seats → Starter ($49 platform) + 3 × $9 = $76.
    assert page.locator("#recommended-plan").inner_text() == "Starter"
    assert page.locator("#usage-total").inner_text() == "76"


def test_calculator_annual_multiplies_the_derived_total(page, live_server):
    page.goto(f"{live_server.url}{CALC}")
    page.wait_for_selector(DATASTAR, state="attached")

    page.get_by_role("button", name="Annual").click()
    page.wait_for_function("document.getElementById('usage-total').textContent === '2,570'")
    assert page.locator("#recommended-plan").inner_text() == "Growth"


# --- zero-JS blocks: the absence is the assertion ---------------------------


def test_single_plan_ships_no_datastar(page, live_server):
    page.goto(f"{live_server.url}{SINGLE}")

    assert page.locator(DATASTAR).count() == 0
    assert page.locator("script[src]").count() == 0
    assert page.get_by_role("heading", name="We only sell one thing").is_visible()


def test_single_plan_faq_opens_without_javascript(page, live_server):
    page.goto(f"{live_server.url}{SINGLE}")

    item = page.locator(".collapse", has_text="What happens past 10,000 customers?")
    item.locator("input[type=radio]").click()

    answer = page.get_by_text("Nothing breaks and nothing gets throttled.")
    answer.wait_for(state="visible")
    assert answer.is_visible()


def test_highlight_tiers_ships_no_datastar(page, live_server):
    page.goto(f"{live_server.url}{HIGHLIGHT}")

    assert page.locator(DATASTAR).count() == 0
    assert page.locator("script[src]").count() == 0
    assert page.get_by_role("heading", name="Three plans. Most teams pick the middle one.").is_visible()


def test_highlight_tiers_raises_the_middle_plan(page, live_server):
    page.goto(f"{live_server.url}{HIGHLIGHT}")

    featured = page.locator(".card", has_text="Most popular").first
    featured_class = featured.get_attribute("class") or ""
    # Featured is signalled by border + elevation + ring, not by resizing the card.
    assert "border-primary" in featured_class
    assert "ring-primary/20" in featured_class
    assert "lg:scale-105" not in featured_class
    assert "lg:-my-6" not in featured_class
    assert page.get_by_text("Tomas Neary").is_visible()


# --- the surface is Arden's, not labb's ------------------------------------


@pytest.mark.parametrize("url", [TOGGLE, MATRIX, CALC, SINGLE, HIGHLIGHT])
def test_no_labb_subject_matter(page, live_server, url):
    page.goto(f"{live_server.url}{url}")

    body = page.locator("main").inner_text()
    assert "Arden" in body
    assert "labb" not in body.lower()
