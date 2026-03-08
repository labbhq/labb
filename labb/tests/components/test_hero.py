from labb.tests.components.test_base import ComponentTestBase


class TestHero(ComponentTestBase):
    """Test hero component"""

    def test_basic_hero(self):
        """Test basic hero rendering"""
        html = self.render_component("hero", slot_content="<div>Content</div>")
        assert "hero" in html
        assert "Content" in html

    def test_hero_with_overlay(self):
        """Test hero with overlay enabled"""
        html = self.render_component(
            "hero", overlay=True, slot_content="<div>Content</div>"
        )
        assert "hero-overlay" in html

    def test_hero_no_overlay_by_default(self):
        """Test that no overlay is rendered by default"""
        html = self.render_component("hero", slot_content="<div>Content</div>")
        assert "hero-overlay" not in html

    def test_hero_custom_class(self):
        """Test hero with custom CSS class"""
        html = self.render_component(
            "hero",
            slot_content="<div>Content</div>",
            **{"class": "min-h-screen bg-base-200"},
        )
        assert "min-h-screen" in html
        assert "bg-base-200" in html


class TestHeroContent(ComponentTestBase):
    """Test hero.content component"""

    def test_basic_hero_content(self):
        """Test basic hero content rendering"""
        html = self.render_component("hero.content", slot_content="<h1>Title</h1>")
        assert "hero-content" in html
        assert "Title" in html

    def test_hero_content_custom_class(self):
        """Test hero content with custom class"""
        html = self.render_component(
            "hero.content",
            slot_content="<h1>Title</h1>",
            **{"class": "text-center"},
        )
        assert "text-center" in html


class TestHeroOverlay(ComponentTestBase):
    """Test hero.overlay component"""

    def test_basic_hero_overlay(self):
        """Test basic hero overlay rendering"""
        html = self.render_component("hero.overlay")
        assert "hero-overlay" in html

    def test_hero_overlay_custom_class(self):
        """Test hero overlay with custom class"""
        html = self.render_component("hero.overlay", **{"class": "bg-opacity-60"})
        assert "bg-opacity-60" in html
