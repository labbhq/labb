"""
Integration tests for the four `fe` variants on the lb/wizard surface.

The claim under test, for all four: step state lives in **client signals with no
server**. Every one of these blocks moves between steps, keeps what was typed, and
never puts a byte on the wire — the real submit belongs to the `onboarding` anchor.

Assertions target ids and input values, never shared copy: a string like "Continue"
appears on all four pages, so a text-only assertion would pass while the binding
underneath was dead.
"""

import pytest

pytestmark = pytest.mark.django_db(transaction=True)

HORIZONTAL = "/lb/wizard/horizontal-steps/preview/"
VERTICAL = "/lb/wizard/vertical-steps/preview/"
SUMMARY = "/lb/wizard/with-summary/preview/"
MINIMAL = "/lb/wizard/progress-minimal/preview/"

DATASTAR = 'script[src*="datastar.js"]'


def _watch_requests(page):
    """Record every request the page fires from now on (favicon excluded)."""
    seen = []
    page.on("request", lambda r: seen.append(r.url))
    return seen


def _fired(seen):
    return [u for u in seen if "favicon" not in u]


def _ready(page, live_server, url):
    """Load a wizard and wait until the runtime is attached and the signals applied."""
    page.goto(f"{live_server.url}{url}")
    page.wait_for_selector(DATASTAR, state="attached")
    return page


# --- horizontal-steps ------------------------------------------------------


def test_horizontal_steps_advance_without_a_single_request(page, live_server):
    _ready(page, live_server, HORIZONTAL)
    page.locator("#hz-company").fill("Kite & Bell")

    seen = _watch_requests(page)
    page.locator("#hz-next").click()
    page.wait_for_function(
        "document.querySelector('#hz-count span').textContent === '2'"
    )
    page.locator("#hz-next").click()
    page.wait_for_function(
        "document.querySelector('#hz-count span').textContent === '3'"
    )

    assert _fired(seen) == [], f"expected zero requests, got {_fired(seen)}"


def test_horizontal_steps_going_back_keeps_what_was_typed(page, live_server):
    _ready(page, live_server, HORIZONTAL)
    page.locator("#hz-company").fill("Kite & Bell")
    page.locator("#hz-slug").fill("kite-and-bell")

    page.locator("#hz-next").click()
    page.wait_for_function(
        "document.querySelector('#hz-count span').textContent === '2'"
    )
    page.locator("#hz-back").click()
    page.wait_for_function(
        "document.querySelector('#hz-count span').textContent === '1'"
    )

    assert page.locator("#hz-company").input_value() == "Kite & Bell"
    assert page.locator("#hz-slug").input_value() == "kite-and-bell"


def test_horizontal_steps_stepper_marks_the_step_done(page, live_server):
    _ready(page, live_server, HORIZONTAL)
    page.locator("#hz-next").click()

    page.wait_for_function(
        "document.getElementById('step-dot-1').className.includes('bg-success')"
    )
    assert "bg-primary" in page.locator("#step-dot-2").get_attribute("class")


def test_horizontal_steps_back_is_disabled_on_the_first_step(page, live_server):
    _ready(page, live_server, HORIZONTAL)
    assert page.locator("#hz-back").is_disabled()

    page.locator("#hz-next").click()
    page.wait_for_function("!document.getElementById('hz-back').disabled")


# --- vertical-steps --------------------------------------------------------


def test_vertical_steps_advance_without_a_single_request(page, live_server):
    _ready(page, live_server, VERTICAL)
    page.locator("#vt-company").fill("Verity Labs")

    seen = _watch_requests(page)
    page.locator("#vt-next").click()
    page.wait_for_function(
        "document.querySelector('#vt-count span').textContent === '2'"
    )

    assert _fired(seen) == [], f"expected zero requests, got {_fired(seen)}"


def test_vertical_steps_going_back_keeps_what_was_typed(page, live_server):
    _ready(page, live_server, VERTICAL)
    page.locator("#vt-company").fill("Verity Labs")
    page.locator("#vt-next").click()
    page.wait_for_function(
        "document.querySelector('#vt-count span').textContent === '2'"
    )

    page.locator("#vt-contact").fill("finance@veritylabs.io")
    page.locator("#vt-back").click()
    page.wait_for_function(
        "document.querySelector('#vt-count span').textContent === '1'"
    )

    assert page.locator("#vt-company").input_value() == "Verity Labs"

    page.locator("#vt-next").click()
    page.wait_for_function(
        "document.querySelector('#vt-count span').textContent === '2'"
    )
    assert page.locator("#vt-contact").input_value() == "finance@veritylabs.io"


def test_vertical_steps_rail_highlights_the_current_step(page, live_server):
    _ready(page, live_server, VERTICAL)
    page.wait_for_function(
        "document.getElementById('rail-step-1').className.includes('border-primary/30')"
    )

    page.locator("#vt-next").click()
    page.wait_for_function(
        "document.getElementById('rail-step-2').className.includes('border-primary/30')"
    )
    assert "border-primary/30" not in page.locator("#rail-step-1").get_attribute(
        "class"
    )


# --- with-summary: the panel has to be derived, or the block has no reason to exist


def test_summary_panel_follows_the_workspace_name_as_it_is_typed(page, live_server):
    _ready(page, live_server, SUMMARY)
    assert page.locator("#sw-summary-name").inner_text() == "Untitled workspace"

    page.locator("#sw-company").fill("Ironvale Group")
    page.locator("#sw-slug").fill("ironvale-group")

    page.wait_for_function(
        "document.getElementById('sw-summary-name').textContent === 'Ironvale Group'"
    )
    assert (
        page.locator("#sw-summary-address").inner_text() == "arden.app/ironvale-group"
    )


def test_summary_total_recomputes_from_seats_with_no_request(page, live_server):
    """Growth is $149 for 10 seats; four extra seats at $12 make it $197."""
    _ready(page, live_server, SUMMARY)
    page.locator("#sw-next").click()
    page.wait_for_function(
        "document.querySelector('#sw-count span').textContent === '2'"
    )

    seen = _watch_requests(page)
    page.locator("#sw-seats").fill("14")
    page.locator("#sw-seats").dispatch_event("input")

    page.wait_for_function(
        "document.getElementById('sw-summary-total').textContent === '197'"
    )
    assert page.locator("#sw-summary-extra").inner_text() == "4"
    assert page.locator("#sw-summary-extra-row").is_visible()
    assert _fired(seen) == [], f"expected zero requests, got {_fired(seen)}"


def test_summary_total_follows_the_plan(page, live_server):
    _ready(page, live_server, SUMMARY)
    page.locator("#sw-next").click()
    page.wait_for_function(
        "document.querySelector('#sw-count span').textContent === '2'"
    )

    assert page.locator("#sw-summary-plan").inner_text() == "Arden Growth"
    assert page.locator("#sw-summary-total").inner_text() == "149"

    page.locator('input[name="sw-plan"][value="scale"]').check()

    page.wait_for_function(
        "document.getElementById('sw-summary-total').textContent === '449'"
    )
    assert page.locator("#sw-summary-plan").inner_text() == "Arden Scale"
    # 8 seats against Scale's 25 — no overage, so the extra-seats line goes away.
    assert not page.locator("#sw-summary-extra-row").is_visible()


def test_summary_survives_going_back(page, live_server):
    _ready(page, live_server, SUMMARY)
    page.locator("#sw-company").fill("Ironvale Group")
    page.locator("#sw-next").click()
    page.locator("#sw-seats").fill("14")
    page.locator("#sw-seats").dispatch_event("input")
    page.wait_for_function(
        "document.getElementById('sw-summary-total').textContent === '197'"
    )

    page.locator("#sw-back").click()
    page.wait_for_function(
        "document.querySelector('#sw-count span').textContent === '1'"
    )

    assert page.locator("#sw-company").input_value() == "Ironvale Group"
    assert page.locator("#sw-summary-total").inner_text() == "197"


def test_summary_billing_contact_reaches_the_panel(page, live_server):
    _ready(page, live_server, SUMMARY)
    assert page.locator("#sw-summary-contact").inner_text() == "No billing contact yet"

    page.locator("#sw-next").click()
    page.locator("#sw-next").click()
    page.wait_for_function(
        "document.querySelector('#sw-count span').textContent === '3'"
    )
    page.locator("#sw-contact").fill("finance@ironvale.com")

    page.wait_for_function(
        "document.getElementById('sw-summary-contact').textContent === 'finance@ironvale.com'"
    )


# --- progress-minimal ------------------------------------------------------


def test_minimal_bar_and_count_track_the_step_with_no_request(page, live_server):
    _ready(page, live_server, MINIMAL)
    assert page.locator("#mw-bar").get_attribute("value") == "25"

    seen = _watch_requests(page)
    page.locator("#mw-next").click()
    page.wait_for_function(
        "document.getElementById('mw-bar').getAttribute('value') === '50'"
    )
    assert page.locator("#mw-count").inner_text() == "Step 2 of 4"

    page.locator("#mw-next").click()
    page.locator("#mw-next").click()
    page.wait_for_function(
        "document.getElementById('mw-bar').getAttribute('value') === '100'"
    )

    assert _fired(seen) == [], f"expected zero requests, got {_fired(seen)}"


def test_minimal_badge_is_a_reactive_prop(page, live_server):
    """`variant="$tone:primary"` — labb recomputes the daisyUI class in the browser."""
    _ready(page, live_server, MINIMAL)
    assert "badge-primary" in page.locator("#mw-tone").get_attribute("class")

    for _ in range(3):
        page.locator("#mw-next").click()

    page.wait_for_function(
        "document.getElementById('mw-tone').className.includes('badge-success')"
    )
    assert page.locator("#mw-tone").inner_text() == "Ready"


def test_minimal_going_back_keeps_every_answer(page, live_server):
    _ready(page, live_server, MINIMAL)
    page.locator("#mw-company").fill("Northwind Co")
    page.locator("#mw-next").click()
    page.locator('input[name="mw-model"][value="usage"]').check()
    page.locator("#mw-next").click()
    page.locator("#mw-source").select_option("chargebee")

    for _ in range(2):
        page.locator("#mw-back").click()
    page.wait_for_function(
        "document.getElementById('mw-bar').getAttribute('value') === '25'"
    )

    assert page.locator("#mw-company").input_value() == "Northwind Co"

    page.locator("#mw-next").click()
    assert page.locator('input[name="mw-model"][value="usage"]').is_checked()
    page.locator("#mw-next").click()
    assert page.locator("#mw-source").input_value() == "chargebee"


# --- the whole surface -----------------------------------------------------


@pytest.mark.parametrize("url", [HORIZONTAL, VERTICAL, SUMMARY, MINIMAL])
def test_wizard_variants_are_ardens_not_labbs(page, live_server, url):
    page.goto(f"{live_server.url}{url}")

    body = page.locator("main").inner_text()
    assert "Arden" in body
    assert "labb" not in body.lower()
