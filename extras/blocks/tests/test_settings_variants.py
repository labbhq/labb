"""
Integration tests for the four `fe` variants on the lb/settings surface.

What each one has to prove:

- `sidebar-nav`  — switching section is a client signal, and the wire stays empty.
- `profile`      — the chosen avatar previews client-side, from an object URL.
- `billing`      — no script[src] at all. A settings page nobody clicks ships no JS.
- `team-members` — role dropdowns bind to signals, and the unsaved bar is derived.

Assertions target ids and attribute values. Copy like "Save changes" is shared across
these pages, so a text-only assertion could go green on a page whose bindings are dead.
"""

import pytest

pytestmark = pytest.mark.django_db(transaction=True)

SIDEBAR = "/lb/settings/sidebar-nav/preview/"
PROFILE = "/lb/settings/profile/preview/"
BILLING = "/lb/settings/billing/preview/"
TEAM = "/lb/settings/team-members/preview/"

DATASTAR = 'script[src*="datastar.js"]'

# A 1×1 PNG, so the upload preview has a real file to make an object URL from.
PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000a49444154789c6360000002000100ffff03000006000557bfabd400"
    "00000049454e44ae426082"
)


def _watch_requests(page):
    seen = []
    page.on("request", lambda r: seen.append(r.url))
    return seen


def _fired(seen):
    return [u for u in seen if "favicon" not in u]


def _ready(page, live_server, url):
    page.goto(f"{live_server.url}{url}")
    page.wait_for_selector(DATASTAR, state="attached")
    return page


# --- sidebar-nav -----------------------------------------------------------


def test_sidebar_opens_on_the_workspace_section(page, live_server):
    _ready(page, live_server, SIDEBAR)

    assert page.get_by_role("heading", name="Workspace", exact=True).is_visible()
    assert not page.get_by_role("heading", name="Billing", exact=True).is_visible()


def test_sidebar_section_switch_fires_no_network_request(page, live_server):
    _ready(page, live_server, SIDEBAR)
    page.wait_for_function("document.getElementById('nav-profile').className.includes('menu-active')")

    seen = _watch_requests(page)
    page.locator("#nav-billing").click()

    page.wait_for_function("document.getElementById('nav-billing').className.includes('menu-active')")
    assert page.get_by_role("heading", name="Billing", exact=True).is_visible()
    assert _fired(seen) == [], f"expected zero requests, got {_fired(seen)}"


def test_sidebar_shows_the_section_that_was_clicked(page, live_server):
    _ready(page, live_server, SIDEBAR)

    page.locator("#nav-billing").click()
    page.wait_for_function("document.getElementById('nav-billing').className.includes('menu-active')")
    assert page.get_by_role("heading", name="Billing", exact=True).is_visible()
    assert not page.get_by_role("heading", name="Workspace", exact=True).is_visible()

    page.locator("#nav-security").click()
    page.wait_for_function("document.getElementById('nav-security').className.includes('menu-active')")
    assert page.get_by_role("heading", name="Security", exact=True).is_visible()
    assert not page.get_by_role("heading", name="Billing", exact=True).is_visible()


def test_sidebar_keeps_a_half_typed_field_across_a_section_trip(page, live_server):
    """Every section is on the page already, which is why this survives at all."""
    _ready(page, live_server, SIDEBAR)
    name = page.locator("input[type='text']").first
    name.fill("Beacon Labs EU")

    page.locator("#nav-team").click()
    page.wait_for_function("document.getElementById('nav-team').className.includes('menu-active')")
    page.locator("#nav-profile").click()
    page.wait_for_function("document.getElementById('nav-profile').className.includes('menu-active')")

    assert name.input_value() == "Beacon Labs EU"


# --- profile ---------------------------------------------------------------


def test_profile_shows_the_initials_avatar_until_a_file_is_chosen(page, live_server):
    _ready(page, live_server, PROFILE)

    assert page.locator("#avatar-fallback").is_visible()
    assert not page.locator("#avatar-preview").is_visible()
    assert page.locator("#avatar-filename").inner_text() == "Nothing chosen yet"


def test_profile_previews_the_chosen_avatar_client_side(page, live_server):
    _ready(page, live_server, PROFILE)

    page.locator("#avatar-file").set_input_files(
        files=[{"name": "nadia.png", "mimeType": "image/png", "buffer": PNG}]
    )

    page.wait_for_selector("#avatar-preview", state="visible")
    src = page.locator("#avatar-preview").get_attribute("src")
    assert src.startswith("blob:"), f"expected a local object URL, got {src!r}"
    assert page.locator("#avatar-filename").inner_text() == "nadia.png"
    assert not page.locator("#avatar-fallback").is_visible()


def test_profile_remove_puts_the_initials_back(page, live_server):
    _ready(page, live_server, PROFILE)
    page.locator("#avatar-file").set_input_files(
        files=[{"name": "nadia.png", "mimeType": "image/png", "buffer": PNG}]
    )
    page.wait_for_selector("#avatar-preview", state="visible")

    page.locator("#avatar-clear").click()

    page.wait_for_selector("#avatar-preview", state="hidden")
    assert page.locator("#avatar-fallback").is_visible()
    assert page.locator("#avatar-filename").inner_text() == "Nothing chosen yet"


def test_profile_details_carry_the_arden_member(page, live_server):
    _ready(page, live_server, PROFILE)

    assert page.locator("#pf-name").input_value() == "Nadia Kessler"
    assert page.locator("#pf-email").input_value() == "nadia.kessler@beaconlabs.com"


# --- billing: the zero-JS one ----------------------------------------------


def test_billing_emits_no_script_src_at_all(page, live_server):
    page.goto(f"{live_server.url}{BILLING}")

    assert page.locator("script[src]").count() == 0


def test_billing_draws_on_the_arden_invoice_fixtures(page, live_server):
    page.goto(f"{live_server.url}{BILLING}")

    body = page.locator("main").inner_text()
    for number in ("ARD-2026-0026", "ARD-2026-0013", "ARD-2026-0006"):
        assert number in body
    assert "Verity Labs" in body
    assert "AtlasForge" in body
    assert "2,927.00" in body


def test_billing_shows_the_plan_and_the_payment_method(page, live_server):
    page.goto(f"{live_server.url}{BILLING}")

    body = page.locator("main").inner_text()
    assert "Arden Scale" in body
    assert "•••• •••• •••• 4242" in body
    assert "1,023.00" in body


# --- team-members ----------------------------------------------------------


def test_team_roles_render_from_the_arden_cast(page, live_server):
    _ready(page, live_server, TEAM)

    assert page.locator("#role-nadia").input_value() == "owner"
    assert page.locator("#role-priya").input_value() == "billing"
    assert page.locator("#role-yusuf").input_value() == "viewer"
    assert not page.locator("#tm-savebar").is_visible()


def test_team_changing_a_role_fires_no_request_and_raises_the_bar(page, live_server):
    _ready(page, live_server, TEAM)

    seen = _watch_requests(page)
    page.locator("#role-jenny").select_option("admin")

    page.wait_for_selector("#tm-savebar", state="visible")
    assert page.locator("#tm-pending").inner_text() == "1"
    assert page.locator("#changed-jenny").is_visible()
    assert _fired(seen) == [], f"expected zero requests, got {_fired(seen)}"


def test_team_pending_count_is_derived_from_the_difference(page, live_server):
    _ready(page, live_server, TEAM)

    page.locator("#role-jenny").select_option("admin")
    page.locator("#role-hana").select_option("billing")
    page.wait_for_function("document.getElementById('tm-pending').textContent === '2'")

    page.locator("#role-jenny").select_option("member")
    page.wait_for_function("document.getElementById('tm-pending').textContent === '1'")
    assert not page.locator("#changed-jenny").is_visible()


def test_team_discard_restores_every_saved_role(page, live_server):
    _ready(page, live_server, TEAM)

    page.locator("#role-jenny").select_option("admin")
    page.locator("#role-marcus").select_option("viewer")
    page.wait_for_function("document.getElementById('tm-pending').textContent === '2'")

    page.locator("#tm-discard").click()

    page.wait_for_selector("#tm-savebar", state="hidden")
    assert page.locator("#role-jenny").input_value() == "member"
    assert page.locator("#role-marcus").input_value() == "admin"


def test_team_invite_line_follows_the_typed_email_and_role(page, live_server):
    _ready(page, live_server, TEAM)
    assert page.locator("#tm-invite-preview").inner_text() == "They will join as a Member."

    page.locator("#tm-invite-email").fill("rafael.sorensen@beaconlabs.com")
    page.locator("#tm-invite-role").select_option("billing")

    page.wait_for_function(
        "document.getElementById('tm-invite-preview').textContent.trim() === "
        "'rafael.sorensen@beaconlabs.com will join as a Billing.'"
    )


# --- the whole surface -----------------------------------------------------


@pytest.mark.parametrize("url", [SIDEBAR, PROFILE, BILLING, TEAM])
def test_settings_variants_are_ardens_not_labbs(page, live_server, url):
    page.goto(f"{live_server.url}{url}")

    body = page.locator("main").inner_text()
    assert "Arden" in body
    assert "labb" not in body.lower()
