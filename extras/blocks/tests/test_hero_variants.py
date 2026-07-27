"""
Integration tests for the five lb/hero/* blocks.

Two things are worth testing about a hero, and neither is "does it look nice".

1. Premium bar rule 2 — every hero carries something beyond the bare
   headline + CTA. Each test asserts that block's *own* surrounding matter, on a
   string unique to it, so a passing assertion cannot be satisfied by copy that
   happens to live somewhere else on the page.

2. The zero-JS claim. It is a labb differentiator and it is invisible by nature:
   nothing on screen tells a reader that no framework was downloaded. So it is
   asserted here — as an ABSENCE, in the browser and in the source.
"""

from pathlib import Path

import pytest

HERO_DIR = Path(__file__).resolve().parent.parent / "hero"

SLUGS = ["split-visual", "centred-bold", "with-logos", "app-screenshot", "gradient-mesh"]

# The line each hero has to land, and one element from that hero and no other.
HEADLINES = {
    "split-visual": "Know your revenue.",
    "centred-bold": "Stop closing the books from memory.",
    "with-logos": "Revenue ops your finance team will actually trust.",
    "app-screenshot": "See the quarter before it lands.",
    "gradient-mesh": "Your revenue, finally in focus.",
}

BEYOND_THE_MECHANISM = {
    "split-visual": "Trusted by 2,400+ finance and ops teams",
    "centred-bold": "4.8 out of 5 from 2,400+ finance and ops teams",
    "with-logos": "The teams closing their quarter on Arden",
    "app-screenshot": "Reads Stripe, Chargebee and NetSuite",
    "gradient-mesh": "Median time to close the books",
}


def preview(slug: str) -> str:
    return f"/lb/hero/{slug}/preview/"


def block_templates(slug: str) -> list[Path]:
    return [p for p in (HERO_DIR / slug / "templates").rglob("*.html") if p.is_file()]


# --- every hero lands its line ---------------------------------------------


@pytest.mark.parametrize("slug", SLUGS)
def test_hero_renders_its_headline(page, live_server, slug):
    page.goto(f"{live_server.url}{preview(slug)}")

    assert page.get_by_role("heading", level=1).inner_text().strip() == HEADLINES[slug]


@pytest.mark.parametrize("slug", SLUGS)
def test_hero_carries_more_than_a_headline_and_a_button(page, live_server, slug):
    """Premium bar rule 2 — a headline plus two buttons is a template, not a block."""
    page.goto(f"{live_server.url}{preview(slug)}")

    beyond = page.get_by_text(BEYOND_THE_MECHANISM[slug], exact=False).first
    assert beyond.is_visible()


@pytest.mark.parametrize("slug", SLUGS)
def test_hero_offers_a_primary_and_a_secondary_action(page, live_server, slug):
    page.goto(f"{live_server.url}{preview(slug)}")

    assert page.get_by_role("button", name="Start free trial").is_visible()
    assert page.locator("main button").count() >= 2


# --- the zero-JS story, asserted as an absence -------------------------------


@pytest.mark.parametrize("slug", SLUGS)
def test_hero_loads_no_datastar(page, live_server, slug):
    """
    The differentiator: a static page ships no framework. Datastar is loaded
    on demand by c-lbr.* components, and a hero uses none — so the tag must be
    absent entirely, not merely deferred.
    """
    page.goto(f"{live_server.url}{preview(slug)}")

    assert page.locator('script[src*="datastar"]').count() == 0
    assert "datastar" not in page.content()


@pytest.mark.parametrize("slug", SLUGS)
def test_hero_templates_contain_no_script_tag(slug):
    """
    Belt and braces at the source. The renderer chrome injects its own script for
    the preview iframe, so the browser check above cannot see a block that starts
    smuggling one in. This can.
    """
    offenders = [p.name for p in block_templates(slug) if "<script" in p.read_text()]
    assert offenders == []


# --- the catalogue rework's whole point --------------------------------------


@pytest.mark.parametrize("slug", SLUGS)
def test_hero_is_ardens_not_labbs(page, live_server, slug):
    page.goto(f"{live_server.url}{preview(slug)}")

    body = page.locator("main").inner_text()
    assert "Arden" in body
    assert "labb" not in body.lower()


@pytest.mark.parametrize("slug", SLUGS)
def test_hero_source_never_mentions_labb(slug):
    """`labb` must not survive in the markup either — not in a class, not in a comment."""
    for template in block_templates(slug):
        text = template.read_text().lower()
        assert "labb" not in text, f"{template} mentions labb"


@pytest.mark.parametrize("slug", SLUGS)
def test_hero_has_no_lorem(slug):
    for template in block_templates(slug):
        assert "lorem" not in template.read_text().lower()


# --- the treatments differ, which is the reason there are five of them --------


def test_with_logos_shows_the_arden_supporting_cast(page, live_server):
    page.goto(f"{live_server.url}{preview('with-logos')}")

    for customer in ("AtlasForge", "Kite & Bell", "Northwind Co", "Verity Labs", "Ironvale Group"):
        assert page.get_by_text(customer, exact=True).first.is_visible()


def test_split_visual_frames_a_product_shot_built_from_markup(page, live_server):
    """No image asset: the 'screenshot' is a themed component tree inside browser chrome."""
    page.goto(f"{live_server.url}{preview('split-visual')}")

    assert page.locator(".mockup-browser").is_visible()
    assert page.locator(".mockup-browser").get_by_text("Net MRR").is_visible()
    assert page.locator("main img").count() == 0


def test_app_screenshot_frames_a_full_dashboard(page, live_server):
    page.goto(f"{live_server.url}{preview('app-screenshot')}")

    shot = page.locator(".mockup-window")
    assert shot.get_by_text("Contraction").is_visible()
    # The nav and the ledger are in the frame; both are held back on small screens,
    # so assert they are in the shot rather than that they are on screen.
    assert shot.get_by_text("Renewals").count() == 1
    assert shot.get_by_text("Verity Labs").count() == 1
    assert page.locator("main img").count() == 0


def test_gradient_mesh_backdrop_has_no_token_colour_blobs(page, live_server):
    """
    The backdrop carries one deliberate fixed-colour aurora (the sanctioned
    allow_fixed_colours exception, identical in every theme) — never
    token-primary/secondary/accent colour blobs, which smear when the theme
    changes. This is the contract that keeps the hero clean in light and dark.
    """
    page.goto(f"{live_server.url}{preview('gradient-mesh')}")

    mesh = page.locator("main div.pointer-events-none").first
    assert mesh.count() == 1
    assert mesh.locator(".bg-primary\\/40").count() == 0
    assert mesh.locator(".bg-secondary\\/40").count() == 0
    assert mesh.locator(".bg-accent\\/30").count() == 0
