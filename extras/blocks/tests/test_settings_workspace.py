"""
Integration tests for the lb/settings/workspace block — the catalogue's settings anchor.

The block exists to prove one thing: saving a section re-renders that section and
nothing else. So the central test does not just check that the saved section
updated — it stamps a marker into every zone first, saves one of them, and shows
that only the saved zone lost its marker.
"""

import datetime

import pytest
from django.utils import timezone

pytestmark = pytest.mark.django_db(transaction=True)

BASE = "/lb/settings/workspace/preview"

ZONES = ("section-profile", "section-team", "section-billing")

STAMP = """() => {
    for (const zone of ['section-profile', 'section-team', 'section-billing']) {
        const el = document.querySelector(`[data-lbr-target='${zone}']`);
        const mark = document.createElement('div');
        mark.setAttribute('data-mark', zone);
        el.appendChild(mark);
    }
}"""


def _marks(page, zone):
    return page.locator(f"[data-mark='{zone}']").count()


def _plan(name, slug, monthly, yearly, seats):
    from lb.models import LbPlan

    return LbPlan.objects.create(
        name=name,
        slug=slug,
        tagline=f"{name} tier",
        price_monthly=monthly,
        price_yearly=yearly,
        seats_included=seats,
        features=["Everything in the tier below", "Priority support"],
    )


def _member(workspace, name, email, role, status, last_active=None):
    from lb.models import LbMember

    return LbMember.objects.create(
        workspace=workspace,
        name=name,
        email=email,
        title="RevOps",
        role=role,
        status=status,
        two_factor=False,
        joined_on=datetime.date(2025, 3, 4),
        last_active_at=last_active,
    )


@pytest.fixture
def arden(db):
    """Beacon Labs on Arden Scale: three seats used of twenty-five."""
    from lb.models import LbCustomer, LbInvoice, LbWorkspace

    starter = _plan("Arden Starter", "starter", 49, 490, 2)
    growth = _plan("Arden Growth", "growth", 149, 1490, 10)
    scale = _plan("Arden Scale", "scale", 449, 4490, 25)

    workspace = LbWorkspace.objects.create(
        name="Beacon Labs",
        slug="beacon-labs",
        plan=scale,
        region="eu-west-1",
        currency="USD",
        billing_email="billing@beaconlabs.com",
        created_at=timezone.now() - datetime.timedelta(days=900),
    )

    _member(
        workspace,
        "Nadia Kessler",
        "nadia@beaconlabs.com",
        "owner",
        "active",
        timezone.now() - datetime.timedelta(hours=3),
    )
    _member(
        workspace,
        "Priya Raghunathan",
        "priya@beaconlabs.com",
        "billing",
        "active",
        timezone.now() - datetime.timedelta(days=2),
    )
    _member(
        workspace,
        "Marcus Oduya",
        "marcus@beaconlabs.com",
        "admin",
        "active",
        timezone.now() - datetime.timedelta(days=1),
    )

    customer = LbCustomer.objects.create(
        workspace=workspace,
        company="AtlasForge",
        contact_name="Mira Chen",
        email="ap@atlasforge.com",
        plan=growth,
        status="active",
        health="good",
        mrr=1490,
        seats=8,
        industry="Manufacturing",
        country="Germany",
        signed_up_on=datetime.date(2025, 1, 9),
    )
    LbInvoice.objects.create(
        customer=customer,
        number="ARD-2026-0417",
        amount="1490.00",
        currency="USD",
        status="open",
        period="Jul 2026",
        issued_on=datetime.date(2026, 7, 1),
        due_on=datetime.date(2026, 7, 31),
    )

    return {
        "workspace": workspace,
        "starter": starter,
        "growth": growth,
        "scale": scale,
    }


def _open(page, live_server):
    page.goto(f"{live_server.url}{BASE}/")
    page.wait_for_selector("text=Workspace settings")


def _team_tab(page):
    page.locator("label.tab", has_text="Team").click()


def _billing_tab(page):
    page.locator("label.tab", has_text="Billing").click()


# --- the block is a page, not a form (premium bar rule 2) -------------------


def test_page_shows_the_workspace_its_team_and_its_plan(page, live_server, arden):
    _open(page, live_server)

    assert page.locator("text=Beacon Labs").first.is_visible()

    _team_tab(page)
    assert page.locator("text=Nadia Kessler").is_visible()
    assert (
        page.locator("[data-lbr-target='section-team']")
        .get_by_text("Priya Raghunathan")
        .is_visible()
    )
    # Seat usage against the plan — the surrounding matter, not the bare form.
    assert page.locator("text=/ 25").first.is_visible()

    _billing_tab(page)
    assert page.locator("#plan-scale").get_by_text("Current").is_visible()
    assert page.locator("text=ARD-2026-0417").is_visible()


def test_block_is_not_labb_centric(page, live_server, arden):
    _open(page, live_server)

    body = page.locator("main").inner_text()
    assert "Arden" in body
    assert "labb" not in body.lower()


# --- live validation --------------------------------------------------------


def test_invalid_billing_email_shows_error_while_typing(page, live_server, arden):
    _open(page, live_server)
    page.locator('input[type="email"]').first.fill("nope")

    page.wait_for_selector("text=Enter a valid billing email.")


def test_invalid_slug_shows_error_while_typing(page, live_server, arden):
    _open(page, live_server)
    page.locator('input[placeholder="beacon-labs"]').fill("Beacon Labs!")

    page.wait_for_selector("text=Lowercase letters, numbers and single hyphens only.")


def test_address_preview_follows_the_slug_signal(page, live_server, arden):
    _open(page, live_server)
    page.locator('input[placeholder="beacon-labs"]').fill("beacon-hq")

    page.wait_for_selector("text=arden.app/w/beacon-hq")


def test_empty_name_is_rejected_on_save(page, live_server, arden):
    _open(page, live_server)
    page.locator('input[placeholder="Beacon Labs"]').fill("")
    page.get_by_role("button", name="Save changes").click()

    page.wait_for_selector("text=A workspace name is required.")


# --- the scoped morph -------------------------------------------------------


def test_saving_the_profile_updates_only_the_profile_zone(page, live_server, arden):
    """The guarantee: one zone is replaced, the others are left alone.

    Every zone is stamped with a marker node the server does not know about. After
    the save, the profile zone has lost its marker (it really was re-rendered) and
    the team and billing zones still carry theirs (they really were not).
    """
    _open(page, live_server)

    page.locator('input[placeholder="Beacon Labs"]').fill("Beacon Labs Group")
    page.wait_for_timeout(1200)  # let the debounced live validation land first

    page.evaluate(STAMP)
    for zone in ZONES:
        assert _marks(page, zone) == 1

    page.get_by_role("button", name="Save changes").click()
    page.wait_for_selector("text=Profile saved")

    assert _marks(page, "section-profile") == 0
    assert _marks(page, "section-team") == 1
    assert _marks(page, "section-billing") == 1

    assert page.locator("h2", has_text="Beacon Labs Group").is_visible()
    arden["workspace"].refresh_from_db()
    assert arden["workspace"].name == "Beacon Labs Group"


def test_saving_the_profile_raises_a_toast(page, live_server, arden):
    _open(page, live_server)
    page.get_by_role("button", name="Save changes").click()

    page.wait_for_selector(".toast")
    assert page.locator(".toast").get_by_text("Profile saved").is_visible()
    assert page.locator(".toast").get_by_text("arden.app/w/beacon-labs").is_visible()


def test_the_toast_dismisses_itself(page, live_server, arden):
    _open(page, live_server)
    page.get_by_role("button", name="Save changes").click()

    page.wait_for_selector(".toast")
    page.wait_for_selector(".toast", state="detached", timeout=10_000)


# --- team: invite, scoped to the team zone ----------------------------------


def test_inviting_a_teammate_updates_only_the_team_zone(page, live_server, arden):
    from lb.models import LbMember

    _open(page, live_server)
    _team_tab(page)

    page.locator('input[placeholder="name@beaconlabs.com"]').fill(
        "hana.ishikawa@beaconlabs.com"
    )
    page.wait_for_timeout(1200)

    page.evaluate(STAMP)
    page.get_by_role("button", name="Send invite").click()
    page.wait_for_selector("text=Invite sent")

    assert _marks(page, "section-team") == 0
    assert _marks(page, "section-profile") == 1
    assert _marks(page, "section-billing") == 1

    assert page.locator("text=hana.ishikawa@beaconlabs.com").first.is_visible()
    assert LbMember.objects.filter(
        email="hana.ishikawa@beaconlabs.com", status="invited"
    ).exists()


def test_inviting_an_existing_member_is_refused_while_typing(page, live_server, arden):
    _open(page, live_server)
    _team_tab(page)

    page.locator('input[placeholder="name@beaconlabs.com"]').fill(
        "marcus@beaconlabs.com"
    )

    page.wait_for_selector("text=Marcus Oduya is already on this workspace.")


def test_a_full_workspace_cannot_invite(page, live_server, arden):
    """Seats come from the plan — an error state the bare form would not have."""
    arden["workspace"].plan = arden["starter"]  # two seats, three members
    arden["workspace"].save()

    _open(page, live_server)
    _team_tab(page)

    page.locator('input[placeholder="name@beaconlabs.com"]').fill("owen@beaconlabs.com")
    page.wait_for_timeout(1200)
    page.get_by_role("button", name="Send invite").click()

    page.wait_for_selector("text=All 2 seats on Arden Starter are in use.")


# --- billing: plan change ---------------------------------------------------


def test_changing_plan_patches_billing_and_team_but_not_profile(
    page, live_server, arden
):
    """Seat allowance comes from the plan, so the team zone is genuinely affected."""
    _open(page, live_server)
    _billing_tab(page)

    page.evaluate(STAMP)
    page.locator("#plan-growth").get_by_role("button", name="Switch").click()
    page.wait_for_selector("text=Plan changed")

    assert _marks(page, "section-billing") == 0
    assert _marks(page, "section-team") == 0
    assert _marks(page, "section-profile") == 1

    assert page.locator("#plan-growth").get_by_text("Current").is_visible()
    _team_tab(page)
    assert page.locator("text=/ 10").first.is_visible()

    arden["workspace"].refresh_from_db()
    assert arden["workspace"].plan.slug == "growth"


def test_downgrading_below_the_seats_in_use_is_refused(page, live_server, arden):
    _open(page, live_server)
    _billing_tab(page)

    page.locator("#plan-starter").get_by_role("button", name="Switch").click()

    page.wait_for_selector("text=Arden Starter includes 2 seats and 3 are in use.")
    arden["workspace"].refresh_from_db()
    assert arden["workspace"].plan.slug == "scale"
