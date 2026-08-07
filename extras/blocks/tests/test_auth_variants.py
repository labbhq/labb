"""
Integration tests for the four lb/auth/* sign-in variants that sit beside the
split-brand anchor: centred-card, social-proof, two-column-visual and magic-link.

Three claims are under test, all through a real browser:

1. Premium bar rule 2 — each variant carries something beyond the bare form, and
   each test asserts that block's *own* surrounding matter on a string unique to
   it. A shared string would go green on a broken page.
2. `magic-link` changes state with **no network request at all** — the whole flow
   is one client signal, and there is no view behind the block.
3. `social-proof` and `two-column-visual` emit **no script[src] whatsoever** —
   reactivity is opt-in, and these two opt out.

Assertions target ids and roles rather than copy wherever a locator can, because
four sign-in pages share most of their vocabulary.
"""

from pathlib import Path

import pytest

pytestmark = pytest.mark.django_db(transaction=True)

AUTH_DIR = Path(__file__).resolve().parent.parent / "auth"

SLUGS = ["centred-card", "social-proof", "two-column-visual", "magic-link"]
STATIC_SLUGS = ["social-proof", "two-column-visual"]

DATASTAR = 'script[src*="datastar"]'

# The line each variant lands, and no other page in the collection lands.
HEADLINES = {
    "centred-card": "Sign in to your workspace",
    "social-proof": "Close the quarter with confidence",
    "two-column-visual": "Pick up where the quarter left off",
    "magic-link": "Sign in without a password",
}

# The element beyond the mechanism — the clause the premium bar actually turns on.
BEYOND_THE_FORM = {
    "centred-card": "SOC 2 Type II · Audited February 2026",
    "social-proof": "4.8 out of 5",
    "two-column-visual": "This is what loads after you sign in.",
    "magic-link": "61% of Arden workspaces have turned passwords off entirely.",
}


def preview(slug: str) -> str:
    return f"/lb/auth/{slug}/preview/"


def block_templates(slug: str) -> list[Path]:
    return [p for p in (AUTH_DIR / slug / "templates").rglob("*.html") if p.is_file()]


def watch_requests(page):
    """Record every request fired from now on (favicon excluded)."""
    seen = []
    page.on("request", lambda r: seen.append(r.url))
    return seen


def fired(seen):
    return [u for u in seen if "favicon" not in u]


# --- every variant is a sign-in page a developer could pick over the others ----


@pytest.mark.parametrize("slug", SLUGS)
def test_variant_lands_its_own_headline(page, live_server, slug):
    page.goto(f"{live_server.url}{preview(slug)}")

    assert page.get_by_role(
        "heading", name=HEADLINES[slug], exact=True
    ).first.is_visible()


@pytest.mark.parametrize("slug", SLUGS)
def test_variant_carries_more_than_the_form(page, live_server, slug):
    """Premium bar rule 2 — a form and a button is a template, not a block."""
    page.goto(f"{live_server.url}{preview(slug)}")

    beyond = page.get_by_text(BEYOND_THE_FORM[slug], exact=False).first
    assert beyond.is_visible()


@pytest.mark.parametrize("slug", SLUGS)
def test_variant_offers_oauth(page, live_server, slug):
    page.goto(f"{live_server.url}{preview(slug)}")

    for provider in ("Google", "Apple", "GitHub"):
        assert page.get_by_role("button", name=provider).first.is_visible()


@pytest.mark.parametrize("slug", SLUGS)
def test_variant_is_ardens_not_labbs(page, live_server, slug):
    page.goto(f"{live_server.url}{preview(slug)}")

    body = page.locator("main").inner_text()
    assert "Arden" in body
    assert "labb" not in body.lower()


@pytest.mark.parametrize("slug", SLUGS)
def test_variant_source_never_mentions_labb(slug):
    for template in block_templates(slug):
        assert "labb" not in template.read_text().lower(), f"{template} mentions labb"


@pytest.mark.parametrize("slug", SLUGS)
def test_variant_has_no_lorem(slug):
    for template in block_templates(slug):
        assert "lorem" not in template.read_text().lower()


# --- the two static variants ship no JavaScript at all ------------------------


@pytest.mark.parametrize("slug", STATIC_SLUGS)
def test_static_variant_loads_no_script_at_all(page, live_server, slug):
    """
    Not merely "no datastar" — no script[src] of any kind. A sign-in page has no
    business downloading a framework, and this is the only way to prove it did not.
    """
    page.goto(f"{live_server.url}{preview(slug)}")

    assert page.locator("script[src]").count() == 0
    assert page.locator(DATASTAR).count() == 0
    assert "datastar" not in page.content()


@pytest.mark.parametrize("slug", STATIC_SLUGS)
def test_static_variant_templates_carry_no_script_tag(slug):
    offenders = [p.name for p in block_templates(slug) if "<script" in p.read_text()]
    assert offenders == []


def test_social_proof_shows_the_arden_supporting_cast(page, live_server):
    page.goto(f"{live_server.url}{preview('social-proof')}")

    logos = page.locator("#proof-logos")
    for customer in (
        "AtlasForge",
        "Kite & Bell",
        "Northwind Co",
        "Verity Labs",
        "Ironvale Group",
    ):
        assert logos.get_by_text(customer, exact=True).is_visible()

    assert page.locator("#proof-quote").get_by_text("Priya Raghavan").is_visible()


def test_two_column_visual_frames_a_product_shot_built_from_markup(page, live_server):
    """No image asset: the 'screenshot' is a themed component tree in browser chrome."""
    page.set_viewport_size({"width": 1280, "height": 900})
    page.goto(f"{live_server.url}{preview('two-column-visual')}")

    shot = page.locator("#tv-shot")
    assert shot.is_visible()
    assert shot.get_by_text("Renewals · next 30 days").is_visible()
    assert shot.get_by_text("Ironvale Group").is_visible()
    assert page.locator("main img").count() == 0


# --- centred-card: one signal, one job ---------------------------------------


def test_centred_card_password_starts_hidden(page, live_server):
    page.goto(f"{live_server.url}{preview('centred-card')}")

    assert page.locator("#cc-password").get_attribute("type") == "password"


def test_centred_card_reveal_toggles_the_input_type(page, live_server):
    page.goto(f"{live_server.url}{preview('centred-card')}")
    page.wait_for_selector(DATASTAR, state="attached")

    page.locator("#cc-password").fill("supersecret")
    page.locator("#cc-reveal").click()
    page.wait_for_function("document.getElementById('cc-password').type === 'text'")

    assert page.locator("#cc-password").input_value() == "supersecret"

    page.locator("#cc-reveal").click()
    page.wait_for_function("document.getElementById('cc-password').type === 'password'")


def test_centred_card_reveal_costs_no_request(page, live_server):
    page.goto(f"{live_server.url}{preview('centred-card')}")
    page.wait_for_selector(DATASTAR, state="attached")
    page.locator("#cc-reveal").wait_for()

    seen = watch_requests(page)
    page.locator("#cc-reveal").click()
    page.wait_for_function("document.getElementById('cc-password').type === 'text'")

    assert fired(seen) == [], f"expected zero requests, got {fired(seen)}"


# --- magic-link: a state machine with no server behind it ---------------------


def test_magic_link_starts_on_the_form(page, live_server):
    page.goto(f"{live_server.url}{preview('magic-link')}")
    page.wait_for_selector(DATASTAR, state="attached")

    assert page.locator("#magic-form").is_visible()
    assert page.locator("#magic-sent").is_hidden()


def test_magic_link_sends_with_no_network_request(page, live_server):
    """
    The claim the block exists to make: form → sent, driven by one client signal,
    with nothing on the wire. If a request fires here, the block is a lie.
    """
    page.goto(f"{live_server.url}{preview('magic-link')}")
    page.wait_for_selector(DATASTAR, state="attached")
    page.locator("#magic-email").wait_for()

    seen = watch_requests(page)

    page.locator("#magic-email").fill("priya@northwind.co")
    page.locator("#magic-send").click()

    page.wait_for_selector("#magic-sent", state="visible")
    assert page.locator("#magic-form").is_hidden()
    assert fired(seen) == [], f"expected zero requests, got {fired(seen)}"


def test_magic_link_sent_state_greets_the_address_that_was_typed(page, live_server):
    page.goto(f"{live_server.url}{preview('magic-link')}")
    page.wait_for_selector(DATASTAR, state="attached")

    page.locator("#magic-email").fill("priya@northwind.co")
    page.locator("#magic-send").click()
    page.wait_for_selector("#magic-sent", state="visible")

    assert page.locator("#magic-recipient").inner_text() == "priya@northwind.co"
    assert (
        page.locator("#magic-sent")
        .get_by_text("The link works once and expires after 10 minutes.")
        .is_visible()
    )


def test_magic_link_can_go_back_to_the_form(page, live_server):
    page.goto(f"{live_server.url}{preview('magic-link')}")
    page.wait_for_selector(DATASTAR, state="attached")

    page.locator("#magic-email").fill("priya@northwind.co")
    page.locator("#magic-send").click()
    page.wait_for_selector("#magic-sent", state="visible")

    page.locator("#magic-back").click()
    page.wait_for_selector("#magic-form", state="visible")

    assert page.locator("#magic-sent").is_hidden()
    assert page.locator("#magic-email").input_value() == "priya@northwind.co"


def test_magic_link_will_not_send_without_an_email(page, live_server):
    page.goto(f"{live_server.url}{preview('magic-link')}")
    page.wait_for_selector(DATASTAR, state="attached")
    page.wait_for_function("document.getElementById('magic-send').disabled === true")

    assert page.locator("#magic-send").is_disabled()
