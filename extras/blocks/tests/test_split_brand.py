"""
Integration tests for the lb/auth/split-brand block — the catalogue's auth anchor.

Covers both pages the anchor ships: sign-in and sign-up, off one shared validation
view. Drives the block through its preview URL in a real browser, asserting only
what a user can observe.
"""

import pytest

pytestmark = pytest.mark.django_db(transaction=True)

BASE = "/lb/auth/split-brand/preview"
SIGN_UP = f"{BASE}/sign-up"


@pytest.fixture
def member(db):
    import datetime

    from django.utils import timezone
    from lb.models import LbMember, LbPlan, LbWorkspace

    plan = LbPlan.objects.create(
        name="Scale",
        slug="scale",
        tagline="For growing teams",
        price_monthly=449,
        price_yearly=4490,
        seats_included=25,
    )
    workspace = LbWorkspace.objects.create(
        name="Beacon Labs",
        slug="beacon-labs",
        plan=plan,
        region="eu-west",
        currency="USD",
        billing_email="billing@beaconlabs.com",
        created_at=timezone.now(),
    )
    return LbMember.objects.create(
        workspace=workspace,
        name="Mira Chen",
        email="mira@beaconlabs.com",
        title="Founder",
        role="owner",
        status="active",
        joined_on=datetime.date(2026, 1, 12),
        last_active_at=timezone.now(),
    )


# --- the block is a page, not a form (premium bar rule 2) -------------------


def test_sign_in_loads_with_brand_and_social_proof(page, live_server):
    page.goto(f"{live_server.url}{BASE}/")

    assert page.locator("text=Welcome back to Arden").is_visible()
    # The surrounding matter is the point — a bare form would fail the premium bar.
    assert page.locator("text=Know your revenue.").is_visible()
    assert page.locator("text=Mira Chen").first.is_visible()
    assert page.locator("text=Trusted by 2,400+ finance and ops teams").is_visible()


def test_sign_in_offers_oauth(page, live_server):
    page.goto(f"{live_server.url}{BASE}/")

    for provider in ("Google", "Apple", "GitHub"):
        assert page.locator("button", has_text=provider).is_visible()


def test_block_is_not_labb_centric(page, live_server):
    """The whole point of the catalogue rework: the block is Arden's, not labb's."""
    page.goto(f"{live_server.url}{BASE}/")

    body = page.locator("main").inner_text()
    assert "Arden" in body
    assert "labb" not in body.lower()


# --- live validation, gentle while typing ----------------------------------


def test_invalid_email_shows_error_while_typing(page, live_server):
    page.goto(f"{live_server.url}{BASE}/")
    page.locator('input[type="email"]').fill("notanemail")
    page.locator('input[type="email"]').dispatch_event("input")

    page.wait_for_selector("text=Enter a valid email address.")
    assert page.locator("text=Enter a valid email address.").is_visible()


def test_short_password_shows_error_while_typing(page, live_server):
    page.goto(f"{live_server.url}{BASE}/")
    page.locator('input[type="password"]').fill("short")
    page.locator('input[type="password"]').dispatch_event("input")

    page.wait_for_selector("text=At least 8 characters")
    assert page.locator("text=At least 8 characters").is_visible()


# --- strict validation on submit -------------------------------------------


def test_empty_submit_shows_required_errors(page, live_server):
    page.goto(f"{live_server.url}{BASE}/")
    page.locator("button", has_text="Sign in").click()

    page.wait_for_selector("text=Email is required.")
    assert page.locator("text=Email is required.").is_visible()
    assert page.locator("text=Password is required.").is_visible()


def test_unknown_email_fails(page, live_server):
    page.goto(f"{live_server.url}{BASE}/")
    page.locator('input[type="email"]').fill("nobody@example.com")
    page.locator('input[type="password"]').fill("supersecret")
    page.locator("button", has_text="Sign in").click()

    page.wait_for_selector("text=No Arden account found for that email.")
    assert page.locator("text=No Arden account found for that email.").is_visible()


def test_successful_sign_in(page, live_server, member):
    page.goto(f"{live_server.url}{BASE}/")
    page.locator('input[type="email"]').fill("mira@beaconlabs.com")
    page.locator('input[type="password"]').fill("supersecret")
    page.locator("button", has_text="Sign in").click()

    page.wait_for_selector("text=Welcome back, Mira Chen.")
    assert page.locator("text=Signed in to Beacon Labs.").is_visible()


# --- sign-up: the second page, off the same validation view -----------------


def test_sign_up_loads(page, live_server):
    page.goto(f"{live_server.url}{SIGN_UP}/")

    assert page.locator("text=Create your Arden account").is_visible()
    assert page.locator("text=Fourteen days free. No card required.").is_visible()


def test_sign_up_requires_a_name(page, live_server):
    """The name field only exists on sign-up — the shared validator is told to expect it."""
    page.goto(f"{live_server.url}{SIGN_UP}/")
    page.locator("button", has_text="Create account").click()

    page.wait_for_selector("text=Name is required.")
    assert page.locator("text=Name is required.").is_visible()


def test_sign_up_rejects_an_existing_member(page, live_server, member):
    page.goto(f"{live_server.url}{SIGN_UP}/")
    page.locator('input[placeholder="Mira Chen"]').fill("Mira Chen")
    page.locator('input[type="email"]').fill("mira@beaconlabs.com")
    page.locator('input[type="password"]').fill("supersecret")
    page.locator("button", has_text="Create account").click()

    page.wait_for_selector("text=That email is already on an Arden workspace.")
    assert page.locator(
        "text=That email is already on an Arden workspace."
    ).is_visible()


def test_successful_sign_up_creates_a_member(page, live_server, member):
    from lb.models import LbMember

    page.goto(f"{live_server.url}{SIGN_UP}/")
    page.locator('input[placeholder="Mira Chen"]').fill("Jonah Price")
    page.locator('input[type="email"]').fill("jonah@kiteandbell.com")
    page.locator('input[type="password"]').fill("supersecret")
    page.locator("button", has_text="Create account").click()

    page.wait_for_selector("text=Welcome to Arden, Jonah Price.")
    assert LbMember.objects.filter(
        email="jonah@kiteandbell.com", status="invited"
    ).exists()
