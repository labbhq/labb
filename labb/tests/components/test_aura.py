from labb.tests.components.test_base import ComponentTestBase


class TestAura(ComponentTestBase):
    """Test aura component"""

    def test_basic(self):
        html = self.render_component("aura", slot_content="X")
        assert "aura" in html

    def test_default_size_md(self):
        html = self.render_component("aura", slot_content="X")
        assert "aura-md" in html

    def test_sizes(self):
        for size in ["xs", "sm", "md", "lg", "xl"]:
            html = self.render_component("aura", size=size, slot_content="X")
            assert f"aura-{size}" in html

    def test_variants(self):
        for variant in ["dual", "rainbow", "holo", "gold", "silver", "glow"]:
            html = self.render_component("aura", variant=variant, slot_content="X")
            assert f"aura-{variant}" in html

    def test_no_variant_by_default(self):
        html = self.render_component("aura", slot_content="X")
        assert "aura-dual" not in html
        assert "aura-rainbow" not in html

    def test_slot_content(self):
        html = self.render_component("aura", slot_content="Hello")
        assert "Hello" in html

    def test_custom_class(self):
        html = self.render_component("aura", slot_content="X", **{"class": "my-aura"})
        assert "my-aura" in html
