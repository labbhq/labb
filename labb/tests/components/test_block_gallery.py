"""Tests for the block renderer gallery (cotton/lbb/renderer/gallery.html)."""

from django.template.loader import render_to_string

from .test_base import ComponentTestBase


def _card(**overrides):
    card = {
        "ref": "lb/auth/split-brand",
        "vendor": "lb",
        "category": "auth",
        "slug": "split-brand",
        "name": "Split Brand",
        "type": "fullstack",
        "description": "Sign in page",
        "thumbnail_url": "",
        "thumbnail_url_dark": "",
    }
    card.update(overrides)
    return card


class TestGalleryDemoMarker(ComponentTestBase):
    def render_gallery(self, card):
        return render_to_string(
            "cotton/lbb/renderer/gallery.html",
            {"categories": [("auth", [card])]},
        )

    def test_demo_block_gets_a_badge(self):
        html = self.render_gallery(_card(demo=True))
        assert "Demo" in html
        assert "badge-warning" in html

    def test_normal_block_has_no_demo_badge(self):
        html = self.render_gallery(_card(demo=False))
        assert "Demo" not in html
        assert "badge-warning" not in html
