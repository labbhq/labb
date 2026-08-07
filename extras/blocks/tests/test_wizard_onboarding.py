"""
Integration tests for the lb/wizard/onboarding block — the catalogue's wizard anchor.

The lesson this block is the only home of: multi-step state carried in signals.
So the tests drive the wizard through a real browser and assert the three things
that lesson has to survive — an invalid step will not let you past it, going back
keeps what you typed, and the final submit round-trips to the database.
"""

import pytest

pytestmark = pytest.mark.django_db(transaction=True)

BASE = "/lb/wizard/onboarding/preview"

NAME = 'input[placeholder="Kite & Bell"]'
SLUG = 'input[placeholder="kite-and-bell"]'
INVITE_1 = 'input[placeholder="jonah@kiteandbell.com"]'
INVITE_2 = 'input[placeholder="rosa@kiteandbell.com"]'
INVITE_3 = 'input[placeholder="finance@kiteandbell.com"]'


@pytest.fixture
def plans(db):
    from lb.models import LbPlan

    return [
        LbPlan.objects.create(
            name="Arden Starter",
            slug="starter",
            tagline="For a founder who needs the numbers out of a spreadsheet.",
            price_monthly=49,
            price_yearly=490,
            seats_included=3,
            features=["Up to 3 seats", "MRR and churn dashboard"],
        ),
        LbPlan.objects.create(
            name="Arden Growth",
            slug="growth",
            tagline="For the revenue team that has outgrown guesswork.",
            price_monthly=149,
            price_yearly=1490,
            seats_included=10,
            is_featured=True,
            features=["Up to 10 seats", "Revenue forecasting"],
        ),
        LbPlan.objects.create(
            name="Arden Scale",
            slug="scale",
            tagline="For finance running the whole book of business.",
            price_monthly=449,
            price_yearly=4490,
            seats_included=25,
            features=["Unlimited seats", "SSO and SCIM"],
        ),
    ]


def _fill_workspace(page):
    page.locator(NAME).fill("Kite & Bell")
    page.locator(SLUG).fill("kite-and-bell")
    page.locator("button", has_text="Continue").click()
    page.wait_for_selector("text=Invite your revenue team")


def _fill_team(page, *emails):
    for selector, email in zip((INVITE_1, INVITE_2, INVITE_3), emails):
        page.locator(selector).fill(email)
    page.locator("button", has_text="Continue").click()
    page.wait_for_selector("text=Pick a plan")


# --- the block is a page, not a stepper (premium bar rule 2) ----------------


def test_it_opens_on_the_workspace_step(page, live_server, plans):
    page.goto(f"{live_server.url}{BASE}/")

    assert page.locator("text=Name your workspace").is_visible()
    assert page.locator("text=Set up your workspace.").is_visible()


def test_the_running_summary_and_reassurance_ship_with_it(page, live_server, plans):
    page.goto(f"{live_server.url}{BASE}/")

    # The summary rail is the surrounding matter — without it this is a bare stepper.
    assert page.locator("text=Untitled workspace").is_visible()
    assert page.locator("text=arden.app/your-team").is_visible()
    assert page.locator("text=Not chosen yet").is_visible()
    assert page.locator("text=14 days free, no card.").is_visible()
    assert page.locator("text=Kite & Bell").first.is_visible()


def test_the_summary_tracks_the_workspace_name_as_it_is_typed(page, live_server, plans):
    page.goto(f"{live_server.url}{BASE}/")
    page.locator(NAME).fill("Bramble Foods")
    page.locator(SLUG).fill("bramble-foods")

    aside = page.locator("aside")
    page.wait_for_selector("aside >> text=Bramble Foods")
    assert "arden.app/bramble-foods" in aside.inner_text()
    assert "Untitled workspace" not in aside.inner_text()


def test_the_block_is_ardens_not_labbs(page, live_server, plans):
    page.goto(f"{live_server.url}{BASE}/")

    body = page.locator("main").inner_text()
    assert "Arden" in body
    assert "labb" not in body.lower()


# --- an invalid step will not let you past it -------------------------------


def test_an_empty_step_one_cannot_advance(page, live_server, plans):
    page.goto(f"{live_server.url}{BASE}/")
    page.locator("button", has_text="Continue").click()

    page.wait_for_selector("text=Name your workspace.")
    assert page.locator(
        "text=Choose the address your team will sign in at."
    ).is_visible()
    # still on step 1
    assert not page.locator("text=Invite your revenue team").is_visible()


def test_a_bad_address_is_caught_while_typing(page, live_server, plans):
    page.goto(f"{live_server.url}{BASE}/")
    page.locator(SLUG).fill("Kite & Bell!")
    page.locator(SLUG).dispatch_event("input")

    page.wait_for_selector("text=Lowercase letters, numbers and hyphens only.")


def test_a_step_with_no_invites_cannot_advance(page, live_server, plans):
    page.goto(f"{live_server.url}{BASE}/")
    _fill_workspace(page)
    page.locator("button", has_text="Continue").click()

    page.wait_for_selector("text=Invite at least one teammate")
    assert not page.locator("text=Pick a plan").is_visible()


def test_a_malformed_invite_cannot_advance(page, live_server, plans):
    page.goto(f"{live_server.url}{BASE}/")
    _fill_workspace(page)
    page.locator(INVITE_1).fill("jonah-at-kiteandbell")
    page.locator("button", has_text="Continue").click()

    page.wait_for_selector("text=That does not look like an email address.")
    assert not page.locator("text=Pick a plan").is_visible()


def test_a_plan_too_small_for_the_team_cannot_submit(page, live_server, plans):
    """The seat check on step 3 reads the invites typed on step 2 — the state is still there."""
    page.goto(f"{live_server.url}{BASE}/")
    _fill_workspace(page)
    _fill_team(
        page,
        "jonah@kiteandbell.com",
        "rosa@kiteandbell.com",
        "finance@kiteandbell.com",
    )

    page.locator("label", has_text="Arden Starter").click()
    page.locator("button", has_text="Create workspace").click()

    page.wait_for_selector(
        "text=Arden Starter includes 3 seats and you are starting with 4."
    )


def test_no_plan_chosen_cannot_submit(page, live_server, plans):
    page.goto(f"{live_server.url}{BASE}/")
    _fill_workspace(page)
    _fill_team(page, "jonah@kiteandbell.com")
    page.locator("button", has_text="Create workspace").click()

    page.wait_for_selector("text=Choose a plan to finish setting up.")


# --- going back keeps what was entered --------------------------------------


def test_going_back_preserves_the_earlier_steps(page, live_server, plans):
    page.goto(f"{live_server.url}{BASE}/")
    _fill_workspace(page)
    _fill_team(page, "jonah@kiteandbell.com")

    page.locator("button", has_text="Back").click()
    page.wait_for_selector("text=Invite your revenue team")
    assert page.locator(INVITE_1).input_value() == "jonah@kiteandbell.com"

    page.locator("button", has_text="Back").click()
    page.wait_for_selector("text=Name your workspace")
    assert page.locator(NAME).input_value() == "Kite & Bell"
    assert page.locator(SLUG).input_value() == "kite-and-bell"


# --- the final submit round-trips -------------------------------------------


def test_the_final_submit_creates_the_workspace_and_the_invites(
    page, live_server, plans
):
    from lb.models import LbMember, LbWorkspace

    page.goto(f"{live_server.url}{BASE}/")
    _fill_workspace(page)
    _fill_team(page, "jonah@kiteandbell.com", "rosa@kiteandbell.com")

    page.locator("label", has_text="Arden Growth").click()
    page.locator("button", has_text="Create workspace").click()

    page.wait_for_selector("text=Kite & Bell is live.")
    assert page.locator("text=arden.app/kite-and-bell").first.is_visible()

    workspace = LbWorkspace.objects.get(slug="kite-and-bell")
    assert workspace.name == "Kite & Bell"
    assert workspace.plan.slug == "growth"
    assert workspace.region == "eu-west-1"

    members = LbMember.objects.filter(workspace=workspace).order_by("email")
    assert [m.email for m in members] == [
        "jonah@kiteandbell.com",
        "rosa@kiteandbell.com",
    ]
    assert {m.status for m in members} == {"invited"}
    assert {m.role for m in members} == {"member"}


def test_an_address_already_taken_is_rejected(page, live_server, plans):
    from django.utils import timezone
    from lb.models import LbWorkspace

    LbWorkspace.objects.create(
        name="Kite & Bell",
        slug="kite-and-bell",
        plan=plans[1],
        region="eu-west-1",
        currency="USD",
        created_at=timezone.now(),
    )

    page.goto(f"{live_server.url}{BASE}/")
    page.locator(NAME).fill("Kite & Bell")
    page.locator(SLUG).fill("kite-and-bell")
    page.locator("button", has_text="Continue").click()

    page.wait_for_selector("text=That address is taken. Try another.")
